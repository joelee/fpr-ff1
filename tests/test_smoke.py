"""Smoke tests for the fpr-ff1 package."""

import pytest

from fpr_ff1 import (
    FF1,
    AlphabetError,
    FF1Error,
    KeyLengthError,
    LengthError,
    RadixError,
    ValueRangeError,
)


def test_construct_with_valid_key() -> None:
    FF1(key=b"\x00" * 16, radix=10)


def test_invalid_key_length() -> None:
    with pytest.raises(KeyLengthError):
        FF1(key=b"\x00" * 15, radix=10)


def test_invalid_radix() -> None:
    with pytest.raises(RadixError):
        FF1(key=b"\x00" * 16, radix=1)
    with pytest.raises(RadixError):
        FF1(key=b"\x00" * 16, radix=2**16)


def test_alphabet_length_mismatch() -> None:
    with pytest.raises(AlphabetError):
        FF1(key=b"\x00" * 16, radix=10, alphabet="0123456789A")


def test_alphabet_duplicate_characters() -> None:
    with pytest.raises(AlphabetError):
        FF1(key=b"\x00" * 16, radix=10, alphabet="0123456788")


def test_string_interface_requires_alphabet() -> None:
    ff1 = FF1(key=b"\x00" * 16, radix=10)
    with pytest.raises(FF1Error):
        ff1.encrypt("123456")


def test_numeral_out_of_range() -> None:
    ff1 = FF1(key=b"\x00" * 16, radix=10)
    with pytest.raises(ValueRangeError):
        ff1.encrypt_numerals([0, 0, 0, 0, 0, 10])


def test_length_below_minimum() -> None:
    ff1 = FF1(key=b"\x00" * 16, radix=10)
    with pytest.raises(LengthError):
        ff1.encrypt_numerals([0] * 5)


def test_round_trip_string() -> None:
    ff1 = FF1(
        key=b"\x01" * 16,
        radix=10,
        alphabet="0123456789",
    )
    plaintext = "123456789012"
    ciphertext = ff1.encrypt(plaintext)
    decrypted = ff1.decrypt(ciphertext)
    assert decrypted == plaintext
    assert len(ciphertext) == len(plaintext)
