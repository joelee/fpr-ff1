//! Property and bijectivity tests for the public API (plan 00009 STEP-07),
//! the Rust counterparts of `tests/test_properties.py`.
//!
//! The bijectivity sweeps encrypt every value of a domain -- about two
//! million FF1 calls -- so they are `#[ignore]`d in the default run; CI runs
//! them with `cargo test --release -- --ignored`.

use proptest::prelude::*;

use crate::FF1;

/// A valid configuration and an input for it, spanning the supported radix
/// range with extra weight on the boundaries.
#[derive(Debug, Clone)]
struct Case {
    key: Vec<u8>,
    radix: u32,
    x: Vec<u16>,
}

fn case() -> impl Strategy<Value = Case> {
    let radix = prop_oneof![
        2u32..=40,
        Just(256u32),
        Just(1000u32),
        prop::sample::select(vec![4u32, 8, 16, 32, 64, 128, 512, 4096, 32768]),
        257u32..65_536,
        Just(65_535u32),
    ];
    let key_len = prop::sample::select(vec![16usize, 24, 32]);
    (radix, key_len)
        .prop_flat_map(|(radix, key_len)| {
            let min = FF1::new(&[0u8; 16], radix).expect("valid").min_length();
            let len = min..=min + 40;
            let numeral = 0u16..=u16::try_from(radix - 1).expect("radix < 2**16");
            (
                prop::collection::vec(any::<u8>(), key_len),
                Just(radix),
                len.prop_flat_map(move |n| prop::collection::vec(numeral.clone(), n)),
            )
        })
        .prop_map(|(key, radix, x)| Case { key, radix, x })
}

proptest! {
    #![proptest_config(ProptestConfig::with_cases(64))]

    #[test]
    fn round_trip_preserves_length_and_range(c in case(), tweak in prop::collection::vec(any::<u8>(), 0..16)) {
        let ff1 = FF1::new(&c.key, c.radix).expect("valid");
        let ct = ff1.encrypt_numerals(&c.x, Some(&tweak)).expect("valid");
        prop_assert_eq!(ct.len(), c.x.len());
        prop_assert!(ct.iter().all(|&v| u32::from(v) < c.radix));
        prop_assert_eq!(ff1.decrypt_numerals(&ct, Some(&tweak)).expect("valid"), c.x);
    }

    #[test]
    fn encryption_is_deterministic(c in case()) {
        let ff1 = FF1::new(&c.key, c.radix).expect("valid");
        prop_assert_eq!(
            ff1.encrypt_numerals(&c.x, None).expect("valid"),
            ff1.encrypt_numerals(&c.x, None).expect("valid")
        );
    }

    /// Changing the tweak changes the ciphertext. As in the Python suite,
    /// one tweak is compared against three others and one must differ: the
    /// domain is at least 1,000,000 values, so a genuine collision costs
    /// about one in a million per pair, while an implementation that ignores
    /// the tweak collides every time.
    #[test]
    fn tweak_sensitivity(c in case(), tweaks in prop::collection::hash_set(prop::collection::vec(any::<u8>(), 0..16), 4)) {
        let ff1 = FF1::new(&c.key, c.radix).expect("valid");
        let tweaks: Vec<Vec<u8>> = tweaks.into_iter().collect();
        let baseline = ff1.encrypt_numerals(&c.x, Some(&tweaks[0])).expect("valid");
        let differs = tweaks[1..]
            .iter()
            .any(|t| ff1.encrypt_numerals(&c.x, Some(t)).expect("valid") != baseline);
        prop_assert!(differs, "four distinct tweaks produced identical ciphertext");
    }

    /// A single flipped key bit produces different output: the hardest case
    /// for the key schedule, and a much stronger test than changing every byte.
    #[test]
    fn key_sensitivity(c in case()) {
        let mut flipped = c.key.clone();
        *flipped.last_mut().expect("non-empty key") ^= 0x01;
        let a = FF1::new(&c.key, c.radix).expect("valid").encrypt_numerals(&c.x, None).expect("valid");
        let b = FF1::new(&flipped, c.radix).expect("valid").encrypt_numerals(&c.x, None).expect("valid");
        prop_assert_ne!(a, b);
    }
}

/// Encrypt every value of a small domain and require the image to be the
/// whole domain, each value exactly once.
fn assert_bijective(radix: u32, n: usize) {
    let ff1 = FF1::new(&[0u8; 16], radix).expect("valid");
    let total = u64::from(radix).pow(u32::try_from(n).expect("small"));
    let total = usize::try_from(total).expect("domain fits memory");
    let mut seen = vec![false; total];
    let mut x = vec![0u16; n];
    for value in 0..total {
        // Big-endian digits of `value`.
        let mut rest = value;
        for slot in x.iter_mut().rev() {
            *slot = u16::try_from(rest % radix as usize).expect("digit");
            rest /= radix as usize;
        }
        let ct = ff1.encrypt_numerals(&x, None).expect("valid");
        let index = ct
            .iter()
            .fold(0usize, |acc, &d| acc * radix as usize + usize::from(d));
        assert!(
            !seen[index],
            "radix {radix} n {n}: image value {index} produced twice"
        );
        seen[index] = true;
    }
    assert!(
        seen.iter().all(|&s| s),
        "radix {radix} n {n}: image is not the whole domain"
    );
}

#[test]
#[ignore = "exhaustive: 1,048,576 encryptions; run with cargo test --release -- --ignored"]
fn bijective_on_radix_2_length_20() {
    assert_bijective(2, 20);
}

#[test]
#[ignore = "exhaustive: 1,000,000 encryptions; run with cargo test --release -- --ignored"]
fn bijective_on_radix_10_length_6() {
    assert_bijective(10, 6);
}
