---
title: "Code Review 00015: V2_1_0rc2_Release_Review"
aliases:
  - "Review 00015"
tags:
  - code-review
  - software-quality
  - opencode
type: code-review
status: open
review_id: "00015"
reviewed_at: "2026-09-27T23:27:06Z"
reviewer_agent: review
review_model: "ollama-cloud/deepseek-v4-pro"
triggered_by: "user"
review_kind: initial
previous_review: null
repository: "joelee/fpr-ff1"
branch: "release/v2.1"
review_mode: range
pr_reference: null
commit: "6379af82bce8de54ac0ac02c065594e4ace92c1b"
base_ref: "v2.0.0"
base_commit: "0ac0877825eeb8dbe4a08524b579d7e991550354"
head_ref: "v2.1.0rc2"
head_commit: "6379af82bce8de54ac0ac02c065594e4ace92c1b"
scope: "v2.0.0..v2.1.0rc2"
related_plan: null
files_changed: 52
files_reviewed: 38
diff_additions: 6853
diff_deletions: 1258
blocking_issues: 0
issues:
  critical: 0
  major: 0
  medium: 0
  low: 1
  info: 0
  total: 1
categories:
  maintainability: 1
verdict: approve
review_complete: true
web_research_used: false
confidence: high
sources: []
---

# Code Review 00015: V2_1_0rc2_Release_Review

> [!abstract] Verdict: `approve`
> The `v2.0.0..v2.1.0rc2` range — the `fpr-ff1` Rust crate, its validation port, conformance suite, CI/publish automation, and the docs landing-page rework — is a faithful, thoroughly-tested release with no correctness, security, or data-integrity defects found; one non-blocking test-infrastructure inconsistency is recorded.

## Review target

| Field | Value |
|---|---|
| Review mode | Range (tag-to-tag) |
| PR or commit | `v2.0.0..v2.1.0rc2` (52 files, +6853/−1258) |
| Base | `v2.0.0` (`0ac0877`) |
| Head | `v2.1.0rc2` (`6379af8`) |
| Branch | `release/v2.1` (working tree is 3 commits ahead of `origin/release/v2.1`; the review is of the tag range, not the dirty tree) |
| Triggered by | user |
| Related plan | Plans 00009 (crate + v2.1.0) and 00010 (docs landing pages + rc2) |

## Executive summary

This release range delivers the **`fpr-ff1` Rust crate** — the FF1 core split out of the PyO3 binding into a publishable crates.io library with its own public API (`FF1`, `Builder`, `Error`, `ErrorKind`), its own validation layer mirroring the Python rules, and its own conformance suite reading the shared `tests/vectors` fixtures. It also upgrades `aes` 0.8→0.9 and `num-bigint` 0.4→0.5, adds shared validation cases (`validation_cases.json`) run by both suites, and (in rc2) reworks the README into a two-language landing page with a docs-rendering test harness (`tests/test_docs.py`).

The most important risks for a change of this kind are: (1) a divergence between the Rust core and the Python reference that produces plausible-but-wrong ciphertext, and (2) a divergence between the two validation layers that accepts/rejects differently. Both are mitigated unusually well: the Rust core is a line-for-line port with the same spec-step comments and dispatch threshold, verified bit-for-bit by the dual-backend suite, per-round intermediates, FIPS 197 AES KAT, frozen oracle vectors (including `d > 16`), and exhaustive bijectivity sweeps; the validation layers are held in step by a shared case file whose Rust-side `ErrorKind → exception` mapping is an exhaustive `match`. I found no defect in either the core or the validation port.

The one finding is a Low, test-only inconsistency: the Python trace hook records `A_before`/`B_before` fields that the Rust `TraceRecord` omits. No current test depends on them, so nothing fails today, but a future dual-backend test asserting them would pass on Python and raise `KeyError` on Rust.

## Issue summary

| Severity | Count | Merge impact |
|---|---:|---|
| Critical | 0 | Blocks merge/release |
| Major | 0 | Blocks merge/release |
| Medium | 0 | Changes requested |
| Low | 1 | Non-blocking |
| **Total** | **1** | |

## Findings

### Critical

None.

### Major

None.

### Medium

None.

### Low

#### REV-00015-LOW-01 — The two test-only trace hooks record different shapes

- **Location:** `src/fpr_ff1/_ff1.py:942-943` vs `rust/fpr-ff1/src/engine.rs:380-394` and `rust/fpr-ff1-rust/src/lib.rs:117-129`
- **What:** The Python per-round trace hook (`FF1._encrypt_traced`) appends `A_before` and `B_before` (the pre-swap `a`/`b_side` halves) to every record. The Rust `TraceRecord` struct and the `_test_encrypt_traced` binding emit only `i, u, v, b, d, P, Q, R, S, y, m, c, C` — no `A_before`/`B_before`. The `encrypt_traced` fixture in `tests/conftest.py` normalises only the shared fields, so the two backends' traces are not actually the same shape.
- **Why it matters:** No current test reads `A_before`/`B_before` (I grepped `tests/`; only `i/P/Q/R/S/y/m/c/C` and `u/v/b/d` are asserted), so nothing fails today. But the dual-backend conformance contract is "each assertion runs unchanged against both backends". A future test that asserts the pre-swap halves — a natural thing to check when debugging the A/B swap in step 6.viii/6.ix — would pass on the Python backend and raise `KeyError` on the Rust backend, or be silently skipped. This is a latent trap in test infrastructure, not a shipped-product defect.
- **Suggested fix:** Either add `a_before`/`b_before` to `TraceRecord` and populate them in `ff1_impl` (captured at the same point as the Python hook, before the swap), and emit them in `_test_encrypt_traced`; or, if the fields are intentionally dropped, document the divergence at the `encrypt_traced` fixture so a future author does not assume shape parity.

## Open questions

1. **`bytes()` of a non-byte-format `memoryview`.** `_require_bytes` accepts any `memoryview` via `isinstance`, then wraps `bytes(value)` in `except ValueError` (the released-memoryview fix). A `memoryview` over multi-byte data (e.g. `memoryview(array('i', ...))`) is not a released view, so `bytes()` of it raises `TypeError` rather than `ValueError` — outside the `FF1Error` hierarchy. This is pre-existing (not introduced by this change) and not covered by `test_contract.py`'s malformed-call sweep. It is an obscure edge; resolving it would require confirming CPython's actual behaviour for `bytes()` of a multi-byte-format memoryview and, if it does raise `TypeError`, deciding whether to broaden the guard. Not counted as a finding because it is out of the reviewed diff's scope.

2. **`cargo-semver-checks` against a pre-release baseline.** `ci.yml`'s `crate-package` job runs `cargo semver-checks --default-features` once a version is published. For `2.1.0rc2` the baseline is `2.1.0rc1` (a pre-release). I could not verify how `cargo-semver-checks` treats a pre-release baseline (it may compare against the latest *stable* version or skip). The rc2 changelog states the crate code is identical to rc1, so the check should pass either way; the CI run result would resolve this definitively.

## Review coverage

### Files and areas reviewed

- **Python core:** `src/fpr_ff1/_ff1.py` (the only Python source change: the released-`memoryview` guard in `_require_bytes`), `src/fpr_ff1/_exceptions.py`.
- **Rust core:** `rust/fpr-ff1/src/engine.rs` (Algorithm 7 + PRF + numeral conversion), `validate.rs`, `ff1.rs`, `error.rs`, `lib.rs`, and the PyO3 binding `rust/fpr-ff1-rust/src/lib.rs`.
- **Rust tests:** `conformance_tests.rs`, `validation_case_tests.rs`, `test_fixtures.rs`, `property_tests.rs`, `validate_tests.rs`, `tests.rs`, `tests/api.rs`.
- **Python tests:** `test_contract.py`, `test_validation_cases.py`, `test_docs.py`, `test_intermediates.py`, `conftest.py`, `test_thread_safety.py`, and the diffs of `test_validation.py`, `test_properties.py`, `test_interoperability.py`.
- **Fixtures:** `tests/vectors/validation_cases.json` (53 cases, 1 `python_only`), `oracle_kat_frozen.json` (46 vectors), `nist_ff1_intermediates.json` (per-round values).
- **CI/publish:** `.github/workflows/ci.yml`, `.github/workflows/publish.yml`, `.github/scripts/assert_crate_contents.py`.
- **Docs/manifests:** `README.md`, `rust/fpr-ff1/README.md`, `docs/python-api.md`, `docs/migrating-from-ubiq.md`, `CHANGELOG.md`, and the diffs of `AGENTS.md`, `CLAUDE.md`, `SECURITY.md`, `docs/*.md`, `pyproject.toml`, the three `Cargo.toml` files, `justfile`, `benchmarks/timing.py`.

### Checks performed

- Resolved the range: `v2.0.0` (`0ac0877`) is an ancestor of `v2.1.0rc2` (`6379af8`); merge-base is `v2.0.0` itself, so the range is the full release history.
- Line-by-line comparison of the Rust `ff1_impl` against `_ff1.py::_ff1`: `b` from `v`, exact-integer bit length, `pad = (-t-b-1) mod 16`, `P`/`Q` construction, `S`-expansion via `CIPH_K(R XOR [j]^16)`, parity rule identical in both directions, three encrypt/decrypt differences, `A||B` output — all match.
- Verified the numeral-conversion dispatch (`D_C_THRESHOLD = 64`, power-of-two packing, divide-and-conquer) and the `pow2_exponent`/`pow2_chunk_size` helpers against the Python equivalents, including the `k=15` (radix 32768) and `u128` accumulator-width boundaries.
- Verified the validation port (`validate.rs`) against `_ff1.py` rule-for-rule, in the same order, with the same messages (key → radix → bounds → default tweak → alphabet at construction; length → tweak → numerals per call).
- Confirmed the crate's public API leaks no `num-bigint`/`aes`/`cipher`/`pyo3` type (including through the `internal` feature), and that the unvalidated core is reachable only via the non-default `internal` feature.
- Confirmed the `FF1::run` `.expect(...)` is unreachable: every core error condition (empty input, key length, `n`/`t` above `u32::MAX`, `NUM_radix(Q source)` exceeding `b` bytes) is pre-empted by validation, including the `u <= v` argument for the decrypt `Q`-source bound.
- Verified the shared-case counts and the crate README's factual claims (46 frozen vectors; radix-2 inputs up to 193 numerals reaching `d > 16`).
- Checked the publish tag-mapping (`-rcN` → `rcN`) and the crate package allow/forbid lists.

### Checks not performed

- Tests, builds, linters, formatters, scanners, hooks, migrations, and runtime execution were not run by this read-only agent. The Rust code was reviewed statically only; I did not compile it or run `cargo test`/`cargo clippy`/`cargo-semver-checks`.
- The `cargo-semver-checks` pre-release-baseline behaviour (open question 2) could not be confirmed without executing the CI job.

## Positive notes

- **Dual-backend conformance is the product, and it is enforced, not asserted.** The Rust core is verified bit-for-bit against the Python reference through per-round intermediates, the FIPS 197 AES KAT, frozen oracle vectors that reach `d > 16`, and exhaustive bijectivity sweeps — the compensating-bug defence the project's own contract demands.
- **The validation parity is held by an exhaustive `match`.** `validation_case_tests.rs` maps every `ErrorKind` to a Python exception class in a non-exhaustive-`match`-guarded table, so a new kind cannot compile without a shared case — a strong guard against silent drift between the two validation layers.
- **Defence-in-depth in the core.** `encode_len_u32` uses a checked conversion (never a wrapping `as u32`), and `FF1::run` documents and enforces the invariant that a validated input cannot fail the core.
- **Secret/plaintext hygiene carried into Rust.** `FF1`'s `Debug` omits the key; validation messages name positions/lengths, never key material, numeral values, or characters — and `validate_tests.rs` asserts this explicitly.
- **Packaging is pinned and reproducible.** `assert_crate_contents.py` allow/forbid-lists the exact `.crate` contents, the sdist contents are asserted, and `publish.yml` publishes the exact gate-built artifact with a tag/version guard.

## External references

None.

## Recommended next actions

1. (Optional, Low) Reconcile the trace-hook shapes per REV-00015-LOW-01 — add `a_before`/`b_before` to `TraceRecord` and the binding, or document the intentional divergence at the `encrypt_traced` fixture.
2. (Optional) Confirm the two open questions: the `bytes()` behaviour for a multi-byte-format `memoryview`, and the `cargo-semver-checks` result against the `2.1.0rc1` baseline (the CI run resolves this).
3. Proceed to release: no blocking findings.

## Handoff

This is an initial review of the `v2.0.0..v2.1.0rc2` range; there is no prior report to reconcile. The calling agent may proceed with the release process. The single Low finding is test-infrastructure only and does not block merge or release.

## Confidence

**High.** The full diff was inspected and the two risk-critical areas — the Rust FF1 core and the validation port — were read in full and compared line-by-line against the Python reference. The principal uncertainty is that no tests were executed (read-only agent), so compile-time and runtime behaviour of the Rust code rests on static reasoning plus the project's own CI configuration rather than observed results.
