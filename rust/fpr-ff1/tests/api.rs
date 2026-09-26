//! The public API, exercised from outside the crate (plan 00009 STEP-06).
//!
//! Integration tests see only what a downstream crate sees, so these also
//! prove the API boundary: nothing here can reach `__internal`.

use fpr_ff1::{ErrorKind, FF1};

const KEY_128: [u8; 16] = [
    0x2B, 0x7E, 0x15, 0x16, 0x28, 0xAE, 0xD2, 0xA6, 0xAB, 0xF7, 0x15, 0x88, 0x09, 0xCF, 0x4F, 0x3C,
];
const NIST_TWEAK: [u8; 10] = [0x39, 0x38, 0x37, 0x36, 0x35, 0x34, 0x33, 0x32, 0x31, 0x30];

#[test]
fn numeral_interface_reproduces_nist_sample_1() {
    let ff1 = FF1::new(&KEY_128, 10).expect("valid configuration");
    let pt = [0u16, 1, 2, 3, 4, 5, 6, 7, 8, 9];
    let ct = ff1.encrypt_numerals(&pt, None).expect("valid input");
    assert_eq!(ct, [2, 4, 3, 3, 4, 7, 7, 4, 8, 4]);
    assert_eq!(ff1.decrypt_numerals(&ct, None).expect("valid input"), pt);
}

#[test]
fn string_interface_reproduces_nist_sample_2() {
    let ff1 = FF1::builder(&KEY_128, 10)
        .alphabet("0123456789")
        .tweak(&NIST_TWEAK)
        .build()
        .expect("valid configuration");
    assert_eq!(
        ff1.encrypt("0123456789", None).expect("valid"),
        "6124200773"
    );
    assert_eq!(
        ff1.decrypt("6124200773", None).expect("valid"),
        "0123456789"
    );
}

#[test]
fn per_call_tweak_overrides_the_default_and_empty_equals_absent() {
    let ff1 = FF1::new(&KEY_128, 10).expect("valid");
    let pt = [0u16, 1, 2, 3, 4, 5, 6, 7, 8, 9];
    // NIST sample 2 through a per-call tweak.
    assert_eq!(
        ff1.encrypt_numerals(&pt, Some(&NIST_TWEAK)).expect("valid"),
        [6, 1, 2, 4, 2, 0, 0, 7, 7, 3]
    );
    // An explicit empty tweak and an omitted tweak are identical.
    assert_eq!(
        ff1.encrypt_numerals(&pt, Some(&[])).expect("valid"),
        ff1.encrypt_numerals(&pt, None).expect("valid")
    );
}

#[test]
fn length_accessors() {
    let ff1 = FF1::new(&KEY_128, 10).expect("valid");
    assert_eq!(ff1.min_length(), 6);
    assert_eq!(ff1.max_length(), (1u64 << 32) - 1);
    assert_eq!(FF1::new(&KEY_128, 2).expect("valid").min_length(), 20);
}

#[test]
fn construction_rejects_in_the_python_order() {
    // Key before radix: both wrong reports the key.
    let err = FF1::new(&[0u8; 15], 1).expect_err("rejected");
    assert_eq!(err.kind(), ErrorKind::KeyLength);
    // Radix before tweak bounds.
    let err = FF1::builder(&KEY_128, 1)
        .min_tweak_len(8)
        .max_tweak_len(4)
        .build()
        .expect_err("rejected");
    assert_eq!(err.kind(), ErrorKind::Radix);
    // Bounds before the default tweak: an unsatisfiable configuration is
    // reported as such, not as whichever bound the default tweak violated.
    let err = FF1::builder(&KEY_128, 10)
        .tweak(b"")
        .min_tweak_len(8)
        .max_tweak_len(4)
        .build()
        .expect_err("rejected");
    assert_eq!(
        err.to_string(),
        "min_tweak_len 8 exceeds max_tweak_len 4; no tweak length could satisfy both bounds"
    );
    // The default tweak before the alphabet.
    let err = FF1::builder(&KEY_128, 10)
        .tweak(b"abc")
        .max_tweak_len(2)
        .alphabet("012")
        .build()
        .expect_err("rejected");
    assert_eq!(err.kind(), ErrorKind::TweakLength);
    // Alphabet problems.
    let err = FF1::builder(&KEY_128, 10)
        .alphabet("0123456788")
        .build()
        .expect_err("rejected");
    assert_eq!(err.kind(), ErrorKind::Alphabet);
}

#[test]
fn calls_reject_in_the_python_order() {
    let ff1 = FF1::builder(&KEY_128, 10)
        .max_tweak_len(2)
        .build()
        .expect("valid");
    // Length before tweak: both wrong reports the length.
    let err = ff1
        .encrypt_numerals(&[1, 2, 3], Some(b"abc"))
        .expect_err("rejected");
    assert_eq!(err.kind(), ErrorKind::Length);
    assert_eq!(
        err.to_string(),
        "plaintext length 3 below minimum 6 for radix 10"
    );
    // Tweak before numerals.
    let err = ff1
        .encrypt_numerals(&[1, 2, 3, 4, 5, 99], Some(b"abc"))
        .expect_err("rejected");
    assert_eq!(err.kind(), ErrorKind::TweakLength);
    // Numerals, by position, labelled by side.
    let err = ff1
        .decrypt_numerals(&[1, 2, 3, 4, 5, 99], None)
        .expect_err("rejected");
    assert_eq!(
        err.to_string(),
        "ciphertext[5] is out of range for radix 10"
    );
}

#[test]
fn string_interface_needs_an_alphabet_and_known_characters() {
    let ff1 = FF1::new(&KEY_128, 10).expect("valid");
    let err = ff1.encrypt("0123456789", None).expect_err("rejected");
    assert_eq!(err.kind(), ErrorKind::AlphabetRequired);
    assert!(err.to_string().contains("use encrypt_numerals"));
    let err = ff1.decrypt("0123456789", None).expect_err("rejected");
    assert!(err.to_string().contains("use decrypt_numerals"));

    let ff1 = FF1::builder(&KEY_128, 10)
        .alphabet("0123456789")
        .build()
        .expect("valid");
    let err = ff1.encrypt("01234x6789", None).expect_err("rejected");
    assert_eq!(err.kind(), ErrorKind::ValueRange);
    assert_eq!(
        err.to_string(),
        "character at index 5 is not in the alphabet"
    );
}

#[test]
fn a_literal_zero_maximum_means_empty_tweaks_only() {
    let ff1 = FF1::builder(&KEY_128, 10)
        .max_tweak_len(0)
        .build()
        .expect("valid");
    let pt = [1u16, 2, 3, 4, 5, 6];
    assert!(ff1.encrypt_numerals(&pt, None).is_ok());
    assert_eq!(
        ff1.encrypt_numerals(&pt, Some(b"x"))
            .expect_err("rejected")
            .kind(),
        ErrorKind::TweakLength
    );
}

#[test]
fn instances_are_send_and_sync() {
    fn assert_send_sync<T: Send + Sync>() {}
    assert_send_sync::<FF1>();
}
