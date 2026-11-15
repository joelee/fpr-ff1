# Backlog

This file tracks high-level feature ideas and technical debt for `fpr-ff1`.

## Active Items

### Ongoing

- Track SP 800-38G Rev. 1. It is still a second public draft; if it is finalised with limits that
  differ from the 2PD, that is a breaking change requiring a major version.
- Test each new CPython release as it ships, and add it to the CI matrix and the classifiers once
  it passes. Raise the `requires-python` floor only as a deliberate decision, when an old version
  leaves upstream support; adding a version never drops one (FF1-29 D3). The upper-bound cap
  policy was retired at 1.0.0 (review 00003 B4): a cap becomes a hard resolution failure on future
  interpreters, so classifiers state the tested versions instead.
- Deferred from the crate's first release (plan 00008 D5, D6): `no_std` support (with `alloc`), and
  key zeroization behind a feature once there is a claim the crate can defend in `SECURITY.md`.

### Candidates

Not planned. Each needs an idea in JoeDocs before planning.

- **Batch API** (Idea 00001, FF1-1). Its real benefit is amortising the Python-to-Rust boundary
  under `backend="rust"`, plus caller convenience; in pure Python the measured ceiling is about
  1.05×. It would be a new public API, in tension with the small-surface rule.
- **Radix 65536** (Idea 00001, FF1-1). Widen the supported domain from `2 <= radix < 2**16` to
  SP 800-38G's inclusive `2**16`. It accepts new inputs, so it is a SemVer minor change.
- **Free-threaded CPython (3.15t)** (FF1-29 D4). Waits on `cryptography`, the only runtime
  dependency, publishing free-threaded 3.15 wheels: 50.0.2 had `cp314t` only on 2026-11-14. Then,
  in order: test the pure-Python path on 3.15t; audit the extension, declare `gil_used = false`
  and add an `abi3t` wheel per platform (PyO3's `abi3t` feature, maturin 1.14 or newer); and
  update the thread-safety docs, because without the GIL the pure-Python backend runs concurrent
  calls in parallel. Free-threaded 3.14 needs version-specific `cp314t` wheels that `abi3t` does
  not cover, and is not proposed. Dropping `cryptography` on free-threaded builds was considered
  and rejected: there is no standard environment marker for it (PEP 780 is still open), per-wheel
  dependency metadata breaks uv and Poetry locks, and free-threaded installs without a native
  wheel could not encrypt.

## Completed Items

- **`2.2.0`: CPython 3.15 support and a dependency refresh** (FF1-29). CPython 3.15 is in the
  quality and installed-wheel CI matrices, and the full conformance run on the installed `abi3`
  wheel uses it; the classifiers and docs state 3.12 to 3.15, with `requires-python` unchanged.
  The native wheels and crate builds carry `pyo3` 0.30.1 and `aes` 0.9.4, and the development lock
  `coverage` 7.17.3 (PyYAML still has no 3.15 wheels and builds from source there). No change to
  accepted inputs, ciphertext or either public API. The release itself is recorded at closeout.
- **`2.1.1` released: the observations left open at `2.1.0`** (plan 00011). `fpr-ff1` 2.1.1 on
  PyPI and crates.io from tag `v2.1.1`, the crate published by Trusted Publishing, with no change to
  accepted inputs, ciphertext or either public API. Trace-hook parity: the Rust
  `TraceRecord` and its binding carry `A_before`/`B_before`, and both suites assert the Algorithm 7
  A/B chaining on every NIST sample (review 00015 LOW-01). The `SECURITY.md` timing row was a
  first-case artifact of the harness (-29.4% measured first, +0.9% measured last in the same run);
  the harness now warms up and times both orders, and the table is re-measured. The crate's
  `cargo-semver-checks` step compares against the last stable release under an explicit release
  type from `.github/scripts/semver_release_type.py`, running 223 checks instead of none. Review
  00015 open question 1 (multi-byte-format `memoryview`) is pinned by a dual-backend test, the guard
  unchanged.
- **`2.1.0` released: the FF1 core as a Rust crate** (plans 00009 and 00010; plan 00008
  superseded). `fpr-ff1` 2.1.0 on PyPI and crates.io from tag `v2.1.0`, the crate published by
  Trusted Publishing. The core is a publishable crate with its own validation, public API,
  conformance suite and CI; `aes` 0.9 and `num-bigint` 0.5; the README is a landing page for both
  languages, with the Python API reference and migration guide in `docs/` and tests that keep the
  registry pages rendering. `2.1.0rc1` and `2.1.0rc2` preceded it on both registries, and review
  00015 approved `v2.0.0..v2.1.0rc2` with no blocking finding.
- **Stable `v2.0.0` released** (plan 00007, from review 00007). Legacy-pickle restoration fixed;
  unencodable tweak lengths and bounds fail closed on both backends; the divide-and-conquer
  conversion ported to the Rust core; the release gate installs and tests all five native wheels
  on their own platforms plus full conformance on the installed abi3 wheel; CI negative-control
  evidence recorded (closing plan 00005 AC-02); the 1.x security-support window decided; the
  `ubiq_security_fpe` migration recipe corrected for the legacy zero-maximum sentinel.
  `2.0.0rc2` was published and soaked from 2026-09-16 to 2026-09-25, and re-reviewed by reviews
  00010 to 00014 with no Critical or Major finding.
- **Divide-and-conquer conversion ported to the Rust core for `2.0.0rc2`** (plan 00007 STEP-04,
  from review 00006 open question 1). The same dispatch as the Python reference, proven equal to
  the retained reference loops across every supported radix, with ciphertext unchanged. Measured
  ~2.8× faster than the pure-Python path at n=20,000 radix 10 and ~11× at radix 256, so the rc1
  crossover no longer exists.
- Review 00007 fixes for `2.0.0rc2` (plan 00007 STEPs 01-03, 06-08): restored 1.x pickles keep
  their backend; unencodable tweak lengths fail closed on both backends; seven more public-contract
  tests run on both backends; every published native wheel is installed and tested on its own
  platform, with full conformance on the installed abi3 wheel; CI negative-control evidence
  (closing plan 00005 AC-02); a decided 1.x security-support window.
- Review 00006 hardening for `2.0.0rc1` (plan 00005): a `rust-conformance` CI job that runs the
  compiled backend's full conformance suite in the release gate, GIL release in the PyO3 bindings,
  a once-per-call AES key schedule, `cargo` Dependabot coverage, a typed pickle key-length
  rejection, `_rs.__version__` from the crate manifest with a two-file version contract test, Rust
  hygiene gates, and a corrected crossover claim.
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
- Reviews 00003 and 00004 pre-1.0 findings resolved for v1.0.0 (plan 00002): minimum-domain
  validation bypass closed, exception messages redacted, instances made thread-safe by
  construction, pickling support, `__version__`, frozen oracle KAT vectors, supply-chain
  hardening (SHA-pinned actions, checksum-verified gitleaks, publish-the-tested-artifact,
  dependabot), wheel-test and sdist-contents CI jobs, coverage gate relocated out of `addopts`,
  benchmark harness, calibrated README language, community files, badges.
- Version policy revised (review 00004 MED-05): expanding the accepted domain without changing
  existing behaviour (e.g. a future radix-65536 addition) is a SemVer **minor** change; newly
  rejecting inputs or changing ciphertext remains major.
- **v1.0.0 published** (2026-09-05, tag `v1.0.0` on `ff97296`): signed annotated tag, release-gated
  Trusted Publishing with provenance attestations, Production/Stable classifier on PyPI. Ciphertext
  unchanged for every input valid in 0.1.1.
- **E1 pure-Python optimisation landed for v1.1.0** (plan 00003, steps 01–05): subquadratic
  divide-and-conquer `NUM`/`STR` conversion plus an O(n) power-of-two fast path, ciphertext
  bit-identical to 1.0.0 across the full conformance suite; naive loops retained as the
  documented reference with a differential equivalence test across every supported radix.
  ~19× at n=20,000 radix 10, ~25× at radix 256; small inputs unchanged.
- **E2 optional accelerated backend landed for v2.0.0rc1** (plan 00003, steps 07–15): an opt-in
  `backend="rust"` PyO3 extension (Algorithm 7 + PRF, pinned RustCrypto AES, validated against
  NIST FIPS 197 KAT and the Python PRF), ~6.8× at 6 numerals / ~3.3× at n=100 (radix 10), with
  the pure-Python path retained as the reference and default. The full conformance suite runs
  bit-exact on both backends including per-round intermediates; abi3-py312 wheels for the
  five-platform matrix with the pure-Python sdist as the universal fallback.

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
