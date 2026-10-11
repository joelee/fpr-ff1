---
title: "Delivery Plan 00011: Patch Release v2.1.1"
aliases:
  - "Plan 00011"
tags:
  - delivery-plan
  - release
  - claude-code
type: delivery-plan
plan_id: "PLAN-00011"
plan_status: approved
plan_kind: initial
created_at: "2026-10-11T12:00:14Z"
approved_at: "2026-10-11T12:47:36Z"
planner_agent: claude-code
planner_model: "anthropic/claude-fable-5-1"
triggered_by: user
request_kind: direct
repository: "joelee/fpr-ff1"
baseline_branch: "main"
baseline_commit: "43f2babb27411dfa67469ebf22b96638663f04aa"
source_ideas: []
source_reviews:
  - "docs/reviews/00015-V2_1_0rc2_Release_Review.md"
previous_plan: null
requirements_count: 6
steps_count: 6
acceptance_criteria_count: 12
blocking_decisions: 0
build_ready: true
web_research_used: false
confidence: high

# Builder-maintained front matter. Builder may update only these keys after
# explicit user approval; Delivery Planner initializes them.
implementation_status: not-started
builder_agent: null
builder_model: null
execution_branch: null
execution_started_at: null
execution_updated_at: null
execution_completed_at: null
current_step: null
---

# Delivery Plan 00011: Patch Release v2.1.1

> [!abstract] Plan status: `approved`
> `fpr-ff1` 2.1.1 on PyPI and crates.io from one tag, closing every observation the `2.1.0`
> release left in `docs/backlog.md`: trace-hook parity between the two cores, a `SECURITY.md`
> timing table from an order-robust measurement, a meaningful `cargo-semver-checks` step across
> pre-releases, and the `memoryview` open question pinned by a test. No change to accepted inputs,
> ciphertext or either public API. Approved; no blocking decision remains.

## 1. Objective and outcome

`2.1.0` shipped with four known loose ends, all recorded in `docs/backlog.md` under *Active Items*
and none affecting a user's ciphertext:

1. The Python per-round trace hook records `A_before` and `B_before`; the Rust `TraceRecord` does
   not, although the `encrypt_traced` fixture's docstring says both traces share one shape
   (review 00015 `REV-00015-LOW-01`, deferred by the owner at plan 00010 STEP-09).
2. `SECURITY.md`'s value-dependent timing row for radix 10, length 10 reads `+0.8%`, while the
   plan 00010 STEP-05 bench run printed `-28.6%` for the same row.
3. CI's `cargo-semver-checks` step compares nothing across pre-releases: at `2.1.0rc2` and again
   at `2.1.0` it reported "major change", 0 of 254 checks (plan 00010 work log).
4. Review 00015 open question 1 asked whether `bytes()` of a multi-byte-format `memoryview`
   escapes as a bare `TypeError`. Plan 00010 STEP-09 disproved the premise by execution, but no
   test pins the behaviour.

The outcome is a patch release, `2.1.1`, that resolves all four, published to both registries by
the existing `publish.yml` flow and verified there, with the backlog updated to match. The owner
chose to publish rather than leave the fixes unreleased on `main` (clarifying question 2,
2026-10-11), and to take all four items (clarifying question 1).

## 2. Source traceability

| Requirement | Source | Source location | Interpretation |
|---|---|---|---|
| PLAN-00011-REQ-01 | Review / Repository | `docs/reviews/00015-V2_1_0rc2_Release_Review.md` §`REV-00015-LOW-01`; `docs/backlog.md` *Trace-hook parity*; `src/fpr_ff1/_ff1.py:942-943`; `rust/fpr-ff1/src/engine.rs:380-394`, `:565-581`; `rust/fpr-ff1-rust/src/lib.rs:117-129`; `tests/conftest.py:63-104` | Both backends' traces carry the pre-swap halves under the same keys, and a dual-backend test reads them |
| PLAN-00011-REQ-02 | Repository / User | `docs/backlog.md` *Open observations*; `SECURITY.md:71-90`; `benchmarks/timing.py:92-103`; plan 00010 work log 2026-09-27T11:57:02Z (`-28.6%` under load 0.89/1.83/1.95); planner probe 2026-10-11 (`+0.5%` zero-first, `+1.0%` max-first) | The published table comes from a measurement that is not biased by case order, and says when and on what it was taken |
| PLAN-00011-REQ-03 | Repository / User | `docs/backlog.md` *Open observations*; `.github/workflows/ci.yml:216-229`; plan 00010 work log 2026-09-28T12:35:45Z ("0 checks: 0 pass, 254 skip"); `cargo semver-checks --help` (`--baseline-version`, `--release-type major|minor|patch`) | The crate API check runs real checks against the last stable release for every version, pre-releases included |
| PLAN-00011-REQ-04 | Review / User | `docs/reviews/00015-V2_1_0rc2_Release_Review.md` *Open questions* 1; plan 00010 work log 2026-09-27T23:44:04Z; `src/fpr_ff1/_ff1.py:116-130`; `tests/test_validation.py:203-233`; user's clarifying answer 1(d) | The accepted behaviour is pinned by a test on both backends; the guard is unchanged because the premise was false |
| PLAN-00011-REQ-05 | Repository | `AGENTS.md` *Conventions* (version lock-step, SemVer); `docs/developer-guide.md:238-249`; `CHANGELOG.md:10-45` (the `[2.1.0]` shape); `docs/AGENTS.md` *Rules* | Three manifests at `2.1.1`, both locks updated, a `[2.1.1]` changelog section, every touched document true in the same commit |
| PLAN-00011-REQ-06 | Repository / User | `docs/developer-guide.md:250-275`; `.github/workflows/publish.yml:60-70`, `:104-112`; plan 00010 STEP-11 (the release pattern); user's clarifying answer 2 | `2.1.1` public on PyPI and crates.io from tag `v2.1.1` on a `main` merge commit, verified, backlog closed |

## 3. Repository baseline

| Field | Value |
|---|---|
| Repository | `joelee/fpr-ff1` |
| Branch | `main` |
| HEAD | `43f2babb27411dfa67469ebf22b96638663f04aa` (merge of PR #23, the virtualenv audit fix) |
| Working tree at publication | Clean (`git status --porcelain=v1 --untracked-files=all` empty at 2026-10-11T12:00:14Z, before allocation) |
| Published versions | PyPI `fpr-ff1` 2.1.0; crates.io `fpr-ff1` 2.1.0 (`max_stable_version` 2.1.0); tag `v2.1.0` on `faa3e9e` |
| Applicable instructions | `AGENTS.md`; `CLAUDE.md`; `docs/AGENTS.md`; `docs/plans/AGENTS.md`; `.opencode/agents/DeliveryPlanner.md` |

## 4. Scope

### In scope

- `rust/fpr-ff1/src/engine.rs` `TraceRecord` and its one construction site; the
  `_test_encrypt_traced` binding in `rust/fpr-ff1-rust/src/lib.rs`; the `encrypt_traced` fixture
  docstring; one new dual-backend test in `tests/test_intermediates.py`.
- `benchmarks/timing.py` `value_dependent_table()` measurement order; the `SECURITY.md` timing
  table and its methodology sentence.
- The `crate-package` job's semver step in `.github/workflows/ci.yml`; one new pure script under
  `.github/scripts/`; one new test module for it; the matching paragraph in
  `docs/developer-guide.md`.
- One new test in `tests/test_validation.py` for a multi-byte-format `memoryview`.
- The version bump to `2.1.1` in the three manifests, `rust/Cargo.lock` and `uv.lock`;
  `CHANGELOG.md`; `docs/backlog.md`.
- The release: CI at the release commit, PR to `main`, tag, GitHub release, `publish.yml`,
  verification on both registries, closeout.

### Out of scope

- Any change to `_require_bytes` or to any validation rule, message or exception type: the
  premise of review 00015 open question 1 was disproved (D1).
- The README backend-comparison table and the GIL-probe figure: the harness change touches only
  `value_dependent_table()`, and the README table is not re-measured.
- Python 3.15 in the CI matrix, `no_std` for the crate, key zeroization: the owner assigned these
  to the next plan (clarifying answer 3).
- The `SECURITY.md` supported-versions table: the `2.1.x` row already covers `2.1.1`.
- A release candidate: a patch with no input, output or API change takes the `2.0.0` → `2.1.0`
  rc-free promotion path's final two steps only (D4).

## 5. Constraints and preserved decisions

- `AGENTS.md` *Never do* and *Implementation gotchas* apply in full. Neither core's arithmetic is
  touched; the only engine change is two added fields on a test-only struct, populated by clones
  at the existing trace push site, which the comment there already describes as "before the A/B
  swap, so the pre-swap a/b_side are captured here".
- `TraceRecord` is exported only through the hidden `internal` feature
  (`rust/fpr-ff1/src/lib.rs:39-42`), outside the crate's semver contract. Adding fields to it is
  not an API change; `cargo semver-checks --default-features` must still report no required bump.
- A change to one core is a change to both: the new dual-backend test runs on both backends
  through `encrypt_traced`, under `FPR_FF1_REQUIRE_RUST_BACKEND=1` in CI.
- `just quality` stays Rust-free. The new script test runs the script as a subprocess with
  `sys.executable`; it needs no network and no Rust.
- 100% line and branch coverage on `fpr_ff1` is unchanged: no source line in `src/fpr_ff1/` is
  added or removed by this plan.
- Version lock-step: `pyproject.toml`, `rust/fpr-ff1/Cargo.toml`, `rust/fpr-ff1-rust/Cargo.toml`
  at `2.1.1`; tag `v2.1.1`; `tests/test_contract.py` compares them.
- Release convention (plan 00010 STEP-11; memory `release-tags-on-main-via-pr`): the release
  branch merges into `main` by PR with a merge commit; the tag goes on that merge commit; the
  publish workflow runs from the tag. Pushes, tags and releases are owner actions or need the
  owner's recorded authorisation.
- Documentation changes in the same commit as the change that makes them true (`docs/AGENTS.md`).
- No new runtime dependency; no new dev dependency. The script uses the standard library only.

## 6. Assumptions

None. Unresolved matters are recorded as decisions and block approval when material.

## 7. Decisions and blockers

| ID | Decision or blocker | Resolution | Owner | Status |
|---|---|---|---|---|
| D1 | Item (d), the `memoryview` guard: the owner selected it as a guard change. Plan 00010 STEP-09 executed `bytes()` of a multi-byte-format (`array('i')`, `array('d')`) and a non-contiguous `memoryview` on CPython 3.12.13 and 3.14.3: it returns the raw bytes, `FF1` accepts a 16-byte view as a key and encrypts, nothing escapes `FF1Error`. The planner reproduced this on 3.12.13 on 2026-10-11 (`bytes(memoryview(array('i',[1,2,3])))` → 12 raw bytes; `FF1(key=memoryview(array('i',[1]*4)), radix=10)` constructs). | No guard change. REQ-04 pins the accepted behaviour with a test on both backends and closes the review's open question in the changelog and backlog. | Planner (evidence); owner may object at approval | Resolved |
| D2 | The `-28.6%` row: a defect in the implementation, in the harness, or in one measurement? The figure came from the one `just bench` run at plan 00010 STEP-05 (load average 0.89 1.83 1.95). The value table is the first thing the harness prints and radix 10 length 10 is its first case, so that measurement is the most exposed to CPU frequency ramp and competing load. Two planner runs on 2026-10-11, one in the harness's order and one with each pair reversed, gave `+0.5%` and `+1.0%` for that row and agreed within 0.5 points on every row. | Treat it as first-case bias in the harness, not an implementation effect. REQ-02 makes the harness measure each pair in both orders after an untimed warm-up, and republishes the table from a run whose conditions are recorded. | Planner (evidence) | Resolved |
| D3 | How the semver step chooses its baseline and release type. Deriving the type from the version alone is what makes a pre-release vacuous, and letting the tool pick "the latest version" can select the previous rc. | Pass both explicitly: `--baseline-version` is crates.io's `max_stable_version` for the crate (the JSON the step already fetches), and `--release-type` is computed by a pure script from the crate's manifest version and that baseline: the pre-release suffix is dropped; a major difference is `major`, a minor difference `minor`, otherwise `patch` (equal versions are `patch`, so an API change on `main` after a release fails until the version is bumped); a manifest version below the baseline fails the step. The 404 skip for an unpublished crate stays. | Planner | Resolved |
| D4 | Release path for a patch: rc or direct? | Direct, per the owner's answer to clarifying question 2. Branch `release/v2.1.1` from `main`; one CI run at the release commit; PR with a merge commit; tag `v2.1.1`; GitHub release (not pre-release). | Owner (2026-10-11) | Resolved |
| D5 | Does the new trace test assert against NIST data? `tests/vectors/nist_ff1_intermediates.json` publishes `P, Q, R, S, y, m, c, C` per round and no `A`/`B`. | The test asserts the spec's own chaining rule (Algorithm 7 steps 6.viii and 6.ix) rather than a fixture: round 0's halves are the input split at `u`; each later round's `A_before` is the previous round's `B_before` and its `B_before` the previous round's `C`; the ciphertext is the last round's `B_before` followed by its `C`. That is specified behaviour, not current behaviour, and it holds on every NIST vector on both backends. Never regenerate or extend the NIST fixture. | Planner | Resolved |

## 8. Affected architecture and components

No boundary moves. The Python package, the PyO3 binding and the crate keep their public APIs.

| Component | Path | Change |
|---|---|---|
| Rust trace record | `rust/fpr-ff1/src/engine.rs` (`TraceRecord`, the `trace.push` in `ff1_impl`) | Two fields, `a_before: Vec<u16>` and `b_before: Vec<u16>`, cloned from `a` and `b_side` at the existing push site |
| PyO3 test binding | `rust/fpr-ff1-rust/src/lib.rs` (`_test_encrypt_traced`) | Emit `A_before` and `B_before` |
| Test fixture | `tests/conftest.py` (`encrypt_traced`) | Docstring states the shared shape truthfully; normalisation unchanged (the new fields are already `list[int]`-shaped: pyo3 maps `Vec<u16>` to a list) |
| Intermediate tests | `tests/test_intermediates.py` | One new dual-backend test: key set and A/B chaining |
| Validation tests | `tests/test_validation.py` | One new dual-backend test: multi-byte-format `memoryview` accepted as its raw bytes |
| Bench harness | `benchmarks/timing.py` (`value_dependent_table`) | Warm-up and both-orders measurement |
| Security policy | `SECURITY.md` (timing section) | Methodology sentence and table from the new run, with date, interpreter and hardware |
| CI | `.github/workflows/ci.yml` (`crate-package`, *API compatibility* step) | Explicit baseline and release type |
| CI script | `.github/scripts/semver_release_type.py` (new) | Pure version arithmetic, stdlib only |
| Script test | `tests/test_ci_scripts.py` (new) | Subprocess cases for the script |
| Developer guide | `docs/developer-guide.md` (*The Rust crate*) | Describe the semver step |
| Versions | `pyproject.toml`, `rust/fpr-ff1/Cargo.toml`, `rust/fpr-ff1-rust/Cargo.toml`, `rust/Cargo.lock`, `uv.lock` | `2.1.1` |
| Changelog, backlog | `CHANGELOG.md`, `docs/backlog.md` | `[2.1.1]` section; observations moved to *Completed Items* |

## 9. Requirement catalogue

### PLAN-00011-REQ-01 — Trace-hook parity across both backends

- **Requirement:** The Rust `TraceRecord` carries the pre-swap halves, and the
  `_test_encrypt_traced` binding emits them as `A_before` and `B_before`, so that a record from
  either backend, after the fixture's normalisation, has exactly the key set
  `{i, u, v, b, d, P, Q, R, S, y, m, c, C, A_before, B_before}`. A test in
  `tests/test_intermediates.py`, parameterised over both backends through `encrypt_traced` and
  over all nine NIST vectors, asserts that key set and the chaining rule of D5. The
  `encrypt_traced` docstring describes the shape accurately.
- **Rationale:** The dual-backend contract is that each assertion runs unchanged against both
  backends; a field present on one side only is a latent `KeyError` for the next author.
- **Source:** `REV-00015-LOW-01`; `docs/backlog.md` *Trace-hook parity*.
- **Acceptance evidence:** The new test fails on the rust backend before the engine change (a
  `KeyError` on `A_before`) and passes on both afterwards; the full dual-backend gate passes;
  `just rust-lint`, `just crate-test` and `just crate-msrv` pass.

### PLAN-00011-REQ-02 — An order-robust timing table in SECURITY.md

- **Requirement:** `value_dependent_table()` performs an untimed warm-up of at least 0.5 s of
  encrypt calls before its first timed measurement, and times every `(radix, length)` pair in
  both orders (all-zero then all-max, then all-max then all-zero), reporting the mean of the two
  deltas. `SECURITY.md`'s methodology sentence describes that procedure, and its table is
  replaced by the output of one run of `just bench` whose date, load average, CPU, interpreter
  and raw output are in the work log. The table's caption states the run date and interpreter.
- **Rationale:** The published figure is a falsifiable empirical claim; a single first-case
  measurement under load falsified it once, which is a harness weakness rather than a cipher
  property.
- **Source:** `docs/backlog.md` *Open observations*; plan 00010 work log
  2026-09-27T11:57:02Z; D2.
- **Acceptance evidence:** Running the harness twice, once as shipped and once with
  `_VALUE_CASES` reversed, yields deltas within 2 percentage points of each other on every row
  (recorded in the work log). `SECURITY.md` and the harness docstring agree on the method.

### PLAN-00011-REQ-03 — A meaningful crate API check across pre-releases

- **Requirement:** The `crate-package` job's semver step passes
  `--baseline-version <max_stable_version>` and `--release-type <type>` to
  `cargo semver-checks`, where `<type>` is printed by `.github/scripts/semver_release_type.py`
  given the crate's manifest version and the baseline, under the rules of D3. The script has no
  dependencies beyond the standard library and no network access. `tests/test_ci_scripts.py`
  runs it as a subprocess for at least: `2.1.1`/`2.1.0` → `patch`; `2.1.0`/`2.1.0` → `patch`;
  `2.2.0-rc1`/`2.1.0` → `minor`; `2.2.0-rc2`/`2.1.0` → `minor`; `3.0.0-rc1`/`2.1.0` → `major`;
  `2.0.9`/`2.1.0` → non-zero exit with a message naming both versions. The 404 skip remains.
  `docs/developer-guide.md` describes the step.
- **Rationale:** At `2.1.0rc2` and at `2.1.0` the step ran 0 of 254 checks; a check that cannot
  fail is not a gate.
- **Source:** `docs/backlog.md` *Open observations*; plan 00010 work log 2026-09-28T12:35:45Z;
  D3.
- **Acceptance evidence:** The CI run at STEP-04 shows the step comparing against `2.1.0` with
  release type `patch` and a non-zero count of checks run; the script test passes under
  `just quality`.

### PLAN-00011-REQ-04 — The multi-byte-format memoryview behaviour is pinned

- **Requirement:** A test in `tests/test_validation.py`, run through `ff1_factory` on both
  backends, constructs an `FF1` with a key given as `memoryview(array('i', ...))` of 16 bytes and
  a tweak given as a multi-byte-format view, and asserts that the ciphertext equals that of the
  same instance built from `view.tobytes()` for each. No change to `_require_bytes`.
- **Rationale:** The review's open question was answered by execution but not by a test; the
  contract test suite is where the answer belongs, so a future CPython change surfaces here.
- **Source:** Review 00015 *Open questions* 1; plan 00010 work log 2026-09-27T23:44:04Z; D1.
- **Acceptance evidence:** The test passes on both backends; coverage stays at 100% with no
  source change.

### PLAN-00011-REQ-05 — Version 2.1.1 in lock-step, with its documentation

- **Requirement:** The three manifests at `2.1.1`; `rust/Cargo.lock` and `uv.lock` updated; a
  `[2.1.1] — <date>` section in `CHANGELOG.md` with a compare link, listing: the trace-hook parity
  (test-only), the timing-table re-measurement and harness change, the semver step, the pinned
  `memoryview` behaviour, and the `virtualenv` audit fix already on `main` (PR #23); stating "no
  change to accepted inputs, ciphertext or either public API". `docs/backlog.md` moves the
  trace-hook item and the two open observations to *Completed Items*.
- **Rationale:** `AGENTS.md` *Conventions*; `docs/AGENTS.md`.
- **Source:** `AGENTS.md`; `docs/developer-guide.md:238-249`.
- **Acceptance evidence:** `tests/test_contract.py` passes; the local gates of STEP-05 pass; CI
  is green at the release commit.

### PLAN-00011-REQ-06 — 2.1.1 published and verified on both registries

- **Requirement:** Tag `v2.1.1` on the `main` merge commit of the release PR; a GitHub release;
  `publish.yml` publishes PyPI then crates.io by Trusted Publishing. The Builder verifies: PyPI
  file digests equal the run's artifacts, attestations present, `pip install fpr-ff1` resolves to
  `2.1.1` with no pin; crates.io checksum equal to the run's `crate` artifact, Trusted Publishing
  data present, `cargo add fpr-ff1` resolves to `2.1.1`; docs.rs builds; a NIST sample and a
  `d > 16` case reproduce the `2.1.0` ciphertext from a clean install of each backend.
- **Rationale:** The two registries always hold the same release; a defective release is yanked
  and followed by `2.1.2`, never replaced.
- **Source:** `docs/developer-guide.md:250-275`; plan 00010 STEP-11.
- **Acceptance evidence:** The verification table in the work log, with the publish run URL.

## 10. Delivery strategy

Four independent fixes, then the release. STEP-01 to STEP-04 are mutually independent and each
is one revertible commit, so a ciphertext question can bisect to a single change (there is none
expected: no arithmetic changes). STEP-01 is first because it is the only change to the Rust
core and the only one that needs `just backend-dev` before the dual gate; STEP-04 is last of the
four because its CI evidence (a semver comparison against `2.1.0` with real checks) needs a push
of the branch, which the owner authorises once for the whole branch at STEP-05 if not earlier.

Every code step is test-first: the trace test fails on the rust backend before the engine
change; the script test is written before the script; the harness is run in both orders before
and after its change. STEP-05 is the release commit and the single full-gate checkpoint; STEP-06
is owner actions with Builder verification, exactly as plan 00010 STEP-11 ran for `2.1.0`.

## 11. Detailed implementation steps

### PLAN-00011-STEP-01 — Trace-hook parity

- **Status placeholder:** `not-started`
- **Objective:** Both backends' traces share one shape, and a test proves it on every NIST vector.
- **Requirements:** `PLAN-00011-REQ-01`
- **Depends on:** None
- **Affected components:** `rust/fpr-ff1/src/engine.rs` (`TraceRecord`, `ff1_impl` trace push);
  `rust/fpr-ff1-rust/src/lib.rs` (`_test_encrypt_traced`); `tests/conftest.py`
  (`encrypt_traced` docstring); `tests/test_intermediates.py`
- **Preconditions:** Branch `release/v2.1.1` created from `main` at `43f2bab` or later; the
  worktree clean; `just backend-dev` builds the extension at the baseline.
- **Test or evidence first:** Add `test_trace_shape_and_chaining` to `tests/test_intermediates.py`,
  parameterised over `_VECTORS` and using `ff1_factory` and `encrypt_traced`. It asserts, for the
  trace of each vector: the key set of every record equals the fixed expected set; round 0's
  `A_before` and `B_before` are the plaintext numerals split at `u`; for `i` in 1..9, record `i`'s
  `A_before` equals record `i-1`'s `B_before` and its `B_before` equals record `i-1`'s `C`; the
  returned ciphertext equals record 9's `B_before` followed by record 9's `C`. Run it with
  `FPR_FF1_REQUIRE_RUST_BACKEND=1`: it must pass on `python` and fail on `rust` with a `KeyError`
  for `A_before`. Record both outcomes.
- **Implementation tasks:**
  1. In `engine.rs`, add `pub a_before: Vec<u16>` and `pub b_before: Vec<u16>` to `TraceRecord`
     with a doc comment naming Algorithm 7 steps 6.viii and 6.ix, and populate them at the
     existing push site with `a.clone()` and `b_side.clone()`. Change nothing else in `ff1_impl`.
  2. In `lib.rs`, add `dict.set_item("A_before", rec.a_before)?` and the `B_before` equivalent.
  3. In `conftest.py`, make the `encrypt_traced` docstring state the shared key set and that
     `A_before`/`B_before` need no normalisation.
  4. `just backend-dev`; run the new test on both backends; run `just rust-lint`,
     `just crate-test`, `just crate-msrv`.
- **Documentation/configuration/operations:** The fixture docstring (task 3). No user-facing
  document changes: the hook is test-only and never exported.
- **Verification:**
  `FPR_FF1_REQUIRE_RUST_BACKEND=1 uv run pytest tests/test_intermediates.py -q` passes with the
  rust parameterisation present; `just rust-lint`; `just crate-test`; `just crate-msrv`.
- **Completion criteria:** One commit; the new test passes on both backends; the three Rust gates
  pass; `cargo clippy --all-targets -- -D warnings` reports no dead-code warning for the new
  fields (the existing `cfg_attr(..., allow(dead_code))` on the struct covers them).
- **Rollback or recovery:** Revert the commit; no artifact or document depends on it.
- **Builder stop conditions:** The new test fails on the `python` backend before any engine change
  (the chaining rule is then wrong, not the port); any change needed outside the trace push site
  or `TraceRecord`; any ciphertext difference in the existing intermediate or vector tests.

### PLAN-00011-STEP-02 — Pin the multi-byte-format memoryview behaviour

- **Status placeholder:** `not-started`
- **Objective:** Review 00015 open question 1 is answered by a test rather than a work-log entry.
- **Requirements:** `PLAN-00011-REQ-04`
- **Depends on:** None
- **Affected components:** `tests/test_validation.py`
- **Preconditions:** STEP-01 committed (for a linear, bisectable history), worktree clean.
- **Test or evidence first:** This step is a test.
- **Implementation tasks:**
  1. Next to `test_live_memoryview_is_still_accepted`, add
     `test_multibyte_format_memoryview_is_accepted_as_raw_bytes` using `ff1_factory`: a key
     `memoryview(array('i', [1, 2, 3, 4]))` (16 bytes on CPython's 4-byte `int`; assert
     `view.nbytes == 16` first so the test is explicit about its assumption) and a tweak
     `memoryview(array('h', [7, 8]))`; assert `encrypt_numerals` of a valid input equals that of
     the instance built from `.tobytes()` of each view.
  2. Add nothing to `_require_bytes`; if the test fails on either backend, stop (see below).
- **Documentation/configuration/operations:** None beyond the changelog line at STEP-05.
- **Verification:** `uv run pytest tests/test_validation.py -q` on both backends
  (`FPR_FF1_REQUIRE_RUST_BACKEND=1`); `just quality` still reports 100% coverage.
- **Completion criteria:** One commit; the test passes on both backends.
- **Rollback or recovery:** Revert the commit.
- **Builder stop conditions:** The test fails: that would mean CPython behaviour differs from the
  plan 00010 evidence, and the guard question reopens for the owner rather than being decided in
  a patch.

### PLAN-00011-STEP-03 — Order-robust timing harness and a fresh SECURITY.md table

- **Status placeholder:** `not-started`
- **Objective:** The published value-dependent table is reproducible to within noise regardless
  of case order, and says how it was measured.
- **Requirements:** `PLAN-00011-REQ-02`
- **Depends on:** None
- **Affected components:** `benchmarks/timing.py` (`value_dependent_table`, module docstring);
  `SECURITY.md` (timing section, item 1)
- **Preconditions:** STEP-02 committed; worktree clean; a quiet machine (record the load
  average from `uptime` before the final run).
- **Test or evidence first:** Run the harness's value table as shipped, then again with
  `_VALUE_CASES` reversed (a scratch script, not a repository change), and record both outputs
  with the load average. This is the before picture.
- **Implementation tasks:**
  1. In `value_dependent_table()`: before the loop, an untimed warm-up calling
     `encrypt_numerals` on the first case for at least 0.5 s; inside the loop, measure
     `t_zero, t_max` then `t_max2, t_zero2` and print the mean of the two deltas. Update the
     module docstring's methodology paragraph to match.
  2. Re-run the two-order evidence of the step above against the changed harness; every row must
     agree within 2 percentage points between orders.
  3. `just bench` once on the quiet machine; paste the value table into `SECURITY.md` item 1,
     update its sentence "Measured on CPython 3.12 (median of 25 batches, all-zero vs all-max
     plaintext)" to describe both-order measurement and name the run date, and keep the
     "re-run it on your own interpreter and hardware" guidance. Leave the README backend table
     untouched.
- **Documentation/configuration/operations:** `SECURITY.md` (task 3). The full raw bench output,
  CPU model, interpreter, load average and UTC time go in the work log.
- **Verification:** The two-order agreement in task 2, recorded; `just quality` (the harness is
  linted and type-checked with the rest of the tree); `uv run pytest tests/test_docs.py -q`.
- **Completion criteria:** One commit containing the harness change and the table it produced.
- **Rollback or recovery:** Revert the commit; the previous table was itself a measured claim.
- **Builder stop conditions:** The two orders disagree by more than 2 points on any row after the
  change (the bias is not first-case bias and the owner decides the next move); any row's
  magnitude exceeds 5% (a possible implementation effect, to be reported, not papered over).

### PLAN-00011-STEP-04 — A real semver gate across pre-releases

- **Status placeholder:** `not-started`
- **Objective:** `cargo semver-checks` compares every version, release candidates included,
  against the last stable crate with the right release type.
- **Requirements:** `PLAN-00011-REQ-03`
- **Depends on:** None (push authorisation for CI evidence; see task 5)
- **Affected components:** `.github/scripts/semver_release_type.py` (new);
  `tests/test_ci_scripts.py` (new); `.github/workflows/ci.yml` (`crate-package`, the *API
  compatibility with the last published version* step); `docs/developer-guide.md` (*The Rust
  crate*)
- **Preconditions:** STEP-03 committed; worktree clean.
- **Test or evidence first:** Write `tests/test_ci_scripts.py` first: a parametrised test that
  runs `[sys.executable, ".github/scripts/semver_release_type.py", current, baseline]` from the
  repository root (`pathlib.Path(__file__).parents[1]`) with `subprocess.run(capture_output=True,
  text=True, check=False)` and asserts stdout and exit code for the six cases in REQ-03. It fails
  (file not found) until the script exists.
- **Implementation tasks:**
  1. The script: a module docstring in the style of `assert_crate_contents.py`; parse each
     version with a strict regex `^(\d+)\.(\d+)\.(\d+)(?:-([0-9A-Za-z.-]+))?$`; drop the
     pre-release part of the current version; compare majors, then minors, else `patch`; a
     current below the baseline writes a message naming both to stderr and exits 1; print the
     type alone on stdout. Standard library only; no network.
  2. `ci.yml`: in the existing step, extract `max_stable_version` from the already-fetched JSON
     with `python3 -c 'import json,sys; ...'` (fetch the body once, not twice; keep the 404 skip
     on the status code), read the crate version from `rust/fpr-ff1/Cargo.toml` with the same
     `grep -m1 '^version = '` used in `publish.yml`, run the script, then
     `cargo semver-checks -p fpr-ff1 --manifest-path rust/Cargo.toml --default-features
     --baseline-version "$baseline" --release-type "$type"`. Keep the pinned
     `cargo-semver-checks` version `0.50.0`.
  3. `docs/developer-guide.md` *The Rust crate*: one or two sentences on the explicit baseline
     and release type and why (pre-releases were compared with 0 checks at `2.1.0`).
  4. `just quality` (the script and its test are in the tree the gate formats, lints and
     type-checks).
  5. CI evidence: with the owner's push authorisation, push `release/v2.1.1` and dispatch or let
     `ci.yml` run. The semver step's log must show `--baseline-version 2.1.0`, release type
     `patch` (the manifest is still `2.1.0` at this point) and a non-zero number of checks run and
     passed. Record the run URL and the step's summary line.
- **Documentation/configuration/operations:** `docs/developer-guide.md` (task 3).
- **Verification:** `uv run pytest tests/test_ci_scripts.py -q`; `just quality`; the CI run of
  task 5.
- **Completion criteria:** One commit; the script test passes; the CI semver step ran real checks
  against `2.1.0`.
- **Rollback or recovery:** Revert the commit; the step returns to its vacuous but green form.
- **Builder stop conditions:** `cargo semver-checks` reports a required bump (an API change would
  have slipped into `main` since `2.1.0`; report, do not bump); the flag names differ on 0.50.0
  from the planner's `--help` reading; no push authorisation by the time STEP-05 needs it.

### PLAN-00011-STEP-05 — Bump to 2.1.1; the release commit is green

- **Status placeholder:** `not-started`
- **Objective:** A release commit at `2.1.1` with CI green on every job.
- **Requirements:** `PLAN-00011-REQ-05`
- **Depends on:** STEP-01, STEP-02, STEP-03, STEP-04
- **Affected components:** `pyproject.toml`; `rust/fpr-ff1/Cargo.toml`;
  `rust/fpr-ff1-rust/Cargo.toml`; `rust/Cargo.lock`; `uv.lock`; `CHANGELOG.md`; `docs/backlog.md`
- **Preconditions:** STEP-01 to STEP-04 committed on `release/v2.1.1`; worktree clean.
- **Test or evidence first:** `tests/test_contract.py` (lock-step and required files).
- **Implementation tasks:**
  1. The three manifests at `2.1.1`; `cargo update -w --manifest-path rust/Cargo.toml` (workspace
     members only) and `uv lock` so both locks carry `2.1.1`; confirm with `git diff` that no
     other dependency moved.
  2. `CHANGELOG.md`: `## [2.1.1] — <UTC date>` under `[Unreleased]`, with a compare link
     `v2.1.0...v2.1.1` in the style of the `[2.1.0]` entry; *Changed* (timing table and harness;
     semver step; `virtualenv` 21.14.6 in the dev lock, PR #23) and *Fixed* (trace-hook parity,
     test-only; review 00015 open question 1 closed by test), and the sentence "No change to
     accepted inputs, ciphertext or either public API; the pure-Python path and the compiled
     backend remain bit-identical."
  3. `docs/backlog.md`: the *Trace-hook parity* item and the *Open observations* item leave
     *Active Items*; a `2.1.1` entry at the top of *Completed Items* summarises the four
     resolutions with this plan's number. The *Ongoing* items that remain (Rev. 1 tracking,
     `requires-python` floor, `no_std` and zeroization) stay.
  4. Local gates, in this order, all recorded with the commit hash they ran at:
     - `FPR_FF1_REQUIRE_RUST_BACKEND=1 FPR_FF1_REQUIRE_ORACLE=1 uv run pytest --cov=fpr_ff1
       --cov-report=term-missing --cov-fail-under=100` (after `just backend-dev`);
     - `just quality` (Rust-free);
     - `just rust-lint`, `just crate-test`, `just crate-msrv`, `just crate-package`;
     - `uv run pytest tests/test_contract.py tests/test_docs.py -q`.
  5. **Owner authorisation:** push `release/v2.1.1`; the Builder records the `ci.yml` run and
     waits for it. The semver step must report release type `patch` against `2.1.0` with checks
     run and no required bump.
- **Documentation/configuration/operations:** Changelog, backlog (tasks 2 and 3).
- **Verification:** CI green on every job at the release commit; the semver step's summary line
  recorded.
- **Completion criteria:** One release commit; a green run at it.
- **Rollback or recovery:** Fix forward on the branch; nothing is published yet.
- **Builder stop conditions:** Any red job; the semver step reporting a required bump; a
  dependency other than the two `fpr-ff1` packages moving in either lock; no push authorisation.

### PLAN-00011-STEP-06 — Owner releases 2.1.1; Builder verifies; plan closes

- **Status placeholder:** `not-started`
- **Objective:** `2.1.1` on both registries by CI, verified; the plan closed.
- **Requirements:** `PLAN-00011-REQ-06`
- **Depends on:** STEP-05
- **Affected components:** None by the Builder except this plan's work log and the closeout
  change to `docs/backlog.md` if STEP-05's entry needs the publish-run facts
- **Preconditions:** STEP-05 green; `origin/release/v2.1.1` at the gated commit.
- **Test or evidence first:** This step is the evidence.
- **Implementation tasks:**
  1. **Owner:** PR `release/v2.1.1` into `main`, merged with a merge commit; tag exactly `v2.1.1`
     on that merge commit (annotated); publish a GitHub release (not a pre-release) whose notes
     are the `[2.1.1]` changelog section. The Builder may perform the tag and release only on the
     owner's explicit, recorded authorisation, as at plan 00010 STEP-11.
  2. **CI:** `publish.yml` on the tag: the reused gate, PyPI, then `publish-crate`.
  3. **Builder:** the REQ-06 verification table: PyPI files and digests against the run's
     artifacts, attestations, `uv pip install fpr-ff1` (no pin, no `--pre`) resolving to `2.1.1`
     on 3.12 and 3.14 with both backends importable from the wheel and the sdist installing
     pure-Python; crates.io checksum equal to the run's `crate` artifact and `trustpub_data`
     present; docs.rs built; `cargo add fpr-ff1` writing `2.1.1`; a NIST sample and a `d > 16`
     case reproducing the `2.1.0` ciphertext.
  4. **Builder:** close the plan in the work log (completion summary, `implementation_status:
     completed`). If `docs/backlog.md` needs the publish-run facts, a closeout commit by PR, as
     for plan 00010 (`chore/plan-00011-closeout`).
- **Documentation/configuration/operations:** Work log; backlog closeout if needed.
- **Verification:** Task 3 in full.
- **Completion criteria:** `2.1.1` public and verified on both registries; the plan closed.
- **Rollback or recovery:** A defective release is yanked if harmful and fixed in `2.1.2`, never
  overwritten.
- **Builder stop conditions:** A digest mismatch; `publish-crate` failing after PyPI published
  (the manual `.crate` path in `docs/developer-guide.md` is then the owner's call); any
  ciphertext difference from `2.1.0` in task 3.

## 12. Cross-cutting concerns

| Area | Applicability | Planned action or reason not applicable | Step or requirement |
|---|---|---|---|
| Compatibility and APIs | Applicable | No public API, input or output change. `TraceRecord` is behind the hidden `internal` feature; the semver step itself verifies the crate against `2.1.0` with `patch` | REQ-01, REQ-03, STEP-05 |
| Data and migration | Not applicable | No persisted data; pickles unchanged | — |
| Security and privacy | Applicable | `SECURITY.md` keeps every disclaimer; the timing claim becomes better-measured, not stronger; no zeroization or FIPS claim is added | REQ-02, STEP-03 |
| Performance and scale | Applicable | Two `Vec<u16>` clones per round in the traced core only; the untraced production path is unchanged (same `ff1_impl`, `trace` is `None`). The README backend table is not re-measured | STEP-01 |
| Reliability and failure handling | Applicable | The semver step fails on a stale or regressed version instead of passing vacuously; the 404 skip stays for a fresh crate | REQ-03 |
| Observability and operations | Not applicable | No runtime component | — |
| Dependencies and supply chain | Applicable | No new dependency; the pinned `cargo-semver-checks` 0.50.0 and all action SHAs unchanged; the dev lock's `virtualenv` fix is already on `main` and is only recorded in the changelog | STEP-04, STEP-05 |
| Accessibility and UX | Not applicable | No user interface; the `SECURITY.md` table keeps its header row | — |
| Documentation and release | Applicable | Changelog, backlog, developer guide, `SECURITY.md`, fixture docstring, in the commits that make them true | REQ-02, REQ-03, REQ-05 |
| Deployment and rollback | Applicable | Registry versions are immutable: `2.1.2`, never an overwrite | STEP-06 |

## 13. Verification strategy

| Level | Evidence or command | When | Required result |
|---|---|---|---|
| Unit, Rust | `just rust-lint`; `just crate-test`; `just crate-msrv` | STEP-01, STEP-05 | Pass |
| Dual-backend conformance | `FPR_FF1_REQUIRE_RUST_BACKEND=1 FPR_FF1_REQUIRE_ORACLE=1 uv run pytest --cov=fpr_ff1 --cov-report=term-missing --cov-fail-under=100` | STEP-01 (intermediates module), STEP-05 (full) | Pass, 100% line and branch |
| Rust-free gate | `just quality` | STEP-02, STEP-03, STEP-04, STEP-05 | Pass |
| Script | `uv run pytest tests/test_ci_scripts.py -q` | STEP-04 | Six cases pass |
| Harness reproducibility | Two orders of `value_dependent_table()`, recorded | STEP-03 | Every row within 2 percentage points |
| Crate packaging | `just crate-package` | STEP-05 | Docs, contents and dry run pass |
| CI | `ci.yml` at the release commit | STEP-04 (semver evidence), STEP-05 | All jobs green; semver step: baseline `2.1.0`, `patch`, checks run, no bump required |
| Release | `publish.yml` on `v2.1.1`; registry checks of REQ-06 | STEP-06 | Both registries verified |

## 14. Acceptance criteria

- [ ] `PLAN-00011-AC-01` A trace record from either backend, after `encrypt_traced`, has exactly
      the keys `i, u, v, b, d, P, Q, R, S, y, m, c, C, A_before, B_before`, asserted by a test
      that runs on both backends for all nine NIST vectors.
- [ ] `PLAN-00011-AC-02` The same test asserts the Algorithm 7 chaining rule of D5 and the
      ciphertext reconstruction from round 9, and it fails on the rust backend at the baseline
      (recorded) before passing after STEP-01.
- [ ] `PLAN-00011-AC-03` The `encrypt_traced` docstring describes the shared key set truthfully.
- [ ] `PLAN-00011-AC-04` `value_dependent_table()` warms up untimed and measures each pair in both
      orders; two runs with opposite case orders agree within 2 percentage points on every row.
- [ ] `PLAN-00011-AC-05` `SECURITY.md`'s timing table and methodology sentence are from and
      describe one recorded run (date, interpreter, CPU, load average in the work log).
- [ ] `PLAN-00011-AC-06` `.github/scripts/semver_release_type.py` passes the six cases of REQ-03
      in `tests/test_ci_scripts.py` under `just quality`, with no non-stdlib import.
- [ ] `PLAN-00011-AC-07` The `crate-package` semver step at the release commit logs
      `--baseline-version 2.1.0` and `--release-type patch`, runs a non-zero number of checks,
      and requires no bump.
- [ ] `PLAN-00011-AC-08` A multi-byte-format `memoryview` key and tweak produce the ciphertext of
      their `.tobytes()` equivalents on both backends, by a test, with `_require_bytes` unchanged.
- [ ] `PLAN-00011-AC-09` `pyproject.toml`, both `Cargo.toml` manifests, `rust/Cargo.lock` and
      `uv.lock` carry `2.1.1`, and no other locked dependency moved in the release commit.
- [ ] `PLAN-00011-AC-10` `CHANGELOG.md` has a `[2.1.1]` section with the five items of REQ-05 and
      the no-change statement; `docs/backlog.md` lists the resolutions under *Completed Items*.
- [ ] `PLAN-00011-AC-11` CI is green on every job at the release commit, and the full
      dual-backend gate passed locally at that commit with 100% coverage.
- [ ] `PLAN-00011-AC-12` `fpr-ff1` 2.1.1 is on PyPI and crates.io from tag `v2.1.1` on a `main`
      merge commit, with the REQ-06 verification table complete in the work log.

## 15. Risks and mitigations

| Risk | Likelihood | Impact | Mitigation or test | Owner/step |
|---|---|---|---|---|
| The chaining test is wrong rather than the Rust port | Low | Step blocked | It must pass on the `python` backend before any engine change; a `python` failure is a stop condition | STEP-01 |
| The harness still shows order bias after the change | Low | Table not publishable | The 2-point criterion is measured before publishing; a miss is a stop condition for the owner | STEP-03 |
| A real value-dependent effect larger than noise | Very low | A `SECURITY.md` claim weakens | Any row over 5% is reported, not smoothed; the planner's two runs today were under 3% on every row | STEP-03 |
| `cargo-semver-checks` 0.50.0 flag names differ from the planner's `--help` | Low | CI step fails | Verified against the locally installed binary's help; the first CI run at STEP-04 is the proof, and the step is revertible | STEP-04 |
| An API change slipped into `main` since `2.1.0` and the real check now fails | Very low | Release blocked | That is the gate working; stop and report rather than bump | STEP-04 |
| The 16-byte `array('i')` assumption varies by platform | Very low | Test flaky on one leg | The test asserts `view.nbytes == 16` and uses `tobytes()` as its oracle; CPython's `int` is 4 bytes on all three CI platforms | STEP-02 |
| `publish-crate` fails after PyPI published | Low | Registries diverge | The documented manual `.crate` path in `docs/developer-guide.md` | STEP-06 |
| A lock update moves an unrelated dependency | Low | Unreviewed change in a release | `git diff` on both locks; a moved dependency is a stop condition | STEP-05 |

## 16. Builder hand-off

- **Start condition:** User approval and a clean repository.
- **First step:** `PLAN-00011-STEP-01` on a new branch `release/v2.1.1` from `main`.
- **Required sequence:** STEP-01 → STEP-02 → STEP-03 → STEP-04 → STEP-05 → STEP-06, one commit
  per step for STEP-01 to STEP-05.
- **Parallel-safe work:** STEP-01 to STEP-04 are independent in content, but commit them in
  order to keep the history bisectable; STEP-04's CI evidence may be gathered at the STEP-05
  push if the owner prefers one push.
- **Do not change:** approved scope, requirements, steps, acceptance criteria, or content outside
  Builder's permitted work-log area. Do not touch `_require_bytes`, any validation rule, any
  fixture under `tests/vectors/`, or the README backend table.
- **Escalate when:** any stop condition fires; a push, tag or release needs authorisation; the
  semver step reports a required bump; a timing row exceeds 5% or the two orders disagree by
  more than 2 points.
- **Completion hand-off:** The REQ-06 verification table, the publish run URL, the `main` merge
  commit and tag, and the closed work log.

<!-- BUILDER_WORK_LOG_START -->
## 17. Builder Work Log

> [!warning] Builder-maintained section
> Delivery Planner creates this section. After approval, Builder may update only
> this delimited section and the Builder-maintained front-matter fields. Builder
> must preserve prior entries and use UTC timestamps.

### Step status

| Step | Status | Started (UTC) | Completed (UTC) | Evidence | Builder notes |
|---|---|---|---|---|---|
| PLAN-00011-STEP-01 | not-started | — | — | — | — |
| PLAN-00011-STEP-02 | not-started | — | — | — | — |
| PLAN-00011-STEP-03 | not-started | — | — | — | — |
| PLAN-00011-STEP-04 | not-started | — | — | — | — |
| PLAN-00011-STEP-05 | not-started | — | — | — | — |
| PLAN-00011-STEP-06 | not-started | — | — | — | — |

Allowed status values: `not-started`, `in-progress`, `blocked`, `completed`,
`skipped`. A skipped step requires explicit user approval recorded in Evidence.

### Execution log

| Timestamp (UTC) | Step | Event | Evidence or reference | Next action |
|---|---|---|---|---|

### Deviations and blockers

| Timestamp (UTC) | Step | Deviation or blocker | Impact | Decision required from |
|---|---|---|---|---|

None

### Verification results

| Timestamp (UTC) | Step | Command or check | Result | Evidence |
|---|---|---|---|---|

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
| 2026-10-11T12:00:14Z | draft | Initial draft | User request to plan `v2.1.1` from the remaining backlog; scope fixed by the four clarifying answers of 2026-10-11 | User |
| 2026-10-11T12:47:36Z | approved | Approved; no planning content changed. The owner committed the draft as `6624c75` ("v2.1.1 release plan.") on `release/v2.1`; this approval commit is on `release/v2.1.1`, branched from it | User: "Plan 00011 approved and committed. Please begin build" | User |

## 19. External references

None. The `cargo semver-checks` flags were read from the locally installed binary's `--help`;
the crates.io version fields from the crate's public API response for `fpr-ff1` on 2026-10-11.

## 20. Confidence

**High.** Every affected path and symbol was read at the baseline commit, the two evidence-based
decisions (D1, D2) were reproduced by execution on 2026-10-11 rather than taken from the earlier
work log alone, and the release steps repeat the pattern that shipped `2.1.0` two weeks ago. The
principal residual uncertainty is the semver step's exact behaviour on `cargo-semver-checks`
0.50.0 with an explicit baseline, which STEP-04's first CI run resolves and which is revertible
in isolation.
