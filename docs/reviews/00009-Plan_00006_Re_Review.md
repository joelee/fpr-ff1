---
title: "Code Review 00009: Plan 00006 Re-Review"
aliases:
  - "Review 00009"
  - "Plan 00006 re-review"
tags:
  - code-review
  - plan-review
  - release-readiness
  - rust-backend
  - claude-code
type: code-review
status: open
review_id: "00009"
reviewed_at: "2026-09-11T11:43:10Z"
reviewer_agent: claude-code
review_model: "anthropic/claude-fable-5-1"
triggered_by: "user"
review_kind: re-review
previous_review: "[[00008-v2.0.0-plan-review]]"
repository: "joelee/fpr-ff1"
branch: "release/v2"
review_mode: commit
pr_reference: null
commit: "7e270174ac165196732d0625e5f7ea064657c1ea"
base_ref: "release/v2"
base_commit: "26b0164ef81283caee3429f971657948d3186d9c"
head_ref: "release/v2"
head_commit: "7e270174ac165196732d0625e5f7ea064657c1ea"
scope: "docs/plans/00006-Review_00007_to_v2.0.0.md as committed in 7e27017, re-tested finding by finding against review 00008; the plan's baseline 26b0164 and HEAD differ only by documentation and the numbering skill"
related_plan: "[[../plans/00006-Review_00007_to_v2.0.0]]"
files_changed: 1
files_reviewed: 9
diff_additions: 638
diff_deletions: 0
blocking_issues: 1
issues:
  critical: 0
  major: 1
  medium: 3
  low: 3
  info: 0
  total: 7
categories:
  documentation: 2
  tests: 2
  correctness: 1
  performance: 1
  release: 1
verdict: request-changes
review_complete: true
web_research_used: false
confidence: high
sources: []
---

# Code Review 00009: Plan 00006 Re-Review

> [!abstract] Verdict: `request-changes`
> The plan committed in `7e27017` is byte-identical to the draft review 00008 examined; no amendment has been made, so all seven prior findings — including the blocking one (decision D4 recorded as resolved without a decided 1.x support window) — remain open. The plan is not approvable until the draft is amended as 00008 describes.

## Review target

| Field | Value |
|---|---|
| Review mode | Commit — `docs/plans/00006-Review_00007_to_v2.0.0.md` as first committed |
| PR or commit | `7e270174ac165196732d0625e5f7ea064657c1ea` ("Plan #00006 for v2.0.0 release and new Agent Skill for Numbered Report file creation") |
| Base | `26b0164` — the plan's own recorded `baseline_commit` (`v2.0.0rc1` tag commit + review 00007) |
| Head | `7e27017` on `release/v2`; worktree clean apart from this report |
| Branch | `release/v2` |
| Triggered by | user ("Please re-review as 00009") |
| Related plan | `docs/plans/00006-Review_00007_to_v2.0.0.md` (the review target) |
| Previous review | [[00008-v2.0.0-plan-review]] |

## Executive summary

Review 00008 examined plan 00006 as an untracked draft on 2026-09-09 and returned `request-changes` with one Major, three Medium and three Low findings. Commit `7e27017` (2026-09-11) added the plan and review 00008 to the repository unchanged, alongside a new `allocating-report-numbers` skill and corresponding edits to the three `docs/*/AGENTS.md` contracts. This re-review establishes three facts:

1. **The plan has not been amended.** `git diff HEAD -- docs/plans/00006-…md` is empty; the file's modification time (2026-09-09 20:13 UTC) precedes review 00008's completion (21:09 UTC); §18 still holds its single initial-draft row; `blocking_decisions` is still `0`; and every passage 00008 cited is present verbatim (D4's "the plan makes explicit (see REQ-08)", REQ-08's "state the actual 1.x maintenance window", STEP-11's "rc2 candidate published or otherwise available for review", STEP-06's unnamed "native Intel macOS runner").
2. **The code the plan's requirements describe has not changed.** `26b0164..7e27017` touches only `docs/**` and `.agents/**`; `src/`, `rust/`, `tests/` and `.github/` are identical, so every code-level verification 00008 performed (MAJ-01 `__setstate__` gap, MED-01 `t as u32`, LOW-01 direct constructions, MED-02 wheel gate) still holds and the plan's defect requirements remain accurate.
3. **The contract passages 00008 relies on survived the contract edit.** `docs/plans/AGENTS.md` still states "`blocking_decisions` must be zero before approval" (`:161`) and "Do not convert an unresolved question into a requirement" (`:386`); the amendment-in-place rule for unapproved drafts (`:397`) is intact. The only substantive contract change is that numbering now goes through the skill script rather than a hand-made lock — which this report followed.

Consequently each prior finding is classified **still-open** below, with the identical severity. No new findings are added: a second reading of an unchanged document against unchanged code produced no defect 00008 missed, and inventing one to justify a new number would be padding. One housekeeping item is recorded under Open questions (the plan's `baseline_commit` is now one docs-only commit behind `HEAD`) for the amendment to pick up.

## Issue summary

| Severity | Count | Merge impact |
|---|---:|---|
| Critical | 0 | Blocks merge/release |
| Major | 1 | Blocks merge/release |
| Medium | 3 | Changes requested |
| Low | 3 | Non-blocking |
| **Total** | **7** | |

## Findings

Each finding below is the re-test of the like-numbered finding in [[00008-v2.0.0-plan-review]]; the full evidence, scenarios and recommendations are recorded there and are not reproduced in full. What follows is the location, the re-test result, and the smallest statement a reader needs to act.

### Critical

None.

### Major

#### REV-00009-MAJ-01 — Decision D4 (post-final 1.x support window) remains unresolved yet recorded as resolved; `blocking_decisions: 0` is still misreported (re-test of `REV-00008-MAJ-01`)

> [!warning] Blocking
> - **Confidence:** High
> - **Category:** Documentation / Release policy (plan integrity)
> - **Location:** `docs/plans/00006-Review_00007_to_v2.0.0.md` §7 row D4; §9 `PLAN-00006-REQ-08`; §11 STEP-08 task 2; front matter `blocking_decisions: 0`; `SECURITY.md:22-29`
> - **Evidence:** Unchanged since 00008. D4's resolution column still reads "the concrete window is a documentation decision the plan makes explicit (see REQ-08)"; REQ-08 still instructs the Builder to "state the actual 1.x maintenance window" without stating one; `SECURITY.md` still says "The latest `2.x` release receives fixes … backported to the most recent minor" above a table marking both `1.1.x` and `1.0.x` supported. The plans contract still requires `blocking_decisions` to be zero only when no user decision remains (`docs/plans/AGENTS.md:161,386`).
> - **Failure or attack scenario:** As in 00008: the Builder reaches STEP-08 with no source for the sentence it must write into `SECURITY.md` and either stalls or invents a support commitment the maintainer never made.
> - **Impact:** A published security-support policy nobody decided, or a plan that cannot be executed as approved.
> - **Recommendation:** Amend the draft: mark D4 open, set `blocking_decisions: 1`, obtain the user's choice (00008 offers three concrete options), then write the exact `SECURITY.md` sentence and table rows into REQ-08 so STEP-08 becomes transcription.
> - **Suggested verification:** After amendment, REQ-08 contains the literal support sentence and table; `blocking_decisions` equals the count of open rows in §7; approval is recorded only after D4 shows a user resolution.
> - **References:** Repository evidence; [[00008-v2.0.0-plan-review]] MAJ-01.

### Medium

#### REV-00009-MED-01 — No step hands `v2.0.0rc2` to the owner for tagging, publication and soak (re-test of `REV-00008-MED-01`)

- **Location:** plan §11 STEP-09/STEP-10/STEP-11 preconditions; §16; `docs/reviews/00007-…md` `STABLE-13`
- **What:** Unchanged. STEP-11's precondition "rc2 candidate published or otherwise available for review" (`:470`) still has no owner, no tag step, no `publish.yml` run, no PyPI verification and no soak window; §16 still lists only the `v2.0.0` tag.
- **Why it matters:** Decision D2 ("cut rc2 first") becomes a version-string change unless the candidate is actually published and soaked.
- **Evidence:** `grep -n "rc2 candidate published or otherwise available" docs/plans/00006-…md` → line 470, verbatim as in 00008.
- **Suggested fix:** As in 00008: an explicit owner hand-off between STEP-10 and STEP-11 (tag exactly `v2.0.0rc2` as a pre-release; `publish.yml`; PyPI verification mirroring STEP-12; soak window or explicit waiver), reflected in AC-09 and §16.

#### REV-00009-MED-02 — STEP-06 remains under-specified on runner labels, venv isolation, import-origin checks and gate flags (re-test of `REV-00008-MED-02`)

- **Location:** plan §9 `PLAN-00006-REQ-06`; §11 STEP-06 tasks 1–3
- **What:** Unchanged. The step still says "a native Intel macOS runner" without a label (`macos-15-intel` exists), gives no fresh-venv install recipe for the abi3 full-conformance leg, lists the import-origin check only under *test-or-evidence-first*, and carries none of `FPR_FF1_REQUIRE_RUST_BACKEND=1`, `FPR_FF1_REQUIRE_ORACLE=1`, the `-k rust` floor or `--cov-fail-under=100` into that leg.
- **Why it matters:** These are the details that determine whether the new gate tests the installed wheel or silently re-tests the editable source tree — the failure class review 00006 MAJ-01 was about.
- **Evidence:** `grep -n "native Intel macOS runner" …` → line 209, verbatim; STEP-06 tasks contain no `uv export`/`uv pip install` recipe and no `__file__` assertion.
- **Suggested fix:** As in 00008: name the labels per target; add the fresh-venv recipe (`uv export --frozen --no-emit-project` + `uv pip install`; never `uv sync`/`uv run` in that leg); make the two `__file__` checks a numbered task; carry the four flags; decide the Python fan-out; add an import-origin stop condition.

#### REV-00009-MED-03 — REQ-02 still omits the configured-bound/ceiling interaction and the sibling `n as u32` cast (re-test of `REV-00008-MED-03`)

- **Location:** plan §9 `PLAN-00006-REQ-02`; §11 STEP-02 tasks 1–2; `src/fpr_ff1/_ff1.py:61-97`; `rust/fpr-ff1-rust/src/lib.rs:300-301`
- **What:** Unchanged. REQ-02 specifies the per-tweak ceiling only; review 00007 MED-01's "define how configured bounds interact with that ceiling without silently clamping" is still absent, so `min_tweak_len=2**32` would still construct an unsatisfiable instance and `max_tweak_len=2**40` would still be a clamp by omission. STEP-02 task 2 still converts only `t`.
- **Why it matters:** The ceiling exists to make rejection explicit and identical on both backends; leaving the bounds path able to admit an unsatisfiable or silently-capped configuration recreates the defect one layer up.
- **Evidence:** `_validate_tweak_bounds` unchanged at `26b0164..7e27017`; `lib.rs:300` `(n as u32)` and `:301` `(t as u32)` unchanged.
- **Suggested fix:** As in 00008: reject both bounds above `2**32 - 1` at construction; `u32::try_from` for both `n` and `t`; add the constructor cases to the contract sweep; note the new rejection in the changelog as SemVer-relevant.

### Low

#### REV-00009-LOW-01 — STEP-04's "fast at long inputs" objective still has no decision rule (re-test of `REV-00008-LOW-01`)

- **Location:** plan §11 STEP-04 objective; §9 `PLAN-00006-REQ-04`/`REQ-05`
- **What / Why / Suggested fix:** Unchanged. The port's outcome is likely favourable (`num-bigint` 0.4.8 uses Burnikel–Ziegler division above 64 limbs) but is asserted rather than gated. Add the park rule from 00008 (`rust ≤ python` at n=20,000 on radix 10 and 256, else escalate with numbers and keep crossover guidance) and mirror Python's `_D_C_THRESHOLD = 64` by name.

#### REV-00009-LOW-02 — REQ-01 still lacks the attribute-parity structural test and the sibling-test fix (re-test of `REV-00008-LOW-02`)

- **Location:** plan §9 `PLAN-00006-REQ-01`; `tests/test_backend_dispatch.py:263-279`; `src/fpr_ff1/_ff1.py:184`
- **What / Why / Suggested fix:** Unchanged. `test_corrupt_unpickled_backend_raises` and `test_non_str_unpickled_backend_raises` still construct their destination normally; no test asserts `set(vars(restored)) == set(vars(fresh))`. Add both to REQ-01 so the next `__init__`-only attribute fails immediately.

#### REV-00009-LOW-03 — Three STABLE sub-items are still missing from the plan (re-test of `REV-00008-LOW-03`)

- **Location:** plan §9 `PLAN-00006-REQ-08`, `REQ-09`; review 00007 `STABLE-10`, `STABLE-11`, `STABLE-12`
- **What / Why / Suggested fix:** Unchanged. Running the sdist's packaged tests, capturing `rustc --version` for the release build, and the "Python coverage ≠ Rust line coverage" wording are still absent. Add to STEP-10 task 2, STEP-10/12 evidence, and STEP-08 respectively.

## Open questions

1. **Refresh the plan's baseline on amendment.** The plan records `baseline_commit: 26b0164`; `HEAD` is now `7e27017`. The delta is documentation and the numbering skill only, so nothing in the plan is invalidated, but the amendment that addresses MAJ-01 should re-run the clean-state gate and update `baseline_commit`/§3 to the commit it is amended against, per `docs/plans/AGENTS.md` §Draft.
2. **Which agent amends?** `docs/plans/AGENTS.md:397` permits amending this same numbered draft in place (it is unapproved, the worktree is clean, no Builder entry exists). The user should name the amending agent; the D4 decision itself must come from the user regardless.

## Review coverage

### Files and areas reviewed

- `docs/plans/00006-Review_00007_to_v2.0.0.md` at `7e27017` — full read; compared against the version reviewed by 00008 via `git diff HEAD`, file mtime, §18 change log, front matter and the four cited passages.
- `docs/reviews/00008-v2.0.0-plan-review.md` — full read, every finding re-tested.
- `git diff --stat 26b0164 7e27017` — confirmed the only changes are `docs/**` and `.agents/**`.
- `docs/plans/AGENTS.md`, `docs/reviews/AGENTS.md` diffs in `7e27017` — confirmed the contract lines 00008 cites are intact and the numbering protocol change is procedural.
- `.agents/skills/allocating-report-numbers/SKILL.md` and `allocate-report.sh` — read before use.
- `src/fpr_ff1/_ff1.py`, `rust/fpr-ff1-rust/src/lib.rs`, `tests/test_backend_dispatch.py`, `SECURITY.md` — confirmed unchanged since 00008 (no re-read required beyond the diff check).

### Checks performed

- Target resolution: plan tracked at `HEAD`; worktree clean except this report; `git diff HEAD -- <plan>` empty.
- Byte-level identity of the reviewed plan with the 00008 target (mtime 2026-09-09 20:13 UTC < 00008's `reviewed_at` 21:09 UTC; single §18 row; counts 12/12/12; `blocking_decisions: 0`).
- Each 00008 finding re-tested by locating its cited text in the current plan and the cited code at `HEAD`.
- Number allocation through `allocate-report.sh docs/reviews Plan_00006_Re_Review.md` (returned `00009`).

### Checks not performed

- No project code, tests, builds or workflows were executed; the target is a document and the code is unchanged.
- No web research; 00008's runner-label lookup (accessed 2026-09-09) is relied on, not repeated.
- The plan was not re-audited from scratch for findings beyond 00008's; a second independent pass over an unchanged document was judged unlikely to add signal and was not performed as a separate exercise.

## Positive notes

- The plan's structural strengths noted in 00008 stand: complete traceability to review 00007, accurate defect requirements, sound sequencing, specific stop conditions.
- Committing the draft and its review together (`7e27017`) keeps the record intact and makes the amendment a clean, diffable step.
- The new `allocating-report-numbers` skill removes a hand-rolled lock protocol from three contracts and worked first time for this allocation.

## External references

None. All findings rest on repository evidence and on [[00008-v2.0.0-plan-review]].

## Recommended next actions

1. Amend draft plan 00006 in place per 00008's seven findings; refresh `baseline_commit` to the amendment's `HEAD`; record the amendment in §18.
2. Obtain the user's D4 decision first — it is the only item the Builder cannot resolve — and write its result into REQ-08 verbatim.
3. Re-review the amended draft (next number) before approval; that review should be able to classify all seven as `resolved`.

## Handoff

To the maintainer: nothing has changed since 00008 — the plan was committed as reviewed, not as amended. The one thing only you can do is decide the 1.x support window (D4); everything else is a mechanical amendment of the draft. Once amended, ask for a re-review; expect it to be short.

### Disposition of every finding from review 00008

| Prior finding | Disposition | Evidence |
|---|---|---|
| `REV-00008-MAJ-01` — D4 unresolved, `blocking_decisions` misreported | **still-open** | D4 row, REQ-08 text, and `blocking_decisions: 0` unchanged; `SECURITY.md:22-29` unchanged |
| `REV-00008-MED-01` — no rc2 owner hand-off | **still-open** | STEP-11 precondition at `:470` unchanged; §16 lists only `v2.0.0` |
| `REV-00008-MED-02` — STEP-06 under-specified | **still-open** | `:209` unchanged; no venv recipe, `__file__` task, or flags in STEP-06 |
| `REV-00008-MED-03` — REQ-02 bounds/ceiling and `n` cast | **still-open** | REQ-02/STEP-02 unchanged; `lib.rs:300-301` unchanged |
| `REV-00008-LOW-01` — no performance decision rule | **still-open** | STEP-04 unchanged |
| `REV-00008-LOW-02` — attribute-parity test, sibling tests | **still-open** | REQ-01 unchanged; `test_backend_dispatch.py:263-279` unchanged |
| `REV-00008-LOW-03` — three STABLE sub-items dropped | **still-open** | REQ-08/REQ-09 unchanged |

Review 00007's four code findings remain valid at `7e27017` and are `not-in-scope` for this document review; review 00006 remains `addressed`.

## Confidence

**High.** The re-review question — has the plan changed, and do the prior findings still hold — is answered by direct evidence (`git diff HEAD` empty, mtime ordering, unchanged cited passages, a docs-only commit delta), not by judgement. The residual uncertainty is the same as 00008's: the Rust conversion's long-input performance is likely but unmeasured, which is why LOW-01 asks for a rule rather than a prediction.
