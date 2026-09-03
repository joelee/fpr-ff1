"""Exact-arithmetic regression tests.

SP 800-38G bit-length and padding calculations must use only integer
arithmetic. This module tests boundary radices and statically scans the FF1
source for forbidden floating-point operations.
"""

import ast
import pathlib
from typing import cast

import pytest

from fpr_ff1 import FF1
from fpr_ff1._ff1 import TraceRecord


def _ff1_source_path() -> pathlib.Path:
    return pathlib.Path(__file__).resolve().parents[1] / "src" / "fpr_ff1" / "_ff1.py"


def test_no_float_operations_in_ff1_core() -> None:
    """Static scan: the FF1 module must not import math or use float syntax."""
    source = _ff1_source_path().read_text()
    tree = ast.parse(source)

    for node in ast.walk(tree):
        if (
            isinstance(node, ast.Import | ast.ImportFrom)
            and node.names
            and any(alias.name == "math" for alias in node.names)
        ):
            raise AssertionError("FF1 core must not import math")
        if isinstance(node, ast.Call):
            func = node.func
            if isinstance(func, ast.Name) and func.id in ("log", "log2", "ceil", "pow"):
                raise AssertionError(f"FF1 core must not call {func.id}()")
        if isinstance(node, ast.BinOp) and isinstance(node.op, ast.Div):
            raise AssertionError("FF1 core must not use true division (/)")
        if isinstance(node, ast.Constant) and isinstance(node.value, float):
            raise AssertionError("FF1 core must not contain float literals")

    forbidden = ["import math", "math.log2(", "math.log(", "math.ceil(", "math.pow(", "**0.5"]
    for token in forbidden:
        assert token not in source, f"forbidden token {token!r} found in FF1 source"


@pytest.mark.parametrize(
    ("radix", "length"),
    [
        (2, 20),
        (4, 10),
        (8, 7),
        (16, 5),
        (32, 4),
        (64, 4),
        (256, 3),
    ],
)
def test_power_of_two_radix_round_trip(radix: int, length: int) -> None:
    """Radices where radix**v sits on a power-of-two boundary must round-trip."""
    key = b"\x00" * 16
    ff1 = FF1(key=key, radix=radix)
    plaintext = [i % radix for i in range(length)]
    ciphertext = ff1.encrypt_numerals(plaintext)
    assert len(ciphertext) == length
    for numeral in ciphertext:
        assert 0 <= numeral < radix
    decrypted = ff1.decrypt_numerals(ciphertext)
    assert decrypted == plaintext


def _bytes_field(record: TraceRecord, key: str) -> list[int]:
    """Read a byte-string field (P, Q, R, S, C) out of a trace record."""
    value = record[key]
    assert isinstance(value, list), f"{key} should be a list, got {type(value).__name__}"
    return cast("list[int]", value)


def _int_field(record: TraceRecord, key: str) -> int:
    """Read an integer field (u, v, b, d, y, m, c, i) out of a trace record."""
    value = record[key]
    assert isinstance(value, int), f"{key} should be an int, got {type(value).__name__}"
    return value


def test_b_is_derived_from_v_not_u_for_odd_length() -> None:
    """When n is odd, u != v, and b must come from v.

    radix 256, n=5 gives u=2, v=3, and the two derivations disagree:

        b from v = ceil(bit_length(256**3 - 1) / 8) = 3   <- correct
        b from u = ceil(bit_length(256**2 - 1) / 8) = 2

    Asserting the observed b pins this directly.  A round-trip assertion is a
    poor substitute: with b from u this particular case happens to raise
    OverflowError from Q's b-byte encoding (B holds v numerals and will not
    fit), so the round-trip fails -- but it fails with a message about integer
    conversion rather than about b, and it says nothing at all when the two
    derivations agree.  It also cannot detect a b that is too *large*, which
    encodes fine with leading zeros and round-trips cleanly while producing
    non-conformant ciphertext.
    """
    ff1 = FF1(key=b"\x00" * 16, radix=256)
    _, trace = ff1._encrypt_traced([0, 1, 2, 3, 4])  # pyright: ignore[reportPrivateUsage]

    assert _int_field(trace[0], "u") == 2
    assert _int_field(trace[0], "v") == 3
    assert _int_field(trace[0], "b") == 3, "b must be derived from v, not u"

    # The Q block carries NUM_radix(B) in exactly b bytes, so a b of 2 would
    # also show up as a shorter Q.
    assert len(_bytes_field(trace[0], "Q")) == 0 + 12 + 1 + 3  # t + pad + [i] + b


@pytest.mark.parametrize("tweak_len", [0, 1, 3, 11, 12, 13, 16, 27, 32])
def test_padding_formula_matches_spec(tweak_len: int) -> None:
    """Q is padded by (-t - b - 1) % 16, keeping P || Q 16-byte aligned.

    Asserts the padding actually emitted into Q, across tweak lengths spanning
    every residue class, rather than restating the arithmetic.
    """
    ff1 = FF1(key=b"\x00" * 16, radix=10)
    tweak = bytes(range(1, tweak_len + 1))  # non-zero, so padding is visible
    _, trace = ff1._encrypt_traced([1] * 10, tweak)  # pyright: ignore[reportPrivateUsage]

    round0 = trace[0]
    b = _int_field(round0, "b")
    p_block = _bytes_field(round0, "P")
    q_block = _bytes_field(round0, "Q")

    expected_pad = (-(tweak_len + b + 1)) % 16

    assert q_block[:tweak_len] == list(tweak), "tweak must lead Q"
    assert q_block[tweak_len : tweak_len + expected_pad] == [0] * expected_pad, (
        f"expected {expected_pad} zero bytes of padding after a {tweak_len}-byte tweak"
    )
    assert q_block[tweak_len + expected_pad] == 0, "round number follows the padding"
    assert len(q_block) == tweak_len + expected_pad + 1 + b
    assert (len(p_block) + len(q_block)) % 16 == 0, "PRF input must be block aligned"
