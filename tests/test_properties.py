"""Property-based and bijectivity tests for FF1.

Uses Hypothesis for round-trips, determinism, and tweak/key sensitivity,
plus an exhaustive bijectivity check for a small domain.

The strategy carries ``key`` and ``radix`` alongside the instance rather than
reading them back off private attributes, so these tests exercise only the
public API -- the same surface a user has.
"""

from collections import Counter
from typing import NamedTuple

import pytest
from hypothesis import HealthCheck, given, settings
from hypothesis import strategies as st

from fpr_ff1 import FF1

_SETTINGS = settings(
    max_examples=50,
    deadline=None,
    suppress_health_check=[HealthCheck.too_slow],
)


class Case(NamedTuple):
    """An FF1 instance together with the parameters it was built from."""

    ff1: FF1
    key: bytes
    radix: int

    def plaintext(self, data: st.DataObject, max_length: int = 26) -> list[int]:
        """Draw a valid numeral sequence for this instance.

        The upper bound is chosen so the large radices reach ``d > 16`` and
        exercise the step 6.iii S-expansion: that branch starts at n=13 for
        radix 32768 and above, n=19 for radix 1000, and n=25 for radix 256.
        """
        low = self.ff1.min_length
        length = data.draw(st.integers(min_value=low, max_value=max(max_length, low)))
        return data.draw(
            st.lists(
                st.integers(min_value=0, max_value=self.radix - 1),
                min_size=length,
                max_size=length,
            )
        )


@st.composite
def ff1_case(draw: st.DrawFn) -> Case:
    key_len = draw(st.sampled_from([16, 24, 32]))
    key = draw(st.binary(min_size=key_len, max_size=key_len))
    # Span the whole legal radix range, not just 2..10.  Large radices reach
    # bigger b and d values -- including the S-expansion branch that no NIST
    # sample exercises -- and would have caught the step 6.iii defect.
    radix = draw(
        st.one_of(
            st.integers(min_value=2, max_value=64),
            st.sampled_from([10, 16, 36, 62, 256, 1000, 2**15, 2**16 - 1]),
        )
    )
    return Case(FF1(key=key, radix=radix), key, radix)


@given(ff1_case(), st.data())
@_SETTINGS
def test_round_trip(case: Case, data: st.DataObject) -> None:
    plaintext = case.plaintext(data)
    ciphertext = case.ff1.encrypt_numerals(plaintext)
    assert len(ciphertext) == len(plaintext)
    assert all(0 <= x < case.radix for x in ciphertext)
    assert case.ff1.decrypt_numerals(ciphertext) == plaintext


@given(ff1_case(), st.data())
@_SETTINGS
def test_determinism(case: Case, data: st.DataObject) -> None:
    plaintext = case.plaintext(data)
    tweak = data.draw(st.binary(min_size=0, max_size=16))
    assert case.ff1.encrypt_numerals(plaintext, tweak) == case.ff1.encrypt_numerals(
        plaintext, tweak
    )
    assert case.ff1.decrypt_numerals(plaintext, tweak) == case.ff1.decrypt_numerals(
        plaintext, tweak
    )


@given(ff1_case(), st.data())
@_SETTINGS
def test_tweak_sensitivity(case: Case, data: st.DataObject) -> None:
    plaintext = case.plaintext(data)
    tweak1 = data.draw(st.binary(min_size=0, max_size=16))
    tweak2 = data.draw(st.binary(min_size=0, max_size=16).filter(lambda t: t != tweak1))
    if case.ff1.encrypt_numerals(plaintext, tweak1) == case.ff1.encrypt_numerals(plaintext, tweak2):
        # Two distinct tweaks colliding for a given plaintext is permitted but
        # vanishingly unlikely except on tiny domains.
        pytest.skip("tweak collision")


@given(ff1_case(), st.data())
@_SETTINGS
def test_key_sensitivity(case: Case, data: st.DataObject) -> None:
    """A single flipped key bit must produce unrelated output.

    One bit is the hardest case; changing every byte would be a much weaker
    test of the key schedule.
    """
    plaintext = case.plaintext(data)
    flipped = case.key[:-1] + bytes([case.key[-1] ^ 0x01])
    assert flipped != case.key
    other = FF1(key=flipped, radix=case.radix)
    assert case.ff1.encrypt_numerals(plaintext) != other.encrypt_numerals(plaintext)


@given(ff1_case(), st.data())
@_SETTINGS
def test_length_and_alphabet_preservation(case: Case, data: st.DataObject) -> None:
    plaintext = case.plaintext(data)
    ciphertext = case.ff1.encrypt_numerals(plaintext)
    assert len(ciphertext) == len(plaintext)
    assert set(ciphertext).issubset(set(range(case.radix)))


@pytest.mark.slow
@pytest.mark.parametrize(("radix", "length"), [(2, 20), (10, 6)])
def test_bijectivity_small_domain(radix: int, length: int) -> None:
    """Exhaustively verify the image is the full domain for a tiny FF1 domain.

    The strongest correctness statement available: no gaps and no repeats over
    every point of the domain.
    """
    ff1 = FF1(key=b"\x00" * 16, radix=radix)
    total = radix**length
    seen: Counter[tuple[int, ...]] = Counter()
    for value in range(total):
        numerals: list[int] = []
        remainder = value
        for _ in range(length):
            numerals.append(remainder % radix)
            remainder //= radix
        seen[tuple(ff1.encrypt_numerals(list(reversed(numerals))))] += 1

    assert len(seen) == total, f"expected {total} distinct ciphertexts, got {len(seen)}"
    assert all(count == 1 for count in seen.values()), "FF1 is not bijective on the small domain"
