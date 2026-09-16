//! SP 800-38G Algorithm 7 (FF1) — Rust accelerated backend for fpr-ff1.
//!
//! Plan 00003 (idea 00001 r02, Option A): the full Algorithm 7 core plus the
//! Algorithm 6 PRF, ported line-for-line from the pure-Python reference in
//! `src/fpr_ff1/_ff1.py`, which remains the reference implementation and the
//! default backend. Every spec-step comment here mirrors the Python module so
//! a reviewer can compare both against SP 800-38G side by side.
//!
//! Numerals are `u16` throughout: the supported radix range is
//! `2 <= radix < 2**16` (AGENTS.md subset), so every numeral fits 16 bits.
//! The Python boundary converts `int` <-> `u16` after `_prepare` validation.
//!
//! Invariants carried over from the reference (AGENTS.md "Implementation
//! gotchas" — each is a failure mode that produces plausible but wrong
//! output):
//! - `b` is derived from `v`, not `u` (they differ when `n` is odd).
//! - The bit length is `(radix**v - 1).bits()`, never a float logarithm —
//!   the Bouncy Castle bug class. No floating-point arithmetic anywhere.
//! - Padding is `(-t - b - 1) mod 16`.
//! - Encrypt and decrypt differ in exactly three places: `Q` built from `B`
//!   vs `A`; round order 0..9 vs 9..0; final assignment `A,B = B,C` vs
//!   `B,A = A,C`. The parity rule `m = u if i % 2 == 0 else v` is IDENTICAL
//!   in both — do not mirror it.
//! - `S` is truncated to `d` BYTES, not bits.
//! - The PRF is CBC-MAC with a zero IV over 16-byte-aligned input.
//! - No shared mutable state: cipher contexts are created per call, so
//!   instances are thread-safe by construction, mirroring the Python
//!   contract (`_ff1.py` `_Aes` docstring).

use std::collections::HashMap;

use aes::cipher::{BlockEncrypt, KeyInit};
use aes::{Aes128, Aes192, Aes256, Block};
use num_bigint::BigUint;
use num_integer::Integer;
use num_traits::{One, Zero};
use pyo3::exceptions::PyValueError;
use pyo3::prelude::*;

#[cfg(test)]
mod tests;

/// The AES key schedule for 128/192/256-bit keys.
///
/// Immutable once constructed and safe to share across threads: no live
/// cipher context is held, mirroring the `_Aes` contract in `_ff1.py`.
/// Every encryption -- PRF chaining blocks and step 6.iii expansion blocks
/// -- operates on a local buffer, so instances are thread-safe by
/// construction.
enum Aes {
    Aes128(Aes128),
    Aes192(Aes192),
    Aes256(Aes256),
}

impl Aes {
    /// Build the key schedule. Key length is validated Python-side before
    /// the core is called (plan 00003 decision D4); the error arm is
    /// defensive, exercised only through the test-only bindings.
    fn new(key: &[u8]) -> Result<Aes, String> {
        match key.len() {
            16 => Ok(Aes::Aes128(
                Aes128::new_from_slice(key).expect("len checked"),
            )),
            24 => Ok(Aes::Aes192(
                Aes192::new_from_slice(key).expect("len checked"),
            )),
            32 => Ok(Aes::Aes256(
                Aes256::new_from_slice(key).expect("len checked"),
            )),
            n => Err(format!("key must be 16, 24, or 32 bytes, got {n}")),
        }
    }

    /// A single forward cipher block (SP 800-38G forward-cipher-only rule).
    fn encrypt_block(&self, block: &mut Block) {
        match self {
            Aes::Aes128(c) => c.encrypt_block(block),
            Aes::Aes192(c) => c.encrypt_block(block),
            Aes::Aes256(c) => c.encrypt_block(block),
        }
    }
}

/// SP 800-38G Algorithm 6 (PRF): CBC-MAC with a zero IV.
///
/// Invoked from Algorithm 7 step 6.ii as `PRF(P || Q)`. `data` must already
/// be 16-byte aligned (callers guarantee it). A fresh chain per call: CBC
/// chaining state must never persist between PRF calls, or instances would
/// not be thread-safe.
///
/// Validated in STEP-09 against the NIST FIPS 197 Appendix C vectors (via
/// the underlying single-block cipher) and against the Python path's `_prf`
/// output across key sizes and block counts
/// (`tests/test_rust_aes_validation.py`).
///
/// Crate-internal because `Aes` is: `prf_with_key` is the outward form.
///
/// Takes the expanded key schedule rather than the raw key: `ff1_impl`
/// builds it once per call and lends it to all ten rounds. `Aes` is
/// immutable and call-local, so sharing it across the rounds of one call
/// introduces no state that outlives the call and no shared mutability.
pub(crate) fn prf(cipher: &Aes, data: &[u8]) -> Result<Vec<u8>, String> {
    // Zero IV: the chain register starts as all-zero and each block is
    // XORed in before encrypting; the final chain IS the MAC tag.
    //
    // `as_chunks::<16>()` rather than `chunks_exact(16)`: it yields
    // `&[u8; 16]`, so the block width the spec fixes is carried in the type
    // instead of being a runtime argument. Both forms discard a trailing
    // partial block identically -- callers guarantee there is none.
    let mut chain = [0u8; 16];
    for block in data.as_chunks::<16>().0 {
        for (slot, byte) in chain.iter_mut().zip(block) {
            *slot ^= byte;
        }
        let mut b = Block::clone_from_slice(&chain);
        cipher.encrypt_block(&mut b);
        chain.copy_from_slice(&b);
    }
    Ok(chain.to_vec())
}

/// A single forward AES block encryption, `CIPH_K(block)`.
///
/// Used only by the step 6.iii S-expansion. Each expansion block is a
/// SINGLE forward-cipher block over `R XOR [j]^16` — it is NOT a PRF, and
/// `j` is not concatenated onto `R`; both mistakes produce
/// non-16-byte-aligned input and are invisible to the NIST samples, none
/// of which reach `d > 16`. (Numerically a zero-IV CBC-MAC of one block
/// coincides with a raw block encryption, but the distinction is load
/// bearing for review against the spec — see the matching comment in
/// `_ff1.py` and AGENTS.md.)
///
/// Covered by the same NIST FIPS 197 KAT validation as the PRF.
///
/// Takes the expanded key schedule, for the reason given on `prf`.
pub(crate) fn cipher_block(cipher: &Aes, block: &[u8; 16]) -> Result<[u8; 16], String> {
    let mut b = Block::clone_from_slice(block);
    cipher.encrypt_block(&mut b);
    let mut out = [0u8; 16];
    out.copy_from_slice(&b);
    Ok(out)
}

/// `prf` from a raw key, for callers outside the ten-round loop.
///
/// Used only by the test-only `_test_prf` binding and by `tests.rs`; the
/// production path builds the schedule once in `ff1_impl` instead.
pub fn prf_with_key(key: &[u8], data: &[u8]) -> Result<Vec<u8>, String> {
    prf(&Aes::new(key)?, data)
}

/// `cipher_block` from a raw key. Same status as `prf_with_key`.
pub fn cipher_block_with_key(key: &[u8], block: &[u8; 16]) -> Result<[u8; 16], String> {
    cipher_block(&Aes::new(key)?, block)
}

/// Encode a length as the four big-endian bytes SP 800-38G Algorithm 7 step 5
/// uses for `[n]^4` and `[t]^4`. Mirrors `_ff1.py::_encode_uint(value, 4)`,
/// which raises rather than truncating; here a length above `u32::MAX` is an
/// error rather than a wrapped value.
pub fn encode_len_u32(len: usize) -> Result<[u8; 4], String> {
    u32::try_from(len)
        .map(u32::to_be_bytes)
        .map_err(|_| format!("length {len} does not fit the four-byte field of Algorithm 7 step 5"))
}

/// Inputs at or below this many numerals use the naive spec-reference loops
/// directly; above it the conversion takes the power-of-two packing path or
/// the divide-and-conquer split. Mirrors `_ff1.py::_D_C_THRESHOLD` by name
/// and value so both cores dispatch at the same length (plan 00007 D9).
pub const D_C_THRESHOLD: usize = 64;

/// Decode a numeral sequence as a big-endian base-radix integer
/// (SP 800-38G NUM_radix). Exact integer arithmetic only.
///
/// The naive digit-at-a-time loop exactly as the spec writes NUM_radix, and
/// the Rust counterpart of `_ff1.py::_num_radix_reference`. Quadratic in the
/// number of numerals and retained deliberately as the line-by-line
/// reference: `num_radix` is verified equal to it across every supported
/// radix by the equivalence tests in `tests.rs`.
pub fn num_radix_reference(radix: u32, numerals: &[u16]) -> BigUint {
    let mut value = BigUint::zero();
    let base = BigUint::from(radix);
    for &x in numerals {
        value = value * &base + BigUint::from(x);
    }
    value
}

/// Encode a non-negative integer as `length` big-endian base-radix numerals
/// (SP 800-38G STR_radix). Values `>= radix**length` silently drop their
/// high digits, matching the Python reference's truncation contract.
///
/// The Rust counterpart of `_ff1.py::_str_radix_reference`; retained as the
/// reference for the same reason as `num_radix_reference`.
pub fn str_radix_reference(value: &BigUint, radix: u32, length: usize) -> Vec<u16> {
    let mut out = vec![0u16; length];
    let mut v = value.clone();
    let base = BigUint::from(radix);
    for slot in out.iter_mut().rev() {
        // div_rem gives both halves in one division, mirroring the Python
        // reference's divmod and avoiding a second pass over the limbs.
        let (q, r) = v.div_rem(&base);
        // r < radix < 2**16, so it always fits u16 (the supported subset).
        *slot = u16::try_from(r.iter_u32_digits().next().unwrap_or(0))
            .expect("remainder fits u16 for radix < 2**16");
        v = q;
    }
    out
}

/// Return `radix ** exponent` through a call-local memo
/// (`_ff1.py::_radix_power`).
///
/// The cache is created per `num_radix`/`str_radix` invocation and passed
/// down the recursion by `&mut`. It MUST stay call-local: a process-wide or
/// instance-held cache would be shared mutable state and break the
/// thread-safety contract (the GIL is released while this code runs).
fn radix_power(radix: u32, exponent: usize, cache: &mut HashMap<usize, BigUint>) -> &BigUint {
    cache.entry(exponent).or_insert_with(|| {
        BigUint::from(radix).pow(u32::try_from(exponent).expect("exponent < 2**32 (length bound)"))
    })
}

/// Divide-and-conquer NUM_radix above `D_C_THRESHOLD`
/// (`_ff1.py::_num_radix_split`): decode both halves recursively and
/// combine them as `high * radix**len(low) + low` -- one big multiply per
/// level instead of one per digit.
fn num_radix_split(radix: u32, numerals: &[u16], cache: &mut HashMap<usize, BigUint>) -> BigUint {
    let length = numerals.len();
    if length <= D_C_THRESHOLD {
        return num_radix_reference(radix, numerals);
    }
    let high_len = length / 2;
    let high = num_radix_split(radix, &numerals[..high_len], cache);
    let low = num_radix_split(radix, &numerals[high_len..], cache);
    high * radix_power(radix, length - high_len, cache) + low
}

/// Return `k` when `radix` is `2**k`, else `None` (`_ff1.py::_pow2_exponent`).
///
/// Exact integer arithmetic: `2**k - 1` has bit length `k` -- never a
/// logarithm.
fn pow2_exponent(radix: u32) -> Option<u32> {
    if radix & (radix - 1) == 0 {
        Some(u32::BITS - (radix - 1).leading_zeros())
    } else {
        None
    }
}

/// Smallest numeral count per byte-aligned group for radix `2**k`
/// (`_ff1.py::_pow2_chunk_size`). `k` is at most 15, so 8 always works.
fn pow2_chunk_size(k: u32) -> usize {
    for candidate in [1usize, 2, 4] {
        if (k as usize * candidate).is_multiple_of(8) {
            return candidate;
        }
    }
    8
}

/// O(n) NUM_radix for power-of-two radices (`_ff1.py::_num_radix_pow2`):
/// pack byte-aligned groups of numerals and decode the whole sequence with
/// one `from_bytes_be`. Leading zero padding never changes the value.
fn num_radix_pow2(k: u32, numerals: &[u16]) -> BigUint {
    let chunk_size = pow2_chunk_size(k);
    // At most 15 * 8 = 120 bits per group, so a u128 accumulator suffices.
    let bytes_per_chunk = k as usize * chunk_size / 8;
    let pad = (chunk_size - numerals.len() % chunk_size) % chunk_size;
    let padded: Vec<u16> = std::iter::repeat_n(0u16, pad)
        .chain(numerals.iter().copied())
        .collect();
    let mut packed = Vec::with_capacity(padded.len() / chunk_size * bytes_per_chunk);
    for group in padded.chunks(chunk_size) {
        let mut acc: u128 = 0;
        for &numeral in group {
            acc = (acc << k) | u128::from(numeral);
        }
        packed.extend_from_slice(&acc.to_be_bytes()[16 - bytes_per_chunk..]);
    }
    BigUint::from_bytes_be(&packed)
}

/// O(n) STR_radix for power-of-two radices (`_ff1.py::_str_radix_pow2`).
///
/// Values `>= radix**length` drop their high digits exactly as the
/// reference loop does: `radix**length` is `2**(k*length)` here, so one
/// mask reproduces the truncation contract bit for bit.
fn str_radix_pow2(value: &BigUint, k: u32, length: usize) -> Vec<u16> {
    let chunk_size = pow2_chunk_size(k);
    let bytes_per_chunk = k as usize * chunk_size / 8;
    let n_chunks = length.div_ceil(chunk_size);
    let total_bytes = n_chunks * bytes_per_chunk;
    let mask = (BigUint::one() << (k as usize * length)) - BigUint::one();
    let masked = (value & mask).to_bytes_be();
    // `to_bytes_be` is minimal (and `[0]` for zero); left-pad to the full
    // width. The mask guarantees the value fits `total_bytes`.
    let mut data = vec![0u8; total_bytes];
    if masked != [0] {
        data[total_bytes - masked.len()..].copy_from_slice(&masked);
    }
    let digit_mask: u128 = (1u128 << k) - 1;
    let mut out: Vec<u16> = Vec::with_capacity(n_chunks * chunk_size);
    for group in data.chunks(bytes_per_chunk) {
        let mut buf = [0u8; 16];
        buf[16 - bytes_per_chunk..].copy_from_slice(group);
        let chunk_int = u128::from_be_bytes(buf);
        for index in (0..chunk_size).rev() {
            // Each digit is at most k <= 15 bits, so it fits u16.
            out.push(((chunk_int >> (index * k as usize)) & digit_mask) as u16);
        }
    }
    // Drop the leading zero padding introduced by the final partial group.
    out.drain(..n_chunks * chunk_size - length);
    out
}

/// Decode a numeral sequence as a big-endian base-radix integer
/// (SP 800-38G NUM_radix), equal to `num_radix_reference`.
///
/// Same dispatch, in the same order, as `_ff1.py::_num_radix`: at or below
/// `D_C_THRESHOLD` the reference loop; above it, power-of-two radices take
/// the O(n) packing path and every other radix the divide-and-conquer split.
pub fn num_radix(radix: u32, numerals: &[u16]) -> BigUint {
    if numerals.len() <= D_C_THRESHOLD {
        return num_radix_reference(radix, numerals);
    }
    if let Some(k) = pow2_exponent(radix) {
        return num_radix_pow2(k, numerals);
    }
    // Call-local cache; see `radix_power` for why it must not be shared.
    num_radix_split(radix, numerals, &mut HashMap::new())
}

/// Divide-and-conquer STR_radix above `D_C_THRESHOLD`
/// (`_ff1.py::_str_radix_split`): split `value` against
/// `radix**len(low_half)` and encode both halves recursively. A value
/// `>= radix**length` drops its high digits through the recursion exactly
/// as the reference loop does.
fn str_radix_split(
    value: &BigUint,
    radix: u32,
    length: usize,
    cache: &mut HashMap<usize, BigUint>,
) -> Vec<u16> {
    if length <= D_C_THRESHOLD {
        return str_radix_reference(value, radix, length);
    }
    let high_len = length / 2;
    let (high, low) = value.div_rem(radix_power(radix, length - high_len, cache));
    let mut out = str_radix_split(&high, radix, high_len, cache);
    out.extend(str_radix_split(&low, radix, length - high_len, cache));
    out
}

/// Encode a non-negative integer as `length` big-endian base-radix numerals
/// (SP 800-38G STR_radix), equal to `str_radix_reference` including its
/// truncation contract. Dispatch mirrors `num_radix` and `_ff1.py::_str_radix`.
pub fn str_radix(value: &BigUint, radix: u32, length: usize) -> Vec<u16> {
    if length <= D_C_THRESHOLD {
        return str_radix_reference(value, radix, length);
    }
    if let Some(k) = pow2_exponent(radix) {
        return str_radix_pow2(value, k, length);
    }
    // Call-local cache; see `radix_power` for why it must not be shared.
    str_radix_split(value, radix, length, &mut HashMap::new())
}

/// One round's intermediate values, mirroring the Python reference's
/// ``TraceRecord`` (see ``FF1._encrypt_traced``). Test-only; consumed by
/// the STEP-11 dual-backend conformance suite through the
/// ``_test_encrypt_traced`` binding.
///
/// ``y`` and ``c`` travel as big-endian byte strings (arbitrary-precision
/// integers have no direct pyo3 mapping); the Python-side bridge
/// normalizes them to ``int`` so both backends' traces share one shape.
pub struct TraceRecord {
    pub i: u8,
    pub u: usize,
    pub v: usize,
    pub b: usize,
    pub d: usize,
    pub p: Vec<u8>,
    pub q: Vec<u8>,
    pub r: Vec<u8>,
    pub s: Vec<u8>,
    pub y: Vec<u8>,
    pub m: usize,
    pub c: Vec<u8>,
    pub c_block: Vec<u16>,
}

/// SP 800-38G Algorithm 7 core (encrypt when `encrypt`, decrypt otherwise).
///
/// Mirrors `_ff1.py::_ff1` step for step, including its optional trace
/// collector: one code path serves both the production entry points and
/// the test-only traced entry point, so the traced and untraced cores can
/// never drift apart. Inputs are pre-validated on the Python side
/// (`_prepare` runs in Python for both backends — plan 00003 decision D4).
pub fn ff1(
    key: &[u8],
    radix: u32,
    x: &[u16],
    tweak: &[u8],
    encrypt: bool,
) -> Result<Vec<u16>, String> {
    ff1_impl(key, radix, x, tweak, encrypt, None)
}

/// The traced core: same loop, recording each round (test-only, STEP-11).
pub fn ff1_traced(
    key: &[u8],
    radix: u32,
    x: &[u16],
    tweak: &[u8],
) -> Result<(Vec<u16>, Vec<TraceRecord>), String> {
    let mut trace: Vec<TraceRecord> = Vec::with_capacity(10);
    let out = ff1_impl(key, radix, x, tweak, true, Some(&mut trace))?;
    Ok((out, trace))
}

fn ff1_impl(
    key: &[u8],
    radix: u32,
    x: &[u16],
    tweak: &[u8],
    encrypt: bool,
    mut trace: Option<&mut Vec<TraceRecord>>,
) -> Result<Vec<u16>, String> {
    let n = x.len();
    if n == 0 {
        return Err("empty input".to_string());
    }

    // The AES key schedule is built ONCE per call and lent to every round
    // (review 00006 LOW-03): the previous code rebuilt it inside each of
    // the ten `prf` calls and once more per S-expansion block. It is
    // immutable and call-local -- never cached on an instance -- so the
    // thread-safety argument is unchanged.
    let cipher = Aes::new(key)?;

    // Step 1: u = floor(n/2), v = n - u
    let u = n / 2;
    let v = n - u;

    // Step 2: A = X[1..u], B = X[u+1..n]
    let mut a: Vec<u16> = x[..u].to_vec();
    let mut b_side: Vec<u16> = x[u..].to_vec();

    // Step 3: b = ceil(ceil(v * log2(radix)) / 8) -- derived from v, not u.
    // Exact integer arithmetic: the bit length of radix**v - 1, never a
    // float logarithm (the Bouncy Castle bug class).
    let radix_big = BigUint::from(radix);
    // Kept as `(bits + 7) / 8` rather than `bits.div_ceil(8)` to match
    // SP 800-38G Algorithm 7 step 3 / `_ff1.py` line for line (decision D5).
    #[allow(clippy::manual_div_ceil)]
    let b: usize = (((radix_big.pow(v as u32) - BigUint::one()).bits() + 7) / 8)
        .try_into()
        .expect("b fits usize");

    // Step 4: d = 4 * ceil(b/4) + 4
    // Kept as `(b + 3) / 4` rather than `b.div_ceil(4)` to match SP 800-38G
    // Algorithm 7 step 4 / `_ff1.py` line for line (decision D5).
    #[allow(clippy::manual_div_ceil)]
    let d: usize = 4 * ((b + 3) / 4) + 4;

    let t = tweak.len();
    // Python: pad = (-t - b - 1) % 16, which is the negation mod 16 — NOT
    // (t + b + 1) mod 16. rem_euclid on the negated sum reproduces Python's
    // always-non-negative % exactly.
    let pad = (-(t as isize) - b as isize - 1).rem_euclid(16) as usize;

    // Step 5: P is loop-invariant, built once.
    // P = [1] || [2] || [1] || [radix]^3 || [10] || [u mod 256] || [n]^4 || [t]^4
    let mut p_block = Vec::with_capacity(16);
    p_block.extend_from_slice(&[1u8, 2, 1]);
    // radix < 2**16 fits three big-endian bytes exactly.
    p_block.push((radix >> 16) as u8);
    p_block.push((radix >> 8) as u8);
    p_block.push(radix as u8);
    p_block.push(10);
    p_block.push((u % 256) as u8);
    // Checked, never `as u32`: a cast would silently wrap a length of 2**32
    // to 0 (review 00007 MED-01). Python validation rejects both lengths
    // first; this keeps the core fail-closed on its own.
    p_block.extend_from_slice(&encode_len_u32(n)?);
    p_block.extend_from_slice(&encode_len_u32(t)?);

    // Loop-invariant moduli, hoisted out of the ten rounds (review 00003
    // M10): step 6.vi reduces modulo radix**m, and m only takes u and v.
    let radix_u = radix_big.pow(u as u32);
    let radix_v = radix_big.pow(v as u32);

    let rounds: Box<dyn Iterator<Item = u8>> = if encrypt {
        Box::new(0..10)
    } else {
        Box::new((0..10).rev())
    };

    for i in rounds {
        // Step 6.i: Q = T || [0]^pad || [i]^1 || [NUM_radix(B)]^b
        // (decrypt builds Q from A instead of B)
        let q_source: &[u16] = if encrypt { &b_side } else { &a };
        let q_num = num_radix(radix, q_source);
        let q_bytes = q_num.to_bytes_be();
        if q_bytes.len() > b {
            return Err("NUM_radix(Q source) does not fit in b bytes".to_string());
        }
        let mut q_block = Vec::with_capacity(t + pad + 1 + b);
        q_block.extend_from_slice(tweak);
        q_block.extend(std::iter::repeat_n(0u8, pad));
        q_block.push(i);
        q_block.extend(std::iter::repeat_n(0u8, b - q_bytes.len()));
        q_block.extend_from_slice(&q_bytes);

        // Step 6.ii: R = PRF(P || Q)
        let mut prf_input = p_block.clone();
        prf_input.extend_from_slice(&q_block);
        let r_block = prf(&cipher, &prf_input)?;

        // Step 6.iii: S is the first d bytes of
        //   R || CIPH_K(R XOR [1]^16) || CIPH_K(R XOR [2]^16) || ...
        // Each expansion block is a SINGLE forward-cipher block over R XOR
        // the 16-byte encoding of j — not a PRF, and j is not concatenated
        // onto R. Both mistakes produce non-16-byte-aligned input and are
        // invisible to the NIST samples, none of which reach d > 16.
        let mut s_block = r_block.clone();
        if s_block.len() < d {
            let mut j: u128 = 1;
            while s_block.len() < d {
                let j_be = j.to_be_bytes();
                let xored: [u8; 16] = std::array::from_fn(|idx| r_block[idx] ^ j_be[idx]);
                s_block.extend_from_slice(&cipher_block(&cipher, &xored)?);
                j += 1;
            }
        }
        // Truncate to d BYTES, not d bits.
        s_block.truncate(d);

        // Step 6.iv: y = NUM(S)
        let y = BigUint::from_bytes_be(&s_block);

        // Step 6.v: parity rule is identical for encrypt and decrypt
        let m_is_u = i % 2 == 0;

        // Step 6.vi: c = (NUM_radix(A) + y) mod radix**m
        // (decrypt subtracts y from NUM_radix(B) instead)
        let modulus = if m_is_u { &radix_u } else { &radix_v };
        let c = if encrypt {
            (num_radix(radix, &a) + &y) % modulus
        } else {
            // (NUM_radix(B) - y) mod radix**m, computed without going
            // negative: add modulus before reducing.
            (num_radix(radix, &b_side) + modulus - (&y % modulus)) % modulus
        };

        // Step 6.vii: C = STR^m_radix(c)
        let m = if m_is_u { u } else { v };
        let c_block = str_radix(&c, radix, m);

        if let Some(trace) = trace.as_deref_mut() {
            // Same position as the Python hook: after C is built, before
            // the A/B swap, so the pre-swap a/b_side are captured here.
            trace.push(TraceRecord {
                i,
                u,
                v,
                b,
                d,
                p: p_block.clone(),
                q: q_block.clone(),
                r: r_block.clone(),
                s: s_block.clone(),
                y: y.to_bytes_be(),
                m,
                c: c.to_bytes_be(),
                c_block: c_block.clone(),
            });
        }

        // Steps 6.viii and 6.ix: A = B, B = C (decrypt assigns B = A, A = C)
        if encrypt {
            a = b_side;
            b_side = c_block;
        } else {
            b_side = a;
            a = c_block;
        }
    }

    // Step 7: return A || B
    let mut out = a;
    out.extend_from_slice(&b_side);
    Ok(out)
}

/// Python-facing module. The public surface is intentionally minimal: the
/// FF1 class in Python constructs the backend and calls `ff1` after
/// `_prepare` validation (plan 00003 decision D4). The test-only trace
/// bridge (STEP-11) extends this module; nothing here is exported from the
/// `fpr_ff1` package's public API.
///
/// The module name is `fpr_ff1._rs` (the extension lives inside the
/// package namespace, the standard maturin mixed layout): the wheel ships
/// `fpr_ff1/**` plus `fpr_ff1/_rs.<abi3>.so`, while the pure wheel and
/// sdist simply lack the `_rs` module -- the package imports fine without
/// it and `backend="rust"` raises a clear `BackendError` (REQ-19).
#[pymodule]
fn _rs(m: &Bound<'_, PyModule>) -> PyResult<()> {
    // From the crate manifest, which is held in lock-step with
    // pyproject.toml (see Cargo.toml). A hard-coded literal here was
    // unrelated to anything shipped and untested, so nothing noticed it
    // was wrong (review 00006 LOW-06).
    m.add("__version__", env!("CARGO_PKG_VERSION"))?;

    /// Encrypt a numeral sequence (values validated Python-side).
    ///
    /// The ten-round computation runs inside `Python::detach`, so the
    /// calling thread releases the GIL for its duration (review 00006
    /// MED-01). Without it the whole computation was a GIL-held block:
    /// concurrent calls serialised, and a long input (n = 20,000 is ~125
    /// ms) stalled every other thread in the process for that whole time.
    /// The closure captures only owned `Vec`s and a `u32` -- no Python
    /// object crosses the boundary -- so it satisfies pyo3's `Ungil` bound
    /// without `unsafe`.
    #[pyfunction]
    fn encrypt_numerals(
        py: Python<'_>,
        key: Vec<u8>,
        radix: u32,
        x: Vec<u16>,
        tweak: Vec<u8>,
    ) -> PyResult<Vec<u16>> {
        py.detach(|| ff1(&key, radix, &x, &tweak, true))
            .map_err(PyValueError::new_err)
    }

    /// Decrypt a numeral sequence (values validated Python-side).
    ///
    /// Releases the GIL for the computation, exactly as `encrypt_numerals`
    /// does; see its comment.
    #[pyfunction]
    fn decrypt_numerals(
        py: Python<'_>,
        key: Vec<u8>,
        radix: u32,
        x: Vec<u16>,
        tweak: Vec<u8>,
    ) -> PyResult<Vec<u16>> {
        py.detach(|| ff1(&key, radix, &x, &tweak, false))
            .map_err(PyValueError::new_err)
    }

    m.add_function(wrap_pyfunction!(encrypt_numerals, m)?)?;
    m.add_function(wrap_pyfunction!(decrypt_numerals, m)?)?;

    /// Test-only: the Algorithm 6 PRF, exposed for the STEP-09 validation
    /// suite (NIST FIPS 197 KAT + PRF equality with the Python path,
    /// `tests/test_rust_aes_validation.py`). Deliberately kept off the
    /// `fpr_ff1` public API, mirroring `_encrypt_traced`'s status.
    #[pyfunction]
    fn _test_prf(key: Vec<u8>, data: Vec<u8>) -> PyResult<Vec<u8>> {
        prf_with_key(&key, &data).map_err(PyValueError::new_err)
    }

    /// Test-only: the raw single-block forward cipher, exposed for the
    /// FIPS 197 Appendix C known-answer tests. Same status as `_test_prf`.
    #[pyfunction]
    fn _test_cipher_block(key: Vec<u8>, block: Vec<u8>) -> PyResult<Vec<u8>> {
        let arr: [u8; 16] = block
            .try_into()
            .map_err(|_| PyValueError::new_err("block must be exactly 16 bytes"))?;
        cipher_block_with_key(&key, &arr)
            .map(|out| out.to_vec())
            .map_err(PyValueError::new_err)
    }

    m.add_function(wrap_pyfunction!(_test_prf, m)?)?;
    m.add_function(wrap_pyfunction!(_test_cipher_block, m)?)?;

    /// Test-only: the traced encrypt, mirroring ``FF1._encrypt_traced``
    /// (plan 00003 STEP-11, REQ-16). Returns ``(ciphertext, trace)`` where
    /// each trace record is a dict with the same keys as the Python hook;
    /// ``y`` and ``c`` are big-endian byte strings that the Python-side
    /// bridge normalizes to ``int``. Never exported from the ``fpr_ff1``
    /// public API.
    #[pyfunction]
    fn _test_encrypt_traced(
        key: Vec<u8>,
        radix: u32,
        x: Vec<u16>,
        tweak: Vec<u8>,
        py: Python<'_>,
    ) -> PyResult<(Vec<u16>, Vec<pyo3::Py<pyo3::types::PyDict>>)> {
        let (out, trace) = ff1_traced(&key, radix, &x, &tweak).map_err(PyValueError::new_err)?;
        let records = trace
            .into_iter()
            .map(|rec| {
                let dict = pyo3::types::PyDict::new(py);
                dict.set_item("i", rec.i)?;
                dict.set_item("u", rec.u)?;
                dict.set_item("v", rec.v)?;
                dict.set_item("b", rec.b)?;
                dict.set_item("d", rec.d)?;
                dict.set_item("P", rec.p)?;
                dict.set_item("Q", rec.q)?;
                dict.set_item("R", rec.r)?;
                dict.set_item("S", rec.s)?;
                dict.set_item("y", rec.y)?;
                dict.set_item("m", rec.m)?;
                dict.set_item("c", rec.c)?;
                dict.set_item("C", rec.c_block)?;
                Ok(dict.unbind())
            })
            .collect::<PyResult<Vec<pyo3::Py<pyo3::types::PyDict>>>>()?;
        Ok((out, records))
    }

    m.add_function(wrap_pyfunction!(_test_encrypt_traced, m)?)?;
    Ok(())
}
