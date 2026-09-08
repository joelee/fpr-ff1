"""NIST SP 800-38G FF1 sample vector tests.

Parameterised over both backends (plan 00003 STEP-11, REQ-16): the
published vectors must pass identically on the pure-Python reference and
the compiled core.
"""

import json
import pathlib
from typing import Any

import pytest

_VECTOR_FILE = pathlib.Path(__file__).with_suffix("").parent / "vectors" / "nist_ff1_samples.json"


def _load_vectors() -> list[dict[str, Any]]:
    with _VECTOR_FILE.open(encoding="utf-8") as handle:
        data = json.load(handle)
    return data["vectors"]


_VECTORS = _load_vectors()


@pytest.mark.parametrize("vector", _VECTORS, ids=lambda v: v["name"])
def test_nist_vector_encrypt(ff1_factory: Any, vector: dict[str, Any]) -> None:
    ff1 = ff1_factory(
        key=bytes.fromhex(vector["key"]),
        radix=vector["radix"],
        alphabet=vector["alphabet"],
        tweak=bytes.fromhex(vector["tweak"]),
    )
    assert ff1.encrypt(vector["plaintext"]) == vector["ciphertext"]


@pytest.mark.parametrize("vector", _VECTORS, ids=lambda v: v["name"])
def test_nist_vector_decrypt(ff1_factory: Any, vector: dict[str, Any]) -> None:
    ff1 = ff1_factory(
        key=bytes.fromhex(vector["key"]),
        radix=vector["radix"],
        alphabet=vector["alphabet"],
        tweak=bytes.fromhex(vector["tweak"]),
    )
    assert ff1.decrypt(vector["ciphertext"]) == vector["plaintext"]


@pytest.mark.parametrize("vector", _VECTORS, ids=lambda v: v["name"])
def test_nist_vector_round_trip(ff1_factory: Any, vector: dict[str, Any]) -> None:
    ff1 = ff1_factory(
        key=bytes.fromhex(vector["key"]),
        radix=vector["radix"],
        alphabet=vector["alphabet"],
        tweak=bytes.fromhex(vector["tweak"]),
    )
    encrypted = ff1.encrypt(vector["plaintext"])
    assert ff1.decrypt(encrypted) == vector["plaintext"]
