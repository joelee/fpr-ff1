"""Direct same-input agreement between the two backends (plan 00007 STEP-04).

Round trips only prove each backend is self-consistent: a wrong-but-symmetric
core still decrypts its own output.  These tests hand *identical* inputs to
the pure-Python reference and the compiled core and require identical
outputs, for encryption **and** decryption, across all three key sizes,
varied tweaks, and lengths on both sides of the 64-numeral conversion
threshold -- including lengths long enough that the compiled core's
divide-and-conquer and power-of-two conversion paths carry the work
(review 00007 STABLE-06).

Decryption is compared on an input that is not a ciphertext of either
backend, so neither side can pass by inverting its own encryption.

Availability follows the dual-backend contract: skipped when the extension
is not built, a hard failure when ``FPR_FF1_REQUIRE_RUST_BACKEND`` is set
(``tests/conftest.py`` raises at import in that case).
"""

import pytest

from fpr_ff1 import FF1
from tests.conftest import BACKENDS

pytestmark = pytest.mark.skipif(
    "rust" not in BACKENDS, reason="Rust backend not built; run `just backend-dev`"
)

_KEY_SIZES = [16, 24, 32]


def _assert_same_numerals(rust: list[int], python: list[int], operation: str) -> None:
    """Fail with the first diverging position, never with a whole-list diff.

    A bare ``assert rust == python`` makes pytest render a full sequence diff
    whenever it is verbose *or* detects CI (``_pytest.assertion._compare_
    sequence``). On CPython 3.12 that diff is pathologically slow for lists of
    thousands of numerals: under a deliberate core defect (plan 00007
    STEP-07) one failing case took minutes and the release gate stalled for
    hours instead of failing. The index and length locate a divergence just
    as well and cost nothing.
    """
    if rust == python:
        return
    if len(rust) != len(python):
        pytest.fail(
            f"{operation}: rust returned {len(rust)} numerals, python {len(python)}",
            pytrace=False,
        )
    first = next(i for i, (r, p) in enumerate(zip(rust, python, strict=True)) if r != p)
    pytest.fail(
        f"{operation}: backends diverge at numeral {first} of {len(python)} "
        f"(rust {rust[first]}, python {python[first]})",
        pytrace=False,
    )


_TWEAK_LENGTHS = [0, 1, 16, 255]
_RADICES = [10, 36, 256, 65535]
_LENGTHS = [6, 64, 65, 1000, 5000]


def _numerals(radix: int, length: int, salt: int) -> list[int]:
    """Deterministic numerals with a zero prefix and a maximum-numeral tail."""
    body = [(i * 7919 + salt * 104729) % radix for i in range(length)]
    edge = length // 8
    return [0] * edge + body[edge : length - edge] + [radix - 1] * edge


@pytest.mark.parametrize("length", _LENGTHS)
@pytest.mark.parametrize("radix", _RADICES)
@pytest.mark.parametrize("tweak_len", _TWEAK_LENGTHS)
@pytest.mark.parametrize("key_size", _KEY_SIZES)
def test_backends_agree_on_identical_inputs(
    key_size: int, tweak_len: int, radix: int, length: int
) -> None:
    key = bytes((i * 31 + key_size) % 256 for i in range(key_size))
    tweak = bytes((i * 17 + tweak_len) % 256 for i in range(tweak_len))
    py = FF1(key=key, radix=radix, backend="python")
    rs = FF1(key=key, radix=radix, backend="rust")

    plaintext = _numerals(radix, length, salt=1)
    _assert_same_numerals(
        rs.encrypt_numerals(plaintext, tweak), py.encrypt_numerals(plaintext, tweak), "encrypt"
    )

    arbitrary = _numerals(radix, length, salt=2)
    _assert_same_numerals(
        rs.decrypt_numerals(arbitrary, tweak), py.decrypt_numerals(arbitrary, tweak), "decrypt"
    )
