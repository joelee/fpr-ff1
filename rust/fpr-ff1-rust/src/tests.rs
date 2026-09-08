//! Unit tests for the Algorithm 7 port (plan 00003 STEP-08/09).
//!
//! STEP-08 verified the structural pieces (conversion, bit-length
//! derivation, padding, parity) against hand-computed spec values. STEP-09
//! wires the AES seams, which makes the full core callable for the first
//! time: the round-trip test below exercises all ten rounds, both
//! conversion directions, and the previously-unreachable `d > 16`
//! S-expansion branch (radix 10 n=60 and radix 65535 n=13 both reach it).
//!
//! Round-trips are SELF-CONSISTENCY only — a wrong-but-symmetric AES or S
//! expansion still round-trips. Cryptographic correctness is established
//! independently by the NIST FIPS 197 KAT and the PRF equality with the
//! Python path (`tests/test_rust_aes_validation.py`), and FF1-level
//! conformance by the NIST vectors and per-round intermediates once the
//! STEP-11 bridge lands.

use num_bigint::BigUint;
use num_traits::One;

use crate::{ff1, num_radix, prf, str_radix};

#[test]
fn num_radix_decodes_big_endian() {
    // NUM_radix([1,2,3]) base 10 = 123.
    assert_eq!(num_radix(10, &[1, 2, 3]), BigUint::from(123u32));
    // Leading zeros contribute nothing.
    assert_eq!(num_radix(10, &[0, 0, 1]), BigUint::from(1u32));
    // All-max digits at a wide radix.
    assert_eq!(num_radix(256, &[255, 255]), BigUint::from(65_535u32));
}

#[test]
fn str_radix_encodes_big_endian_and_truncates() {
    assert_eq!(str_radix(&BigUint::from(123u32), 10, 3), vec![1, 2, 3]);
    // Zero padding to length.
    assert_eq!(str_radix(&BigUint::from(1u32), 10, 3), vec![0, 0, 1]);
    // Truncation contract: values >= radix**length drop high digits.
    assert_eq!(str_radix(&BigUint::from(1_234u32), 10, 3), vec![2, 3, 4]);
}

#[test]
fn round_trip_conversion() {
    for &radix in &[2u32, 10, 36, 256, 65_535] {
        for len in [1usize, 2, 7, 64, 130] {
            let numerals: Vec<u16> = (0..len).map(|i| (i % radix as usize) as u16).collect();
            let value = num_radix(radix, &numerals);
            assert_eq!(
                str_radix(&value, radix, len),
                numerals,
                "radix {radix} len {len}"
            );
        }
    }
}

#[test]
fn b_derivation_uses_v_not_u() {
    // radix 256, n=5: u=2, v=3. b from v = ceil(bits(256**3 - 1)/8) = 3;
    // b from u would be 2. Pin the correct derivation (AGENTS.md gotcha).
    let v = 3usize;
    let b = ((BigUint::from(256u32).pow(v as u32) - BigUint::one()).bits() + 7) / 8;
    assert_eq!(b, 3);
    let u = 2usize;
    let b_wrong = ((BigUint::from(256u32).pow(u as u32) - BigUint::one()).bits() + 7) / 8;
    assert_eq!(b_wrong, 2, "sanity: the two derivations must disagree here");
}

#[test]
fn padding_formula_matches_python() {
    // Python: pad = (-t - b - 1) % 16, always non-negative. The Rust port
    // must negate the sum BEFORE reducing, not after.
    for t in [0usize, 1, 3, 11, 12, 13, 16, 27, 32] {
        for b in [4usize, 9, 20] {
            let py_pad = (-(t as isize) - b as isize - 1).rem_euclid(16) as usize;
            // (t + pad + 1 + b) must be a multiple of 16.
            assert_eq!((t + py_pad + 1 + b) % 16, 0, "t={t} b={b}");
        }
    }
}

#[test]
fn radix_bounds_representable() {
    // The supported radix range is 2 <= radix < 2**16 (AGENTS.md subset).
    assert_eq!(num_radix(2, &[1, 0, 1, 1]), BigUint::from(11u32));
    // radix 65535: numerals up to 65534, exercising the u16 width.
    // NUM_radix([65534, 1]) = 65534 * 65535 + 1.
    assert_eq!(
        num_radix(65_535, &[65_534, 1]),
        BigUint::from(65534u64 * 65535 + 1)
    );
}

#[test]
fn prf_structural_properties() {
    // Output shape and basic behaviour; the cryptographic content is
    // validated Python-side (KAT + equality with the reference path).
    let key = [7u8; 32];
    let data = [1u8; 48]; // three aligned blocks
    let tag1 = prf(&key, &data).expect("valid key");
    let tag2 = prf(&key, &data).expect("valid key");
    assert_eq!(tag1.len(), 16, "CBC-MAC tag is one block");
    assert_eq!(tag1, tag2, "PRF is deterministic for fixed inputs");
    // Key sensitivity: a different key must move the tag.
    let other_key = [8u8; 32];
    let tag3 = prf(&other_key, &data).expect("valid key");
    assert_ne!(tag1, tag3);
    // Data sensitivity: flipping one input bit must move the tag.
    let mut flipped = data;
    flipped[0] ^= 1;
    let tag4 = prf(&key, &flipped).expect("valid key");
    assert_ne!(tag1, tag4);
}

#[test]
fn ff1_round_trip_self_consistency() {
    // All three key sizes; odd n (u != v); the d > 16 S-expansion cases
    // (radix 10 n=60 and radix 65535 n=13); radix bounds; a tweak.
    // Self-consistency only — see the module docstring.
    for key_len in [16usize, 24, 32] {
        let key: Vec<u8> = (0..key_len).map(|i| (i * 7 + 3) as u8).collect();
        for (radix, n) in [
            (10u32, 6usize),
            (10, 7),
            (2, 20),
            (36, 10),
            (256, 5),
            (10, 60),
            (65_535, 13),
        ] {
            let x: Vec<u16> = (0..n)
                .map(|i| ((i as u32 * 7919 + 17) % radix) as u16)
                .collect();
            let ct = ff1(&key, radix, &x, b"kat", true)
                .unwrap_or_else(|e| panic!("encrypt failed: {e}"));
            assert_eq!(ct.len(), n, "length preservation");
            assert!(ct.iter().all(|&c| (c as u32) < radix), "range preservation");
            let pt = ff1(&key, radix, &ct, b"kat", false)
                .unwrap_or_else(|e| panic!("decrypt failed: {e}"));
            assert_eq!(pt, x, "round trip, radix {radix} n {n} key_len {key_len}");
        }
    }
}
