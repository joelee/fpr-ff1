"""Backend selection and dispatch tests (plan 00003 STEP-10, REQ-13/18/19).

The ``backend`` keyword is additive and opt-in: the default path must be
byte-for-byte the pure-Python reference, ``backend="rust"`` dispatches to
the compiled core *after* ``_prepare`` so validation and exceptions are
identical for both backends, and a missing compiled extension is a clear
``BackendError`` rather than an opaque ``ImportError``.

Availability mirrors the oracle contract (AGENTS.md tests section 7): the
rust-backend tests skip locally when the extension is not built and fail
hard when ``FPR_FF1_REQUIRE_RUST_BACKEND`` is set.  CI's ``rust-conformance``
job sets that variable, so a missing extension fails the release gate rather
than skipping.  The pure-Python and validation-parity tests always run.
"""

import importlib
import os
import pickle
import sys
import types
from typing import Any

import pytest
from packaging.version import Version

import fpr_ff1
from fpr_ff1 import FF1
from fpr_ff1._exceptions import (  # pyright: ignore[reportPrivateUsage]
    BackendError,
    FF1Error,
    LengthError,
    TweakLengthError,
    ValueRangeError,
)

_KEY = bytes(range(16))
_TWEAK = b"dispatch-test"
_REQUIRED = os.environ.get("FPR_FF1_REQUIRE_RUST_BACKEND", "").strip() not in {"", "0"}

#: Rust-dependent tests skip locally without the built extension, and fail
#: hard when the backend is required (mirroring FPR_FF1_REQUIRE_ORACLE).
_rust_available = True
try:
    importlib.import_module("fpr_ff1._rs")
except ImportError:
    _rust_available = False

requires_rust = pytest.mark.skipif(
    not _rust_available and not _REQUIRED,
    reason="Rust backend not built; run `just backend-dev`",
)
if _REQUIRED and not _rust_available:
    raise ImportError("FPR_FF1_REQUIRE_RUST_BACKEND is set but fpr_ff1._rs is not built")


def _plaintext(n: int = 10, radix: int = 10) -> list[int]:
    return [(i * 7 + 1) % radix for i in range(n)]


def test_default_backend_is_python() -> None:
    """No ``backend`` argument means the pure-Python reference path."""
    ff1 = FF1(key=_KEY, radix=10)
    assert ff1._backend == "python"  # pyright: ignore[reportPrivateUsage]


def test_explicit_python_backend_matches_default() -> None:
    """``backend="python"`` is the same path, byte for byte."""
    default = FF1(key=_KEY, radix=10)
    explicit = FF1(key=_KEY, radix=10, backend="python")
    pt = _plaintext()
    assert default.encrypt_numerals(pt, _TWEAK) == explicit.encrypt_numerals(pt, _TWEAK)
    assert default.decrypt_numerals(pt, _TWEAK) == explicit.decrypt_numerals(pt, _TWEAK)


def test_unknown_backend_raises() -> None:
    """An unknown backend name is a configuration fault with a typed error."""
    with pytest.raises(BackendError, match=r"python.*rust"):
        FF1(key=_KEY, radix=10, backend="go")


def test_non_str_backend_raises() -> None:
    """Types are checked before values, like every other parameter."""
    with pytest.raises(BackendError, match="must be a str"):
        FF1(key=_KEY, radix=10, backend=1)  # pyright: ignore[reportArgumentType]


def test_backend_error_roots_at_ff1_error() -> None:
    """REQ-19: every backend rejection is rooted at ``FF1Error``."""
    assert issubclass(BackendError, FF1Error)


def test_missing_extension_raises_backend_error(monkeypatch: pytest.MonkeyPatch) -> None:
    """A missing compiled backend is a clear BackendError, not ImportError.

    ``None`` in ``sys.modules`` makes ``importlib.import_module`` raise
    ImportError for the module — the standard way to simulate an
    uninstalled extension without uninstalling it.
    """
    monkeypatch.setitem(sys.modules, "fpr_ff1._rs", None)
    with pytest.raises(BackendError, match="not available"):
        FF1(key=_KEY, radix=10, backend="rust")


def _install_fake_rust_backend(
    monkeypatch: pytest.MonkeyPatch,
) -> list[tuple[str, tuple[Any, ...]]]:
    """Install a fake ``fpr_ff1._rs`` module and record its calls.

    The real extension is optional and absent in CI's ``quality`` job, so the
    rust dispatch plumbing (``_rust_ff1``, the ``backend == "rust"`` branches,
    and the unpickle re-validation) would otherwise never execute there and
    drop the coverage floor. A fake module in ``sys.modules`` makes
    ``importlib.import_module`` succeed, so the plumbing runs and its calls
    are recorded — the same simulation technique the missing-extension test
    uses in reverse.
    """
    calls: list[tuple[str, tuple[Any, ...]]] = []
    fake = types.ModuleType("fpr_ff1._rs")

    def encrypt_numerals(key: bytes, radix: int, x: list[int], tweak: bytes) -> list[int]:
        calls.append(("encrypt_numerals", (key, radix, x, tweak)))
        return [0] * len(x)

    def decrypt_numerals(key: bytes, radix: int, x: list[int], tweak: bytes) -> list[int]:
        calls.append(("decrypt_numerals", (key, radix, x, tweak)))
        return [0] * len(x)

    fake.encrypt_numerals = encrypt_numerals  # type: ignore[attr-defined]
    fake.decrypt_numerals = decrypt_numerals  # type: ignore[attr-defined]
    monkeypatch.setitem(sys.modules, "fpr_ff1._rs", fake)
    return calls


def test_rust_dispatch_plumbing_without_real_extension(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """The rust dispatch path routes to the compiled module's functions.

    Exercises ``_rust_ff1`` and both ``backend == "rust"`` branches with a
    fake extension, proving the plumbing (import, function selection,
    argument passing) without the real one — keeping those lines inside the
    coverage floor when CI runs without a built extension.
    """
    calls = _install_fake_rust_backend(monkeypatch)
    ff1 = FF1(key=_KEY, radix=10, backend="rust")
    pt = _plaintext()

    ct = ff1.encrypt_numerals(pt, _TWEAK)
    assert ct == [0] * len(pt)
    assert calls[-1] == ("encrypt_numerals", (_KEY, 10, pt, _TWEAK))

    dec = ff1.decrypt_numerals(pt, _TWEAK)
    assert dec == [0] * len(pt)
    assert calls[-1] == ("decrypt_numerals", (_KEY, 10, pt, _TWEAK))


def test_rust_unpickle_revalidates_extension(monkeypatch: pytest.MonkeyPatch) -> None:
    """Unpickling a rust instance re-imports the backend (``__setstate__``).

    The far side of a pickle may not have the extension installed, so
    ``__setstate__`` re-validates availability. With a fake extension present
    the re-validation succeeds and the instance round-trips; this keeps the
    ``_load_rust_backend()`` call in ``__setstate__`` inside the coverage
    floor when the real extension is absent.
    """
    _install_fake_rust_backend(monkeypatch)
    ff1 = FF1(key=_KEY, radix=10, backend="rust")
    clone = pickle.loads(pickle.dumps(ff1))  # noqa: S301
    assert clone._backend == "rust"  # pyright: ignore[reportPrivateUsage]
    assert clone.encrypt_numerals(_plaintext(), _TWEAK) == [0] * 10


@requires_rust
def test_rust_backend_matches_python_bit_for_bit() -> None:
    """The compiled backend produces identical ciphertext to the reference."""
    for radix in (10, 36, 256):
        py_ff1 = FF1(key=_KEY, radix=radix)
        rs_ff1 = FF1(key=_KEY, radix=radix, backend="rust")
        assert rs_ff1._backend == "rust"  # pyright: ignore[reportPrivateUsage]
        for n in (6, 7, 60):  # includes odd n and the d > 16 expansion case
            pt = _plaintext(n, radix)
            ct_py = py_ff1.encrypt_numerals(pt, _TWEAK)
            ct_rs = rs_ff1.encrypt_numerals(pt, _TWEAK)
            assert ct_rs == ct_py, f"encrypt diverged at radix {radix} n {n}"
            assert rs_ff1.decrypt_numerals(ct_rs, _TWEAK) == pt
            assert rs_ff1.decrypt_numerals(ct_py, _TWEAK) == pt


@requires_rust
def test_string_interface_dispatches_identically() -> None:
    """The string wrappers ride the same dispatch as the numeral methods."""
    py = FF1(key=_KEY, radix=10, alphabet="0123456789")
    rs = FF1(key=_KEY, radix=10, alphabet="0123456789", backend="rust")
    assert rs.encrypt("123456", _TWEAK) == py.encrypt("123456", _TWEAK)
    assert rs.decrypt(py.encrypt("123456", _TWEAK), _TWEAK) == "123456"


@pytest.mark.parametrize(
    ("bad_input", "error_type"),
    [
        ([1, 2], LengthError),
        ([1, 2, 3, 4, 5, 10], ValueRangeError),
        ([1, 2, 3, 4, 5, -1], ValueRangeError),
    ],
)
def test_validation_identical_across_backends(
    bad_input: list[int], error_type: type[FF1Error]
) -> None:
    """REQ-18: identical invalid inputs raise identical exceptions.

    Validation runs in Python for both backends (plan decision D4), so the
    exception type AND message must match exactly. The rust instance is
    constructible only when the extension is built; without it the parity
    guarantee is carried by the shared ``_prepare`` path itself.
    """
    py = FF1(key=_KEY, radix=10)
    with pytest.raises(error_type) as py_exc:
        py.encrypt_numerals(bad_input, _TWEAK)

    if _rust_available:
        rs = FF1(key=_KEY, radix=10, backend="rust")
        with pytest.raises(error_type) as rs_exc:
            rs.encrypt_numerals(bad_input, _TWEAK)
        assert str(py_exc.value) == str(rs_exc.value)


def test_bad_tweak_identical_across_backends() -> None:
    """Tweak validation is also shared, including per-call tweaks."""
    # The default tweak satisfies the bound; the per-call tweak violates it.
    py = FF1(key=_KEY, radix=10, tweak=b"valid-tweak", min_tweak_len=4)
    with pytest.raises(TweakLengthError) as py_exc:
        py.encrypt_numerals(_plaintext(), b"ab")

    if _rust_available:
        rs = FF1(key=_KEY, radix=10, tweak=b"valid-tweak", min_tweak_len=4, backend="rust")
        with pytest.raises(TweakLengthError) as rs_exc:
            rs.encrypt_numerals(_plaintext(), b"ab")
        assert str(py_exc.value) == str(rs_exc.value)


@requires_rust
def test_rust_instance_pickles_and_round_trips() -> None:
    """A rust instance survives pickling and encrypts identically."""
    rs = FF1(key=_KEY, radix=10, backend="rust")
    clone = pickle.loads(pickle.dumps(rs))  # noqa: S301
    assert clone._backend == "rust"  # pyright: ignore[reportPrivateUsage]
    pt = _plaintext()
    assert clone.encrypt_numerals(pt, _TWEAK) == rs.encrypt_numerals(pt, _TWEAK)


def test_legacy_pickle_state_defaults_to_python() -> None:
    """A pickle from 1.x (no ``_backend`` key) unpickles as the python backend.

    The destination is ``FF1.__new__(FF1)``, not a constructed instance: real
    unpickling bypasses ``__init__``, so a normally-constructed destination
    would supply the very attribute ``__setstate__`` must restore (review
    00007 MAJ-01 -- this test passed while every restored 1.x instance was
    unusable).
    """
    ff1 = FF1(key=_KEY, radix=10)
    state: dict[str, Any] = ff1.__getstate__()  # pyright: ignore[reportPrivateUsage]
    del state["_backend"]
    clone = FF1.__new__(FF1)
    clone.__setstate__(state)  # pyright: ignore[reportPrivateUsage]
    assert clone._backend == "python"  # pyright: ignore[reportPrivateUsage]
    assert clone.encrypt_numerals(_plaintext(), _TWEAK) == ff1.encrypt_numerals(
        _plaintext(), _TWEAK
    )


#: The instance attributes a 1.1.x ``FF1.__getstate__`` produced: 2.0 added
#: ``_backend`` and nothing else.  Pinned here rather than derived from the
#: current class so the legacy format is a fixed fact, not a moving target.
_LEGACY_1_1_STATE_KEYS = frozenset(
    {
        "_key",
        "_radix",
        "_min_tweak_len",
        "_max_tweak_len",
        "_default_tweak",
        "_alphabet",
        "_char_to_index",
        "_index_to_char",
        "_min_length",
    }
)


def test_legacy_serialized_state_round_trips(monkeypatch: pytest.MonkeyPatch) -> None:
    """A real serialized 1.1-format payload restores into a working instance.

    The payload goes through the pickle machinery itself -- ``dumps`` with a
    ``__getstate__`` that emits exactly the 1.1 attribute set, then
    ``loads`` -- so restoration runs on an object ``__init__`` never touched.
    Every operation is exercised, then the restored instance is serialized
    a second time with the current format.
    """
    alphabet = "0123456789"
    ff1 = FF1(key=_KEY, radix=10, alphabet=alphabet, tweak=_TWEAK)
    plaintext = _plaintext()
    text = "".join(alphabet[d] for d in plaintext)

    def legacy_getstate(self: FF1) -> dict[str, Any]:
        state = dict(self.__dict__)
        del state["_aes"]
        del state["_backend"]
        return state

    monkeypatch.setattr(FF1, "__getstate__", legacy_getstate)
    payload = pickle.dumps(ff1)
    monkeypatch.undo()

    restored: FF1 = pickle.loads(payload)  # noqa: S301 -- trusted, test-built payload
    # Attribute parity with a constructed instance: the drift MAJ-01 was an
    # instance of (restoration missing an attribute ``__init__`` sets).
    assert set(vars(restored)) == set(vars(ff1))
    assert set(vars(restored)) - {"_aes", "_backend"} == _LEGACY_1_1_STATE_KEYS
    assert restored._backend == "python"  # pyright: ignore[reportPrivateUsage]

    ciphertext = restored.encrypt_numerals(plaintext)
    assert ciphertext == ff1.encrypt_numerals(plaintext)
    assert restored.decrypt_numerals(ciphertext) == plaintext
    assert restored.encrypt(text) == ff1.encrypt(text)
    assert restored.decrypt(restored.encrypt(text)) == text

    again: FF1 = pickle.loads(pickle.dumps(restored))  # noqa: S301
    assert again._backend == "python"  # pyright: ignore[reportPrivateUsage]
    assert again.encrypt_numerals(plaintext) == ciphertext


def test_corrupt_unpickled_backend_raises() -> None:
    """A hand-crafted pickle with an unknown backend is rejected, not ignored."""
    ff1 = FF1(key=_KEY, radix=10)
    state: dict[str, Any] = ff1.__getstate__()  # pyright: ignore[reportPrivateUsage]
    state["_backend"] = "fortran"
    clone = FF1.__new__(FF1)
    with pytest.raises(BackendError, match="fortran"):
        clone.__setstate__(state)  # pyright: ignore[reportPrivateUsage]


def test_non_str_unpickled_backend_raises() -> None:
    """A hand-crafted pickle with a non-str backend is rejected too."""
    ff1 = FF1(key=_KEY, radix=10)
    state: dict[str, Any] = ff1.__getstate__()  # pyright: ignore[reportPrivateUsage]
    state["_backend"] = 42
    clone = FF1.__new__(FF1)
    with pytest.raises(BackendError, match="str backend"):
        clone.__setstate__(state)  # pyright: ignore[reportPrivateUsage]


@requires_rust
def test_extension_version_matches_distribution() -> None:
    """``_rs.__version__`` reports the crate version, and it is ours.

    It was a hard-coded ``"0.1.0"`` -- a literal unrelated to anything
    shipped, and untested, so nothing noticed. It now comes from
    ``CARGO_PKG_VERSION``, which makes it a real provenance signal for a
    wheel: the compiled core in your site-packages says which release it
    was built from.

    Compared after normalisation, for the reason given in
    ``test_crate_version_matches_project_version``.
    """
    rs = importlib.import_module("fpr_ff1._rs")
    assert Version(rs.__version__) == Version(fpr_ff1.__version__)
