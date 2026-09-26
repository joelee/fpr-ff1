#![doc = include_str!("../README.md")]
//!
//! ## Relationship to the Python package
//!
//! Validation matches the `fpr-ff1` Python package rule for rule, in the same
//! order and with the same messages, so an input either both accept or both
//! reject in the same way. [`ErrorKind`] maps one to one onto the Python
//! exception classes.
//!
//! No type from `num-bigint`, `aes` or `cipher` appears in the public API
//! (plan 00009 D10), so their major versions never become this crate's.

// The FF1 core stays private: nothing in it is reachable from outside the
// crate except through the public API below or the `internal` feature.
mod engine;
mod error;
mod ff1;
mod validate;

pub use error::{Error, ErrorKind};
pub use ff1::{Builder, FF1};

#[cfg(test)]
mod tests;
#[cfg(test)]
mod validate_tests;

/// Unvalidated core and test seams for the PyO3 binding and the
/// conformance tests. Not public API; not covered by semver (plan 00009
/// D10). Inputs must already be validated by the caller.
#[cfg(feature = "internal")]
#[doc(hidden)]
pub mod __internal {
    pub use crate::engine::{cipher_block_with_key, ff1, ff1_traced, prf_with_key, TraceRecord};
}
