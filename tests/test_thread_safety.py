"""Thread-safety tests (review 00003 H2 / review 00004 MED-01).

The instance previously cached a single ECB encryptor for the step 6.iii
S-expansion.  pyca/cryptography documents concurrent ``update()`` calls on a
shared ``CipherContext`` as producing indeterminate results, so sharing one
``FF1`` instance across threads could silently produce wrong ciphertext --
and the hazard was invisible at the short lengths people unit-test with,
because the shared context is only touched when ``d > 16``.

The fix is structural: no shared mutable cipher state exists on the instance
at all.  These tests pin both the structure and the behaviour.
"""

import threading

from cryptography.hazmat.primitives.ciphers import CipherContext

from fpr_ff1 import FF1
from fpr_ff1._ff1 import _Aes  # pyright: ignore[reportPrivateUsage]

_VALID_KEY = b"\x00" * 16


def test_aes_carries_no_live_cipher_context() -> None:
    """The structural guarantee: _Aes holds only immutable configuration.

    With no ``CipherContext`` on the instance there is no shared mutable
    state, which is what makes separate calls safe to run concurrently.
    A race-detector test alone cannot prove this; the structure does.
    """
    for field_name in _Aes._fields:
        field_type = _Aes.__annotations__[field_name]
        assert field_name not in ("ecb_encryptor",), (
            f"_Aes.{field_name} must not be a cached encryptor; "
            "the instance must hold no live cipher context"
        )
        assert field_type != "CipherContext", (
            f"_Aes.{field_name} is annotated as a live CipherContext"
        )


def test_no_ciphercontext_attribute_on_instance() -> None:
    """No attribute reachable from a constructed instance is a CipherContext."""
    ff1 = FF1(key=_VALID_KEY, radix=10)
    for name, value in vars(ff1).items():
        assert not isinstance(value, CipherContext), (
            f"FF1.{name} holds a live CipherContext; instances cannot be "
            "thread-safe while any mutable cipher state is shared"
        )
        if isinstance(value, _Aes):
            for aes_field in value:
                assert not isinstance(aes_field, CipherContext), (
                    f"FF1.{name} carries a CipherContext inside _Aes"
                )


def test_shared_instance_concurrent_encryption_matches_serial() -> None:
    """Threads sharing one instance must produce exactly the serial results.

    Uses inputs with ``d > 16`` (radix 10 needs 57+ numerals), the only
    regime where the old shared context was touched.  A single wrong
    ciphertext would previously have been silent; here every result is
    compared against the single-threaded expectation.
    """
    ff1 = FF1(key=_VALID_KEY, radix=10)
    plaintexts = [[(thread_index * 17 + i) % 10 for i in range(60)] for thread_index in range(8)]
    expected = [ff1.encrypt_numerals(p) for p in plaintexts]

    results: list[list[int]] = [[] for _ in plaintexts]
    errors: list[BaseException] = []

    def worker(index: int) -> None:
        try:
            for _ in range(20):
                results[index] = ff1.encrypt_numerals(plaintexts[index])
        except BaseException as exc:
            errors.append(exc)

    threads = [threading.Thread(target=worker, args=(i,)) for i in range(len(plaintexts))]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join()

    assert not errors, f"concurrent encryption raised: {errors}"
    assert results == expected, "concurrent encryption diverged from serial results"


def test_shared_instance_concurrent_mixed_operations() -> None:
    """Encrypt and decrypt concurrently on one shared instance.

    Both directions run through the same expansion path; mixing them on one
    instance is the realistic web-service usage the old caveat warned about.
    """
    ff1 = FF1(key=_VALID_KEY, radix=10)
    plaintexts = [[(thread_index * 13 + i) % 10 for i in range(60)] for thread_index in range(4)]
    ciphertexts = [ff1.encrypt_numerals(p) for p in plaintexts]

    decrypted: list[list[int]] = [[] for _ in plaintexts]
    encrypted: list[list[int]] = [[] for _ in plaintexts]
    errors: list[BaseException] = []

    def worker(index: int) -> None:
        try:
            for _ in range(20):
                decrypted[index] = ff1.decrypt_numerals(ciphertexts[index])
                encrypted[index] = ff1.encrypt_numerals(plaintexts[index])
        except BaseException as exc:
            errors.append(exc)

    threads = [threading.Thread(target=worker, args=(i,)) for i in range(len(plaintexts))]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join()

    assert not errors, f"concurrent mixed operations raised: {errors}"
    assert decrypted == plaintexts
    assert encrypted == ciphertexts


def test_expansion_path_still_reaches_d_over_16() -> None:
    """The concurrency tests above must actually exercise the expansion.

    Radix 10 at length 60 gives ``d > 16`` (first expansion at 57 numerals),
    so the S-expansion loop -- the code the shared context used to live in --
    runs on every round of every test encryption here.
    """
    ff1 = FF1(key=_VALID_KEY, radix=10)
    _, trace = ff1._encrypt_traced([0] * 60)  # pyright: ignore[reportPrivateUsage]
    d_value = trace[0]["d"]
    assert isinstance(d_value, int)
    assert d_value > 16, "length 60 at radix 10 must reach the S-expansion branch"
