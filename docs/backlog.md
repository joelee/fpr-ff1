# Backlog

This file tracks high-level feature ideas and technical debt for `fpr-ff1`.

## Active Items

### 2.0

- Optional accelerated backend. Opt-in only; the pure-Python implementation stays the reference
  and the default. Blocked on 1.0 shipping first — an accelerated path is only worth having once
  the reference is settled and the conformance suite can prove the two agree bit for bit.

### Ongoing

- Track SP 800-38G Rev. 1. It is still a second public draft; if it is finalised with limits that
  differ from the 2PD, that is a breaking change requiring a major version.
- Raise the `requires-python` floor as new Python versions enter the CI matrix and pass. The
  upper-bound cap policy was retired at 1.0.0 (review 00003 B4): a cap becomes a hard resolution
  failure on future interpreters, so classifiers state the tested versions instead.

## Completed Items

- Initial FF1 implementation.
- NIST sample vector conformance tests (9 vectors, encrypt + decrypt).
- Per-round intermediate value conformance tests for all 9 NIST samples.
- Parameter and input validation tests.
- Exact-arithmetic regression tests and AST scan for float operations.
- Hypothesis property-based tests (round-trip, determinism, key/tweak sensitivity, length/alphabet preservation).
- Small-domain bijectivity tests.
- Project metadata, packaging, and tooling setup.
- Fixed the SP 800-38G step 6.iii S-expansion, which raised rather than encrypting for any input
  reaching `d > 16` (radix 10 from 57 numerals, radix 65535 from 13).
- Differential testing against an independent oracle for radices without NIST vectors
  (2, 16, 32, 62, 256, 65535).
- `ubiq_security_fpe` interoperability test, both directions, all three key sizes.
- 100% line and branch coverage, enforced.
- CI across Python 3.12/3.13/3.14 on Linux, macOS and Windows, with PyPI Trusted Publishing.
- `SECURITY.md`, `CHANGELOG.md`, README FF3 rationale and migration guide.

- CI executed across the full 9-leg matrix (Python 3.12/3.13/3.14 on Linux, macOS and Windows);
  first green release-gate run at v0.1.0.
- Claimed `fpr-ff1` on PyPI, configured Trusted Publishing, and published v0.1.0 (2026-09-03)
  with provenance attestations on both artifacts.

## Decided

- **Migration shim: guide only** (2026-08-21). No `compat` layer ships. The README migration
  section plus bidirectional interoperability tests carry it. A shim would be a permanent
  CamelCase second API mirroring a deprecated library, against the "small surface" rule.
- **v0.1.0 shipped the S-expansion fix** (published 2026-09-03), so no disclosure framing was
  needed; the pre-release fixes folded into the first published release as planned.

## Dropped Items

- **Rust `fpe` crate as a second differential oracle.** The Python oracle is validated against all
  nine NIST vectors before use and agrees byte-exact across every supported radix; a Rust
  toolchain across nine matrix legs is disproportionate cost. Revisit only if
  `ubiq-security-fpe` becomes uninstallable.
- **Rewriting the PRF as a CBC-MAC loop over the cached ECB encryptor.** Measured: 1.34x faster at
  2 blocks, break-even at 3, and 0.58x — slower — at 5, as the Python-level XOR loop overtakes the
  C-level CBC call. Hoisting the `algorithms.AES` and `modes.CBC` value objects was taken instead,
  for a flat ~1.3x with no Python-level crypto.
