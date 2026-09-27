---
title: "Delivery Plan 00009: Crate And v2.1.0 Release"
aliases:
  - "Plan 00009"
tags:
  - delivery-plan
  - implementation
  - claude-code
  - rust
  - packaging
  - release
type: delivery-plan
plan_id: "PLAN-00009"
plan_status: approved
plan_kind: superseding
created_at: "2026-09-25T19:14:08Z"
approved_at: "2026-09-26T16:25:46Z"
planner_agent: claude-code
planner_model: "anthropic/claude-opus-5-5"
triggered_by: user
request_kind: direct
repository: "joelee/fpr-ff1"
baseline_branch: "chore/plan-00007-closeout"
baseline_commit: "e322cf5d2d77f7e10205bb8a5340333fc07b4186"
source_ideas: []
source_reviews:
  - "docs/reviews/00011-Release_V2_Rc2_Code_Review.md"
  - "docs/reviews/00013-Release_V2_Comprehensive_Re_Review.md"
  - "docs/reviews/00014-V2_Release_Readiness_Re_Review.md"
previous_plan: "docs/plans/00008-Publish_Rust_Crate_To_Crates_io.md"
requirements_count: 14
steps_count: 17
acceptance_criteria_count: 17
blocking_decisions: 0
build_ready: true
web_research_used: true
confidence: medium

# Builder-maintained front matter. Builder may update only these keys after
# explicit user approval; Delivery Planner initializes them.
implementation_status: blocked
builder_agent: claude-code
builder_model: "anthropic/claude-opus-5-5"
execution_branch: "release/v2.1"
execution_started_at: "2026-09-26T16:28:45Z"
execution_updated_at: "2026-09-27T00:12:23Z"
execution_completed_at: null
current_step: "PLAN-00009-STEP-14"
---

# Delivery Plan 00009: Crate And v2.1.0 Release

> [!abstract] Plan status: `approved`
> Publish the Rust core as the `fpr-ff1` crate on crates.io, in version lock-step with a `2.1.0` release on PyPI, after first taking the held `aes` and `num-bigint` upgrades as separately gated changes. Supersedes approved plan 00008 to correct its MSRV, keep third-party types out of the crate's public API, bootstrap the first crates.io publication correctly, and fix the three deferred findings from review 00011. No decision is open; approved by the user on 2026-09-26 and Builder-ready.

## 1. Objective and outcome

Plan 00008 (approved 2026-09-22, never started) set out to publish the Rust core as a crate. Before its start gate cleared, four problems surfaced that each change a frozen decision or requirement, so the contract requires a superseding plan rather than an edit:

| Problem | Source | Correction in this plan |
|---|---|---|
| Plan 00008 D8 declares MSRV 1.87, but the core calls `slice::as_chunks` (stable 1.88) at `rust/fpr-ff1-rust/src/lib.rs:112` | Review 00013 `REV-00013-MED-01`, re-confirmed by review 00014 | MSRV raised; see the next row for the final value |
| `aes` 0.9.3, which the held Dependabot PR #7 brings in, declares `rust-version = 1.89`; the reviews did not see this because the upgrade was not yet applied | crates.io metadata, verified 2026-09-25 (§19) | MSRV is **1.89**, the higher of the code's 1.88 and the dependency's 1.89 (D8) |
| The core's `num_radix`, `str_radix` and their reference variants are `pub` and take or return `num_bigint::BigUint`. Moved as-is into a published crate, every future `num-bigint` major becomes a breaking change for crate users | Repository: `rust/fpr-ff1-rust/src/lib.rs:182,197,326,361` | No third-party type in the public API; internals behind a hidden, non-default feature (D10) |
| crates.io Trusted Publishing cannot create a crate: the first publication of a new crate must use a maintainer-held API token. Plan 00008 REQ-09 assumed every publication could go through OIDC | crates.io documentation (§19) | The user's requested crate pre-release becomes the manual bootstrap publication; Trusted Publishing is configured afterwards and used for `2.1.0` (D11) |

Also folded in, because they belong in the same release: the held Dependabot PR #7 is taken as two separately gated upgrades before the crate's first publication (D12), and review 00011's three deferred Low findings are fixed (D13).

Outcome: `fpr-ff1` `2.1.0` on crates.io and PyPI, published from the same tagged commit on `main`, preceded by a soaked and re-reviewed `2.1.0rc1` on both registries. The Python package's accepted inputs and ciphertext are unchanged; the compiled wheels carry the upgraded `aes` and `num-bigint`, proven bit-exact.

## 2. Source traceability

| Requirement | Source | Source location | Interpretation |
|---|---|---|---|
| PLAN-00009-REQ-01 | Dependabot PR #7; user | PR #7 diff; user decision 2026-09-25 to hold it until after `v2.0.0` | Take `aes` 0.9 with `cipher` 0.5 and `crypto-common` 0.2 as its own gated change |
| PLAN-00009-REQ-02 | Dependabot PR #7; plan 00007 STEP-05 | PR #7 diff; `rust/fpr-ff1-rust/src/lib.rs` conversion | Take `num-bigint` 0.5 as its own gated change, with a benchmark under a park rule |
| PLAN-00009-REQ-03 | Review 00011 | `REV-00011-LOW-01`, `LOW-02`, `LOW-03` | Fix the three deferred Lows |
| PLAN-00009-REQ-04 | Plan 00008 REQ-01; repository | `rust/fpr-ff1-rust/Cargo.toml`; public items at `lib.rs:149-414` | Split into a publishable core and a PyO3 binding; no third-party type in the public API |
| PLAN-00009-REQ-05 | Plan 00008 REQ-02 | `src/fpr_ff1/_ff1.py` validation; `src/fpr_ff1/_exceptions.py` | Port every validation rule into the crate with typed errors |
| PLAN-00009-REQ-06 | Plan 00008 REQ-03 | `AGENTS.md` §Public API | A documented Rust API: construction, numeral primitive, string interface, length accessors |
| PLAN-00009-REQ-07 | Plan 00008 REQ-04 | `AGENTS.md` §Tests; `tests/vectors/*.json` | The crate's own conformance evidence from the shared vectors |
| PLAN-00009-REQ-08 | Plan 00008 REQ-05 | `AGENTS.md` "a change to one core is a change to both" | A shared case file proves the two validation layers agree |
| PLAN-00009-REQ-09 | Plan 00008 REQ-06; user D1 | `tests/test_contract.py` | Lock-step across `pyproject.toml` and both crate manifests |
| PLAN-00009-REQ-10 | Plan 00008 REQ-07; reviews 00013, 00014 | crates.io packaging rules; `REV-00013-MED-01` | Correct packaging, metadata and `rust-version = "1.89"` |
| PLAN-00009-REQ-11 | Plan 00008 REQ-08 | `.github/workflows/ci.yml` | Crate tests, lint, MSRV leg, docs, packaging and API-compatibility checks in the gate |
| PLAN-00009-REQ-12 | Plan 00008 REQ-09; crates.io documentation; user | §19; plan 00008 work log (pre-release instruction, 2026-09-22) | Bootstrap the crate manually with a scoped token at `2.1.0-rc1`, then publish `2.1.0` by Trusted Publishing |
| PLAN-00009-REQ-13 | Plan 00008 REQ-10 | `docs/AGENTS.md` | Every maintained document updated |
| PLAN-00009-REQ-14 | Plan 00008 REQ-11; plan 00007; user memory rule | `SECURITY.md`; `release-tags-on-main-via-pr` convention | Release `2.1.0rc1` then `2.1.0` through a PR merge commit on `main`, verified on both registries |

## 3. Repository baseline

| Field | Value |
|---|---|
| Repository | joelee/fpr-ff1 |
| Branch | chore/plan-00007-closeout |
| HEAD | e322cf5d2d77f7e10205bb8a5340333fc07b4186 |
| Working tree at publication | Clean (the strict gate returned only the empty file allocated for this plan) |
| Applicable instructions | `AGENTS.md`, `CLAUDE.md`, `docs/AGENTS.md`, `docs/plans/AGENTS.md`, `docs/reviews/AGENTS.md` |

`v2.0.0` is published on PyPI from tag `v2.0.0` at `0ac0877` on `main` (plan 00007, completed 2026-09-25). The baseline branch holds only plan 00007's closing work-log commits on top of `main`; its code is identical to `v2.0.0`. Open at baseline: Dependabot PRs #7 (`aes` and `num-bigint` majors, conflicting, checks from the pre-plan-00007 gate), #10 (actions) and #11 (Python dev tools), all held by user decision until after `v2.0.0`. `rust-toolchain.toml` pins the `stable` channel; CI builds with rustc 1.98.1.

## 4. Scope

### In scope

- `aes` 0.9 (with `cipher` 0.5, `crypto-common` 0.2) and `num-bigint` 0.5, each as a separate gated change; Dependabot PR #7 closed in their favour.
- The three Low findings from review 00011.
- Everything plan 00008 scoped: workspace split, validation port, public API, conformance suite, cross-language case file, lock-step, packaging, CI, documentation, publication and verification, with the corrections in §1.
- Release `2.1.0rc1` on PyPI and crates.io, owner soak, independent re-review, then `2.1.0` on both.

### Out of scope

- Any change to the Python package's accepted inputs, ciphertext, public API or default backend. The one exception-type change (REQ-03, a released `memoryview` now raising the documented `FF1Error` subclass instead of `ValueError`) narrows an already-rejected input to the documented contract.
- FF3/FF3-1, key management and every other permanent exclusion in `AGENTS.md`.
- `no_std`, key zeroization, constant-time claims and a `serde` feature (plan 00008 D5, D6 carried).
- Publishing the PyO3 binding crate.
- Widening the per-platform wheel test subset (plan 00007 deviation; not requested).
- Merging Dependabot PRs #10 and #11: owner housekeeping before this plan starts (§16).

## 5. Constraints and preserved decisions

- **The two cores stay in step**, proven by the dual-backend suite at every checkpoint; the validation layers are held in step by the case file (REQ-08).
- **Exact integer arithmetic only** in both cores; no float type or `libm` call in any FF1 path.
- **No shared mutable state, no `unsafe`**, in either crate.
- **Vectors are never regenerated**, and no self-generated output is committed as a vector.
- **Lock-step versions (plan 00008 D1):** `pyproject.toml`, the core crate and the binding crate carry the same version, Cargo semver spelling for pre-releases.
- **Claims parity:** no FIPS, constant-time or zeroization claim for either artifact.
- **Release convention:** each release reaches `main` through a PR merged with a merge commit, and the tag is placed on that merge commit (plan 00007; user memory rule).
- Only the user tags, pushes, merges and publishes; Builder takes no outward action without per-action authorization. No crates.io token is ever stored in the repository or in a CI secret.
- 100% line and branch coverage on `fpr_ff1`; `just quality` stays Rust-free.

## 6. Assumptions

None. Unresolved matters are recorded as decisions and block approval when material.

## 7. Decisions and blockers

| ID | Decision or blocker | Resolution | Owner | Status |
|---|---|---|---|---|
| D1 | Crate version scheme | Lock-step with the distribution (user decision 2026-09-22, plan 00008 D1), carried | User | Resolved |
| D2 | Crate name | `fpr-ff1`, directory `rust/fpr-ff1/`, library target `fpr_ff1` (user decision 2026-09-22, plan 00008 D2), carried | User | Resolved |
| D3 | Crate licence | `MIT OR Apache-2.0` for the crate; the PyPI distribution stays MIT (user decision 2026-09-22, plan 00008 D3), carried | User | Resolved |
| D4 | Where validation lives | Duplicated in the crate; Python unchanged; a shared case file proves agreement (plan 00008 D4), carried | Planner | Resolved |
| D5 | Key zeroization | Out of scope (plan 00008 D5), carried | Planner | Resolved |
| D6 | `no_std` | Out of scope (plan 00008 D6), carried | Planner | Resolved |
| D7 | Release version | **`2.1.0`**, preceded by `2.1.0rc1`. Lock-step means the crate cannot ship without a matching Python release; the Python package's behaviour is unchanged and the crate is a new artifact, so a minor version. Proposed by the planner on 2026-09-25 and accepted with the request to write this plan | User | Resolved |
| D8 | **MSRV** | **`rust-version = "1.89"`**, replacing plan 00008's 1.87. The code needs 1.88 (`slice::as_chunks`, `lib.rs:112`); `aes` 0.9.3 declares 1.89; every other dependency is lower (`cipher`, `crypto-common`, `hybrid-array`, `inout`, `cpufeatures` 1.85; `pyo3` 1.83; `num-bigint` 0.5.1 1.60). Rejected alternative: swapping `as_chunks` for `chunks_exact` to reach 1.88, which the `aes` floor makes pointless | Planner | Resolved |
| D9 | Numeral type in the public API | `u16` slices (plan 00008 D9), carried | Planner | Resolved |
| D10 | **What the public API exposes** | Only the crate's own types: the FF1 instance, its error enum and its alphabet type, over `u16`, `&[u8]` and `&str`. `num_radix`, `str_radix`, their reference variants, `prf`, `cipher_block`, `encode_len_u32` and the trace hook become crate-private; the PyO3 binding and the conformance tests reach them through a `#[doc(hidden)] pub mod __internal` compiled only with a non-default `internal` feature, documented as outside the semver contract. `cargo-semver-checks` runs without that feature | Planner | Resolved |
| D11 | **How the first crates.io publication happens** | Trusted Publishing cannot create a crate (§19). The owner publishes `2.1.0-rc1` manually, from the tagged commit, uploading a `.crate` whose SHA-256 matches the one CI built, with a crates.io token scoped to `publish-new` for `fpr-ff1` only and revoked immediately afterwards. The owner then configures the Trusted Publisher for this repository and `publish.yml`, and `2.1.0` is published by CI. This also fulfils the user's instruction of 2026-09-22 to publish a crate pre-release. Rejected alternative: a temporary token in a CI secret, which contradicts "no stored token" | Planner (owner performs) | Resolved |
| D12 | Dependabot PR #7 | Close it and take its two upgrades as STEP-01 (`aes`) and STEP-02 (`num-bigint`), each with its own gate, before the split. Rationale: the two are unrelated; #7's checks came from the pre-plan-00007 gate; and upgrading before the first publication means no crate user ever sees these majors | Planner | Resolved |
| D13 | Review 00011's three Lows | Fixed in this release (STEP-03). They were deferred past `2.0.0` by the user; `2.1.0` is the next release and each fix is small | Planner (user may drop at approval) | Resolved |
| D14 | Soak for `2.1.0rc1` | The owner states "soak until <date>" or "soak waived" in the work log after verifying the pre-release, as for `2.0.0rc2` | User (at STEP-14) | Resolved |
| D15 | Park rule for `num-bigint` 0.5 | After STEP-02, `just bench` must show `rust <= python` at n = 20,000 on radix 10 and 256, **and** the Rust time at n = 20,000 no more than 10% above the plan 00007 STEP-05 record (radix 10 9.9 ms, radix 256 4.1 ms) on the same machine class. Otherwise the Builder stops and escalates with numbers; keeping `num-bigint` 0.4.8, still maintained, is the fallback | Planner | Resolved |

## 8. Affected architecture and components

- `rust/Cargo.toml` — workspace members become `fpr-ff1` (published) and `fpr-ff1-rust` (PyO3 binding, unpublished).
- `rust/fpr-ff1/` (new) — `src/lib.rs`, `src/validate.rs`, `src/error.rs`, `src/alphabet.rs`, `src/internal.rs` (feature-gated), `tests/`, `README.md`, `LICENSE-MIT`, `LICENSE-APACHE`, `Cargo.toml` with `rust-version = "1.89"`.
- `rust/fpr-ff1-rust/` — PyO3 layer only; depends on `fpr-ff1` by path with `features = ["internal"]`.
- `rust/Cargo.lock` — `aes` 0.9.3, `cipher` 0.5.2, `crypto-common` 0.2.2, `num-bigint` 0.5.1 and their transitive changes.
- `src/fpr_ff1/_ff1.py` — `_require_bytes` normalises a released-buffer `ValueError` (REQ-03); no other change.
- `tests/test_properties.py`, `tests/test_thread_safety.py`, `tests/test_validation.py`, `tests/test_contract.py` — REQ-03, REQ-08, REQ-09.
- `tests/vectors/validation_cases.json` (new) — the shared case file.
- `.github/workflows/ci.yml`, `.github/workflows/publish.yml` — crate jobs, MSRV leg at 1.89, the Trusted Publishing job.
- `README.md`, `AGENTS.md`, `SECURITY.md`, `CHANGELOG.md`, `docs/architecture.md`, `docs/directory-structure.md`, `docs/developer-guide.md`, `docs/backlog.md`, `justfile`.

```mermaid
flowchart LR
    Deps["STEP-01/02: aes 0.9, num-bigint 0.5"] --> Split["STEP-04: fpr-ff1 core + PyO3 binding"]
    Lows["STEP-03: review 00011 Lows"] --> Split
    Split --> Crate["STEP-05..12: validation, API, conformance, case file, packaging, CI, docs"]
    Crate --> RC["STEP-13/14: 2.1.0rc1 on PyPI (CI) and crates.io (manual bootstrap)"]
    RC --> Review["STEP-15: re-review"]
    Review --> Final["STEP-16/17: 2.1.0 on PyPI and crates.io (both by CI)"]
```

## 9. Requirement catalogue

### PLAN-00009-REQ-01 — Upgrade `aes` to 0.9 as its own gated change

- **Requirement:** Bump `aes` to 0.9 (resolving `cipher` 0.5.2, `crypto-common` 0.2.2, `hybrid-array`, `inout` 0.2, `cpufeatures` 0.3) and migrate the two AES seams: `BlockEncrypt` to `BlockCipherEncrypt`, `Block::clone_from_slice` to `Block::from`, as in PR #7. No other change in the commit. Close PR #7 with a comment pointing at this commit and STEP-02.
- **Rationale:** The AES implementation is the one component a second cryptographic implementation must never get wrong; the FIPS 197 known-answer vectors and PRF-equality tests exist to police exactly this swap.
- **Source:** Dependabot PR #7; user decision to hold it until after `v2.0.0`.
- **Acceptance evidence:** `tests/test_rust_aes_validation.py` (FIPS 197 KAT and PRF equality with the Python path) green; full dual-backend suite bit-exact including per-round intermediates; `cargo audit` clean; `Cargo.lock` diff limited to the AES stack.

### PLAN-00009-REQ-02 — Upgrade `num-bigint` to 0.5 under a park rule

- **Requirement:** Bump `num-bigint` to 0.5.1, adapting any changed API at its call sites (`BigUint::from`, `to_bytes_be`, `from_bytes_be`, `pow`, `div_rem`, `bits`, `iter_u32_digits`). Re-run the Rust conversion equivalence sweep across every supported radix, the full dual-backend suite, and `just bench`, then apply the park rule in D15.
- **Rationale:** `num-bigint` is the arithmetic engine of the divide-and-conquer conversion; its subquadratic division is why the Rust backend overtook the Python path. A major version needs a performance decision rule, not only a green suite.
- **Source:** Dependabot PR #7; plan 00007 STEP-05 benchmark record.
- **Acceptance evidence:** Equivalence sweep and full suite green and bit-exact; the benchmark recorded with machine, interpreter and toolchain; the park-rule verdict recorded; or an escalation entry and a reverted bump.

### PLAN-00009-REQ-03 — Fix review 00011's three deferred Low findings

- **Requirement:** (a) `_require_bytes` translates the `ValueError` raised by `bytes(memoryview)` on a released view into the caller-selected `FF1Error` subclass, with a message naming the argument but not its contents; no broader exception is caught. (b) `test_tweak_sensitivity` asserts: over the drawn cases, a collision is tolerated only on domains small enough for one to be plausible, and the test fails if every drawn pair collides. (c) Both concurrency tests in `tests/test_thread_safety.py` compare every iteration's result with the serial expectation, not only the last.
- **Rationale:** (a) keeps every rejection inside the documented hierarchy; (b) and (c) make two tests able to fail when their property breaks, in a project where a test that cannot fail is a defect.
- **Source:** Review 00011 `REV-00011-LOW-01`, `LOW-02`, `LOW-03`, re-confirmed still open by review 00013.
- **Acceptance evidence:** New rejection tests for a released view as key, default tweak and per-call tweak on both backends; (b) and (c) shown to fail against a deliberately broken implementation (tweak ignored; one wrong result injected mid-loop) and pass against the real one; coverage 100%.

### PLAN-00009-REQ-04 — Split the workspace and keep third-party types out of the public API

- **Requirement:** Create the `fpr-ff1` crate with the FF1 core, PRF, AES seams and conversion, no PyO3 dependency, `crate-type = ["rlib"]`. Reduce `fpr-ff1-rust` to the PyO3 layer, depending on `fpr-ff1` by path with the `internal` feature, keeping `cdylib`, `publish = false` and the `_fpr_ff1_rs` target. Per D10, the published API names no type from `num-bigint`, `aes`, `cipher` or `pyo3`; internal helpers live in the feature-gated `__internal` module.
- **Rationale:** Publication requires an `rlib` free of `extension-module`; and a third-party type in a published signature ties the crate's semver to that dependency's.
- **Source:** Plan 00008 REQ-01; `rust/fpr-ff1-rust/src/lib.rs:149-414`.
- **Acceptance evidence:** `cargo tree -p fpr-ff1` shows no `pyo3`; `cargo doc -p fpr-ff1` (without `internal`) lists no third-party type in any public signature; the wheel's file list and the extension's behaviour are unchanged; the full gate is green.

### PLAN-00009-REQ-05 — Port the validation layer with typed errors

- **Requirement:** As plan 00008 REQ-02: key length; radix `2 <= radix < 2**16`; minimum domain `radix**minlen >= 1_000_000` by integer arithmetic; length `min_length..=2**32 - 1`; numerals `< radix`; tweak length `<= 2**32 - 1`; tweak bounds including rejection above the ceiling and `min > max`; alphabet length and uniqueness; string characters from the alphabet. Errors are a non-exhaustive enum mirroring the Python hierarchy, implementing `core::error::Error`, with messages free of plaintext and key material.
- **Rationale:** The core validates nothing today; a published library must not fail open.
- **Source:** Plan 00008 REQ-02; `src/fpr_ff1/_ff1.py`; `src/fpr_ff1/_exceptions.py`.
- **Acceptance evidence:** A rejection test for every rule and boundary; no message contains a numeral value or key byte.

### PLAN-00009-REQ-06 — A documented Rust public API

- **Requirement:** As plan 00008 REQ-03: a constructor returning `Result`; `encrypt_numerals`/`decrypt_numerals` over `&[u16]`; `encrypt`/`decrypt` over `&str` with an alphabet; `min_length`/`max_length`. `Send + Sync`, no interior mutability. Every public item documented; crate-root documentation states the supported subset, the limits, no FF3, no FIPS, no constant-time, and that the Python package is the reference implementation; runnable doctests.
- **Rationale:** The API is the part fixed at publication.
- **Source:** Plan 00008 REQ-03; `AGENTS.md` §Public API.
- **Acceptance evidence:** `cargo test --doc` green; `cargo doc` with warnings denied; a compile-time `Send + Sync` assertion.

### PLAN-00009-REQ-07 — The crate's own conformance evidence

- **Requirement:** As plan 00008 REQ-04: the nine NIST samples both directions; per-round intermediates for every round of every sample; FIPS 197 AES vectors; frozen vectors including `d > 16`; exact-arithmetic boundary radices; property tests; exhaustive bijectivity for radix 2 length 20 and radix 10 length 6; a scan failing on any float type or `libm` call in the crate's FF1 path. All from the existing JSON files.
- **Rationale:** The crate must carry the evidence itself, not inherit it by association.
- **Source:** Plan 00008 REQ-04; `AGENTS.md` §Tests.
- **Acceptance evidence:** `cargo test` green; the float scan fails on a deliberate float; a deliberate S-expansion break fails the intermediates.

### PLAN-00009-REQ-08 — Prove the two validation layers agree

- **Requirement:** As plan 00008 REQ-05: `tests/vectors/validation_cases.json`, consumed by both suites, covering every Python exception type except `BackendError` and every Rust error variant; the released-`memoryview` case from REQ-03 is Python-only and marked so.
- **Rationale:** Two validation layers are two chances to diverge.
- **Source:** Plan 00008 REQ-05.
- **Acceptance evidence:** Both suites green; a deliberate divergence fails exactly one.

### PLAN-00009-REQ-09 — Lock-step across three manifests

- **Requirement:** As plan 00008 REQ-06: the contract test checks `pyproject.toml` and both crate manifests, and the `publish` flags (core publishable, binding not).
- **Rationale:** Plan 00008 D1.
- **Source:** Plan 00008 REQ-06; `tests/test_contract.py`.
- **Acceptance evidence:** Red on drift, green when aligned, without a Rust toolchain.

### PLAN-00009-REQ-10 — Packaging and metadata, with MSRV 1.89

- **Requirement:** As plan 00008 REQ-07, with `rust-version = "1.89"` (D8), `license = "MIT OR Apache-2.0"` and both licence files. The `.crate` contains the crate's sources, README, licences and any fixtures its packaged tests need, and nothing from the Python tree, no agent instructions, plans or reviews. docs.rs builds without the `internal` feature.
- **Rationale:** Publication is irreversible per version.
- **Source:** Plan 00008 REQ-07; review 00013 `REV-00013-MED-01`; D8.
- **Acceptance evidence:** `cargo package --locked` and `cargo publish --dry-run` green; a contents assertion passes and fails on a forbidden path; the crate builds and tests on Rust 1.89.

### PLAN-00009-REQ-11 — Gate the crate in CI

- **Requirement:** As plan 00008 REQ-08: workspace `cargo test` on three operating systems; `clippy -D warnings` and `fmt --check`; an MSRV leg pinned to **1.89**; `cargo doc` with warnings denied; `cargo package --locked` with the contents assertion; `cargo-semver-checks` against the last published version without the `internal` feature, skipped with a recorded reason before the first publication. All inside `ci.yml`, so `publish.yml` requires them.
- **Rationale:** The existing gate proves the extension, not the library crate.
- **Source:** Plan 00008 REQ-08.
- **Acceptance evidence:** All new jobs green; each fails when its subject is deliberately broken.

### PLAN-00009-REQ-12 — Bootstrap, then publish by Trusted Publishing

- **Requirement:** (a) `2.1.0-rc1` is published **manually by the owner** per D11: from the tagged commit, uploading the exact `.crate` CI built (SHA-256 compared), with a token scoped to `publish-new` for `fpr-ff1`, revoked immediately after. (b) The owner then configures the crates.io Trusted Publisher for `joelee/fpr-ff1`, workflow `publish.yml`. (c) `publish.yml` gains a `publish-crate` job using `rust-lang/crates-io-auth-action` (SHA-pinned) with `id-token: write`, running `cargo publish --locked -p fpr-ff1` only for non-prerelease versions, after the gate. No token is stored in the repository or a CI secret at any point.
- **Rationale:** crates.io cannot create a crate by OIDC (§19); the manual step must still publish exactly what CI verified.
- **Source:** Plan 00008 REQ-09; crates.io documentation; user instruction of 2026-09-22 (crate pre-release).
- **Acceptance evidence:** The published `2.1.0-rc1` `.crate` digest equals CI's; the token's revocation recorded by the owner; `2.1.0` published by the CI job.

### PLAN-00009-REQ-13 — Update the maintained documents

- **Requirement:** As plan 00008 REQ-10: `AGENTS.md` (the crate as a third artifact, validation duplicated, the case file, lock-step, no floats, the crate is not the reference, the `internal` feature is not public API); `docs/architecture.md`; `docs/directory-structure.md`; `docs/developer-guide.md` (recipes, CI jobs, MSRV, the bootstrap-then-OIDC publishing sequence); `README.md` (a Rust section); `SECURITY.md` (the crate named, same claims and channel); `docs/backlog.md`; `CHANGELOG.md`.
- **Rationale:** `docs/AGENTS.md`.
- **Source:** Plan 00008 REQ-10.
- **Acceptance evidence:** No document implies the crate is the reference or carries stronger claims.

### PLAN-00009-REQ-14 — Release `2.1.0rc1` and `2.1.0` on both registries

- **Requirement:** For each of `2.1.0rc1` and `2.1.0`: all three manifests at that version; a dated changelog section; the full gate and CI green at the release commit; the owner merges the release branch into `main` by PR **with a merge commit**, tags exactly `v2.1.0rc1` / `v2.1.0` on that merge commit, and publishes the GitHub release (pre-release, then final); `publish.yml` publishes to PyPI (and, for `2.1.0`, crates.io). Builder verifies both registries: files and digests against CI artifacts, PyPI attestations, docs.rs build, a scratch project outside the repository depending on the published crate reproducing a NIST vector and a `d > 16` case, and clean Python installs on both backends. An owner soak (D14) and an independent re-review with no Critical or Major finding separate the two.
- **Rationale:** Plan 00007's proven release discipline, including the merge-to-`main` step it initially missed.
- **Source:** Plan 00008 REQ-11; plan 00007 STEP-09 to STEP-14; user memory rule on tags.
- **Acceptance evidence:** Both versions live on both registries from tags on `main`; verification and handoff recorded.

## 10. Delivery strategy

1. **Dependencies first, while the code is still one crate** (STEP-01, STEP-02). Each upgrade is proven bit-exact on its own, so a later failure is never ambiguous between "the upgrade" and "the split".
2. **Small deferred fixes** (STEP-03), independent and quick.
3. **The split, with the API boundary drawn at the same time** (STEP-04). Deciding what is public while moving code avoids moving it twice.
4. **The crate's substance** (STEP-05 to STEP-08): validation, API, conformance, agreement.
5. **Packaging, CI and documentation** (STEP-09 to STEP-12).
6. **Candidate** (STEP-13, STEP-14): `2.1.0rc1` on PyPI by CI and on crates.io by the manual bootstrap, then Trusted Publisher configuration and soak.
7. **Promotion** (STEP-15 to STEP-17): re-review, final bump, both registries by CI.

Checkpoint after every code step: `just quality` (Rust-free), the full dual-backend gate with both `REQUIRE` flags, `cargo test` for the workspace, `just rust-lint`. From STEP-10 onward, also the MSRV build on 1.89 and `cargo package`.

## 11. Detailed implementation steps

### PLAN-00009-STEP-01 — Upgrade `aes` to 0.9

- **Status placeholder:** `not-started`
- **Objective:** The AES stack at 0.9, proven bit-exact.
- **Requirements:** `PLAN-00009-REQ-01`
- **Depends on:** None
- **Affected components:** `rust/fpr-ff1-rust/Cargo.toml`, `rust/Cargo.lock`, `rust/fpr-ff1-rust/src/lib.rs` (`prf`, `cipher_block` imports and block construction)
- **Preconditions:** Plan approved; clean worktree on a branch from `main` that includes plan 00007's closeout; Dependabot #10 and #11 merged or explicitly left open by the owner.
- **Test or evidence first:** Record the AES KAT, PRF-equality and full-suite results at the baseline.
- **Implementation tasks:**
  1. Set `aes = "0.9"`; `cargo update -p aes`; confirm the lock diff is the AES stack only.
  2. Apply the two API migrations from PR #7 and nothing else.
  3. Run the checkpoint; record `cargo audit`.
  4. Close PR #7 with a comment linking this commit and STEP-02 (owner-authorized outward action).
- **Documentation/configuration/operations:** None.
- **Verification:** `tests/test_rust_aes_validation.py`; full dual-backend gate including intermediates; `cargo test`; `just rust-lint`; `cargo audit`.
- **Completion criteria:** Bit-exact; one commit.
- **Rollback or recovery:** Revert the commit.
- **Builder stop conditions:** Any KAT, PRF-equality, ciphertext or intermediate difference; a lock change outside the AES stack.

### PLAN-00009-STEP-02 — Upgrade `num-bigint` to 0.5 under the park rule

- **Status placeholder:** `not-started`
- **Objective:** `num-bigint` 0.5.1 with no loss of correctness or of the long-input result.
- **Requirements:** `PLAN-00009-REQ-02`
- **Depends on:** STEP-01
- **Affected components:** `rust/fpr-ff1-rust/Cargo.toml`, `rust/Cargo.lock`, `rust/fpr-ff1-rust/src/lib.rs` conversion call sites
- **Preconditions:** STEP-01 committed.
- **Test or evidence first:** Record the equivalence sweep and a `just bench` run at `num-bigint` 0.4.8 on the machine that will measure 0.5.1.
- **Implementation tasks:**
  1. Set `num-bigint = "0.5"`; update the lock; adapt any changed API.
  2. Run the equivalence sweep and the checkpoint.
  3. Run `just bench` with the release-built extension; apply D15; record machine, interpreter, toolchain and every row.
- **Documentation/configuration/operations:** README performance figures only if the park rule passes and the numbers moved materially; otherwise unchanged.
- **Verification:** Equivalence sweep; full gate; benchmark recorded.
- **Completion criteria:** Park rule passed; one commit.
- **Rollback or recovery:** Revert to 0.4.8 (still maintained).
- **Builder stop conditions:** Park-rule failure (escalate with numbers); any divergence.

### PLAN-00009-STEP-03 — Fix review 00011's three Lows

- **Status placeholder:** `not-started`
- **Objective:** Every rejection typed; two tests able to fail.
- **Requirements:** `PLAN-00009-REQ-03`
- **Depends on:** None
- **Affected components:** `src/fpr_ff1/_ff1.py` (`_require_bytes`), `tests/test_validation.py`, `tests/test_properties.py`, `tests/test_thread_safety.py`, `CHANGELOG.md` (`[Unreleased]`)
- **Preconditions:** Clean worktree.
- **Test or evidence first:** Released-view tests first (they fail with `ValueError`); for (b) and (c), demonstrate each test failing against a deliberately broken implementation before relying on it, recorded in the work log and not committed.
- **Implementation tasks:**
  1. Narrow `ValueError` translation in `_require_bytes`, message without contents.
  2. Give `test_tweak_sensitivity` a failing assertion per REQ-03(b).
  3. Compare every iteration in both concurrency tests.
- **Documentation/configuration/operations:** Changelog entry for the exception-type change.
- **Verification:** Checkpoint; coverage 100%.
- **Completion criteria:** Three fixes, each with its red evidence; one commit.
- **Rollback or recovery:** Revert the commit.
- **Builder stop conditions:** Any change to accepted inputs or ciphertext; a catch broader than the released-buffer case.

### PLAN-00009-STEP-04 — Split the workspace and draw the API boundary

- **Status placeholder:** `not-started`
- **Objective:** A publishable `fpr-ff1` with no third-party type in its public API.
- **Requirements:** `PLAN-00009-REQ-04`
- **Depends on:** STEP-01, STEP-02, STEP-03
- **Affected components:** `rust/Cargo.toml`, `rust/fpr-ff1/` (new), `rust/fpr-ff1-rust/{Cargo.toml,src/lib.rs}`, `rust/Cargo.lock`, `justfile`
- **Preconditions:** STEP-01 to STEP-03 committed.
- **Test or evidence first:** Record the wheel's file list and `_rs.__version__`, and the gate result.
- **Implementation tasks:**
  1. Create `rust/fpr-ff1/` (package `fpr-ff1`, target `fpr_ff1`, `crate-type = ["rlib"]`); move the core, PRF, AES seams, conversion and trace types; remove PyO3.
  2. Make conversion, PRF, block-cipher, length-encoding and trace items crate-private; re-export what the binding and tests need from `#[doc(hidden)] pub mod __internal`, compiled only with feature `internal`.
  3. Reduce `fpr-ff1-rust` to the PyO3 layer, depending on `fpr-ff1` with `features = ["internal"]`.
  4. Re-run the gate; compare the wheel file list.
- **Documentation/configuration/operations:** None (STEP-12).
- **Verification:** `cargo tree -p fpr-ff1` without `pyo3`; `cargo doc -p fpr-ff1` public signatures free of third-party types; full gate; wheel file list unchanged.
- **Completion criteria:** Extension identical; boundary drawn; one commit.
- **Rollback or recovery:** Revert the commit.
- **Builder stop conditions:** Any behaviour or wheel-content change; a public signature that needs a third-party type.

### PLAN-00009-STEP-05 — Port validation and typed errors

- **Status placeholder:** `not-started`
- **Objective:** The crate rejects everything the Python package rejects.
- **Requirements:** `PLAN-00009-REQ-05`
- **Depends on:** STEP-04
- **Affected components:** `rust/fpr-ff1/src/{error.rs,validate.rs,lib.rs}`
- **Preconditions:** STEP-04 committed.
- **Test or evidence first:** Rejection tests for every rule and boundary, failing until implemented.
- **Implementation tasks:**
  1. The non-exhaustive error enum with `Display` and `core::error::Error`, redacted messages.
  2. `min_length` by integer arithmetic, matching `_min_length`.
  3. Validation wired into every entry point before computation.
- **Documentation/configuration/operations:** Doc comments naming the rule behind each check.
- **Verification:** `cargo test`; `just rust-lint`; no float in the crate.
- **Completion criteria:** Every rule enforced and tested; one commit.
- **Rollback or recovery:** Revert the commit.
- **Builder stop conditions:** A rule needing floats; a message that would echo data.

### PLAN-00009-STEP-06 — Public API and documentation

- **Status placeholder:** `not-started`
- **Objective:** The API Rust callers use, with runnable examples.
- **Requirements:** `PLAN-00009-REQ-06`
- **Depends on:** STEP-05
- **Affected components:** `rust/fpr-ff1/src/{lib.rs,alphabet.rs}`, `rust/fpr-ff1/README.md`
- **Preconditions:** STEP-05 committed.
- **Test or evidence first:** Doctests for construction, both interfaces and a rejection; a `Send + Sync` assertion.
- **Implementation tasks:**
  1. The constructor, four operations and accessors over `u16`.
  2. The alphabet type: length and uniqueness by code point.
  3. Crate-root documentation and README.
- **Documentation/configuration/operations:** This step is the crate's documentation.
- **Verification:** `cargo test --doc`; `cargo doc --no-deps` with warnings denied.
- **Completion criteria:** Every public item documented; examples run; one commit.
- **Rollback or recovery:** Revert the commit.
- **Builder stop conditions:** Any claim beyond the Python package's.

### PLAN-00009-STEP-07 — Conformance suite

- **Status placeholder:** `not-started`
- **Objective:** The crate's own evidence.
- **Requirements:** `PLAN-00009-REQ-07`
- **Depends on:** STEP-06
- **Affected components:** `rust/fpr-ff1/tests/`, dev-dependencies (a JSON parser, a property-test crate)
- **Preconditions:** STEP-06 committed.
- **Test or evidence first:** This step is the evidence.
- **Implementation tasks:**
  1. NIST samples both directions and per-round intermediates from the JSON files.
  2. AES KAT and frozen vectors including `d > 16`.
  3. Property tests and gated bijectivity sweeps (CI runs them in full).
  4. The float scan.
- **Documentation/configuration/operations:** None.
- **Verification:** `cargo test`; deliberate float and deliberate S-expansion break both fail.
- **Completion criteria:** REQ-07 covered; one commit.
- **Rollback or recovery:** Revert the commit.
- **Builder stop conditions:** A regenerated or hand-written expected value; any divergence from the Python core.

### PLAN-00009-STEP-08 — Cross-language validation agreement

- **Status placeholder:** `not-started`
- **Objective:** Both validation layers proven equivalent.
- **Requirements:** `PLAN-00009-REQ-08`
- **Depends on:** STEP-07
- **Affected components:** `tests/vectors/validation_cases.json`, a Python test module, `rust/fpr-ff1/tests/`
- **Preconditions:** STEP-07 committed.
- **Test or evidence first:** The case file written from the Python rules; the Python side passes before the Rust side exists.
- **Implementation tasks:**
  1. Case schema and cases covering every error kind.
  2. Consume from both suites.
  3. Record a deliberate divergence failing exactly one side.
- **Documentation/configuration/operations:** `AGENTS.md` at STEP-12.
- **Verification:** Both suites green; the probe recorded.
- **Completion criteria:** Agreement proven; one commit.
- **Rollback or recovery:** Revert the commit.
- **Builder stop conditions:** A case one language cannot express; any weakened assertion.

### PLAN-00009-STEP-09 — Lock-step for three manifests

- **Status placeholder:** `not-started`
- **Objective:** No manifest can drift.
- **Requirements:** `PLAN-00009-REQ-09`
- **Depends on:** STEP-04
- **Affected components:** `tests/test_contract.py`, both crate manifests
- **Preconditions:** STEP-04 committed.
- **Test or evidence first:** Drift one manifest; record red; restore; record green.
- **Implementation tasks:**
  1. Extend the contract test to both manifests and the `publish` flags.
- **Documentation/configuration/operations:** `AGENTS.md` at STEP-12.
- **Verification:** `uv run pytest tests/test_contract.py`, without a Rust toolchain.
- **Completion criteria:** Red-then-green recorded; one commit.
- **Rollback or recovery:** Revert the commit.
- **Builder stop conditions:** None.

### PLAN-00009-STEP-10 — Packaging, metadata and MSRV 1.89

- **Status placeholder:** `not-started`
- **Objective:** A correct `.crate` that builds on its declared minimum Rust.
- **Requirements:** `PLAN-00009-REQ-10`
- **Depends on:** STEP-07, STEP-09
- **Affected components:** `rust/fpr-ff1/{Cargo.toml,README.md,LICENSE-MIT,LICENSE-APACHE}`
- **Preconditions:** STEP-07 and STEP-09 committed.
- **Test or evidence first:** `cargo package --list` recorded; a build on Rust 1.88 recorded failing (proving 1.89 is the true floor, not a guess).
- **Implementation tasks:**
  1. Metadata: description, repository, documentation, homepage, keywords, categories, `rust-version = "1.89"`, `license = "MIT OR Apache-2.0"`, docs.rs configuration without `internal`.
  2. Licence files; fixtures included or packaged tests gated.
  3. The contents assertion; `cargo package --locked`; `cargo publish --dry-run`.
  4. Build and test on 1.89 with the locked dependencies.
- **Documentation/configuration/operations:** Crate README final.
- **Verification:** All green on 1.89; contents assertion passes and fails on a forbidden path.
- **Completion criteria:** The package is correct and reproducible; one commit.
- **Rollback or recovery:** Revert the commit.
- **Builder stop conditions:** A forbidden file in the package; the crate needing more than 1.89 (escalate: D8 would be wrong again).

### PLAN-00009-STEP-11 — CI jobs for the crate

- **Status placeholder:** `not-started`
- **Objective:** Every claim about the crate gated.
- **Requirements:** `PLAN-00009-REQ-11`, `PLAN-00009-REQ-12` (the `publish-crate` job)
- **Depends on:** STEP-10
- **Affected components:** `.github/workflows/ci.yml`, `.github/workflows/publish.yml`, `justfile`
- **Preconditions:** STEP-10 committed; push authorization.
- **Test or evidence first:** actionlint; each command run locally first.
- **Implementation tasks:**
  1. Workspace tests on three operating systems; the 1.89 MSRV leg; `cargo doc`; `cargo package` with the assertion; `cargo-semver-checks` with its recorded first-publication skip.
  2. The `publish-crate` job in `publish.yml`: SHA-pinned `rust-lang/crates-io-auth-action`, `id-token: write`, non-prerelease only, after the gate.
  3. Matching `just` recipes.
  4. Push (authorized) and iterate to green.
- **Documentation/configuration/operations:** Developer guide at STEP-12.
- **Verification:** All new jobs green; each fails on a deliberate break; the publish job skipped for a pre-release version in a dry run.
- **Completion criteria:** Gate as strong as the wheels'; one commit plus recorded fix-ups.
- **Rollback or recovery:** Revert the workflow commit.
- **Builder stop conditions:** A job that cannot be made green on a supported runner.

### PLAN-00009-STEP-12 — Documentation

- **Status placeholder:** `not-started`
- **Objective:** Every maintained document describes both artifacts truthfully.
- **Requirements:** `PLAN-00009-REQ-13`
- **Depends on:** STEP-11
- **Affected components:** `AGENTS.md`, `README.md`, `SECURITY.md`, `docs/architecture.md`, `docs/directory-structure.md`, `docs/developer-guide.md`, `docs/backlog.md`
- **Preconditions:** STEP-11 committed.
- **Test or evidence first:** Not applicable.
- **Implementation tasks:**
  1. The documents listed in REQ-13, including the bootstrap-then-OIDC publishing sequence and the `internal` feature's status.
- **Documentation/configuration/operations:** This step is the documentation.
- **Verification:** Ruff checks; a read-through against REQ-13.
- **Completion criteria:** No document implies the crate is the reference or has stronger claims; one commit.
- **Rollback or recovery:** Revert the commit.
- **Builder stop conditions:** A statement not sourced from the shipped artifacts.

### PLAN-00009-STEP-13 — Cut and gate `2.1.0rc1`

- **Status placeholder:** `not-started`
- **Objective:** A gated candidate commit at `2.1.0rc1` / `2.1.0-rc1`.
- **Requirements:** `PLAN-00009-REQ-14`, `PLAN-00009-REQ-09`
- **Depends on:** STEP-12
- **Affected components:** `pyproject.toml`, both crate manifests, `uv.lock`, `rust/Cargo.lock`, `CHANGELOG.md`
- **Preconditions:** STEP-12 committed.
- **Test or evidence first:** Contract test red-then-green across the bump.
- **Implementation tasks:**
  1. Bump all three manifests and both locks; a dated `[2.1.0rc1]` section.
  2. Full local gate; `cargo package --locked`, recording the `.crate` SHA-256; CI green at the candidate commit (push authorized).
  3. Hand off: frozen commit, `.crate` digest, CI run.
- **Documentation/configuration/operations:** Changelog.
- **Verification:** `uv lock --check`; `cargo build --locked`; contract test; full gate; CI green.
- **Completion criteria:** Candidate gated; `.crate` digest recorded.
- **Rollback or recovery:** Revert the commit.
- **Builder stop conditions:** Lock drift beyond version lines.

### PLAN-00009-STEP-14 — Owner publishes `2.1.0rc1` on both registries; soak

- **Status placeholder:** `not-started`
- **Objective:** The candidate public on PyPI and crates.io, Trusted Publisher configured.
- **Requirements:** `PLAN-00009-REQ-12`, `PLAN-00009-REQ-14`
- **Depends on:** STEP-13
- **Affected components:** None (owner actions; Builder verification)
- **Preconditions:** STEP-13 complete.
- **Test or evidence first:** This step is the evidence.
- **Implementation tasks:**
  1. **Owner:** PR the release branch into `main`, merge with a merge commit, tag `v2.1.0rc1` on it, publish a GitHub **pre-release**; `publish.yml` publishes to PyPI (its crate job skips the pre-release).
  2. **Owner:** download the `.crate` from the release's CI run, confirm its SHA-256 equals STEP-13's, and `cargo publish` it with a token scoped to `publish-new` for `fpr-ff1`; then revoke the token and record that it is revoked.
  3. **Owner:** configure the Trusted Publisher on crates.io for `joelee/fpr-ff1`, `publish.yml`.
  4. **Builder:** verify PyPI (files, digests, attestations, installs on both backends) and crates.io (version, licence, metadata, `.crate` digest, docs.rs build, a scratch project reproducing a NIST vector and a `d > 16` case).
  5. **Owner:** the D14 soak statement.
- **Documentation/configuration/operations:** Work log.
- **Verification:** Both registries verified; token revocation and Trusted Publisher configuration recorded.
- **Completion criteria:** `2.1.0rc1` public on both registries, verified, soak stated.
- **Rollback or recovery:** A defective candidate is left in place (yank if harmful) and fixed in `2.1.0rc2`; never overwritten.
- **Builder stop conditions:** A digest mismatch; any behavioural difference from the gated candidate.

### PLAN-00009-STEP-15 — Independent re-review

- **Status placeholder:** `not-started`
- **Objective:** Independent verification before promotion.
- **Requirements:** `PLAN-00009-REQ-14`
- **Depends on:** STEP-14 and the soak
- **Affected components:** `docs/reviews/` (the reviewer's report)
- **Preconditions:** Soak elapsed or waived.
- **Test or evidence first:** The review is the evidence.
- **Implementation tasks:**
  1. Builder prepares an evidence bundle for `v2.0.0..v2.1.0rc1`.
  2. **Owner** commissions the review.
  3. Owner dispositions any remaining finding in the work log.
- **Documentation/configuration/operations:** None by Builder.
- **Verification:** No Critical or Major finding; every finding dispositioned.
- **Completion criteria:** A clean review recorded.
- **Rollback or recovery:** A Critical or Major finding sends the work to `2.1.0rc2`.
- **Builder stop conditions:** Any Critical or Major finding.

### PLAN-00009-STEP-16 — Bump to `2.1.0`

- **Status placeholder:** `not-started`
- **Objective:** The final release commit.
- **Requirements:** `PLAN-00009-REQ-14`, `PLAN-00009-REQ-09`
- **Depends on:** STEP-15
- **Affected components:** `pyproject.toml`, both crate manifests, both locks, `CHANGELOG.md`, `README.md`, `docs/backlog.md`
- **Preconditions:** STEP-15 clean.
- **Test or evidence first:** Contract test red-then-green.
- **Implementation tasks:**
  1. Bump all three manifests and both locks; a dated `[2.1.0]` section; `[Unreleased]` at `v2.1.0...HEAD`.
  2. Full gate; `cargo package --locked`; CI green at the commit.
- **Documentation/configuration/operations:** Changelog, README, backlog.
- **Verification:** As STEP-13.
- **Completion criteria:** Gated final commit; one commit.
- **Rollback or recovery:** Revert the commit.
- **Builder stop conditions:** Lock drift; a red gate.

### PLAN-00009-STEP-17 — Owner publishes `2.1.0`; verify; handoff

- **Status placeholder:** `not-started`
- **Objective:** `2.1.0` on both registries by CI, verified.
- **Requirements:** `PLAN-00009-REQ-12`, `PLAN-00009-REQ-14`
- **Depends on:** STEP-16
- **Affected components:** `docs/backlog.md` (completion record)
- **Preconditions:** STEP-16 committed; Trusted Publisher configured (STEP-14).
- **Test or evidence first:** This step is the evidence.
- **Implementation tasks:**
  1. **Owner:** PR into `main` with a merge commit, tag `v2.1.0` on it, publish a non-prerelease GitHub release; `publish.yml` publishes PyPI and crates.io.
  2. **Builder:** verify both registries as in STEP-14; confirm the crate was published by the CI job (Trusted Publishing), not by hand.
  3. **Builder:** handoff record (commits, tags, runs, digests, toolchain, support policy) and the recovery procedure (yank-and-patch on either registry; never overwrite; never move a tag).
- **Documentation/configuration/operations:** Handoff; backlog.
- **Verification:** Both registries show `2.1.0` from `v2.1.0` on `main`.
- **Completion criteria:** Released, verified, handed off.
- **Rollback or recovery:** Yank and publish `2.1.1`.
- **Builder stop conditions:** Any gate failure; a crate published by anything other than the CI job.

## 12. Cross-cutting concerns

| Area | Applicability | Planned action or reason not applicable | Step or requirement |
|---|---|---|---|
| Compatibility and APIs | Applicable | Python API unchanged apart from one exception-type narrowing; the crate's API fixed at publication with no third-party types, then checked by `cargo-semver-checks` | REQ-03, REQ-04, REQ-11 |
| Data and migration | Not applicable | Ciphertext unchanged | — |
| Security and privacy | Applicable | AES upgrade proven by KAT and PRF equality; validation fail-closed with redacted messages; scoped, revoked bootstrap token; no stored token | REQ-01, REQ-05, REQ-12 |
| Performance and scale | Applicable | `num-bigint` 0.5 under a park rule with a fallback | REQ-02 |
| Reliability and failure handling | Applicable | Typed errors; case file prevents divergent acceptance | REQ-05, REQ-08 |
| Observability and operations | Not applicable | Library | — |
| Dependencies and supply chain | Applicable | Two majors taken separately; `--locked`; `cargo audit`; SHA-pinned actions; digests compared across CI and registries | REQ-01, REQ-02, REQ-12 |
| Accessibility and UX | Not applicable | No UI | — |
| Documentation and release | Applicable | Every maintained document; two changelog sections | REQ-13, REQ-14 |
| Deployment and rollback | Applicable | Immutable versions on both registries; yank-and-patch recorded; tags on `main` merge commits | REQ-14 |

## 13. Verification strategy

| Level | Evidence or command | When | Required result |
|---|---|---|---|
| AES correctness | `tests/test_rust_aes_validation.py` | STEP-01 onward | FIPS 197 KAT and PRF equality green |
| Conversion equivalence | Rust sweep over every supported radix | STEP-02 onward | Equal to the reference |
| Performance | `just bench`, D15 | STEP-02 | Park rule passed or escalated |
| Python suite | Full dual-backend gate; `just quality` Rust-free | Every code step | 100% coverage; bit-exact |
| Rust unit and integration | `cargo test`; `just rust-lint` | Every code step | Green |
| API boundary | `cargo doc -p fpr-ff1` without `internal` | STEP-04 onward | No third-party type in a public signature |
| Docs and doctests | `cargo test --doc`; `cargo doc` warnings denied | STEP-06 onward | Green |
| Cross-language agreement | Shared case file in both suites | STEP-08 onward | Both green; probe fails one |
| Lock-step | Contract test | STEP-09, STEP-13, STEP-16 | Red on drift |
| MSRV | Build and test on 1.89; 1.88 shown failing | STEP-10 onward | 1.89 green |
| Packaging | `cargo package --locked`; dry run; contents assertion | STEP-10 onward | Green; nothing forbidden |
| CI | New jobs in `ci.yml` | STEP-11 onward | Green and required by `publish.yml` |
| Registries | PyPI digests and attestations; crates.io digest, docs.rs, scratch project | STEP-14, STEP-17 | Match the gated candidate |
| Re-review | Independent review of `v2.0.0..v2.1.0rc1` | STEP-15 | No Critical or Major |

## 14. Acceptance criteria

- [ ] `PLAN-00009-AC-01` `aes` is 0.9 with the lock diff limited to the AES stack, and the FIPS 197 KAT, PRF equality and full dual-backend suite are bit-exact; PR #7 is closed with a link to STEP-01 and STEP-02.
- [ ] `PLAN-00009-AC-02` `num-bigint` is 0.5.1, the equivalence sweep and full suite are green, and the recorded benchmark passes D15, or an escalation is recorded and 0.4.8 retained.
- [ ] `PLAN-00009-AC-03` A released `memoryview` as key, default tweak or per-call tweak raises the matching `FF1Error` subclass on both backends; `test_tweak_sensitivity` and both concurrency tests are shown to fail against deliberately broken implementations.
- [ ] `PLAN-00009-AC-04` `fpr-ff1` has no `pyo3` in `cargo tree`, no third-party type in any public signature documented without `internal`, and the wheel's file list is unchanged.
- [ ] `PLAN-00009-AC-05` Every validation rule is enforced in the crate and covered by a rejection test, with redacted messages.
- [ ] `PLAN-00009-AC-06` The public API is documented, doctests pass, `cargo doc` has no warnings, and the type is `Send + Sync`.
- [ ] `PLAN-00009-AC-07` The crate's tests reproduce the NIST samples, intermediates, AES vectors, frozen vectors, property and bijectivity suites from the existing JSON files, and the float scan fails on a deliberate float.
- [ ] `PLAN-00009-AC-08` The shared case file is consumed by both suites, covers every error kind, and a deliberate divergence fails exactly one suite.
- [ ] `PLAN-00009-AC-09` The contract test checks all three manifests and their `publish` flags and fails on drift.
- [ ] `PLAN-00009-AC-10` The package declares `rust-version = "1.89"` and `MIT OR Apache-2.0` with both licence files; it builds and tests on 1.89 and is shown to fail on 1.88; `cargo package --locked` and the dry run are green; the contents assertion passes and fails on a forbidden path.
- [ ] `PLAN-00009-AC-11` The crate's CI jobs, including the 1.89 MSRV leg, are green and required by `publish.yml`, and the `publish-crate` job is skipped for a pre-release.
- [ ] `PLAN-00009-AC-12` The maintained documents describe both artifacts, the `internal` feature's status and the publishing sequence, with no stronger claims for the crate.
- [ ] `PLAN-00009-AC-13` `2.1.0rc1` is on PyPI from a tag on a `main` merge commit, with digests and attestations verified.
- [ ] `PLAN-00009-AC-14` `fpr-ff1` `2.1.0-rc1` is on crates.io, its `.crate` digest equals CI's, docs.rs built it, a scratch project reproduces a NIST vector and a `d > 16` case, the bootstrap token is recorded as revoked, and the Trusted Publisher is configured.
- [ ] `PLAN-00009-AC-15` An independent re-review of `v2.0.0..v2.1.0rc1` exists with no Critical or Major finding, and every finding is dispositioned.
- [ ] `PLAN-00009-AC-16` `2.1.0` is on PyPI and crates.io from `v2.1.0` on a `main` merge commit, the crate published by the CI job through Trusted Publishing.
- [ ] `PLAN-00009-AC-17` The handoff record and recovery procedure for both registries are in the work log, and `docs/backlog.md` records plan 00009 as completed.

## 15. Risks and mitigations

| Risk | Likelihood | Impact | Mitigation or test | Owner/step |
|---|---|---|---|---|
| The AES upgrade changes output | Low | High | FIPS 197 KAT, PRF equality, per-round intermediates before anything else changes | Builder/STEP-01 |
| `num-bigint` 0.5 is slower or behaves differently | Medium | Medium | Equivalence sweep; park rule; 0.4.8 fallback | Builder/STEP-02 |
| A third-party type leaks into the public API | Medium | High | Boundary drawn in the split; checked with `cargo doc` without `internal`; `cargo-semver-checks` afterwards | Builder/STEP-04, STEP-11 |
| The `internal` feature is mistaken for public API | Medium | Low | `#[doc(hidden)]`, non-default, documented as outside semver in `AGENTS.md` and the crate README | Builder/STEP-04, STEP-12 |
| The manual bootstrap publishes something CI did not build | Low | High | Upload the CI-built `.crate` after comparing SHA-256; verify on crates.io afterwards | Owner/STEP-14 |
| The bootstrap token outlives its use | Low | High | Scoped to `publish-new` for one crate; revoked immediately; revocation recorded | Owner/STEP-14 |
| MSRV is still wrong | Low | Medium | 1.89 derived from the code and every dependency; build on 1.89 and a failing 1.88 build recorded | Builder/STEP-10 |
| A crate-only fix later forces a Python release | Medium | Medium | Accepted consequence of lock-step (D1) | User/D1 |
| Two validation layers drift | Medium | High | The case file is the gate | Builder/STEP-08 |
| Registry versions are immutable | Certain | Medium | Dry runs, digest checks and a pre-release before the stable version | Builder/STEP-10 to STEP-14 |

## 16. Builder hand-off

- **Start condition:** User approval; plan 00007's closeout merged into `main` by PR; Dependabot #10 and #11 merged or explicitly left open by the owner; a clean worktree on a branch from `main`.
- **First step:** PLAN-00009-STEP-01.
- **Required sequence:** STEP-01 → STEP-02 → STEP-03 → STEP-04 → STEP-05 → STEP-06 → STEP-07 → STEP-08 → STEP-09 → STEP-10 → STEP-11 → STEP-12 → STEP-13 → STEP-14 → STEP-15 → STEP-16 → STEP-17. STEP-03 is independent of STEP-01/02; STEP-09 depends only on STEP-04.
- **Parallel-safe work:** STEP-03 alongside STEP-01/02.
- **Do not change:** accepted inputs, ciphertext, the Python public API or default backend; plan 00003 D3 and D4; the coverage floor; the Rust-free `just quality`. No FF3/FF3-1, key management, new Python runtime dependency, `unsafe`, shared state or float in an FF1 path. Do not publish the binding crate. Do not store a crates.io token anywhere. No tag, push, merge, PR closure or publication without per-action authorization.
- **Escalate when:** an AES or conversion divergence; a park-rule failure; a third-party type that cannot be kept out of a public signature; the crate needing more than Rust 1.89; a validation rule inexpressible without floats or in one language; a digest mismatch between CI and a registry; a Critical or Major review finding.
- **Completion hand-off:** `2.1.0` on PyPI and crates.io from `v2.1.0` on `main`, the crate published by CI, both verified, handoff and recovery recorded.

<!-- BUILDER_WORK_LOG_START -->
## 17. Builder Work Log

> [!warning] Builder-maintained section
> Delivery Planner creates this section. After approval, Builder may update only
> this delimited section and the Builder-maintained front-matter fields. Builder
> must preserve prior entries and use UTC timestamps.

### Step status

| Step | Status | Started (UTC) | Completed (UTC) | Evidence | Builder notes |
|---|---|---|---|---|---|
| PLAN-00009-STEP-01 | completed | 2026-09-26T16:46:28Z | 2026-09-26T16:46:28Z | Commit (this one); checkpoint-163734; cargo audit clean | Closing PR #7 deferred to after STEP-02 (authorization pending) |
| PLAN-00009-STEP-02 | completed | 2026-09-26T16:57:05Z | 2026-09-26T16:57:05Z | Commit (this one); park rule passed; checkpoint-164751 | No API adaptation needed; performance unchanged |
| PLAN-00009-STEP-03 | completed | 2026-09-26T17:07:11Z | 2026-09-26T17:07:11Z | Commit (this one); red probes recorded; checkpoint-165857 | No change to accepted inputs or ciphertext; the only behaviour change narrows an already-rejected input to the documented exception |
| PLAN-00009-STEP-04 | completed | 2026-09-26T17:19:01Z | 2026-09-26T17:19:01Z | Commit (this one); checkpoint-171023; wheel identity check | engine.rs is the former lib.rs; use git log -C --follow / git blame -C for its history |
| PLAN-00009-STEP-05 | completed | 2026-09-26T17:30:12Z | 2026-09-26T17:30:12Z | Commit (this one); checkpoint-172153 | Error modelled as struct + ErrorKind (see Deviations) |
| PLAN-00009-STEP-06 | completed | 2026-09-26T17:41:32Z | 2026-09-26T17:41:32Z | Commit (this one); checkpoint-173259 | Alphabet kept private (see Deviations) |
| PLAN-00009-STEP-07 | completed | 2026-09-26T17:54:52Z | 2026-09-26T17:54:52Z | Commit (this one); probes recorded; checkpoint-174537 | Bijectivity sweeps gated #[ignore]; STEP-11 must run them in CI with --release -- --ignored |
| PLAN-00009-STEP-08 | completed | 2026-09-26T18:05:36Z | 2026-09-26T18:05:36Z | Commit (this one); divergence probe recorded; checkpoint-175654 | Cases carry exact messages as well as kinds, which is stricter than REQ-08 requires |
| PLAN-00009-STEP-09 | completed | 2026-09-26T18:14:34Z | 2026-09-26T18:14:34Z | Commit (this one) | — |
| PLAN-00009-STEP-10 | completed | 2026-09-26T18:27:32Z | 2026-09-26T18:27:32Z | Commit (this one); checkpoint-181841; clean-tree package digest recorded after commit | MSRV 1.89 proven; packaged-test limitation documented |
| PLAN-00009-STEP-11 | completed | 2026-09-26T18:30:21Z | 2026-09-26T20:37:39Z | f3301e3; CI run 36269172052 green 41/41; .crate reproducible | The pre-release skip of publish-crate is evidenced at STEP-14 (release event only) |
| PLAN-00009-STEP-12 | completed | 2026-09-26T20:39:40Z | 2026-09-26T20:39:40Z | Commit (this one) | No document implies the crate is the reference or carries stronger claims |
| PLAN-00009-STEP-13 | completed | 2026-09-26T20:49:15Z | 2026-09-26T21:41:28Z | c06cc3f; local gate; CI run 36272767880 green 41/41 | Tag goes on the PR merge commit on main; the bootstrap digest is checked at that commit (see Deviations) |
| PLAN-00009-STEP-14 | blocked | 2026-09-26T21:41:28Z | — | Both registries verified; token revocation and Trusted Publisher recorded on the owner's statement | Waiting on owner: the D14 soak statement |
| PLAN-00009-STEP-15 | not-started | — | — | — | — |
| PLAN-00009-STEP-16 | not-started | — | — | — | — |
| PLAN-00009-STEP-17 | not-started | — | — | — | — |

Allowed status values: `not-started`, `in-progress`, `blocked`, `completed`,
`skipped`. A skipped step requires explicit user approval recorded in Evidence.

### Execution log

| Timestamp (UTC) | Step | Event | Evidence or reference | Next action |
|---|---|---|---|---|
| 2026-09-26T16:28:46Z | — | Builder started on approved plan 00009 (approval commit ab95fd6) on release/v2.1, branched from main 62c6115 | git status clean; plan 00007 closeout (PR #13) and Dependabot #10, #11 merged into main | Baseline, then STEP-01 |
| 2026-09-26T16:46:28Z | PLAN-00009-STEP-01 | Evidence first at baseline: tests/test_rust_aes_validation.py (FIPS 197 KAT + PRF equality) 19 passed with aes 0.8.4 | Baseline checkpoint-162846 green | Upgrade |
| 2026-09-26T16:46:28Z | PLAN-00009-STEP-01 | aes 0.8 -> 0.9 in rust/fpr-ff1-rust/Cargo.toml; cargo update -p aes; applied PR #7's two API migrations only: BlockEncrypt -> BlockCipherEncrypt, Block::clone_from_slice -> Block::from (in prf and cipher_block) | Lock diff limited to the AES stack: aes 0.8.4->0.9.3, cipher 0.4.4->0.5.2, crypto-common 0.1.7->0.2.2, inout 0.1.4->0.2.2, cpufeatures 0.2.17->0.3.1; added cpubits 0.1.1, hybrid-array 0.4.15; removed generic-array 0.14.7, cfg-if 1.0.4, version_check 0.9.5 (build dependency of generic-array). Build: no warnings | Checkpoint |
| 2026-09-26T16:57:05Z | PLAN-00009-STEP-02 | Evidence first: just bench with num-bigint 0.4.8 (aes 0.9.3 already in place), 2026-09-26T16:46:37Z, load 2.40; same machine as plan 00007 STEP-05 (AMD Ryzen AI Max+ PRO 395, CPython 3.12.13, rustc 1.98.1) | Backend table python/rust µs/op: r10 n6 28.2/4.5; n100 108.9/38.1; n1000 940.8/390.1; n5000 5167.4/2109.9; n20000 26615.9/9689.6. r256 n100 139.5/50.3; n1000 2521.2/206.4; n5000 12866.6/1028.0; n20000 51800.6/4056.7 | Upgrade |
| 2026-09-26T16:57:05Z | PLAN-00009-STEP-02 | num-bigint 0.4 -> 0.5 in rust/fpr-ff1-rust/Cargo.toml; cargo update -p num-bigint | Lock diff: num-bigint 0.4.8 -> 0.5.1 only. No source change needed: every call site (BigUint::from, to_bytes_be, from_bytes_be, pow, div_rem, bits, iter_u32_digits) compiles unchanged, no warnings | Checkpoint and benchmark |
| 2026-09-26T17:07:10Z | PLAN-00009-STEP-03 | (a) Tests first: released memoryview as key, default tweak, per-call tweak (encrypt and decrypt), both backends, plus a live-view acceptance test. Before the fix: 8 failed with 'ValueError: operation forbidden on released memoryview object'. Fix: _require_bytes catches ValueError around bytes() only (bytes/bytearray cannot raise it) and raises the caller's error class with '<name> memoryview has been released'. After: 16 passed | tests/test_validation.py; src/fpr_ff1/_ff1.py _require_bytes | (b) |
| 2026-09-26T17:07:10Z | PLAN-00009-STEP-03 | (b) test_tweak_sensitivity now draws four unique tweaks and asserts at least one of three alternatives changes the ciphertext. Red probe (not committed): _prepare patched to return self._default_tweak (tweak ignored) -> new test FAILED 'four distinct tweaks produced identical ciphertext; the tweak is being ignored'; the OLD test against the same broken code: '1 skipped' (could not fail). Probe reverted (grep PROBE = 0); new test passes on the real code | tests/test_properties.py | (c) |
| 2026-09-26T17:07:11Z | PLAN-00009-STEP-03 | (c) Both concurrency tests keep every iteration's result and check each against the serial expectation. Red probe (not committed): a pytest plugin wrapping FF1.encrypt_numerals to corrupt exactly one mid-run result (call 30) -> new test FAILED 'thread 1 iteration 1 diverged from the serial result'; the OLD test with the same corruption: '1 passed'. Changelog [Unreleased] gains the exception-type fix, the two test fixes, and the STEP-01/02 dependency upgrades | tests/test_thread_safety.py; CHANGELOG.md; probe plugin in the session scratchpad | Checkpoint |
| 2026-09-26T17:19:01Z | PLAN-00009-STEP-04 | Before-state recorded: maturin wheel fpr_ff1-2.0.0-cp312-abi3-manylinux_2_34_x86_64.whl (10 entries); _rs.__version__ 2.0.0; exports _test_cipher_block, _test_encrypt_traced, _test_prf, decrypt_numerals, encrypt_numerals | scratchpad step04/before-files.txt, before-rs.txt | Split |
| 2026-09-26T17:19:01Z | PLAN-00009-STEP-04 | Split: git mv rust/fpr-ff1-rust/src/lib.rs -> rust/fpr-ff1/src/engine.rs (PyO3 imports and the #[pymodule] block removed) and src/tests.rs -> rust/fpr-ff1/src/tests.rs; new rust/fpr-ff1 crate (package fpr-ff1, lib fpr_ff1, rlib, MIT OR Apache-2.0, feature 'internal'); engine is a private module, so every item is unreachable outside the crate; #[cfg(feature = "internal")] #[doc(hidden)] pub mod __internal re-exports ff1, ff1_traced, TraceRecord, prf_with_key, cipher_block_with_key; fpr-ff1-rust keeps cdylib, publish = false, _fpr_ff1_rs, and holds only the #[pymodule] block, depending on fpr-ff1 with features = ["internal"]; workspace members [fpr-ff1, fpr-ff1-rust]. Aes enum widened from private to pub(crate) (same reach as before: it was private at the crate root) | Build, clippy -D warnings (workspace and fpr-ff1 alone): no warnings | Checkpoint |
| 2026-09-26T17:30:11Z | PLAN-00009-STEP-05 | Tests first: rust/fpr-ff1/src/validate_tests.rs (14 tests: key lengths 0/15/17/23/25/31/33/64; radix 0/1/65536/u32::MAX; min_length table incl. 999->3 and 1000->2; length min and 2**32 ceiling; numerals by position; tweak-bound ceilings and min>max; tweak ceiling first then min/max; literal zero maximum; alphabet length by scalar value and duplicates; decode by position; alphabet-required; Error is std::error::Error + Send + Sync). Red: E0432 unresolved crate::validate and crate::{Error, ErrorKind} | cargo test -p fpr-ff1 compile failure | Implement |
| 2026-09-26T17:30:11Z | PLAN-00009-STEP-05 | Implemented error.rs (pub struct Error { kind, message } with kind(), Display and core::error::Error; #[non_exhaustive] pub enum ErrorKind { KeyLength, Radix, Length, ValueRange, TweakLength, Alphabet, AlphabetRequired }, one per Python exception class, AlphabetRequired = base FF1Error) and validate.rs (key, radix, min_length by integer multiplication, length, numerals, tweak_bounds, tweak, alphabet, decode, alphabet_required), in the Python order and with the Python messages; messages give positions and lengths, never values, key bytes or characters | 30 passed (16 existing + 14 new) | Checkpoint |
| 2026-09-26T17:41:32Z | PLAN-00009-STEP-06 | Tests first: rust/fpr-ff1/tests/api.rs (9 integration tests seeing only the public API: NIST sample 1 numerals and sample 2 string interface, per-call vs default tweak and empty == absent, length accessors, construction order key->radix->bounds->default tweak->alphabet, call order length->tweak->numerals, alphabet-required and unknown character, literal zero maximum, Send + Sync). Red: E0432 unresolved fpr_ff1::FF1 | cargo test --test api compile failure | Implement |
| 2026-09-26T17:41:32Z | PLAN-00009-STEP-06 | Implemented rust/fpr-ff1/src/ff1.rs: pub struct FF1 (Clone; Debug omits the key), FF1::new(key, radix), FF1::builder(key, radix) -> Builder { alphabet, tweak, min_tweak_len, max_tweak_len, build }, encrypt_numerals/decrypt_numerals(&[u16], Option<&[u8]>), encrypt/decrypt(&str, Option<&[u8]>), min_length() -> usize, max_length() -> u64. Validation in the Python order before engine::ff1; the core's own Result is unwrapped with an invariant message because every condition it can refuse is rejected first. Alphabet kept crate-private. rust/fpr-ff1/README.md written and used as the crate-root docs via include_str!, so its three examples run as doctests. The temporary dead_code allows from STEP-04/05 removed; instead prf_with_key is compiled for tests or 'internal', cipher_block_with_key and ff1_traced only for 'internal', and TraceRecord's fields allowed unread without 'internal' | Unit 30, integration 9, doctests 3 passed | Checkpoint |
| 2026-09-26T17:54:52Z | PLAN-00009-STEP-07 | Conformance suite added as crate unit tests (rust/fpr-ff1/src/conformance_tests.rs, property_tests.rs), reading tests/vectors/*.json at runtime: 9 NIST samples both directions via the public string API; per-round intermediates (i, P, Q, R, S, y, m, c, C, and u, v, b, d) for all 10 rounds of all 9 samples via the trace hook; 3 FIPS 197 AES vectors; 46 frozen oracle vectors both directions via the public API, with max d > 16 asserted; power-of-two radices 2..256 round trip with b checked against an independent exact computation; b-from-v and Q padding/alignment; a float scan of engine.rs, validate.rs, ff1.rs, error.rs, lib.rs; proptest (64 cases each) round trip with length and range, determinism, tweak sensitivity (4 unique tweaks), key sensitivity (one flipped bit); exhaustive bijectivity for radix 2 n=20 and radix 10 n=6, #[ignore] by default. Dev-dependencies serde_json 1 (arbitrary_precision) and proptest 1 (std only); cipher_block_with_key and ff1_traced now compiled for tests too | cargo test -p fpr-ff1: 41 passed, 2 ignored; cargo test --release -- --ignored: both sweeps passed in 7.56s | Red probes |
| 2026-09-26T17:54:52Z | PLAN-00009-STEP-07 | Two defects in the new test helpers, fixed before any result was relied on: (1) the AES-192 key in nist_ff1_intermediates.json carries an embedded line break from its transcription; the Python suite reads it with bytes.fromhex, which skips whitespace, so the Rust decoder now skips ASCII whitespace the same way (the fixture is not edited); (2) the frozen radix-62 vectors use a non-ASCII alphabet starting at U+10000, and the test's numeral mapping used str::find byte offsets; now by character position. The crate's own alphabet handling was already correct: both public-API assertions for those vectors passed before the helper failed | No change to fixtures or to crate code | Red probes |
| 2026-09-26T18:05:36Z | PLAN-00009-STEP-08 | Case file first: tests/vectors/validation_cases.json, 53 cases written from the Python rules (key lengths, radix, bounds incl. ceilings and min>max, default tweak, alphabet length/duplicates/non-ASCII, lengths by side incl. min_length at radix 2/999/1000, numerals by position incl. radix 65535, call tweaks incl. literal zero maximum, string interface, and six cross-check ordering cases), each with the expected Python class and exact message; one python_only case (released memoryview key) with its reason. tests/test_validation_cases.py passed on both backends before any Rust harness existed | 108 passed (53 x 2 backends + 2 coverage/meta tests); every FF1Error subclass except BackendError covered | Rust harness |
| 2026-09-26T18:05:36Z | PLAN-00009-STEP-08 | Rust harness rust/fpr-ff1/src/validation_case_tests.rs: builds each case through the public builder, runs the call, maps ErrorKind to the Python class with an exhaustive match (a new variant fails to compile until mapped), compares class and exact message; skips only python_only cases and asserts exactly one such; a second test requires a case for every ErrorKind | 2 passed; 52 cases run, 1 python_only skipped | Divergence probe |
| 2026-09-26T18:14:34Z | PLAN-00009-STEP-09 | tests/test_contract.py: test_crate_version_matches_project_version parametrized over rust/fpr-ff1/Cargo.toml and rust/fpr-ff1-rust/Cargo.toml; new test_only_the_library_crate_is_publishable (fpr-ff1 publishable, fpr-ff1-rust publish = false, names pinned). Reads TOML only; runs without a Rust toolchain | 3 passed | Red-then-green |
| 2026-09-26T18:27:32Z | PLAN-00009-STEP-10 | Evidence first: cargo package --list before metadata (16 entries, no licence files); Rust 1.88 and 1.89 installed with rustup (minimal profile). cargo +1.88 build -p fpr-ff1 --locked: refused, 'rustc 1.88.0 is not supported by the following package: aes@0.9.3 requires rustc 1.89'. cargo +1.89 test -p fpr-ff1 --locked: 43 unit + 9 integration + 3 doctests passed | D8 floor proven, not assumed | Metadata |
| 2026-09-26T18:27:32Z | PLAN-00009-STEP-10 | rust/fpr-ff1/Cargo.toml: rust-version 1.89, description, homepage, documentation (docs.rs), readme, keywords [ff1, fpe, format-preserving, encryption, sp800-38g], categories [cryptography], explicit include list, [package.metadata.docs.rs] with no features (never 'internal'). LICENSE-MIT copied from the repository LICENSE; LICENSE-APACHE is the canonical https://www.apache.org/licenses/LICENSE-2.0.txt verbatim (sha256 cfc7749b96f63bd31c3c42b5c471bf756814053e847c10f3eb003417bc523d30). Fixture access moved to src/test_fixtures.rs: outside the repository fixture tests skip; with FPR_FF1_REQUIRE_FIXTURES set they fail; the switch is set in just rust-test and the CI rust-conformance job. .github/scripts/assert_crate_contents.py: cargo package --list checked against an allow-list, forbidden patterns (agent files, docs, .github, target, Python, native libraries, fixtures) and required files; only --allow-dirty accepted as an argument | package list: 19 entries | Probes |
| 2026-09-26T18:30:06Z | PLAN-00009-STEP-11 | ci.yml: crate-test (ubuntu/macos/windows: cargo test -p fpr-ff1 --locked, then --release -- --ignored for the bijectivity sweeps; FPR_FF1_REQUIRE_FIXTURES=1), crate-msrv (cargo +1.89 test, plus a check that Cargo.toml declares 1.89), crate-package (cargo doc -D warnings; assert_crate_contents.py; cargo package and publish --dry-run --locked; sha256 of the .crate; .crate uploaded as artifact 'crate'; cargo-semver-checks 0.50.0 --default-features against the last published version, skipped while crates.io returns 404). publish.yml: publish-crate needs [quality, publish], runs only for non-prerelease releases, environment crates-io, id-token: write, tag == v<crate version> check, rust-lang/crates-io-auth-action pinned to v1.0.5 c6f97d42243bad5fab37ca0427f495c86d5b1a18, cargo publish --locked -p fpr-ff1. justfile: crate-test, crate-msrv, crate-package | actionlint 1.7.12 clean on both workflows | Local runs and probes |
| 2026-09-26T20:20:42Z | PLAN-00009-STEP-11 | User authorized the push and closing PR #7 ('Push authorised to complete STEP-11. Yes, close PR #7.'). Builder pushed release/v2.1 (new branch, 5a6ca38), closed Dependabot PR #7 with a comment linking 126ece6 and c1f5a79, and dispatched ci.yml | origin/release/v2.1 = 5a6ca385edb400df87c4193286ef81eefc4ed40f; PR #7 state CLOSED; run https://github.com/joelee/fpr-ff1/actions/runs/36269172052 | Watch the run; iterate to green |
| 2026-09-26T20:37:39Z | PLAN-00009-STEP-11 | Environment check: the owner created the GitHub environment crates-io (2026-09-26T20:24:14Z); like pypi it has no protection rules or deployment policy. Builder gave hardening guidance (restrict to v* tags; optional required reviewer) and the crates.io Trusted Publisher fields to enter after the bootstrap (joelee / fpr-ff1 / publish.yml / crates-io) | gh api repos/joelee/fpr-ff1/environments | STEP-12 |
| 2026-09-26T20:39:40Z | PLAN-00009-STEP-12 | Documentation for two artifacts: README (roadmap row 2.1; a Rust section with a usage example, lock-step, MSRV, the shared case file, 'the pure-Python implementation remains the reference'; the licence section explaining MIT for the package and MIT OR Apache-2.0 for rust/fpr-ff1 with the MIT option covering the wheels; the crate README in the documentation list). SECURITY.md (policy covers both artifacts; reports name the artifact; the crate follows the support table from 2.1.0; the crate makes no zeroization claim). AGENTS.md (crate recipes; test rule 11 for shared validation cases; fixtures never copied into the crate and FPR_FF1_REQUIRE_FIXTURES; licence; three-file version rule; a paragraph on the crate: public API FF1/Builder/Error/ErrorKind only, no third-party types, hidden 'internal' feature outside semver, duplicated validation, Python remains the reference, MSRV 1.89). CLAUDE.md (crate recipes; three manifests). docs/architecture.md (system context with the crate; module entry; a 'Two validation layers' section; conversion table now names engine.rs). docs/directory-structure.md (rust/ tree for both crates). docs/developer-guide.md (crate recipes; the binding over the core; rust-test requires fixtures; three-file bump; a 'The Rust crate' section with the CI jobs, reproducible .crate and the bootstrap-then-Trusted-Publishing sequence). docs/backlog.md (plan 00009 in progress, superseding 00008; deferred no_std and zeroization) | 8 files, +106/-23 | Verify |
| 2026-09-26T20:49:15Z | PLAN-00009-STEP-13 | Contract test red after bumping pyproject.toml alone (both crate manifests '2.0.0' vs '2.1.0rc1'), green after both crates moved to 2.1.0-rc1 (3 passed). uv lock and cargo build moved only the three project version lines; uv lock --check clean; Cargo.lock stable under --locked. CHANGELOG [2.1.0rc1] dated 2026-09-26 (Added: the crate, its conformance evidence, shared validation cases, crate CI; Changed: aes and num-bigint; Fixed: review 00011 Lows; Unchanged), links [Unreleased] -> v2.1.0rc1...HEAD and [2.1.0rc1] -> v2.0.0...v2.1.0rc1. Committed as c06cc3f | Red/green output recorded above | Gate the candidate |
| 2026-09-26T21:23:52Z | PLAN-00009-STEP-13 | User authorized the push ('Push authorised.'). Builder pushed release/v2.1 (5a6ca38..0294db7) and dispatched ci.yml | origin/release/v2.1 = 0294db75cca154b9d9e5f0ebcd6b21a96678d34d; run https://github.com/joelee/fpr-ff1/actions/runs/36272767880 | Record the run; hand off for STEP-14 |
| 2026-09-26T21:41:28Z | PLAN-00009-STEP-14 | Hand-off to owner. (1) PR release/v2.1 -> main, merged with a MERGE COMMIT. (2) Tag exactly v2.1.0rc1 on that merge commit; publish a GitHub PRE-RELEASE; publish.yml publishes to PyPI, and publish-crate must show as skipped. (3) Crate bootstrap from a clean checkout of the tag: cargo package --locked -p fpr-ff1, confirm its sha256 equals the 'crate' artifact of the release's publish run; create a crates.io token scoped to publish-new for crate fpr-ff1 with a short expiry; CARGO_REGISTRY_TOKEN=<token> cargo publish --locked -p fpr-ff1 --manifest-path rust/Cargo.toml (repackages identically, since cargo package is reproducible); revoke the token and say so. (4) Add the crates.io Trusted Publisher: joelee / fpr-ff1 / publish.yml / crates-io. Then Builder verifies PyPI, crates.io (checksum vs the CI artifact), docs.rs and a scratch project; owner states the soak | Frozen candidate: origin/release/v2.1 at 0294db7 | Owner release actions |
| 2026-09-26T23:59:33Z | PLAN-00009-STEP-14 | Owner merged PR #14 (release/v2.1 -> main) as merge commit d3f1f97, tagged v2.1.0rc1 on it, and published a GitHub pre-release (2026-09-26T23:41:29Z) with the Builder's notes | tag v2.1.0rc1 -> d3f1f97 = origin/main head; pyproject version 2.1.0rc1 at the tag | Verify publish run; crate bootstrap |
| 2026-09-27T00:12:22Z | PLAN-00009-STEP-14 | Owner stated: 'Crate published to crates.io and token revoked. Truster Publisher created.' The owner bootstrapped fpr-ff1 2.1.0-rc1 on crates.io with a scoped token, revoked the token, and configured the crates.io Trusted Publisher (joelee/fpr-ff1, publish.yml, environment crates-io). Token revocation and the Trusted Publisher configuration rest on the owner's statement: neither is visible through crates.io's unauthenticated API. The Trusted Publisher is proven in use at STEP-17, when publish-crate publishes 2.1.0 | crates.io: fpr-ff1 2.1.0-rc1 published_by joelee, trustpub_data null (a token publish, as expected for the bootstrap) | Builder verification of both registries |

### Deviations and blockers

| Timestamp (UTC) | Step | Deviation or blocker | Impact | Decision required from |
|---|---|---|---|---|
| 2026-09-26T16:46:28Z | PLAN-00009-STEP-01 | Task 4 (close Dependabot PR #7 with a comment) is an outward action; no per-action authorization recorded yet. Deferred until STEP-02 lands so the closing comment can link both commits | None on the code; #7 stays open meanwhile | User: authorize closing PR #7 after STEP-02 |
| 2026-09-26T17:19:01Z | PLAN-00009-STEP-04 | The split broke 'cargo fmt --check --manifest-path rust/Cargo.toml' (just rust-lint and the CI rust-conformance job): with a virtual manifest and more than one package, cargo-fmt selects only packages whose manifest equals the given path, finds none, and exits 1 with 'Failed to find targets'. Fixed with --all in justfile and ci.yml in this commit, ahead of STEP-11, so the tree and CI are never broken. AGENTS.md and CLAUDE.md named the core's old path (rust/fpr-ff1-rust/src/lib.rs); updated here per docs/AGENTS.md (document updated in the change that makes it true). Temporary #[cfg_attr(not(feature = "internal"), allow(dead_code))] on mod engine until STEP-06's public API calls into it | Small scope additions to STEP-04, each forced by the split; broader documentation remains STEP-12 | None |
| 2026-09-26T17:30:12Z | PLAN-00009-STEP-05 | REQ-05 asks for 'a non-exhaustive enum ... implementing core::error::Error'. Implemented as std::io::Error does: a struct Error implementing core::error::Error and Display, whose kind() returns the non-exhaustive ErrorKind enum with the six Python-mirroring variants plus AlphabetRequired. Messages then match Python's exactly and can be reworded without a breaking change. The validation functions are pub(crate) and called only by tests until STEP-06 builds the public API on them (temporary allow(dead_code) outside test builds, removed at STEP-06) | Same kinds and messages as specified; API shape differs slightly from a bare enum | None; recorded for the re-review |
| 2026-09-26T17:41:32Z | PLAN-00009-STEP-06 | D10 lists 'its alphabet type' among the types the public API may expose. Kept crate-private instead: the builder takes the alphabet as &str, so no public alphabet type is needed, and a smaller public surface is a smaller semver obligation. The type is named FF1 (not Ff1) for parity with the Python package; clippy raises no upper_case_acronyms warning | Public API is FF1, Builder, Error, ErrorKind only | None; recorded for the re-review |
| 2026-09-26T17:54:52Z | PLAN-00009-STEP-07 | The plan's evidence item 'a deliberate S-expansion break fails the intermediates' cannot hold: none of the nine NIST samples reaches d > 16, so the NIST intermediates never execute the step 6.iii expansion (the core's own comments say so). Probe 2 confirmed it: the break passes both NIST suites and is caught by the frozen oracle vectors, which include d > 16. The intermediates' teeth were demonstrated with a break they can see (probe 3, b from u) | Evidence reworded, not weakened: each suite shown to catch what it can see | None; recorded for the re-review |
| 2026-09-26T18:27:32Z | PLAN-00009-STEP-10 | Fixtures cannot be packaged (Cargo includes only files under the crate directory) and copying them would duplicate the conformance evidence, which plans 00008/00009 say to escalate rather than do. Chose the gate the plan offers ('packaged tests gated'), modelled on FPR_FF1_REQUIRE_ORACLE. Limitation: libtest hides a passing test's output, so in the packaged crate the skip notice is not visible and fixture tests pass vacuously unless FPR_FF1_REQUIRE_FIXTURES=1; stated in the crate README's Testing section. In the repository and CI the switch is always set | Downstream packagers running cargo test on the published crate get the API, validation, property and doc tests, not the fixture-backed conformance tests | None; recorded for the re-review |
| 2026-09-26T18:30:06Z | PLAN-00009-STEP-11 | The publish-crate job's 'skipped for a pre-release' behaviour depends on GitHub's release event and cannot be exercised locally; it will be evidenced by the v2.1.0rc1 publish run at STEP-14. The job uses a GitHub environment named crates-io, which the owner should create (with any protection rules) and name in the crates.io Trusted Publisher configuration | One acceptance item (AC-11: skipped for a pre-release) moves its evidence to STEP-14 | Owner: create the crates-io environment before STEP-14 |
| 2026-09-26T18:30:21Z | PLAN-00009-STEP-11 | BLOCKER: task 4 needs release/v2.1 pushed so the new jobs run in CI (the branch has never been pushed). Pushing is an outward action with no authorization recorded. Also pending since STEP-01: closing Dependabot PR #7 with a comment linking 126ece6 (aes 0.9) and c1f5a79 (num-bigint 0.5) | STEP-11 cannot complete; STEP-12 onward wait, per the required sequence | User: authorize 'git push -u origin release/v2.1' (Builder then dispatches ci.yml and iterates to green), and closing PR #7 |
| 2026-09-26T20:49:15Z | PLAN-00009-STEP-13 | Plan STEP-14 task 2 says to confirm the downloaded .crate's SHA-256 'equals STEP-13's'. That cannot hold: the .crate embeds the commit hash (.cargo_vcs_info.json, shown at STEP-11), and the release convention tags the PR merge commit on main, not c06cc3f. The digest that matters is the crate built at the tagged commit: compare the artifact from the release run's crate-package job against a local 'cargo package --locked' at the tag (reproducible, proven byte-identical at STEP-11), and upload exactly that file | Same guarantee (publish exactly what CI built at the tag), different reference digest | None; the STEP-14 hand-off will state the corrected procedure |
| 2026-09-26T20:49:15Z | PLAN-00009-STEP-13 | BLOCKER: task 2 needs CI green at the candidate commit, which needs release/v2.1 pushed again (the STEP-11 push authorization covered that step only) | STEP-13 cannot complete; STEP-14 waits | User: authorize pushing release/v2.1 for STEP-13 (Builder then dispatches ci.yml and records the run) |

### Verification results

| Timestamp (UTC) | Step | Command or check | Result | Evidence |
|---|---|---|---|---|
| 2026-09-26T16:37:02Z | Baseline | Checkpoint at 88bd449+work log: static; just backend-dev; just rust-test; just rust-lint; full dual-backend gate; just quality Rust-free | Pass | pyright 1.1.414 (Dependabot #11) 0 errors; 1688 passed in 259.28s, 100%, -k rust 576/1688; Rust-free 872 passed, 245 skipped, 100%; rustc 1.98.1; logs checkpoint-162846 |
| 2026-09-26T16:46:28Z | PLAN-00009-STEP-01 | Full checkpoint with aes 0.9.3; then tests/test_rust_aes_validation.py, test_intermediates.py, test_nist_vectors.py, test_frozen_kat.py, test_backend_agreement.py with FPR_FF1_REQUIRE_RUST_BACKEND=1 | Pass (bit-exact) | 1688 passed in 266.27s, 100%, -k rust 576; Rust-free 872 passed, 100%; cargo test and clippy -D warnings green; AES/conformance modules 336 passed (FIPS 197 KAT, PRF equality with the Python path, per-round intermediates, NIST, frozen KAT incl. d > 16, backend agreement); logs checkpoint-163734 |
| 2026-09-26T16:46:28Z | PLAN-00009-STEP-01 | cargo-audit 0.22.2 (CI pin) on rust/Cargo.lock | Pass | exit 0, 27 crate dependencies, no advisories |
| 2026-09-26T16:57:05Z | PLAN-00009-STEP-02 | cargo test (includes every_supported_radix_is_equivalent_above_the_threshold and the power-of-two chunk sweep); full checkpoint | Pass | cargo test 16 passed; dual gate 1688 passed in 257.40s, 100%, -k rust 576; Rust-free 872 passed, 100%; logs checkpoint-164751 |
| 2026-09-26T16:57:05Z | PLAN-00009-STEP-02 | just bench with num-bigint 0.5.1, 2026-09-26T16:55:51Z, load 1.50; park rule D15 | Pass | r10 n20000 rust 9657.1 µs vs python 26330.7 (rust <= python) and vs ceiling 10.89 ms (plan 00007 9.9 ms + 10%); r256 n20000 rust 4111.6 µs vs python 51802.1 and vs ceiling 4.51 ms. Full table r10: n6 27.8/4.4, n100 108.4/38.1, n1000 916.8/391.8, n5000 5091.8/2103.7; r256: n100 140.2/50.7, n1000 2503.1/202.7, n5000 12915.5/1019.6. Within noise of 0.4.8 on every row, so README performance figures left unchanged |
| 2026-09-26T17:07:11Z | PLAN-00009-STEP-03 | Full checkpoint | Pass | 1698 passed in 257.63s, TOTAL 345 stmts 120 branches 100% (the new except branch covered), -k rust 581; Rust-free 877 passed, 100%; static clean; logs checkpoint-165857 |
| 2026-09-26T17:19:01Z | PLAN-00009-STEP-04 | Full checkpoint after the split | Pass | 1698 passed in 258.68s, 100%, -k rust 581; Rust-free 877 passed, 100%; cargo test 16 passed (tests now in the fpr-ff1 crate); just rust-lint green with --all; actionlint clean; logs checkpoint-171023 |
| 2026-09-26T17:19:01Z | PLAN-00009-STEP-04 | Wheel and extension identity; core dependencies; public API without 'internal' | Pass | maturin wheel after the split: file list identical to the before-state (10 entries); _rs.__version__ and exported names identical. cargo tree -p fpr-ff1 -e normal: aes 0.9.3, num-bigint 0.5.1, num-integer 0.1.47, num-traits 0.2.19; pyo3 count 0. cargo doc -p fpr-ff1 --no-deps: SIDEBAR_ITEMS = {} (no public items, so no third-party type in any public signature) |
| 2026-09-26T17:30:12Z | PLAN-00009-STEP-05 | cargo clippy -D warnings (workspace, and fpr-ff1 alone); cargo fmt --all --check; float scan over rust/fpr-ff1/src; full checkpoint | Pass | clippy clean both ways; fmt ok; the only float-like match is the step-3 comment quoting the spec; dual gate 1698 passed, 100%; Rust-free 877 passed, 100%; logs checkpoint-172153 |
| 2026-09-26T17:41:32Z | PLAN-00009-STEP-06 | cargo clippy -D warnings in three configurations (fpr-ff1 alone, fpr-ff1 --features internal, workspace); cargo fmt --all --check; RUSTDOCFLAGS='-D warnings' cargo doc -p fpr-ff1 --no-deps; public-item listing | Pass | 0 warnings in each configuration; docs build clean; SIDEBAR_ITEMS = {enum: [ErrorKind], struct: [Builder, Error, FF1]}; no num_bigint, BigUint, aes, cipher, hybrid_array or pyo3 in any public page |
| 2026-09-26T17:41:32Z | PLAN-00009-STEP-06 | Full checkpoint | Pass | 1698 passed in 267.75s, 100%, -k rust 581; Rust-free 877 passed, 100%; logs checkpoint-173259 |
| 2026-09-26T17:54:52Z | PLAN-00009-STEP-07 | Red probes on engine.rs (each reverted; restored byte-identical by cmp): (1) float literal '1.5_f64' added; (2) S-expansion counter j starts at 0; (3) b derived from u instead of v | Pass (each break caught) | (1) no_floating_point_in_any_ff1_path FAILED. (2) nist_per_round_intermediates ok, nist_samples ok, frozen_oracle_vectors FAILED. (3) nist_per_round_intermediates FAILED, nist_samples FAILED. After restore: 41 passed |
| 2026-09-26T17:54:52Z | PLAN-00009-STEP-07 | clippy -D warnings in three configurations; fmt; cargo doc -D warnings; cargo-audit on the lock with the new dev-dependencies; full checkpoint | Pass | 0 warnings each (after replacing '% 2 == 0' with is_multiple_of in a test helper); docs clean; audit exit 0, 52 crate dependencies; dual gate 1698 passed, 100%; Rust-free 877 passed, 100%; logs checkpoint-174537 |
| 2026-09-26T18:05:36Z | PLAN-00009-STEP-08 | Divergence probe (not committed): Rust validate::key accepts 17 bytes | Pass (fails exactly one suite) | Rust: every_shared_case_has_the_same_outcome FAILED 'key-17: accepted, expected KeyLengthError'; Python tests/test_validation_cases.py at the same moment: 108 passed. validate.rs restored byte-identical; Rust harness 2 passed |
| 2026-09-26T18:05:36Z | PLAN-00009-STEP-08 | clippy -D warnings in three configurations; fmt; full checkpoint | Pass | 0 warnings each; dual gate 1806 passed in 259.79s, 100%, -k rust 634; Rust-free 932 passed, 100%; logs checkpoint-175654 |
| 2026-09-26T18:14:34Z | PLAN-00009-STEP-09 | Red-then-green: library crate version drifted to 2.0.1; binding's publish = false removed; each restored | Pass | Drift: 'fpr-ff1/Cargo.toml version 2.0.1 and project version 2.0.0 disagree' (1 failed); publish: 'the PyO3 binding must set publish = false' (1 failed); after restore git diff on rust/ empty and tests/test_contract.py 63 passed |
| 2026-09-26T18:14:34Z | PLAN-00009-STEP-09 | Full checkpoint | Pass | see checkpoint log of this step (dual gate and Rust-free quality at 100%) |
| 2026-09-26T18:15:06Z | PLAN-00009-STEP-09 | Full checkpoint (concrete figures for the row above, which only pointed at the log) | Pass | dual gate 1808 passed in 268.84s, TOTAL 345 stmts 120 branches 100%; Rust-free 934 passed, 245 skipped, 100%; logs checkpoint-180619 |
| 2026-09-26T18:27:32Z | PLAN-00009-STEP-10 | Contents assertion: clean run, then probes (AGENTS.md packaged; a fixture JSON copied into src/), each reverted | Pass | Clean: '19 entries, 0 problems'. AGENTS.md: 'not allowed' + 'forbidden', exit 1. src/kat.json: 'not allowed' + 'forbidden', exit 1. Restored: 0 problems |
| 2026-09-26T18:27:32Z | PLAN-00009-STEP-10 | cargo package --locked; cargo publish --dry-run --locked; unpacked .crate tests outside the repository with and without FPR_FF1_REQUIRE_FIXTURES (working tree, --allow-dirty) | Pass | Packaged 19 files, 122.8KiB (37.0KiB compressed), verification build green; dry run 'aborting upload due to dry run'. Unpacked package: 43 + 9 + 3 passed without the switch; with it, each fixture test fails naming the missing tests/vectors file |
| 2026-09-26T18:27:32Z | PLAN-00009-STEP-10 | clippy -D warnings (three configurations); fmt; cargo doc -D warnings; doctests; full checkpoint | Pass | 0 warnings each; docs clean; 3 doctests; dual gate 1808 passed in 277.45s, 100%; Rust-free 934 passed, 100%; logs checkpoint-181841 |
| 2026-09-26T18:30:06Z | PLAN-00009-STEP-11 | Local runs of the new recipes; probes; the semver skip path | Pass | just crate-test: 43 + 9 + 3 passed, sweeps 2 passed in 7.56s; just crate-msrv on 1.89: 43 + 9 passed. Probes (reverted): unresolved doc link -> 'error: unresolved link to NoSuchItem'; rust-version 1.85 -> the MSRV grep step fails. crates.io/api/v1/crates/fpr-ff1 -> 404, so the semver step takes its recorded skip |
| 2026-09-26T20:37:39Z | PLAN-00009-STEP-11 | CI run 36269172052 on release/v2.1 at 5a6ca38 https://github.com/joelee/fpr-ff1/actions/runs/36269172052 | Pass | completed/success, 41/41 jobs. crate-test on ubuntu, macos and windows: 43 unit (2 ignored) + 9 integration + 3 doctests, then both bijectivity sweeps 2 passed in release; FPR_FF1_REQUIRE_FIXTURES=1 set. crate-msrv on rustc 1.89.0: 43 + 9 + 3 passed. crate-package: docs built with -D warnings, 'crate package: 19 entries, 0 problems', dry run aborted before upload, .crate sha256 82477361864de20048c8f5b86a984808d911cbc79608debb1bd5bf8ebbf0e61c uploaded as artifact 'crate', semver step skipped ('fpr-ff1 is not yet on crates.io'). rust-conformance: 1808 passed, 100.00% coverage, workspace cargo test 43 + 9 + 3 passed |
| 2026-09-26T20:37:39Z | PLAN-00009-STEP-11 | Reproducibility of the .crate: cargo package --locked locally at 5a6ca38 vs the CI artifact | Pass | Byte-identical: both 82477361864de20048c8f5b86a984808d911cbc79608debb1bd5bf8ebbf0e61c. The digest varies between commits only through .cargo_vcs_info.json, which records the commit sha1 (5a6ca385...) and path_in_vcs rust/fpr-ff1; STEP-14's bootstrap must therefore upload the .crate built at the tagged commit, and the digest comparison proves it |
| 2026-09-26T20:39:40Z | PLAN-00009-STEP-12 | ruff format --check; ruff check; tests/test_contract.py; grep for overclaims (crate as reference, FIPS validated, constant-time, zeroization) across README, SECURITY, crate README, AGENTS, architecture, developer guide | Pass | 60 files formatted; All checks passed; 63 passed; the only match is SECURITY.md's out-of-scope 'Key zeroization' bullet; every 'reference' statement names the pure-Python implementation |
| 2026-09-26T20:49:15Z | PLAN-00009-STEP-13 | Local gate at c06cc3f: full checkpoint; just crate-test; just crate-msrv; just crate-package; installed versions | Pass | dual gate 1808 passed in 256.25s, 100%, -k rust 635; Rust-free 934 passed, 100%; crate-test 43 + 9 + 3 and sweeps 2 passed; crate-msrv (1.89) 43 + 9 + 3; crate-package: docs clean, 19 entries 0 problems, dry run aborted before upload; fpr-ff1-2.1.0-rc1.crate sha256 4f722d998f0013d30017ffd7efb6de2d11cb9b034dae426177545ccfd3fd84dc at c06cc3f; fpr_ff1.__version__ 2.1.0rc1, _rs.__version__ 2.1.0-rc1; logs checkpoint-204032 |
| 2026-09-26T21:41:28Z | PLAN-00009-STEP-13 | CI run 36272767880 at 0294db7 (candidate c06cc3f + work-log commit) https://github.com/joelee/fpr-ff1/actions/runs/36272767880 | Pass | completed/success, 41/41 jobs; crate-package 'crate package: 19 entries, 0 problems', fpr-ff1-2.1.0-rc1.crate sha256 d6b9fa405509132296d269df2ee441b61ecd3830a1b73174142abcf4757707e3 at 0294db7 (differs from c06cc3f's only through the embedded commit hash) |
| 2026-09-26T23:59:33Z | PLAN-00009-STEP-14 | publish.yml run 36280228842 on v2.1.0rc1 (d3f1f97) https://github.com/joelee/fpr-ff1/actions/runs/36280228842 | Pass | completed/success, 43 jobs: 42 success, 1 skipped; publish (PyPI): success; publish-crate: skipped, as designed for a pre-release (AC-11's pre-release evidence). PyPI shows 2.1.0rc1 with 7 files |
| 2026-09-26T23:59:33Z | PLAN-00009-STEP-14 | Crate for the bootstrap: the 'crate' artifact of run 36280228842 vs cargo package --locked in a clean worktree at v2.1.0rc1 | Pass | Both fpr-ff1-2.1.0-rc1.crate sha256 3e3b832fe6dcfc5d90ed6def91d6b4362752fb54c3786b75c0e4a03fe0f84d25; artifact .cargo_vcs_info.json sha1 d3f1f97b7198c11d4b2a676dc984f194246deb1e (the tag). This is the digest the owner's bootstrap must reproduce and crates.io's checksum must equal |
| 2026-09-27T00:12:22Z | PLAN-00009-STEP-14 | crates.io: fpr-ff1 2.1.0-rc1 metadata and .crate digest | Pass | API checksum 3e3b832fe6dcfc5d90ed6def91d6b4362752fb54c3786b75c0e4a03fe0f84d25 = the 'crate' artifact of run 36280228842 = cargo package --locked at the tag; the .crate downloaded from static.crates.io hashes the same. license 'MIT OR Apache-2.0', rust_version 1.89, keywords, categories [cryptography], repository and documentation links as in Cargo.toml |
| 2026-09-27T00:12:22Z | PLAN-00009-STEP-14 | docs.rs build of fpr-ff1 2.1.0-rc1 | Pass | status.json {doc_status: true, version: 2.1.0-rc1}; fpr_ff1/index.html, struct.FF1.html and enum.ErrorKind.html return 200; fpr_ff1/__internal/index.html returns 404 (the internal feature is off on docs.rs, as configured) |
| 2026-09-27T00:12:22Z | PLAN-00009-STEP-14 | Scratch Cargo project outside the repository depending on fpr-ff1 = '=2.1.0-rc1' from crates.io (public API only) | Pass | Cargo.lock source registry+crates.io-index; the registry-cache .crate sha256 3e3b832f...0f84d25. NIST SP 800-38G sample 1 (numerals, no tweak) -> 2433477484 and sample 2 (Builder with alphabet and tweak) -> '6124200773'; a radix-10 n=60 input (d > 16) under a 32-byte key and tweak 'cross-check' -> 363405670682792558537082293754099735584196068294081152677333, identical to PyPI fpr-ff1 2.1.0rc1 on both backends; a 15-byte key -> ErrorKind::KeyLength |
| 2026-09-27T00:12:22Z | PLAN-00009-STEP-14 | PyPI: the 7 files of fpr-ff1 2.1.0rc1 vs the artifacts of publish run 36280228842 | Pass | 7/7 SHA-256 match: sdist, py3-none-any, and cp312-abi3 wheels for manylinux_2_34 x86_64 and aarch64, macosx 10_12 x86_64 and 11_0 arm64, and win_amd64 |
| 2026-09-27T00:12:22Z | PLAN-00009-STEP-14 | PyPI attestations: pypi-attestations verify pypi --repository https://github.com/joelee/fpr-ff1 for each file | Pass | OK for all 7 files |
| 2026-09-27T00:12:23Z | PLAN-00009-STEP-14 | Clean installs of fpr-ff1==2.1.0rc1 from PyPI, NIST sample 2 plus the d > 16 case above on each available backend | Pass | 3.12.13: abi3 manylinux x86_64 wheel, python and rust agree. 3.14.7 (GIL): the same abi3 wheel, python and rust agree. 3.14.3 free-threaded: resolver chose py3-none-any (abi3 does not apply), rust backend reports BackendError and python passes. --no-binary (sdist build) on 3.12 and 3.14: py3-none-any, no _rs module, BackendError for rust, python passes |

### Completion summary

- **Implementation status:** `blocked`
- **Completed requirements:** PLAN-00009-REQ-01 to REQ-11, REQ-13; REQ-12 2.1.0rc1 published and verified on both registries; REQ-09 and REQ-14 candidate gated
- **Incomplete requirements:** REQ-12 publication of 2.1.0 by Trusted Publishing; REQ-14 soak, re-review, 2.1.0
- **Outstanding blockers:** Owner: D14 soak statement for 2.1.0rc1
- **Review request:** Not ready
<!-- BUILDER_WORK_LOG_END -->

## 18. Planning change log

| Timestamp (UTC) | Plan status | Change | Reason | Requested/approved by |
|---|---|---|---|---|
| 2026-09-26T16:25:46Z | approved | Plan approved: `plan_status: approved`, `build_ready: true`, `approved_at` set. Planning content frozen; only the Builder-maintained front matter and §17 may change from here. Start conditions in §16 are met: plan 00007's closeout (PR #13) and Dependabot #10 and #11 are merged into `main`, and `release/v2.1` branches from `main` at `62c6115`. | Explicit user approval ("plan 00009 commited and approved") after the draft was committed in 88bd449 | User |
| 2026-09-25T19:14:08Z | draft | Initial draft written at `docs/plans/00009-Crate_And_v2.1.0_Release.md`, superseding approved plan 00008 (never started). Changes from 00008: MSRV 1.87 → 1.89 (code needs 1.88 for `as_chunks`, review 00013 MED-01; `aes` 0.9.3 declares 1.89); no third-party type in the crate's public API, internals behind a hidden `internal` feature; first crates.io publication bootstrapped manually with a scoped, revoked token because Trusted Publishing cannot create a crate, then `2.1.0` by CI; Dependabot #7 taken as two gated upgrades before the split, with a park rule for `num-bigint`; review 00011's three Lows fixed; release version `2.1.0` preceded by `2.1.0rc1` on both registries, each through a `main` merge commit. Plan 00008's decisions D1 to D6 and D9 and its requirements carried forward. | User request on 2026-09-25 ("the word") to write the superseding plan proposed after `v2.0.0` shipped | User |

## 19. External references

1. **crates.io Trusted Publishing**, crates.io documentation; accessed 2026-09-25. Establishes that Trusted Publishing works from GitHub Actions through `rust-lang/crates-io-auth-action` with `id-token: write`, and that a crate must already exist: the first publication of a new crate requires an API token, after which the Trusted Publisher can be configured. <https://crates.io/docs/trusted-publishing>
2. **RFC 3691: Trusted Publishing for crates.io**, The Rust RFC Book; accessed 2026-09-25. Design background for the OIDC flow. <https://rust-lang.github.io/rfcs/3691-trusted-publishing-cratesio.html>
3. **Publishing on crates.io**, The Cargo Book; accessed 2026-09-25. Token scopes and `cargo publish` behaviour. <https://doc.crates.io/crates-io.html>
4. **crates.io crate metadata** for `aes` 0.9.3 (`rust-version` 1.89), `cipher` 0.5.2, `crypto-common` 0.2.2, `hybrid-array` 0.4.15, `inout` 0.2.2, `cpufeatures` 0.3.1 (each 1.85), `pyo3` 0.29.2 (1.83), `num-bigint` 0.5.1 and 0.4.8 (1.60), `num-traits` 0.2.19 (1.60), `num-integer` 0.1.47 (1.31); accessed 2026-09-25 through the crates.io API. <https://crates.io>
5. **`slice::as_chunks`**, Rust standard library documentation; stable since 1.88.0, as cited by reviews 00013 and 00014 and not re-fetched for this plan. <https://doc.rust-lang.org/std/primitive.slice.html#method.as_chunks>

## 20. Confidence

**Medium.** The repository evidence is direct and the corrections are each grounded in a verified fact: the call site at `lib.rs:112`, the public signatures, the dependency floors from crates.io, and the Trusted Publishing constraint from its documentation. The uncertainty is the same as plan 00008's, in the new surface: a validation layer and a public API with no Python counterpart to compare line by line, fixed at publication. Two new external dependencies add some: whether `num-bigint` 0.5 keeps the performance the Rust backend now advertises, which D15 turns into a rule rather than a hope, and the owner-performed bootstrap publication, which is the one step in the release that CI cannot perform.
