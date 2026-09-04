"""Differential tests against an independent FF1 implementation.

AGENTS.md section 7: radices 10 and 36 have NIST vectors; every other radix has
none.  Correctness for the rest is established only by agreement with an
independent implementation.

Just as importantly, the NIST samples never exercise the whole algorithm.  The
largest ``d`` across all nine published samples is 12, so the step 6.iii
``S``-expansion loop -- taken only when ``d > 16`` -- is dead code under the
published vectors.  Round-trip and property tests cannot cover it either:
encrypt and decrypt share that code, so a wrong ``S`` still round-trips
cleanly.  Only an independent oracle catches it.  See
``test_s_expansion_boundary`` below.

The frozen KAT vectors live in ``tests/test_frozen_kat.py``: the oracle is
deprecated and unmaintained, and the day it stops installing the live tests
above go dark.  That module carries the same evidence forward, with no oracle
dependency.
"""

import string
from typing import Any

import pytest

from fpr_ff1 import FF1
from tests._oracle import load_oracle_or_none

_oracle = load_oracle_or_none()

pytestmark = pytest.mark.skipif(
    _oracle is None,
    reason="ubiq-security-fpe oracle not installed",
)

_BASE36 = string.digits + string.ascii_lowercase
_KEY = bytes(range(16))
_TWEAK = bytes.fromhex("393837")


def _alphabet_for(radix: int) -> str:
    """An alphabet of exactly ``radix`` distinct characters.

    Above base36 the characters come from the supplementary plane, which is
    contiguous and free of surrogates -- a lone surrogate would be a valid
    ``str`` element but would break the moment anything encoded it.
    """
    if radix <= len(_BASE36):
        return _BASE36[:radix]
    return "".join(chr(0x10000 + i) for i in range(radix))


def _plaintext(n: int, alphabet: str) -> str:
    """Deterministic, non-degenerate plaintext of length ``n``."""
    return "".join(alphabet[(i * 7 + n) % len(alphabet)] for i in range(n))


def _oracle_context(key: bytes, tweak: bytes, radix: int, alphabet: str) -> Any:
    assert _oracle is not None
    return _oracle.Context(key, tweak, 0, 0, radix, alphabet)


def _expansion_blocks(d: int) -> int:
    """Number of ``CIPH_K`` blocks appended to R to reach ``d`` bytes."""
    length = 16
    blocks = 0
    while length < d:
        length += 16
        blocks += 1
    return blocks


def test_oracle_agrees_with_nist_vectors(nist_samples: list[dict[str, Any]]) -> None:
    """Validate the oracle before trusting it as a reference.

    An oracle that has not itself been checked against the published vectors is
    worse than no oracle: it lends false authority to whatever it produces.
    """
    for vector in nist_samples:
        context = _oracle_context(
            bytes.fromhex(vector["key"]),
            bytes.fromhex(vector["tweak"]),
            vector["radix"],
            vector["alphabet"],
        )
        assert context.Encrypt(vector["plaintext"], None) == vector["ciphertext"], (
            f"oracle disagrees with NIST sample {vector['name']!r}; "
            "it must not be used as a differential reference"
        )


def _min_length(radix: int) -> int:
    return FF1(key=_KEY, radix=radix).min_length


#: Every (radix, n) pair that is actually valid, computed up front.  Filtering
#: here rather than calling pytest.skip() inside the test keeps the run free of
#: skips, so a genuinely skipped oracle suite stands out instead of blending
#: into dozens of routine ones.
_LENGTH_CASES = [(radix, n) for radix in (10, 16, 36) for n in range(_min_length(radix), 70)]


@pytest.mark.parametrize(("radix", "n"), _LENGTH_CASES)
def test_encrypt_matches_oracle(radix: int, n: int) -> None:
    """Byte-exact agreement with the oracle across the full length range."""
    alphabet = _alphabet_for(radix)
    ff1 = FF1(key=_KEY, radix=radix, alphabet=alphabet, tweak=_TWEAK)

    plaintext = _plaintext(n, alphabet)
    expected = _oracle_context(_KEY, _TWEAK, radix, alphabet).Encrypt(plaintext, None)

    assert ff1.encrypt(plaintext) == expected


@pytest.mark.parametrize(("radix", "n"), _LENGTH_CASES)
def test_decrypt_matches_oracle(radix: int, n: int) -> None:
    alphabet = _alphabet_for(radix)
    ff1 = FF1(key=_KEY, radix=radix, alphabet=alphabet, tweak=_TWEAK)

    ciphertext = _plaintext(n, alphabet)
    expected = _oracle_context(_KEY, _TWEAK, radix, alphabet).Decrypt(ciphertext, None)

    assert ff1.decrypt(ciphertext) == expected


@pytest.mark.parametrize(
    ("radix", "n", "expected_b", "expected_d", "expected_blocks"),
    [
        # d == 16: the largest S that fits in R alone.  The loop never runs;
        # this is the regime every NIST sample lives in.
        (10, 56, 12, 16, 0),
        # d == 20: first length that needs an expansion block (j == 1).
        (10, 57, 13, 20, 1),
        (36, 37, 13, 20, 1),
        (256, 25, 13, 20, 1),
        # d == 36: two expansion blocks (j == 1 and j == 2).  A single-block
        # case cannot catch an off-by-one in the counter, since j is only ever
        # 1 there.  Note d == 32 still needs just one block, because S starts
        # at 16 bytes.
        (10, 135, 29, 36, 2),
        (36, 87, 29, 36, 2),
        (256, 57, 29, 36, 2),
    ],
)
def test_s_expansion_boundary(
    radix: int,
    n: int,
    expected_b: int,
    expected_d: int,
    expected_blocks: int,
) -> None:
    """Cover each ``d`` transition where the S-expansion loop engages.

    Guards the SP 800-38G Algorithm 7 step 6.iii construction
    ``CIPH_K(R XOR [j]^16)``.  No NIST sample reaches ``d > 16``.
    """
    alphabet = _alphabet_for(radix)
    ff1 = FF1(key=_KEY, radix=radix, alphabet=alphabet, tweak=_TWEAK)

    # Confirm the case really does target the intended branch.
    v = n - n // 2
    b = ((radix**v - 1).bit_length() + 7) // 8
    d = 4 * ((b + 3) // 4) + 4
    assert (b, d) == (expected_b, expected_d), f"case drifted: got b={b}, d={d}"
    assert _expansion_blocks(d) == expected_blocks, "case no longer targets the intended branch"

    plaintext = _plaintext(n, alphabet)
    expected = _oracle_context(_KEY, _TWEAK, radix, alphabet).Encrypt(plaintext, None)

    ciphertext = ff1.encrypt(plaintext)
    assert ciphertext == expected
    assert ff1.decrypt(ciphertext) == plaintext


@pytest.mark.parametrize("radix", [2, 16, 32, 62, 256, 2**16 - 1])
@pytest.mark.parametrize("offset", [0, 1, 2, 7, 20])
def test_radices_without_nist_vectors_match_oracle(radix: int, offset: int) -> None:
    """Radices 2, 16, 32, 62, 256 and 65535 have no published vectors.

    AGENTS.md section 7: for these, correctness is established only by
    agreement with an independent implementation.  Lengths are taken relative
    to ``min_length`` so each radix is exercised from its own lower bound
    upward, including odd and even ``n`` (the ``u != v`` path).
    """
    alphabet = _alphabet_for(radix)
    ff1 = FF1(key=_KEY, radix=radix, alphabet=alphabet, tweak=_TWEAK)
    n = ff1.min_length + offset

    plaintext = _plaintext(n, alphabet)
    context = _oracle_context(_KEY, _TWEAK, radix, alphabet)

    ciphertext = ff1.encrypt(plaintext)
    assert ciphertext == context.Encrypt(plaintext, None)
    assert ff1.decrypt(ciphertext) == plaintext


@pytest.mark.parametrize("radix", [2, 10, 36, 256])
def test_degenerate_inputs_match_oracle(radix: int) -> None:
    """All-zero and all-max numerals are the arithmetic corner cases."""
    alphabet = _alphabet_for(radix)
    ff1 = FF1(key=_KEY, radix=radix, alphabet=alphabet, tweak=_TWEAK)
    n = ff1.min_length + 1
    context = _oracle_context(_KEY, _TWEAK, radix, alphabet)

    for symbol in (alphabet[0], alphabet[-1]):
        plaintext = symbol * n
        ciphertext = ff1.encrypt(plaintext)
        assert ciphertext == context.Encrypt(plaintext, None)
        assert ff1.decrypt(ciphertext) == plaintext


@pytest.mark.parametrize("tweak_len", [0, 1, 15, 16, 17, 64])
def test_tweak_lengths_match_oracle(tweak_len: int) -> None:
    """Tweak length shifts the Q-block padding; verify each residue class."""
    radix = 10
    alphabet = _alphabet_for(radix)
    tweak = bytes(range(tweak_len))
    plaintext = _plaintext(20, alphabet)

    ff1 = FF1(key=_KEY, radix=radix, alphabet=alphabet, tweak=tweak)
    expected = _oracle_context(_KEY, tweak, radix, alphabet).Encrypt(plaintext, None)

    assert ff1.encrypt(plaintext) == expected


@pytest.mark.parametrize("key_len", [16, 24, 32])
def test_all_key_sizes_match_oracle(key_len: int) -> None:
    radix = 36
    alphabet = _alphabet_for(radix)
    key = bytes(range(key_len))
    plaintext = _plaintext(40, alphabet)

    ff1 = FF1(key=key, radix=radix, alphabet=alphabet, tweak=_TWEAK)
    expected = _oracle_context(key, _TWEAK, radix, alphabet).Encrypt(plaintext, None)

    assert ff1.encrypt(plaintext) == expected
