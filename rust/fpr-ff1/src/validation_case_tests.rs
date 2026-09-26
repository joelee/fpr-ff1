//! Shared validation cases, Rust side (plan 00009 STEP-08).
//!
//! `tests/vectors/validation_cases.json` is read by this module and by
//! `tests/test_validation_cases.py`. Both must reach the same outcome for
//! every case: accepted, or rejected with the named Python exception class
//! -- mapped here to one `ErrorKind` -- and exactly the recorded message.

use serde_json::Value;

use crate::{Error, ErrorKind, FF1};

/// The Python exception class each kind corresponds to. Exhaustive on
/// purpose: a new `ErrorKind` does not compile until it is mapped, and then
/// the coverage test below requires a case for it.
fn python_class(kind: ErrorKind) -> &'static str {
    match kind {
        ErrorKind::KeyLength => "KeyLengthError",
        ErrorKind::Radix => "RadixError",
        ErrorKind::Length => "LengthError",
        ErrorKind::ValueRange => "ValueRangeError",
        ErrorKind::TweakLength => "TweakLengthError",
        ErrorKind::Alphabet => "AlphabetError",
        ErrorKind::AlphabetRequired => "FF1Error",
    }
}

const ALL_KINDS: [ErrorKind; 7] = [
    ErrorKind::KeyLength,
    ErrorKind::Radix,
    ErrorKind::Length,
    ErrorKind::ValueRange,
    ErrorKind::TweakLength,
    ErrorKind::Alphabet,
    ErrorKind::AlphabetRequired,
];

fn cases() -> Vec<Value> {
    let path = concat!(
        env!("CARGO_MANIFEST_DIR"),
        "/../../tests/vectors/validation_cases.json"
    );
    let text = std::fs::read_to_string(path)
        .unwrap_or_else(|e| panic!("shared case file {path} is required and unreadable: {e}"));
    let doc: Value = serde_json::from_str(&text).expect("valid JSON");
    doc["cases"].as_array().expect("cases").clone()
}

fn hex(s: &str) -> Vec<u8> {
    (0..s.len())
        .step_by(2)
        .map(|i| u8::from_str_radix(&s[i..i + 2], 16).expect("hex"))
        .collect()
}

fn opt_usize(v: &Value, key: &str) -> Option<usize> {
    v.get(key)
        .map(|n| usize::try_from(n.as_u64().expect("unsigned")).expect("fits usize on 64-bit"))
}

fn outcome(case: &Value) -> Result<(), Error> {
    let construct = &case["construct"];
    let key_len = usize::try_from(construct["key_len"].as_u64().expect("key_len")).expect("small");
    let key: Vec<u8> = (0..key_len)
        .map(|i| u8::try_from(i).expect("small"))
        .collect();
    let tweak = construct
        .get("tweak_hex")
        .map(|t| hex(t.as_str().expect("hex")));
    let radix = u32::try_from(construct["radix"].as_u64().expect("radix")).expect("u32");

    let mut builder = FF1::builder(&key, radix);
    if let Some(alphabet) = construct.get("alphabet") {
        builder = builder.alphabet(alphabet.as_str().expect("str"));
    }
    if let Some(t) = &tweak {
        builder = builder.tweak(t);
    }
    if let Some(n) = opt_usize(construct, "min_tweak_len") {
        builder = builder.min_tweak_len(n);
    }
    if let Some(n) = opt_usize(construct, "max_tweak_len") {
        builder = builder.max_tweak_len(n);
    }
    let ff1 = builder.build()?;

    let Some(call) = case.get("call") else {
        return Ok(());
    };
    let call_tweak = call.get("tweak_hex").map(|t| hex(t.as_str().expect("hex")));
    let tweak = call_tweak.as_deref();
    let numerals = || -> Vec<u16> {
        call["x"]
            .as_array()
            .expect("x")
            .iter()
            .map(|n| u16::try_from(n.as_u64().expect("numeral")).expect("u16"))
            .collect()
    };
    let text = || call["s"].as_str().expect("s");
    match call["op"].as_str().expect("op") {
        "encrypt_numerals" => ff1.encrypt_numerals(&numerals(), tweak).map(drop),
        "decrypt_numerals" => ff1.decrypt_numerals(&numerals(), tweak).map(drop),
        "encrypt" => ff1.encrypt(text(), tweak).map(drop),
        "decrypt" => ff1.decrypt(text(), tweak).map(drop),
        op => panic!("unknown op {op}"),
    }
}

#[test]
fn every_shared_case_has_the_same_outcome() {
    let mut ran = 0;
    let mut python_only = 0;
    for case in cases() {
        let id = case["id"].as_str().expect("id");
        if case.get("python_only").is_some() {
            python_only += 1;
            continue;
        }
        let expect = case["expect"].as_str().expect("expect");
        match outcome(&case) {
            Ok(()) => assert_eq!(expect, "accepted", "{id}: accepted, expected {expect}"),
            Err(err) => {
                assert_eq!(python_class(err.kind()), expect, "{id}: {err}");
                assert_eq!(
                    err.to_string(),
                    case["message"].as_str().expect("message"),
                    "{id}"
                );
            }
        }
        ran += 1;
    }
    assert!(ran >= 50, "only {ran} shared cases ran");
    // Only cases that declare why may be skipped here.
    assert_eq!(python_only, 1, "python_only cases changed; review each one");
}

#[test]
fn every_error_kind_has_a_shared_case() {
    let expects: Vec<String> = cases()
        .iter()
        .filter(|c| c.get("python_only").is_none())
        .map(|c| c["expect"].as_str().expect("expect").to_string())
        .collect();
    for kind in ALL_KINDS {
        let class = python_class(kind);
        assert!(
            expects.iter().any(|e| e == class),
            "no shared case for {kind:?} ({class})"
        );
    }
    assert!(expects.iter().any(|e| e == "accepted"));
}
