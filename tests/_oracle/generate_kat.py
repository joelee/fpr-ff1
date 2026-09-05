"""Generate frozen KAT vectors from the independent oracle (review 00003 H6).

Dev-only tool: run manually, never in CI or the test suite.

    uv run python -m tests._oracle.generate_kat

The oracle (``ubiq-security-fpe``) is deprecated and unmaintained.  The day it
stops installing, the live differential suite -- the only correctness evidence
for radices without published NIST vectors -- goes dark.  This script freezes
oracle-derived known-answer vectors into a committed JSON file so the
evidence survives.

This does **not** violate the no-self-authored-vectors rule: every expected
value is produced by the independent implementation, not by ``fpr-ff1``.  The
rule exists to stop this package locking in its own bugs; oracle-derived
vectors do the opposite.

The frozen file is a *fallback*, not a replacement.  The live differential run
stays primary while the oracle installs; the frozen vectors carry the evidence
when it cannot.
"""

import json
import pathlib
import string
from datetime import UTC, datetime
from importlib.metadata import version as dist_version
from typing import Any

from tests._oracle import load_oracle

_VECTOR_PATH = pathlib.Path(__file__).resolve().parents[1] / "vectors" / "oracle_kat_frozen.json"

_BASE36 = string.digits + string.ascii_lowercase
_KEY = bytes(range(16))
_TWEAK = bytes.fromhex("393837")

#: Radices the live differential suite covers.  10 and 36 also have NIST
#: vectors; the rest have none, which is exactly why they need frozen
#: oracle-derived evidence.
_RADICES = [2, 10, 16, 32, 36, 62, 256, 2**16 - 1]


def _alphabet_for(radix: int) -> str:
    if radix <= len(_BASE36):
        return _BASE36[:radix]
    return "".join(chr(0x10000 + i) for i in range(radix))


def _plaintext(n: int, alphabet: str) -> str:
    """Deterministic, non-degenerate plaintext of length ``n``.

    Mirrors ``tests/test_differential.py`` so the frozen vectors cover the
    same shapes the live suite does.
    """
    return "".join(alphabet[(i * 7 + n) % len(alphabet)] for i in range(n))


def _lengths_for(radix: int) -> list[int]:
    """Representative lengths: the lower bound, odd/even mix, and the
    ``d > 16`` S-expansion transitions (the branch no NIST sample reaches)."""
    min_len = 1
    value = radix
    while value < 1_000_000:
        value *= radix
        min_len += 1

    def d_for(n: int) -> int:
        v = n - n // 2
        b = ((radix**v - 1).bit_length() + 7) // 8
        return 4 * ((b + 3) // 4) + 4

    lengths = {min_len, min_len + 1, 20}
    # First length where d crosses 16, and one where it crosses 32 (two
    # expansion blocks).
    n = min_len
    first_over, second_over = None, None
    while n < 400:
        d = d_for(n)
        if d > 16 and first_over is None:
            first_over = n
        if d > 32 and second_over is None:
            second_over = n
            break
        n += 1
    if first_over is not None:
        lengths.add(first_over)
        lengths.add(first_over - 1)  # the last length below the transition
    if second_over is not None:
        lengths.add(second_over)
    return sorted(lengths)


def main() -> None:
    oracle = load_oracle()
    oracle_version = dist_version("ubiq-security-fpe")

    vectors: list[dict[str, Any]] = []
    for radix in _RADICES:
        alphabet = _alphabet_for(radix)
        for n in _lengths_for(radix):
            plaintext = _plaintext(n, alphabet)
            context = oracle.Context(_KEY, _TWEAK, 0, 0, radix, alphabet)
            ciphertext: str = context.Encrypt(plaintext, None)
            vectors.append(
                {
                    "radix": radix,
                    "key_hex": _KEY.hex(),
                    "tweak_hex": _TWEAK.hex(),
                    "alphabet": alphabet,
                    "plaintext": plaintext,
                    "ciphertext": ciphertext,
                }
            )

    payload = {
        "provenance": {
            "source": "ubiq-security-fpe (independent FF1 implementation)",
            "oracle_version": oracle_version,
            "generated_at": datetime.now(UTC).isoformat(timespec="seconds"),
            "generator": "tests/_oracle/generate_kat.py",
            "note": (
                "Expected values produced by the oracle, never by fpr-ff1. "
                "Frozen so differential evidence survives the oracle "
                "(deprecated, unmaintained) becoming uninstallable. The live "
                "differential suite remains primary while the oracle installs."
            ),
        },
        "vectors": vectors,
    }

    _VECTOR_PATH.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n")
    print(f"wrote {len(vectors)} vectors to {_VECTOR_PATH}")  # noqa: T201 - CLI tool output


if __name__ == "__main__":
    main()
