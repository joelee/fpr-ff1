"""Per-round intermediate value conformance tests.

These tests reproduce the published NIST SP 800-38G FF1 sample-vector
round-by-round values (P, Q, R, S, y, m, c, C plus derived u, v, b, d) using
the private ``FF1._encrypt_traced`` hook. The hook is a private method rather
than a parameter on the public methods, so the documented API surface stays
exactly as the contract specifies.
"""

import json
import pathlib
from typing import Any

import pytest

from fpr_ff1 import FF1

_VECTOR_FILE = (
    pathlib.Path(__file__).with_suffix("").parent / "vectors" / "nist_ff1_intermediates.json"
)


def _load_vectors() -> list[dict[str, Any]]:
    with _VECTOR_FILE.open() as handle:
        data = json.load(handle)
    return data["vectors"]


_VECTORS = _load_vectors()


def _numerals_from_plaintext(plaintext: str, radix: int) -> list[int]:
    return [int(ch, radix) for ch in plaintext]


@pytest.mark.parametrize("vector", _VECTORS, ids=lambda v: v["name"])
def test_nist_intermediate_values(vector: dict[str, Any]) -> None:
    ff1 = FF1(
        key=bytes.fromhex(vector["key"]),
        radix=vector["radix"],
        tweak=bytes.fromhex(vector["tweak"]),
    )
    _, trace = ff1._encrypt_traced(  # pyright: ignore[reportPrivateUsage]
        _numerals_from_plaintext(vector["plaintext"], vector["radix"])
    )

    assert len(trace) == 10, "FF1 must run exactly 10 rounds"

    # Derived values u, v, b, d are identical for every round; verify once.
    for name in ("u", "v", "b", "d"):
        assert trace[0][name] == vector[name], f"derived {name} mismatch"

    for expected, actual in zip(vector["rounds"], trace, strict=True):
        assert actual["i"] == expected["i"]
        for field in ("P", "Q", "R", "S", "y", "m", "c", "C"):
            assert actual[field] == expected[field], (
                f"{vector['name']} round {expected['i']} {field} mismatch: "
                f"got {actual[field]!r}, expected {expected[field]!r}"
            )
