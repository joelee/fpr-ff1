# fpr-ff1

[![CI](https://github.com/joelee/fpr-ff1/actions/workflows/ci.yml/badge.svg)](https://github.com/joelee/fpr-ff1/actions/workflows/ci.yml)
[![PyPI](https://img.shields.io/pypi/v/fpr-ff1.svg)](https://pypi.org/project/fpr-ff1/)
[![Python](https://img.shields.io/pypi/pyversions/fpr-ff1.svg)](https://pypi.org/project/fpr-ff1/)
[![crates.io](https://img.shields.io/crates/v/fpr-ff1.svg)](https://crates.io/crates/fpr-ff1)
[![docs.rs](https://img.shields.io/docsrs/fpr-ff1)](https://docs.rs/fpr-ff1)
[![License: Python MIT, Rust MIT OR Apache-2.0](https://img.shields.io/badge/license-Python%3A%20MIT%20%C2%B7%20Rust%3A%20MIT%20OR%20Apache--2.0-blue.svg)](https://github.com/joelee/fpr-ff1/blob/main/LICENSE)

**FF1 format-preserving encryption (NIST SP 800-38G) for Python and Rust, conformance-tested round
by round against the published NIST vectors.**

- **Python** ([PyPI](https://pypi.org/project/fpr-ff1/)): pure Python with one dependency,
  `cryptography`, plus an optional compiled backend that is faster and bit-identical.
- **Rust** ([crates.io](https://crates.io/crates/fpr-ff1)): the same FF1 core as a native crate
  with a small, stable API, validating inputs exactly as the Python package does.

Both are built from this repository, share one conformance suite, and are released together under
one version number.

## What FF1 is for

Format-preserving encryption turns a value into ciphertext of the same shape: a 16-digit card
number encrypts to 16 digits, and a code over `A-Z0-9` stays over `A-Z0-9`. Encrypted values still
fit the columns, fixed-width files, validators and APIs built for the plaintext, so you can protect:

- card and account numbers in legacy schemas;
- national and customer identifiers passed between services;
- production data copied into test and analytics environments, still valid for the code that
  reads it.

FF1 is reversible encryption, not hashing or vault tokenisation: anyone holding the key can decrypt.
It provides confidentiality only, so read the [security notes](#security-notes--read-before-use).

## Install

```bash
pip install fpr-ff1       # Python 3.12 or newer
cargo add fpr-ff1         # Rust 1.89 or newer
```

## Quick start

```python
import secrets

from fpr_ff1 import FF1

key = secrets.token_bytes(32)  # for real data, load the key from your secret store

ff1 = FF1(
    key=key,
    radix=10,
    alphabet="0123456789",
    # Derive the tweak from stable record context (an account ID, a table name):
    # equal plaintexts under the same key and tweak give equal ciphertexts.
    tweak=b"customer-pans",
)

encrypted = ff1.encrypt("123456")
assert ff1.decrypt(encrypted) == "123456"
```

In Rust, with NIST's published sample 2 values, so the output can be checked:

```rust
use fpr_ff1::FF1;

fn main() -> Result<(), fpr_ff1::Error> {
    // NIST SP 800-38G sample 2: AES-128, radix 10, a ten-byte tweak. The key is a
    // published test key; load real keys from your secret store.
    let key: [u8; 16] = [
        0x2B, 0x7E, 0x15, 0x16, 0x28, 0xAE, 0xD2, 0xA6,
        0xAB, 0xF7, 0x15, 0x88, 0x09, 0xCF, 0x4F, 0x3C,
    ];
    let ff1 = FF1::builder(&key, 10)
        .alphabet("0123456789")
        .tweak(b"9876543210")
        .build()?;

    let ciphertext = ff1.encrypt("0123456789", None)?;
    assert_eq!(ciphertext, "6124200773");
    assert_eq!(ff1.decrypt(&ciphertext, None)?, "0123456789");
    Ok(())
}
```

### Check it against NIST

The same NIST sample 2 check in Python. Its key is a published test key, for checking only:

```python
nist = FF1(
    key=bytes.fromhex("2B7E151628AED2A6ABF7158809CF4F3C"),
    radix=10,
    alphabet="0123456789",
    tweak=b"9876543210",
)
assert nist.encrypt("0123456789") == "6124200773"
```

## Security notes — read before use

FF1 is a deterministic permutation for a fixed key and tweak. That has operational consequences:

1. **Equal plaintexts produce equal ciphertexts** under the same key and tweak. NIST recommends
   varying the tweak with each encryption instance where feasible — derive it from stable record
   context so identical plaintexts in different records encrypt differently.
2. **FF1 provides confidentiality only — no integrity or authentication.** Modified ciphertext
   decrypts to another plausible in-domain value; there is no error, and the tampering is
   invisible. Applications needing tamper detection must authenticate the ciphertext and its
   context separately, where their format allows.
3. **A wrong key or tweak does not raise.** Decryption with the wrong key or tweak yields
   plausible-looking plaintext, not an exception. There is no way to detect key mismatch from
   the output alone.
4. **The one-million-value domain is a standards floor, not a guarantee.** `radix ** minlen >=
   1_000_000` rules out trivially enumerable domains, but a determined attacker with oracle
   access can still search a million-value space. Small-domain FPE needs rate limiting or
   access control around the encryption interface.
5. **Validation exceptions never echo your data.** Rejected values are located by index, not
   repeated in the message, so a malformed record does not leak plaintext into your logs.

## Why you can trust this implementation

A subtly wrong FF1 still round-trips perfectly while producing ciphertext no conformant
implementation can read, and by the time anyone notices, the data is written. So conformance is the
product here, and it is evidenced rather than asserted:

- **All nine NIST sample vectors** in both directions, and **every per-round intermediate value**
  NIST publishes, for every round of every sample. Compensating bugs can pass an output test; they
  cannot pass this one.
- **Differential tests against an independent implementation** across radices 2, 10, 16, 32, 36,
  62, 256 and 65535, at every length where FF1's block structure changes. NIST publishes vectors
  for radix 10 and 36 only. The oracle is checked against NIST first, and its outputs are frozen
  into the repository.
- **Exhaustive bijectivity** over two whole domains: radix 2 at length 20 and radix 10 at length 6.
- **Vectors transcribed from the NIST document**, never regenerated from this code.
- **100% line and branch coverage** of the Python package, enforced in CI. The Rust core passes the
  whole Python conformance suite bit for bit, and its own tests of the same fixtures.

Each known way FF1 implementations go wrong has a dedicated test:

| Known failure mode | How it is prevented |
|---|---|
| Floating-point `ceil(v · log₂(radix))` — the Bouncy Castle bug class | Exact integer arithmetic; an AST scan fails the build if `math.log`, `ceil`, `/` or any float literal appears in the core |
| `b` derived from `u` instead of `v` | Asserted against the traced value, not a round-trip — which passes either way |
| Wrong `S` expansion when `d > 16` | Differential cases at each block-count transition; no NIST sample reaches this branch |
| Mirrored parity rule in decrypt | Encrypt and decrypt share one code path for it |
| Silent coercion of bad input | Every rejection raises a typed exception; a 50-case sweep asserts nothing escapes as a bare `AttributeError` or `KeyError` |

This is strong conformance evidence, not proof: see [what this is not](#what-this-is-not).

## Why FF1 only — and why FF3 is excluded

SP 800-38G originally specified FF1 and FF3. FF3 was revised to FF3-1 after an attack, but Beyne
then showed a weakness in the **tweak schedule** that affects FF3 and FF3-1 alike, and the
**February 2025 second public draft of SP 800-38G Rev. 1 removes FF3 entirely**. FF1 is the only
format-preserving mode left standing, so this project will never implement FF3 or FF3-1: no flag,
no opt-in, no plan to add one.

## Limits

SP 800-38G, with the tighter limits of its Rev. 1 second public draft. Inputs below the minimum
domain fail closed with `LengthError`, even where older libraries accept them.

| Constraint | Value |
|---|---|
| Minimum domain | `radix ** minlen >= 1_000_000`: 6 numerals at radix 10, 4 at radix 36 |
| Maximum length | `2 ** 32 - 1` numerals; tweaks up to `2 ** 32 - 1` bytes |
| Key sizes | AES-128, AES-192, AES-256 |
| Radix | `2 <= radix < 2**16`, a deliberate subset of the specification's range |

Why each limit is where it is: [`docs/configuration.md`](https://github.com/joelee/fpr-ff1/blob/main/docs/configuration.md#domain-limits-are-stricter-than-the-2016-text).

## Backends and platforms

In Python, `FF1(..., backend="rust")` opts in to the compiled backend. `backend="python"` is the
default and the reference implementation. Both produce bit-identical ciphertext and raise identical
exceptions, because validation runs in Python for both.

Native wheels carry the compiled backend for Linux x86_64 and aarch64 (glibc 2.34 or newer), macOS
on Intel and Apple silicon, and Windows x64, on CPython 3.12 to 3.14 ([wheel list](https://github.com/joelee/fpr-ff1/blob/main/docs/configuration.md#distribution-and-backend-availability)).
Elsewhere, including musl, older glibc and free-threaded builds, `pip` installs the pure-Python
wheel, and `backend="rust"` raises `BackendError` rather than falling back silently.

## Performance

Measured on one core, CPython 3.12.13, Linux x86_64 (AMD Ryzen AI Max+ PRO 395), extension built
in release mode with rustc 1.98.1 — reproduce with `just bench`:

| Input | `backend="python"` | `backend="rust"` | Speedup |
|---|---:|---:|---:|
| 6 numerals, radix 10 | 29.5 µs/op | 4.1 µs/op | ~7.3× |
| n = 100, radix 10 | 110.6 µs/op | 38.8 µs/op | ~2.9× |
| n = 1,000, radix 10 | 966.0 µs/op | 399.5 µs/op | ~2.4× |
| n = 5,000, radix 10 | 5.3 ms/op | 2.2 ms/op | ~2.5× |
| n = 20,000, radix 10 | 27.9 ms/op | 9.9 ms/op | ~2.8× |
| n = 100, radix 256 | 145.6 µs/op | 50.2 µs/op | ~2.9× |
| n = 1,000, radix 256 | 2.2 ms/op | 0.2 ms/op | ~11× |
| n = 5,000, radix 256 | 11.2 ms/op | 1.0 ms/op | ~11× |
| n = 20,000, radix 256 | 45.7 ms/op | 4.1 ms/op | ~11× |

The compiled backend is faster on every shape measured: at short inputs it avoids the per-call
cipher setup that dominates pure Python, and at long inputs both use subquadratic numeral
conversion. These are one machine's numbers; measure your own data with `just bench`.

## Python API at a glance

```python
assert ff1.decrypt_numerals(ff1.encrypt_numerals([1, 2, 3, 4, 5, 6])) == [1, 2, 3, 4, 5, 6]
assert ff1.decrypt(ff1.encrypt("123456", b"per-call"), b"per-call") == "123456"  # per-call tweak
assert ff1.min_length == 6
```

Numerals need no alphabet. Every rejection raises a typed exception derived from `FF1Error` that
never echoes your data. Instances are thread-safe and picklable (pickling serialises the key), and
the compiled backend releases the GIL. Full reference:
[`docs/python-api.md`](https://github.com/joelee/fpr-ff1/blob/main/docs/python-api.md). Rust API: [docs.rs](https://docs.rs/fpr-ff1).

## Migrating from `ubiq_security_fpe`

`fpr-ff1` replaces the deprecated, unmaintained `ubiq_security_fpe`. **The two produce identical
ciphertext** in both directions, enforced by `tests/test_interoperability.py`, so existing data
stays readable without re-encryption. One trap: the legacy `twk_max_len=0` meant "no maximum",
which here is `max_tweak_len=None`; a literal `0` means empty tweaks only. The
[migration guide](https://github.com/joelee/fpr-ff1/blob/main/docs/migrating-from-ubiq.md) has the API mapping and every behaviour change.

## What this is not

- **Not FIPS validated.** Passing the published NIST sample vectors is conformance evidence, not
  FIPS 140 validation, and no such claim is made.
- **Not independently audited**, and **not constant-time**; see [`SECURITY.md`](https://github.com/joelee/fpr-ff1/blob/main/SECURITY.md).
- **No key zeroization.** Python `bytes` are immutable and the interpreter may copy them; the Rust
  crate holds keys in ordinary heap memory and does not wipe them.
- **Not a key-management or tokenisation toolkit, permanently.** No key generation, storage or
  derivation, identifier generation, persistence, checksums or application-specific alphabets.

## Documentation

- [Python API reference](https://github.com/joelee/fpr-ff1/blob/main/docs/python-api.md) ·
  [Migrating from `ubiq_security_fpe`](https://github.com/joelee/fpr-ff1/blob/main/docs/migrating-from-ubiq.md) ·
  [Configuration and limits](https://github.com/joelee/fpr-ff1/blob/main/docs/configuration.md)
- [Rust crate](https://github.com/joelee/fpr-ff1/blob/main/rust/fpr-ff1/README.md) · [Rust API on docs.rs](https://docs.rs/fpr-ff1)
- [Architecture](https://github.com/joelee/fpr-ff1/blob/main/docs/architecture.md) · [Developer guide](https://github.com/joelee/fpr-ff1/blob/main/docs/developer-guide.md) ·
  [Changelog](https://github.com/joelee/fpr-ff1/blob/main/CHANGELOG.md) · [Security policy](https://github.com/joelee/fpr-ff1/blob/main/SECURITY.md) ·
  [Contributing](https://github.com/joelee/fpr-ff1/blob/main/CONTRIBUTING.md) · [Code of conduct](https://github.com/joelee/fpr-ff1/blob/main/CODE_OF_CONDUCT.md)

## Development

Requires Python 3.12, `uv` and `just`; the compiled backend and the crate also need Rust.

```bash
just setup    # create venv and install deps
just quality  # format check, lint, typecheck, tests
```

## License

The Python package is [MIT](https://github.com/joelee/fpr-ff1/blob/main/LICENSE). The Rust crate is MIT OR Apache-2.0, at your option; its
sources are also compiled into the Python platform wheels, where the MIT option applies.
