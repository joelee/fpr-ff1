"""Differential-equivalence and boundary tests for the radix conversions.

SP 800-38G Algorithm 7 converts between a numeral sequence and a big
integer ten times per call (NUM_radix at step 6.i, STR_radix at step
6.vii). The shipped conversion is a digit-at-a-time loop, which is
quadratic in the number of numerals; plan 00003 (idea 00001 r02,
re-baselined by review 00005) replaces it with a subquadratic
divide-and-conquer conversion plus a power-of-two fast path while
retaining the naive loops as the documented spec reference.

This module is the equivalence oracle for that change
(PLAN-00003-REQ-03, PLAN-00003-REQ-04):

- the production conversion must be bit-identical to an independent
  transcription of the naive loops across every supported radix, at
  degenerate lengths, at the recursion-threshold boundaries
  (63/64/65/128/129 around the future 64-numeral threshold), and under
  property-based sampling; and
- full FF1 round trips must succeed at the boundary lengths.

The reference lives here, in the test module, rather than being imported
from the code under test, so the oracle cannot drift along with an
optimisation. Until the subquadratic conversion lands
(PLAN-00003-STEP-02), the production helpers ARE the naive loops, so the
differential compares the naive loops to an independent copy of
themselves and is trivially green. STEP-02 retains the loops in `_ff1`
under the `_num_radix_reference`/`_str_radix_reference` names; the
pinning test below then exercises that retained copy against this
transcription, keeping it inside the differential and the coverage floor.
"""

from __future__ import annotations

from collections.abc import Callable, Sequence

import pytest
from hypothesis import HealthCheck, given, settings
from hypothesis import strategies as st

from fpr_ff1 import FF1
from fpr_ff1 import _ff1 as _ff1_module  # pyright: ignore[reportPrivateUsage]
from fpr_ff1._ff1 import _num_radix, _str_radix  # pyright: ignore[reportPrivateUsage]

#: The retained reference names STEP-02 gives the naive loops inside
#: ``_ff1``; ``None`` until that step lands. Resolved dynamically against
#: a declared type so this module type-checks in both states and exercises
#: the retained functions the moment they exist.
_retained_num_radix: Callable[[int, Sequence[int]], int] | None = getattr(
    _ff1_module, "_num_radix_reference", None
)
_retained_str_radix: Callable[[int, int, int], list[int]] | None = getattr(
    _ff1_module, "_str_radix_reference", None
)

#: Every radix the package accepts: 2 <= radix < 2**16 (AGENTS.md subset).
_SUPPORTED_RADICES = range(2, 2**16)

#: Lengths around the future 64-numeral divide-and-conquer threshold, with
#: odd and even values so both split parities are exercised.
_BOUNDARY_LENGTHS = [63, 64, 65, 128, 129]

#: Radices spanning the supported range: minimum, NIST-sample, common
#: alphabet, power-of-two, and the supported maximum.
_REPRESENTATIVE_RADICES = [2, 10, 36, 256, 65535]

_SETTINGS = settings(
    max_examples=50,
    deadline=None,
    suppress_health_check=[HealthCheck.too_slow],
)


def _reference_num_radix(radix: int, numerals: Sequence[int]) -> int:
    """Independent transcription of SP 800-38G NUM_radix (the naive loop).

    Deliberately not imported from ``_ff1``: a differential oracle must
    not be modifiable by the same change it guards.
    """
    value = 0
    for x in numerals:
        value = value * radix + x
    return value


def _reference_str_radix(value: int, radix: int, length: int) -> list[int]:
    """Independent transcription of SP 800-38G STR_radix (the naive loop)."""
    out = [0] * length
    for i in range(length - 1, -1, -1):
        out[i] = value % radix
        value //= radix
    return out


def _pseudo_numerals(radix: int, length: int) -> list[int]:
    """Deterministic, well-spread numerals in ``[0, radix)``.

    A fixed polynomial pattern rather than randomness: a differential must
    fail identically on every run, and seeded randomness would make a
    failure intermittent. The coefficients avoid degeneracy for every
    supported radix: 7919 is prime but is itself inside the radix range
    (where the ``i * 7919`` term vanishes), and the ``2 * i**2`` term
    keeps the pattern varying at radix 7919 and alternating at radix 2.
    """
    return [(i * 7919 + 2 * i * i + 17) % radix for i in range(length)]


def test_differential_across_every_supported_radix() -> None:
    """Production and reference conversions agree for every radix the package accepts.

    Direct helper-level calls at a small length keep the full sweep cheap;
    larger lengths and threshold boundaries are covered separately. The
    round-trip assertion gives the differential an independent correctness
    anchor: two implementations that are wrong in the same way still fail
    to reproduce the input numerals.
    """
    for radix in _SUPPORTED_RADICES:
        numerals = _pseudo_numerals(radix, 8)
        value = _num_radix(radix, numerals)
        assert value == _reference_num_radix(radix, numerals), f"NUM diverged at radix {radix}"

        out = _str_radix(value, radix, 8)
        assert out == _reference_str_radix(value, radix, 8), f"STR diverged at radix {radix}"
        assert out == numerals, f"round trip broke at radix {radix}"

        # Full-width extreme: all-max numerals encode the largest value
        # eight digits can hold, where a conversion bug is most visible.
        max_numerals = [radix - 1] * 8
        max_value = _num_radix(radix, max_numerals)
        assert max_value == _reference_num_radix(radix, max_numerals)
        assert _str_radix(max_value, radix, 8) == _reference_str_radix(max_value, radix, 8)


def test_retained_module_reference_pinned() -> None:
    """The retained ``_ff1`` reference copy equals this module's transcription.

    STEP-02 keeps the naive loops in ``_ff1`` as the documented spec
    reference under the ``_num_radix_reference``/``_str_radix_reference``
    names. This test exercises that retained copy across every supported
    radix so it stays inside the differential and the 100% coverage
    floor. Until the names exist, the production helpers are the naive
    loops and the first assertion alone carries the same guarantee.
    """
    for radix in _SUPPORTED_RADICES:
        numerals = _pseudo_numerals(radix, 8)
        value = _reference_num_radix(radix, numerals)
        assert _num_radix(radix, numerals) == value
        assert _str_radix(value, radix, 8) == _reference_str_radix(value, radix, 8)

        if _retained_num_radix is not None:
            assert _retained_num_radix(radix, numerals) == value
        if _retained_str_radix is not None:
            assert _retained_str_radix(value, radix, 8) == _reference_str_radix(value, radix, 8)


@pytest.mark.parametrize("radix", _REPRESENTATIVE_RADICES)
@pytest.mark.parametrize("length", _BOUNDARY_LENGTHS)
def test_differential_at_threshold_boundaries(radix: int, length: int) -> None:
    """Lengths 63/64/65/128/129 straddle the future 64-numeral threshold.

    Odd lengths exercise the uneven split of the divide-and-conquer
    recursion; 128/129 cross the threshold twice. The all-zero and
    all-max extremes pin the full-width values at exactly the sizes where
    a threshold bug would appear.
    """
    numerals = _pseudo_numerals(radix, length)
    value = _num_radix(radix, numerals)
    assert value == _reference_num_radix(radix, numerals)
    assert _str_radix(value, radix, length) == _reference_str_radix(value, radix, length)

    for extreme in ([0] * length, [radix - 1] * length):
        v = _num_radix(radix, extreme)
        assert v == _reference_num_radix(radix, extreme)
        assert _str_radix(v, radix, length) == _reference_str_radix(v, radix, length)


@pytest.mark.parametrize("radix", _REPRESENTATIVE_RADICES)
@pytest.mark.parametrize("length", [0, 1, 2, 3])
def test_differential_at_degenerate_lengths(radix: int, length: int) -> None:
    """Lengths 0-3 pin the base cases any recursion must terminate on.

    Production never calls the helpers with length < 2 (min_length is 2
    at the widest radix), but the divide-and-conquer recursion will
    subdivide into exactly these sizes, so their behaviour is part of the
    contract being pinned, not dead input space.
    """
    numerals = _pseudo_numerals(radix, length)
    value = _num_radix(radix, numerals)
    assert value == _reference_num_radix(radix, numerals)
    assert _str_radix(value, radix, length) == _reference_str_radix(value, radix, length)


@pytest.mark.parametrize("radix", _REPRESENTATIVE_RADICES)
@pytest.mark.parametrize("length", [1, 8, 64])
def test_str_radix_truncation_contract(radix: int, length: int) -> None:
    """STR silently drops high digits above ``radix**length``; pin that exactly.

    Production callers never pass such a value (step 6.vi reduces c
    modulo ``radix**m`` before step 6.vii encodes it), but the shipped
    loop defines the behaviour, so the subquadratic replacement must
    reproduce it bit-for-bit rather than raise -- silently changing a
    helper's contract is exactly the class of drift this differential
    exists to catch.
    """
    for overflow in (radix**length, radix**length + 12345):
        assert _str_radix(overflow, radix, length) == _reference_str_radix(overflow, radix, length)


@st.composite
def _conversion_case(draw: st.DrawFn) -> tuple[int, int, list[int]]:
    """A radix, a length, and a valid numeral list at that length."""
    radix = draw(st.integers(min_value=2, max_value=2**16 - 1))
    length = draw(st.integers(min_value=0, max_value=300))
    numerals = draw(
        st.lists(
            st.integers(min_value=0, max_value=radix - 1),
            min_size=length,
            max_size=length,
        )
    )
    return radix, length, numerals


@given(_conversion_case())
@_SETTINGS
def test_property_conversion_equivalence(case: tuple[int, int, list[int]]) -> None:
    """Randomised differential sampling at lengths up to 300.

    Uniform sampling will not hit the threshold boundaries reliably (the
    parametrised boundary tests own that region deterministically), but it
    explores the multi-level recursion depths above the threshold across
    the full radix range.
    """
    radix, length, numerals = case
    value = _num_radix(radix, numerals)
    assert value == _reference_num_radix(radix, numerals)
    assert _str_radix(value, radix, length) == _reference_str_radix(value, radix, length)


@pytest.mark.parametrize("radix", _REPRESENTATIVE_RADICES)
@pytest.mark.parametrize("length", _BOUNDARY_LENGTHS)
def test_end_to_end_round_trip_at_boundary_lengths(radix: int, length: int) -> None:
    """Full FF1 encrypt/decrypt round-trips at the threshold-boundary lengths.

    The conversion helpers are exercised through the real Algorithm 7
    call path (ten rounds, both conversion directions, and the ``d > 16``
    S-expansion at the larger radices), so a STEP-02 integration mistake
    shows up here even if a helper-level differential were skipped.
    """
    ff1 = FF1(key=b"\x00" * 16, radix=radix)
    plaintext = _pseudo_numerals(radix, length)
    ciphertext = ff1.encrypt_numerals(plaintext)
    assert len(ciphertext) == length
    assert all(0 <= x < radix for x in ciphertext)
    assert ff1.decrypt_numerals(ciphertext) == plaintext
