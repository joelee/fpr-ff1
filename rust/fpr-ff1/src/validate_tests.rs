//! Rejection tests for the validation layer (plan 00009 STEP-05).
//!
//! One test per rule in `src/fpr_ff1/_ff1.py`, with the same boundaries and
//! the same messages, so the two layers can be held in step by the shared
//! case file (STEP-08). Every rejection is also checked for leaking data:
//! no message may contain a numeral value or a key byte.

use std::collections::HashMap;

use crate::validate::{self, Operand, MAX_LEN, MAX_TWEAK_LEN};
use crate::{Error, ErrorKind};

fn rejected<T: std::fmt::Debug>(result: Result<T, Error>) -> Error {
    result.expect_err("expected a rejection")
}

#[test]
fn key_lengths() {
    for len in [16usize, 24, 32] {
        assert!(validate::key(&vec![0u8; len]).is_ok(), "len {len}");
    }
    for len in [0usize, 15, 17, 23, 25, 31, 33, 64] {
        let err = rejected(validate::key(&vec![0xABu8; len]));
        assert_eq!(err.kind(), ErrorKind::KeyLength);
        assert_eq!(
            err.to_string(),
            format!("key must be 16, 24, or 32 bytes, got {len}")
        );
        // The key bytes (0xAB = 171) never appear in the message.
        assert!(!err.to_string().contains("171") && !err.to_string().contains("ab"));
    }
}

#[test]
fn radix_range() {
    for radix in [2u32, 10, 36, 256, 65_535] {
        assert!(validate::radix(radix).is_ok(), "radix {radix}");
    }
    for radix in [0u32, 1, 65_536, u32::MAX] {
        let err = rejected(validate::radix(radix));
        assert_eq!(err.kind(), ErrorKind::Radix);
        assert_eq!(
            err.to_string(),
            format!("radix must satisfy 2 <= radix < 65536, got {radix}")
        );
    }
}

#[test]
fn min_length_matches_the_python_reference() {
    // The smallest n with radix**n >= 1_000_000 (AGENTS.md tests section 3,
    // plus the boundaries either side of radix 1000).
    for (radix, expected) in [
        (2u32, 20usize),
        (10, 6),
        (16, 5),
        (32, 4),
        (36, 4),
        (256, 3),
        (999, 3),
        (1_000, 2),
        (65_535, 2),
    ] {
        assert_eq!(validate::min_length(radix), expected, "radix {radix}");
    }
}

#[test]
fn input_length_bounds() {
    assert!(validate::length(6, 6, 10, Operand::Plaintext).is_ok());
    let err = rejected(validate::length(5, 6, 10, Operand::Plaintext));
    assert_eq!(err.kind(), ErrorKind::Length);
    assert_eq!(
        err.to_string(),
        "plaintext length 5 below minimum 6 for radix 10"
    );
    let err = rejected(validate::length(5, 6, 10, Operand::Ciphertext));
    assert_eq!(
        err.to_string(),
        "ciphertext length 5 below minimum 6 for radix 10"
    );
}

#[cfg(target_pointer_width = "64")]
#[test]
fn input_length_ceiling() {
    let max = MAX_LEN as usize;
    assert!(validate::length(max, 6, 10, Operand::Plaintext).is_ok());
    let err = rejected(validate::length(max + 1, 6, 10, Operand::Plaintext));
    assert_eq!(err.kind(), ErrorKind::Length);
    assert_eq!(
        err.to_string(),
        format!("plaintext length {} above maximum {MAX_LEN}", max + 1)
    );
}

#[test]
fn numerals_out_of_range_do_not_disclose_the_value() {
    assert!(validate::numerals(&[0, 9, 5], 10, Operand::Plaintext).is_ok());
    let err = rejected(validate::numerals(&[1, 2, 47_111], 10, Operand::Plaintext));
    assert_eq!(err.kind(), ErrorKind::ValueRange);
    assert_eq!(err.to_string(), "plaintext[2] is out of range for radix 10");
    assert!(!err.to_string().contains("47111"));
    // The boundary: radix - 1 is valid, radix is not.
    assert!(validate::numerals(&[65_534], 65_535, Operand::Ciphertext).is_ok());
    let err = rejected(validate::numerals(&[65_535], 65_535, Operand::Ciphertext));
    assert_eq!(
        err.to_string(),
        "ciphertext[0] is out of range for radix 65535"
    );
}

#[test]
fn tweak_bounds_at_construction() {
    assert!(validate::tweak_bounds(None, None).is_ok());
    assert!(validate::tweak_bounds(Some(0), Some(0)).is_ok());
    assert!(validate::tweak_bounds(Some(4), Some(8)).is_ok());
    let err = rejected(validate::tweak_bounds(Some(8), Some(4)));
    assert_eq!(err.kind(), ErrorKind::TweakLength);
    assert_eq!(
        err.to_string(),
        "min_tweak_len 8 exceeds max_tweak_len 4; no tweak length could satisfy both bounds"
    );
}

#[cfg(target_pointer_width = "64")]
#[test]
fn tweak_bounds_above_the_encodable_ceiling() {
    let ceiling = MAX_TWEAK_LEN as usize;
    assert!(validate::tweak_bounds(Some(ceiling), Some(ceiling)).is_ok());
    let err = rejected(validate::tweak_bounds(Some(ceiling + 1), None));
    assert_eq!(err.kind(), ErrorKind::TweakLength);
    assert_eq!(
        err.to_string(),
        format!(
            "min_tweak_len {} above encodable maximum tweak length {MAX_TWEAK_LEN}; \
             no tweak could satisfy it",
            ceiling + 1
        )
    );
    let err = rejected(validate::tweak_bounds(None, Some(ceiling + 1)));
    assert_eq!(
        err.to_string(),
        format!(
            "max_tweak_len {} above encodable maximum tweak length {MAX_TWEAK_LEN}; \
             bounds are rejected, not clamped",
            ceiling + 1
        )
    );
    // Python checks the minimum's ceiling before the maximum's.
    let err = rejected(validate::tweak_bounds(Some(ceiling + 1), Some(ceiling + 2)));
    assert!(err.to_string().starts_with("min_tweak_len"));
}

#[test]
fn tweak_length_against_bounds() {
    assert!(validate::tweak(0, None, None).is_ok());
    assert!(validate::tweak(4, Some(4), Some(8)).is_ok());
    assert!(validate::tweak(8, Some(4), Some(8)).is_ok());
    let err = rejected(validate::tweak(3, Some(4), Some(8)));
    assert_eq!(err.kind(), ErrorKind::TweakLength);
    assert_eq!(err.to_string(), "tweak length 3 below minimum 4");
    let err = rejected(validate::tweak(9, Some(4), Some(8)));
    assert_eq!(err.to_string(), "tweak length 9 above maximum 8");
    // A literal zero maximum means empty tweaks only (README migration note 5).
    assert!(validate::tweak(0, None, Some(0)).is_ok());
    assert!(validate::tweak(1, None, Some(0)).is_err());
}

#[cfg(target_pointer_width = "64")]
#[test]
fn tweak_length_ceiling_is_checked_first() {
    let ceiling = MAX_TWEAK_LEN as usize;
    assert!(validate::tweak(ceiling, None, None).is_ok());
    let err = rejected(validate::tweak(ceiling + 1, None, Some(ceiling + 5)));
    assert_eq!(err.kind(), ErrorKind::TweakLength);
    assert_eq!(
        err.to_string(),
        format!(
            "tweak length {} above encodable maximum {MAX_TWEAK_LEN}",
            ceiling + 1
        )
    );
}

#[test]
fn alphabet_length_and_uniqueness() {
    assert_eq!(
        validate::alphabet("0123456789", 10).expect("valid"),
        "0123456789".chars().collect::<Vec<_>>()
    );
    // Length counts Unicode scalar values, as Python counts code points.
    assert!(validate::alphabet("αβγδεζηθικ", 10).is_ok());
    let err = rejected(validate::alphabet("012345678", 10));
    assert_eq!(err.kind(), ErrorKind::Alphabet);
    assert_eq!(err.to_string(), "alphabet length 9 does not match radix 10");
    let err = rejected(validate::alphabet("0123456788", 10));
    assert_eq!(err.kind(), ErrorKind::Alphabet);
    assert_eq!(err.to_string(), "alphabet contains duplicate characters");
}

#[test]
fn decoding_rejects_characters_outside_the_alphabet() {
    let lookup: HashMap<char, u16> = "0123456789"
        .chars()
        .enumerate()
        .map(|(i, c)| (c, i as u16))
        .collect();
    assert_eq!(
        validate::decode("0912", &lookup).expect("valid"),
        vec![0, 9, 1, 2]
    );
    let err = rejected(validate::decode("12x45", &lookup));
    assert_eq!(err.kind(), ErrorKind::ValueRange);
    assert_eq!(
        err.to_string(),
        "character at index 2 is not in the alphabet"
    );
    // The offending character is plaintext and is never echoed.
    let err = rejected(validate::decode("12Z45", &lookup));
    assert!(!err.to_string().contains('Z'));
}

#[test]
fn string_interface_without_an_alphabet() {
    let err = validate::alphabet_required("encrypt_numerals");
    assert_eq!(err.kind(), ErrorKind::AlphabetRequired);
    assert_eq!(
        err.to_string(),
        "alphabet required for string interface; use encrypt_numerals for the numeral interface"
    );
}

#[test]
fn error_is_a_std_error_and_send_sync() {
    fn assert_traits<T: std::error::Error + Send + Sync + 'static>() {}
    assert_traits::<Error>();
}
