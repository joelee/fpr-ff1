"""Independent FF1 oracle used for differential testing.

AGENTS.md section 7: for radices without published NIST vectors, correctness is
established by agreement with an independent implementation, never by expected
values authored from this implementation.  Committing self-generated outputs as
"vectors" tests nothing and locks in bugs permanently.

The oracle here is ``ubiq_security_fpe`` (MIT, deprecated, self-contained), the
library this package exists to replace.  It is a dev-only dependency, pinned by
hash in ``uv.lock``, and every use is gated on :func:`load_oracle` so a missing
oracle skips rather than fails -- optional locally, required in CI.

Callers must not trust the oracle blindly; ``test_differential.py`` validates it
against all nine NIST sample vectors before comparing anything against it.
"""

import importlib
import os
from typing import Any

from tests._oracle import _m2crypto_shim

__all__ = [
    "REQUIRE_ORACLE_ENV",
    "OracleUnavailableError",
    "load_oracle",
    "load_oracle_or_none",
    "oracle_decrypt",
    "oracle_encrypt",
    "oracle_is_required",
]

#: Set this to a non-empty, non-"0" value to turn a missing oracle from a skip
#: into a hard failure.  CI sets it; local development does not.
REQUIRE_ORACLE_ENV = "FPR_FF1_REQUIRE_ORACLE"


class OracleUnavailableError(ImportError):
    """The oracle package is not installed in this environment."""


def oracle_is_required() -> bool:
    """Whether a missing oracle should fail rather than skip."""
    return os.environ.get(REQUIRE_ORACLE_ENV, "").strip() not in {"", "0"}


def load_oracle_or_none() -> Any | None:
    """Return the oracle module, or ``None`` if it is unavailable.

    Raises rather than returning ``None`` when :data:`REQUIRE_ORACLE_ENV` is
    set.  Without that guard a broken oracle install in CI would silently skip
    the differential tests -- and those are the *only* coverage for radices
    with no published NIST vectors, and for the S-expansion branch the NIST
    samples never reach.  Skipping them quietly would look exactly like
    passing.
    """
    try:
        return load_oracle()
    except OracleUnavailableError:
        if oracle_is_required():
            raise
        return None


def load_oracle() -> Any:
    """Return the ``ubiq_security_fpe.ff1`` module.

    Raises:
        OracleUnavailableError: if the oracle package is not installed.
    """
    _m2crypto_shim.install()
    try:
        # Imported dynamically: the oracle must not be a hard import (it is an
        # optional dev dependency), and it ships no type stubs.
        return importlib.import_module("ubiq_security_fpe.ff1")
    except ImportError as exc:  # pragma: no cover - environment dependent
        raise OracleUnavailableError(
            "ubiq-security-fpe is not installed; run `uv sync` to enable differential tests"
        ) from exc


def oracle_encrypt(key: bytes, tweak: bytes, radix: int, alphabet: str, plaintext: str) -> str:
    """Encrypt ``plaintext`` with the oracle, using no tweak-length bounds."""
    ff1 = load_oracle()
    context = ff1.Context(key, tweak, 0, 0, radix, alphabet)
    result: str = context.Encrypt(plaintext, None)
    return result


def oracle_decrypt(key: bytes, tweak: bytes, radix: int, alphabet: str, ciphertext: str) -> str:
    """Decrypt ``ciphertext`` with the oracle, using no tweak-length bounds."""
    ff1 = load_oracle()
    context = ff1.Context(key, tweak, 0, 0, radix, alphabet)
    result: str = context.Decrypt(ciphertext, None)
    return result
