//! NIST SP 800-38G FF1 format-preserving encryption.
//!
//! The FF1 core ported line for line from the pure-Python reference in
//! `src/fpr_ff1/_ff1.py` of the `fpr-ff1` project, which remains the
//! reference implementation. The public API, with its own validation, is
//! added by plan 00009 STEP-05 and STEP-06; until then this crate only
//! carries the core for the PyO3 binding.
//!
//! No type from `num-bigint`, `aes` or `cipher` appears in the public API
//! (plan 00009 D10), so their major versions never become this crate's.

// The core stays private: every item in it is unreachable from outside the
// crate unless re-exported below. The allow lifts once STEP-06's public API
// calls into it; until then only the `internal` feature and the tests do.
#[cfg_attr(not(feature = "internal"), allow(dead_code))]
mod engine;

#[cfg(test)]
mod tests;

/// Unvalidated core and test seams for the PyO3 binding and the
/// conformance tests. Not public API; not covered by semver (plan 00009
/// D10). Inputs must already be validated by the caller.
#[cfg(feature = "internal")]
#[doc(hidden)]
pub mod __internal {
    pub use crate::engine::{cipher_block_with_key, ff1, ff1_traced, prf_with_key, TraceRecord};
}
