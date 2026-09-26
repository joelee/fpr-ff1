//! The crate's error type (plan 00009 STEP-05).

use core::fmt;

/// What kind of input was rejected.
///
/// One variant per exception class in the `fpr-ff1` Python package, so code
/// ported between the two maps each exception to exactly one kind:
///
/// | Kind | Python exception |
/// |---|---|
/// | [`KeyLength`](ErrorKind::KeyLength) | `KeyLengthError` |
/// | [`Radix`](ErrorKind::Radix) | `RadixError` |
/// | [`Length`](ErrorKind::Length) | `LengthError` |
/// | [`ValueRange`](ErrorKind::ValueRange) | `ValueRangeError` |
/// | [`TweakLength`](ErrorKind::TweakLength) | `TweakLengthError` |
/// | [`Alphabet`](ErrorKind::Alphabet) | `AlphabetError` |
/// | [`AlphabetRequired`](ErrorKind::AlphabetRequired) | `FF1Error` (the base class) |
///
/// Python's `BackendError` has no counterpart: backend selection is a
/// Python-side concern.
#[derive(Debug, Clone, Copy, PartialEq, Eq, Hash)]
#[non_exhaustive]
pub enum ErrorKind {
    /// The key is not 16, 24 or 32 bytes.
    KeyLength,
    /// The radix is outside `2 <= radix < 2**16`.
    Radix,
    /// The input length is below the minimum domain for the radix, or above
    /// `2**32 - 1`.
    Length,
    /// A numeral is not less than the radix, or a character is not in the
    /// alphabet.
    ValueRange,
    /// A tweak or a tweak-length bound is outside the configured bounds or
    /// above the four-byte encodable maximum.
    TweakLength,
    /// The alphabet's length does not equal the radix, or a character repeats.
    Alphabet,
    /// The string interface was used without an alphabet.
    AlphabetRequired,
}

/// A rejected input.
///
/// The message matches the Python package's for the same rejection. It never
/// contains key material, a numeral value or a character from the input:
/// validation errors are routinely logged, and those are secrets or
/// plaintext. It names the offending position or length instead.
#[derive(Debug, Clone, PartialEq, Eq)]
pub struct Error {
    kind: ErrorKind,
    message: String,
}

impl Error {
    pub(crate) fn new(kind: ErrorKind, message: impl Into<String>) -> Self {
        Self {
            kind,
            message: message.into(),
        }
    }

    /// The kind of rejection.
    pub fn kind(&self) -> ErrorKind {
        self.kind
    }
}

impl fmt::Display for Error {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        f.write_str(&self.message)
    }
}

impl core::error::Error for Error {}
