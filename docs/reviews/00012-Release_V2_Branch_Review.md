---
title: "Code Review 00012: Release V2 Branch Review"
aliases:
  - "Review 00012"
tags:
  - code-review
  - software-quality
  - opencode
  - release-readiness
  - ff1
type: code-review
status: open
review_id: "00012"
reviewed_at: "2026-09-25T14:43:06Z"
reviewer_agent: review
review_model: "ollama-cloud/deepseek-v4.1-flash"
triggered_by: "user"
review_kind: re-review
previous_review: "[[00011-Release_V2_Rc2_Code_Review]]"
repository: "joelee/fpr-ff1"
branch: "release/v2"
review_mode: branch
pr_reference: null
commit: "0fe89eac31cf5b7281de095f506559c4882f00d2"
base_ref: "main"
base_commit: "b10d3b0e88a425e424b040a925de43364f5ae08d"
head_ref: "release/v2"
head_commit: "0fe89eac31cf5b7281de095f506559c4882f00d2"
scope: "merge-base(origin/main, release/v2)..release/v2 = b10d3b0..0fe89ea (12 commits, 7 files); plus release-readiness context at HEAD"
related_plan: "[[00007-Stable_v2.0.0_Release]]"
files_changed: 7
files_reviewed: 30
diff_additions: 1531
diff_deletions: 11
blocking_issues: 0
issues:
  critical: 0
  major: 0
  medium: 0
  low: 1
  info: 0
  total: 1
categories:
  documentation: 1
verdict: approve
review_complete: true
web_research_used: false
confidence: high
sources: []
---

# Code Review 00012: Release V2 Branch Review

> [!abstract] Verdict: `approve`
> The `release/v2` branch at `0fe89ea` is sound: the only code change is the review-00011 MED-01 migration-recipe fix, which is correct, correctly tested on both backends, and touches no shipped runtime code. One Low traceability defect was found in the plan work log. The remaining work before `v2.0.0` is the plan's own STEP-13/STEP-14 release steps plus several still-open prior findings, none of which is a code defect in this branch.

## Review target

| Field | Value |
|---|---|
| Review mode | Branch (`merge-base(origin/main, release/v2)..release/v2`) |
| PR or commit | `0fe89eac31cf5b7281de095f506559c4882f00d2` ("docs(review-00011-MED-01): translate the legacy zero tweak maximum") |
| Base | `origin/main` = `895c633`; merge base = `b10d3b0` (the `v2.0.0rc2` tag commit) |
| Head | `0fe89ea` = `HEAD` = `origin/release/v2`; worktree clean |
| Branch | `release/v2` |
| Triggered by | User: "comprehensive code review of this current branch (commit 0fe89ea) before I prepare for the `v2.0.0` release" |
| Related plan | [[00007-Stable_v2.0.0_Release]] (mid-execution: rc2 published and soaking; STEP-12 to STEP-14 outstanding); [[00008-Publish_Rust_Crate_To_Crates_io]] (approved, starts after `v2.0.0`) |
| Previous review | [[00011-Release_V2_Rc2_Code_Review]] (whose `REV-00011-MED-01` this branch implements); [[00010-Full_Codebase_Review_6fd3548]] (same branch, ancestor commit) |

### Scope and inference

The caller named a commit, not a range. The branch is `release/v2`, whose upstream default is `origin/main`; `origin/main` is a merge commit (`895c633`) that merged `b10d3b0` (the `v2.0.0rc2` tag) into `main`. The merge base is therefore `b10d3b0`, and the branch diff is the 12 commits since rc2 was tagged. That is the reviewed change set.

`docs/reviews/**` is excluded as a change target per the agent contract, but the two review files added by this branch were read as evidence, and the plan and backlog were read as release-readiness context. The review is a re-review because the branch's head commit exists specifically to close a finding from [[00011-Release_V2_Rc2_Code_Review]].

## Executive summary

The branch adds 12 commits and 7 changed files on top of the `v2.0.0rc2` tag. Only two of those files are code or tests; the rest are review reports, a new plan, and plan work-log entries. `src/`, `rust/`, `.github/` and `pyproject.toml` are **byte-identical to `6fd3548`** (`git diff --stat 6fd3548..HEAD -- src rust .github pyproject.toml` is empty), so the published rc2 artifacts are unaffected by this branch and no ciphertext, validation, or packaging behaviour changed.

The substantive change is the fix for `REV-00011-MED-01`: the README migration recipe copied the legacy `twk_max_len` straight into `max_tweak_len`, where a legacy `0` ("no maximum") became a literal maximum of zero ("empty tweaks only"). The recipe, the API-mapping table, and the interoperability module's docstring now translate a legacy `0` to `None` and copy positive bounds unchanged, with a new behaviour-change note 5 explaining the sentinel. I verified the underlying claim against the pinned oracle source in the local environment: `ubiq_security_fpe` applies its maximum only when positive (`ffx.py:48`, `ff1.py:37`), so the documentation is accurate. The translation `twk_max_len or None` is correct for every legacy-valid configuration, because the legacy constructor rejects `mintwklen > maxtwklen` (`ffx.py:46-49`), so a legacy maximum of `0` always implies a minimum of `0`.

Two tests were added. `test_documented_migration_recipe_accepts_what_the_legacy_context_accepted` follows the documented recipe literally against the pinned oracle on both backends for `(0, 0)` and `(4, 8)`, covering encrypt, decrypt, and a per-call tweak; it is capable of failing before the fix (reverting the helper to `max_tweak_len=twk_max_len` raises `TweakLengthError` at construction for the `(0, 0)` case, as the plan's red-then-green record states). `test_max_tweak_len_zero_means_empty_tweaks_only` pins the literal-zero semantics so the translation stays necessary. Both use the `ff1_factory` fixture, so both run on the python and rust backends.

One Low finding was established: the plan 00007 work log instructs the STEP-12 review to disposition `REV-00010-MED-01`, an identifier that does not exist. Commit `699f5fe` fixed the review file's internal references but missed the two plan references. This is internal traceability only — `docs/plans/` is excluded from the sdist by the CI contents assertion — so it does not ship.

The remaining work before `v2.0.0` is process, not code: the version bump and documentation finalisation (STEP-13), the owner's tag and publication (STEP-14), the merge of `release/v2` into `main` before the final tag (a recorded deviation the approved plan does not contain), and the still-open prior findings listed in the Handoff. None of these is a defect in this branch's change.

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

#### REV-00012-LOW-01 — The plan work log instructs the STEP-12 review to disposition a finding identifier that does not exist

- **Location:** `docs/plans/00007-Stable_v2.0.0_Release.md:797` (execution log) and `docs/plans/00007-Stable_v2.0.0_Release.md:816` (deviations and blockers) — both in the Builder Work Log.
- **What:** Both entries reference `REV-00010-MED-01` as the finding this branch fixes. That identifier does not exist. The finding is `REV-00011-MED-01`, in `docs/reviews/00011-Release_V2_Rc2_Code_Review.md`. Review 00010 contains exactly one finding, `REV-00010-LOW-01` (a backlog-staleness item), and no Medium finding at all. Commit `699f5fe` ("Fix code review #00011 internal references") corrected the review file's own `REV-00010-*` → `REV-00011-*` references but did not touch the two plan references, so the dangling identifier survived the fix.
- **Why it matters:** The plan is the release process record, and `PLAN-00007-AC-11` requires that "any remaining finding is dispositioned in the work log". The work log's own instruction to the STEP-12 review names a finding that cannot be looked up. A reviewer or agent following the plan literally would either fail to find the finding or record the disposition against the wrong identifier, weakening exactly the traceability the plan's review-to-plan mapping exists to provide. The correct file path appears in the same sentence, so recovery is easy — which is why this is Low rather than Medium.
- **Evidence:**

  ```markdown
  # docs/plans/00007-Stable_v2.0.0_Release.md:797
  | 2026-09-22T14:29:41Z | PLAN-00007-STEP-12 | User-directed fix outside the approved plan:
  review 00011 (file docs/reviews/00011-Release_V2_Rc2_Code_Review.md) REV-00010-MED-01, ...

  # docs/plans/00007-Stable_v2.0.0_Release.md:816
  | ... | The STEP-12 review should disposition REV-00010-MED-01 against this commit | ...
  ```

  The only finding in review 00010 is `REV-00010-LOW-01` (`docs/reviews/00010-Full_Codebase_Review_6fd3548.md:110`); the migration finding is `REV-00011-MED-01` (`docs/reviews/00011-Release_V2_Rc2_Code_Review.md:132`).

- **Suggested fix (described, not applied):** Replace both occurrences of `REV-00010-MED-01` with `REV-00011-MED-01` in the plan 00007 work log. This is a Builder-maintained section, so the correction belongs to the Builder's next work-log update (STEP-12 or STEP-13) rather than to a planning amendment. Do not alter the approved planning content.
- **References:** Repository evidence; `docs/plans/AGENTS.md` §Builder execution (Builder owns the delimited work-log section); `docs/reviews/AGENTS.md` §Relationship to plans.

## Open questions

These are release-process items and missing evidence, not counted defects.

| Question | Why it matters | Evidence that would resolve it |
|---|---|---|
| Does this review satisfy `PLAN-00007-STEP-12`, or is a range-mode review still wanted? | STEP-12 asks for an independent review of `v2.0.0rc1..v2.0.0rc2` with the STEP-10/STEP-11 evidence bundle attached. [[00011-Release_V2_Rc2_Code_Review]] was a bounded snapshot review of a ZIP (`requested_branch_comparison_complete: false`), and this report reviews the branch since rc2, not the rc1→rc2 range. | An owner decision recorded in the plan work log, or a range-mode review with the CI run URLs, PyPI verification, bench run and negative-control run attached. |
| Will `release/v2` be merged into `main` before the final `v2.0.0` tag? | The plan's own deviation record (`docs/plans/00007-Stable_v2.0.0_Release.md:815`) states the approved plan never merges `release/v2` into `main`, that every earlier release tag sits on `main` after a PR merge, and that the user chose a merge commit. The final tag must be reachable from `main` or the rc2 gap repeats. | A recorded merge step in the STEP-13/STEP-14 work log, or an explicit owner decision that the final tag may sit on `release/v2`. |
| Has the rc2 soak elapsed? | The owner's D6 statement is "soak until 2026-09-25" (`docs/plans/00007-Stable_v2.0.0_Release.md:796`), and STEP-12 "may not start before that entry exists and, if dated, the date has passed". Today is 2026-09-25, so the gate has now cleared, but the plan front matter still reads `implementation_status: blocked` and the step table still reads STEP-12 `blocked`. | A Builder work-log entry recording the soak as elapsed and moving STEP-12 to `in-progress`/`completed`. |
| Are the three still-open review-00011 Low findings to be fixed before `v2.0.0`, or accepted? | `REV-00011-LOW-01` (released `memoryview` escapes the typed error family), `REV-00011-LOW-02` (the tweak-sensitivity property cannot fail), and `REV-00011-LOW-03` (concurrency tests keep only the last iteration) are all still present at HEAD. STEP-12 task 3 requires the owner to disposition any remaining non-Major finding in the work log. | A work-log disposition entry for each, or fixes in a further candidate. |

## Review coverage

### Files and areas reviewed

- **Changed files, full read (7):** `README.md` (migration section and note 5), `docs/plans/00007-Stable_v2.0.0_Release.md` (full), `docs/plans/00008-Publish_Rust_Crate_To_Crates_io.md` (full), `docs/reviews/00010-Full_Codebase_Review_6fd3548.md` (full), `docs/reviews/00011-Release_V2_Rc2_Code_Review.md` (full), `tests/test_interoperability.py` (full), `tests/test_validation.py` (targeted: the new test and the surrounding tweak-bound suite).
- **Runtime code, re-read for the changed contract:** `src/fpr_ff1/_ff1.py` — `_validate_tweak_bounds` (`:61-113`), `_require_bytes` (`:116-122`), `__init__` (`:209-317`), `__setstate__` (`:332-380`), `_validate_tweak_length`/`_validate_tweak` (`:395-415`), `_prepare` (`:446-485`).
- **Test infrastructure:** `tests/conftest.py` (`BACKENDS`, `ff1_factory`, `encrypt_traced`), `tests/_oracle/__init__.py` (the `(0, 0)` legacy adapter), `tests/test_contract.py`, `tests/test_properties.py` (`:96-122`), `tests/test_thread_safety.py` (`:63-142`).
- **Pinned oracle source (local environment, read-only):** `.venv/lib/python3.12/site-packages/ubiq_security_fpe/ff1.py` and `ffx.py` — used to verify the legacy zero-maximum semantics the README now documents.
- **Release and packaging context:** `.github/workflows/ci.yml` (full), `.github/workflows/publish.yml` (full), `pyproject.toml` (full), `justfile` (full), `uv.lock` and `rust/Cargo.lock` (version entries), `rust/fpr-ff1-rust/Cargo.toml`.
- **Documentation and process context:** `AGENTS.md`, `docs/AGENTS.md`, `docs/reviews/AGENTS.md`, `docs/plans/AGENTS.md`, `.opencode/agents/CodeReview.md`, `.agents/skills/allocating-report-numbers/allocate-report.sh`, `docs/backlog.md`, `SECURITY.md`, `CHANGELOG.md`, `docs/configuration.md`, `docs/developer-guide.md`, `docs/reviews/00007`, `00008`, `00009`.

### Checks performed

- **Target resolution:** `git status --short --branch` clean; `HEAD` = `0fe89ea` = `origin/release/v2`; `origin/HEAD` → `origin/main` = `895c633`; `git merge-base origin/main HEAD` = `b10d3b0`; `git rev-list --count b10d3b0..HEAD` = 12; `git diff --stat` = 7 files, 1531 insertions, 11 deletions.
- **Scope isolation:** `git diff --stat 6fd3548..HEAD -- src rust .github pyproject.toml` is empty, confirming no runtime, CI, or packaging change on this branch and therefore no effect on the published rc2 artifacts.
- **Legacy-semantics verification:** read the pinned `ubiq_security_fpe` source and confirmed the README's claim — the maximum is applied only when positive (`ffx.py:48`, `ff1.py:37`), and the constructor rejects `mintwklen > maxtwklen` (`ffx.py:46-49`), which is what makes `twk_max_len or None` a complete translation for every legacy-valid configuration.
- **Translation equivalence reasoning:** enumerated legacy `(0, 0)`, `(0, 8)`, `(4, 8)`, `(4, 4)` and the degenerate negative-bound cases against the new API's literal-bound semantics in `_validate_tweak_bounds` and `_validate_tweak`.
- **Test-capability reasoning:** confirmed by static tracing that reverting the helper to `max_tweak_len=twk_max_len` makes the new migration test raise `TweakLengthError` at construction for the `(0, 0)` case, so the test can fail before the fix.
- **Dual-backend coverage:** confirmed both new tests construct through `ff1_factory`, so each runs on the python and rust backends.
- **Traceability sweep:** `grep` for `REV-00010`, `REV-00011`, `REV-00007` and `REV-00008/00009` across the repository to check finding-identifier integrity and prior-finding status.
- **Release-state checks:** version lock-step (`pyproject.toml` `2.0.0rc2` / crate `2.0.0-rc2` / both locks), the `publish.yml` tag-versus-version guard, the sdist include list and its forbidden-path assertion, and the remaining `<v2.0.0 date` placeholders.

### Checks not performed

- **No project code, tests, builds, linters, formatters, scanners, benchmarks, or generators were executed by this read-only agent.** All test counts, coverage figures, CI outcomes and red-then-green claims cited are recorded evidence from the plan work logs, not fresh results.
- No wheels or sdists were built, downloaded, or imported; PyPI and crates.io were not queried; attestations were not verified.
- The NIST SP 800-38G Rev. 1 draft status was not re-checked externally; that is a STEP-13 task.
- The oracle was read but not executed; the legacy/new ciphertext agreement asserted by the new test was not reproduced here.
- `docs/reviews/00001`–`00006` were not re-read in full; only their finding identifiers were searched.

## Positive notes

- **The fix is correct and complete for the documented contract.** The `twk_max_len or None` translation is not merely plausible: the legacy constructor's `mintwklen > maxtwklen` rejection guarantees a legacy maximum of `0` always implies a minimum of `0`, so no legacy-valid configuration is mistranslated. The README's factual claim about the legacy library was verified against the pinned source rather than assumed.
- **The regression test is genuinely capable of failing.** It follows the documented recipe literally rather than re-using the already-correct `_migrated` helper, so it exercises the published instructions, and reverting the recipe breaks it. The companion test pins the literal-zero semantics so the translation cannot be "simplified" away later.
- **The change is correctly scoped.** No `src/` or `rust/` line changed, so the published rc2 artifacts and their conformance evidence remain valid; the plan work log records this explicitly as a deviation rather than silently widening the release.
- **The release gate remains strong.** `publish.yml` reuses the full `ci.yml` as its gate, publishes exactly the gated artifacts, and refuses a tag that does not match `pyproject.toml`; the sdist contents assertion excludes `docs/plans/` and `docs/reviews/`, which is why the Low finding above does not ship.

## External references

None. No web research was used for this review. The legacy-library semantics were verified against the pinned dependency source already present in the local environment, which is stronger evidence than a documentation lookup.

## Recommended next actions

1. **(Low, this report)** Correct the two `REV-00010-MED-01` references to `REV-00011-MED-01` in the plan 00007 work log, in the Builder's next work-log update.
2. **(Owner decision)** Record whether this report satisfies `PLAN-00007-STEP-12` or whether a range-mode review of `v2.0.0rc1..v2.0.0rc2` with the STEP-10/STEP-11 evidence bundle is still required.
3. **(Owner disposition)** Disposition the three still-open review-00011 Low findings and the still-open review-00010 Low finding in the plan work log, per STEP-12 task 3.
4. **(STEP-13)** Bump both manifests to `2.0.0`, refresh both locks, add the dated `[2.0.0]` changelog section with its comparison link, rewrite the README roadmap row ("Shipped as `2.0.0rc1`", `README.md:213`), and fill the `<v2.0.0 date + six months>` placeholders in `SECURITY.md:23` and `SECURITY.md:29`. Verify `grep -rn "<v2.0.0 date" .` is empty before tagging.
5. **(STEP-14)** Merge `release/v2` into `main` before the final tag, then tag exactly `v2.0.0`, publish as a non-prerelease, and verify as in STEP-11. This review found no code impediment to that.

## Handoff

**Next step:** the branch at `0fe89ea` is approved as reviewed. The only change required from this report is the one-word finding-identifier correction in the plan work log. Everything else outstanding is the plan's own STEP-12/STEP-13/STEP-14 process, plus the prior findings classified below.

### Classification of prior findings

Previous report: [[00011-Release_V2_Rc2_Code_Review]]. Each finding was re-tested against the current tree rather than assumed fixed from the change log.

| Prior finding | Classification | Current evidence |
|---|---|---|
| `REV-00011-MED-01` — the documented migration copies a legacy zero maximum into an empty-only tweak policy | **resolved** | `README.md:428-437` now passes `max_tweak_len=twk_max_len or None` with an explanatory comment; the mapping table gained the sentinel row (`README.md:445`) and behaviour-change note 5 (`README.md:465-470`); the interoperability docstring matches (`tests/test_interoperability.py:26-29`). Two new tests pin the behaviour on both backends (`tests/test_interoperability.py:137-164`, `tests/test_validation.py:185-199`). The legacy semantics were verified against the pinned oracle source. |
| `REV-00011-LOW-01` — a released `memoryview` escapes the documented typed validation errors | **still-open** | `src/fpr_ff1/_ff1.py:116-122` still calls `bytes(...)` on the accepted `memoryview` without translating the released-buffer `ValueError`. `src/` is unchanged on this branch. |
| `REV-00011-LOW-02` — the tweak-sensitivity property cannot fail when tweaks are ignored | **still-open** | `tests/test_properties.py:102-105` still reaches `pytest.skip("tweak collision")` rather than a failing assertion. The file is unchanged on this branch. |
| `REV-00011-LOW-03` — concurrency tests overwrite the intermediate results they claim to verify | **still-open** | `tests/test_thread_safety.py:81-82` and `:113-115` still assign each iteration into the same slot, so only the last result is compared. The file is unchanged on this branch. |
| `REV-00010-LOW-01` — backlog understates release progress | **still-open** | `docs/backlog.md:14-15` still reads "Candidate `2.0.0rc2` is cut; still to come are its publication and soak, an independent re-review, then the final bump and release", although rc2 was published 2026-09-18 and the soak statement recorded. `docs/backlog.md` ships in the sdist (`pyproject.toml:87`), so this text reaches users. |
| `REV-00007-MAJ-01` — restored 1.x pickles lack `_backend` | **resolved** (re-confirmed) | `src/fpr_ff1/_ff1.py:360-376` validates and stores the backend after `__dict__.update`; unchanged on this branch and independently re-confirmed by [[00010-Full_Codebase_Review_6fd3548]] and [[00011-Release_V2_Rc2_Code_Review]]. |
| `REV-00007-MED-01` — Rust wraps the tweak length | **resolved** (re-confirmed) | `src/fpr_ff1/_ff1.py:395-415` enforces the `2**32 - 1` ceiling for default and per-call tweaks, and `:96-105` rejects configured bounds above it; unchanged on this branch. |
| `REV-00007-MED-02` — only one packaged native target executed | **resolved** (re-confirmed) | `.github/workflows/ci.yml:352-472` defines the 15 installed-native legs and the full installed-abi3 gate; unchanged on this branch. Execution evidence remains the builder-reported run `35158807685`. |
| `REV-00007-LOW-01` — dual-backend sweep incomplete | **resolved** (re-confirmed) | The flagged cases route through `ff1_factory`; unchanged on this branch. |

Review 00011's own `status` remains `open`; its Medium finding is now resolved, but its three Low findings are not, so the report is not yet fully dispositioned. This review does not edit that report.

## Confidence

**High.** The change set is small, fully read, and confined to documentation and tests; the runtime code it depends on was read directly, and the one external-behaviour claim the documentation makes was verified against the pinned dependency source rather than inferred. The principal uncertainty is the release process rather than the code: whether this report satisfies STEP-12, whether the merge-to-main step will be executed before the final tag, and how the still-open prior findings will be dispositioned — all of which are owner decisions recorded as open questions, not defects in this branch.
