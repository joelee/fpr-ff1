"""Backend selection and dispatch tests (plan 00003 STEP-10, REQ-13/18/19).

The ``backend`` keyword is additive and opt-in: the default path must be
byte-for-byte the pure-Python reference, ``backend="rust"`` dispatches to
the compiled core *after* ``_prepare`` so validation and exceptions are
identical for both backends, and a missing compiled extension is a clear
``BackendError`` rather than an opaque ``ImportError``.

Availability mirrors the oracle contract (AGENTS.md tests section 7): the
rust-backend tests skip locally when the extension is not built and fail
hard when ``FPR_FF1_REQUIRE_RUST_BACKEND`` is set (CI wiring lands in
STEP-14).  The pure-Python and validation-parity tests always run.
"""

import importlib
import os
import pickle
import sys
from typing import Any

import pytest

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
    raise ImportError("FPR_FF1_REQUIRE_RUST_BACKEND is set but _fpr_ff1_rs is not built")


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
    """A pickle from 1.x (no ``_backend`` key) unpickles as the python backend."""
    ff1 = FF1(key=_KEY, radix=10)
    state: dict[str, Any] = ff1.__getstate__()  # pyright: ignore[reportPrivateUsage]
    del state["_backend"]
    clone = FF1(key=_KEY, radix=10)
    clone.__setstate__(state)  # pyright: ignore[reportPrivateUsage]
    assert clone._backend == "python"  # pyright: ignore[reportPrivateUsage]
    assert clone.encrypt_numerals(_plaintext(), _TWEAK) == ff1.encrypt_numerals(
        _plaintext(), _TWEAK
    )


def test_corrupt_unpickled_backend_raises() -> None:
    """A hand-crafted pickle with an unknown backend is rejected, not ignored."""
    ff1 = FF1(key=_KEY, radix=10)
    state: dict[str, Any] = ff1.__getstate__()  # pyright: ignore[reportPrivateUsage]
    state["_backend"] = "fortran"
    clone = FF1(key=_KEY, radix=10)
    with pytest.raises(BackendError, match="fortran"):
        clone.__setstate__(state)  # pyright: ignore[reportPrivateUsage]


def test_non_str_unpickled_backend_raises() -> None:
    """A hand-crafted pickle with a non-str backend is rejected too."""
    ff1 = FF1(key=_KEY, radix=10)
    state: dict[str, Any] = ff1.__getstate__()  # pyright: ignore[reportPrivateUsage]
    state["_backend"] = 42
    clone = FF1(key=_KEY, radix=10)
    with pytest.raises(BackendError, match="str backend"):
        clone.__setstate__(state)  # pyright: ignore[reportPrivateUsage]
