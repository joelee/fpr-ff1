---
title: "Delivery Plan 00007: Stable v2.0.0 Release"
aliases:
  - "Plan 00007"
tags:
  - delivery-plan
  - implementation
  - claude-code
  - release
  - rust-backend
type: delivery-plan
plan_id: "PLAN-00007"
plan_status: approved
plan_kind: superseding
created_at: "2026-09-16T11:38:45Z"
approved_at: "2026-09-16T12:24:43Z"
planner_agent: claude-code
planner_model: "anthropic/claude-fable-5-1"
triggered_by: user
request_kind: review
repository: "joelee/fpr-ff1"
baseline_branch: "release/v2"
baseline_commit: "5eb518c3b0c58fe1e862a2512c07d37c2447d6bd"
source_ideas: []
source_reviews:
  - "docs/reviews/00007-V2_0_0_Stable_Release_Readiness.md"
  - "docs/reviews/00008-v2.0.0-plan-review.md"
  - "docs/reviews/00009-Plan_00006_Re_Review.md"
previous_plan: "docs/plans/00006-Review_00007_to_v2.0.0.md"
requirements_count: 13
steps_count: 14
acceptance_criteria_count: 14
blocking_decisions: 0
build_ready: true
web_research_used: false
confidence: high

# Builder-maintained front matter. Builder may update only these keys after
# explicit user approval; Delivery Planner initializes them.
implementation_status: in-progress
builder_agent: claude-code
builder_model: "anthropic/claude-opus-5"
execution_branch: "release/v2"
execution_started_at: "2026-09-16T12:32:08Z"
execution_updated_at: "2026-09-16T13:00:49Z"
execution_completed_at: null
current_step: "PLAN-00007-STEP-04"
---

# Delivery Plan 00007: Stable v2.0.0 Release

> [!abstract] Plan status: `approved`
> Close the four code findings of review 00007, ship the Rust divide-and-conquer conversion, make the release gate execute every published native wheel, publish and soak `v2.0.0rc2`, then promote a re-reviewed candidate to a stable `v2.0.0`. This plan rewrites draft plan 00006 to resolve all seven findings of reviews 00008 and 00009. All decisions are resolved (D4 chosen by the user on 2026-09-16: Option A, a bounded 1.1.x security-fix window); approved by the user on 2026-09-16; Builder-ready.

## 1. Objective and outcome

Review 00007 (`docs/reviews/00007-V2_0_0_Stable_Release_Readiness.md`, verdict `request-changes`) found one blocking compatibility defect and three smaller findings in `v2.0.0rc1`, and produced a twenty-item stable-release checklist (STABLE-01 to STABLE-20). Draft plan 00006 turned that checklist into twelve steps; review 00008 returned `request-changes` on the draft with seven findings, and review 00009 confirmed the draft was committed unamended with all seven still open. The user asked on 2026-09-16 for a new plan rather than an amendment. This plan is that rewrite: it keeps everything 00008 called sound (traceability, sequencing, stop conditions, the three defect requirements) and changes exactly what the seven findings asked for.

What changed from plan 00006, by finding:

| Review finding | Change in this plan |
|---|---|
| `REV-00008-MAJ-01` / `REV-00009-MAJ-01` — D4 recorded as resolved without a decided window | D4 was put to the user with three concrete `SECURITY.md` texts and resolved by the user (Option A, 2026-09-16); REQ-08 transcribes that text verbatim rather than inventing one |
| `REV-00008-MED-01` — no rc2 owner hand-off | New STEP-11: owner tags `v2.0.0rc2` as a pre-release, `publish.yml` runs, Builder verifies PyPI, owner states or waives the soak window (D6); STEP-12's precondition now names that step; §16 lists both tags |
| `REV-00008-MED-02` — STEP-06 under-specified | STEP-06 names runner labels per target, the fresh-venv install recipe, the two `__file__` import-origin checks as a numbered task, the four gate flags on the abi3 leg, the Python fan-out (D7), and an import-origin stop condition |
| `REV-00008-MED-03` — bounds/ceiling interaction and the `n` cast | REQ-02 rejects `min_tweak_len`/`max_tweak_len` above the ceiling at construction, converts both `n` and `t` with `u32::try_from`, adds the constructor cases to the contract sweep, and marks the changelog entry SemVer-relevant |
| `REV-00008-LOW-01` — no performance decision rule | STEP-05 carries a park rule (`rust <= python` at n = 20,000 on radix 10 and 256, else escalate) and the Rust threshold mirrors `_D_C_THRESHOLD = 64` by name (D9) |
| `REV-00008-LOW-02` — attribute-parity test, sibling tests | REQ-01 adds the structural `vars()` parity test and restores all three `__setstate__` tests onto `FF1.__new__(FF1)` |
| `REV-00008-LOW-03` — three STABLE sub-items dropped | STEP-10 runs the packaged tests from an unpacked sdist and records `rustc --version`; STEP-08 adds the Python-coverage-is-not-Rust-coverage wording |

Also picked up from 00009's open questions: the baseline is refreshed to the current `HEAD` (`5eb518c`, which adds only review 00009 to the `7e27017` the re-review examined), and the amending agent question is closed by this plan being a new numbered file (D8).

Outcome: a stable `v2.0.0` on PyPI whose pure-Python path is byte-identical to 1.1.0, whose opt-in `backend="rust"` path is bit-exact with the reference and no longer slower than it at long inputs, whose legacy 1.x pickles restore into working instances, whose tweak-length validation fails closed identically on both backends, whose release gate actually executes every published native wheel, and whose security-support statement was decided by the maintainer.

## 2. Source traceability

| Requirement | Source | Source location | Interpretation |
|---|---|---|---|
| PLAN-00007-REQ-01 | Review 00007; Review 00008 | `REV-00007-MAJ-01`; `REV-00008-LOW-02` | Persist the validated/default backend in `__setstate__`; restore all three `__setstate__` tests onto an uninitialized object; add a real 1.1-format round trip and a structural attribute-parity test |
| PLAN-00007-REQ-02 | Review 00007; Review 00008 | `REV-00007-MED-01`; `REV-00008-MED-03` | Absolute tweak-length ceiling in shared validation, bound-vs-ceiling rejection at construction, `u32::try_from` for both `n` and `t`, boundary tests without gigabyte allocations, documentation, SemVer-flagged changelog entry |
| PLAN-00007-REQ-03 | Review 00007 | `REV-00007-LOW-01` | Parameterize the remaining public-contract acceptance and interoperability tests over both backends |
| PLAN-00007-REQ-04 | Review 00007; user D1; Review 00008 | `STABLE-06`; `docs/backlog.md` "Port the divide-and-conquer conversion"; `REV-00008-LOW-01` | Port the divide-and-conquer and power-of-two conversion to the Rust core with the naive loops retained, threshold mirroring `_D_C_THRESHOLD`, equivalence tests, direct Python/Rust encrypt and decrypt comparisons |
| PLAN-00007-REQ-05 | Review 00007; Review 00008 | `STABLE-08`; `REV-00008-LOW-01` | Re-measure with `just bench`, apply the park rule, update README/changelog from the recorded run only |
| PLAN-00007-REQ-06 | Review 00007; plan 00003; Review 00008 | `REV-00007-MED-02`; plan 00003 `REQ-20`; `REV-00008-MED-02` | Install and exercise every published native wheel on a named compatible runner across Python 3.12/3.13/3.14; run full conformance against an abi3 distribution build in an isolated venv with import-origin checks and the four gate flags; `--locked` release builds; record `rustc --version` |
| PLAN-00007-REQ-07 | Review 00007; plan 00005 | `STABLE-07`; plan 00005 `AC-02` and work log lines 639, 648 | Produce the CI negative-control evidence on a disposable branch |
| PLAN-00007-REQ-08 | Review 00007; user D3; decision D4; Review 00008 | `STABLE-12`; open questions 3 and 4; `REV-00008-MAJ-01`; `REV-00008-LOW-03` | Document the glibc 2.34 native-wheel floor and the pure fallback; transcribe the D4 support text into `SECURITY.md`; clarify that Python coverage is not Rust line coverage; recheck NIST draft status; update the developer-guide CI description |
| PLAN-00007-REQ-09 | Review 00007; Review 00008 | `STABLE-09`, `STABLE-10`, `STABLE-11`; `REV-00008-LOW-03` | Re-run every gate on the candidate; lock consistency; package-contents verification; sdist fallback proven; packaged tests run from an unpacked sdist; compiler version recorded |
| PLAN-00007-REQ-10 | Review 00007; user D2; Review 00008 | `STABLE-13`; `REV-00008-MED-01` | Cut `2.0.0rc2` / `2.0.0-rc2`, owner tags `v2.0.0rc2` as a pre-release, `publish.yml` publishes it, Builder verifies the public candidate, owner states or waives the soak (D6) |
| PLAN-00007-REQ-11 | Review 00007 | `STABLE-14` | Independent read-only re-review of the rc2 change set before any final bump |
| PLAN-00007-REQ-12 | Review 00007 | `STABLE-15`, `STABLE-16` | Bump to `2.0.0` / `2.0.0` with lock entries; `[2.0.0]` changelog section; README roadmap and supported-version text; final NIST-status recheck |
| PLAN-00007-REQ-13 | Review 00007 | `STABLE-17` to `STABLE-20` | Freeze and gate the exact final commit; owner publishes `v2.0.0`; verify the public release end to end; record handoff and recovery |

## 3. Repository baseline

| Field | Value |
|---|---|
| Repository | joelee/fpr-ff1 |
| Branch | release/v2 |
| HEAD | 5eb518c3b0c58fe1e862a2512c07d37c2447d6bd |
| Working tree at publication | Clean (the strict gate returned only the empty file allocated for this plan) |
| Applicable instructions | `AGENTS.md`, `CLAUDE.md`, `docs/AGENTS.md`, `docs/plans/AGENTS.md`, `docs/reviews/AGENTS.md` |

`5eb518c` is `7e27017` (plan 00006 and review 00008 committed, plus the `allocating-report-numbers` skill) plus review 00009. Relative to the `v2.0.0rc1` tag commit (`89c74b7`), `release/v2` differs only in `docs/**` and `.agents/**`: `src/`, `rust/`, `tests/` and `.github/` are identical to the published candidate, so every code citation in reviews 00007 and 00008 holds at this baseline. Versions at baseline: `pyproject.toml` `2.0.0rc1`, `rust/fpr-ff1-rust/Cargo.toml` `2.0.0-rc1`. Tags present: `v0.1.0`, `v0.1.1`, `v1.0.0`, `v1.1.0`, `v2.0.0rc1`.

## 4. Scope

### In scope

- Fix `FF1.__setstate__` so a restored 1.x instance carries `_backend`; restore all three `__setstate__` tests onto an uninitialized object; add a real 1.1-format round trip and a structural attribute-parity test (REQ-01).
- Add a shared absolute tweak-length ceiling of `2**32 - 1`, reject configured bounds above it at construction, replace both `as u32` casts in the Rust P block with checked conversions, add boundary tests that never allocate gigabytes, and document the new rejection as a SemVer-relevant change (REQ-02).
- Parameterize the remaining public-contract acceptance and tweak-bound interoperability tests over both backends (REQ-03).
- Port the divide-and-conquer and power-of-two `NUM_radix`/`STR_radix` conversion to the Rust core, naive loops retained, with equivalence tests and direct Python/Rust encrypt and decrypt comparisons (REQ-04).
- Re-measure with `just bench`, apply the park rule, and rewrite the README/changelog performance guidance from the recorded run (REQ-05).
- Expand the release gate to install and exercise all five native wheel targets on named runners across three Python versions, plus a full-conformance leg against an abi3 distribution build in an isolated environment; `--locked` release builds; compiler version recorded (REQ-06).
- Produce the CI negative-control evidence on a disposable branch (REQ-07).
- Make support and deployment statements precise: glibc floor, pure fallback, the decided 1.x window, coverage wording, NIST status, developer-guide CI description (REQ-08).
- Full gate, dependency and lock consistency, package-contents verification, sdist packaged-test run (REQ-09).
- Cut, publish, verify and soak `v2.0.0rc2` (REQ-10); re-review (REQ-11); final bump and docs (REQ-12); freeze, publish, verify and hand off `v2.0.0` (REQ-13).

### Out of scope

- FF3/FF3-1, key management, application-specific defaults or alphabets, a `ubiq_security_fpe` compatibility shim, automatic backend switching, and any new runtime dependency: permanently out of scope per `AGENTS.md`.
- Lowering the Linux native-wheel floor below `manylinux_2_34` (user decision D3: keep and document).
- Free-threaded Python, additional native architectures, musl or lower-glibc native wheels.
- An independent cryptographic audit; it must not be represented as completed.
- Re-tagging, overwriting or yanking the already-published `v2.0.0rc1`.
- Changing the pure-Python path's ciphertext, public API, or default backend.
- Editing plan 00006 or any review report (both are immutable records; 00006 is superseded by this file, D8).

## 5. Constraints and preserved decisions

- The pure-Python path, its public API and its ciphertext are unchanged; every Rust change is output-neutral and proven so by the full dual-backend suite, including per-round intermediates, at each checkpoint.
- Plan 00003 decisions D3 (Rust backend opt-in only; pure Python is the reference and default) and D4 (validation runs in Python for both backends) are preserved. The tweak ceiling is therefore enforced in Python; the Rust checked conversion is defence in depth, not the primary gate.
- No floating-point arithmetic in either FF1 core; bit lengths come from exact integer arithmetic (`tests/test_exact_arithmetic.py` AST-scans the Python core).
- No cipher context, scratch buffer or cache is stored on the instance or in a `static`/`OnceLock`; all state is call-local in both cores.
- The 100% line-and-branch coverage floor on `fpr_ff1` holds with and without the extension present. `just quality` stays Rust-free.
- Two-file version rule: `pyproject.toml` and `rust/fpr-ff1-rust/Cargo.toml` move together (`2.0.0rc2` / `2.0.0-rc2`, then `2.0.0` / `2.0.0`), enforced by `tests/test_contract.py::test_crate_version_matches_project_version`. Tags follow `pyproject.toml` exactly (`v2.0.0rc2`, `v2.0.0`); `publish.yml` compares the tag to the project version.
- Only the user tags, pushes and publishes. Builder never performs an outward action (push, tag, release, branch deletion on `origin`) without explicit per-action authorization recorded in the work log.
- The `Development Status :: 5 - Production/Stable` classifier stays (plan 00005 decision D7).
- Review reports and plan 00006 are never edited. Numbers for any new report come from `.agents/skills/allocating-report-numbers/allocate-report.sh`.
- Documentation is updated in the same commit that makes it true (`docs/AGENTS.md`).

## 6. Assumptions

None. Unresolved matters are recorded as decisions and block approval when material.

## 7. Decisions and blockers

| ID | Decision or blocker | Resolution | Owner | Status |
|---|---|---|---|---|
| D1 | Review 00007 open question 1: ship the Rust divide-and-conquer conversion in v2.0.0 or defer | User selected "Ship in v2.0.0" on 2026-09-09 (carried from plan 00006) | User | Resolved |
| D2 | Review 00007 STABLE-13: cut an intermediate rc2 or go straight to final | User selected "Cut `v2.0.0rc2` first" on 2026-09-09 (carried from plan 00006) | User | Resolved |
| D3 | Review 00007 open question 3: keep `manylinux_2_34` or lower the floor | User selected "Keep `manylinux_2_34`, document it" on 2026-09-09 (carried from plan 00006) | User | Resolved |
| D4 | **Post-final 1.x security-support window** (review 00007 open question 4; `REV-00008-MAJ-01`; `REV-00009-MAJ-01`). `SECURITY.md` currently says "the latest `2.x` release receives fixes ... backported to the most recent minor" above a table marking `2.0.0rc1`, `1.1.x` and `1.0.x` all supported, which is self-contradictory. A support window is a maintainer commitment and cannot be set by the planner or the Builder. | **User selected Option A on 2026-09-16**: the latest `2.x` release receives bug and security fixes; `1.1.x` receives security fixes only until `2.1.0` ships or six months after the `v2.0.0` publication date, whichever is later; `1.0.x` is no longer supported. The exact `SECURITY.md` text is the Option A block in §7.1, quoted verbatim in REQ-08. | User | Resolved |
| D5 | Review 00007 open question 2: how the plan 00005 AC-02 negative-control evidence is produced | Produced in STEP-07 on a disposable branch; the push and the branch deletion are outward actions the user authorizes per action (carried from plan 00006) | User (authorization) | Resolved |
| D6 | rc2 soak window (review 00007 STABLE-13 leaves duration to the owner; review 00008 open question 1) | The plan fixes no duration. At STEP-11 the owner writes one of "soak until <UTC date>" or "soak waived; proceed on verified publication" into the work log, and STEP-12 may not start before that entry exists and, if dated, the date has passed. This is a process decision, not a scope decision, so it does not block approval. | User (at STEP-11) | Resolved |
| D7 | Wheel-job fan-out (review 00008 MED-02 asked the plan to decide) | Subset jobs: a matrix of the five targets times Python 3.12/3.13/3.14 (15 short jobs; each installs one wheel and runs the installed-package subset). Full-conformance leg: one job, Linux x86_64 wheel, Python 3.14 (the newest interpreter the abi3-py312 wheel promises to serve and the one the rc1 gate never exercised natively). | Planner | Resolved |
| D8 | Amend draft 00006 in place or write a new plan (review 00009 open question 2) | User instructed a rewrite on 2026-09-16. This plan is a new numbered file with `plan_kind: superseding` and `previous_plan` pointing at 00006; 00006 is left unedited as a draft record and must not be approved or executed. | User | Resolved |
| D9 | Rust divide-and-conquer threshold and naming (review 00008 LOW-01) | The Rust constant is `D_C_THRESHOLD: usize = 64`, documented as mirroring `_ff1.py::_D_C_THRESHOLD`; the naive functions are renamed `num_radix_reference`/`str_radix_reference` and the dispatching `num_radix`/`str_radix` keep the public names, mirroring the Python module's `_num_radix_reference`/`_num_radix` split. | Planner | Resolved |

### 7.1 D4 options (Option A selected; B and C retained as the record of what was offered)

Each option replaces `SECURITY.md` §Supported versions in full. The `2.0.0rc1` row is removed in every option (STEP-13 replaces `2.0.x` with the published version). `<v2.0.0 date>` is filled by the Builder at STEP-13 from the tag date.

**Option A: overlap window (selected).**

```markdown
## Supported versions

The latest `2.x` release receives bug and security fixes. The `1.1.x` line receives security
fixes only, until `2.1.0` ships or until <v2.0.0 date + six months>, whichever is later. `1.0.x`
is no longer supported: upgrade to `1.1.x` or `2.0.x` (both produce identical ciphertext).

| Version | Supported |
|---|---|
| 2.0.x | ✅ bug and security fixes |
| 1.1.x | ✅ security fixes only, until `2.1.0` or <v2.0.0 date + six months> |
| 1.0.x | ❌ |
```

**Option B: 1.x end-of-life at v2.0.0.**

```markdown
## Supported versions

Only the latest `2.x` release receives fixes. The `1.x` line reached end of life when `v2.0.0`
was published on <v2.0.0 date>. Upgrading is drop-in: the pure-Python path in `2.0.0` is
byte-identical to `1.1.0` for every valid input, the `backend` keyword is opt-in, and no
compiled extension is required.

| Version | Supported |
|---|---|
| 2.0.x | ✅ |
| 1.x | ❌ end of life |
```

**Option C: 1.1.x maintained for the life of 2.x.**

```markdown
## Supported versions

The latest `2.x` release receives bug and security fixes. The `1.1.x` line receives security
fixes for as long as the `2.x` line is supported. `1.0.x` is no longer supported.

| Version | Supported |
|---|---|
| 2.0.x | ✅ bug and security fixes |
| 1.1.x | ✅ security fixes only |
| 1.0.x | ❌ |
```

## 8. Affected architecture and components

- `src/fpr_ff1/_ff1.py`: `__setstate__` backend persistence (REQ-01); `_MAX_TWEAK_LEN` constant beside `_MAX_LEN`, a factored `_validate_tweak_length(length: int)` helper called by `_validate_tweak`, and ceiling checks in `_validate_tweak_bounds` (REQ-02).
- `rust/fpr-ff1-rust/src/lib.rs`: checked `u32` conversions for `n` and `t` via a factored `encode_len_u32(len: usize) -> Result<[u8; 4], String>` (REQ-02); `D_C_THRESHOLD`, `num_radix_reference`/`str_radix_reference`, power-of-two packing, and the dispatching `num_radix`/`str_radix` (REQ-04).
- `rust/fpr-ff1-rust/src/tests.rs`: checked-encoding tests (REQ-02); fast-versus-reference equivalence tests (REQ-04).
- `tests/test_backend_dispatch.py`, `tests/test_pickle.py`: corrected `__setstate__` tests, real 1.1-format round trip, attribute-parity test (REQ-01).
- `tests/test_validation.py`, `tests/test_contract.py`: ceiling and bound boundary tests, `_malformed_calls` constructor cases (REQ-02); dual-backend parameterization (REQ-03).
- `tests/test_interoperability.py`: `test_tweak_bounds_map_across_apis` through `ff1_factory` (REQ-03).
- New `tests/test_backend_agreement.py` (or an extension of `tests/test_rust_aes_validation.py`): direct same-input Python/Rust encrypt and decrypt comparisons (REQ-04).
- `benchmarks/timing.py`: measurement shapes retained; no new shape is required unless the README quotes one (REQ-05).
- `.github/workflows/ci.yml`: `wheel-build` gains `--locked` and a `rustc --version` step; `wheel-test-platform` is replaced by a `wheel-test-native` matrix and a `wheel-conformance-abi3` job; `rust-conformance` gains `--locked` (REQ-06, REQ-07).
- `README.md`, `CHANGELOG.md`, `SECURITY.md`, `docs/configuration.md`, `docs/developer-guide.md`, `docs/backlog.md`, `docs/architecture.md`: documentation (REQ-02, REQ-05, REQ-08, REQ-10, REQ-12).
- `pyproject.toml`, `rust/fpr-ff1-rust/Cargo.toml`, `uv.lock`, `rust/Cargo.lock`: version bumps (REQ-10, REQ-12).

```mermaid
flowchart LR
    FIX[STEP-01..03 defect fixes] --> CORE[STEP-04 Rust D&C port]
    CORE --> BENCH[STEP-05 bench + park rule]
    BENCH --> GATE[STEP-06 wheel matrix + abi3 leg]
    GATE --> NEG[STEP-07 negative control]
    NEG --> DOCS[STEP-08 support docs incl. D4 text]
    DOCS --> RC2V[STEP-09 rc2 version + changelog]
    RC2V --> FULL[STEP-10 full gate + packages]
    FULL --> RC2P[STEP-11 owner tags v2.0.0rc2, verify, soak]
    RC2P --> RR[STEP-12 re-review]
    RR --> FINAL[STEP-13 final bump + docs]
    FINAL --> PUB[STEP-14 owner tags v2.0.0, verify, handoff]
```

## 9. Requirement catalogue

### PLAN-00007-REQ-01 — Persist the backend on legacy-pickle restoration, and make the drift class fail structurally

- **Requirement:** In `FF1.__setstate__`, after the existing backend validation block, assign `self._backend = backend` (the validated value, defaulted to `"python"`), keeping the `_load_rust_backend()` availability check for a saved `"rust"` backend. Restore the destination onto `FF1.__new__(FF1)` in all three tests that currently construct it normally (`test_legacy_pickle_state_defaults_to_python`, `test_corrupt_unpickled_backend_raises`, `test_non_str_unpickled_backend_raises` in `tests/test_backend_dispatch.py`). Add a test that builds a 1.1-format state (no `_backend` key), restores it on an uninitialized object, exercises `encrypt_numerals`/`decrypt_numerals` and `encrypt`/`decrypt`, then pickles and restores it a second time. Add a structural attribute-parity test asserting `set(vars(pickle.loads(pickle.dumps(fresh)))) == set(vars(fresh))` for a python instance and, under `@requires_rust`, a rust instance.
- **Rationale:** Real unpickling bypasses `__init__`; the current code leaves `_backend` unset and every numeral or string method raises `AttributeError` (MAJ-01). The three tests hide the class of defect by supplying the attribute through normal construction. The parity test makes the next `__init__`-only attribute fail immediately, which is what the comment at `_ff1.py:184` ("the constructor and `__setstate__` ... must not drift") asks for.
- **Source:** Review 00007 `REV-00007-MAJ-01`; review 00008 `REV-00008-LOW-02`; `src/fpr_ff1/_ff1.py:310-352`, `:484`, `:506`; `tests/test_backend_dispatch.py:251-279`; `tests/test_pickle.py:123,140` (the existing `FF1.__new__(FF1)` pattern).
- **Acceptance evidence:** The 1.1-format payload restores on an uninitialized object with `_backend == "python"`, all four operations succeed, and a second cycle round-trips; the parity test passes for both backends; the three corrected tests fail with `AttributeError` before the fix and pass after; coverage stays at 100%.

### PLAN-00007-REQ-02 — Fail closed on oversized tweaks and oversized tweak bounds, identically on both backends

- **Requirement:**
  1. Add `_MAX_TWEAK_LEN: ClassVar[int] = 2**32 - 1` beside `_MAX_LEN` and a factored `_validate_tweak_length(length: int) -> None` that raises `TweakLengthError` naming the ceiling when `length > _MAX_TWEAK_LEN`. `_validate_tweak` calls it before the configured-bound checks, for both default and per-call tweaks, on both backends.
  2. In `_validate_tweak_bounds`, reject at construction `min_tweak_len > 2**32 - 1` (unsatisfiable: no tweak can reach it) and `max_tweak_len > 2**32 - 1` (exceeds the encodable ceiling; reject rather than clamp), each with `TweakLengthError` and a message naming the ceiling.
  3. In `lib.rs`, replace both `(n as u32)` and `(t as u32)` in the P block with a factored `encode_len_u32(len: usize) -> Result<[u8; 4], String>` using `u32::try_from`, mapped into the existing `Result<_, String>` error path.
  4. Tests: boundary cases for the helper at `2**32 - 1` (accepted), `2**32` and `2**40` (rejected) without allocating a tweak; constructor cases `min_tweak_len=2**32`, `max_tweak_len=2**32`, `max_tweak_len=2**40` added to `tests/test_validation.py` and to `tests/test_contract.py::_malformed_calls` so the typed-rejection sweep covers them; a Rust unit test for `encode_len_u32` at `u32::MAX as usize` (accepted) and `u32::MAX as usize + 1` (rejected, on 64-bit targets).
  5. Document the ceiling in `docs/configuration.md` §Runtime Constraints (tweak length `<= 2**32 - 1`, the four-byte `[t]^4` field of the P block) and in the README parameter table.
  6. The changelog entry (written in STEP-09) states that a tweak or tweak bound at or above `2**32` is newly rejected, and that this is a SemVer-relevant input-domain change permitted by the major version.
- **Rationale:** The P block encodes `t` in four bytes; the reference raises `OverflowError` (outside `FF1Error`) at `2**32` while the Rust core silently wraps (MED-01). Review 00007 also required defining how configured bounds interact with the ceiling without silently clamping; without item 2 a caller can construct an instance no tweak can satisfy, or a bound that silently means `2**32 - 1` (00008 MED-03). The `n` cast is bounded by `_MAX_LEN` in Python and is not a live defect, but leaving one of two identical casts unchecked contradicts the line-by-line comparability posture.
- **Source:** Review 00007 `REV-00007-MED-01`; review 00008 `REV-00008-MED-03`; `src/fpr_ff1/_ff1.py:61-97`, `:180`, `:367-371`, `:813`, `:908`; `rust/fpr-ff1-rust/src/lib.rs:300-301`; `AGENTS.md` version policy.
- **Acceptance evidence:** Ceiling and bound rejections raise `TweakLengthError` with identical messages on both backends before any FF1 calculation; the Rust helper test is green; `_malformed_calls` includes the new constructor cases; ordinary empty/short/long-tweak conformance cases are unchanged; no test allocates more than a few kilobytes for these cases.

### PLAN-00007-REQ-03 — Complete the dual-backend public-contract sweep

- **Requirement:** Parameterize through `ff1_factory` (or draw `backend` from `BACKENDS`) the public-contract tests that perform real encryption and still construct `FF1` directly: `test_empty_tweak_equals_absent_tweak`, `test_long_tweaks_are_accepted`, `test_integer_like_numerals_are_accepted`, `test_integer_like_numerals_are_normalised_to_int`, `test_bytes_like_keys_and_tweaks_accepted`, `test_mutable_key_and_tweak_are_copied_at_construction` in `tests/test_validation.py`, and `test_tweak_bounds_map_across_apis` in `tests/test_interoperability.py`. Leave Python-only conversion-internals tests and backend-selection tests unparameterized. Do not weaken any assertion.
- **Rationale:** These cases never cross the FFI boundary today, so the Rust backend is not exercised for them (LOW-01), contrary to the dual-backend testing rule in `AGENTS.md`.
- **Source:** Review 00007 `REV-00007-LOW-01`; `tests/test_validation.py:244-259`, `:324-358`, `:393-441`; `tests/test_interoperability.py:109-124`; `tests/conftest.py` (`BACKENDS`, `ff1_factory`).
- **Acceptance evidence:** `uv run pytest --collect-only -q -k rust` lists a rust case for each named test with the extension built; all pass on both backends with unchanged expected outcomes.

### PLAN-00007-REQ-04 — Port the divide-and-conquer conversion to the Rust core

- **Requirement:** In `lib.rs`, rename the existing naive loops `num_radix_reference`/`str_radix_reference` (documented as the SP 800-38G reference) and add dispatching `num_radix`/`str_radix` that mirror `_ff1.py::_num_radix`/`_str_radix`: a power-of-two byte-packing path when `radix` is a power of two, the reference loop at or below `D_C_THRESHOLD = 64` numerals, and divide-and-conquer above it with a call-local power cache. `num-bigint`'s `from_radix_be`/`to_radix_be` may be used only where `radix <= 256`; larger power-of-two radices are hand-packed. Wire the dispatchers into `ff1_impl` at the same call sites the Python reference uses (step 6.i Q, step 6.vi A/B, step 6.vii C). No `static`, `OnceLock`, `unsafe`, or instance-held state. Add Rust equivalence tests (fast versus reference across the representative radices `2, 10, 36, 256, 65535` and a full sweep of every supported radix at one length above the threshold; leading zeros; truncation contract at `radix**length`; odd splits; lengths `63, 64, 65, 128, 129`; degenerate lengths `0, 1`). Add a Python module of direct same-input Python/Rust **encrypt and decrypt** comparisons across all three key sizes, tweaks of length `0, 1, 16, 255`, radices `10, 36, 256, 65535`, and lengths `6, 64, 65, 1000, 5000`, asserting equality of outputs (not merely round trips).
- **Rationale:** User decision D1 brings the backlog item into this release; STABLE-06 requires spec-comparable reference logic, call-local scratch state, and direct rather than round-trip comparisons. Mirroring the Python names and threshold (D9) keeps the two cores comparable line by line.
- **Source:** Review 00007 `STABLE-06`; review 00008 `REV-00008-LOW-01`; `docs/backlog.md` (rc2 conversion item); `src/fpr_ff1/_ff1.py:568-762`; `rust/fpr-ff1-rust/src/lib.rs:156-184`; `tests/test_conversion_equivalence.py` (the Python model for the equivalence tests).
- **Acceptance evidence:** `cargo test` green including the new equivalence tests; full dual-backend suite bit-exact including per-round intermediates; the new direct-comparison module green; `grep -n "static\|OnceLock\|unsafe" rust/fpr-ff1-rust/src/lib.rs` shows no new match; `D_C_THRESHOLD` is `64` and its doc comment names `_D_C_THRESHOLD`.

### PLAN-00007-REQ-05 — Refresh performance evidence under a decision rule

- **Requirement:** After STEP-04, run `just bench` with a release-built extension and record machine, interpreter, toolchain (`rustc --version`), package and extension versions, every per-case timing, and the GIL probe in the work log. **Park rule:** the Rust backend must be at most as slow as the Python backend (`rust <= python` per-call time) at n = 20,000 on radix 10 and on radix 256; if either fails, the Builder stops, records the numbers, and escalates. Only on a pass does the README Backends section and the changelog change; every number in them traces to the recorded run. No universal-speedup or constant-time claim.
- **Rationale:** The Rust core change alters long-input performance; the published crossover guidance must be re-measured (STABLE-08). The port's outcome is likely but unmeasured (`num-bigint` 0.4.8 uses Burnikel–Ziegler division above 64 limbs), so a rule replaces a prediction (00008 LOW-01).
- **Source:** Review 00007 `STABLE-08`; review 00008 `REV-00008-LOW-01`; `benchmarks/timing.py`; `README.md` §Backends.
- **Acceptance evidence:** Work log contains the run and the park-rule verdict; README/changelog numbers match it; or an escalation entry exists and the README keeps its crossover guidance.

### PLAN-00007-REQ-06 — Execute every published native wheel in the release gate, from the artifact, not the source tree

- **Requirement:**
  1. Replace `wheel-test-platform` with a `wheel-test-native` matrix: five targets times Python 3.12/3.13/3.14 (D7). Runner labels per target: `x86_64-unknown-linux-gnu` on `ubuntu-24.04`; `aarch64-unknown-linux-gnu` on `ubuntu-24.04-arm`; `aarch64-apple-darwin` on `macos-latest`; `x86_64-apple-darwin` on `macos-15-intel`; `x86_64-pc-windows-msvc` on `windows-latest`. Each job downloads exactly its `wheels-<target>` artifact, creates a fresh venv with `uv venv --python <version>`, installs the wheel plus the exported dev requirements (`uv export --frozen --no-emit-project --no-hashes -o requirements-ci.txt` then `uv pip install --python <venv> -r requirements-ci.txt dist-wheels/<the one wheel>`), and never runs `uv sync` or `uv run` in that leg.
  2. Each subset job runs the import-origin assertion as its own step: `fpr_ff1.__file__` resolves under the venv's `site-packages`, and `fpr_ff1._rs.__file__` ends with the platform extension suffix (`.so` or `.pyd`) and is not under the checkout's `src/`. Then it runs, with `FPR_FF1_REQUIRE_RUST_BACKEND=1` and `FPR_FF1_REQUIRE_ORACLE=1`, the installed-package subset `tests/test_nist_vectors.py tests/test_intermediates.py tests/test_rust_aes_validation.py tests/test_frozen_kat.py tests/test_backend_dispatch.py tests/test_smoke.py` via `<venv python> -m pytest -p no:cacheprovider -q` (NIST vectors both directions, per-round intermediates, AES KAT, a `d > 16` case, typed errors, version and `py.typed` checks).
  3. Add `wheel-conformance-abi3`: `ubuntu-24.04`, Python 3.14, the `x86_64-unknown-linux-gnu` wheel, same install recipe and import-origin step, then `-k rust` collection floor `>= 500`, then the full suite with `FPR_FF1_REQUIRE_RUST_BACKEND=1 FPR_FF1_REQUIRE_ORACLE=1 <venv python> -m pytest --cov=fpr_ff1 --cov-report=term-missing --cov-fail-under=100`.
  4. `wheel-build` adds `--locked` to the maturin build and a step that prints `rustc --version` and `cargo --version`; `rust-conformance` adds `--locked` to its `cargo build`.
  5. All new jobs run inside `ci.yml`, so `publish.yml`'s `workflow_call` reuse makes them required by the gate automatically. Update the CI description in `docs/developer-guide.md` (STEP-08).
- **Rationale:** Four of five published native wheels are never imported by the gate, and the full suite runs against a source-tree, non-abi3 extension (MED-02). A leg that reinstalls the editable project over the wheel would reproduce the review 00006 MAJ-01 failure class with a green badge, which is why the recipe, the import-origin checks and the flags are specified rather than left to inference (00008 MED-02).
- **Source:** Review 00007 `REV-00007-MED-02`; plan 00003 `REQ-20`; review 00008 `REV-00008-MED-02` and its external reference (runner labels, accessed 2026-09-09); `.github/workflows/ci.yml:78-135`, `:219-275`, `:329-373`; `tests/__init__.py` and `tests/test_exact_arithmetic.py:17-18` (checkout-relative reads that keep working with the venv interpreter).
- **Acceptance evidence:** Fifteen subset jobs and the abi3 leg green on the pushed branch; each job's import-origin step prints paths under the venv; the abi3 leg reports 100% coverage with `-k rust >= 500`; `publish.yml`'s gate includes them; `rustc --version` appears in every `wheel-build` log.

### PLAN-00007-REQ-07 — Produce the CI negative-control evidence

- **Requirement:** On a disposable, non-release branch that the user authorizes pushing, apply a controlled S-expansion error in `lib.rs` (the block counter `j` starting at `0` instead of `1`), push, and confirm that `rust-conformance`, every `wheel-test-native` job and `wheel-conformance-abi3` fail while the pure-Python `quality` matrix stays green. Record the run URL and the failing job names, restore correct source, and, with authorization, delete the branch. Never tag or publish the mutated revision.
- **Rationale:** Plan 00005 AC-02's deliberate-break evidence was produced locally but never in CI (STABLE-07; review 00007 open question 2). With STEP-06 in place the installed-wheel jobs must fail the same mutation; the plan 00005 expectation that only `rust-conformance` turns red is obsolete and must not be reinstated.
- **Source:** Review 00007 `STABLE-07`; plan 00005 `AC-02` and work log lines 639, 648.
- **Acceptance evidence:** A recorded run shows the mutation failing the Rust and installed-wheel jobs while the correct source passes on the release branch; the mutated commit exists on no tag and no published artifact.

### PLAN-00007-REQ-08 — Make support and deployment statements precise

- **Requirement:**
  1. State the native-wheel coverage (Linux x86_64 and aarch64 at `manylinux_2_34`, glibc 2.34 or newer; macOS x86_64 and arm64; Windows x64; CPython 3.12 to 3.14 via abi3) and the pure-Python fallback for older glibc, musl and every other platform, in `README.md` (Backends) and `docs/configuration.md`.
  2. Replace `SECURITY.md` §Supported versions with the D4 Option A text from §7.1, verbatim, leaving `<v2.0.0 date + six months>` as the literal placeholder for STEP-13 to fill from the tag date. **This item is transcription, not policy-making; the Builder stops if the text it writes differs from §7.1 Option A in anything but the placeholder.**
  3. Add one sentence wherever "100% line and branch coverage" appears next to "both backends" (`README.md`, `CHANGELOG.md`, `docs/developer-guide.md`): the coverage figure measures the Python package; the Rust core is covered by the dual-backend conformance suite and `cargo test`, not by a line-coverage figure.
  4. Recheck NIST SP 800-38G Rev. 1 status (still a second public draft as of review 00007) and retain the chosen radix subset and the no-float/forward-AES rules; record the check date in the work log.
  5. Update the `docs/developer-guide.md` CI/CD description for the new wheel jobs, the abi3 leg and `--locked`.
- **Rationale:** Review 00007 open questions 3 and 4 and STABLE-12 require explicit statements; 00008 MAJ-01 requires the support window to come from the maintainer; 00008 LOW-03 requires the coverage wording.
- **Source:** Review 00007 `STABLE-12`, open questions 3 and 4; review 00008 `REV-00008-MAJ-01`, `REV-00008-LOW-03`; decisions D3, D4; `SECURITY.md:22-29`; `README.md` §Backends, §Supported Python versions.
- **Acceptance evidence:** The four documents state the floor, the fallback, the D4 text and the coverage clarification; no statement implies native support on an untested platform; `uv run ruff format --check .` and `ruff check .` clean.

### PLAN-00007-REQ-09 — Re-run the full gate and verify build and package consistency

- **Requirement:** On the rc2 candidate commit: `just quality`; `just rust-test`; `just rust-lint`; the full dual-backend gate; `uv lock --check`; `cargo build --locked --manifest-path rust/Cargo.toml` leaving `rust/Cargo.lock` unchanged; `uv build` then `uvx twine check dist/*`; `uvx maturin@1.15.0 build -m rust/fpr-ff1-rust/Cargo.toml --release --locked --out dist-native` then `uvx twine check dist-native/*`; the Python locked and minimum-dependency audits, `cargo audit`, and `just secrets`. Verify package contents: sdist and pure wheel contain source, metadata, licence, `py.typed`, tests and vectors, and none of caches, `.agents/`, `AGENTS.md`, plans, reviews or dev binaries; the native wheel places `fpr_ff1/_rs.abi3.so`. Prove the sdist installs pure-Python in a fresh venv and that `backend="rust"` raises `BackendError` there. **Run the packaged tests from an unpacked sdist**: unpack, install the sdist plus `pytest`, `hypothesis` and `packaging` into a fresh venv, run a bare `pytest` (no coverage flags, oracle absent and therefore skipped, Rust absent and therefore skipped) and record the result. Record `rustc --version` and `cargo --version` for the local native build. Record the CI run URL for the branch at the candidate commit, green in every job.
- **Rationale:** STABLE-09/10/11 require the candidate to be gated and its artifacts verified as artifacts; 00008 LOW-03 restores the sdist packaged-test run and the compiler-version record.
- **Source:** Review 00007 `STABLE-09`, `STABLE-10`, `STABLE-11`; review 00008 `REV-00008-LOW-03`; `pyproject.toml` `[tool.hatch.build.targets.sdist]`; `.github/workflows/ci.yml` `build`, `sdist-test`.
- **Acceptance evidence:** Every command above green with output recorded; lock files unchanged by the builds; contents checks pass; the unpacked-sdist `pytest` run passes with only oracle and rust skips; compiler versions recorded; CI run URL recorded.

### PLAN-00007-REQ-10 — Cut, publish, verify and soak `v2.0.0rc2`

- **Requirement:** Bump `pyproject.toml` to `2.0.0rc2` and `rust/fpr-ff1-rust/Cargo.toml` to `2.0.0-rc2`, refresh `uv.lock` and `rust/Cargo.lock`, add a dated `[2.0.0rc2]` changelog section (fixes, the conversion, the new rejection flagged as SemVer-relevant, the wheel gate) with its comparison link, and update `docs/backlog.md` (move the conversion item to Completed). After REQ-09 is green: Builder records the frozen rc2 commit hash and evidence in the work log; the **owner** tags exactly `v2.0.0rc2` at that commit, pushes the tag, and publishes a GitHub **pre-release**; `publish.yml` runs the gate and uploads the gated artifacts. Builder then verifies the public candidate: PyPI exposes seven files (sdist, pure wheel, five native wheels) with `2.0.0rc2` metadata, non-yanked, with attestations whose subject digests match the CI artifacts; a fresh venv installs `fpr-ff1==2.0.0rc2` and passes the NIST vectors plus a `d > 16` case on both backends; a `--no-binary` install exercises the pure fallback. The owner then records the D6 soak statement.
- **Rationale:** User decision D2 requires an intermediate candidate; STABLE-13 requires its own immutable release evidence; 00008 MED-01 requires the hand-off to be a step with an owner, not a precondition.
- **Source:** Review 00007 `STABLE-13`; review 00008 `REV-00008-MED-01`; decisions D2, D6; `.github/workflows/publish.yml`.
- **Acceptance evidence:** `v2.0.0rc2` tag, GitHub pre-release, `publish.yml` run URL, PyPI verification results and the soak statement are all in the work log.

### PLAN-00007-REQ-11 — Obtain an independent re-review of the rc2 change set

- **Requirement:** The owner requests an independent read-only review of the change set `v2.0.0rc1..v2.0.0rc2` with review 00007 as predecessor and the STEP-10/STEP-11 evidence attached; the Builder prepares the evidence bundle (commit range, CI run URLs, PyPI verification, bench run, negative-control run). The report is a new numbered review. It must classify `REV-00007-MAJ-01`, `MED-01`, `MED-02` and `LOW-01` as resolved, and contain no Critical or Major finding, before any final bump.
- **Rationale:** STABLE-14 requires a re-review before final publication; the Rust core change warrants independent verification.
- **Source:** Review 00007 `STABLE-14`; `docs/reviews/AGENTS.md`.
- **Acceptance evidence:** A new review report exists with verdict `approve` (or `request-changes` with no Critical/Major and every remaining finding dispositioned by the owner in the work log).

### PLAN-00007-REQ-12 — Bump to final with lock entries and release documentation

- **Requirement:** After REQ-11: bump `pyproject.toml` to `2.0.0` and `rust/fpr-ff1-rust/Cargo.toml` to `2.0.0`; refresh both lock files; add a dated `[2.0.0]` changelog section summarizing the delivered 2.0 feature and the post-rc fixes with its comparison link; point `[Unreleased]` at `v2.0.0...HEAD`; keep the `[2.0.0rc1]` and `[2.0.0rc2]` sections intact; update the README roadmap row ("Shipped as `2.0.0rc1`") and the `SECURITY.md` table's version cell and any `<v2.0.0 date>` placeholder from D4; repeat the NIST status check and record the date.
- **Rationale:** STABLE-15/16 require the two-file version rule and final documentation.
- **Source:** Review 00007 `STABLE-15`, `STABLE-16`; `tests/test_contract.py::test_crate_version_matches_project_version`.
- **Acceptance evidence:** Contract test green; `uv lock --check` clean; changelog links resolve; no `<v2.0.0 date>` placeholder remains.

### PLAN-00007-REQ-13 — Freeze, publish, verify and record the handoff for `v2.0.0`

- **Requirement:** Freeze the exact final commit (only reviewed changes, both manifests and locks verified); rerun REQ-09's local gate and confirm the branch's CI run is green at that commit; confirm the `pypi` environment and Trusted Publisher binding are unchanged. The **owner** tags exactly `v2.0.0`, pushes, and publishes a non-prerelease GitHub release; `publish.yml` reruns the gate and uploads its artifacts. Builder verifies the public release (seven files, `2.0.0` metadata, non-yanked, attestations matching CI artifacts, fresh-venv installs on both backends and the pure fallback, NIST plus `d > 16` smoke) and records the handoff: commit and tag, run URLs, artifact digests, compiler versions, support policy, verification outcome, and the recovery procedure (stop promotion, notify, consider yank plus a corrected version; never replace published files or retag).
- **Rationale:** STABLE-17 to STABLE-20 define the final publication and verification sequence.
- **Source:** Review 00007 `STABLE-17` to `STABLE-20`; `.github/workflows/publish.yml`.
- **Acceptance evidence:** `v2.0.0` discoverable on PyPI without prerelease opt-in; verification results and the handoff record in the work log.

## 10. Delivery strategy

The order is unchanged in spirit from plan 00006 (00008 found the sequencing sound) with two additions: an owner hand-off step for rc2 and a separate re-review step.

1. **Defect fixes first** (STEP-01 pickle, STEP-02 tweak ceiling and bounds, STEP-03 dual-backend sweep): small, independent, red-then-green; may run in any order or in parallel.
2. **Rust core change** (STEP-04): the riskiest edit, proven bit-exact by the full dual-backend suite and the new direct comparisons before anything measures or documents it.
3. **Performance evidence under the park rule** (STEP-05): measured after the core is final; the README changes only on a pass.
4. **CI and evidence** (STEP-06 wheel matrix and abi3 leg, STEP-07 negative control): the gate is expanded once the code it guards is final, then proven to have teeth.
5. **Documentation** (STEP-08): written once the artifacts and decisions it describes exist; D4 is resolved (Option A).
6. **Candidate** (STEP-09 version, STEP-10 full gate and packages, STEP-11 owner publishes and soaks rc2).
7. **Promotion** (STEP-12 re-review, STEP-13 final bump, STEP-14 owner publishes and verifies final).

Checkpoint after each of STEP-01 to STEP-05: `FPR_FF1_REQUIRE_RUST_BACKEND=1 FPR_FF1_REQUIRE_ORACLE=1 uv run pytest --cov=fpr_ff1 --cov-report=term-missing --cov-fail-under=100`, `cargo test --manifest-path rust/Cargo.toml`, `just rust-lint`, and `just quality` (Rust-free), each recorded. STEP-06, STEP-07, STEP-11 and STEP-14 need outward actions and are gated on per-action user authorization. One revertible commit per step keeps the history bisectable for ciphertext questions; STEP-01 to STEP-03 may each be one commit.

## 11. Detailed implementation steps

### PLAN-00007-STEP-01 — Persist the backend on legacy-pickle restoration

- **Status placeholder:** `not-started`
- **Objective:** Make a real 1.x pickle restore into a fully functional instance, and make the drift class fail structurally.
- **Requirements:** `PLAN-00007-REQ-01`
- **Depends on:** None
- **Affected components:** `src/fpr_ff1/_ff1.py` (`__setstate__`), `tests/test_backend_dispatch.py`, `tests/test_pickle.py`
- **Preconditions:** Clean worktree on `release/v2`; plan approved.
- **Test or evidence first:** Change the three `__setstate__` tests in `tests/test_backend_dispatch.py:251-279` to restore onto `FF1.__new__(FF1)`; add `test_legacy_serialized_state_round_trips` (1.1-format state, uninitialized destination, all four operations, second cycle); add `test_unpickled_instance_has_every_constructor_attribute` (the `vars()` set comparison, python and `@requires_rust` rust). Run them and record that the legacy and parity tests fail with `AttributeError` or a set difference containing `_backend`.
- **Implementation tasks:**
  1. In `__setstate__`, after `_load_rust_backend()` and before `self._aes = ...`, add `self._backend = backend`.
  2. Leave every other line of `__setstate__` unchanged.
  3. Run the module tests to green.
- **Documentation/configuration/operations:** Changelog wording lands in STEP-09 (`### Fixed`).
- **Verification:** `uv run pytest tests/test_backend_dispatch.py tests/test_pickle.py -q`; the STEP checkpoint commands from §10.
- **Completion criteria:** All new and corrected tests green on both backends; coverage 100%; one commit.
- **Rollback or recovery:** Revert the commit.
- **Builder stop conditions:** Any regression in existing pickle, deepcopy or spawn tests; any ciphertext change; the parity test revealing a second missing attribute (escalate; do not silently add it).

### PLAN-00007-STEP-02 — Fail closed on oversized tweaks and oversized bounds

- **Status placeholder:** `not-started`
- **Objective:** Reject tweaks and tweak bounds the four-byte P-block field cannot encode, identically on both backends, at the earliest point.
- **Requirements:** `PLAN-00007-REQ-02`
- **Depends on:** None
- **Affected components:** `src/fpr_ff1/_ff1.py` (`_MAX_TWEAK_LEN`, `_validate_tweak_length`, `_validate_tweak`, `_validate_tweak_bounds`), `rust/fpr-ff1-rust/src/lib.rs` (`encode_len_u32`, `ff1_impl`), `rust/fpr-ff1-rust/src/tests.rs`, `tests/test_validation.py`, `tests/test_contract.py`, `docs/configuration.md`, `README.md`
- **Preconditions:** Clean worktree.
- **Test or evidence first:** Add the helper boundary tests (`2**32 - 1` accepted; `2**32`, `2**40` rejected with `TweakLengthError` naming the ceiling), the three constructor cases in `tests/test_validation.py` and in `_malformed_calls`, and the Rust `encode_len_u32` tests. Record that before the fix the Python path raises `OverflowError` from `_encode_uint` for a length of `2**32` (demonstrated on the helper, not by allocation) and the bound cases construct successfully.
- **Implementation tasks:**
  1. Add `_MAX_TWEAK_LEN` and `_validate_tweak_length`; call it first in `_validate_tweak`.
  2. Extend `_validate_tweak_bounds` with the two ceiling rejections, message naming `2**32 - 1`.
  3. In `lib.rs`, add `encode_len_u32` and use it for both `n` and `t`; keep the P-block byte layout identical.
  4. Document the ceiling in `docs/configuration.md` §Runtime Constraints and the README parameter table row for `tweak`/`min_tweak_len`/`max_tweak_len`.
- **Documentation/configuration/operations:** `docs/configuration.md`, `README.md`; changelog entry (SemVer-flagged) in STEP-09.
- **Verification:** `uv run pytest tests/test_validation.py tests/test_contract.py -q`; `cargo test --manifest-path rust/Cargo.toml`; `just rust-lint`; the §10 checkpoint; NIST, intermediate and frozen-KAT suites unchanged.
- **Completion criteria:** Identical `TweakLengthError` type and message on both backends for every new case; no allocation above kilobytes in the tests; ordinary-input outputs unchanged; one commit.
- **Rollback or recovery:** Revert the commit.
- **Builder stop conditions:** Any ciphertext change for a currently valid input; any divergence in exception type or message between backends; any test that needs a multi-gigabyte tweak.

### PLAN-00007-STEP-03 — Complete the dual-backend public-contract sweep

- **Status placeholder:** `not-started`
- **Objective:** Exercise the remaining public-contract acceptance cases on both backends.
- **Requirements:** `PLAN-00007-REQ-03`
- **Depends on:** None
- **Affected components:** `tests/test_validation.py`, `tests/test_interoperability.py`
- **Preconditions:** Clean worktree.
- **Test or evidence first:** With the extension built, record `uv run pytest --collect-only -q -k rust | tail -1` before the change and confirm none of the seven named tests appears in the rust selection.
- **Implementation tasks:**
  1. Route the six `tests/test_validation.py` cases through `ff1_factory`, keeping every assertion.
  2. Route `test_tweak_bounds_map_across_apis` through `ff1_factory`.
  3. Leave conversion-internals and backend-selection tests unparameterized.
- **Documentation/configuration/operations:** None.
- **Verification:** `uv run pytest tests/test_validation.py tests/test_interoperability.py -q`; the collect-only count after the change shows the added rust cases; the §10 checkpoint.
- **Completion criteria:** Each named test collects and passes for both backends with unchanged expected outcomes; one commit.
- **Rollback or recovery:** Revert the commit.
- **Builder stop conditions:** Any assertion weakened or removed to pass on both backends.

### PLAN-00007-STEP-04 — Port the divide-and-conquer conversion to the Rust core

- **Status placeholder:** `not-started`
- **Objective:** Make the Rust conversion subquadratic while remaining bit-exact with the reference and comparable to it line by line.
- **Requirements:** `PLAN-00007-REQ-04`
- **Depends on:** PLAN-00007-STEP-01, STEP-02, STEP-03
- **Affected components:** `rust/fpr-ff1-rust/src/lib.rs`, `rust/fpr-ff1-rust/src/tests.rs`, new `tests/test_backend_agreement.py`, `docs/architecture.md`
- **Preconditions:** STEP-01 to STEP-03 committed; `just rust-lint` green.
- **Test or evidence first:** Write the Rust equivalence tests against `num_radix_reference`/`str_radix_reference` and the Python direct-comparison module first; the comparison module passes already (both cores are currently correct) and is the regression net for the port; the Rust equivalence tests fail to compile until the new functions exist.
- **Implementation tasks:**
  1. Rename the naive loops to `num_radix_reference`/`str_radix_reference` with doc comments naming SP 800-38G and `_ff1.py::_num_radix_reference`/`_str_radix_reference`.
  2. Add `pub const D_C_THRESHOLD: usize = 64;` with a doc comment naming `_ff1.py::_D_C_THRESHOLD`.
  3. Add the power-of-two packing pair and the divide-and-conquer pair with a call-local `Vec`/`HashMap` power cache passed by `&mut`, mirroring `_num_radix_split`/`_str_radix_split`.
  4. Add dispatching `num_radix`/`str_radix` with the same three-way dispatch order as Python (power of two, then threshold, then split).
  5. Confirm `ff1_impl`'s three call sites still call `num_radix`/`str_radix` (names unchanged) and that no other caller uses the reference functions in production.
  6. Run the Rust equivalence tests, `cargo test`, and the full dual-backend gate to green.
  7. Add a paragraph to `docs/architecture.md` describing the mirrored dispatch in both cores.
- **Documentation/configuration/operations:** `docs/architecture.md` in this step; README performance text in STEP-05.
- **Verification:** `cargo test --manifest-path rust/Cargo.toml`; `just rust-lint`; `just backend-dev`; the §10 checkpoint including per-round intermediates; `uv run pytest tests/test_backend_agreement.py -q`; `grep -n "static\|OnceLock\|unsafe" rust/fpr-ff1-rust/src/lib.rs` unchanged from baseline.
- **Completion criteria:** Suite bit-exact on both backends; equivalence and direct-comparison tests green; no shared mutable state; `D_C_THRESHOLD == 64`; one commit.
- **Rollback or recovery:** Revert the commit; the reference loops remain intact.
- **Builder stop conditions:** Any ciphertext or intermediate-value divergence; any need for `unsafe`, a `static`, or instance-held state; any radix in the full sweep where fast and reference disagree.

### PLAN-00007-STEP-05 — Refresh performance evidence under the park rule

- **Status placeholder:** `not-started`
- **Objective:** Re-measure the backend crossover and update guidance only if the port delivers.
- **Requirements:** `PLAN-00007-REQ-05`
- **Depends on:** PLAN-00007-STEP-04
- **Affected components:** `benchmarks/timing.py` (only if a quoted shape is missing), `README.md` §Backends, `CHANGELOG.md`
- **Preconditions:** STEP-04 committed; `just backend-dev` release build present.
- **Test or evidence first:** Run `just bench` with the release extension; record in the work log: machine, OS, CPython version, `rustc --version`, `fpr_ff1.__version__`, `fpr_ff1._rs.__version__`, every table row, the GIL probe.
- **Implementation tasks:**
  1. Apply the park rule: `rust <= python` per-call at n = 20,000 on radix 10 and radix 256. Record the verdict.
  2. On a pass: rewrite the README Backends table and prose from the recorded run (drop "deliberately uses the naive spec-reference conversion"; state the measured band); write the changelog performance note for STEP-09.
  3. On a fail: stop, escalate with the numbers, leave the README's crossover guidance in place.
- **Documentation/configuration/operations:** README and changelog are the documentation work.
- **Verification:** Every README number traces to the work-log run; `uv run ruff format --check .` and `ruff check .` clean.
- **Completion criteria:** Park-rule verdict recorded; README/changelog match the run or an escalation entry exists; one commit (on a pass).
- **Rollback or recovery:** Revert the commit.
- **Builder stop conditions:** A README number not present in the recorded run; a park-rule fail (escalate, do not proceed to STEP-06 without the user's decision).

### PLAN-00007-STEP-06 — Execute every published native wheel in the release gate

- **Status placeholder:** `not-started`
- **Objective:** Make the gate install and exercise each published native wheel from the artifact, and run full conformance against an abi3 distribution build.
- **Requirements:** `PLAN-00007-REQ-06`
- **Depends on:** PLAN-00007-STEP-01 to STEP-05
- **Affected components:** `.github/workflows/ci.yml`
- **Preconditions:** All code steps committed and locally green; user authorization to push the branch (the jobs only prove themselves in CI).
- **Test or evidence first:** The jobs are the evidence. Before pushing, validate the workflow locally with `uvx --from yamllint yamllint .github/workflows/ci.yml` (or equivalent) and dry-run the install recipe on the local machine: build a wheel with `uvx maturin@1.15.0 build --release --locked --out dist-native`, `uv venv /tmp/w --python 3.14`, `uv export --frozen --no-emit-project --no-hashes -o requirements-ci.txt`, `uv pip install --python /tmp/w -r requirements-ci.txt dist-native/*.whl`, then run the import-origin check and the subset with `/tmp/w/bin/python -m pytest ...` from the checkout.
- **Implementation tasks:**
  1. In `wheel-build`: add `--locked` to the maturin command; add a step printing `rustc --version` and `cargo --version`.
  2. In `rust-conformance`: add `--locked` to `cargo build`.
  3. Replace `wheel-test-platform` with `wheel-test-native`: `strategy.matrix.include` of the five `{os, target}` pairs from REQ-06 crossed with `python-version: ["3.12", "3.13", "3.14"]`; `needs: wheel-build`; download `wheels-${{ matrix.target }}`; `uv venv wheel-venv --python ${{ matrix.python-version }}`; the export-and-install recipe; the import-origin step; the subset run with both flags. Use `wheel-venv/bin/python` on POSIX and `wheel-venv\Scripts\python.exe` on Windows (a small `if: runner.os == 'Windows'` split or a shell-agnostic `uv run --python wheel-venv --no-project` invocation is acceptable, provided the editable project is never installed).
  4. Add `wheel-conformance-abi3`: `ubuntu-24.04`, Python 3.14, the linux x86_64 wheel, same recipe and import-origin step, then the `-k rust >= 500` floor and the full suite with coverage, both flags set.
  5. Keep the existing `wheel-test` (pure wheel) and `sdist-test` jobs unchanged.
  6. Push the branch (user-authorized) and iterate until every job is green; record the run URL.
- **Documentation/configuration/operations:** `docs/developer-guide.md` CI description updated in STEP-08.
- **Verification:** All fifteen subset jobs and the abi3 leg green; each import-origin step's log shows both paths under the venv; the abi3 leg's log shows `-k rust` count `>= 500` and `TOTAL ... 100%`; `wheel-build` logs show the compiler version.
- **Completion criteria:** Green run with every new job present; one commit (plus fix-up commits squashed or kept, per the user's preference recorded in the work log).
- **Rollback or recovery:** Revert the workflow commit; the package remains installable pure-Python.
- **Builder stop conditions:** The import-origin step resolving to the checkout (escalate: never mask it by adjusting the assertion); a runner label unavailable (escalate with the label; do not substitute a `-large` label without authorization); a target that cannot be made green (escalate rather than drop the target).

### PLAN-00007-STEP-07 — Produce the CI negative-control evidence

- **Status placeholder:** `not-started`
- **Objective:** Prove in CI that the Rust and installed-wheel gates fail on a controlled core defect.
- **Requirements:** `PLAN-00007-REQ-07`
- **Depends on:** PLAN-00007-STEP-06
- **Affected components:** None (a disposable branch)
- **Preconditions:** STEP-06 green in CI; user authorization to push and later delete a disposable branch.
- **Test or evidence first:** This step is the evidence.
- **Implementation tasks:**
  1. Create `negative-control/plan-00007` from the STEP-06 commit; change the S-expansion counter initialisation in `lib.rs` from `1` to `0`; commit with a message stating it must never be tagged or merged.
  2. Push (user-authorized); wait for the run; record the URL and the names of every failed job.
  3. Confirm `quality` (pure Python) stayed green and `rust-conformance`, all `wheel-test-native` jobs and `wheel-conformance-abi3` failed.
  4. Delete the branch on `origin` (user-authorized) and locally.
- **Documentation/configuration/operations:** Work-log entry cross-referenced to plan 00005 `AC-02`.
- **Verification:** The recorded run shows the expected red set; the mutated commit is unreachable from any tag or from `release/v2`.
- **Completion criteria:** Evidence recorded; branch deleted.
- **Rollback or recovery:** Delete the branch; nothing else changes.
- **Builder stop conditions:** The mutation does not turn every Rust-executing job red (escalate: the gate has a hole); any attempt to tag or merge the mutated revision.

### PLAN-00007-STEP-08 — Make support and deployment statements precise

- **Status placeholder:** `not-started`
- **Objective:** Document the native-wheel floor and fallback, transcribe the D4 support policy, clarify the coverage claim, recheck NIST status, and describe the new CI jobs.
- **Requirements:** `PLAN-00007-REQ-08`
- **Depends on:** PLAN-00007-STEP-06; decision D4 resolved in §7
- **Affected components:** `README.md`, `SECURITY.md`, `CHANGELOG.md`, `docs/configuration.md`, `docs/developer-guide.md`
- **Preconditions:** STEP-06 committed.
- **Test or evidence first:** Not applicable (documentation). Confirm `grep -n "Supported versions" -A 12 SECURITY.md` shows the pre-change text so the diff is reviewable.
- **Implementation tasks:**
  1. README Backends and `docs/configuration.md`: native-wheel coverage and the `manylinux_2_34`/glibc 2.34 floor with the pure fallback statement.
  2. `SECURITY.md`: replace §Supported versions with the D4 text verbatim.
  3. Coverage wording in `README.md`, `CHANGELOG.md` (the rc2 section drafted for STEP-09) and `docs/developer-guide.md`.
  4. NIST Rev. 1 status check; record the date and finding in the work log; no document change unless the status changed (then escalate: a finalised revision with different limits is a major-version question).
  5. `docs/developer-guide.md` CI/CD section: the `wheel-test-native` matrix, the `wheel-conformance-abi3` leg, `--locked`.
- **Documentation/configuration/operations:** This step is the documentation work.
- **Verification:** `uv run ruff format --check .` and `ruff check .` clean; `git diff --stat` touches only the five documents; the `SECURITY.md` diff equals the D4 text.
- **Completion criteria:** Statements present and sourced; one commit.
- **Rollback or recovery:** Revert the commit.
- **Builder stop conditions:** A `SECURITY.md` text that differs from §7.1 Option A beyond the placeholder; any statement that cannot be sourced from a shipped artifact or a resolved decision; a NIST status change.

### PLAN-00007-STEP-09 — Cut the rc2 candidate version

- **Status placeholder:** `not-started`
- **Objective:** Produce the `2.0.0rc2` candidate with consistent versions, locks, changelog and backlog.
- **Requirements:** `PLAN-00007-REQ-10` (version and documentation portion)
- **Depends on:** PLAN-00007-STEP-01 to STEP-08
- **Affected components:** `pyproject.toml`, `rust/fpr-ff1-rust/Cargo.toml`, `uv.lock`, `rust/Cargo.lock`, `CHANGELOG.md`, `docs/backlog.md`
- **Preconditions:** All prior steps committed and green.
- **Test or evidence first:** Bump one manifest first and record `uv run pytest tests/test_contract.py -q` red; bump the other and record green.
- **Implementation tasks:**
  1. `pyproject.toml` to `2.0.0rc2`; `rust/fpr-ff1-rust/Cargo.toml` to `2.0.0-rc2`; `uv lock`; `cargo build --locked` (expect only the local crate's version line to change in `rust/Cargo.lock`).
  2. Changelog `[2.0.0rc2]` dated section: `### Fixed` (legacy pickle, tweak ceiling with the SemVer note), `### Changed` (Rust conversion with the STEP-05 numbers, release gate now executes every native wheel, `--locked` builds), `### Added` (bound-ceiling rejection, attribute-parity test); comparison link `v2.0.0rc1...v2.0.0rc2`; `[Unreleased]` link updated.
  3. `docs/backlog.md`: move the conversion item to Completed with the measured result; add the plan 00007 line under Completed at STEP-14.
- **Documentation/configuration/operations:** Changelog and backlog are the documentation work.
- **Verification:** `uv lock --check`; `cargo build --locked` leaves the lock unchanged on a second run; `uv run pytest tests/test_contract.py -q`; `uv run ruff format --check .` and `ruff check .` clean.
- **Completion criteria:** Versions, locks, changelog and backlog consistent; one commit.
- **Rollback or recovery:** Revert the commit.
- **Builder stop conditions:** `uv lock` or `cargo build` changing more than the intended version edges (escalate).

### PLAN-00007-STEP-10 — Run the full gate and verify build and package consistency

- **Status placeholder:** `not-started`
- **Objective:** Prove the rc2 candidate green end to end and its artifacts correct as artifacts.
- **Requirements:** `PLAN-00007-REQ-09`
- **Depends on:** PLAN-00007-STEP-09
- **Affected components:** None (verification only)
- **Preconditions:** STEP-09 committed; branch pushed (user-authorized) so CI runs at the candidate commit.
- **Test or evidence first:** This step is the evidence.
- **Implementation tasks:**
  1. Local: `just quality`; `just rust-test`; `just rust-lint`; the full dual-backend gate; `uv lock --check`; `cargo build --locked --manifest-path rust/Cargo.toml`; `uv build` and `uvx twine check dist/*`; `uvx maturin@1.15.0 build -m rust/fpr-ff1-rust/Cargo.toml --release --locked --out dist-native` and `uvx twine check dist-native/*`; the audits and `just secrets`; `rustc --version` and `cargo --version` recorded.
  2. Package contents: list the sdist, pure wheel and native wheel members; assert the presence and absence lists from REQ-09; assert `fpr_ff1/_rs.abi3.so` in the native wheel.
  3. Sdist fallback: fresh venv, `uv pip install dist/*.tar.gz`, `FF1(..., backend="rust")` raises `BackendError`, NIST sample 2 passes on the python backend.
  4. Packaged tests from the unpacked sdist: `tar xf`, fresh venv, install the sdist plus `pytest hypothesis packaging`, `python -m pytest -q` inside the unpacked tree; record pass count and skips (oracle and rust only).
  5. CI: record the run URL at the candidate commit, green in every job including the new ones.
- **Documentation/configuration/operations:** None.
- **Verification:** Every command green with output in the work log; lock files unchanged; contents checks pass; unpacked-sdist run passes with only oracle and rust skips.
- **Completion criteria:** Full gate green locally and in CI; artifacts verified; sdist fallback and packaged tests proven; compiler versions recorded.
- **Rollback or recovery:** Not applicable.
- **Builder stop conditions:** Any red gate; any package-contents violation; a skip in the unpacked-sdist run other than oracle or rust.

### PLAN-00007-STEP-11 — Owner publishes `v2.0.0rc2`; Builder verifies; soak

- **Status placeholder:** `not-started`
- **Objective:** Give the candidate its own immutable release evidence and a soak point before promotion.
- **Requirements:** `PLAN-00007-REQ-10` (publication and verification portion)
- **Depends on:** PLAN-00007-STEP-10
- **Affected components:** None (owner release actions; Builder verification)
- **Preconditions:** STEP-10 green; the frozen rc2 commit hash recorded in the work log.
- **Test or evidence first:** This step is the evidence.
- **Implementation tasks:**
  1. Builder writes the hand-off entry: commit hash, CI run URL, local gate summary.
  2. **Owner** tags exactly `v2.0.0rc2` at that commit, pushes the tag, publishes a GitHub release marked **pre-release**; `publish.yml` runs.
  3. Builder verifies the public candidate: PyPI JSON shows `2.0.0rc2` with seven files, non-yanked; attestation subject digests match the CI artifacts (download the workflow artifacts and compare SHA-256); fresh venv `uv pip install fpr-ff1==2.0.0rc2` on the local platform, import-origin check, NIST vectors and a `d > 16` case on both backends; a second venv with `--no-binary fpr-ff1` proves the pure fallback and the `BackendError` contract.
  4. **Owner** records the D6 soak statement in the work log ("soak until <UTC date>" or "soak waived; proceed on verified publication").
- **Documentation/configuration/operations:** Work log only.
- **Verification:** `publish.yml` run URL green; PyPI verification results recorded; soak statement present.
- **Completion criteria:** `v2.0.0rc2` public, verified, and the soak statement recorded; STEP-12 may start only after the soak date (if any) has passed.
- **Rollback or recovery:** A defective rc2 is left in place (never overwritten or retagged); fixes go into a new candidate number.
- **Builder stop conditions:** Any file-set, metadata or attestation mismatch; any behavioural difference between the public artifact and the gated candidate.

### PLAN-00007-STEP-12 — Obtain the independent re-review

- **Status placeholder:** `not-started`
- **Objective:** Independent verification of the rc2 change set before any final bump.
- **Requirements:** `PLAN-00007-REQ-11`
- **Depends on:** PLAN-00007-STEP-11
- **Affected components:** `docs/reviews/` (a new numbered report written by the reviewer, not by Builder)
- **Preconditions:** STEP-11 complete; soak elapsed or waived.
- **Test or evidence first:** The review is the evidence.
- **Implementation tasks:**
  1. Builder prepares the evidence bundle in the work log: commit range `v2.0.0rc1..v2.0.0rc2`, CI run URLs (STEP-06, STEP-07, STEP-10, `publish.yml`), bench run, PyPI verification.
  2. **Owner** requests the read-only re-review with review 00007 as predecessor.
  3. Owner dispositions any remaining non-Major finding in the work log (fix in a further candidate, or accept with reason).
- **Documentation/configuration/operations:** None by Builder.
- **Verification:** The new review's front matter shows `critical: 0`, `major: 0` and classifies the four 00007 findings as resolved.
- **Completion criteria:** Review exists and meets the bar; dispositions recorded.
- **Rollback or recovery:** A Critical or Major finding sends the work back to a new candidate (`2.0.0rc3`), following STEP-09 to STEP-12 again; never bump to final.
- **Builder stop conditions:** Any Critical or Major finding; any finding classified `still-open` from review 00007.

### PLAN-00007-STEP-13 — Bump to final and finish the release documentation

- **Status placeholder:** `not-started`
- **Objective:** Prepare the exact final commit.
- **Requirements:** `PLAN-00007-REQ-12`
- **Depends on:** PLAN-00007-STEP-12
- **Affected components:** `pyproject.toml`, `rust/fpr-ff1-rust/Cargo.toml`, `uv.lock`, `rust/Cargo.lock`, `CHANGELOG.md`, `README.md`, `SECURITY.md`, `docs/backlog.md`
- **Preconditions:** STEP-12 clean.
- **Test or evidence first:** Contract test red after the first manifest bump, green after the second.
- **Implementation tasks:**
  1. Bump both manifests to `2.0.0`; refresh both locks.
  2. Changelog `[2.0.0]` dated section summarising the 2.0 feature and the post-rc fixes; comparison links; `[Unreleased]` at `v2.0.0...HEAD`; rc sections intact.
  3. README roadmap row: replace "Shipped as `2.0.0rc1`" with the final statement; `SECURITY.md`: replace the `<v2.0.0 date + six months>` placeholder with the planned tag date plus six months (ISO date), recording both dates in the work log.
  4. Repeat the NIST status check; record the date.
- **Documentation/configuration/operations:** Changelog, README, SECURITY.md.
- **Verification:** `uv lock --check`; `uv run pytest tests/test_contract.py -q`; `uv run ruff format --check .` and `ruff check .`; `grep -rn "<v2.0.0 date" .` empty.
- **Completion criteria:** Final version, locks and docs consistent; one commit.
- **Rollback or recovery:** Revert the commit.
- **Builder stop conditions:** Lock drift beyond the version edges; a NIST status change.

### PLAN-00007-STEP-14 — Freeze, owner publishes `v2.0.0`, verify, record the handoff

- **Status placeholder:** `not-started`
- **Objective:** Deliver stable `v2.0.0` and record the recovery procedure.
- **Requirements:** `PLAN-00007-REQ-13`
- **Depends on:** PLAN-00007-STEP-13
- **Affected components:** `docs/backlog.md` (completion record); otherwise owner release actions
- **Preconditions:** STEP-13 committed and pushed (user-authorized); CI green at that commit.
- **Test or evidence first:** This step is the release evidence.
- **Implementation tasks:**
  1. Rerun the STEP-10 local gate at the final commit; record the CI run URL; confirm the `pypi` environment and Trusted Publisher binding unchanged (owner checks the PyPI publisher settings page; Builder records the confirmation).
  2. **Owner** tags exactly `v2.0.0`, pushes, publishes a non-prerelease GitHub release; `publish.yml` runs.
  3. Builder verifies the public release exactly as in STEP-11 task 3, for `2.0.0`, plus discoverability without prerelease opt-in (`uv pip install fpr-ff1` in a fresh venv resolves `2.0.0`).
  4. Record the handoff: commit and tag, run URLs, artifact digests, compiler versions, support policy (D4 text), verification outcome, recovery procedure.
  5. `docs/backlog.md`: record plan 00007 as completed (the one post-release commit this step makes, user-authorized).
- **Documentation/configuration/operations:** Handoff and recovery record; backlog.
- **Verification:** `v2.0.0` on PyPI with seven files and attestations; behaviour matches the gated candidate; handoff recorded.
- **Completion criteria:** Stable `v2.0.0` published and verified; recovery procedure recorded.
- **Rollback or recovery:** For a defective release: stop promotion, notify users, consider yanking plus a corrected `2.0.1`; never replace published files or retag history.
- **Builder stop conditions:** Any red gate at the final commit; any attestation or artifact mismatch.

## 12. Cross-cutting concerns

| Area | Applicability | Planned action or reason not applicable | Step or requirement |
|---|---|---|---|
| Compatibility and APIs | Applicable | Legacy pickles restore; the tweak and bound ceiling is a new rejection flagged SemVer-relevant in the changelog; no public API change; ciphertext unchanged | REQ-01, REQ-02; STEP-01, STEP-02, STEP-09 |
| Data and migration | Applicable | 1.x pickles must restore; no other persisted state | REQ-01; STEP-01 |
| Security and privacy | Applicable | Fail-closed ceiling closes a parity gap; support policy decided by the maintainer (D4); no new key handling; no constant-time claim | REQ-02, REQ-08; STEP-02, STEP-08 |
| Performance and scale | Applicable | Rust D&C port under a park rule; measurements recorded before any claim | REQ-04, REQ-05; STEP-04, STEP-05 |
| Reliability and failure handling | Applicable | Identical typed errors on both backends; installed-wheel jobs hard-fail on import-origin, ABI or conformance defects | REQ-02, REQ-06; STEP-02, STEP-06 |
| Observability and operations | Not applicable | Library without telemetry; the benchmark harness and work log are the operational evidence | — |
| Dependencies and supply chain | Applicable | `--locked` release builds; audits and secret gate re-run; compiler version recorded; attestation digests compared; no new dependency | REQ-06, REQ-09, REQ-10, REQ-13; STEP-06, STEP-10, STEP-11, STEP-14 |
| Accessibility and UX | Not applicable | No UI | — |
| Documentation and release | Applicable | glibc floor, D4 text, coverage wording, changelog and backlog, README guidance, rc2 then final | REQ-05, REQ-08, REQ-10, REQ-12; STEP-05, STEP-08, STEP-09, STEP-13 |
| Deployment and rollback | Applicable | rc2 published and soaked; final via the gated pipeline; yank-and-correct recovery recorded | REQ-10, REQ-13; STEP-11, STEP-14 |

## 13. Verification strategy

| Level | Evidence or command | When | Required result |
|---|---|---|---|
| Focused Python | `uv run pytest tests/test_backend_dispatch.py tests/test_pickle.py tests/test_validation.py tests/test_contract.py tests/test_interoperability.py -q` | STEP-01 to STEP-03 | Green |
| Rust unit | `cargo test --manifest-path rust/Cargo.toml` | STEP-02, STEP-04, STEP-10, STEP-14 | Green including new tests |
| Rust hygiene | `just rust-lint` | STEP-02, STEP-04, STEP-10, STEP-14 | Exit 0 |
| Rust-free gate | `just quality` | Every checkpoint | Green without the extension |
| Full dual-backend gate | `FPR_FF1_REQUIRE_RUST_BACKEND=1 FPR_FF1_REQUIRE_ORACLE=1 uv run pytest --cov=fpr_ff1 --cov-report=term-missing --cov-fail-under=100` | STEP-01 to STEP-05, STEP-10, STEP-14 | 100% line and branch; bit-exact including intermediates |
| Direct backend agreement | `uv run pytest tests/test_backend_agreement.py -q` | STEP-04 onward | Green |
| Static (Python) | `uv run ruff format --check .`; `uv run ruff check .`; `uv run pyright` | STEP-05, STEP-08, STEP-09, STEP-13 | Clean |
| Lock consistency | `uv lock --check`; `cargo build --locked` leaves `rust/Cargo.lock` unchanged | STEP-09, STEP-10, STEP-13 | Consistent |
| Benchmark and park rule | `just bench` with the release extension; `rust <= python` at n = 20,000, radix 10 and 256 | STEP-05 | Recorded; pass or escalation |
| CI wheel matrix | `wheel-test-native` (15 jobs) with import-origin steps; `wheel-conformance-abi3` with `-k rust >= 500` and 100% coverage | STEP-06, STEP-10, STEP-14 | Green and inside `ci.yml` |
| Negative control | Disposable-branch mutation | STEP-07 | Rust and installed-wheel jobs red, `quality` green; run URL recorded |
| Packaging | `uv build`, `uvx maturin ... --locked`, `uvx twine check`; contents lists; sdist fallback; unpacked-sdist `pytest` | STEP-10, STEP-14 | Pass; only oracle and rust skips |
| Candidate publication | `publish.yml` run; PyPI JSON; attestation digest comparison; fresh-venv installs | STEP-11 | Seven files, matching digests, both backends and fallback pass |
| Re-review | New numbered review of `v2.0.0rc1..v2.0.0rc2` | STEP-12 | No Critical or Major; 00007 findings resolved |
| Release verification | As candidate publication, for `2.0.0`, plus default resolution without prerelease opt-in | STEP-14 | Pass; handoff recorded |

## 14. Acceptance criteria

- [ ] `PLAN-00007-AC-01` A 1.1-format pickle state restores on `FF1.__new__(FF1)` with `_backend == "python"`, all four operations succeed, a second cycle round-trips; `set(vars(restored)) == set(vars(fresh))` holds for python and rust instances; the three corrected tests restore onto an uninitialized object.
- [ ] `PLAN-00007-AC-02` A tweak length of `2**32` or more, and `min_tweak_len` or `max_tweak_len` above `2**32 - 1`, raise `TweakLengthError` with identical messages on both backends before any FF1 calculation; `_malformed_calls` contains the constructor cases; `encode_len_u32` is used for both `n` and `t`; no test allocates a multi-gigabyte tweak; ordinary outputs unchanged.
- [ ] `PLAN-00007-AC-03` The seven named public-contract tests collect and pass for both backends with unchanged assertions.
- [ ] `PLAN-00007-AC-04` `lib.rs` has `D_C_THRESHOLD = 64`, `num_radix_reference`/`str_radix_reference`, and dispatching `num_radix`/`str_radix` with power-of-two and divide-and-conquer paths; `cargo test` and the full dual-backend suite are green and bit-exact; `tests/test_backend_agreement.py` passes; no `static`, `OnceLock` or `unsafe` added.
- [ ] `PLAN-00007-AC-05` The `just bench` run is recorded with machine, interpreter, `rustc --version` and versions; the park-rule verdict is recorded; every README and changelog performance number traces to that run.
- [ ] `PLAN-00007-AC-06` Fifteen `wheel-test-native` jobs on the named runners and the `wheel-conformance-abi3` leg are green on the pushed branch; every import-origin step shows the installed wheel; the abi3 leg shows `-k rust >= 500` and 100% coverage; `wheel-build` and `rust-conformance` use `--locked`; `rustc --version` is printed.
- [ ] `PLAN-00007-AC-07` A recorded run on a disposable branch shows the S-expansion mutation failing `rust-conformance`, all `wheel-test-native` jobs and `wheel-conformance-abi3` while `quality` stays green; the branch is deleted; the mutated commit is on no tag.
- [ ] `PLAN-00007-AC-08` `README.md`, `docs/configuration.md`, `docs/developer-guide.md` and `SECURITY.md` state the native-wheel coverage and glibc 2.34 floor, the pure fallback, the D4 text verbatim, and the coverage clarification; the NIST status check date is recorded.
- [ ] `PLAN-00007-AC-09` At the rc2 commit: versions `2.0.0rc2` / `2.0.0-rc2`, locks consistent, changelog and backlog updated; the full local gate, audits, secret scan, package-contents checks, sdist fallback and unpacked-sdist `pytest` run pass; compiler versions recorded; CI green at that commit.
- [ ] `PLAN-00007-AC-10` `v2.0.0rc2` is tagged by the owner, published as a pre-release, and verified on PyPI (seven files, attestation digests matching CI artifacts, fresh-venv installs on both backends and the pure fallback); the D6 soak statement is in the work log.
- [ ] `PLAN-00007-AC-11` A new numbered review of `v2.0.0rc1..v2.0.0rc2` exists with no Critical or Major finding and the four review 00007 findings classified resolved; any remaining finding is dispositioned in the work log.
- [ ] `PLAN-00007-AC-12` Versions `2.0.0` / `2.0.0`, locks consistent, `[2.0.0]` changelog with links, README roadmap and `SECURITY.md` version cell updated, no `<v2.0.0 date` placeholder remains; the contract test passes.
- [ ] `PLAN-00007-AC-13` `v2.0.0` is tagged by the owner, published as a non-prerelease, resolves by default on PyPI, and passes the same verification as AC-10.
- [ ] `PLAN-00007-AC-14` The handoff record (commit and tag, run URLs, artifact digests, compiler versions, support policy, verification outcome, recovery procedure) is in the work log and `docs/backlog.md` records plan 00007 as completed.

## 15. Risks and mitigations

| Risk | Likelihood | Impact | Mitigation or test | Owner/step |
|---|---|---|---|---|
| The D4 six-month date is computed wrongly at STEP-13 | Low | Low | STEP-13 verification greps for the placeholder and the work log records the tag date and the computed date side by side | Builder/STEP-13 |
| Rust D&C port diverges bit-wise on some radix | Medium | High | Full-radix equivalence sweep, per-round intermediates, direct encrypt and decrypt comparisons | Builder/STEP-04 |
| Port fails the park rule | Low | Medium | Rule recorded before measurement; escalation path leaves README guidance in place | Builder/STEP-05 |
| Conversion introduces shared mutable state | Low | High | Call-local cache by `&mut`; grep for `static`/`OnceLock`/`unsafe`; thread-safety suite | Builder/STEP-04 |
| A wheel job silently tests the checkout instead of the wheel | Medium | High | Fresh venv, no `uv sync`/`uv run`, import-origin step, stop condition | Builder/STEP-06 |
| `macos-15-intel` label retired or renamed | Low | Medium | Escalate with the current label list; never substitute a `-large` label unasked | Builder/STEP-06 |
| Windows venv path handling breaks the subset job | Medium | Low | Explicit `runner.os` split or `uv run --no-project`; the Windows arm is otherwise unchanged | Builder/STEP-06 |
| Exported requirements with hashes reject the local wheel | Medium | Low | `--no-hashes` in the export recipe | Builder/STEP-06 |
| Negative-control mutation leaves some Rust-executing job green | Low | High | Stop condition: escalate; the gate has a hole | Builder/STEP-07 |
| Re-review surfaces a new Major | Medium | High | rc2 soak; new candidate number; never bump to final on red | Owner/STEP-12 |
| Version or lock drift beyond the intended edges | Low | Medium | `uv lock --check`; `cargo build --locked`; stop condition | Builder/STEP-09, STEP-13 |
| Crossover numbers differ on other hardware | Medium | Low | README states the band as measured on named hardware and points at `just bench` | Builder/STEP-05 |

## 16. Builder hand-off

- **Start condition:** User approval and a clean repository on `release/v2`.
- **First step:** PLAN-00007-STEP-01.
- **Required sequence:** STEP-01, STEP-02, STEP-03 (any order) → STEP-04 → STEP-05 → STEP-06 → STEP-07 → STEP-08 → STEP-09 → STEP-10 → STEP-11 → STEP-12 → STEP-13 → STEP-14.
- **Parallel-safe work:** STEP-01, STEP-02 and STEP-03 only.
- **Do not change:** approved scope, requirements, steps, acceptance criteria, or content outside Builder's permitted work-log area. Do not change the pure-Python path's ciphertext, public API or default backend. Do not add FF3/FF3-1, key management, a compatibility shim, a runtime dependency, `unsafe`, or shared state. Do not lower the native-wheel floor. Do not edit plan 00006 or any review. Do not tag, push, publish, or delete remote branches without a per-action authorization recorded in the work log.
- **Escalate when:** any ciphertext or intermediate divergence; a park-rule fail; an import-origin check resolving to the checkout; a runner label unavailable; a target that cannot be made green; the negative-control mutation leaving a Rust-executing job green; a NIST status change; a re-review Critical or Major; a README number not in a recorded run; a `SECURITY.md` text that differs from §7.1 Option A.
- **Completion hand-off:** `v2.0.0rc2` tagged, published as a pre-release, verified and soaked (owner statement); re-review clean; `v2.0.0` tagged (exactly), published, verified; handoff and recovery procedure recorded; backlog updated. Tags, pushes and GitHub releases remain the user's.

<!-- BUILDER_WORK_LOG_START -->
## 17. Builder Work Log

> [!warning] Builder-maintained section
> Delivery Planner creates this section. After approval, Builder may update only
> this delimited section and the Builder-maintained front-matter fields. Builder
> must preserve prior entries and use UTC timestamps.

### Step status

| Step | Status | Started (UTC) | Completed (UTC) | Evidence | Builder notes |
|---|---|---|---|---|---|
| PLAN-00007-STEP-01 | completed | 2026-09-16T12:32:08Z | 2026-09-16T12:42:01Z | Commit (this one); red-then-green recorded; checkpoint green | The plan-named parity test passes before the fix by design (a current-format payload already carries _backend); the red evidence is the same vars() parity assertion inside the legacy round-trip test |
| PLAN-00007-STEP-02 | completed | 2026-09-16T12:42:01Z | 2026-09-16T12:51:56Z | Commit (this one); checkpoint logs checkpoint-124333 | Ceiling message: 'tweak length N above encodable maximum 4294967295'. Changelog wording (SemVer note) deferred to STEP-09 as planned |
| PLAN-00007-STEP-03 | completed | 2026-09-16T12:51:56Z | 2026-09-16T13:00:49Z | Commit (this one); checkpoint logs checkpoint-125233 | No assertion weakened; pyright ignore comments on direct FF1 calls removed because ff1_factory returns Any |
| PLAN-00007-STEP-04 | not-started | — | — | — | — |
| PLAN-00007-STEP-05 | not-started | — | — | — | — |
| PLAN-00007-STEP-06 | not-started | — | — | — | — |
| PLAN-00007-STEP-07 | not-started | — | — | — | — |
| PLAN-00007-STEP-08 | not-started | — | — | — | — |
| PLAN-00007-STEP-09 | not-started | — | — | — | — |
| PLAN-00007-STEP-10 | not-started | — | — | — | — |
| PLAN-00007-STEP-11 | not-started | — | — | — | — |
| PLAN-00007-STEP-12 | not-started | — | — | — | — |
| PLAN-00007-STEP-13 | not-started | — | — | — | — |
| PLAN-00007-STEP-14 | not-started | — | — | — | — |

Allowed status values: `not-started`, `in-progress`, `blocked`, `completed`,
`skipped`. A skipped step requires explicit user approval recorded in Evidence.

### Execution log

| Timestamp (UTC) | Step | Event | Evidence or reference | Next action |
|---|---|---|---|---|
| 2026-09-16T12:32:08Z | — | Builder started on approved plan (approval commit 57c4794); clean worktree on release/v2 | git status --porcelain empty; HEAD 57c4794 | Record baseline, then STEP-01 |
| 2026-09-16T12:42:01Z | PLAN-00007-STEP-01 | Tests written first: 3 __setstate__ tests restore onto FF1.__new__(FF1); added test_legacy_serialized_state_round_trips (real pickle payload with the pinned 1.1 attribute set) and test_unpickled_instance_has_every_constructor_attribute (both backends) | Before fix: 2 failed -- AttributeError '_backend' and the vars() parity assertion in the legacy test | Apply fix |
| 2026-09-16T12:42:01Z | PLAN-00007-STEP-01 | Fix: __setstate__ assigns self._backend = backend after validation | src/fpr_ff1/_ff1.py; 44 passed in the two modules | Checkpoint |
| 2026-09-16T12:51:56Z | PLAN-00007-STEP-02 | Tests written first: ceiling tests via a len() double (no allocation) on both backends; three constructor bound cases in test_validation.py and _malformed_calls; Rust encode_len_u32 tests | Before fix: 14 Python tests failed; Rust tests did not compile (unresolved encode_len_u32); _encode_uint(2**32, 4) raised OverflowError. Contract case bounds-min-unencodable already raised pre-fix, via the empty default tweak failing the minimum | Implement |
| 2026-09-16T12:51:56Z | PLAN-00007-STEP-02 | Implemented FF1._MAX_TWEAK_LEN, FF1._validate_tweak_length (called first in _validate_tweak), bound-ceiling checks in _validate_tweak_bounds, lib.rs encode_len_u32 for both n and t; documented in docs/configuration.md and README parameter table | 201 passed in test_validation.py + test_contract.py; cargo test 10 passed | Checkpoint |
| 2026-09-16T13:00:48Z | PLAN-00007-STEP-03 | Evidence first: -k rust over the seven named tests collected 0 cases | uv run pytest --collect-only -k 'rust and (...)' -> no tests collected (1428 deselected) | Parameterize |
| 2026-09-16T13:00:48Z | PLAN-00007-STEP-03 | Routed six test_validation.py tests and test_tweak_bounds_map_across_apis through ff1_factory; assertions unchanged; conversion-internals and backend-selection tests untouched | 14 rust cases now collected across the seven tests; 191 passed in the two modules with both flags set | Checkpoint |

### Deviations and blockers

| Timestamp (UTC) | Step | Deviation or blocker | Impact | Decision required from |
|---|---|---|---|---|

None

### Verification results

| Timestamp (UTC) | Step | Command or check | Result | Evidence |
|---|---|---|---|---|
| 2026-09-16T12:32:08Z | Baseline | just backend-dev; just rust-test; just rust-lint | Pass | cargo test 8 passed; fmt + clippy -D warnings exit 0; rustc 1.98.1, cargo 1.98.1 |
| 2026-09-16T12:32:08Z | Baseline | FPR_FF1_REQUIRE_RUST_BACKEND=1 FPR_FF1_REQUIRE_ORACLE=1 uv run pytest --cov=fpr_ff1 --cov-report=term-missing --cov-fail-under=100 | Pass | 1406 passed in 255.76s; coverage 100.00% (330 stmts, 114 branches); -k rust collects 550/1406 |
| 2026-09-16T12:42:01Z | PLAN-00007-STEP-01 | just format-check lint typecheck; just rust-test; just rust-lint | Pass | pyright 0 errors after annotating pickle.loads results as FF1 (first run: 4 reportUnknownArgumentType errors in the new tests) |
| 2026-09-16T12:42:01Z | PLAN-00007-STEP-01 | FPR_FF1_REQUIRE_RUST_BACKEND=1 FPR_FF1_REQUIRE_ORACLE=1 uv run pytest --cov=fpr_ff1 --cov-fail-under=100 | Pass | 1409 passed in 262.38s; TOTAL 331 stmts 0 miss 114 branches 100%; -k rust 551/1409. Run before the annotation-only test change |
| 2026-09-16T12:42:01Z | PLAN-00007-STEP-01 | just quality with src/fpr_ff1/_rs.so moved aside (Rust-free) | Pass | 858 passed, 5 skipped in 217.70s; coverage 100% |
| 2026-09-16T12:51:56Z | PLAN-00007-STEP-02 | static checks; just rust-test; just rust-lint | Pass | ruff + pyright clean; cargo test 10 passed; fmt + clippy -D warnings exit 0 |
| 2026-09-16T12:51:56Z | PLAN-00007-STEP-02 | FPR_FF1_REQUIRE_RUST_BACKEND=1 FPR_FF1_REQUIRE_ORACLE=1 uv run pytest --cov=fpr_ff1 --cov-fail-under=100 | Pass | 1428 passed in 266.98s; TOTAL 342 stmts 120 branches 100%; -k rust 559/1428; NIST, intermediates and frozen KAT unchanged |
| 2026-09-16T12:51:56Z | PLAN-00007-STEP-02 | just quality with _rs.so moved aside (Rust-free) | Pass | 869 passed, 5 skipped in 215.34s; coverage 100% |
| 2026-09-16T13:00:48Z | PLAN-00007-STEP-03 | static checks; just rust-test; just rust-lint | Pass | ruff + pyright clean; cargo test 10 passed; lint exit 0 |
| 2026-09-16T13:00:49Z | PLAN-00007-STEP-03 | FPR_FF1_REQUIRE_RUST_BACKEND=1 FPR_FF1_REQUIRE_ORACLE=1 uv run pytest --cov=fpr_ff1 --cov-fail-under=100 | Pass | 1442 passed in 260.89s; 100%; -k rust 573/1442 (was 559) |
| 2026-09-16T13:00:49Z | PLAN-00007-STEP-03 | just quality with _rs.so moved aside (Rust-free) | Pass | 869 passed, 5 skipped in 217.61s; 100% |

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
| 2026-09-16T11:38:45Z | draft | Initial draft written at `docs/plans/00007-Stable_v2.0.0_Release.md`, superseding draft plan 00006 (never approved). Resolves all seven findings of reviews 00008 and 00009: D4 reopened as blocking with three candidate texts; rc2 owner hand-off added (STEP-11); STEP-06 specified (labels, venv recipe, import-origin task, flags, fan-out); REQ-02 extended (bounds, `n` cast, contract sweep, SemVer note); park rule and threshold naming; attribute-parity test; sdist packaged-test run, compiler version and coverage wording restored. Baseline refreshed to `5eb518c`. | User request on 2026-09-16 to rewrite the plan from review 00009 and plan 00006 | User |
| 2026-09-16T12:20:57Z | draft | D4 resolved: user selected Option A (1.1.x security fixes until `2.1.0` or six months after `v2.0.0`; `1.0.x` dropped). `blocking_decisions` 1 → 0; REQ-08, STEP-08, STEP-13, §1, §10, §15, §16 and §20 updated to reference the chosen text; Options B and C retained in §7.1 as the record of what was offered. No requirement, step or acceptance-criterion count changed. | User decision on D4 ("D4, as recommended (A)") | User |
| 2026-09-16T12:24:43Z | approved | Plan approved: `plan_status: approved`, `build_ready: true`, `approved_at` set. Planning content frozen; only the Builder-maintained front matter and §17 may change from here. | Explicit user approval ("approve") after the D4 amendment was committed in `b641e91` | User |

## 19. External references

None. All requirements derive from reviews 00007, 00008 and 00009, the user's decisions, and repository evidence at `5eb518c`. The GitHub runner labels named in REQ-06 are taken from review 00008's external reference (`actions/runner-images`, accessed 2026-09-09) and are to be re-verified by the Builder at STEP-06.

## 20. Confidence

**High.** Every requirement traces to a review finding, a user decision or a verified repository path at a clean baseline whose code is identical to the published `v2.0.0rc1`; the seven changes from plan 00006 each correspond to a specific review 00008 finding re-confirmed by 00009. The principal residual uncertainty is execution evidence the Builder and CI must produce: the Rust port's bit-exactness and long-input performance, the fifteen-plus-one wheel jobs on runners this repository has not yet used, and the negative-control run. D4 was a maintainer commitment the plan deliberately did not make; the user made it on 2026-09-16.
