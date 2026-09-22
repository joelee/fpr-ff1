---
title: "Code Review 00010: Full Codebase Review 6fd3548"
aliases:
  - "Review 00010"
  - "Full codebase review at 6fd3548"
tags:
  - code-review
  - software-quality
  - opencode
  - release-readiness
  - ff1
type: code-review
status: open
review_id: "00010"
reviewed_at: "2026-09-22T13:34:09Z"
reviewer_agent: review
review_model: "zai-coding-plan/glm-5.3"
triggered_by: "user"
review_kind: initial
previous_review: null
repository: "joelee/fpr-ff1"
branch: "release/v2"
review_mode: repository
pr_reference: null
commit: "6fd3548504ca453f1714773a5a0228408e9f8017"
base_ref: null
base_commit: null
head_ref: "release/v2"
head_commit: "6fd3548504ca453f1714773a5a0228408e9f8017"
scope: "Whole-repository snapshot review at 6fd3548 (= HEAD of release/v2, clean worktree); no diff base. The reviewed commit itself is a one-line docs change to plan 00007; the caller explicitly requested a full review of the existing code base, so all shipped source, tests, CI, packaging, and maintained docs were inspected. docs/reviews/** excluded as change targets."
related_plan: "[[../plans/00007-Stable_v2_0_0_Release|Plan 00007]]"
files_changed: 0
files_reviewed: 42
diff_additions: 0
diff_deletions: 0
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

# Code Review 00010: Full Codebase Review 6fd3548

> [!abstract] Verdict: `approve`
> The repository at `6fd3548` (the `2.0.0rc2` soak state on `release/v2`) is in publishable shape: every prior blocking finding is verifiably fixed in source, both FF1 cores were re-checked line by line against the SP 800-38G gotcha list with no deviation found, and the release pipeline executes and verifies every artifact it ships; the sole finding is a stale progress line in `docs/backlog.md`.

## Review target

| Field | Value |
|---|---|
| Review mode | Repository (whole-codebase snapshot) |
| PR or commit | `6fd3548504ca453f1714773a5a0228408e9f8017` ("docs(PLAN-00007-STEP-05): resolve the value-dependent timing deviation") |
| Base | None — snapshot review, no diff base |
| Head | `6fd3548` = `HEAD`, worktree clean (gitignored build artifacts `src/fpr_ff1/_rs.so`, `__pycache__/`, `dist/` only; none tracked) |
| Branch | `release/v2` |
| Triggered by | User ("full code review on the existing code base (commit `6fd3548`)") |
| Related plan | [[../plans/00007-Stable_v2_0_0_Release|Plan 00007]] (mid-execution: rc2 published and soaking until 2026-09-25; STEP-12 to STEP-14 outstanding); [[../plans/00008-Publish_Rust_Crate_To_Crates_io|Plan 00008]] (approved, starts after v2.0.0) |
| Previous review | None as a re-review basis; [[00007-V2_0_0_Stable_Release_Readiness|Review 00007]]'s four findings are re-tested below because this snapshot is the rc2 that implemented them |

## Executive summary

This is a full review of the codebase as it stands at `6fd3548`: version `2.0.0rc2` (`pyproject.toml`) / `2.0.0-rc2` (crate manifest, held in lock-step), published on PyPI and soaking ahead of the final `v2.0.0` bump. The reviewed state is the product of plans 00003/00005/00007 executing findings from reviews 00006 and 0007.

What was verified, and how it came out:

1. **Both FF1 cores were re-checked statement by statement against SP 800-38G Algorithm 6/7 and the repository's own gotcha list.** `b` derives from `v` with exact integer `bit_length()` in both cores (`_ff1.py:842`, `lib.rs:456-462`); padding is `(-t-b-1) % 16` with `rem_euclid` reproducing Python's non-negative modulo (`lib.rs:474`); `P`/`Q` construction, zero-IV CBC-MAC PRF, the single-block `CIPH_K(R XOR [j]^16)` expansion, `d`-byte truncation, the identical parity rule, the three encrypt/decrypt differences, and the `A||B` return all match the spec and each other. No floating point anywhere in either core (enforced by the AST scan, `tests/test_exact_arithmetic.py:21-44`). The modular subtraction in the Rust decrypt arm (`lib.rs:557`) was checked for underflow and equivalence to Python's `%` semantics: it cannot underflow and is mathematically identical.
2. **All four findings of [[00007-V2_0_0_Stable_Release_Readiness|review 00007]] are resolved in the source**, not merely claimed: `__setstate__` now stores the validated backend (`_ff1.py:371-376`) and the regression tests restore onto `FF1.__new__(FF1)` with a real serialised 1.1-format payload and a pinned legacy attribute set (`test_backend_dispatch.py:251-328`); the tweak-length ceiling `2**32 - 1` is enforced in shared Python validation with configuration bounds rejected rather than clamped (`_ff1.py:61-113,396-415`) and the Rust core uses a checked `encode_len_u32` (`lib.rs:162-166,486-490`); every one of the five native wheels is now installed and exercised on its own platform and all three CPython versions, with an import-origin assertion and a full-suite abi3 leg (`ci.yml:352-472`), and the negative-control run recorded in plan 00007's work log shows all of these jobs reddening on a deliberate S-expansion defect; the dual-backend sweep is complete for the public-contract cases (interop, acceptance, normalisation, long-tweak, tweak-bound interop all use `ff1_factory`).
3. **The release pipeline gates publishing on everything it verifies.** `publish.yml` reuses `ci.yml` as its gate and publishes exactly the gated artifacts, with a tag/version guard; the sdist-contents assertion and wheel-conformance legs close the packaging gaps earlier reviews identified.
4. **Known, plan-tracked transitional states are not findings:** `SECURITY.md`'s literal `<v2.0.0 date + six months>` placeholder is filled by plan 00007 STEP-13 from the tag date and its absence is an acceptance criterion (`PLAN-00007-AC-12`); the README roadmap row "Shipped as `2.0.0rc1`" is rewritten by the same step. The Rust crate's public functions perform no input validation — that is recorded as the first sentence of plan 00008's objective and remedied by its REQ-02, and today the crate is `publish = false`, `cdylib`-only (not linkable as a library), with validation shared in Python for both backends by plan 00003 decision D4.

The one defect found is documentation staleness: `docs/backlog.md` still lists rc2's "publication and soak" as "still to come" although STEP-11 tagged, published, and verified rc2 and recorded the soak (commits `ebd0a66`, `aff62c4`, `052dc22`).

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

#### REV-00010-LOW-01 — Backlog understates release progress: rc2 publication and soak recorded as outstanding after STEP-11 completed them

- **Location:** `docs/backlog.md:14-15` — "Active Items / Ongoing"
- **What:** The Ongoing item reads "Candidate `2.0.0rc2` is cut; still to come are its publication and soak, an independent re-review, then the final bump and release." Since that text was written (STEP-09, commit `3050615` — the last commit touching `docs/backlog.md`), STEP-11 has run: rc2 was tagged at `b10d3b0`, merged to `main`, published to PyPI, verified, and the soak recorded until 2026-09-25 (commits `ebd0a66`, `aff62c4`, `052dc22`; plan 00007 work log entries dated 2026-09-16).
- **Why it matters:** `docs/AGENTS.md` requires the backlog to be updated "in the same change" that makes it true, and the backlog is the documented input for deciding what remains before stable `v2.0.0`. A reader consulting it at HEAD would believe publication has not happened when PyPI already serves `2.0.0rc2` — the exact "state recorded in one place, contradicted by the work log in another" drift this repository's process is built to avoid.
- **Evidence:**

  ```markdown
  - **Stable `v2.0.0` (plan 00007).** Candidate `2.0.0rc2` is cut; still to come are its
    publication and soak, an independent re-review, then the final bump and release.
  ```

  vs. plan 00007 work log: "record rc2 publication and PyPI verification" (`aff62c4`), "record the rc2 soak statement" (`052dc22`).

- **Suggested fix (described, not applied):** Update the Ongoing item to the current state — rc2 published 2026-09-16 and soaking until 2026-09-25; remaining: the independent re-review (STEP-12), final bump and documentation finalisation (STEP-13), release (STEP-14). Fold the update into the next docs-touching change on this branch (STEP-13 will rewrite the item to Completed anyway).
- **References:** Repository evidence; `docs/AGENTS.md` §Rules.

## Open questions

1. **Per-platform wheel-job depth (parked by the Builder for the owner/re-review, plan 00007 work log 2026-09-16T21:30:06Z).** The STEP-07 negative control observed that each `wheel-test-native` leg detects a core S-expansion defect through only 2 of its 149 tests (the frozen-KAT `d > 16` case and the dispatch n=60 case), while the full-suite jobs detect it through 338. **Assessment:** acceptable as shipped. Each leg's purpose is platform/ABI validation — a platform-specific AES or linking defect corrupts *all* ciphertext and fails the leg's NIST-vector subset, and the negative-control run (`35150890829`) proved every leg reddens on a core defect. Widening the subset (e.g. adding `test_backend_agreement`) multiplies per-leg runtime roughly ninefold for marginal assurance. An owner decision to widen (or explicitly accept) closes this; nothing blocks rc2→final on it.
2. **Placeholder fill at final release.** `grep -rn "<v2.0.0 date"` must return empty before the `v2.0.0` tag (STEP-13 fills it from the tag date; `PLAN-00007-AC-12` verifies). Recorded here so the checklist item survives into the final-release review.
3. **Is this report the STEP-12 re-review?** Plan 00007 STEP-12 anticipates an independent review of `v2.0.0rc1..v2.0.0rc2` with the STEP-10/11 evidence bundle (CI run URLs, PyPI verification) attached. The caller requested a full codebase review at `6fd3548` without supplying that bundle; this report reviews the same code (plus everything else) and performs the classification AC-11 requires, but the owner decides whether it satisfies STEP-12 or whether a range-mode review with the attached run evidence is wanted. The classification itself is done either way (see Handoff).

## Review coverage

### Files and areas reviewed

- **Python runtime, full read:** `src/fpr_ff1/_ff1.py` (958 lines), `src/fpr_ff1/__init__.py`, `src/fpr_ff1/_exceptions.py`. Both cores cross-checked against SP 800-38G Algorithm 6/7 and every AGENTS.md gotcha (b-from-v, exact bit length, padding, three encrypt/decrypt differences, identical parity rule, d-byte truncation, zero-IV CBC-MAC, no cached cipher contexts).
- **Rust runtime, full read:** `rust/fpr-ff1-rust/src/lib.rs` (724 lines), `src/tests.rs`, both `Cargo.toml` manifests, workspace `rust/Cargo.toml`, `rust-toolchain.toml`. Verified the decrypt modular-subtraction arm, `rem_euclid` padding equivalence, checked length encoding, `u16` numeral invariants, pow2 packing paths at every chunk alignment (k=1..15), and the GIL-release boundary (`py.detach` with owned buffers only).
- **Tests, full or substantial read:** `conftest.py`, `test_backend_agreement.py`, `test_backend_dispatch.py`, `test_contract.py`, `test_differential.py`, `test_exact_arithmetic.py`, `test_frozen_kat.py`, `test_intermediates.py`, `test_interoperability.py`, `test_nist_vectors.py`, `test_pickle.py`, `test_properties.py`, `test_rust_aes_validation.py`, `test_smoke.py`, `test_thread_safety.py`, `test_validation.py`, `test_conversion_equivalence.py`, `_oracle/__init__.py`, `_oracle/generate_kat.py`, `_oracle/_m2crypto_shim.py`. Vector files listed (`tests/vectors/`); contents deliberately not re-derived (never regenerate fixtures).
- **CI/release, full read:** `.github/workflows/ci.yml`, `.github/workflows/publish.yml`, `.github/scripts/assert_installed_wheel.py`, `justfile`, `pyproject.toml`. Checked the publish gate reuses the full workflow (all jobs gate the release), artifacts published are the gated ones, the sdist allow-list and contents assertion, the `--locked` builds, the `-k rust` collection floor, and the import-origin checks.
- **Docs:** `README.md`, `SECURITY.md`, `CHANGELOG.md` (2.0.0rc2 section in full), `docs/architecture.md`, `docs/backlog.md`, `docs/configuration.md`, `docs/developer-guide.md` (CI section). Cross-checked published claims (perf tables, coverage wording, support policy, wheel platforms) against their recorded sources in the plan work log.
- **Plans/instructions:** `AGENTS.md`, `docs/AGENTS.md`, `docs/reviews/AGENTS.md`, `.agents/skills/allocating-report-numbers/` (used for this report's allocation), plan 00008 in full, plan 00007 requirements/work log via targeted search.
- **Prior reviews:** [[00007-V2_0_0_Stable_Release_Readiness|00007]] in full (its four findings re-tested), [[00009-Plan_00006_Re_Review|00009]] and [[00008-v2.0.0-plan-review|0008]] for finding history.

### Checks performed

- Target resolution: HEAD == `6fd3548` == caller's commit; branch `release/v2`; `git status --short` clean; `git ls-files` confirms no build artifacts tracked.
- Static spec-conformance reasoning over both cores (listed above), including boundary behaviour of the pow2 conversion paths, the truncation contracts, and the checked length encoding at `2**32`.
- Exception-hierarchy reasoning over the malformed-input sweep, redaction rules (no plaintext/key echo in messages), and the pickle trust boundary (`__getstate__`/`__setstate__` contract, legacy 1.x state shape).
- CI dependency-graph reasoning (reusable-workflow gating of `publish.yml`), plus consistency checks of docs claims against the plan work-log measurements.
- Version lock-step verified across `pyproject.toml`, crate manifest, and the contract test's normalisation rule.

### Checks not performed

- **No project code, tests, builds, linters, formatters, scanners, benchmarks, or generators were executed by this read-only reviewer.** All test counts, coverage figures, CI outcomes, and performance numbers cited are recorded evidence from the plans' work logs, not fresh results.
- No wheels or sdists were downloaded or imported; PyPI/crates.io were not queried; attestations were not verified.
- NIST/oracle fixtures were not re-transcribed from the standards; the oracle's own implementation was not audited.
- `uv.lock`, `rust/Cargo.lock`, `docs/directory-structure.md`, `CONTRIBUTING.md`, `.pre-commit-config.yaml`, and `.github/dependabot.yml` were not read line by line (no change since the last reviewing cycle flagged them; the dependabot config was verified in review 00007).
- No timing/side-channel measurements; no 4-GiB tweak experiment; plan work-log claims (CI run URLs) were accepted as recorded records, not re-fetched.

## Positive notes

- **The rc2 fixes are real and regression-pinned.** The `__setstate__` fix stores the backend and is guarded by a genuine legacy-payload round trip with the 1.1 attribute set frozen as a constant — the exact drift class cannot silently recur. The tweak ceiling is enforced in shared validation *and* defended in depth by a checked Rust conversion with its own boundary test.
- **The dual-backend evidence structure is unusually strong.** Per-round intermediates through a normalised trace bridge, direct same-input encrypt/decrypt agreement across key sizes/tweaks/lengths straddling the conversion threshold, a validated oracle, frozen oracle-derived KATs, exhaustive bijectivity, and the AST float scan — with `FPR_FF1_REQUIRE_RUST_BACKEND`/`FPR_FF1_REQUIRE_ORACLE` turning silent skips into collection errors.
- **The release gate verifies what it publishes.** Every native wheel is installed and exercised on its own platform/interpreter with an import-origin assertion; publishing reuses the full gate and uploads exactly the gated artifacts; the negative-control run demonstrates the gate has teeth end to end.
- **Claims calibration.** README/SECURITY/CHANGELOG statements checked against their recorded measurements; coverage wording distinguishes Python line coverage from Rust conformance; no FIPS, zeroization, or constant-time overclaims anywhere.

## External references

None. No web research was used for this review.

## Recommended next actions

1. **(Low, this report)** Update the `docs/backlog.md` Ongoing item to reflect rc2's publication and in-progress soak — fold into the next docs change on the branch.
2. **(Owner decision, open question 1)** Accept or widen the per-platform wheel subset depth; record the decision in the plan work log.
3. **(Plan 00007 STEP-12)** Owner to decide whether this report satisfies the independent re-review requirement or to commission a range-mode review with the STEP-10/11 evidence bundle attached.
4. **(Plan 00007 STEP-13/14)** Proceed to the final bump: fill the `SECURITY.md` placeholder from the tag date, rewrite the README roadmap row, verify `grep -rn "<v2.0.0 date"` is empty, and release per the approved steps. This review found no code impediment to that.

## Handoff

**Next step:** the codebase at `6fd3548` is approved as reviewed; the rc2→final path is documentation-and-process only. Hand the backlog one-liner to the next docs change, decide open question 1, then continue plan 00007 STEP-12→14.

### Disposition of review 00007 findings (re-tested at this snapshot)

| Prior finding | Disposition | Current evidence |
|---|---|---|
| `REV-00007-MAJ-01` — restored 1.x pickles lack `_backend` | **resolved** | `src/fpr_ff1/_ff1.py:371-376` stores the validated backend after `__dict__.update`; `tests/test_backend_dispatch.py:251-268` restores onto `FF1.__new__(FF1)`, `:271-328` round-trips a real serialised 1.1-format payload (legacy `__getstate__` monkeypatch, pinned attribute set, second serialisation cycle); `tests/test_pickle.py:112-122` asserts attribute parity on both backends. |
| `REV-00007-MED-01` — Rust wraps the tweak length | **resolved** | `_ff1.py:396-415` enforces the `2**32 - 1` ceiling for default and per-call tweaks before any computation, and `_ff1.py:91-105` rejects configured bounds above it (never clamps); `lib.rs:162-166` `encode_len_u32` is a checked conversion used for both `[n]^4` and `[t]^4` (`lib.rs:486-490`), with boundary tests in `tests.rs:154-171` and rejection tests in `test_contract.py:78-80` / `test_validation.py:170-182`. |
| `REV-00007-MED-02` — only one packaged native target executed | **resolved** | `ci.yml:352-385` `wheel-test-native` installs each of the five wheels on its own architecture (including Intel macOS via `macos-15-intel`) across Python 3.12/3.13/3.14 with an import-origin assertion; `ci.yml:438-472` `wheel-conformance-abi3` runs the full suite at the 100% floor against the installed abi3 wheel; plan 00007's STEP-07 negative-control run (recorded `35150890829`) shows all sixteen wheel jobs failing on a deliberate S-expansion defect while the pure matrix stays green. |
| `REV-00007-LOW-01` — dual-backend sweep incomplete | **resolved** | The flagged cases now run through `ff1_factory`: long tweaks (`test_validation.py:339-346`), `IntEnum`/`__index__` acceptance and normalisation (`:411-445`), bytes-like keys/tweaks and mutable-buffer snapshots (`:480-528`), tweak-bound interoperability (`test_interoperability.py:109-124`), plus a new direct same-input agreement module (`test_backend_agreement.py`). Remaining direct `FF1(...)` constructions are constructor-validation tests, Python-only `Sequence`-protocol tests, or backend-selection tests — the distinction review 00007 itself drew. |

Review 00007's open questions: #1 (rc2 optimisation) resolved by plan 00007 STEP-04 with measured results and the park rule applied; #2 (negative-control CI evidence) resolved by run `35150890829`; #3 (glibc floor) documented in README/configuration; #4 (1.x support window) resolved by user decision D4 Option A, transcribed into `SECURITY.md` with the date placeholder scheduled for STEP-13; #5 (artifact provenance) remains release-verification work for the final release, unchanged in substance.

Plan-level predecessors: `REV-00008/00009-MAJ-01` (D4 support window) — **resolved** (user decision 2026-09-16, Option A transcribed verbatim; the literal date placeholder is by design, see open question 2).

## Confidence

**High.** Both algorithm cores, the full validation layer, the release pipeline, and the maintained documentation were read in full and cross-checked against the normative spec and the repository's own invariants; the single finding is documentation staleness with direct git-history evidence. The principal residual uncertainties are the ones inherent to a read-only review: no tests or builds were executed here (all cited outcomes are recorded work-log evidence), and the vector files were accepted on their documented provenance rather than re-derived.
