"""AES and PRF validation for the Rust accelerated backend (plan 00003 STEP-09).

Before any FF1-level conformance is trusted on the Rust path, its
cryptography is validated independently (plan 00003 REQ-15, idea r01
MED-02): a second AES implementation is a cryptographic correctness risk
that the NIST FF1 vectors — radix 10/36 only — would not isolate.

Two independent checks:

1. **NIST FIPS 197 known-answer tests** for the underlying single-block
   cipher, from ``tests/vectors/aes_kat_fips197.json`` (transcribed from
   the standard, cross-verified against the OpenSSL-backed ``cryptography``
   package, never generated from this repository).
2. **PRF equality with the reference path**: the Rust Algorithm 6 CBC-MAC
   must equal ``fpr_ff1._ff1._prf`` byte for byte across all three key
   sizes and block counts 1-5, which spans every chaining shape the FF1
   core produces (and the block counts where a mis-wired CBC chain would
   diverge).

Availability mirrors the differential-oracle contract (AGENTS.md tests
section 7): optional locally, mandatory when ``FPR_FF1_REQUIRE_RUST_BACKEND``
is set — which CI's ``rust-conformance`` job does, so a missing extension
fails the release gate rather than skipping.
"""

import importlib
import json
import os
import pathlib
from types import ModuleType
from typing import Any

import pytest
from cryptography.hazmat.primitives.ciphers import algorithms, modes

from fpr_ff1._ff1 import _Aes, _prf  # pyright: ignore[reportPrivateUsage]

_VECTOR_FILE = pathlib.Path(__file__).parent / "vectors" / "aes_kat_fips197.json"

#: Set by CI's ``rust-conformance`` job to turn a missing backend into a
#: hard failure instead of a skip, mirroring ``FPR_FF1_REQUIRE_ORACLE``.
_REQUIRED = os.environ.get("FPR_FF1_REQUIRE_RUST_BACKEND", "").strip() not in {"", "0"}


def _load_backend() -> ModuleType:
    if _REQUIRED:
        # A hard ImportError: when the backend is required it must be there.
        return importlib.import_module("fpr_ff1._rs")
    return pytest.importorskip(
        "fpr_ff1._rs", reason="Rust backend not built; run `just backend-dev`"
    )


_rs = _load_backend()


def _python_prf(key: bytes, data: bytes) -> bytes:
    """The reference path's Algorithm 6 PRF, via the production ``_prf``."""
    aes = _Aes(algorithm=algorithms.AES(key), cbc_zero_iv=modes.CBC(b"\x00" * 16))
    return _prf(aes, data)


def _rust_prf(key: bytes, data: bytes) -> bytes:
    """The Rust backend's PRF through the test-only binding."""
    result: Any = _rs._test_prf(key, data)
    return bytes(result)  # pyright: ignore[reportUnknownArgumentType, reportAny]


def _rust_cipher_block(key: bytes, block: bytes) -> bytes:
    """The Rust backend's raw single-block cipher (test-only binding)."""
    result: Any = _rs._test_cipher_block(key, block)
    return bytes(result)  # pyright: ignore[reportUnknownArgumentType, reportAny]


def _kat_vectors() -> list[dict[str, str]]:
    with _VECTOR_FILE.open(encoding="utf-8") as handle:
        data: dict[str, Any] = json.load(handle)
    vectors: list[dict[str, str]] = data["vectors"]
    return vectors


@pytest.mark.parametrize("vector", _kat_vectors())
def test_aes_kat_fips197(vector: dict[str, str]) -> None:
    """The Rust AES single-block cipher matches NIST FIPS 197 Appendix C."""
    key = bytes.fromhex(vector["key"])
    plaintext = bytes.fromhex(vector["plaintext"])
    expected = bytes.fromhex(vector["ciphertext"])

    assert len(plaintext) == 16, "KAT plaintexts are single blocks"
    assert _rust_cipher_block(key, plaintext) == expected, vector["name"]


@pytest.mark.parametrize("key_len", [16, 24, 32])
@pytest.mark.parametrize("blocks", [1, 2, 3, 4, 5])
def test_prf_equality_with_reference(key_len: int, blocks: int) -> None:
    """The Rust PRF equals the reference path byte for byte.

    Block counts 1-5 span every chaining shape the FF1 core produces; a
    mis-wired IV, chain update, or final-block selection diverges on one
    of them.
    """
    key = bytes(range(key_len))
    data = bytes((i * 31 + 7) % 256 for i in range(16 * blocks))

    assert _rust_prf(key, data) == _python_prf(key, data)


def test_prf_data_sensitivity_both_backends() -> None:
    """Both PRFs respond to a one-bit data change (shared sanity)."""
    key = bytes(range(32))
    data = bytes(48)
    flipped = bytearray(data)
    flipped[0] ^= 1

    assert _rust_prf(key, data) != _rust_prf(key, bytes(flipped))
    assert _python_prf(key, data) != _python_prf(key, bytes(flipped))
