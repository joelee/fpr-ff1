"""Tests for FF1 parameter and input validation.

These tests exercise every rejection path described in AGENTS.md:
key lengths, radix, input lengths, numeral range, tweak bounds, and
alphabet mismatches/duplicates.
"""

from collections.abc import Sequence
from decimal import Decimal
from enum import IntEnum
from fractions import Fraction
from typing import Any

import pytest

from fpr_ff1 import (
    FF1,
    AlphabetError,
    FF1Error,
    KeyLengthError,
    LengthError,
    RadixError,
    TweakLengthError,
    ValueRangeError,
)

_VALID_KEY = b"\x00" * 16


def test_key_length_zero_raises() -> None:
    with pytest.raises(KeyLengthError):
        FF1(key=b"", radix=10)


@pytest.mark.parametrize("key_len", [1, 8, 15, 17, 23, 25, 31, 33, 64])
def test_key_length_invalid_raises(key_len: int) -> None:
    with pytest.raises(KeyLengthError):
        FF1(key=b"\x00" * key_len, radix=10)


@pytest.mark.parametrize("radix", [1, 0, -1, -10])
def test_radix_too_small_raises(radix: int) -> None:
    with pytest.raises(RadixError):
        FF1(key=_VALID_KEY, radix=radix)


@pytest.mark.parametrize("radix", [2**16, 2**16 + 1, 2**20])
def test_radix_too_large_raises(radix: int) -> None:
    with pytest.raises(RadixError):
        FF1(key=_VALID_KEY, radix=radix)


@pytest.mark.parametrize("radix", [2, 3, 10, 36, 256, 2**16 - 1])
def test_radix_boundaries_accepted(radix: int) -> None:
    """Both ends of the legal radix range must construct."""
    assert FF1(key=_VALID_KEY, radix=radix).min_length >= 2


@pytest.mark.parametrize(
    ("radix", "expected"),
    [(2, 20), (10, 6), (16, 5), (32, 4), (36, 4), (256, 3), (2**16 - 1, 2)],
)
def test_min_length_for_radix(radix: int, expected: int) -> None:
    """min_length is the smallest n with radix**n >= 1_000_000."""
    ff1 = FF1(key=_VALID_KEY, radix=radix)
    assert ff1.min_length == expected
    assert radix**expected >= 1_000_000
    assert radix ** (expected - 1) < 1_000_000


def test_max_length_is_one_below_two_to_the_32() -> None:
    """SP 800-38G specifies maxlen < 2**32, so the bound is 2**32 - 1."""
    assert FF1(key=_VALID_KEY, radix=10).max_length == 2**32 - 1


def test_default_tweak_too_short_raises() -> None:
    with pytest.raises(TweakLengthError):
        FF1(key=_VALID_KEY, radix=10, tweak=b"", min_tweak_len=1)


def test_default_tweak_too_long_raises() -> None:
    with pytest.raises(TweakLengthError):
        FF1(key=_VALID_KEY, radix=10, tweak=b"abc", max_tweak_len=2)


def test_call_tweak_too_short_raises() -> None:
    ff1 = FF1(key=_VALID_KEY, radix=10, tweak=b"x", min_tweak_len=1)
    with pytest.raises(TweakLengthError):
        ff1.encrypt_numerals([0] * 6, tweak=b"")


def test_call_tweak_too_long_raises() -> None:
    ff1 = FF1(key=_VALID_KEY, radix=10, max_tweak_len=2)
    with pytest.raises(TweakLengthError):
        ff1.encrypt_numerals([0] * 6, tweak=b"abc")


def test_plaintext_too_short_raises() -> None:
    ff1 = FF1(key=_VALID_KEY, radix=10)
    with pytest.raises(LengthError):
        ff1.encrypt_numerals([0] * 5)


def test_plaintext_too_long_raises() -> None:
    """Over-long input is rejected without being materialised.

    ``range`` supplies the length lazily, so this costs O(1) memory.  Building
    a real ``[0] * (2**32 + 1)`` list would need roughly 34 GB and be
    OOM-killed on a normal CI runner.
    """
    ff1 = FF1(key=_VALID_KEY, radix=10)
    with pytest.raises(LengthError):
        ff1.encrypt_numerals(range(2**32 + 1))


def test_ciphertext_too_long_raises() -> None:
    ff1 = FF1(key=_VALID_KEY, radix=10)
    with pytest.raises(LengthError):
        ff1.decrypt_numerals(range(2**32 + 1))


def test_max_length_input_is_not_materialised() -> None:
    """The length check must run before the input is copied.

    Guards the ordering in ``_prepare``: a sequence that raises on iteration
    still fails on length, proving no copy was attempted.
    """

    class ExplodingSequence(Sequence[int]):
        def __len__(self) -> int:
            return 2**32 + 1

        def __getitem__(self, index: int | slice) -> Any:  # pragma: no cover - never reached
            raise AssertionError("input must not be read before the length check")

    ff1 = FF1(key=_VALID_KEY, radix=10)
    with pytest.raises(LengthError):
        ff1.encrypt_numerals(ExplodingSequence())


def test_numeral_negative_raises() -> None:
    ff1 = FF1(key=_VALID_KEY, radix=10)
    with pytest.raises(ValueRangeError):
        ff1.encrypt_numerals([0, 0, 0, 0, 0, -1])


def test_numeral_too_large_raises() -> None:
    ff1 = FF1(key=_VALID_KEY, radix=10)
    with pytest.raises(ValueRangeError):
        ff1.encrypt_numerals([0, 0, 0, 0, 0, 10])


def test_alphabet_wrong_length_raises() -> None:
    with pytest.raises(AlphabetError):
        FF1(key=_VALID_KEY, radix=10, alphabet="012345678")


def test_alphabet_duplicate_raises() -> None:
    with pytest.raises(AlphabetError):
        FF1(key=_VALID_KEY, radix=10, alphabet="0123456789a")


def test_string_interface_without_alphabet_raises() -> None:
    ff1 = FF1(key=_VALID_KEY, radix=10)
    with pytest.raises(FF1Error):
        ff1.encrypt("012345")
    with pytest.raises(FF1Error):
        ff1.decrypt("012345")


def test_string_character_not_in_alphabet_raises() -> None:
    """A character outside the alphabet must raise a typed FF1 error.

    Regression guard: this previously escaped as a bare ``KeyError``, which is
    outside the documented ``FF1Error`` hierarchy.

    The message must locate the offending position but must **not** echo the
    offending character: validation exceptions are routinely logged, and a
    rejected plaintext symbol landing in a log contradicts the package's own
    security policy (``SECURITY.md`` scope: anything that causes plaintext to
    be logged or raised in a message).  Review 00003 B3 / review 00004 MAJ-03.
    """
    ff1 = FF1(key=_VALID_KEY, radix=10, alphabet="0123456789")
    for method in (ff1.encrypt, ff1.decrypt):
        with pytest.raises(ValueRangeError) as excinfo:
            method("01234a")
        assert issubclass(excinfo.type, FF1Error)
        assert not issubclass(excinfo.type, KeyError)
        # The message must locate the offending character...
        assert "index 5" in str(excinfo.value)
        # ...without disclosing it.  The old message embedded the character
        # via ``{ch!r}``; its quoted form must be absent.
        assert "'a'" not in str(excinfo.value)


def test_numeral_out_of_range_does_not_disclose_value() -> None:
    """An out-of-range numeral must be located but never echoed.

    Same policy as the character case above: the index and the failure kind
    are safe to log; the rejected value is plaintext data.
    """
    ff1 = FF1(key=_VALID_KEY, radix=10)
    for method in (ff1.encrypt_numerals, ff1.decrypt_numerals):
        with pytest.raises(ValueRangeError) as excinfo:
            method([1, 2, 3, 4, 5, 42])
        message = str(excinfo.value)
        assert "[5]" in message
        assert "42" not in message


def test_negative_numeral_does_not_disclose_value() -> None:
    """The negative branch of the range check redacts too."""
    ff1 = FF1(key=_VALID_KEY, radix=10)
    with pytest.raises(ValueRangeError) as excinfo:
        ff1.encrypt_numerals([1, 2, 3, 4, 5, -7])
    message = str(excinfo.value)
    assert "[5]" in message
    assert "-7" not in message


def test_decryption_input_out_of_range_raises() -> None:
    ff1 = FF1(key=_VALID_KEY, radix=10)
    with pytest.raises(ValueRangeError):
        ff1.decrypt_numerals([0, 0, 0, 0, 0, 10])


@pytest.mark.parametrize("radix", [2, 10, 16, 36, 256, 2**16 - 1])
def test_length_at_min_length_exactly_succeeds(radix: int) -> None:
    """The lower bound is inclusive: min_length itself must encrypt."""
    ff1 = FF1(key=_VALID_KEY, radix=radix)
    plaintext = [0] * ff1.min_length
    ciphertext = ff1.encrypt_numerals(plaintext)
    assert len(ciphertext) == ff1.min_length
    assert ff1.decrypt_numerals(ciphertext) == plaintext


@pytest.mark.parametrize("radix", [2, 10, 16, 36, 256, 2**16 - 1])
def test_one_below_min_length_raises(radix: int) -> None:
    ff1 = FF1(key=_VALID_KEY, radix=radix)
    with pytest.raises(LengthError):
        ff1.encrypt_numerals([0] * (ff1.min_length - 1))


def test_empty_tweak_equals_absent_tweak() -> None:
    """An explicit empty tweak and an omitted tweak must be identical."""
    ff1 = FF1(key=_VALID_KEY, radix=10)
    plaintext = [1, 2, 3, 4, 5, 6]
    assert ff1.encrypt_numerals(plaintext, b"") == ff1.encrypt_numerals(plaintext)
    assert ff1.encrypt_numerals(plaintext, None) == ff1.encrypt_numerals(plaintext, b"")


@pytest.mark.parametrize("tweak_len", [0, 1, 16, 255, 1024, 4096])
def test_long_tweaks_are_accepted(tweak_len: int) -> None:
    """With no configured bounds, a tweak of any length is valid."""
    ff1 = FF1(key=_VALID_KEY, radix=10)
    plaintext = [1, 2, 3, 4, 5, 6]
    tweak = bytes(i % 256 for i in range(tweak_len))
    ciphertext = ff1.encrypt_numerals(plaintext, tweak)
    assert ff1.decrypt_numerals(ciphertext, tweak) == plaintext


@pytest.mark.parametrize("radix", [2, 10, 36, 256, 2**16 - 1])
def test_all_zero_and_all_max_numerals(radix: int) -> None:
    """The arithmetic corner cases: NUM_radix(X) == 0 and == radix**n - 1."""
    ff1 = FF1(key=_VALID_KEY, radix=radix)
    n = ff1.min_length + 1  # odd/even mix across radices
    for numeral in (0, radix - 1):
        plaintext = [numeral] * n
        ciphertext = ff1.encrypt_numerals(plaintext)
        assert len(ciphertext) == n
        assert all(0 <= value < radix for value in ciphertext)
        assert ff1.decrypt_numerals(ciphertext) == plaintext


@pytest.mark.parametrize("n", [6, 7, 8, 9, 20, 21])
def test_odd_and_even_lengths(n: int) -> None:
    """n odd exercises the u != v path; n even exercises u == v."""
    ff1 = FF1(key=_VALID_KEY, radix=10)
    plaintext = [(i * 3) % 10 for i in range(n)]
    ciphertext = ff1.encrypt_numerals(plaintext)
    assert ff1.decrypt_numerals(ciphertext) == plaintext


# --- Type validation (review 45bc40f, finding K1) -----------------------------
#
# Comparison alone is not a type gate: `1.0 < 10` is True, so a float numeral
# used to pass validation and then crash in `_encode_uint` with AttributeError
# -- outside the FF1Error hierarchy the contract and README both promise.


class _Comparable:
    """An object that compares against int but is not a numeral."""

    def __lt__(self, other: object) -> bool:
        return True

    def __ge__(self, other: object) -> bool:
        return False


@pytest.mark.parametrize(
    "value",
    [
        pytest.param(1.0, id="float"),
        pytest.param(True, id="bool-true"),
        pytest.param(False, id="bool-false"),
        pytest.param("1", id="str"),
        pytest.param(Decimal(1), id="decimal"),
        pytest.param(Fraction(1, 1), id="fraction"),
        pytest.param(None, id="none"),
        pytest.param(_Comparable(), id="comparable-object"),
        pytest.param([1], id="list"),
    ],
)
def test_non_integer_numerals_raise_typed_error(value: object) -> None:
    """Non-integer numerals must raise ValueRangeError, never a bare builtin."""
    ff1 = FF1(key=_VALID_KEY, radix=10)
    with pytest.raises(ValueRangeError) as excinfo:
        ff1.encrypt_numerals([value, 1, 2, 3, 4, 5])  # pyright: ignore[reportArgumentType]
    assert "plaintext[0]" in str(excinfo.value)
    assert issubclass(excinfo.type, FF1Error)


def test_integer_like_numerals_are_accepted() -> None:
    """The type gate must not over-reject genuine integers.

    ``IntEnum`` and any object implementing ``__index__`` are losslessly
    integral and must still work.
    """

    class Digit(IntEnum):
        ZERO = 0
        ONE = 1

    class Indexable:
        def __index__(self) -> int:
            return 2

    ff1 = FF1(key=_VALID_KEY, radix=10)
    expected = ff1.encrypt_numerals([0, 1, 2, 0, 1, 2])
    mixed = [Digit.ZERO, Digit.ONE, Indexable(), Digit.ZERO, Digit.ONE, Indexable()]
    assert ff1.encrypt_numerals(mixed) == expected  # pyright: ignore[reportArgumentType]


def test_integer_like_numerals_are_normalised_to_int() -> None:
    """Values are converted, not just checked.

    Fixed-width integers from other numeric libraries must not reach the
    big-integer arithmetic, where they could overflow silently.
    """

    class Indexable:
        def __index__(self) -> int:
            return 3

    ff1 = FF1(key=_VALID_KEY, radix=10)
    numerals = ff1.encrypt_numerals([Indexable()] * 6)  # pyright: ignore[reportArgumentType]
    assert all(type(value) is int for value in numerals)


@pytest.mark.parametrize(
    ("kwargs", "expected"),
    [
        pytest.param({"key": "0" * 16, "radix": 10}, KeyLengthError, id="key-str"),
        pytest.param({"key": _VALID_KEY, "radix": 10.0}, RadixError, id="radix-float"),
        pytest.param({"key": _VALID_KEY, "radix": Decimal(10)}, RadixError, id="radix-decimal"),
        pytest.param({"key": _VALID_KEY, "radix": "10"}, RadixError, id="radix-str"),
        pytest.param(
            {"key": _VALID_KEY, "radix": 10, "alphabet": list("0123456789")},
            AlphabetError,
            id="alphabet-list",
        ),
        pytest.param(
            {"key": _VALID_KEY, "radix": 10, "tweak": "abc"}, TweakLengthError, id="tweak-str"
        ),
        pytest.param(
            {"key": _VALID_KEY, "radix": 10, "min_tweak_len": 1.5},
            TweakLengthError,
            id="min-tweak-float",
        ),
        pytest.param(
            {"key": _VALID_KEY, "radix": 10, "max_tweak_len": "4"},
            TweakLengthError,
            id="max-tweak-str",
        ),
    ],
)
def test_constructor_type_errors(kwargs: dict[str, Any], expected: type[FF1Error]) -> None:
    with pytest.raises(expected):
        FF1(**kwargs)


@pytest.mark.parametrize("key", [b"\x00" * 16, bytearray(16), memoryview(b"\x00" * 16)])
def test_bytes_like_keys_and_tweaks_accepted(key: object) -> None:
    """bytes, bytearray and memoryview are all valid byte sources."""
    ff1 = FF1(key=key, radix=10, tweak=bytearray(b"abc"))  # pyright: ignore[reportArgumentType]
    assert ff1.encrypt_numerals([1, 2, 3, 4, 5, 6]) == FF1(
        key=b"\x00" * 16, radix=10, tweak=b"abc"
    ).encrypt_numerals([1, 2, 3, 4, 5, 6])


def test_call_time_tweak_type_is_checked() -> None:
    ff1 = FF1(key=_VALID_KEY, radix=10)
    with pytest.raises(TweakLengthError):
        ff1.encrypt_numerals([1, 2, 3, 4, 5, 6], "abc")  # pyright: ignore[reportArgumentType]


def test_generator_raises_typeerror_with_actionable_message() -> None:
    """A generator is API misuse, not bad data, so TypeError is correct.

    The annotation says ``Sequence[int]``; the message should say so too rather
    than surfacing a bare "object of type 'generator' has no len()".
    """
    ff1 = FF1(key=_VALID_KEY, radix=10)
    with pytest.raises(TypeError, match="Sequence"):
        ff1.encrypt_numerals(value for value in [1, 2, 3, 4, 5, 6])  # pyright: ignore[reportArgumentType]


@pytest.mark.parametrize("value", [123456, list("123456"), b"123456", None])
def test_string_interface_rejects_non_str(value: object) -> None:
    ff1 = FF1(key=_VALID_KEY, radix=10, alphabet="0123456789")
    for method in (ff1.encrypt, ff1.decrypt):
        with pytest.raises(ValueRangeError):
            method(value)  # pyright: ignore[reportArgumentType]


def test_mutable_key_and_tweak_are_copied_at_construction() -> None:
    """A caller mutating its bytearray afterwards must not change behaviour.

    ``_require_bytes`` normalises to immutable ``bytes``; without that, an
    instance would silently track later edits to the caller's buffer.
    """
    key = bytearray(b"\x00" * 16)
    tweak = bytearray(b"abc")
    ff1 = FF1(key=key, radix=10, tweak=tweak)  # pyright: ignore[reportArgumentType]
    before = ff1.encrypt_numerals([1, 2, 3, 4, 5, 6])

    key[0] = 0xFF
    tweak[0] = 0xFF

    assert ff1.encrypt_numerals([1, 2, 3, 4, 5, 6]) == before


# --- Tweak bound configuration (review 45bc40f, finding K2) --------------------


@pytest.mark.parametrize(
    ("min_len", "max_len"),
    [(8, 4), (1, 0), (100, 99), (2, 1)],
)
def test_inverted_tweak_bounds_rejected_at_construction(min_len: int, max_len: int) -> None:
    """Unsatisfiable bounds must be reported as a configuration fault.

    These already failed, but with a message about whichever bound the default
    tweak happened to violate first -- true, yet pointing at the tweak when the
    real problem is that no tweak could ever satisfy both.
    """
    with pytest.raises(TweakLengthError) as excinfo:
        FF1(key=_VALID_KEY, radix=10, min_tweak_len=min_len, max_tweak_len=max_len)

    message = str(excinfo.value)
    assert "min_tweak_len" in message and "max_tweak_len" in message
    assert "satisfy both" in message


def test_inverted_bounds_reported_regardless_of_default_tweak() -> None:
    """The configuration check must not depend on the default tweak's length."""
    for tweak in (b"", b"xx", b"x" * 8, b"x" * 20):
        with pytest.raises(TweakLengthError, match="satisfy both"):
            FF1(key=_VALID_KEY, radix=10, tweak=tweak, min_tweak_len=8, max_tweak_len=4)


@pytest.mark.parametrize(
    ("min_len", "max_len"),
    [
        pytest.param(-1, None, id="min-negative"),
        pytest.param(-5, None, id="min-very-negative"),
        pytest.param(None, -1, id="max-negative"),
        pytest.param(-2, -1, id="both-negative"),
        pytest.param(-1, 8, id="min-negative-max-valid"),
    ],
)
def test_negative_tweak_bounds_rejected(min_len: int | None, max_len: int | None) -> None:
    """A negative bound is silently inert, which is not what the caller asked for."""
    with pytest.raises(TweakLengthError, match="non-negative"):
        FF1(key=_VALID_KEY, radix=10, min_tweak_len=min_len, max_tweak_len=max_len)


@pytest.mark.parametrize(
    ("min_len", "max_len", "tweak"),
    [
        (4, 4, b"abcd"),  # min == max is a valid, satisfiable bound
        (0, 0, b""),  # zero-length tweak pinned exactly
        (0, 16, b"abc"),
        (2, 8, b"abcd"),
        (None, 8, b"abcd"),
        (2, None, b"abcd"),
    ],
)
def test_valid_tweak_bounds_accepted(
    min_len: int | None, max_len: int | None, tweak: bytes
) -> None:
    """Satisfiable configurations, including the min == max boundary, must work."""
    ff1 = FF1(
        key=_VALID_KEY,
        radix=10,
        tweak=tweak,
        min_tweak_len=min_len,
        max_tweak_len=max_len,
    )
    plaintext = [1, 2, 3, 4, 5, 6]
    assert ff1.decrypt_numerals(ff1.encrypt_numerals(plaintext)) == plaintext


def test_tweak_bound_violations_still_name_the_tweak() -> None:
    """Data faults must not be relabelled as configuration faults.

    Guards the boundary: after adding the config checks, a tweak that violates
    a perfectly valid bound must still produce a message about the tweak.
    """
    ff1 = FF1(key=_VALID_KEY, radix=10, tweak=b"abcd", min_tweak_len=2, max_tweak_len=8)
    numerals = [1, 2, 3, 4, 5, 6]

    with pytest.raises(TweakLengthError, match="below minimum") as short:
        ff1.encrypt_numerals(numerals, b"x")
    assert "satisfy both" not in str(short.value)

    with pytest.raises(TweakLengthError, match="above maximum") as long:
        ff1.encrypt_numerals(numerals, b"x" * 99)
    assert "satisfy both" not in str(long.value)
