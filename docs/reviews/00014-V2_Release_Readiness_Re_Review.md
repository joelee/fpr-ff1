---
title: "Code Review 00014: V2 Release Readiness Re Review"
aliases:
  - "Review 00014"
tags:
  - code-review
  - software-quality
  - opencode
  - release-readiness
  - ff1
type: code-review
status: open
review_id: "00014"
reviewed_at: "2026-09-25T15:16:54Z"
reviewer_agent: review
review_model: "zai-coding-plan/glm-5.3"
triggered_by: "user"
review_kind: re-review
previous_review: "[[00013-Release_V2_Comprehensive_Re_Review]]"
repository: "joelee/fpr-ff1"
branch: "release/v2"
review_mode: branch
pr_reference: null
commit: "0fe89eac31cf5b7281de095f506559c4882f00d2"
base_ref: "origin/main"
base_commit: "b10d3b0e88a425e424b040a925de43364f5ae08d"
head_ref: "release/v2"
head_commit: "0fe89eac31cf5b7281de095f506559c4882f00d2"
scope: "merge-base(origin/main, release/v2)..HEAD = b10d3b0..0fe89ea (12 commits, 7 files), excluding docs/reviews/** as change targets (5 files, 782/11); supplemental full reads of both runtime cores and release-critical state at HEAD"
related_plan: "docs/plans/00007-Stable_v2.0.0_Release.md"
files_changed: 5
files_reviewed: 24
diff_additions: 782
diff_deletions: 11
blocking_issues: 0
issues:
  critical: 0
  major: 0
  medium: 0
  low: 0
  info: 0
  total: 0
categories: {}
verdict: approve
review_complete: true
web_research_used: true
confidence: high
sources:
  - https://doc.rust-lang.org/std/primitive.slice.html#method.as_chunks
---

# Code Review 00014: V2 Release Readiness Re Review

> [!abstract] Verdict: `approve`
> Independent re-review of `release/v2` at `0fe89ea` established no new defect: both FF1 cores were re-verified line by line against SP 800-38G, the branch's migration-recipe fix was verified against the pinned legacy source, and no runtime, packaging, or CI byte has moved since the published `v2.0.0rc2` — the branch is fit to continue `v2.0.0` preparation, while six prior findings (one Medium, five Low) still await the owner's STEP-12 dispositions and STEP-13/14 remain outstanding.

## Review target

| Field | Value |
|---|---|
| Review mode | Branch (`merge-base(origin/main, release/v2)..release/v2`), with supplemental core reads and release-readiness checks |
| PR or commit | `0fe89eac31cf5b7281de095f506559c4882f00d2` ("docs(review-00011-MED-01): translate the legacy zero tweak maximum"), verified equal to local `HEAD` |
| Base | `origin/main` = `895c63350e33a17ffa8719b55a2c861baaf24942` (PR #9, which merged rc2); merge base = `b10d3b0e88a425e424b040a925de43364f5ae08d` (the `v2.0.0rc2` tag commit) |
| Head | `0fe89ea`, 12 commits beyond the merge base |
| Branch | `release/v2` |
| Triggered by | User: "comprehensive code review of this current branch (commit 0fe89ea) before I prepare for the `v2.0.0` release" |
| Related plan | [[../plans/00007-Stable_v2.0.0_Release]] (STEP-12 to STEP-14 outstanding); [[../plans/00008-Publish_Rust_Crate_To_Crates_io]] (approved, starts after v2.0.0) |
| Previous review | [[00013-Release_V2_Comprehensive_Re_Review]] (untracked, written today); its predecessor [[00012-Release_V2_Branch_Review]] (also untracked) |
| Working-tree scope | No staged or unstaged tracked changes. Pre-existing untracked reports 00012 and 00013 are context, not change targets; review reports are excluded from the target per the review contract. |

### Comparison boundaries

The caller names the current branch and its head commit. The inferred comparison is `b10d3b0..0fe89ea`: 12 commits, 7 files, 1,531 additions, 11 deletions. The two added review reports (00010, 00011) are excluded as change targets, leaving the 5 files and 782/11 recorded in front matter: `README.md`, plans 00007/00008, and the interoperability/validation test modules.

Because `origin/main` already absorbed rc2 through PR #9, the branch diff alone understates the release. This review therefore also re-read, in full and at HEAD, the two runtime cores (`src/fpr_ff1/_ff1.py`, `rust/fpr-ff1-rust/src/lib.rs`) and the surrounding contract surfaces, and confirmed by direct diff that `src/`, `rust/`, `.github/`, `pyproject.toml`, `justfile`, `benchmarks/`, and `uv.lock` are **byte-identical to the published rc2 tag commit** (`git diff --stat b10d3b0..HEAD` over those paths is empty). Reviews 00010–00013 covered the rc1→rc2 product diff; this review re-verified rather than re-derived their conclusions. No remote was fetched, so remote-tracking refs are local evidence.

## Executive summary

**No new finding was established.** The substance of this review was independent verification, and every check passed:

- **Both FF1 cores conform to SP 800-38G Algorithm 7 under a fresh line-by-line read.** All seven AGENTS.md "implementation gotchas" were checked in both cores: `b` derived from `v` (`_ff1.py:842`, `lib.rs:460`); exact-integer bit length with no floating point anywhere; padding `(-t - b - 1) % 16` (the Rust `rem_euclid` form at `lib.rs:474` reproduces Python's always-non-negative modulo); encrypt/decrypt differing in exactly the three specified places with the parity rule identical in both; `S` truncated to `d` bytes; the PRF as a zero-IV CBC-MAC over 16-byte-aligned input with a fresh chain per call; and no cached cipher context on the instance. The P-block layout (`[1,2,1] || [radix]^3 || [10] || [u mod 256] || [n]^4 || [t]^4`), the S-expansion as single forward blocks over `R XOR [j]^16`, the ten rounds, and the final `A || B` all match the specification. The Rust decrypt's `+ modulus - (y % modulus)` form avoids negative `BigUint` for validated inputs.
- **The branch's only code-bearing change — the legacy zero-maximum migration fix — is correct.** The README recipe's `max_tweak_len=twk_max_len or None` translation was verified against the pinned oracle source in the local environment (`ubiq_security_fpe/ffx.py:46-49`): the legacy constructor applies its maximum only when positive and rejects `mintwklen > maxtwklen`, so a legacy maximum of `0` always implies a minimum of `0` and the translation is complete for every legacy-valid configuration. Both new tests construct through `ff1_factory` (dual-backend), and static tracing confirms the recipe test fails under the pre-fix direct copy (constructor with `min=0`, `max=0`, and the 5-byte default tweak raises `TweakLengthError` at `_ff1.py:414-415`).
- **The published rc2 artifacts are untouched.** No runtime, CI, packaging, or lock byte changed since `b10d3b0`, so rc2's recorded conformance evidence remains valid for this tree.
- **Release state is consistent and plan-tracked.** `pyproject.toml` `2.0.0rc2`, crate `2.0.0-rc2`, both locks in step; `SECURITY.md`'s `<v2.0.0 date + six months>` placeholders and the empty `CHANGELOG` `[Unreleased]` section are the documented STEP-13 work, not defects.
- **The one open Medium finding was re-verified with fresh external evidence.** `slice::as_chunks` is stable since **1.88.0** per the current Rust standard-library documentation (accessed 2026-09-25), while plan 00008 decision D8 declares `rust-version = "1.87"` reasoning only from `is_multiple_of`/`repeat_n`/`div_ceil`, and STEP-01 moves the `as_chunks`-using PRF into the published core. This affects the future crate plan, not the v2.0.0 artifacts (`rust-toolchain.toml` pins `channel = "stable"`; plan 00008 starts only after v2.0.0 per D7).

This is approval to continue release preparation. **It is not approval to tag this tree as `v2.0.0`**: both manifests still read rc2, and the version bump, changelog, placeholder fills, final CI evidence, merge-to-main, and tag are STEP-13/14 work. Six prior findings (one Medium, five Low) remain open and require the owner dispositions that plan 00007 STEP-12 task 3 demands; they are classified in Handoff and retain their original identifiers.

## Issue summary

Counts describe findings newly established by this report. There are none; the open prior findings are listed in Handoff under their original identifiers and are not republished here as new discoveries.

| Severity | Count | Merge impact |
|---|---:|---|
| Critical | 0 | Blocks merge/release |
| Major | 0 | Blocks merge/release |
| Medium | 0 | Changes requested |
| Low | 0 | Non-blocking |
| **Total** | **0** | |

## Findings

> [!success] No actionable findings
> No Critical, Major, Medium, or Low issues were newly identified within the reviewed scope. This does not prove the change is defect-free; see review coverage and limitations. Six findings from prior reviews of this same release line remain open and are classified in Handoff.

## Open questions

| Question | Why it matters | Evidence that would resolve it |
|---|---|---|
| Owner dispositions for the six open prior findings | STEP-12 task 3 requires every remaining finding to be fixed or accepted with reasons in the work log; no such record exists yet for `REV-00013-MED-01`, `REV-00012-LOW-01`, `REV-00011-LOW-01/02/03`, `REV-00010-LOW-01` | A work-log entry per finding (fix or reasoned acceptance) |
| Soak-gate bookkeeping | The owner's D6 statement is "soak until 2026-09-25" (today); the step table still reads STEP-12 `blocked` (`docs/plans/00007-Stable_v2.0.0_Release.md:751`) and the front matter still says blocked | A Builder work-log entry recording the soak as elapsed and STEP-12's state |
| Committing the review record | Reviews 00012, 00013, and this report are untracked; the branch's committed review evidence currently ends at 00011. Traceability for the STEP-12 disposition (and `PLAN-00007-AC-11`) is weaker while the newer reports are local-only. `docs/reviews/` is excluded from the sdist, so nothing ships either way | The STEP-12/13 work committing `docs/reviews/00012–00014` (or an explicit owner decision not to) |
| Final-commit evidence | The plan records green CI (runs 35158807685, 35402901107) at `b10d3b0`, not at the future version-bump commit; release verification must attach to that exact commit before the `v2.0.0` tag | The STEP-13/14 work-log entries with the final commit's run URLs and local gate results |

## Review coverage

### Files and areas reviewed

- **Changed files (all 7 inspected):** `README.md` (migration recipe, mapping table, note 5, with surrounding section), `docs/plans/00007-Stable_v2.0.0_Release.md` (work log, deviations, verification results), `docs/plans/00008-Publish_Rust_Crate_To_Crates_io.md` (front matter, objective, decisions D1–D9, requirements, strategy, STEP-01 through STEP-09), `docs/reviews/00010` and `00011` (finding identifiers verified directly), `tests/test_interoperability.py` (full), `tests/test_validation.py` (new test and suite context).
- **Runtime cores, full reads:** `src/fpr_ff1/_ff1.py` (958 lines) and `rust/fpr-ff1-rust/src/lib.rs` (724 lines), compared step by step against SP 800-38G Algorithm 7 and each other.
- **Package surface:** `src/fpr_ff1/__init__.py` (full).
- **Test infrastructure:** `tests/conftest.py` (full: `BACKENDS`, `ff1_factory`, `encrypt_traced`, oracle guard), `tests/_oracle/__init__.py` (full), `tests/test_properties.py:80-139`, `tests/test_thread_safety.py:60-139`, inventory greps of `test_exact_arithmetic.py`, `test_backend_dispatch.py`, `test_differential.py`, `test_contract.py`, `test_sequence_validation.py`, `test_conversion_equivalence.py`, `test_nist_vectors.py`, `test_intermediates.py`, `test_frozen_kat.py`, `test_pickle.py`, `test_rust_aes_validation.py`, `test_backend_agreement.py`.
- **Release and packaging state:** `pyproject.toml` and `rust/fpr-ff1-rust/Cargo.toml` (version fields), `uv.lock` and `rust/Cargo.lock` (version entries), `CHANGELOG.md` (top sections), `SECURITY.md` (placeholder greps), `rust-toolchain.toml` (full), `docs/backlog.md:1-30`.
- **Pinned oracle (read-only, local environment):** `.venv/lib/python3.12/site-packages/ubiq_security_fpe/ffx.py` (full) — the source of the legacy zero-maximum semantics the README now documents.
- **Prior reports:** [[00012-Release_V2_Branch_Review]] and [[00013-Release_V2_Comprehensive_Re_Review]] in full; finding identifiers of reviews 00005–00011 verified by search.

### Checks performed

- **Target resolution:** `git status --short --branch` (clean except the two untracked reports); `HEAD` = `0fe89ea` on `release/v2`; `origin/HEAD` → `origin/main` = `895c633`; merge base `b10d3b0`; 12 commits in range; diff stat 7 files / 1,531 / 11 (5 / 782 / 11 excluding review reports).
- **Runtime isolation:** `git diff --stat b10d3b0..HEAD -- src rust .github pyproject.toml justfile benchmarks uv.lock` is empty — no runtime, CI, packaging, or lock change since the published rc2 tag commit.
- **Spec conformance:** line-by-line trace of both cores against Algorithm 7 steps 1–7 and Algorithm 6, including every AGENTS.md gotcha (see Executive summary); P/Q construction, PRF chaining, S-expansion semantics, moduli hoisting, round order, and swaps checked individually.
- **Conversion fast paths:** dispatch order and threshold parity (`_D_C_THRESHOLD`/`D_C_THRESHOLD` = 64 in both), power-of-two packing widths (k ≤ 15, ≤ 120-bit `u128` accumulators), truncation contracts, call-local caches.
- **Legacy-semantics verification:** read the pinned `ubiq_security_fpe` source and confirmed the maximum is applied only when positive (`ffx.py:48`) and `mintwklen > maxtwklen` is rejected (`ffx.py:46-49`), which makes `twk_max_len or None` a complete translation; enumerated the `(0, 0)`, `(0, 8)`, `(4, 8)`, `(4, 4)` cases against `_validate_tweak_bounds`/`_validate_tweak`.
- **Test-capability reasoning:** statically traced both new tests to confirm they can fail before the fix and pin the literal-zero semantics afterwards; confirmed dual-backend parameterisation through `ff1_factory`.
- **Prior-finding re-testing:** each open finding from reviews 00007, 00010, 00011, 00012, and 00013 re-verified against current source (see Handoff), not assumed from the earlier reports.
- **External verification:** Rust standard-library documentation for `slice::as_chunks` (stable since 1.88.0), accessed 2026-09-25, independently confirming the stabilization version underlying `REV-00013-MED-01`.
- **Release state:** version lock-step across four files; `rust-toolchain.toml` channel pin; `SECURITY.md`/`CHANGELOG`/README placeholder and roadmap status; plan 00007 step-table vs. work-log consistency.

### Checks not performed

- **No project code, tests, builds, linters, formatters, scanners, benchmarks, hooks, package managers, or scripts were executed** by this read-only agent. No passing-test claim here originates from a reviewer run; recorded CI outcomes (runs 35158807685, 35402901107) are builder-reported plan entries.
- No wheels or sdists were built, downloaded, or imported; PyPI and crates.io were not queried; attestations were not verified.
- The oracle was read but not executed; ciphertext agreement asserted by the new interoperability test was not reproduced.
- NIST vector fixtures were not retranscribed or recomputed; their consumers and their preservation in the diff were checked.
- The rc1→rc2 product diff was covered by reviews 00010–00013 and re-verified here only through full reads of the resulting cores at HEAD, not as a hunk-by-hunk re-review.
- No `.codegraph/` index exists in this checkout; sources were read directly.
- Only `slice::as_chunks` was externally re-verified; D8's other stabilization claims (1.87/1.82/1.73) were accepted as consistent with the plan's own reasoning, since the defect is the omitted API, not the listed ones.

## Positive notes

- The branch's fix is correctly scoped: documentation and tests only, with byte-identical runtime since the published candidate — the release evidence carries over untouched, and the commit message says exactly that.
- The migration recipe fix was verified against the pinned legacy source rather than assumed, and its regression test follows the published instructions literally instead of re-using an already-correct helper, so it genuinely exercises the documentation.
- Both cores carry the spec-step comments and the gotcha warnings inline (including the deliberate `manual_div_ceil` allows with rationale), which is what made an independent line-by-line verification practical.
- The test suite's structure — dual-backend fixtures, oracle-gated differential tests, per-round intermediate traces, float-op AST scan, 100% coverage floor — materially reduces the risk that a plausible-but-wrong core change ships.

## External references

- **[R1] "Primitive type slice — `as_chunks`," Rust standard-library documentation, Rust project** (current stable 1.98.1). Living documentation; update date not stated. The API is labelled stable since **1.88.0** (const since 1.88.0). Accessed **2026-09-25**. <https://doc.rust-lang.org/std/primitive.slice.html#method.as_chunks>

## Recommended next actions

1. **Record STEP-12 dispositions** for the six open prior findings (fix or reasoned acceptance) in the plan 00007 work log, including the soak-gate update (today is the stated end date) and the correction of the two `REV-00010-MED-01` → `REV-00011-MED-01` references (`REV-00012-LOW-01`).
2. **Commit the review record** — reviews 00012, 00013, and this report — as part of the STEP-12/13 work so the release's review evidence is complete in-repo.
3. **Execute STEP-13** exactly as approved: bump both manifests to `2.0.0` together, refresh only the intended lock edges, add the dated `[2.0.0]` changelog section with comparison links (covering the post-rc README migration fix), fill the `SECURITY.md` placeholders, rewrite the README roadmap row, and repeat the NIST draft-status check; verify no `<v2.0.0 date` placeholder remains.
4. **Execute STEP-14 with the recorded merge-to-main step** (plan 00007 line 815): merge `release/v2` into main, tag exactly the final commit `v2.0.0`, publish through the gated workflow, and verify as in STEP-11. Do not tag `0fe89ea` while its manifests read rc2.
5. **Before starting plan 00008**, resolve `REV-00013-MED-01` through an authorized plan revision: MSRV ≥ 1.88, or an approved `chunks_exact(16)` rewrite of `lib.rs:112` with the lower floor then verified. Do not change the FF1 core now to satisfy a future plan decision.

## Handoff

**To the user:** the branch at `0fe89ea` is approved as reviewed for continued `v2.0.0` preparation. Nothing in this report blocks STEP-13/14. The remaining obligations are the plan's own process steps plus the dispositions below.

### Disposition of previous findings

Each classification follows this review's own source inspection. Reports 00012 and 00013 were themselves untracked when this review began; their findings are re-classified here so the record is current.

| Prior finding | Classification | Current evidence / next action |
|---|---|---|
| `REV-00013-MED-01` — plan 00008 MSRV 1.87 below `as_chunks` (1.88) used by the core it moves | **still-open** | `rust/fpr-ff1-rust/src/lib.rs:112` still calls `data.as_chunks::<16>()`; plan 00008 D8 (`docs/plans/00008-Publish_Rust_Crate_To_Crates_io.md:139`) still declares `rust-version = "1.87"` from `is_multiple_of`/`repeat_n`/`div_ceil` only; STEP-01 task 1 (line 291) still moves the PRF into the published core; STEP-07/STEP-08 (lines 410, 431) still set and gate the MSRV. Stabilization version 1.88.0 independently re-verified [R1]. No impact on v2.0.0 artifacts (`rust-toolchain.toml` pins `channel = "stable"`; plan 00008 starts after v2.0.0 per D7). Resolve by plan revision before execution. |
| `REV-00012-LOW-01` — work log names a nonexistent finding identifier | **still-open** | `docs/plans/00007-Stable_v2.0.0_Release.md:797` and `:816` still reference `REV-00010-MED-01`; review 00010 contains exactly one finding, `REV-00010-LOW-01` (verified directly at `docs/reviews/00010-Full_Codebase_Review_6fd3548.md:110`), and the migration finding is `REV-00011-MED-01` (`docs/reviews/00011-Release_V2_Rc2_Code_Review.md:132`). One-word correction in each location, in the Builder's next work-log update. |
| `REV-00011-MED-01` — legacy zero maximum mistranslated by the documented recipe | **resolved** (re-confirmed) | `README.md` migration recipe translates `twk_max_len or None` with an explanatory comment, sentinel table row, and behaviour-change note 5; `tests/test_interoperability.py:111-164` follows the recipe literally on both backends for `(0, 0)` and `(4, 8)`; `tests/test_validation.py:185-199` pins literal-zero semantics. Legacy semantics verified against the pinned oracle source this review. |
| `REV-00011-LOW-01` — released `memoryview` escapes the typed error family | **still-open** | `_require_bytes` at `src/fpr_ff1/_ff1.py:116-122` still calls `bytes(value)` without translating the released-buffer `ValueError`. Fix narrowly with key/tweak-specific errors plus regression tests, or record acceptance. |
| `REV-00011-LOW-02` — tweak-sensitivity property cannot fail; key-sensitivity assumes universal inequality | **still-open** | `tests/test_properties.py:102-105` still reaches `pytest.skip("tweak collision")` with no failing assertion; the key check at `:122` still asserts single-input inequality for all domains. Rework or accept. |
| `REV-00011-LOW-03` — concurrency tests keep only the last iteration's results | **still-open** | `tests/test_thread_safety.py:81-82` and `:113-115` still overwrite each worker's slot twenty times; only the final value is compared. Verify every iteration or retain the first mismatch. No runtime race was established. |
| `REV-00010-LOW-01` — backlog understates release progress | **still-open** | `docs/backlog.md:14-15` still describes rc2 publication, soak, and re-review as outstanding, all of which the plan work log records as done (publication 2026-09-18; this and prior re-reviews since). Update in the next authorized documentation change. |
| `REV-00007-MAJ-01` — restored 1.x pickles lack `_backend` | **resolved** (re-confirmed) | `src/fpr_ff1/_ff1.py:360-376` validates and stores the backend after `__dict__.update`, including the 1.x no-`_backend` default. Unchanged on this branch. |
| `REV-00007-MED-01` — Rust wraps the tweak length | **resolved** (re-confirmed) | `_validate_tweak_length`/`_validate_tweak` at `src/fpr_ff1/_ff1.py:395-415` enforce the `2**32 - 1` ceiling before dispatch; `encode_len_u32` (`rust/fpr-ff1-rust/src/lib.rs:162-166`) is checked and used for both `n` and `t` (`:489-490`). Unchanged on this branch. |
| `REV-00007-MED-02` — unexecuted native wheel targets | **resolved** in workflow definitions (re-confirmed unchanged) | `.github/` is byte-identical to the rc2 tag commit, whose CI defines the 15 installed-native legs and the full installed-abi3 gate. Execution evidence remains the builder-reported runs. |
| `REV-00007-LOW-01` — dual-backend sweep incomplete | **resolved** (re-confirmed) | The flagged cases, including this branch's new tests, route through `ff1_factory`. |

This report does not edit any prior report and does not mark the open findings accepted on the owner's behalf.

## Confidence

**High.** The reviewed change set is small and fully read; both runtime cores were independently re-verified line by line against the specification and each other; the branch's one behavioural claim was checked against the pinned legacy source; and the single external fact underlying the open Medium finding was re-verified against current official documentation. The principal uncertainty is execution and artifact assurance — no code, tests, or CI were run by this read-only agent, and the final `v2.0.0` gate evidence must attach to the future version-bump commit, not to this review.
