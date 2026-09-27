# fpr-ff1

FF1 format-preserving encryption, from NIST SP 800-38G, in Rust.

FF1 encrypts a string of numerals to another string of the same length over the same alphabet:
a 16-digit card number to 16 digits, a postcode to a postcode. This crate implements FF1 only.
FF3 and FF3-1 are deliberately absent: the second public draft of SP 800-38G Rev. 1 removes FF3
after a published weakness in its tweak schedule.

It is the Rust core of the [`fpr-ff1`](https://github.com/joelee/fpr-ff1) Python package, where
the pure-Python implementation is the reference. The two produce bit-identical ciphertext, and
the Rust code is tested against the same published NIST sample vectors, per-round intermediate
values and independent-oracle vectors as the Python package.

## Usage

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

The numeral interface is the primitive and needs no alphabet:

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

## Limits

- **Keys:** 128, 192 or 256 bits.
- **Radix:** `2 <= radix < 2**16`, a deliberate subset of the specification's range; numerals are
  `u16`.
- **Minimum domain:** `radix**minlen >= 1_000_000`, from the Rev. 1 draft (stricter than the 2016
  text), so the shortest input is 6 numerals at radix 10 and 20 at radix 2.
- **Maximum length:** `2**32 - 1` numerals, and a tweak of at most `2**32 - 1` bytes.
- **Arithmetic:** exact integers throughout. Bit lengths come from the integer `radix**v - 1`,
  never a floating-point logarithm.

## What this is not

- **Not FIPS validated.** Passing the published NIST vectors is conformance evidence, not
  validation.
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

## Licence

Licensed under either of the Apache License, Version 2.0, or the MIT licence, at your option.
