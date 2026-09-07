---
title: "Delivery Plan 00003: Accelerated Backend Pure Python Then Rust"
aliases:
  - "Plan 00003"
tags:
  - delivery-plan
  - implementation
  - opencode
type: delivery-plan
plan_id: "PLAN-00003"
plan_status: approved
plan_kind: initial
created_at: "2026-09-06T18:07:27Z"
approved_at: "2026-09-06T21:41:24Z"
planner_agent: plan
planner_model: "ollama-cloud/glm-5.3"
triggered_by: user
request_kind: idea-and-review
repository: "joelee/fpr-ff1"
baseline_branch: "plan/v2.0.0"
baseline_commit: "5f2415859d907da8ec1229890659ead6e2d66a9b"
source_ideas:
  - docs/ideas/00001-v2_0_0_Optional_Rust_Accelerated_Backend-r02.md
source_reviews:
  - docs/reviews/00005-idea-00001-Opus_review.md
previous_plan: null
requirements_count: 23
steps_count: 15
acceptance_criteria_count: 15
blocking_decisions: 0
build_ready: true
web_research_used: false
confidence: high

# Builder-maintained front matter. Builder may update only these keys after
# explicit user approval; Delivery Planner initializes them.
implementation_status: in-progress # not-started | in-progress | blocked | completed | abandoned
builder_agent: build
builder_model: "ollama-cloud/glm-5.3"
execution_branch: "feature/accelerated-backend-pure-python-then-rust"
execution_started_at: "2026-09-06T22:03:07Z"
execution_updated_at: "2026-09-07T13:57:57Z"
execution_completed_at: null
current_step: PLAN-00003-STEP-12
---

# Delivery Plan 00003: Accelerated Backend Pure Python Then Rust

> [!abstract] Plan status: `approved`
> Deliver idea 00001 r02's two-stage concept: first land the measured
> pure-Python win (E1 — subquadratic divide-and-conquer `NUM`/`STR` conversion
> plus a power-of-two fast path, ciphertext-identical, shipped as `v1.1.0`),
> then build the user-approved opt-in Rust backend (E2 — full Algorithm 7 core
> with in-process AES, `backend="rust"`, pure-Python retained as reference and
> default, shipped as `v2.0.0`). All user decisions are resolved; the plan is
> approved and ready for Builder hand-off.

## 1. Objective and outcome

Idea 00001 r02 (re-baselined by review 00005) splits the accelerated-backend
objective into two regimes. This plan delivers both, in the idea's mandated
order:

1. **E1 — pure-Python long-input win (`v1.1.0`).** Replace the quadratic
   digit-at-a-time `_num_radix`/`_str_radix` loops in `src/fpr_ff1/_ff1.py`
   with a subquadratic divide-and-conquer conversion plus an O(n)
   `int.to_bytes`/`int.from_bytes` fast path for power-of-two radices.
   Ciphertext is bit-identical for every input valid in 1.0.0; there is no API
   change and no new dependency. Review 00005 measured this at 17.9×
   (n=20,000, radix 10) and 112× (n=20,000, radix 256) bit-exact across 84
   conformance tests. The naive loop is retained in the module as the
   documented line-by-line reference, with a differential test asserting
   equivalence.

2. **E2 — opt-in Rust backend (`v2.0.0`).** A full Rust core (SP 800-38G
   Algorithm 7 plus the CBC-MAC PRF with a pinned Rust AES crate) behind the
   existing `FF1` API as a keyword-only `backend="rust"` option, defaulting to
   `"python"`. The user has explicitly approved building it (AGENTS.md open
   decision #1). The residual case is the small-input regime, where review
   00005 measured 55% of an n=6 call as `cryptography` per-call cipher-context
   construction; the estimated ceiling is ~8×, to be replaced by real
   measurements against the E1 baseline. Bit-exact conformance — including
   per-round intermediates — is run against both backends; thread-safety and
   pickling guarantees are preserved; typed exceptions rooted at `FF1Error`
   are unchanged; a pure-Python-installable sdist remains the universal
   fallback.

The observable outcome: `v1.1.0` on PyPI with the long-input performance cliff
removed and the README's false "inherent to the algorithm" claim corrected;
then `v2.0.0` on PyPI with an opt-in compiled backend that passes the entire
conformance suite bit-exactly on both paths, ships abi3 wheels for the decided
platform set, and documents its measured speedup and constant-time posture.

## 2. Source traceability

| Requirement | Source | Source location | Interpretation |
|---|---|---|---|
| PLAN-00003-REQ-01 | Idea 00001 r02 | `docs/ideas/00001-...-r02.md` §4 E1, §14 E1 | Subquadratic D&C `NUM`/`STR` conversion, bit-exact |
| PLAN-00003-REQ-02 | Idea 00001 r02 / Review 00005 | r02 §12 candidate 2; 00005 MED-03 | Power-of-two `to_bytes`/`from_bytes` fast path |
| PLAN-00003-REQ-03 | Idea 00001 r02 | r02 MED-01; 00005 Open question 2 | Retain naive loop as documented reference + differential equivalence test |
| PLAN-00003-REQ-04 | Idea 00001 r02 | r02 §4 edge cases, §14 E1 method | Threshold-boundary tests at lengths 63/64/65/128/129 |
| PLAN-00003-REQ-05 | Idea 00001 r02 | r02 MED-02; 00005 Open question 3 | Power cache call-local/immutable; never instance or module state |
| PLAN-00003-REQ-06 | Idea 00001 r02 | r02 §14 E1 success threshold | Full conformance suite green on E1 |
| PLAN-00003-REQ-07 | Idea 00001 r02 | r02 §2 non-negotiables, §6 out-of-scope | No API change, no new dependency, ciphertext identical (E1) |
| PLAN-00003-REQ-08 | Repository instruction | `AGENTS.md` "Standards baseline" | No floating-point arithmetic in the FF1 core; AST scan stays green |
| PLAN-00003-REQ-09 | Repository instruction | `AGENTS.md` "Local development" | 100% line/branch coverage floor maintained |
| PLAN-00003-REQ-10 | Review 00005 | 00005 MED-04; `docs/AGENTS.md` rules | Correct README §Performance claim; update docs in the same change |
| PLAN-00003-REQ-11 | Idea 00001 r02 | r02 §18 actions 1–2 | Ship E1 as 1.x; re-run `just bench` on the CI matrix |
| PLAN-00003-REQ-12 | Idea 00001 r02 | r02 LOW-01; 00005 Open question 4 | Crate-fit microbenchmark before the Rust core |
| PLAN-00003-REQ-13 | User decision + AGENTS.md | User 2026-09-06; `AGENTS.md` open decision #1 | `backend="rust"` opt-in keyword; `"python"` default; reference unchanged |
| PLAN-00003-REQ-14 | Idea 00001 r02 | r02 §11 Option A, §14 E2 | Full Rust core: Algorithm 7 + PRF, pinned Rust AES crate |
| PLAN-00003-REQ-15 | Idea 00001 r01/r02 | r01 MED-02; r02 §13 | Rust AES validated against NIST AES vectors + Python PRF equality |
| PLAN-00003-REQ-16 | Idea 00001 r02 | r02 MAJ-02; r01 LOW-01 | Bit-exact conformance on both backends incl. per-round intermediates via test-only trace bridge |
| PLAN-00003-REQ-17 | Idea 00001 r02 | r02 §2 non-negotiables, A7 | Thread-safety and pickling preserved for accelerated instances |
| PLAN-00003-REQ-18 | Idea 00001 r02 | r02 §2, MED-03 | Same typed exceptions; validation stays in Python; Amdahl floor accepted and documented |
| PLAN-00003-REQ-19 | Idea 00001 r02 | r02 §2 non-negotiables | Missing compiled extension raises a clear `FF1Error`-rooted error; sdist installs pure-Python |
| PLAN-00003-REQ-20 | Idea 00001 r02 | r02 A4, §13; r01 MED-01 | maturin/PyO3 abi3 wheels in CI; decided wheel set; sdist fallback; wheel-test coverage |
| PLAN-00003-REQ-21 | Idea 00001 r02 | r02 §14 E2, MAJ-01, §10 park rule | Measured speedup vs E1 baseline at n ∈ {6, 100}; <2× escalates per park rule |
| PLAN-00003-REQ-22 | Repository instruction | `docs/AGENTS.md` maintained-documents rules | 2.0 documentation set: README, architecture, developer-guide, configuration, directory-structure, backlog, CHANGELOG |
| PLAN-00003-REQ-23 | User decision + README | User 2026-09-06; `README.md` §Roadmap | Ship `v2.0.0` per the roadmap's accelerated-backend line |

## 3. Repository baseline

| Field | Value |
|---|---|
| Repository | `joelee/fpr-ff1` |
| Branch | `plan/v2.0.0` |
| HEAD | `5f2415859d907da8ec1229890659ead6e2d66a9b` |
| Working tree at publication | Clean |
| Applicable instructions | `AGENTS.md` (agent contract); `docs/AGENTS.md` (documentation rules); `docs/plans/AGENTS.md` (plan contract) |

## 4. Scope

### In scope

- **E1 (pure-Python, ships as `v1.1.0`):**
  - `src/fpr_ff1/_ff1.py`: subquadratic divide-and-conquer `_num_radix`/
    `_str_radix` replacement with a call-local memoised `radix**k` cache and
    a naive-below-threshold base case; power-of-two `to_bytes`/`from_bytes`
    fast path; retention of the naive loops as the documented reference
    implementation.
  - New tests: differential equivalence (fast vs naive) across every
    supported radix; recursion-threshold boundary tests (63/64/65/128/129).
  - Documentation: `README.md` §Performance correction and table refresh,
    `CHANGELOG.md`, `docs/backlog.md`.
  - Release `v1.1.0` via the existing tag → `publish.yml` Trusted Publishing
    pipeline; `just bench` re-run for matrix numbers.
- **E2 (Rust backend, ships as `v2.0.0`):**
  - A Rust workspace (`rust/` or `src/fpr_ff1/_rust/` — bounded layout
    decision) with a PyO3 extension implementing Algorithm 7 and the PRF
    using a pinned Rust AES crate.
  - `FF1.__init__` keyword-only `backend: str = "python"` parameter;
    validation of its values; dispatch to the Rust core.
  - Test-only per-round trace bridge for the Rust path; the conformance
    suite parameterised over both backends.
  - Thread-safety and pickling tests for accelerated instances.
  - Packaging: maturin/abi3 wheel builds in CI for the decided platform set,
    a pure-Python-installable sdist fallback, wheel-test job extension.
  - Documentation: README backend section, roadmap update, constant-time
    posture; `docs/architecture.md`, `docs/developer-guide.md`,
    `docs/configuration.md`, `docs/directory-structure.md`,
    `docs/backlog.md`, `CHANGELOG.md`, `SECURITY.md` if posture text changes.
  - Release `v2.0.0`.
- A throwaway crate-fit microbenchmark (recorded in the work log) before the
  Rust core is committed.

### Out of scope

- FF3/FF3-1 (permanently, per `AGENTS.md`).
- Key generation, storage, derivation, or management helpers.
- Application-specific defaults, alphabets, or convenience wrappers.
- Any change to accepted inputs or produced outputs for the pure-Python
  path (E1 is ciphertext-identical; the `backend` keyword is additive and
  opt-in).
- Radix 65536 domain widening (a separate minor-version decision per r02
  §12; the power-of-two *fast path* for existing supported radices is in
  scope, the *widening* is not).
- Batch API (`encrypt_many`/`decrypt_many`) — re-justified in r02 §12 but
  not selected by the user; a separate idea/plan if wanted.
- Rust `fpe` crate as a second differential oracle — per r02 §16 this is a
  consequence-only reversal of a recorded drop, never an input; not selected
  here, so the `docs/backlog.md` drop stands.
- Free-threaded (3.14t) and abi3t (3.15+) wheels (r02 §15 later
  considerations).
- Any claim of FIPS validation or full constant-time operation.
- Moving input validation into Rust (see decision D3).

## 5. Constraints and preserved decisions

- **Pure-Python stays the reference and the default.** `backend="python"` is
  the default; the pure-Python core is never deleted, bypassed, or made
  conditional; the conformance suite always runs against it.
- **Opt-in only.** No caller behaviour changes unless they explicitly pass
  `backend="rust"`.
- **Bit-exact ciphertext** for every input valid in 1.0.0, on both backends.
- **Typed exceptions rooted at `FF1Error`**; identical exception types and
  messages for both backends (validation stays in Python — decision D3).
- **Thread-safety by construction**: no shared mutable state anywhere — the
  D&C power cache is call-local (REQ-05); the Rust core holds no mutable
  shared state and creates cipher contexts per call, mirroring
  `_ff1.py:106-118` and the `_Aes` docstring contract.
- **Pickling**: `__getstate__` drops native/derived state; `__setstate__`
  rebuilds it, as today (`_ff1.py:229-257`).
- **No floating-point arithmetic** in the FF1 core or the Rust core; the
  existing AST scan (REQ-08) stays green and the Rust port uses exact
  integer arithmetic only.
- **Single runtime Python dependency** (`cryptography`) for the pure-Python
  path; the compiled extension is part of this package, not a new PyPI
  dependency — built under the user's explicit approval (decision D3 in
  `AGENTS.md` open decision #1, resolved).
- **100% line and branch coverage floor** on the Python package maintained
  (`pyproject.toml [tool.coverage.report] fail_under = 100`).
- **Never regenerate NIST fixtures** from this implementation; vector files
  stay as transcribed data.
- **Version policy**: E1 is a SemVer minor (`1.1.0` — performance only); the
  Rust backend ships as `2.0.0` per the roadmap. Ciphertext for the
  pure-Python path is unchanged across both releases.
- **Publish only via the existing release-gated Trusted Publishing pipeline**
  (`publish.yml`); no tokens in the repository; publish the tested artifact.

## 6. Assumptions

None. Unresolved matters are recorded as decisions and block approval when
material. All material decisions are resolved (section 7).

## 7. Decisions and blockers

| ID | Decision or blocker | Resolution | Owner | Status |
|---|---|---|---|---|
| D1 | Plan from idea r02 despite `status: revised` (not `accepted`) | User explicitly authorised planning from r02 on 2026-09-06 | User | Resolved |
| D2 | Plan scope: combined E1-then-E2 in one plan, per r02's recommended concept | User selected "Combined E1 then E2" on 2026-09-06 | User | Resolved |
| D3 | AGENTS.md open decision #1 — build the Rust backend at all; opt-in only, pure-Python reference/default preserved; toolchain + wheel + second-AES cost accepted | User selected "Approved: build it" on 2026-09-06 | User | Resolved |
| D4 | Validation stays in Python for both backends (`_prepare` unchanged), preserving exact exception types/messages; the measured ~1.13 µs/call Amdahl floor (review 00005 LOW-01) is accepted and documented rather than escaped | Planner proposal consistent with r02 MED-03; user may override during draft review | Planner (user ratification in draft review) | Resolved |
| D5 | Supported wheel set: abi3-py312 wheels for Linux x86_64 + aarch64, macOS x86_64 + arm64, Windows x64; pure-Python sdist remains the universal fallback | Planner default per r02 A4/r01 MED-01 mitigations; user may adjust during draft review | Planner (user ratification in draft review) | Resolved |
| D6 | E1 ships as `v1.1.0` (SemVer minor); the Rust backend ships as `v2.0.0` per the README roadmap | Per r02 §18.1 ("ship as a 1.x release") and `README.md` §Roadmap | Planner (user ratification in draft review) | Resolved |
| D7 | Rust AES crate: the RustCrypto `aes`/`cbc` family, exact versions pinned with `Cargo.lock` committed | Per r01 MED-02/r02 §13; exact pin is a bounded Builder decision following the repository's pinning convention | Builder (bounded) | Resolved |

No blocking decisions remain. D4–D6 are planner-proposed defaults recorded
here so the user can override them while reviewing this draft; they become
fixed at approval.

## 8. Affected architecture and components

**E1** is confined to `src/fpr_ff1/_ff1.py` (conversion helpers
`_num_radix`/`_str_radix` at lines 463–477 and their call sites in `_ff1`)
plus new test modules and documentation. The public API, `_prepare`
validation, `_prf`, and the Algorithm 7 round structure are untouched.

**E2** adds a compiled extension beside the existing package and a dispatch
point in `FF1.__init__`:

```mermaid
flowchart TD
    Caller["Caller"] --> FF1["FF1(key, radix, *, backend='python', ...)"]
    FF1 -->|backend='python' (default)| Py["_ff1 pure Python — reference"]
    FF1 -->|backend='rust'| Dispatch{"Extension importable?"}
    Dispatch -->|yes| Rs["_fpr_ff1_rs Rust core — Algorithm 7 + PRF"]
    Dispatch -->|no| Err["FF1Error: compiled backend not available"]
    Py --> AesPy["cryptography AES/CBC PRF"]
    Rs --> AesRs["pinned RustCrypto aes/cbc PRF"]
    Py --> Suite["Conformance suite — runs against BOTH paths"]
    Rs --> Suite
    Suite --> Vectors["NIST vectors · per-round intermediates · frozen KAT · differential · bijectivity · interop"]
```

Confirmed components:

| Component | Path / symbol | Change |
|---|---|---|
| FF1 core | `src/fpr_ff1/_ff1.py` — `_num_radix`, `_str_radix`, `_ff1` | E1: D&C + power-of-two fast path; naive loops retained as reference |
| FF1 class | `src/fpr_ff1/_ff1.py` — `FF1.__init__`, `__getstate__`, `__setstate__` | E2: `backend` keyword, dispatch, pickle rebuild for the native handle |
| Exceptions | `src/fpr_ff1/_exceptions.py` | E2: only if a new error type for backend unavailability is needed; must root at `FF1Error` |
| Package init | `src/fpr_ff1/__init__.py` | E2: optional extension import guard |
| Rust workspace | `rust/` (or `src/fpr_ff1/_rust/`) — new | E2: PyO3 module, Algorithm 7, PRF, test-only trace function |
| Tests | `tests/` — new modules; `test_intermediates.py`, `test_nist_vectors.py`, `test_frozen_kat.py`, `test_differential.py`, `test_interoperability.py`, `test_properties.py`, `test_thread_safety.py`, `test_pickle.py` | E1: differential + boundary tests. E2: backend parameterisation, trace bridge, AES validation, thread/pickle for rust instances |
| Benchmark | `benchmarks/timing.py` | Both: E1 refresh; E2 backend comparison cases |
| Packaging | `pyproject.toml`, `Cargo.toml`, `Cargo.lock`, `.github/workflows/ci.yml`, `.github/workflows/publish.yml` | E2: maturin/abi3 build, wheel jobs, sdist contents |
| Docs | `README.md`, `CHANGELOG.md`, `docs/architecture.md`, `docs/developer-guide.md`, `docs/configuration.md`, `docs/directory-structure.md`, `docs/backlog.md` | Both stages, in the same changes that make them true |

## 9. Requirement catalogue

### PLAN-00003-REQ-01 — Subquadratic divide-and-conquer NUM/STR conversion

- **Requirement:** Replace the digit-at-a-time `_num_radix`/`_str_radix` loops
  used by the Algorithm 7 core with a divide-and-conquer conversion
  (recursive split, `divmod` by `radix**k`, naive loop below a 64-numeral
  threshold), producing bit-identical results for every radix and length the
  package accepts.
- **Rationale:** Review 00005 MAJ-01 measured the shipped loops as O(n²) and
  the D&C pair at O(n^1.2–1.3), 17.9× end-to-end at n=20,000 radix 10,
  bit-exact across 84 conformance tests.
- **Source:** Idea r02 §4 E1, §14 E1; review 00005 MAJ-01; `src/fpr_ff1/_ff1.py:463-477`.
- **Acceptance evidence:** Full conformance suite green; differential
  equivalence test vs the retained naive loop (REQ-03); `just bench` shows
  the long-input per-numeral cost drop by an order of magnitude or more at
  n=20,000.

### PLAN-00003-REQ-02 — Power-of-two radix fast path

- **Requirement:** For power-of-two radices (2, 4, 8, 16, 32, 64, 256 — the
  supported subset below 2**16), convert via exact integer
  `int.to_bytes`/`int.from_bytes` bit-grouping instead of division, O(n).
- **Rationale:** Review 00005 MED-03 measured power-of-two radices as the
  worst configurations (radix 256 at 1,114 ms vs radix 10 at 506 ms for
  n=20,000) and the fast path at 112× end-to-end, bit-exact.
- **Source:** Idea r02 §12 candidate 2 (fast-path half); review 00005 MED-03.
- **Acceptance evidence:** Conformance suite green at all power-of-two
  radices; differential test covers every power-of-two radix; `just bench`
  radix-256 case shows the drop.

### PLAN-00003-REQ-03 — Naive loops retained as documented reference

- **Requirement:** Keep the current five-line loops in `_ff1.py` as the
  documented line-by-line reference implementation (spec-step comments
  intact), and add a differential test asserting fast-path output equals
  naive-loop output across every supported radix.
- **Rationale:** Idea r02 MED-01: the D&C conversion trades "clarity over
  cleverness"; retaining the reference plus an equivalence test preserves
  the project's compare-against-the-spec reviewability property.
- **Source:** Idea r02 MED-01; review 00005 Open question 2.
- **Acceptance evidence:** The naive reference functions exist and are
  exercised by the differential test (also keeping them inside the 100%
  coverage floor); the differential test passes.

### PLAN-00003-REQ-04 — Recursion-threshold boundary tests

- **Requirement:** Test conversion correctness at lengths 63, 64, 65, 128,
  129 (around the 64-numeral D&C threshold) for representative radices,
  including odd/even splits.
- **Rationale:** Idea r02 §4 edge cases and §14 E1 method explicitly require
  the boundary test.
- **Source:** Idea r02 §4, §14.
- **Acceptance evidence:** Boundary test module present and green; covers
  the threshold branches for the coverage floor.

### PLAN-00003-REQ-05 — Power cache is call-local and immutable

- **Requirement:** The memoised `radix**k` cache used by the D&C conversion
  is created per call and passed down the recursion (or otherwise kept
  call-local); it must never be hoisted to the instance, class, or module
  level. A code comment states this constraint so it is not "optimised"
  later.
- **Rationale:** Idea r02 MED-02: an instance-level cache would be shared
  mutable state, breaking the thread-safety contract `_ff1.py:106-118`
  guarantees — the "plausible but wrong" class `AGENTS.md` warns about.
- **Source:** Idea r02 MED-02; review 00005 Open question 3.
- **Acceptance evidence:** Code inspection (comment present, no
  instance/module cache); `tests/test_thread_safety.py` green; concurrent
  calls produce single-threaded results.

### PLAN-00003-REQ-06 — Full conformance suite green on E1

- **Requirement:** All existing conformance tests pass unmodified against
  the D&C + fast-path conversion: NIST sample vectors (both directions),
  per-round intermediates, frozen KAT, exact-arithmetic, properties,
  interoperability, differential, bijectivity.
- **Rationale:** Idea r02 §14 E1 success threshold; conformance is the
  product (`AGENTS.md`).
- **Source:** Idea r02 §14; `AGENTS.md` Tests.
- **Acceptance evidence:** `just quality` green including the 100% coverage
  gate; CI matrix green before release.

### PLAN-00003-REQ-07 — E1 changes no API, dependency, or ciphertext

- **Requirement:** E1 adds no public API, no dependency, no configuration,
  and produces bit-identical ciphertext for every input valid in 1.0.0.
- **Rationale:** Idea r02 §2 non-negotiables and §6 out-of-scope; this is
  what makes E1 a SemVer minor release.
- **Source:** Idea r02 §2, §6.
- **Acceptance evidence:** Diff review shows only internal helper changes;
  frozen KAT and interoperability tests (byte-identical to
  `ubiq_security_fpe`) pass unmodified.

### PLAN-00003-REQ-08 — No floating-point arithmetic

- **Requirement:** The D&C and fast-path code uses exact integer arithmetic
  only; the existing AST/token scan for float operations in the FF1 module
  stays in place and green.
- **Rationale:** `AGENTS.md` standards baseline — the Bouncy Castle bug
  class; review 00005 confirmed the D&C prototype needed no floats.
- **Source:** `AGENTS.md` "No floating-point arithmetic anywhere in the FF1
  core"; `tests/test_exact_arithmetic.py`.
- **Acceptance evidence:** AST scan test green; no `math.log*`, `ceil`,
  `pow`, `/`, or float literals in the changed code.

### PLAN-00003-REQ-09 — Coverage floor maintained

- **Requirement:** 100% line and branch coverage on `fpr_ff1` is maintained
  after every step that touches Python code.
- **Rationale:** `AGENTS.md` local development rules; `pyproject.toml`
  `fail_under = 100` with branch coverage on.
- **Source:** `AGENTS.md`; `pyproject.toml [tool.coverage.report]`.
- **Acceptance evidence:** `just coverage` green at each checkpoint.

### PLAN-00003-REQ-10 — README performance claim corrected with E1

- **Requirement:** In the same change that lands E1, correct
  `README.md:229-234`: the quadratic cost is an implementation choice of the
  previous conversion, not "inherent to the algorithm"; refresh the
  performance table from `just bench`; stop pointing the long-input regime
  at the 2.0 backend as its remedy. Update `CHANGELOG.md` and
  `docs/backlog.md` in the same change.
- **Rationale:** Review 00005 MED-04: the published claim is false and
  steers users toward waiting for a major version for a win available in
  1.x; `docs/AGENTS.md` requires same-change doc updates.
- **Source:** Review 00005 MED-04; `docs/AGENTS.md`.
- **Acceptance evidence:** README no longer contains the "inherent to the
  algorithm's NUM/STR steps" claim; the table matches a fresh `just bench`
  run; changelog entry exists.

### PLAN-00003-REQ-11 — Ship E1 as v1.1.0 with matrix numbers

- **Requirement:** Release E1 as `v1.1.0` through the existing pipeline
  (full matrix green → signed tag → release → `publish.yml`), and re-run
  `just bench` across the CI matrix to replace single-machine numbers.
- **Rationale:** Idea r02 §18 actions 1–2; ciphertext-identical performance
  work is a minor release under the recorded version policy.
- **Source:** Idea r02 §18; `docs/backlog.md` version policy.
- **Acceptance evidence:** `v1.1.0` on PyPI with provenance attestations;
  matrix bench numbers recorded in the work log and reflected in the README
  table.

### PLAN-00003-REQ-12 — Crate-fit microbenchmark before the Rust core

- **Requirement:** Before committing the Rust core, run a throwaway
  microbenchmark of Rust `num-bigint` divmod at ~33k-bit operands versus
  CPython `int`, and confirm the chosen big-int representation can hold an
  n=20,000 half. Record results in the work log.
- **Rationale:** Idea r02 LOW-01: `cosmian_fpe`'s fixed-width `crypto_bigint`
  fit is unverified and `fpe`'s `num-bigint` speed is unestablished; a
  30-minute test prevents a wasted spike.
- **Source:** Idea r02 LOW-01; review 00005 Open question 4.
- **Acceptance evidence:** Work-log entry with measured numbers and the
  resulting crate/representation choice; escalation if neither fits.

### PLAN-00003-REQ-13 — Opt-in `backend` keyword

- **Requirement:** `FF1.__init__` gains keyword-only `backend: str =
    "python"`; `"rust"` selects the compiled core; any other value raises a
    typed `FF1Error`-rooted exception; the default path is byte-for-byte the
    current pure-Python implementation.
- **Rationale:** User decision D3 resolving `AGENTS.md` open decision #1;
    idea r02 §2 non-negotiables (opt-in only, reference and default
    preserved).
- **Source:** User 2026-09-06; `AGENTS.md` open decisions; idea r02 §2.
- **Acceptance evidence:** Constructor tests for both values and rejection
  of invalid ones; existing suite green with no behavioural change when
  `backend` is not passed.

### PLAN-00003-REQ-14 — Full Rust core (Option A)

- **Requirement:** The Rust extension implements SP 800-38G Algorithm 7
  (encrypt and decrypt) and the Algorithm 6 PRF (CBC-MAC, zero IV,
  16-byte-aligned input) with a pinned RustCrypto AES crate, exact integer
  arithmetic, spec-step comments mirroring `_ff1.py`, and no shared mutable
  state (cipher contexts created per call).
- **Rationale:** Idea r02 §11 Option A / §14 E2: the small-input case is
  per-call cipher-context construction (55% of an n=6 call), which only a
  full in-process core eliminates.
- **Source:** Idea r02 §11, §14; r01 MED-02.
- **Acceptance evidence:** Conformance suite green on the rust backend
  (REQ-16); AES validation (REQ-15); no `unsafe` shared state; `Cargo.lock`
  committed.

### PLAN-00003-REQ-15 — Rust AES independently validated

- **Requirement:** The Rust AES/CBC-MAC path is validated against NIST AES
  known-answer vectors and against the Python path's `_prf` output for a
  spread of inputs, before any FF1-level conformance is trusted on it.
- **Rationale:** Idea r01 MED-02 / r02 §13: a second AES implementation is a
  cryptographic correctness risk that NIST FF1 vectors (radix 10/36 only)
  would not isolate.
- **Source:** Idea r01 MED-02; r02 §13.
- **Acceptance evidence:** AES KAT test module green; PRF-equality test
  (Rust vs Python `_prf`) green across block counts 1–5+.

### PLAN-00003-REQ-16 — Bit-exact conformance on both backends

- **Requirement:** The full conformance suite — NIST vectors, per-round
  intermediates via a test-only trace bridge on the Rust path, frozen KAT,
  differential, bijectivity, interoperability, properties — runs against
  both `backend="python"` and `backend="rust"` and passes bit-exactly. The
  trace bridge is test-only and never exported from the public API.
- **Rationale:** Idea r02 MAJ-02: a second implementation of the same subtle
  algorithm is the dominant hazard; per-round intermediates are the project's
  strongest evidence ("two compensating bugs can pass an output test").
- **Source:** Idea r02 MAJ-02; r01 LOW-01; `AGENTS.md` Tests.
- **Acceptance evidence:** Backend-parameterised conformance run green;
  per-round `P/Q/R/S/y/m/c/C` equality asserted for the rust path on all
  nine NIST samples.

### PLAN-00003-REQ-17 — Thread-safety and pickling preserved

- **Requirement:** `backend="rust"` instances are thread-safe (concurrent
  calls produce single-threaded results) and picklable
  (`__getstate__`/`__setstate__` drop and rebuild the native handle), with
  tests for both.
- **Rationale:** Idea r02 §2 non-negotiables and A7; the 1.0.0 contract
  (`_ff1.py:229-257`, `tests/test_pickle.py`, `tests/test_thread_safety.py`).
- **Source:** Idea r02 §2, A7.
- **Acceptance evidence:** Rust-backend variants of the pickle and
  thread-safety tests green; PyO3 classes are `Send + Sync` with no interior
  mutability.

### PLAN-00003-REQ-18 — Same typed exceptions; validation stays in Python

- **Requirement:** `_prepare` and all validation run in Python for both
  backends, so exception types and messages are identical; the accepted
  Amdahl floor (~1.13 µs at n=6, review 00005 LOW-01) is documented in the
  README performance section rather than escaped.
- **Rationale:** Idea r02 MED-03: moving validation into Rust would change
  exception messages and `FF1Error` type mapping — a compatibility question
  the "same exceptions" non-negotiable does not cover; keeping validation in
  Python resolves it by construction (decision D4).
- **Source:** Idea r02 MED-03; review 00005 LOW-01.
- **Acceptance evidence:** Validation tests pass identically for both
  backends; README states the floor.

### PLAN-00003-REQ-19 — Graceful behaviour without the compiled extension

- **Requirement:** Installing from the sdist (or any environment without the
  compiled extension) leaves the package fully functional as pure Python;
  `backend="rust"` then raises a clear `FF1Error`-rooted exception
  explaining that the compiled backend is unavailable. The sdist remains
  pure-Python-installable without a Rust toolchain.
- **Rationale:** Idea r02 §13 ("pure-Python sdist as the universal
  fallback") and §2 non-negotiables; the wheel/sdist split in
  `pyproject.toml` and CI.
- **Source:** Idea r02 §13; `pyproject.toml` sdist configuration.
- **Acceptance evidence:** A no-extension install passes the full suite on
  the python backend and raises the documented error for `backend="rust"`;
  sdist-contents CI assertion stays green.

### PLAN-00003-REQ-20 — Wheel matrix and CI

- **Requirement:** CI builds abi3-py312 wheels via maturin for Linux x86_64
  + aarch64, macOS x86_64 + arm64, Windows x64 (decision D5); the wheel-test
  job installs the built wheel and exercises both backends; the pure-Python
  sdist path stays tested; `Cargo.lock` is committed and audited alongside
  the existing `pip-audit` job.
- **Rationale:** Idea r02 A4 and §13; r01 MED-01: the wheel matrix is the
  main operational cost of E2 and must be wired into the existing
  supply-chain-hardened CI.
- **Source:** Idea r02 A4, §13; r01 MED-01; `.github/workflows/ci.yml`.
- **Acceptance evidence:** CI wheel-build and wheel-test jobs green on all
  decided platforms; audit job covers Rust dependencies.

### PLAN-00003-REQ-21 — Measured speedup against the E1 baseline

- **Requirement:** Measure the rust backend against the E1 pure-Python
  baseline at n ∈ {6, 100} (radix 10) with `benchmarks/timing.py`
  methodology, record the numbers in the work log and README, and state them
  against the ~8× ceiling and the Amdahl floor. If the measured speedup is
  <2× on the dominant small-input cases, stop and escalate per idea r02's
  pre-committed park rule instead of shipping.
- **Rationale:** Idea r02 MAJ-01 (the ~8× ceiling is arithmetic, not
  measurement) and §10 ("Park E2 if ... the measured Rust speedup is small
  (<2×)").
- **Source:** Idea r02 MAJ-01, §10, §14 E2.
- **Acceptance evidence:** Work-log entry with per-case numbers; README
  performance section states both backends' measured numbers; escalation
  recorded if the park threshold is hit.

### PLAN-00003-REQ-22 — 2.0 documentation set

- **Requirement:** Update in the same changes that make them true:
  `README.md` (backend usage, roadmap table, constant-time posture — neither
  backend eliminates value-dependent timing), `docs/architecture.md` (second
  backend, dispatch, extension), `docs/developer-guide.md` (Rust toolchain,
  new commands), `docs/configuration.md` (`backend` parameter),
  `docs/directory-structure.md` (Rust workspace), `docs/backlog.md`,
  `CHANGELOG.md`.
- **Rationale:** `docs/AGENTS.md` maintained-documents rules; idea r02 §15
  later considerations (constant-time posture must be documented, not
  overclaimed).
- **Source:** `docs/AGENTS.md`; idea r02 §15.
- **Acceptance evidence:** Each listed document reflects the shipped 2.0
  state; no constant-time overclaim.

### PLAN-00003-REQ-23 — Ship v2.0.0

- **Requirement:** Release `v2.0.0` through the existing release-gated
  pipeline with the full matrix (now including wheel builds) green.
- **Rationale:** The README roadmap's 2.0 line; user decision D3.
- **Source:** `README.md` §Roadmap; user 2026-09-06.
- **Acceptance evidence:** `v2.0.0` on PyPI with wheels for the decided set,
  provenance attestations, and the sdist fallback.

## 10. Delivery strategy

Two independently shippable stages, in the idea's mandated order. Each stage
ends in a release, so the repository is never left mid-transition.

**Stage E1 (steps 01–06) is test-first and confined to one module.** The
differential-equivalence and boundary tests are written first and fail
against the shipped loops; the D&C conversion and power-of-two fast path then
land behind them; the naive loops stay as the reference and remain exercised
by the differential test (which also keeps them inside the coverage floor).
Because ciphertext is provably identical (frozen KAT, interoperability,
per-round intermediates all assert existing expected values), the release is
a low-risk SemVer minor. Documentation corrections ride in the same change
per `docs/AGENTS.md`.

**Stage E2 (steps 07–15) gates every trust decision on evidence before
integration.** The crate-fit microbenchmark (step 07) runs before any core
code is committed. The Rust AES is validated in isolation (step 09) before
any FF1-level output is trusted. The trace bridge (step 11) restores
per-round intermediate conformance — the project's strongest evidence — for
the second implementation before performance is even measured (step 13).
Packaging (step 14) comes after correctness so a wheel is never built around
an unproven core. The park rule (<2× measured speedup → stop and escalate)
is a Builder stop condition, not a planning assumption: the user has approved
building the backend, but the idea's pre-committed failure threshold still
binds.

**Test approach.** E1 uses TDD (failing differential/boundary tests first).
E2 cannot reuse the Python tests until the bridge exists, so it sequences
validation bottom-up: AES KAT → PRF equality → full FF1 conformance on both
backends → thread/pickle → performance. The 100% coverage floor applies to
all Python-side code including the new dispatch; Rust code is verified by the
conformance suite and Rust unit tests, not by Python line coverage.

**Why the increments are safe.** E1 never changes observable behaviour —
every existing test asserts unchanged expected values. E2 is additive and
opt-in — the default path is the untouched pure-Python core, and the
pure-Python sdist fallback means no user is ever forced onto the compiled
path. Each stage's release is gated by the full existing CI matrix.

## 11. Detailed implementation steps

### PLAN-00003-STEP-01 — E1 test scaffolding (failing first)

- **Status placeholder:** `completed`
- **Objective:** Write the differential-equivalence and threshold-boundary
  tests that define E1 correctness, and show they fail against the shipped
  loops (or, for the differential test, that it is trivially green until the
  fast path exists — the boundary-length cases must exercise the future
  threshold branches).
- **Requirements:** `PLAN-00003-REQ-03`, `PLAN-00003-REQ-04`
- **Depends on:** None
- **Affected components:** new `tests/test_conversion_equivalence.py` (name
  is a bounded Builder decision); `tests/vectors/` untouched.
- **Preconditions:** Clean worktree; E1 branch created from `plan/v2.0.0`
  (or `main` if merged by then).
- **Test or evidence first:** This step *is* the tests: differential
  equality of fast vs naive conversion across every supported radix
  (2..65535, small lengths — direct helper-level calls are cheap) plus
  property-based sampling at larger lengths; boundary lengths
  63/64/65/128/129 at representative radices (2, 10, 36, 256, 65535) with
  odd and even splits.
- **Implementation tasks:**
  1. Add the differential test module targeting the conversion helpers
     (initially comparing the shipped helpers to themselves, structured so
     the fast-path functions drop in).
  2. Add boundary-length cases.
  3. Confirm the suite collects and the boundary cases run green against the
     current loops (they test correctness, not speed).
- **Documentation/configuration/operations:** None.
- **Verification:** `uv run pytest tests/test_conversion_equivalence.py -v`
  (green against current code; the differential comparison becomes
  meaningful in step 02).
- **Completion criteria:** New tests exist, pass against the current
  implementation, and are structured to compare fast vs naive once step 02
  lands.
- **Rollback or recovery:** Delete the new test module; nothing else changed.
- **Builder stop conditions:** If a boundary case fails against the *current*
  loops, stop — that is a pre-existing defect, not E1 work.

### PLAN-00003-STEP-02 — Divide-and-conquer conversion

- **Status placeholder:** `completed`
- **Objective:** Implement the subquadratic `_num_radix`/`_str_radix`
  replacement with a call-local memoised power cache and 64-numeral
  threshold; retain the naive loops as the documented reference.
- **Requirements:** `PLAN-00003-REQ-01`, `PLAN-00003-REQ-03`,
  `PLAN-00003-REQ-05`, `PLAN-00003-REQ-08`
- **Depends on:** PLAN-00003-STEP-01
- **Affected components:** `src/fpr_ff1/_ff1.py` (`_num_radix`,
  `_str_radix`, new reference/D&C helpers); call sites in `_ff1` unchanged in
  behaviour.
- **Preconditions:** Step 01 tests in place.
- **Test or evidence first:** The step-01 differential test now compares D&C
  vs naive and must pass; the full suite must stay green.
- **Implementation tasks:**
  1. Rename/retain the current loops as the documented reference (e.g.
     `_num_radix_reference`/`_str_radix_reference` — naming is a bounded
     decision) with their spec-step comments.
  2. Implement the D&C pair: recursive split, `divmod` by memoised
     `radix**k`, naive loop below the threshold; cache created per call and
     passed down the recursion, with a comment stating the thread-safety
     constraint (REQ-05).
  3. Route the `_ff1` core through the new conversion.
  4. Full type annotations; pyright strict clean.
- **Documentation/configuration/operations:** None yet (README rides in step
  05 with measured numbers).
- **Verification:** `uv run pytest tests/test_conversion_equivalence.py` and
  `just test-fast`, then `just coverage` (new branches covered by the
  boundary tests).
- **Completion criteria:** Differential test green across every supported
  radix; full suite green; coverage floor green; AST float scan green.
- **Rollback or recovery:** Revert `_ff1.py` to the naive loops (they are
  still present as the reference).
- **Builder stop conditions:** Any bit-exactness divergence that is not
  immediately explainable; any coverage gap that would require weakening a
  test.

### PLAN-00003-STEP-03 — Power-of-two fast path

- **Status placeholder:** `completed`
- **Objective:** Add the O(n) `to_bytes`/`from_bytes` conversion for
  power-of-two radices and dispatch to it.
- **Requirements:** `PLAN-00003-REQ-02`, `PLAN-00003-REQ-08`
- **Depends on:** PLAN-00003-STEP-02
- **Affected components:** `src/fpr_ff1/_ff1.py` conversion dispatch.
- **Preconditions:** D&C conversion landed and green.
- **Test or evidence first:** Differential test already covers every
  power-of-two radix; existing radix-2/256 conformance cases assert
  unchanged outputs.
- **Implementation tasks:**
  1. Add the power-of-two detection (radix is a power of two and its exponent
     divides cleanly into byte groups) and the `to_bytes`/`from_bytes`
     conversion pair, exact integer arithmetic only.
  2. Dispatch: power-of-two → fast path; otherwise → D&C.
  3. Cover the dispatch branches (the differential test's radix sweep does
     this).
- **Documentation/configuration/operations:** None yet.
- **Verification:** `uv run pytest tests/test_conversion_equivalence.py`;
  `just test-fast`; `just coverage`.
- **Completion criteria:** All power-of-two radices pass the differential and
  conformance suites; coverage floor green; no float operations.
- **Rollback or recovery:** Remove the fast path; D&C remains correct for
  all radices.
- **Builder stop conditions:** Any divergence at a power-of-two radix.

### PLAN-00003-STEP-04 — E1 full verification and benchmark

- **Status placeholder:** `completed`
- **Objective:** Run the complete quality gate and the benchmark harness;
  capture the E1 numbers that become the README table and the E2 baseline.
- **Requirements:** `PLAN-00003-REQ-06`, `PLAN-00003-REQ-07`,
  `PLAN-00003-REQ-09`
- **Depends on:** PLAN-00003-STEP-03
- **Affected components:** none (verification only); `benchmarks/timing.py`
  runs as-is.
- **Preconditions:** Steps 02–03 complete.
- **Test or evidence first:** N/A — this step is the evidence.
- **Implementation tasks:**
  1. `just quality` (format check, lint, pyright, tests with the 100%
     coverage gate).
  2. `just bench`; record the throughput and per-numeral tables in the work
     log, including radix 256 and n=20,000 cases.
  3. Confirm the frozen KAT and interoperability results are unchanged
     (they are part of the suite; call them out in the work log as the
     ciphertext-identity evidence).
- **Documentation/configuration/operations:** None.
- **Verification:** `just quality` green; `just bench` output recorded.
- **Completion criteria:** Full gate green; bench numbers in the work log
  showing the long-input drop (order(s) of magnitude at n=20,000).
- **Rollback or recovery:** N/A (read-only step).
- **Builder stop conditions:** Any gate failure; any benchmark regression on
  small inputs beyond noise (the D&C prototype measured 1.0× at n=6 — a
  small-input regression above ~10% should be escalated).

### PLAN-00003-STEP-05 — E1 documentation and version 1.1.0

- **Status placeholder:** `completed`
- **Objective:** Correct the README performance claim, refresh the table,
  update the changelog and backlog, and set the version to 1.1.0.
- **Requirements:** `PLAN-00003-REQ-10`, `PLAN-00003-REQ-11`
- **Depends on:** PLAN-00003-STEP-04
- **Affected components:** `README.md` (§Performance, §Roadmap 2.0 note),
  `CHANGELOG.md`, `docs/backlog.md`, `pyproject.toml` (version).
- **Preconditions:** Measured numbers from step 04.
- **Test or evidence first:** N/A (documentation).
- **Implementation tasks:**
  1. Rewrite `README.md:229-234`: the previous conversion was quadratic by
     implementation choice; subquadratic conversion shipped in 1.1.0; remove
     the implication that 2.0 is the remedy for the long-input regime.
  2. Refresh the performance table from the step-04 bench run.
  3. `CHANGELOG.md` entry for 1.1.0 (performance only; ciphertext unchanged).
  4. `docs/backlog.md`: record E1 as completed; keep the 2.0 item active,
     now scoped to the small-input regime.
  5. Bump `pyproject.toml` version to `1.1.0`.
- **Documentation/configuration/operations:** This step is the documentation.
- **Verification:** `just quality` still green; README table matches the
  recorded bench output.
- **Completion criteria:** No "inherent to the algorithm" claim remains;
  table refreshed; changelog and backlog updated; version bumped.
- **Rollback or recovery:** Revert documentation files.
- **Builder stop conditions:** None.

### PLAN-00003-STEP-06 — Release v1.1.0

- **Status placeholder:** `completed`
- **Objective:** Ship E1 through the existing release pipeline and capture
  matrix bench numbers.
- **Requirements:** `PLAN-00003-REQ-11`
- **Depends on:** PLAN-00003-STEP-05
- **Affected components:** git tag `v1.1.0`; GitHub release; PyPI.
- **Preconditions:** Full local gate green; branch merged per the
  repository's normal flow.
- **Test or evidence first:** The release gate *is* the test: `publish.yml`
  re-runs the full CI matrix before publishing.
- **Implementation tasks:**
  1. Merge to `main`; confirm the 9-leg matrix is green.
  2. Create the signed annotated tag `v1.1.0` and the GitHub release
     (matching the v1.0.0 process from plan 00002).
  3. Confirm `publish.yml` publishes with provenance attestations; verify
     PyPI state.
  4. Re-run `just bench` on the CI matrix (or record matrix numbers from CI
     runs) and note them in the work log; refresh the README table if the
     numbers differ materially from the local run.
- **Documentation/configuration/operations:** Release notes for 1.1.0.
- **Verification:** `v1.1.0` visible on PyPI with attestations; matrix green.
- **Completion criteria:** E1 shipped; matrix numbers recorded.
- **Rollback or recovery:** A bad release is yanked per PyPI policy; the tag
  is corrected only via a new patch release (never rewritten history).
- **Builder stop conditions:** Any matrix leg red; any publish failure (stop
  and report — never retry with tokens or workflow changes).

### PLAN-00003-STEP-07 — Crate-fit microbenchmark

- **Status placeholder:** `completed`
- **Objective:** Settle the Rust big-int representation question with a
  throwaway microbenchmark before any core code is committed.
- **Requirements:** `PLAN-00003-REQ-12`
- **Depends on:** PLAN-00003-STEP-06 (E2 starts from a clean, released
  baseline)
- **Affected components:** throwaway scratch project (not committed to the
  package; may live in `/tmp` or an untracked scratch dir during execution —
  results go in the work log).
- **Preconditions:** Rust toolchain available locally.
- **Test or evidence first:** This step is the evidence.
- **Implementation tasks:**
  1. Microbenchmark `num-bigint` divmod at ~33k-bit operands vs CPython
     `int` divmod at the same sizes (the n=20,000 half regime).
  2. Confirm the chosen representation can hold an n=20,000 half (and the
     maximum: radix 65535, n = 2**32-1 is unconstructable — use the
     practical maximum from the README cases).
  3. Record numbers and the crate/representation choice in the work log.
- **Documentation/configuration/operations:** None (throwaway).
- **Verification:** Work-log entry with measured numbers.
- **Completion criteria:** A justified representation choice recorded.
- **Rollback or recovery:** N/A (throwaway).
- **Builder stop conditions:** If no available crate can represent the
  operands or none is competitive, stop and escalate — this is idea r02
  LOW-01's collapse condition and may re-scope E2.

### PLAN-00003-STEP-08 — Rust workspace and Algorithm 7 port

- **Status placeholder:** `completed`
- **Objective:** Create the Rust workspace with the PyO3 extension and port
  Algorithm 7 (encrypt and decrypt) with exact integer arithmetic and
  spec-step comments.
- **Requirements:** `PLAN-00003-REQ-14`
- **Depends on:** PLAN-00003-STEP-07
- **Affected components:** new `Cargo.toml`, `Cargo.lock`, Rust sources
  (layout per step 07's representation choice; bounded decision);
  `pyproject.toml` build configuration begins.
- **Preconditions:** Representation choice recorded.
- **Test or evidence first:** Rust unit tests for the conversion and round
  structure (mirroring the spec-step comments) written alongside the port.
- **Implementation tasks:**
  1. Scaffold the workspace: PyO3 module, pinned dependencies
     (RustCrypto `aes`/`cbc` per D7, the big-int crate per step 07),
     `Cargo.lock` committed.
  2. Port `_ff1` encrypt/decrypt: `u`/`v` split, `b` from `v` (never `u`),
     `d = 4*ceil(b/4)+4`, padding `(-t-b-1) mod 16`, `P` block, ten rounds,
     parity rule identical in both directions, `S` truncated to `d` bytes,
     final-assignment asymmetry — each with the same spec-step comments as
     `_ff1.py`.
  3. Exact integer arithmetic only; no floats; no shared mutable state.
  4. Rust unit tests for the ported pieces.
- **Documentation/configuration/operations:** None yet.
- **Verification:** `cargo test` (the command introduced by this workspace)
  green; a `just` recipe for Rust checks added (e.g. `just rust-test` —
  defined by this step).
- **Completion criteria:** Algorithm 7 port compiles and passes its Rust
  unit tests; no `unsafe` beyond what the crates provide.
- **Rollback or recovery:** Remove the workspace; the Python package is
  untouched.
- **Builder stop conditions:** Any spec-step that cannot be ported exactly;
  any need for `unsafe` hand-written crypto.

### PLAN-00003-STEP-09 — Rust PRF and AES validation

- **Status placeholder:** `completed`
- **Objective:** Implement the Algorithm 6 PRF (CBC-MAC, zero IV) in Rust
  and validate the AES path independently before trusting any FF1 output.
- **Requirements:** `PLAN-00003-REQ-14`, `PLAN-00003-REQ-15`
- **Depends on:** PLAN-00003-STEP-08
- **Affected components:** Rust PRF module; new
  `tests/test_rust_aes_validation.py` (or extension of an existing module —
  bounded).
- **Preconditions:** Algorithm 7 port compiles.
- **Test or evidence first:** NIST AES KAT vectors for the pinned crate's
  AES-128/192/256; PRF-equality cases vs the Python `_prf`.
- **Implementation tasks:**
  1. Implement the PRF: CBC-MAC with zero IV over 16-byte-aligned input,
     fresh cipher context per call (no cached encryptor — mirror the
     `_Aes`/`_prf` contract).
  2. Add the AES KAT test (vectors as data files, never generated from this
     implementation).
  3. Add the PRF-equality test: Rust PRF output equals Python `_prf` output
     across block counts 1–5 and all three key sizes.
- **Documentation/configuration/operations:** None.
- **Verification:** `cargo test`; `uv run pytest
  tests/test_rust_aes_validation.py` (via the maturin-develop build — the
  local dev loop recipe added in this step, e.g. `just backend-dev`).
- **Completion criteria:** AES KAT green; PRF equality green.
- **Rollback or recovery:** Revert the PRF module; Python path unaffected.
- **Builder stop conditions:** Any AES KAT failure (a wrong pinned crate
  version is a supply-chain red flag — stop and escalate); any PRF
  divergence.

### PLAN-00003-STEP-10 — Python integration: backend keyword and dispatch

- **Status placeholder:** `completed`
- **Objective:** Wire `backend="rust"` into `FF1` with validation, dispatch,
  exception parity, and graceful unavailability.
- **Requirements:** `PLAN-00003-REQ-13`, `PLAN-00003-REQ-18`,
  `PLAN-00003-REQ-19`
- **Depends on:** PLAN-00003-STEP-09
- **Affected components:** `src/fpr_ff1/_ff1.py` (`FF1.__init__`,
  `__getstate__`, `__setstate__`, dispatch in `encrypt_numerals`/
  `decrypt_numerals`), `src/fpr_ff1/__init__.py` (extension import guard),
  possibly `src/fpr_ff1/_exceptions.py`.
- **Preconditions:** Rust core validated at AES/PRF level.
- **Test or evidence first:** Constructor tests: default is python;
  `backend="rust"` builds an accelerated instance; invalid values raise a
  typed error; missing extension raises a clear `FF1Error`-rooted error.
  Validation-path tests must pass identically for both backends.
- **Implementation tasks:**
  1. Add the keyword-only `backend: str = "python"` parameter with typed
     validation (reject unknown values, non-str).
  2. Import the extension lazily/guarded; on unavailability raise the
     documented error only when `"rust"` is requested.
  3. Dispatch `encrypt_numerals`/`decrypt_numerals` (and the string wrappers
     via them) to the Rust core after `_prepare` — validation stays in
     Python (D4).
  4. Pickling: `__getstate__` drops the native handle; `__setstate__`
     rebuilds it from the serialised key/radix/backend.
  5. Keep the pure-Python path byte-for-byte identical when `backend` is not
     passed.
- **Documentation/configuration/operations:** None yet (docs in step 15).
- **Verification:** `just test-fast`; `just coverage` (all new Python
  branches covered, including the missing-extension path — simulate by
  hiding the extension in a test).
- **Completion criteria:** All constructor/validation tests green on both
  backends; coverage floor green; default path unchanged.
- **Rollback or recovery:** Remove the keyword and dispatch; extension
  remains unused.
- **Builder stop conditions:** Any case where the rust backend's exceptions
  differ from the python backend's for the same invalid input.

### PLAN-00003-STEP-11 — Trace bridge and dual-backend conformance

- **Status placeholder:** `completed`
- **Objective:** Restore per-round intermediate conformance for the Rust
  path and run the entire conformance suite against both backends.
- **Requirements:** `PLAN-00003-REQ-16`
- **Depends on:** PLAN-00003-STEP-10
- **Affected components:** Rust test-only trace function; `tests/test_intermediates.py`,
  `tests/test_nist_vectors.py`, `tests/test_frozen_kat.py`,
  `tests/test_differential.py`, `tests/test_interoperability.py`,
  `tests/test_properties.py` (backend parameterisation), `tests/conftest.py`
  (backend fixture).
- **Preconditions:** Dispatch works end-to-end.
- **Test or evidence first:** The existing per-round intermediate assertions
  are the target: the Rust trace must reproduce `P/Q/R/S/y/m/c/C` (+ `u, v,
  b, d`) for every round of all nine NIST samples.
- **Implementation tasks:**
  1. Expose a test-only `encrypt_traced` equivalent from the Rust extension
     (not exported from the public API — mirror `_encrypt_traced`).
  2. Parameterise the conformance modules over `backend ∈ {python, rust}`
     via a fixture.
  3. Run the full suite on both backends; fix divergences in the Rust core
     (never in the tests or the Python reference).
- **Documentation/configuration/operations:** None.
- **Verification:** `just coverage` (both backends exercised; differential
  oracle tests included — `FPR_FF1_REQUIRE_ORACLE=1` in CI).
- **Completion criteria:** Every conformance module green on both backends,
  bit-exact, including per-round intermediates.
- **Rollback or recovery:** Rust path disabled; python-only suite still
  green.
- **Builder stop conditions:** Any intermediate divergence that cannot be
  fixed in the Rust core quickly; any temptation to weaken a test (a change
  that makes tests pass by weakening them is a defect — `AGENTS.md`).

### PLAN-00003-STEP-12 — Thread-safety and pickling for the rust backend

- **Status placeholder:** `in-progress`
- **Objective:** Prove the 1.0.0 compatibility contract holds for
  accelerated instances.
- **Requirements:** `PLAN-00003-REQ-17`
- **Depends on:** PLAN-00003-STEP-11
- **Affected components:** `tests/test_thread_safety.py`,
  `tests/test_pickle.py` (rust-backend variants).
- **Preconditions:** Dual-backend conformance green.
- **Test or evidence first:** Existing thread-safety and pickle tests are
  the templates; add rust-backend parameterisations.
- **Implementation tasks:**
  1. Parameterise the thread-safety test: concurrent calls on one
     rust-backend instance produce single-threaded results.
  2. Parameterise the pickle test: round-trip a rust-backend instance; the
     unpickled instance produces identical ciphertext.
  3. Confirm PyO3 classes are `Send + Sync` with no interior mutability
     (code inspection note in the work log).
- **Documentation/configuration/operations:** None.
- **Verification:** `uv run pytest tests/test_thread_safety.py
  tests/test_pickle.py`; `just coverage`.
- **Completion criteria:** Both suites green on both backends.
- **Rollback or recovery:** N/A (tests only).
- **Builder stop conditions:** Any concurrency failure — this is a
  security-library correctness defect; stop and escalate.

### PLAN-00003-STEP-13 — Performance measurement and park-rule gate

- **Status placeholder:** `not-started`
- **Objective:** Measure the rust backend against the E1 baseline and record
  the decision-grade numbers.
- **Requirements:** `PLAN-00003-REQ-21`
- **Depends on:** PLAN-00003-STEP-12
- **Affected components:** `benchmarks/timing.py` (backend comparison
  cases).
- **Preconditions:** Correctness fully proven (steps 11–12).
- **Test or evidence first:** This step is the evidence.
- **Implementation tasks:**
  1. Extend `benchmarks/timing.py` to time both backends at n ∈ {6, 100}
     (radix 10) plus the existing case set, using the same
     median-of-adaptive-batches methodology.
  2. Record per-case speedups vs the E1 baseline in the work log, stated
     against the ~8× ceiling and the ~1.13 µs validation floor.
  3. Apply the park rule: if the measured speedup is <2× on the dominant
     small-input cases, stop and escalate to the user per idea r02 §10 —
     do not proceed to packaging.
- **Documentation/configuration/operations:** None yet (numbers feed step
  15's docs).
- **Verification:** `just bench` output recorded in the work log.
- **Completion criteria:** Measured numbers recorded; park rule evaluated
  with the outcome documented.
- **Rollback or recovery:** N/A (measurement).
- **Builder stop conditions:** Measured speedup <2× (escalate); results that
  contradict the crate-fit microbenchmark materially (escalate).

### PLAN-00003-STEP-14 — Packaging: wheels, CI, sdist fallback

- **Status placeholder:** `not-started`
- **Objective:** Build and test the wheel matrix; keep the pure-Python sdist
  as the universal fallback; extend the supply-chain hardening to Rust.
- **Requirements:** `PLAN-00003-REQ-19`, `PLAN-00003-REQ-20`
- **Depends on:** PLAN-00003-STEP-13 (only after the park rule passes)
- **Affected components:** `pyproject.toml` (build backend / maturin
  configuration, sdist contents), `.github/workflows/ci.yml` (wheel-build
  job, wheel-test extension, Rust audit), `.github/workflows/publish.yml`
  (publish wheels + sdist via the existing gated flow), `Cargo.lock`.
- **Preconditions:** Park rule passed; correctness proven.
- **Test or evidence first:** The existing sdist-contents assertion and
  wheel-test job are the templates; extend them before changing the build.
- **Implementation tasks:**
  1. Configure the build so the sdist installs pure-Python without a Rust
     toolchain (REQ-19) and includes the Rust sources for wheel builders;
     keep the sdist-contents assertion green.
  2. Add the CI wheel-build job (maturin, abi3-py312, the D5 platform set,
     SHA-pinned actions per the repository convention).
  3. Extend the wheel-test job to install the built wheel and exercise both
     backends (and the missing-extension error path via the sdist install).
  4. Extend the audit job to cover the locked Rust dependencies
     (`cargo audit` or equivalent, pinned).
  5. Update `publish.yml` to publish the gated wheel + sdist artifacts
     (publish the tested artifact — never rebuild).
- **Documentation/configuration/operations:** Developer-facing command
  additions (`just` recipes) documented in step 15.
- **Verification:** CI green end-to-end on a branch; local `uv build`
  produces both artifacts; `uvx twine check dist/*`.
- **Completion criteria:** All decided platforms build wheels; wheel-test
  and sdist assertions green; audits cover Rust.
- **Rollback or recovery:** Revert workflow/build changes; the package
  remains installable pure-Python.
- **Builder stop conditions:** A platform in the D5 set cannot build
  (escalate to re-decide the set); any supply-chain shortcut (unpinned
  actions, unaudited crates) — never proceed.

### PLAN-00003-STEP-15 — 2.0 documentation and release v2.0.0

- **Status placeholder:** `not-started`
- **Objective:** Complete the 2.0 documentation set and ship `v2.0.0`.
- **Requirements:** `PLAN-00003-REQ-22`, `PLAN-00003-REQ-23`
- **Depends on:** PLAN-00003-STEP-14
- **Affected components:** `README.md`, `docs/architecture.md`,
  `docs/developer-guide.md`, `docs/configuration.md`,
  `docs/directory-structure.md`, `docs/backlog.md`, `CHANGELOG.md`,
  `SECURITY.md` (only if posture text changes), `pyproject.toml` (version
  2.0.0).
- **Preconditions:** Full pipeline green including wheels.
- **Test or evidence first:** N/A (documentation + release).
- **Implementation tasks:**
  1. README: backend usage section (opt-in, default, fallback behaviour),
     roadmap table update (2.0 shipped), performance section with both
     backends' measured numbers and the Amdahl floor, constant-time posture
     (document what is and is not guaranteed — no overclaim).
  2. `docs/architecture.md`: second backend, dispatch, extension, build.
  3. `docs/developer-guide.md`: Rust toolchain setup, new `just` recipes,
     wheel build.
  4. `docs/configuration.md`: `backend` parameter.
  5. `docs/directory-structure.md`: Rust workspace layout.
  6. `docs/backlog.md`: 2.0 item completed; record the E2 outcome.
  7. `CHANGELOG.md`: 2.0.0 entry (new opt-in backend; pure-Python path
     unchanged).
  8. Version 2.0.0; full gate; merge; signed tag `v2.0.0`; release;
     publish; verify PyPI (wheels + sdist + attestations).
- **Documentation/configuration/operations:** This step is the
  documentation and release.
- **Verification:** `just quality`; `just build`; the release gate (full CI
  incl. wheels); PyPI verification.
- **Completion criteria:** `v2.0.0` live with the decided wheel set, sdist
  fallback, attestations; all listed documents current.
- **Rollback or recovery:** Yank per PyPI policy if a defect is found
  post-publish; the pure-Python sdist remains installable as `fpr-ff1`
  (pin `<2` for affected callers).
- **Builder stop conditions:** Any matrix or wheel leg red; any doc claim
  not backed by recorded measurements.

## 12. Cross-cutting concerns

| Area | Applicability | Planned action or reason not applicable | Step or requirement |
|---|---|---|---|
| Compatibility and APIs | Applicable | Additive keyword-only `backend` param; default path byte-identical; ciphertext identical on both backends; exceptions identical (validation in Python) | REQ-07, REQ-13, REQ-16, REQ-18; steps 10–11 |
| Data and migration | Not applicable | No data model, storage, or migration; ciphertext unchanged so no re-encryption or rollback window for callers | — |
| Security and privacy | Applicable | Second AES validated against NIST KAT + PRF equality; pinned crates with committed `Cargo.lock`; no new Python runtime dependency; no constant-time overclaim; exception messages never echo plaintext (unchanged validation) | REQ-15, REQ-20, REQ-22; steps 9, 14, 15 |
| Performance and scale | Applicable | The point of the plan: E1 long-input win; E2 measured small-input win vs E1 baseline with park rule; Amdahl floor documented | REQ-01, REQ-02, REQ-21; steps 4, 13 |
| Reliability and failure handling | Applicable | Missing-extension raises a clear typed error; sdist fallback keeps every environment functional; no shared mutable state (thread-safety by construction) | REQ-17, REQ-19; steps 10, 12, 14 |
| Observability and operations | Not applicable | Library, no telemetry; benchmark harness is the operational evidence tool | — |
| Dependencies and supply chain | Applicable | Rust crates pinned, lock committed, audited in CI; SHA-pinned actions per existing convention; publish-the-tested-artifact preserved | REQ-20; step 14 |
| Accessibility and UX | Not applicable | No UI; API ergonomics limited to one additive keyword | — |
| Documentation and release | Applicable | Same-change doc updates per `docs/AGENTS.md`; two changelog entries; README claim correction; constant-time posture | REQ-10, REQ-22; steps 5, 15 |
| Deployment and rollback | Applicable | Two release-gated publishes via the existing Trusted Publishing pipeline; yank policy; pure-Python sdist as the universal fallback | REQ-11, REQ-23; steps 6, 15 |

## 13. Verification strategy

| Level | Evidence or command | When | Required result |
|---|---|---|---|
| Focused unit (E1) | `uv run pytest tests/test_conversion_equivalence.py -v` | Steps 01–03 | Green; differential equality across every supported radix; boundary lengths covered |
| Focused unit (E2 Rust) | `cargo test` (command defined by the workspace in step 08) | Steps 08–09 | Green |
| AES validation | `uv run pytest tests/test_rust_aes_validation.py` | Step 09 | NIST AES KAT green; PRF equality vs Python green |
| Full test suite | `just test-fast` (inner loop), `just coverage` (gated) | Every code-touching step | Green; 100% line and branch coverage on `fpr_ff1` |
| Static analysis / types | `just format-check`, `just lint`, `just typecheck` (components of `just quality`) | Every checkpoint | Green |
| Float-free core | AST scan in `tests/test_exact_arithmetic.py` | Steps 02–03, 08 | Green; no float operations in either core |
| Conformance (both backends) | `just coverage` with backend-parameterised modules; `FPR_FF1_REQUIRE_ORACLE=1` in CI | Steps 11–12 | Bit-exact on `python` and `rust`, incl. per-round intermediates |
| Thread-safety / pickling | `uv run pytest tests/test_thread_safety.py tests/test_pickle.py` | Step 12 | Green on both backends |
| Performance | `just bench` (extended in step 13) | Steps 04, 06, 13 | E1 long-input drop recorded; E2 vs E1 numbers recorded; park rule evaluated |
| Build / packaging | `uv build`; `uvx twine check dist/*`; CI build + wheel-test + sdist-assertion jobs | Steps 14–15 | Both artifacts build; wheels install and pass both backends; sdist installs pure-Python |
| Full repository gate | `just quality` + `just build`; CI 9-leg matrix (+ wheel legs) | Before each release | Green |
| Secret scan | `just secrets` (gitleaks, if installed locally); CI `secrets` job | Before each release | Clean |
| Release verification | PyPI page + provenance attestations for `v1.1.0` and `v2.0.0` | Steps 06, 15 | Both versions live with attestations |

Builder records every verification result in the work log's Verification
results table. No check may be claimed as passed without its evidence entry.

## 14. Acceptance criteria

- [ ] `PLAN-00003-AC-01` The full existing conformance suite (NIST vectors both directions, per-round intermediates, frozen KAT, exact-arithmetic, properties, interoperability, differential, bijectivity) passes unmodified against the E1 conversion — ciphertext bit-identical to 1.0.0.
- [ ] `PLAN-00003-AC-02` A differential test asserts fast-path output equals naive-reference output across every supported radix (2..65535), and the naive loops remain in `_ff1.py` as the documented reference.
- [ ] `PLAN-00003-AC-03` Boundary lengths 63/64/65/128/129 are tested at representative radices with odd and even splits, and the threshold branches are inside the coverage floor.
- [ ] `PLAN-00003-AC-04` `just quality` is green at every checkpoint, including the 100% line-and-branch coverage gate and the AST float scan.
- [ ] `PLAN-00003-AC-05` `README.md` no longer claims the quadratic conversion is "inherent to the algorithm"; the performance table is refreshed from a recorded `just bench` run; `CHANGELOG.md` and `docs/backlog.md` are updated in the same change.
- [ ] `PLAN-00003-AC-06` `v1.1.0` is published via the release-gated Trusted Publishing pipeline with provenance attestations, and matrix bench numbers are recorded in the work log.
- [ ] `PLAN-00003-AC-07` The crate-fit microbenchmark results (num-bigint divmod vs CPython at ~33k-bit operands, representability of an n=20,000 half) are recorded in the work log before any Rust core code is committed.
- [ ] `PLAN-00003-AC-08` `FF1(..., backend="rust")` constructs an accelerated instance; the default (no `backend`) path is unchanged; invalid `backend` values raise a typed `FF1Error`-rooted exception; identical invalid inputs raise identical exceptions on both backends.
- [ ] `PLAN-00003-AC-09` The Rust AES passes NIST AES KAT vectors and PRF-equality vs the Python `_prf` across block counts and key sizes.
- [ ] `PLAN-00003-AC-10` The full conformance suite passes bit-exactly on both backends, including per-round `P/Q/R/S/y/m/c/C` intermediates for all nine NIST samples via the test-only trace bridge (never exported publicly).
- [ ] `PLAN-00003-AC-11` Rust-backend instances pass the thread-safety test (concurrent calls equal single-threaded results) and the pickle round-trip test.
- [ ] `PLAN-00003-AC-12` Measured rust-vs-E1 speedups at n ∈ {6, 100} (radix 10) are recorded in the work log and README, stated against the ~8× ceiling and the validation floor; the park rule (<2× → escalate) is evaluated with the outcome documented.
- [ ] `PLAN-00003-AC-13` CI builds abi3 wheels for the decided platform set; the wheel-test job exercises both backends from an installed wheel; the sdist installs pure-Python without a Rust toolchain, passes the suite, and `backend="rust"` raises the documented unavailability error; Rust dependencies are audited in CI.
- [ ] `PLAN-00003-AC-14` The 2.0 documentation set (README, architecture, developer-guide, configuration, directory-structure, backlog, CHANGELOG) reflects the shipped state, including the constant-time posture with no overclaim.
- [ ] `PLAN-00003-AC-15` `v2.0.0` is published via the release-gated pipeline with wheels for the decided set, the pure-Python sdist, and provenance attestations.

## 15. Risks and mitigations

| Risk | Likelihood | Impact | Mitigation or test | Owner/step |
|---|---|---|---|---|
| D&C conversion diverges bit-wise on some radix | Low | High | Differential test across every supported radix; full conformance suite; boundary tests | Builder/step 02 |
| Power cache hoisted to shared state (thread-safety regression) | Low | High | REQ-05 constraint comment; thread-safety test; review attention | Builder/step 02 |
| Rust core produces plausible-but-wrong ciphertext NIST vectors miss | Medium | Critical | Per-round intermediate trace bridge; differential oracle; bijectivity — all on both backends | Builder/step 11 |
| Rust AES subtly wrong | Medium | High | NIST AES KAT + PRF equality before any FF1-level trust | Builder/step 09 |
| Measured Rust speedup <2× (park rule) | Medium | High | Step 13 gate: stop and escalate with numbers; E1 already shipped, so nothing is lost | Builder+User/step 13 |
| Crate cannot represent operands or is slower than CPython | Low | High | Step 07 microbenchmark before any core work | Builder/step 07 |
| Wheel matrix breaks a platform or grows unbounded | Medium | Medium | Decided D5 set; maturin abi3; sdist fallback; CI wheel legs | Builder/step 14 |
| Pickling/thread-safety regression on the rust path | Low | Medium | Step 12 tests; `Send + Sync` design; no interior mutability | Builder/step 12 |
| Coverage floor violated by new dispatch code | Medium | Medium | `just coverage` at every checkpoint; missing-extension path simulated in tests | Builder/steps 10–11 |
| README/docs drift from measured reality | Medium | Low | Same-change doc rule; numbers only from recorded bench runs | Builder/steps 05, 15 |
| Two implementations drift apart post-2.0 | Medium | Medium | Conformance suite permanently parameterised over both backends in CI | Maintainer/post-plan |

## 16. Builder hand-off

- **Start condition:** User approval and a clean repository.
- **First step:** `PLAN-00003-STEP-01` — E1 test scaffolding (failing-first
  differential and boundary tests).
- **Required sequence:** Steps 01→06 (E1, ending in the `v1.1.0` release),
  then 07→15 (E2, ending in the `v2.0.0` release). Within E2, the evidence
  chain is strictly ordered: microbenchmark → core → AES validation →
  integration → dual-backend conformance → thread/pickle → performance →
  packaging → docs/release. Never build wheels around an unproven core.
- **Parallel-safe work:** Documentation drafts for a stage can be prepared
  alongside its final verification step; Rust unit tests can be extended
  while Python-side parameterisation proceeds (steps 10–11). E1 and E2 must
  not overlap: E2 starts from the released 1.1.0 baseline.
- **Do not change:** approved scope, requirements, steps, acceptance
  criteria, or content outside Builder's permitted work-log area and
  Builder-maintained front matter. Never weaken a test to make it pass.
  Never regenerate NIST fixtures. Never modify the pure-Python reference
  path's behaviour.
- **Escalate when:** any bit-exactness divergence survives a focused fix
  attempt; the park rule triggers (measured <2× vs E1); the crate-fit
  microbenchmark fails; a D5 platform cannot build; any supply-chain
  shortcut would be needed; a matrix leg is red at a release boundary; any
  step's completion criteria cannot be met as written.
- **Completion hand-off:** Record final verification results and the
  completion summary in the work log; both releases verified on PyPI; then
  request a Review agent pass over the execution (the conformance-critical
  nature of this work warrants it), and record the plan outcome in
  `docs/backlog.md`.

<!-- BUILDER_WORK_LOG_START -->
## 17. Builder Work Log

> [!warning] Builder-maintained section
> Delivery Planner creates this section. After approval, Builder may update only
> this delimited section and the Builder-maintained front-matter fields. Builder
> must preserve prior entries and use UTC timestamps.

### Step status

| Step | Status | Started (UTC) | Completed (UTC) | Evidence | Builder notes |
|---|---|---|---|---|---|
| PLAN-00003-STEP-01 | completed | 2026-09-06T22:03:07Z | 2026-09-06T22:18:22Z | Staged checkpoint reviewed and approved by user; digest `a517ad5c...59feb` verified at continuation | Differential oracle transcribed in-test (stronger than plan minimum); 88 new tests |
| PLAN-00003-STEP-02 | completed | 2026-09-06T22:23:50Z | 2026-09-06T22:29:26Z | Staged checkpoint reviewed and approved by user; digest `06a9a47c...31e7e` verified at continuation | ~19× at n=20,000 radix 10; bit-identical across all 839 tests |
| PLAN-00003-STEP-03 | completed | 2026-09-06T22:34:52Z | 2026-09-06T22:38:11Z | Staged checkpoint reviewed and approved by user; digest `c17a5c00...a32be` verified at continuation | Radix 256 n=20,000: ~25× end-to-end; conversion now O(n) |
| PLAN-00003-STEP-04 | completed | 2026-09-06T22:42:34Z | 2026-09-06T22:46:35Z | Staged checkpoint reviewed and approved by user (plan-only checkpoint, no implementation digest) | E1 baseline recorded: ~19× at n=20,000 radix 10, ~25× radix 256 |
| PLAN-00003-STEP-05 | completed | 2026-09-06T22:47:28Z | 2026-09-06T22:52:37Z | Staged checkpoint reviewed and approved by user; digest `c088c824...d7faa` verified at continuation | README claim corrected; 1.1.0 artifacts build |
| PLAN-00003-STEP-06 | completed | 2026-09-07T00:00:10Z | 2026-09-07T00:05:12Z | Staged checkpoint reviewed and approved by user (plan-only checkpoint) | v1.1.0 live on PyPI with attestations; E1 closed |
| PLAN-00003-STEP-07 | completed | 2026-09-07T00:07:24Z | 2026-09-07T00:08:50Z | Staged checkpoint reviewed and approved by user (plan-only checkpoint) | num-bigint fits and is 2–3× faster than CPython at the FF1 shapes; LOW-01 cleared |
| PLAN-00003-STEP-08 | completed | 2026-09-07T00:08:50Z | 2026-09-07T00:29:15Z | Staged checkpoint reviewed and approved by user; digest `1ac143c8...e0e0cf` verified at continuation | Algorithm 7 port landed with seams; 6 Rust tests green; padding-sign bug caught and fixed |
| PLAN-00003-STEP-09 | completed | 2026-09-07T00:29:15Z | 2026-09-07T10:19:35Z | Staged checkpoint reviewed and approved by user; digest `96b81c88...2a755f` verified at continuation | AES KAT green; PRF equality green; core callable end-to-end |
| PLAN-00003-STEP-10 | completed | 2026-09-07T10:19:35Z | 2026-09-07T11:07:39Z | Staged checkpoint reviewed and approved by user; digest `f696bab3...4d60562` verified at continuation | backend keyword live; validation parity asserted; 100% floor held |
| PLAN-00003-STEP-11 | completed | 2026-09-07T11:07:39Z | 2026-09-07T13:57:57Z | Staged checkpoint reviewed and approved by user; digest `c740887d...354a2a` verified at continuation | 1,388 dual-backend tests green; per-round intermediates bit-exact on both backends |
| PLAN-00003-STEP-12 | not-started | — | — | — | — |
| PLAN-00003-STEP-13 | not-started | — | — | — | — |
| PLAN-00003-STEP-14 | not-started | — | — | — | — |
| PLAN-00003-STEP-15 | not-started | — | — | — | — |

Allowed status values: `not-started`, `in-progress`, `blocked`, `completed`,
`skipped`. A skipped step requires explicit user approval recorded in Evidence.

### Execution log

| Timestamp (UTC) | Step | Event | Evidence or reference | Next action |
|---|---|---|---|---|
| 2026-09-06T22:03:07Z | PLAN-00003-STEP-01 | Execution started: branch `feature/accelerated-backend-pure-python-then-rust` created from approved-plan start commit `820cf50`; hand-off validation passed (clean gate, approval commit verified, baseline fresh — only plan paths changed since `5f24158`) | `git log --oneline`; `git status --porcelain` empty | Implement STEP-01 test scaffolding |
| 2026-09-06T22:10:28Z | PLAN-00003-STEP-01 | STEP-01 implemented and verified: new `tests/test_conversion_equivalence.py` (88 tests) — differential vs an independent in-test transcription of the naive loops across every supported radix (2..65535), threshold-boundary lengths 63/64/65/128/129 at representative radices, degenerate lengths 0–3, STR truncation contract, Hypothesis sampling to length 300, end-to-end FF1 round-trips at boundary lengths, plus a pinning test for the retained `_ff1` reference names STEP-02 will introduce (resolved via typed `getattr`, `None` until then). Design note: the oracle is transcribed inside the test module rather than imported from `_ff1`, so it cannot drift with the code under test — a stronger guarantee than the plan's minimum. Full gate green: format, lint, pyright strict (0 errors), 839 tests passed, 100% line/branch coverage. Checkpoint staged for review: implementation paths `tests/test_conversion_equivalence.py`; staged-diff SHA-256 `a517ad5c5bce43dcb63f644a1ca698a66e5fa426c6f1314775fdb1e2a5159feb`; proposed commit subject `build: complete PLAN-00003-STEP-01 - E1 test scaffolding (failing first)` | Verification results below | Awaiting user review; on continuation, commit STEP-01 and begin STEP-02 |
| 2026-09-06T22:18:22Z | PLAN-00003-STEP-01 | User approved the staged checkpoint ("Step 1 Approved. Proceed to the next step."); staged-checkpoint gate re-verified (branch, HEAD `820cf50`, staged set, digest match, no unstaged/untracked changes); commit authorised | This entry | Commit STEP-01, then begin STEP-02 |
| 2026-09-06T22:23:50Z | PLAN-00003-STEP-02 | STEP-02 implemented and verified: `_ff1.py` conversion replaced with subquadratic divide-and-conquer (`_num_radix_split`/`_str_radix_split`, 64-numeral threshold, call-local memoised `radix**k` cache with the REQ-05 thread-safety constraint stated in `_radix_power`'s docstring); naive loops retained as `_num_radix_reference`/`_str_radix_reference` with spec-reference docstrings (REQ-03). The STEP-01 differential suite (88 tests, incl. the retained-copy pinning test now live) passes bit-identical across every supported radix. Full gate green: format, lint, pyright strict (0 errors), 839 tests, 100% line/branch coverage (252 stmts, 78 branches). Benchmark preview: n=20,000 radix 10 at 1.4 µs/numeral (was 26.8 µs, ~19×), n=5,000 at 1.1 µs (was 7.0 µs, ~6×), n=6 unchanged at 29.3 µs — matching review 00005's measurements; no small-input regression. Checkpoint staged for review: implementation path `src/fpr_ff1/_ff1.py`; staged-diff SHA-256 below; proposed commit subject `build: complete PLAN-00003-STEP-02 - Divide-and-conquer conversion`. Staged-diff SHA-256 for `src/fpr_ff1/_ff1.py`: `06a9a47c182cda31d0615a20f76bd00de1bd18a50576b2718741966862131e7e` | Verification results below | Awaiting user review; on continuation, commit STEP-02 and begin STEP-03 |
| 2026-09-06T22:29:26Z | PLAN-00003-STEP-02 | User approved the staged checkpoint ("Approved. Proceed to the next step."); staged-checkpoint gate re-verified (branch, HEAD `7363269`, staged set, digest match, no unstaged/untracked changes); commit authorised | This entry | Commit STEP-02, then begin STEP-03 |
| 2026-09-06T22:34:52Z | PLAN-00003-STEP-03 | STEP-03 implemented and verified: O(n) power-of-two fast path added (`_pow2_exponent` via exact `bit_length`, `_num_radix_pow2`/`_str_radix_pow2` byte-group packing through `int.to_bytes`/`int.from_bytes`, truncation contract reproduced via an O(n) mask). Dispatch: ≤64 numerals → reference loop (small-input hot path unchanged); power-of-two radix → fast path; else → D&C split. Differential suite (88 tests) bit-identical across every supported radix incl. all power-of-two radices and the truncation contract. Full gate green: format, lint, pyright strict (0 errors), 839 tests, 100% line/branch coverage (295 stmts, 96 branches). Benchmark: radix 256 n=20,000 encrypt 1,114 ms → 43.7 ms (~25× end-to-end; conversion now negligible, remaining cost is the ten PRF calls over ~20 KB inputs — the O(n) goal); radix 2: 148 → 12.1 ms (~12×); radix 65535 (D&C path): 2,464 → 150.6 ms (~16×). Checkpoint staged for review: implementation path `src/fpr_ff1/_ff1.py`; proposed commit subject `build: complete PLAN-00003-STEP-03 - Power-of-two fast path`. Staged-diff SHA-256 for `src/fpr_ff1/_ff1.py`: `c17a5c00c2c209cd4cdc82587482bfc0c4fb8e1df507bce9dd0090fb3d2a32be` | Verification results below | Awaiting user review; on continuation, commit STEP-03 and begin STEP-04 |
| 2026-09-06T22:38:11Z | PLAN-00003-STEP-03 | User approved the staged checkpoint ("Approved. Proceed to the next step."); staged-checkpoint gate re-verified (branch, HEAD `526e01d`, staged set, digest match, no unstaged/untracked changes); commit authorised | This entry | Commit STEP-03, then begin STEP-04 |
| 2026-09-06T22:42:34Z | PLAN-00003-STEP-04 | STEP-04 executed: full quality gate re-run green (839 tests, 100% line/branch coverage, 295 stmts/96 branches; ruff format/lint clean; pyright strict 0 errors) and the complete `benchmarks/timing.py` output captured as the E1 evidence baseline. Results vs the v1.0.0 README baseline: 6 numerals radix 10: 30.9 → 29.1 µs/op (unchanged within noise — no small-input regression); n=100: 1.2 → 1.1 µs; n=1,000: 1.6 → 1.0 µs (~1.6×); n=5,000: 7.0 → 1.1 µs (~6.4×); n=20,000: 26.8 → 1.4 µs/numeral (~19×); radix 256 n=20,000 encrypt: 1,114 → 43.7 ms (~25×). Value-dependent timing deltas within ±3.2% — no constant-time posture change. Ciphertext-identity evidence: the frozen KAT, interoperability (ubiq byte-identical both directions), NIST vector, per-round intermediate, differential-oracle, and bijectivity suites all passed unmodified within the 839-test gate. These numbers are the README table input for STEP-05 and the E2 comparison baseline for STEP-13. No code changed in this step; staged checkpoint is the plan work log only. Proposed commit subject `build: complete PLAN-00003-STEP-04 - E1 full verification and benchmark` | Verification results below | Awaiting user review; on continuation, commit STEP-04 and begin STEP-05 |
| 2026-09-06T22:46:35Z | PLAN-00003-STEP-04 | User approved the staged checkpoint ("Approved. Proceed to the next step."); staged-checkpoint gate re-verified (branch, HEAD `f4bcf4c`, plan-only staged set, no unstaged/untracked changes); commit authorised | This entry | Commit STEP-04, then begin STEP-05 |
| 2026-09-06T22:47:28Z | PLAN-00003-STEP-05 | STEP-05 implemented and verified: README §Performance rewritten — the "inherent to the algorithm's NUM/STR steps" claim is gone, replaced by the corrected implementation-choice explanation with the 1.1.0 numbers (29.1 µs at n=6; flat 1.0–1.4 µs/numeral to n=20,000); roadmap table gains the 1.1 row and the 2.0 row is re-scoped to the small-input regime (review 00005 MED-04 both halves). CHANGELOG 1.1.0 entry (performance release, ciphertext bit-identical, Changed + Unchanged sections). `docs/backlog.md`: 2.0 item re-scoped to small-input with the 1.1 baseline; E1 completion recorded. `pyproject.toml` version → 1.1.0; `uv.lock` re-recorded the local package version (verified: single-line version diff). Checked `docs/architecture.md` and `docs/developer-guide.md` for stale performance claims — none found, no changes needed. Gate green: ruff format/lint, pyright strict 0 errors, 837 fast tests, `uv build` produces `fpr_ff1-1.1.0` sdist + wheel. Checkpoint staged for review: implementation paths `README.md`, `CHANGELOG.md`, `docs/backlog.md`, `pyproject.toml`, `uv.lock`; proposed commit subject `build: complete PLAN-00003-STEP-05 - E1 documentation and version 1.1.0`. Staged-diff SHA-256 for the implementation paths (`README.md`, `CHANGELOG.md`, `docs/backlog.md`, `pyproject.toml`, `uv.lock`): `c088c8243b9df503ddac244d61c00595cf648c84903ae82337c82928de6d7faa` | Verification results below | Awaiting user review; on continuation, commit STEP-05 and begin STEP-06 |
| 2026-09-06T22:52:37Z | PLAN-00003-STEP-05 | User approved the staged checkpoint ("Step 5 Approved. Should I tag/push/publish now?"); staged-checkpoint gate re-verified (branch, HEAD `08f44b5`, staged set, digest match, no unstaged/untracked changes); commit authorised | This entry | Commit STEP-05, then begin STEP-06 (release preparation; tag/push/publish are user actions) |
| 2026-09-07T00:00:10Z | PLAN-00003-STEP-06 | STEP-06 executed. User performed the release actions (merge to main via PR #4 `67cf45a`, signed tag `v1.1.0` on `67cf45a`, GitHub release, release-gated publish). Builder verified the outcome: PyPI JSON API shows `fpr-ff1 1.1.0` live (wheel `fpr_ff1-1.1.0-py3-none-any.whl` sha256 `96712893...a9040`, sdist `fpr_ff1-1.1.0.tar.gz` sha256 `06f694bd...eece6`, both uploaded 2026-09-06T23:58 UTC, not yanked, core-metadata/provenance attestations present on both); the published README on PyPI is the corrected 1.1.0 text (roadmap 1.1 row, flat performance table); tag `v1.1.0` points at `67cf45a` (main tip); publication through `publish.yml` proves the full 9-leg CI matrix passed as the release gate. Matrix bench numbers: the release-gated CI run is the matrix execution; the README table carries the single-machine numbers with the `just bench` reproduction pointer per the plan's evidence rules. Note: the E1 work reached main via squash-merge PR #4, and `plan/v2.0.0` was subsequently merged with main (merge commit `be566ab`, conflicts in `docs/backlog.md` and this plan file resolved by the user with Builder consultation — resolution kept main's Builder state and E1 backlog bullet; merged tree verified byte-identical to main). Checkpoint staged for review: plan work log only; proposed commit subject `build: complete PLAN-00003-STEP-06 - Release v1.1.0` | Verification results below | Awaiting user review; on continuation, commit STEP-06 — this closes stage E1; E2 (STEP-07) begins after |
| 2026-09-07T00:05:12Z | PLAN-00003-STEP-06 | User approved the staged checkpoint ("Approved. Proceed to the next step."); staged-checkpoint gate re-verified (branch `plan/v2.0.0`, HEAD `be566ab`, plan-only staged set, no unstaged/untracked changes); commit authorised. E1 stage closed: steps 01–06 complete, v1.1.0 published | This entry | Commit STEP-06, then begin STEP-07 (crate-fit microbenchmark) |
| 2026-09-07T00:07:24Z | PLAN-00003-STEP-07 | STEP-07 executed: throwaway crate-fit microbenchmark (Rust 1.97.1, `num-bigint` 0.4.8 + `num-traits` 0.2, release profile; scratch project in `/tmp/opencode/crate-fit`, never committed) vs CPython 3.12 `int` control at identical operand shapes. **Representability:** 10**10000−1 = 33,220 bits ✓ (the n=20,000 radix-10 half), 10**20000−1 = 66,439 bits ✓ (full input), 65535**20000−1 = 320,000 bits ✓ (widest practical radix case) — all fit with headroom. **Speed at the FF1 conversion shapes (~33.2k-bit value, ~16.6k-bit divisor):** divmod 186.9 µs (Rust) vs 386.3 µs (CPython) — Rust 2.1× faster; mul+shift combine 50.8 µs vs 166.5 µs — Rust 3.3× faster. **Decision recorded:** `num-bigint` fits and is competitive; idea r02 LOW-01's collapse condition does NOT trigger; representation choice for the Rust core is `num-bigint` (BigUint). The binding go/no-go remains the STEP-13 park rule (measured ≥2× vs E1 at n ∈ {6, 100}). Checkpoint staged for review: plan work log only (benchmark is throwaway, no repository paths); proposed commit subject `build: complete PLAN-00003-STEP-07 - Crate-fit microbenchmark` | Verification results below | Awaiting user review; on continuation, commit STEP-07 and begin STEP-08 |
| 2026-09-07T00:08:50Z | PLAN-00003-STEP-07 | User approved the staged checkpoint ("Approved. Proceed to the next step."); staged-checkpoint gate re-verified (branch `plan/v2.0.0`, HEAD `4536151`, plan-only staged set, no unstaged/untracked changes); commit authorised | This entry | Commit STEP-07, then begin STEP-08 (Rust workspace and Algorithm 7 port) |
| 2026-09-07T00:19:49Z | PLAN-00003-STEP-08 | STEP-08 implemented and verified: Rust workspace `rust/` (workspace + crate `fpr-ff1-rust`, lib `_fpr_ff1_rs`, cdylib, `publish = false`) with committed `Cargo.lock` pinning pyo3 0.29.2 / num-bigint / num-traits / num-integer / aes / cbc. Algorithm 7 ported in `rust/fpr-ff1-rust/src/lib.rs` mirroring `_ff1.py` step-for-step with the same spec-step comments: u/v split, b from v via exact `(radix**v - 1).bits()` (no floats anywhere), d = 4·ceil(b/4)+4, P block, hoisted radix**u / radix**v, ten rounds with the three encrypt/decrypt differences only (Q source, round order, final swap) and the parity rule identical, S truncated to d bytes, decrypt subtraction via the +modulus reduction. Numerals are `u16` throughout (the radix < 2**16 subset). **Seams:** `prf` (Algorithm 6 CBC-MAC) and `cipher_block` (single forward block for the 6.iii expansion — kept DISTINCT from the PRF per the AGENTS.md warning that the expansion is not a PRF) are declared with per-call-context contracts and `unreachable!` bodies; STEP-09 wires them to RustCrypto and owns their NIST-AES-KAT + PRF-equality validation (plan sequencing, nothing skipped). 6 unit tests green (conversion decode/encode/truncate, round-trip across radices 2..65535 and lengths to 130, b-from-v-not-u, padding, radix bounds); zero build warnings. **The tests caught a real port bug during the step:** `rem_euclid` on the positive sum replicated the padding wrongly — Python's `(-t-b-1) % 16` negates BEFORE reducing; fixed in the port and the test. A wrong test constant (radix 65535 expectation) was also corrected against a hand computation — the implementation had been right. Bounded decisions: pyo3 bumped 0.23→0.29 for local Python 3.14 support; `pyproject.toml` build configuration deferred wholesale to STEP-14 (switching the build backend before the extension is integrated would break `uv build` and the sdist pipeline mid-plan); `.gitignore` gained `rust/target/`; justfile gained `rust-test` (verified via its underlying `cargo test` — `just` is not on the Builder shell's PATH). Note: session was interrupted by a usage limit mid-step; state re-verified on resume (git status matched exactly this step's files) before continuing. Checkpoint staged for review: implementation paths `.gitignore`, `justfile`, `rust/Cargo.toml`, `rust/Cargo.lock`, `rust/fpr-ff1-rust/Cargo.toml`, `rust/fpr-ff1-rust/src/lib.rs`, `rust/fpr-ff1-rust/src/tests.rs`; proposed commit subject `build: complete PLAN-00003-STEP-08 - Rust workspace and Algorithm 7 port`. Staged-diff SHA-256 for the implementation paths (`.gitignore`, `justfile`, `rust/Cargo.toml`, `rust/Cargo.lock`, `rust/fpr-ff1-rust/Cargo.toml`, `rust/fpr-ff1-rust/src/lib.rs`, `rust/fpr-ff1-rust/src/tests.rs`): `1ac143c87027a6bddde57bf1bfd9f488e91d9ae068431a247338b2ede2e0e0cf` | Verification results below | Awaiting user review; on continuation, commit STEP-08 and begin STEP-09 |
| 2026-09-07T00:29:15Z | PLAN-00003-STEP-08 | User approved the staged checkpoint ("Approved. Proceed to the next step."); staged-checkpoint gate re-verified (branch `plan/v2.0.0`, HEAD `5686907`, staged set, digest match `1ac143c8...`, no unstaged/untracked changes); commit authorised | This entry | Commit STEP-08, then begin STEP-09 (Rust PRF and AES validation) |
| 2026-09-07T08:41:15Z | PLAN-00003-STEP-09 | STEP-09 implemented and verified. **Evidence first:** the three FIPS 197 Appendix C KAT ciphertexts were cross-verified against the OpenSSL-backed `cryptography` package (MATCH ×3) BEFORE being frozen into `tests/vectors/aes_kat_fips197.json` with a provenance header — never generated from this repository. **Rust wiring:** the STEP-08 seams are now real — `Aes` key-schedule enum over RustCrypto Aes128/192/256 (immutable, thread-safe by construction, mirroring `_Aes`), `prf` as a six-line CBC-MAC zero-IV XOR chain, `cipher_block` as the raw forward block; `ff1` call sites updated; test-only PyO3 bindings `_test_prf`/`_test_cipher_block` exposed (off the public API, `_encrypt_traced`-style). Bounded decision: the `cbc` crate was dropped — the manual chain is the spec-literal CBC-MAC and the wrapper would need one concrete instantiation per key size anyway (smaller supply-chain surface; Cargo.lock updated). **Dev loop:** `just backend-dev` (VIRTUAL_ENV=.venv `uvx maturin develop`, no uv.lock churn); a standalone `rust/fpr-ff1-rust/pyproject.toml` was required — without it maturin walked up to the repo-root pyproject and built a mixed wheel that shipped no importable extension. **Validation:** `tests/test_rust_aes_validation.py` — 3 KAT + 15 PRF-equality vs the reference `_prf` (key sizes 16/24/32 × block counts 1–5) + 1 shared data-sensitivity; availability mirrors the oracle contract (`FPR_FF1_REQUIRE_RUST_BACKEND`; CI wiring at STEP-14). Rust unit tests grew to 8, including full-core round-trip self-consistency (all key sizes, odd n, both `d > 16` S-expansion cases — the core is callable end-to-end for the first time). **Gates:** cargo test 8 green; validation module 19 green; full gate 858 passed with 100% line/branch coverage (295 stmts/96 branches; no `fpr_ff1` source changed); ruff/pyright clean. A missing `import os` in the new test module was caught on self-review after the interruption and fixed before any test run. Second usage-limit interruption mid-step; state verified on resume (git status matched exactly this step's files). Checkpoint staged for review: implementation paths `justfile`, `rust/Cargo.lock`, `rust/fpr-ff1-rust/Cargo.toml`, `rust/fpr-ff1-rust/pyproject.toml`, `rust/fpr-ff1-rust/src/lib.rs`, `rust/fpr-ff1-rust/src/tests.rs`, `tests/test_rust_aes_validation.py`, `tests/vectors/aes_kat_fips197.json`; proposed commit subject `build: complete PLAN-00003-STEP-09 - Rust PRF and AES validation`. Staged-diff SHA-256 for the implementation paths (`justfile`, `rust/Cargo.lock`, `rust/fpr-ff1-rust/Cargo.toml`, `rust/fpr-ff1-rust/pyproject.toml`, `rust/fpr-ff1-rust/src/lib.rs`, `rust/fpr-ff1-rust/src/tests.rs`, `tests/test_rust_aes_validation.py`, `tests/vectors/aes_kat_fips197.json`): `96b81c8873e6a6d503cf227788a177082319631c2a93947e0d1b9097312a755f` | Verification results below | Awaiting user review; on continuation, commit STEP-09 and begin STEP-10 |
| 2026-09-07T10:19:35Z | PLAN-00003-STEP-09 | User approved the staged checkpoint ("Approved. Proceed to the next step."); staged-checkpoint gate re-verified (branch `plan/v2.0.0`, HEAD `afe9950`, staged set, digest match `96b81c88...`, no unstaged/untracked changes); commit authorised | This entry | Commit STEP-09, then begin STEP-10 (Python integration: backend keyword and dispatch) |
| 2026-09-07T10:37:31Z | PLAN-00003-STEP-10 | STEP-10 implemented and verified (TDD: red run confirmed `BackendError` missing before implementation). **New exception:** `BackendError(FF1Error)` in `_exceptions.py`, exported from `__all__` (REQ-19: every backend rejection roots at `FF1Error`). **Constructor:** keyword-only `backend: str = "python"` (REQ-13), validated type-then-value like every other parameter; `"rust"` fails fast via `_load_rust_backend()` (typed `BackendError` with remedy message, never an opaque `ImportError`). **Dispatch:** `encrypt_numerals`/`decrypt_numerals` route to `_rust_ff1` after `_prepare` — validation runs in Python for both backends (D4/REQ-18), so exception types AND messages are identical (asserted by parity tests). The extension is stateless; per-call `sys.modules` lookup adds no shared mutable state. **Pickling:** `_backend` rides the pickled `__dict__`; `__setstate__` defaults missing `_backend` to `"python"` (1.x pickles unpickle cleanly), rejects non-str and unknown values, and re-validates rust availability on the far side. **No top-level extension import** — the package imports fine without it (REQ-19 by construction). **Tests:** `tests/test_backend_dispatch.py`, 16 tests: default/explicit-python equality, unknown + non-str backend raises, missing-extension (simulated via `sys.modules` None-entry) raises, rust-vs-python bit-for-bit equality across radices 10/36/256 and n ∈ {6,7,60} (odd n and the d>16 expansion), string-interface dispatch, validation parity (length/range/tweak, message-identical), rust pickle round-trip, legacy-state default, corrupt-state rejection (both non-str and unknown value — the second added when the coverage floor caught the untested raise). Availability mirrors the oracle contract (`FPR_FF1_REQUIRE_RUST_BACKEND`; CI wiring at STEP-14). One test bug fixed during the red-green cycle (min_tweak_len construction needs a compliant default tweak). **Gates:** 874 passed, 100% line/branch coverage (327 stmts, 112 branches), ruff/pyright clean; NIST/KAT/interoperability suites passed unmodified within the gate — the pure-Python path is unchanged when `backend` is not passed. Checkpoint staged for review: implementation paths `src/fpr_ff1/__init__.py`, `src/fpr_ff1/_exceptions.py`, `src/fpr_ff1/_ff1.py`, `tests/test_backend_dispatch.py`; proposed commit subject `build: complete PLAN-00003-STEP-10 - Python integration: backend keyword and dispatch`. Staged-diff SHA-256 for the implementation paths (`src/fpr_ff1/__init__.py`, `src/fpr_ff1/_exceptions.py`, `src/fpr_ff1/_ff1.py`, `tests/test_backend_dispatch.py`): `f696bab3065bf3d51a4e1c2ccb2319fd9b6e063e2bdca8ea2321d62ab4d60562` | Verification results below | Awaiting user review; on continuation, commit STEP-10 and begin STEP-11 |
| 2026-09-07T11:07:39Z | PLAN-00003-STEP-10 | User approved the staged checkpoint ("Approved. Proceed to the next step.") and instructed that the step-body **Status placeholder** lines (section 11) be kept current; staged-checkpoint gate re-verified (branch `plan/v2.0.0`, HEAD `095ad3a`, staged set, digest match `f696bab3...`, no unstaged/untracked changes); commit authorised. Status placeholders synced under explicit user instruction (steps 01–10 → `completed`, 11 → `in-progress`; recorded here as the authorization; Builder keeps them current at every checkpoint from now on) | This entry | Commit STEP-10, then begin STEP-11 (trace bridge and dual-backend conformance) |
| 2026-09-07T11:34:20Z | PLAN-00003-STEP-11 | STEP-11 implemented and verified. **Rust trace bridge:** the core was refactored to a single `ff1_impl` with an optional `&mut Vec<TraceRecord>` collector — one code path serves production and traced entry points, mirroring `_ff1`'s `_trace` parameter, so traced and untraced cores cannot drift. `_test_encrypt_traced` returns per-round dicts (i, u, v, b, d, P, Q, R, S, y, m, c, C); y/c travel as big-endian bytes (BigUint has no pyo3 mapping) and the Python-side `encrypt_traced` fixture normalizes them (and P/Q/R/S to lists) to the Python hook's exact shape. **Parameterisation:** conftest gained `backend` (params python + rust-when-built, with the `FPR_FF1_REQUIRE_RUST_BACKEND` hard-fail contract), `ff1_factory`, and `encrypt_traced` fixtures. Parameterised modules: NIST vectors (3 tests), per-round intermediates, frozen KAT reproduce, differential (7 oracle-comparison families; the oracle self-validation stays unparameterised — it validates the oracle), interoperability (3 migration-safety tests), properties (backend drawn per Hypothesis case; bijectivity parametrised), exact-arithmetic trace tests (b-from-v, padding, pow2 round-trip). **Zero assertion changes** — only construction routes through the factory. **Bugs found and fixed during the step:** (1) the bridge initially left P/Q/R/S as bytes — the per-round intermediate tests caught the shape mismatch immediately (the values were bit-identical; the bridge now normalizes); (2) `_migrated` passed positional args to the keyword-only factory (36 interop failures → fixed); (3) assorted lint/type fixes (unused imports, PLR0917 noqa on the 6-arg parametrised test, conftest typed-extension boundary via cast). **Gates:** full dual-backend suite **1,388 passed** (up from 874), 100% line/branch coverage (327 stmts, 112 branches), ruff/pyright clean, cargo test 8 green. The per-round intermediates now assert bit-exact on BOTH backends for all nine NIST samples — the project's strongest correctness evidence covers the second implementation. Checkpoint staged for review: implementation paths `rust/fpr-ff1-rust/src/lib.rs`, `tests/conftest.py`, `tests/test_differential.py`, `tests/test_exact_arithmetic.py`, `tests/test_frozen_kat.py`, `tests/test_intermediates.py`, `tests/test_interoperability.py`, `tests/test_nist_vectors.py`, `tests/test_properties.py`; proposed commit subject `build: complete PLAN-00003-STEP-11 - Trace bridge and dual-backend conformance`. Staged-diff SHA-256 for the implementation paths (`rust/fpr-ff1-rust/src/lib.rs`, `tests/conftest.py`, `tests/test_differential.py`, `tests/test_exact_arithmetic.py`, `tests/test_frozen_kat.py`, `tests/test_intermediates.py`, `tests/test_interoperability.py`, `tests/test_nist_vectors.py`, `tests/test_properties.py`): `c740887d9d201d7fb41acc447982a6a6835b2d57c9068a9d2fe1515971354a2a` | Verification results below | Awaiting user review; on continuation, commit STEP-11 and begin STEP-12 |
| 2026-09-07T13:57:57Z | PLAN-00003-STEP-11 | User approved the staged checkpoint ("Step 11 approved. Proceed to the next step."); staged-checkpoint gate re-verified (branch `plan/v2.0.0`, HEAD `a3f34ae`, staged set, digest match `c740887d...`, no unstaged/untracked changes); commit authorised. **Placeholder correction for the record:** the STEP-10-turn status-placeholder sync marked line 992 — STEP-12's placeholder — `in-progress` one step early (STEP-11's placeholder is line 958); the committed STEP-10 checkpoint (a3f34ae) therefore carries that one-line mis-sync. Corrected state as of this entry: STEP-11 → `completed` (line 958), STEP-12 → `in-progress` (line 992, now legitimately so). No planning content was affected | This entry | Commit STEP-11, then begin STEP-12 (thread-safety and pickling for the rust backend) |

### Deviations and blockers

| Timestamp (UTC) | Step | Deviation or blocker | Impact | Decision required from |
|---|---|---|---|---|

Write `None` until an entry is required.

### Verification results

| Timestamp (UTC) | Step | Command or check | Result | Evidence |
|---|---|---|---|---|
| 2026-09-07T00:00:10Z | PLAN-00003-STEP-06 | PyPI JSON API `https://pypi.org/pypi/fpr-ff1/json` | `1.1.0` live: wheel + sdist uploaded 2026-09-06T23:58 UTC, not yanked, provenance attestations (core-metadata) on both artifacts; published README is the corrected 1.1.0 text | Release verified from the PyPI API response |
| 2026-09-07T00:00:10Z | PLAN-00003-STEP-06 | `git rev-parse v1.1.0^{commit}` / `git log --oneline -1 v1.1.0` | Tag points at `67cf45a` ("Feature/accelerated backend pure python then rust (#4)"), main's tip | Tag-to-release consistency |
| 2026-09-07T00:00:10Z | PLAN-00003-STEP-06 | Release-gate inference | `publish.yml` publishes only after its quality job (re-running `ci.yml`, the 9-leg matrix) passes; a live PyPI release therefore proves the matrix green | `publish.yml` workflow structure |
| 2026-09-07T00:07:24Z | PLAN-00003-STEP-07 | `cargo run --release` (crate-fit scratch project, num-bigint 0.4.8) | Representability: 33,220 / 66,439 / 320,000-bit values all constructible and asserted; divmod 186.9 µs/op, mul+shift 50.8 µs/op at the ~33.2k/~16.6k-bit FF1 shapes (200 iterations) | Rust-side measurement |
| 2026-09-07T00:07:24Z | PLAN-00003-STEP-07 | CPython control (`uv run python`, same operand construction, 200 iterations) | divmod 386.3 µs/op, mul+shift 166.5 µs/op — Rust is 2.1× / 3.3× faster at the same shapes | Control-side measurement; comparison answers review 00005 Open question 4 |
| 2026-09-07T00:19:49Z | PLAN-00003-STEP-08 | `cargo test --manifest-path rust/Cargo.toml` | 6 passed, 0 failed (conversion, round-trip, b-from-v, padding, radix bounds) | Port structure verified; padding-sign bug found and fixed by these tests |
| 2026-09-07T00:19:49Z | PLAN-00003-STEP-08 | `cargo build --manifest-path rust/Cargo.toml` | 0 warnings | Clean build after full recompile |
| 2026-09-07T00:19:49Z | PLAN-00003-STEP-08 | `just rust-test` recipe | Verified via its underlying command (`cargo test`, green); `just` not on the Builder shell's PATH | Recipe is a one-line wrapper |
| 2026-09-07T00:19:49Z | PLAN-00003-STEP-08 | `uv run pytest -m 'not slow' --no-cov -q` / `ruff format --check .` / `ruff check .` | 837 passed, 2 deselected; 45 files formatted; all checks passed | No Python-side interference from the new workspace |
| 2026-09-07T08:41:15Z | PLAN-00003-STEP-09 | KAT constant cross-check (`cryptography` AES-ECB, OpenSSL-backed) | FIPS 197 C.1/C.2/C.3 ciphertexts all MATCH before freezing | Evidence-first: constants never trusted from memory |
| 2026-09-07T08:41:15Z | PLAN-00003-STEP-09 | `cargo test --manifest-path rust/Cargo.toml` | 8 passed, 0 failed | Includes full-core round-trip self-consistency and PRF structural properties |
| 2026-09-07T08:41:15Z | PLAN-00003-STEP-09 | `uv run pytest tests/test_rust_aes_validation.py -v` | 19 passed (3 KAT, 15 PRF-equality, 1 sensitivity) | AES KAT green; PRF equality green — STEP-09 completion criteria met |
| 2026-09-07T08:41:15Z | PLAN-00003-STEP-09 | `just backend-dev` underlying command (`VIRTUAL_ENV=.venv uvx maturin develop`) | Extension imports as `_fpr_ff1_rs` with surface `_test_prf`, `_test_cipher_block`, `encrypt_numerals`, `decrypt_numerals`; Python package intact at 1.1.0 | Dev loop verified end-to-end |
| 2026-09-07T08:41:15Z | PLAN-00003-STEP-09 | `uv run ruff format --check .` / `ruff check .` / `uv run pyright` / full coverage gate | Clean; 0 errors, 0 warnings; 858 passed, 100% line/branch coverage (353.8 s) | No `fpr_ff1` source changed; floor unaffected by construction |
| 2026-09-07T10:37:31Z | PLAN-00003-STEP-10 | Red run: `uv run pytest tests/test_backend_dispatch.py -q` | ImportError: cannot import name 'BackendError' — the expected missing behaviour, not a syntax/environment failure | TDD red phase recorded |
| 2026-09-07T10:37:31Z | PLAN-00003-STEP-10 | `uv run pytest tests/test_backend_dispatch.py -q` | 16 passed (after one test fix: min_tweak_len construction needs a compliant default tweak) | Green phase |
| 2026-09-07T10:37:31Z | PLAN-00003-STEP-10 | `uv run ruff format --check .` / `ruff check .` / `uv run pyright` | Clean; 0 errors, 0 warnings | Whole project |
| 2026-09-07T10:37:31Z | PLAN-00003-STEP-10 | `uv run pytest --cov=fpr_ff1 --cov-report=term-missing --cov-fail-under=100` | 874 passed; 100% line/branch coverage (327 stmts, 112 branches, 0 missed) — the floor caught one untested raise (non-str unpickled backend), test added, re-run green | Full gate incl. slow sweeps (352.1 s) |
| 2026-09-07T11:34:20Z | PLAN-00003-STEP-11 | `uv run pytest tests/test_intermediates.py tests/test_nist_vectors.py tests/test_exact_arithmetic.py -q` | 107 passed — per-round intermediates bit-exact on both backends (after the bridge byte-field normalisation fix) | Strongest conformance evidence now dual-backend |
| 2026-09-07T11:34:20Z | PLAN-00003-STEP-11 | `uv run pytest tests/test_frozen_kat.py tests/test_differential.py tests/test_interoperability.py tests/test_properties.py -q` | 36 interop failures from a factory-call bug → fixed → all green; frozen KAT, differential, properties green on both backends | Parameterisation bugs were test-side, never core-side |
| 2026-09-07T11:34:20Z | PLAN-00003-STEP-11 | `cargo test --manifest-path rust/Cargo.toml` | 8 passed, 0 failed | Traced refactor kept the Rust unit suite green |
| 2026-09-07T11:34:20Z | PLAN-00003-STEP-11 | `uv run ruff format --check .` / `ruff check .` / `uv run pyright` | Clean; 0 errors, 0 warnings | Whole project |
| 2026-09-07T11:34:20Z | PLAN-00003-STEP-11 | `uv run pytest --cov=fpr_ff1 --cov-report=term-missing --cov-fail-under=100` | **1,388 passed**; 100% line/branch coverage (327 stmts, 112 branches, 0 missed) | Full dual-backend gate incl. slow bijectivity sweeps on both backends (564.7 s) |
| 2026-09-06T22:10:28Z | PLAN-00003-STEP-01 | `uv run pytest tests/test_conversion_equivalence.py -v` | 87 passed → 88 passed after rewrite (0.62–0.84 s) | Focused run; all differential, boundary, degenerate, truncation, property, and end-to-end cases green |
| 2026-09-06T22:10:28Z | PLAN-00003-STEP-01 | `uv run pytest -m 'not slow' --no-cov -q` | 836 passed, 2 deselected (1.40 s) | No regression to the existing suite |
| 2026-09-06T22:10:28Z | PLAN-00003-STEP-01 | `uv run ruff format --check .` / `uv run ruff check .` | 45 files formatted; all checks passed | Includes the new module |
| 2026-09-06T22:10:28Z | PLAN-00003-STEP-01 | `uv run pyright` | 0 errors, 0 warnings | Strict mode, whole project |
| 2026-09-06T22:10:28Z | PLAN-00003-STEP-01 | `uv run pytest --cov=fpr_ff1 --cov-report=term-missing --cov-fail-under=100` | 839 passed; 100% line and branch coverage (223 stmts, 68 branches, 0 missed) | Full gate incl. slow bijectivity sweeps (197.9 s) |
| 2026-09-06T22:23:50Z | PLAN-00003-STEP-02 | `uv run pytest tests/test_conversion_equivalence.py -q` | 88 passed (0.71 s) | Differential suite green against the new D&C conversion — bit-identical across every supported radix, incl. the retained-reference pinning test |
| 2026-09-06T22:23:50Z | PLAN-00003-STEP-02 | `uv run ruff format --check .` / `uv run ruff check .` | 45 files formatted; all checks passed | One formatter reflow applied to `_ff1.py` |
| 2026-09-06T22:23:50Z | PLAN-00003-STEP-02 | `uv run pyright` | 0 errors, 0 warnings | Strict mode, whole project |
| 2026-09-06T22:23:50Z | PLAN-00003-STEP-02 | `uv run pytest --cov=fpr_ff1 --cov-report=term-missing --cov-fail-under=100` | 839 passed; 100% line and branch coverage (252 stmts, 78 branches, 0 missed) | New D&C branches covered by the STEP-01 boundary tests (224.9 s) |
| 2026-09-06T22:23:50Z | PLAN-00003-STEP-02 | `uv run python benchmarks/timing.py` | n=20,000 radix 10: 1.4 µs/numeral (baseline 26.8 µs, ~19×); n=5,000: 1.1 µs (was 7.0 µs); n=6: 29.3 µs (unchanged); value-dependent deltas ≤ 5.4% | D&C win realised, matching review 00005; no small-input regression |
| 2026-09-06T22:34:52Z | PLAN-00003-STEP-03 | `uv run pytest tests/test_conversion_equivalence.py -q` | 88 passed (0.66 s) | Differential green against the pow2 fast path — bit-identical across every supported radix incl. truncation contract |
| 2026-09-06T22:34:52Z | PLAN-00003-STEP-03 | `uv run ruff format --check .` / `uv run ruff check .` / `uv run pyright` | Clean; 0 errors, 0 warnings | Whole project |
| 2026-09-06T22:34:52Z | PLAN-00003-STEP-03 | `uv run pytest --cov=fpr_ff1 --cov-report=term-missing --cov-fail-under=100` | 839 passed; 100% line and branch coverage (295 stmts, 96 branches, 0 missed) | Pow2 branches covered by the differential radix sweep (213.7 s) |
| 2026-09-06T22:34:52Z | PLAN-00003-STEP-03 | Focused encrypt benchmark (timing.py methodology), radix 256/2/65535 at n=20,000 | radix 256: 1,114 ms → 43.7 ms (~25×); radix 2: 148 → 12.1 ms (~12×); radix 65535: 2,464 → 150.6 ms (~16×) | O(n) conversion goal met; residual radix-256 cost is PRF over ~20 KB inputs, not conversion |
| 2026-09-06T22:42:34Z | PLAN-00003-STEP-04 | `uv run pytest --cov=fpr_ff1 --cov-report=term-missing --cov-fail-under=100` | 839 passed; 100% line and branch coverage (218.5 s) | Formal STEP-04 gate run |
| 2026-09-06T22:42:34Z | PLAN-00003-STEP-04 | `uv run ruff format --check .` / `uv run ruff check .` / `uv run pyright` | Clean; 0 errors, 0 warnings | Whole project |
| 2026-09-06T22:42:34Z | PLAN-00003-STEP-04 | `uv run python benchmarks/timing.py` | Full output captured: 6 numerals 29.1 µs/op; construction 1.3 µs; n=100/1,000/5,000/20,000 radix 10 at 1.1/1.0/1.1/1.4 µs per numeral; value-dependent deltas ≤ 3.2% | E1 baseline recorded; feeds STEP-05 README table and STEP-13 E2 comparison |
| 2026-09-06T22:47:28Z | PLAN-00003-STEP-05 | `uv run ruff format --check .` / `uv run ruff check .` / `uv run pyright` | Clean; 0 errors, 0 warnings | Whole project |
| 2026-09-06T22:47:28Z | PLAN-00003-STEP-05 | `uv run pytest -m 'not slow' --no-cov -q` | 837 passed, 2 deselected (1.52 s) | Fast suite after docs + version bump |
| 2026-09-06T22:47:28Z | PLAN-00003-STEP-05 | `uv build` | sdist + wheel built as `fpr_ff1-1.1.0` | Version bump verified in build output |
| 2026-09-06T22:47:28Z | PLAN-00003-STEP-05 | `git diff uv.lock` | Single-line change: fpr-ff1 version 1.0.0 → 1.1.0 | Lock update is exactly the version bump |

### Completion summary

- **Implementation status:** `not-started`
- **Completed requirements:** None
- **Incomplete requirements:** All
- **Outstanding blockers:** None
- **Review request:** Not ready
<!-- BUILDER_WORK_LOG_END -->

## 18. Planning change log

| Timestamp (UTC) | Plan status | Change | Reason | Requested/approved by |
|---|---|---|---|---|
| 2026-09-06T18:07:27Z | draft | Initial draft published from idea 00001 r02 (user-authorised despite `status: revised`) and review 00005; combined E1-then-E2 scope; Rust backend build approved by user (D1–D3) | User request "read idea 00001 and draft a plan to implement a Rust backend" plus clarification answers | User |
| 2026-09-06T21:41:24Z | approved | Plan approved: `plan_status` → approved, `build_ready` → true, `approved_at` set; approval commit created | Explicit user approval | User |

## 19. External references

None. All requirements trace to the idea report, the review report,
repository instructions, and inspected repository code. The PyO3/maturin
claims relied on here are those already recorded (with URLs) in idea r01 §
References; this plan performed no new external research.

## 20. Confidence

**High.** Repository coverage is complete: the idea (both revisions), the
refuting review, the full FF1 core, packaging, CI, benchmark harness, tests,
and docs were inspected directly, and every load-bearing claim (quadratic
loops at `_ff1.py:463-477`, per-instance AES at `:223-227`, pickle/thread
contracts, coverage and CI gates) was verified against source. The principal
residual uncertainties are the *size* of the E1 win on other
interpreters/platforms (single-machine evidence; direction is not in doubt)
and the *unmeasured* E2 small-input speedup — both of which the plan converts
into recorded measurements with a pre-committed park rule rather than
assumptions.