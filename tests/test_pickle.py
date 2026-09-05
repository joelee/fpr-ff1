"""Pickling, deepcopy and ``__version__`` tests (review 00003 H1, B2).

FPE is overwhelmingly a batch-processing workload: ``multiprocessing`` with
the spawn start method (the default on macOS and Windows, and on Linux from
3.14) and ``ProcessPoolExecutor`` cannot pass an unpicklable object to a
worker, and PySpark cannot broadcast one.  The cached ``CipherContext``
previously made ``FF1`` unpicklable -- opaque Rust state that ``pickle``
refuses to serialise.

The fix serialises the *configuration* and rebuilds the cipher objects on
the other side.  Note the security consequence asserted here and documented
in ``SECURITY.md``: the key crosses the pickle boundary.
"""

import copy
import multiprocessing
import pickle
from importlib.metadata import version as _distribution_version
from typing import Any

import pytest

import fpr_ff1
from fpr_ff1 import FF1, KeyLengthError

_VALID_KEY = b"\x00" * 16
# Length 60 at radix 10 reaches d > 16, exercising the expansion branch
# through a rebuilt instance.
_LONG_PLAINTEXT = [1, 2, 3, 4, 5, 6, 7, 8, 9, 0] * 6


def _make() -> FF1:
    return FF1(key=_VALID_KEY, radix=10, tweak=b"tweak")


def _worker(ff1: FF1, plaintext: list[int], queue: Any) -> None:
    """Module-level so the spawn context can pickle the target by name."""
    queue.put(ff1.encrypt_numerals(plaintext))


def test_pickle_round_trip_encrypts_identically() -> None:
    """A pickled instance must behave exactly like the original."""
    original = _make()
    # S301: loading only bytes this test just dumped itself.
    restored = pickle.loads(pickle.dumps(original))  # noqa: S301

    for plaintext in ([1, 2, 3, 4, 5, 6], _LONG_PLAINTEXT):
        assert restored.encrypt_numerals(plaintext) == original.encrypt_numerals(plaintext)
        ciphertext = original.encrypt_numerals(plaintext)
        assert restored.decrypt_numerals(ciphertext) == plaintext


def test_deepcopy_round_trip_encrypts_identically() -> None:
    """copy.deepcopy must produce an independent, equivalent instance."""
    original = _make()
    duplicate = copy.deepcopy(original)

    ciphertext = original.encrypt_numerals(_LONG_PLAINTEXT)
    assert duplicate.decrypt_numerals(ciphertext) == _LONG_PLAINTEXT


def test_copy_copy_is_independent() -> None:
    """copy.copy shares configuration but must remain fully functional."""
    original = _make()
    duplicate = copy.copy(original)

    assert duplicate.encrypt_numerals([1, 2, 3, 4, 5, 6]) == original.encrypt_numerals(
        [1, 2, 3, 4, 5, 6]
    )


def test_multiprocessing_spawn_round_trip() -> None:
    """A spawn-context worker must be able to use a pickled instance.

    This is the archetypal batch use case: the instance is constructed in
    the parent, pickled by the spawn machinery, rebuilt in the child, and
    must produce identical ciphertext there.
    """
    ctx = multiprocessing.get_context("spawn")
    queue = ctx.Queue()
    original = _make()
    expected = original.encrypt_numerals(_LONG_PLAINTEXT)

    process = ctx.Process(target=_worker, args=(original, _LONG_PLAINTEXT, queue))
    process.start()
    try:
        result = queue.get(timeout=30)
        process.join(timeout=30)
    finally:
        if process.is_alive():
            process.terminate()
            process.join()

    assert result == expected


def test_pickle_does_not_serialise_cipher_objects() -> None:
    """The pickle payload must carry configuration, not opaque cipher state.

    ``Cipher`` objects are unserialisable by design; the state dict must
    contain the key and parameters but no ``_aes`` entry.
    """
    state = _make().__getstate__()  # pyright: ignore[reportPrivateUsage]
    assert isinstance(state, dict)
    assert "_aes" not in state, "cipher objects must be rebuilt, never serialised"
    assert state["_key"] == _VALID_KEY
    assert state["_radix"] == 10


def test_setstate_rejects_non_bytes_key() -> None:
    """A corrupted payload must raise from the documented hierarchy.

    ``__setstate__`` gates the rebuilt key's type: an assert would vanish
    under ``python -O``, and an ungated wrong type would surface later as an
    opaque cryptography error outside ``FF1Error``.
    """
    ff1 = _make()
    state = ff1.__getstate__()  # pyright: ignore[reportPrivateUsage]
    state["_key"] = "not-bytes"  # pyright: ignore[reportArgumentType]

    restored = FF1.__new__(FF1)
    with pytest.raises(KeyLengthError, match="bytes key"):
        restored.__setstate__(state)  # pyright: ignore[reportPrivateUsage]


def test_version_is_exported_and_matches_distribution() -> None:
    """``__version__`` must exist, be a string, and match the installed dist.

    Callers recording which build produced a dataset need it; it is part of
    the stable surface from 1.0.0.
    """
    assert hasattr(fpr_ff1, "__version__")
    assert isinstance(fpr_ff1.__version__, str)
    assert fpr_ff1.__version__ == _distribution_version("fpr-ff1")


def test_version_in_all() -> None:
    """``__version__`` is part of the documented public surface."""
    assert "__version__" in fpr_ff1.__all__


@pytest.mark.parametrize("protocol", range(2, pickle.HIGHEST_PROTOCOL + 1))
def test_all_pickle_protocols_round_trip(protocol: int) -> None:
    """Every pickle protocol Python 3.12 supports must work."""
    original = _make()
    # S301: loading only bytes this test just dumped itself.
    restored = pickle.loads(pickle.dumps(original, protocol=protocol))  # noqa: S301
    assert restored.encrypt_numerals([1, 2, 3, 4, 5, 6]) == original.encrypt_numerals(
        [1, 2, 3, 4, 5, 6]
    )
