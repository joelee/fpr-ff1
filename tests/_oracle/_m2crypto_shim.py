"""A minimal ``M2Crypto.EVP`` stand-in backed by ``cryptography``.

``ubiq_security_fpe`` imports ``M2Crypto`` at module scope, and M2Crypto does
not build cleanly on current toolchains.  Without this shim the oracle named in
AGENTS.md as an approved differential reference is simply unusable, and the
"optional-but-run-in-CI" tests silently degrade into tests that never run.

The shim implements only the surface ``ubiq_security_fpe.ffx`` actually uses:
``EVP.Cipher(alg=..., key=..., iv=..., op=1)`` followed by a single
``update()``.  ``ffx`` only ever encrypts in CBC mode with a zero IV -- its
``Ciph()`` is ``PRF()`` over one block -- so ECB is deliberately not supported;
anything unexpected raises rather than quietly returning wrong bytes.

Each ``Cipher`` builds a fresh encryptor, matching ``ffx``, which constructs a
new cipher per PRF call so no CBC chaining state carries between calls.
"""

import importlib.util
import sys
import types
from typing import Final

from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes

_ALGORITHMS: Final[dict[str, int]] = {
    "aes_128_cbc": 16,
    "aes_192_cbc": 24,
    "aes_256_cbc": 32,
}


class _Cipher:
    """Encrypt-only AES-CBC context mimicking ``M2Crypto.EVP.Cipher``."""

    def __init__(
        self,
        alg: str | bytes,
        key: bytes | bytearray,
        iv: bytes | bytearray,
        op: int,
    ) -> None:
        name = alg.decode() if isinstance(alg, bytes) else alg
        if name not in _ALGORITHMS:
            raise ValueError(f"shim supports only {sorted(_ALGORITHMS)}, got {name!r}")
        if op != 1:
            raise ValueError(f"shim supports encryption (op=1) only, got op={op!r}")
        expected = _ALGORITHMS[name]
        if len(key) != expected:
            raise ValueError(f"{name} needs a {expected}-byte key, got {len(key)}")

        self._ctx = Cipher(
            algorithms.AES(bytes(key)),
            modes.CBC(bytes(iv)),
        ).encryptor()

    def set_padding(self, padding: int) -> "_Cipher":  # noqa: ARG002
        return self

    def update(self, data: bytes | bytearray) -> bytes:
        return self._ctx.update(bytes(data))

    def final(self) -> bytes:
        return b""


class EVP:
    """Namespace mirroring ``M2Crypto.EVP``."""

    Cipher = _Cipher


def install() -> None:
    """Register the shim as ``M2Crypto`` if the real package is unavailable.

    No-op when genuine M2Crypto is importable, so a developer who has it
    installed exercises the real thing.
    """
    if "M2Crypto" in sys.modules:
        return
    if importlib.util.find_spec("M2Crypto") is not None:  # pragma: no cover
        return  # genuine M2Crypto is available; prefer it

    module = types.ModuleType("M2Crypto")
    module.EVP = EVP  # pyright: ignore[reportAttributeAccessIssue]
    sys.modules["M2Crypto"] = module
