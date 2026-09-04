"""Regression tests for the minimum-domain validation bypass (review 00004 MAJ-01).

``_prepare`` previously trusted the declared ``__len__`` of its input without
verifying that the materialised list has the same length, and accepted
anything with a ``__len__`` -- including mappings and sets.  A ``Sequence``
whose ``__len__`` lies could therefore reach the FF1 core with fewer numerals
than the enforced minimum domain, producing ciphertext for a domain the
package promises to reject.

Every test here asserts *specified* behaviour, not current behaviour.
"""

from collections.abc import Iterator, Sequence
from typing import Any

import pytest

from fpr_ff1 import FF1, LengthError, TweakLengthError, ValueRangeError

_VALID_KEY = b"\x00" * 16


class _LyingSequence(Sequence[int]):
    """A concrete ``Sequence`` whose ``__len__`` over-reports.

    Reports six elements (radix 10's minimum length) but yields only
    ``yielded`` values, reproducing review 00004 MAJ-01 exactly: the
    pre-check accepted the declared length while the core recalculated
    ``n`` from the shorter materialised list.
    """

    def __init__(self, yielded: int) -> None:
        self._values = list(range(yielded))

    def __len__(self) -> int:
        return 6

    def __getitem__(self, index: int | slice) -> Any:
        return self._values[index]


class _ExplodingOnRead(Sequence[int]):
    """A ``Sequence`` that raises if read before the length check.

    Guards the ordering kept from the original fix: an over-long input must
    still be rejected on its declared length alone, without materialising it.
    """

    def __len__(self) -> int:
        return 2**32 + 1

    def __getitem__(self, index: Any) -> Any:  # pragma: no cover - never reached
        raise AssertionError("input must not be read before the length check")


class _IterOnly:
    """Has ``__len__`` but is not a ``Sequence`` -- the old gate accepted it."""

    def __len__(self) -> int:
        return 6

    def __iter__(self) -> Iterator[int]:
        return iter([1, 2, 3, 4, 5, 6])


@pytest.mark.parametrize("yielded", [0, 1, 5])
@pytest.mark.parametrize("method_name", ["encrypt_numerals", "decrypt_numerals"])
def test_lying_sequence_length_is_rejected(yielded: int, method_name: str) -> None:
    """A Sequence whose __len__ disagrees with its yielded values must raise.

    The declared length (6) passes the minimum-domain check, but the
    materialised length (``yielded``) is below ``min_length`` -- the exact
    bypass review 00004 reproduced.  The rejection must come from the
    documented hierarchy, not a bare builtin.
    """
    ff1 = FF1(key=_VALID_KEY, radix=10)
    method = getattr(ff1, method_name)
    with pytest.raises(LengthError) as excinfo:
        method(_LyingSequence(yielded))  # pyright: ignore[reportArgumentType]
    assert str(excinfo.value)


@pytest.mark.parametrize("method_name", ["encrypt_numerals", "decrypt_numerals"])
def test_dict_input_is_rejected(method_name: str) -> None:
    """A mapping is not an ordered Sequence; its iteration order is not stable."""
    ff1 = FF1(key=_VALID_KEY, radix=10)
    method = getattr(ff1, method_name)
    with pytest.raises(TypeError, match="Sequence"):
        method(dict.fromkeys(range(6)))  # pyright: ignore[reportArgumentType]


@pytest.mark.parametrize("method_name", ["encrypt_numerals", "decrypt_numerals"])
def test_set_input_is_rejected(method_name: str) -> None:
    """A set is unordered, so its encryption semantics are not stable."""
    ff1 = FF1(key=_VALID_KEY, radix=10)
    method = getattr(ff1, method_name)
    with pytest.raises(TypeError, match="Sequence"):
        method(set(range(6)))  # pyright: ignore[reportArgumentType]


@pytest.mark.parametrize("method_name", ["encrypt_numerals", "decrypt_numerals"])
def test_len_without_sequence_protocol_is_rejected(method_name: str) -> None:
    """``__len__`` alone must not be the gate; a true Sequence is required.

    The old ``hasattr(x, "__len__")`` check accepted this object.  It is not
    a ``Sequence`` (no ``__getitem__``), so it must now raise the same
    TypeError as any other non-Sequence.
    """
    ff1 = FF1(key=_VALID_KEY, radix=10)
    method = getattr(ff1, method_name)
    with pytest.raises(TypeError, match="Sequence"):
        method(_IterOnly())  # pyright: ignore[reportArgumentType]


def test_overlong_input_still_rejected_without_materialising() -> None:
    """The early length rejection must survive the Sequence enforcement.

    ``range`` is a ``Sequence``, so the isinstance gate passes; the length
    check must still reject before any element is read.
    """
    ff1 = FF1(key=_VALID_KEY, radix=10)
    with pytest.raises(LengthError):
        ff1.encrypt_numerals(_ExplodingOnRead())


def test_honest_sequence_still_encrypts() -> None:
    """The gate must not over-reject: a true Sequence of valid length works."""
    ff1 = FF1(key=_VALID_KEY, radix=10)
    plaintext = [1, 2, 3, 4, 5, 6]
    ciphertext = ff1.encrypt_numerals(plaintext)
    assert ff1.decrypt_numerals(ciphertext) == plaintext


@pytest.mark.parametrize("container", [(1, 2, 3, 4, 5, 6), range(1, 7)])
def test_builtin_sequences_still_accepted(container: Any) -> None:
    """list, tuple and range are Sequences and must keep working."""
    ff1 = FF1(key=_VALID_KEY, radix=10)
    expected = ff1.encrypt_numerals([1, 2, 3, 4, 5, 6])
    assert ff1.encrypt_numerals(container) == expected


def test_tweak_validated_before_numerals_are_coerced() -> None:
    """A bad tweak must reject before the O(n) numeral walk (review 00003 L5).

    The input's ``__getitem__`` raises ``AssertionError`` if read, proving the
    coercion never started when the tweak check failed first.
    """

    class _NoRead(Sequence[int]):
        def __len__(self) -> int:
            return 6

        def __getitem__(self, index: int | slice) -> Any:  # pragma: no cover - never reached
            raise AssertionError("numerals must not be read before the tweak check")

    ff1 = FF1(key=_VALID_KEY, radix=10, tweak=b"x", min_tweak_len=1)
    with pytest.raises(TweakLengthError):
        ff1.encrypt_numerals(_NoRead(), tweak=b"")


def test_lying_sequence_with_valid_materialised_length_raises() -> None:
    """Even a materialised length that clears the minimum is a structural fault.

    A ``Sequence`` whose declared and materialised lengths disagree is lying
    about its structure regardless of whether the shorter list happens to
    clear ``min_length``; the mismatch itself must raise a typed error.
    """

    class _UnderReport(Sequence[int]):
        """Declares 7, yields 6 -- both above min_length for radix 10."""

        def __len__(self) -> int:
            return 7

        def __getitem__(self, index: int | slice) -> Any:
            values = [1, 2, 3, 4, 5, 6]
            if isinstance(index, slice):
                return values[index]
            if index >= 6:
                raise IndexError(index)
            return values[index]

    ff1 = FF1(key=_VALID_KEY, radix=10)
    with pytest.raises((LengthError, ValueRangeError)) as excinfo:
        ff1.encrypt_numerals(_UnderReport())
    assert str(excinfo.value)


def test_lying_sequence_zero_yielded_does_not_encrypt() -> None:
    """The headline bypass: zero yielded values previously produced [] ciphertext."""
    ff1 = FF1(key=_VALID_KEY, radix=10)
    with pytest.raises(LengthError):
        ff1.encrypt_numerals(_LyingSequence(0))
