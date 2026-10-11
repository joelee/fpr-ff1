"""Per-round intermediate value conformance tests.

These tests reproduce the published NIST SP 800-38G FF1 sample-vector
round-by-round values (P, Q, R, S, y, m, c, C plus derived u, v, b, d) using
the private ``FF1._encrypt_traced`` hook. The hook is a private method rather
than a parameter on the public methods, so the documented API surface stays
exactly as the contract specifies.

Parameterised over both backends (plan 00003 STEP-11, REQ-16): the rust
backend's trace comes from the extension's test-only
``_test_encrypt_traced`` binding, normalized to the same shape by the
``encrypt_traced`` fixture. Two compensating bugs can pass an output test;
they cannot pass this one on either backend.
"""

import itertools
import json
import pathlib
from typing import Any

import pytest

_VECTOR_FILE = (
    pathlib.Path(__file__).with_suffix("").parent / "vectors" / "nist_ff1_intermediates.json"
)


def _load_vectors() -> list[dict[str, Any]]:
    with _VECTOR_FILE.open(encoding="utf-8") as handle:
        data = json.load(handle)
    return data["vectors"]


_VECTORS = _load_vectors()


def _numerals_from_plaintext(plaintext: str, radix: int) -> list[int]:
    return [int(ch, radix) for ch in plaintext]


@pytest.mark.parametrize("vector", _VECTORS, ids=lambda v: v["name"])
def test_nist_intermediate_values(
    ff1_factory: Any, encrypt_traced: Any, vector: dict[str, Any]
) -> None:
    ff1 = ff1_factory(
        key=bytes.fromhex(vector["key"]),
        radix=vector["radix"],
        tweak=bytes.fromhex(vector["tweak"]),
    )
    _, trace = encrypt_traced(ff1, _numerals_from_plaintext(vector["plaintext"], vector["radix"]))

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


#: Every key a trace record carries, on either backend, after the
#: ``encrypt_traced`` fixture's normalisation (review 00015 LOW-01).
_TRACE_KEYS = frozenset(
    {"i", "u", "v", "b", "d", "P", "Q", "R", "S", "y", "m", "c", "C", "A_before", "B_before"}
)


@pytest.mark.parametrize("vector", _VECTORS, ids=lambda v: v["name"])
def test_trace_shape_and_chaining(
    ff1_factory: Any, encrypt_traced: Any, vector: dict[str, Any]
) -> None:
    """Both backends record the pre-swap halves, and they chain as specified.

    The NIST samples publish no per-round ``A`` or ``B``, so this asserts the
    specification's own rule rather than a fixture: SP 800-38G Algorithm 7
    step 2 splits ``X`` at ``u``; steps 6.viii and 6.ix make each round's
    ``A`` the previous round's ``B`` and its ``B`` the previous round's ``C``;
    step 7 returns ``A || B`` after the last round.
    """
    ff1 = ff1_factory(
        key=bytes.fromhex(vector["key"]),
        radix=vector["radix"],
        tweak=bytes.fromhex(vector["tweak"]),
    )
    x = _numerals_from_plaintext(vector["plaintext"], vector["radix"])
    ciphertext, trace = encrypt_traced(ff1, x)

    # Step 2: A = X[1..u], B = X[u+1..n]
    u = len(x) // 2
    assert trace[0]["A_before"] == x[:u]
    assert trace[0]["B_before"] == x[u:]

    # Steps 6.viii and 6.ix: A = B, B = C
    for previous, current in itertools.pairwise(trace):
        assert current["A_before"] == previous["B_before"], f"round {current['i']} A"
        assert current["B_before"] == previous["C"], f"round {current['i']} B"

    # Step 7: return A || B, where the final round's B and C are those halves
    assert ciphertext == trace[-1]["B_before"] + trace[-1]["C"]

    for record in trace:
        assert set(record) == _TRACE_KEYS, f"round {record['i']} keys"
