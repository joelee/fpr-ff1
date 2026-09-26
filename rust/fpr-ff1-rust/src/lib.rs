//! PyO3 binding for the fpr-ff1 FF1 core (plan 00003 E2; split out of the
//! core by plan 00009 STEP-04).
//!
//! The FF1 algorithm lives in the `fpr-ff1` crate. This crate only exposes
//! it to Python as `fpr_ff1._rs`, through the core's `internal` entry points:
//! every input has already passed the Python `FF1` class's validation, so
//! the binding calls the unvalidated core directly and error types and
//! messages stay identical across backends (plan 00003 decision D4).

use fpr_ff1::__internal::{cipher_block_with_key, ff1, ff1_traced, prf_with_key};
use pyo3::exceptions::PyValueError;
use pyo3::prelude::*;

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
