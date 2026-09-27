# fpr-ff1

[![crates.io](https://img.shields.io/crates/v/fpr-ff1.svg)](https://crates.io/crates/fpr-ff1)
[![docs.rs](https://img.shields.io/docsrs/fpr-ff1)](https://docs.rs/fpr-ff1)
[![MSRV 1.89](https://img.shields.io/badge/MSRV-1.89-blue.svg)](https://github.com/joelee/fpr-ff1/blob/main/rust/fpr-ff1/Cargo.toml)
[![License: MIT OR Apache-2.0](https://img.shields.io/badge/license-MIT%20OR%20Apache--2.0-blue.svg)](https://github.com/joelee/fpr-ff1/tree/main/rust/fpr-ff1)

**FF1 format-preserving encryption (NIST SP 800-38G) for Rust, conformance-tested round by round
against the published NIST vectors.**

Format-preserving encryption turns a value into ciphertext of the same shape. A 16-digit card
number encrypts to 16 digits, a 9-digit identifier to 9 digits, and a code over `A-Z0-9` stays over
`A-Z0-9`. Encrypted values still fit the column types, fixed-width files, validators and APIs built
for the plaintext, so you can protect data in systems you cannot redesign:

- card numbers and account numbers in legacy schemas;
- national and customer identifiers passed between services;
- production data copied into test and analytics environments, still valid for the code that reads
  it.

FF1 is reversible encryption, not hashing or vault tokenisation: anyone holding the key can
decrypt. It provides confidentiality only (see [What this is not](#what-this-is-not)).

## Install

```sh
cargo add fpr-ff1
```

Requires Rust 1.89 or newer. The direct dependencies are RustCrypto's `aes` and the
`num-bigint` family. API documentation is on [docs.rs](https://docs.rs/fpr-ff1).

## Quick start

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

The key and tweak above are NIST's published sample 2 values, so this example is also a
conformance check: `6124200773` is the ciphertext NIST publishes. Never use a published key for real
data: load keys from your secret store, and derive the tweak from stable record context (a table
name, a tenant ID) so that equal values in different contexts encrypt differently.

The numeral interface is the primitive and needs no alphabet. This is NIST sample 1:

```rust
use fpr_ff1::FF1;

fn main() -> Result<(), fpr_ff1::Error> {
    // NIST SP 800-38G sample 1: the same published test key, no tweak.
    let key: [u8; 16] = [
        0x2B, 0x7E, 0x15, 0x16, 0x28, 0xAE, 0xD2, 0xA6,
        0xAB, 0xF7, 0x15, 0x88, 0x09, 0xCF, 0x4F, 0x3C,
    ];
    let ff1 = FF1::new(&key, 10)?;
    let ciphertext = ff1.encrypt_numerals(&[0, 1, 2, 3, 4, 5, 6, 7, 8, 9], None)?;
    assert_eq!(ciphertext, [2, 4, 3, 3, 4, 7, 7, 4, 8, 4]);
    Ok(())
}
```

Every rejection is an
[`Error`](https://docs.rs/fpr-ff1/latest/fpr_ff1/struct.Error.html) whose
[`kind()`](https://docs.rs/fpr-ff1/latest/fpr_ff1/struct.Error.html#method.kind) says what was
wrong. Messages name the position or length at fault, never key material or plaintext:

```rust
use fpr_ff1::{ErrorKind, FF1};

fn main() -> Result<(), fpr_ff1::Error> {
    let key = [0u8; 16]; // for the example only
    let ff1 = FF1::new(&key, 10)?;
    let err = ff1.encrypt_numerals(&[1, 2, 3], None).unwrap_err();
    assert_eq!(err.kind(), ErrorKind::Length);
    assert_eq!(err.to_string(), "plaintext length 3 below minimum 6 for radix 10");
    Ok(())
}
```

`FF1` is `Clone`, `Send` and `Sync`. It holds no cipher state between calls, so one instance can
serve every thread.

## Why trust it

A subtly wrong FF1 still round-trips perfectly while producing ciphertext no conformant
implementation can read. So the evidence here goes beyond "decrypt inverts encrypt". Each item
below is a test in this crate, run in CI on Linux, macOS and Windows; all but the exhaustive sweeps
also run on Rust 1.89:

- **All nine NIST SP 800-38G samples**, in both directions.
- **Every per-round intermediate value** NIST publishes, for every round of every sample. Two
  compensating bugs can pass an output test; they cannot pass this one.
- **46 frozen vectors from an independent implementation** over radices 2, 10, 16, 32, 36, 62, 256
  and 65535, with inputs of up to 193 numerals. These cover the long-input path (`d > 16`) that no
  NIST sample reaches.
- **The FIPS 197 AES known-answer vectors** for the block cipher underneath.
- **Exhaustive bijectivity:** every one of the 1,048,576 values at radix 2, length 20, and the
  1,000,000 values at radix 10, length 6, map to distinct ciphertexts.
- **Property tests** for round trip, determinism, and key and tweak sensitivity.
- **Exact integer arithmetic**, enforced by a test that scans the crate's source for floating-point
  types, functions and literals. A floating-point `ceil(v * log2(radix))` is the bug class that has
  broken other FF1 implementations.

This is the same core that runs behind the Python package's `backend="rust"`, where the full Python
conformance suite checks it bit for bit against the pure-Python reference implementation.

## Limits

- **Keys:** 128, 192 or 256 bits.
- **Radix:** `2 <= radix < 2**16`, a deliberate subset of the specification's range; numerals are
  `u16`.
- **Minimum domain:** `radix**minlen >= 1_000_000`, from the Rev. 1 draft (stricter than the 2016
  text), so the shortest input is 6 numerals at radix 10 and 20 at radix 2.
- **Maximum length:** `2**32 - 1` numerals, and a tweak of at most `2**32 - 1` bytes.
- **FF1 only.** FF3 and FF3-1 are deliberately absent: the second public draft of SP 800-38G Rev. 1
  removes FF3 after a published weakness in its tweak schedule.

## What this is not

- **No integrity.** Modified ciphertext decrypts to another plausible value without an error, and a
  wrong key or tweak does not fail either. Authenticate the ciphertext separately if you need to
  detect tampering.
- **Not FIPS validated.** Passing the published NIST vectors is conformance evidence, not
  validation.
- **Not independently audited.**
- **Not constant-time.** The big-integer arithmetic runs in time that depends on the values
  processed. If your threat model includes a local timing adversary, this is not the right
  implementation.
- **No key zeroization.** Key material is held in ordinary heap memory and is not wiped.
- **No key management.** Generating, storing, deriving and rotating keys is the caller's job.

## Testing

The conformance tests read the shared fixtures in the repository's `tests/vectors/` directory
-- the NIST samples and per-round intermediates, the FIPS 197 AES vectors, the frozen oracle
vectors and the validation cases -- which a published crate cannot contain. Run them from a
checkout of the repository. In the packaged crate those tests skip, and because Rust's test
harness hides a passing test's output, the skip is not visible: set `FPR_FF1_REQUIRE_FIXTURES=1`
to turn a missing fixture into a failure, as the repository's own runs and CI always do.

## Also available for Python

The same FF1 core ships in the [`fpr-ff1`](https://pypi.org/project/fpr-ff1/) Python package,
whose pure-Python implementation is the reference. The two produce bit-identical ciphertext and
validate inputs with the same rules, order and messages, checked by a case file both test suites
share. The crate's version always matches the Python package's. Source, issues and the security
policy are at [github.com/joelee/fpr-ff1](https://github.com/joelee/fpr-ff1).

## Licence

Licensed under either of the Apache License, Version 2.0, or the MIT licence, at your option.
