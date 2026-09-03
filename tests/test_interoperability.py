"""Migration safety: `fpr-ff1` is drop-in compatible with `ubiq_security_fpe`.

AGENTS.md section 9 treats this as a correctness obligation to downstream
users, not a nicety.  `fpr-ff1` exists to replace `ubiq_security_fpe`, which was
deprecated in favour of a SaaS client.  Anyone migrating has data already
encrypted with the old library, so the property that actually matters is not
"both produce the same bytes" but:

    **Ciphertext written by the old library must still decrypt correctly with
    this one, and vice versa.**

If that fails, migrating silently strands data as undecryptable.  These tests
demonstrate it directly, in both directions, across every key size, both
tweaked and untweaked.

The mapping between the two APIs::

    # before
    from ubiq_security_fpe import ff1
    ctx = ff1.Context(key, tweak, twk_min_len, twk_max_len, radix, alphabet)
    ct  = ctx.Encrypt(pt, None)
    pt  = ctx.Decrypt(ct, None)

    # after
    from fpr_ff1 import FF1
    ctx = FF1(key, radix, alphabet=alphabet, tweak=tweak,
              min_tweak_len=twk_min_len, max_tweak_len=twk_max_len)
    ct  = ctx.encrypt(pt)
    pt  = ctx.decrypt(ct)

Note that `fpr-ff1` enforces the SP 800-38G Rev. 1 minimum domain
(``radix ** minlen >= 1_000_000``), which is stricter than the 2016 text.
Inputs shorter than :attr:`FF1.min_length` were accepted by some older
libraries and are rejected here; see the README migration section.
"""

import string
from typing import Any

import pytest

from fpr_ff1 import FF1
from tests._oracle import load_oracle_or_none

_oracle = load_oracle_or_none()

pytestmark = pytest.mark.skipif(
    _oracle is None,
    reason="ubiq-security-fpe oracle not installed",
)

_ALPHABET = string.digits
_RADIX = 10
_PLAINTEXT = "0123456789012345"

_CASES = [
    pytest.param(16, b"", id="aes128-no-tweak"),
    pytest.param(16, bytes.fromhex("39383736353433323130"), id="aes128-tweaked"),
    pytest.param(24, b"", id="aes192-no-tweak"),
    pytest.param(24, bytes.fromhex("39383736353433323130"), id="aes192-tweaked"),
    pytest.param(32, b"", id="aes256-no-tweak"),
    pytest.param(32, bytes.fromhex("39383736353433323130"), id="aes256-tweaked"),
]


def _legacy(key: bytes, tweak: bytes) -> Any:
    """Build a legacy `ubiq_security_fpe` context."""
    assert _oracle is not None
    return _oracle.Context(key, tweak, 0, 0, _RADIX, _ALPHABET)


def _migrated(key: bytes, tweak: bytes) -> FF1:
    """Build the equivalent `fpr-ff1` context."""
    return FF1(key, _RADIX, alphabet=_ALPHABET, tweak=tweak)


@pytest.mark.parametrize(("key_len", "tweak"), _CASES)
def test_legacy_ciphertext_decrypts_after_migration(key_len: int, tweak: bytes) -> None:
    """Data encrypted before migrating must still be readable after."""
    key = bytes(range(key_len))
    legacy_ciphertext = _legacy(key, tweak).Encrypt(_PLAINTEXT, None)

    assert _migrated(key, tweak).decrypt(legacy_ciphertext) == _PLAINTEXT


@pytest.mark.parametrize(("key_len", "tweak"), _CASES)
def test_new_ciphertext_decrypts_with_legacy_library(key_len: int, tweak: bytes) -> None:
    """Migration is reversible: a rollback must not strand new data."""
    key = bytes(range(key_len))
    new_ciphertext = _migrated(key, tweak).encrypt(_PLAINTEXT)

    assert _legacy(key, tweak).Decrypt(new_ciphertext, None) == _PLAINTEXT


@pytest.mark.parametrize(("key_len", "tweak"), _CASES)
def test_ciphertexts_are_identical(key_len: int, tweak: bytes) -> None:
    """The two libraries agree byte for byte, so stored data needs no rewrite."""
    key = bytes(range(key_len))

    assert _migrated(key, tweak).encrypt(_PLAINTEXT) == _legacy(key, tweak).Encrypt(
        _PLAINTEXT, None
    )


def test_tweak_bounds_map_across_apis() -> None:
    """The legacy twk_min_len/twk_max_len arguments map onto the new keywords."""
    key = bytes(range(16))
    tweak = bytes.fromhex("3938373635")

    legacy = _oracle.Context(key, tweak, 4, 8, _RADIX, _ALPHABET)  # pyright: ignore[reportOptionalMemberAccess]
    migrated = FF1(
        key,
        _RADIX,
        alphabet=_ALPHABET,
        tweak=tweak,
        min_tweak_len=4,
        max_tweak_len=8,
    )

    assert migrated.encrypt(_PLAINTEXT) == legacy.Encrypt(_PLAINTEXT, None)
