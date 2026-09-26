//! Input validation (plan 00009 STEP-05).
//!
//! A line-for-line port of the checks in `src/fpr_ff1/_ff1.py`, in the same
//! order and with the same messages, so the Python package and this crate
//! accept and reject exactly the same inputs. The shared case file
//! `tests/vectors/validation_cases.json` holds the two in step (STEP-08).
//!
//! Exact integer arithmetic only, as in both FF1 cores.

use std::collections::HashMap;
use std::collections::HashSet;

use crate::error::{Error, ErrorKind};

/// Smallest supported radix (SP 800-38G, and the supported subset in
/// `AGENTS.md`).
pub(crate) const RADIX_MIN: u32 = 2;
/// The supported radix subset is `2 <= radix < 2**16`: radix 65536 is
/// deliberately excluded, so every numeral fits a `u16`.
pub(crate) const RADIX_MAX_EXCLUSIVE: u32 = 1 << 16;
/// SP 800-38G requires `maxlen < 2**32`; the boundary is excluded.
pub(crate) const MAX_LEN: u64 = (1 << 32) - 1;
/// Algorithm 7 step 5 encodes the tweak length in four bytes (`[t]^4`), so a
/// longer tweak cannot be expressed.
pub(crate) const MAX_TWEAK_LEN: u64 = (1 << 32) - 1;
/// The minimum domain `radix**minlen >= 1_000_000`, from the second public
/// draft of SP 800-38G Rev. 1 (stricter than the 2016 text's 100).
const MIN_DOMAIN: u64 = 1_000_000;

/// Which side of FF1 an input is, for messages ("plaintext length ...").
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub(crate) enum Operand {
    Plaintext,
    Ciphertext,
}

impl Operand {
    fn as_str(self) -> &'static str {
        match self {
            Operand::Plaintext => "plaintext",
            Operand::Ciphertext => "ciphertext",
        }
    }
}

/// The key must be 16, 24 or 32 bytes (AES-128, -192, -256).
pub(crate) fn key(key: &[u8]) -> Result<(), Error> {
    match key.len() {
        16 | 24 | 32 => Ok(()),
        n => Err(Error::new(
            ErrorKind::KeyLength,
            format!("key must be 16, 24, or 32 bytes, got {n}"),
        )),
    }
}

/// `2 <= radix < 2**16`.
pub(crate) fn radix(radix: u32) -> Result<(), Error> {
    if (RADIX_MIN..RADIX_MAX_EXCLUSIVE).contains(&radix) {
        Ok(())
    } else {
        Err(Error::new(
            ErrorKind::Radix,
            format!("radix must satisfy {RADIX_MIN} <= radix < {RADIX_MAX_EXCLUSIVE}, got {radix}"),
        ))
    }
}

/// The smallest `n` with `radix**n >= 1_000_000`, by repeated integer
/// multiplication -- never a logarithm (`_ff1.py::_min_length`).
///
/// The caller has validated `radix`, so it is at least 2 and the loop ends;
/// the running product stays below `1_000_000 * 65_535`, well inside `u64`.
pub(crate) fn min_length(radix: u32) -> usize {
    let radix = u64::from(radix);
    let mut n = 1;
    let mut value = radix;
    while value < MIN_DOMAIN {
        value *= radix;
        n += 1;
    }
    n
}

/// Input length between the minimum domain and `2**32 - 1`.
pub(crate) fn length(
    n: usize,
    min_length: usize,
    radix: u32,
    operand: Operand,
) -> Result<(), Error> {
    let side = operand.as_str();
    if n < min_length {
        return Err(Error::new(
            ErrorKind::Length,
            format!("{side} length {n} below minimum {min_length} for radix {radix}"),
        ));
    }
    if n as u64 > MAX_LEN {
        return Err(Error::new(
            ErrorKind::Length,
            format!("{side} length {n} above maximum {MAX_LEN}"),
        ));
    }
    Ok(())
}

/// Every numeral is less than the radix. The message gives the position,
/// never the value: the value is plaintext data.
pub(crate) fn numerals(x: &[u16], radix: u32, operand: Operand) -> Result<(), Error> {
    match x.iter().position(|&v| u32::from(v) >= radix) {
        None => Ok(()),
        Some(idx) => Err(Error::new(
            ErrorKind::ValueRange,
            format!(
                "{}[{idx}] is out of range for radix {radix}",
                operand.as_str()
            ),
        )),
    }
}

/// Configured tweak-length bounds, checked once at construction: neither may
/// exceed the four-byte encodable maximum (a minimum above it is
/// unsatisfiable; a maximum above it would silently mean the ceiling), and
/// the minimum may not exceed the maximum. Order as in `_validate_tweak_bounds`.
pub(crate) fn tweak_bounds(min: Option<usize>, max: Option<usize>) -> Result<(), Error> {
    if let Some(low) = min {
        if low as u64 > MAX_TWEAK_LEN {
            return Err(Error::new(
                ErrorKind::TweakLength,
                format!(
                    "min_tweak_len {low} above encodable maximum tweak length {MAX_TWEAK_LEN}; \
                     no tweak could satisfy it"
                ),
            ));
        }
    }
    if let Some(high) = max {
        if high as u64 > MAX_TWEAK_LEN {
            return Err(Error::new(
                ErrorKind::TweakLength,
                format!(
                    "max_tweak_len {high} above encodable maximum tweak length {MAX_TWEAK_LEN}; \
                     bounds are rejected, not clamped"
                ),
            ));
        }
    }
    if let (Some(low), Some(high)) = (min, max) {
        if low > high {
            return Err(Error::new(
                ErrorKind::TweakLength,
                format!(
                    "min_tweak_len {low} exceeds max_tweak_len {high}; \
                     no tweak length could satisfy both bounds"
                ),
            ));
        }
    }
    Ok(())
}

/// A tweak's length: the encodable ceiling first, then the configured
/// bounds (`_validate_tweak`). A bound of `Some(0)` is literal: only an empty
/// tweak satisfies `max = Some(0)`.
pub(crate) fn tweak(len: usize, min: Option<usize>, max: Option<usize>) -> Result<(), Error> {
    if len as u64 > MAX_TWEAK_LEN {
        return Err(Error::new(
            ErrorKind::TweakLength,
            format!("tweak length {len} above encodable maximum {MAX_TWEAK_LEN}"),
        ));
    }
    if let Some(low) = min {
        if len < low {
            return Err(Error::new(
                ErrorKind::TweakLength,
                format!("tweak length {len} below minimum {low}"),
            ));
        }
    }
    if let Some(high) = max {
        if len > high {
            return Err(Error::new(
                ErrorKind::TweakLength,
                format!("tweak length {len} above maximum {high}"),
            ));
        }
    }
    Ok(())
}

/// The alphabet has exactly `radix` characters, all distinct. Length and
/// uniqueness are by Unicode scalar value, as Python's are by code point.
pub(crate) fn alphabet(alphabet: &str, radix: u32) -> Result<Vec<char>, Error> {
    let chars: Vec<char> = alphabet.chars().collect();
    if chars.len() as u64 != u64::from(radix) {
        return Err(Error::new(
            ErrorKind::Alphabet,
            format!(
                "alphabet length {} does not match radix {radix}",
                chars.len()
            ),
        ));
    }
    let distinct: HashSet<char> = chars.iter().copied().collect();
    if distinct.len() != chars.len() {
        return Err(Error::new(
            ErrorKind::Alphabet,
            "alphabet contains duplicate characters",
        ));
    }
    Ok(chars)
}

/// Map each character to its numeral, rejecting any character outside the
/// alphabet by position -- never by the character itself, which is plaintext.
pub(crate) fn decode(s: &str, lookup: &HashMap<char, u16>) -> Result<Vec<u16>, Error> {
    s.chars()
        .enumerate()
        .map(|(idx, ch)| {
            lookup.get(&ch).copied().ok_or_else(|| {
                Error::new(
                    ErrorKind::ValueRange,
                    format!("character at index {idx} is not in the alphabet"),
                )
            })
        })
        .collect()
}

/// The string interface needs an alphabet; point the caller at the numeral
/// interface instead (Python raises the base `FF1Error` here).
pub(crate) fn alphabet_required(numeral_method: &str) -> Error {
    Error::new(
        ErrorKind::AlphabetRequired,
        format!(
            "alphabet required for string interface; use {numeral_method} for the numeral interface"
        ),
    )
}
