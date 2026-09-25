---
title: "Code Review 00013: Release V2 Comprehensive Re Review"
aliases:
  - "Review 00013"
tags:
  - code-review
  - software-quality
  - opencode
  - release-readiness
type: code-review
status: open
review_id: "00013"
reviewed_at: "2026-09-25T15:03:20Z"
reviewer_agent: review
review_model: "openai/gpt-6-astra"
triggered_by: "user"
review_kind: re-review
previous_review: "[[00012-Release_V2_Branch_Review]]"
repository: "joelee/fpr-ff1"
branch: "release/v2"
review_mode: branch
pr_reference: null
commit: "0fe89eac31cf5b7281de095f506559c4882f00d2"
base_ref: "origin/main"
base_commit: "b10d3b0e88a425e424b040a925de43364f5ae08d"
head_ref: "release/v2"
head_commit: "0fe89eac31cf5b7281de095f506559c4882f00d2"
scope: "merge-base(origin/main, release/v2)..0fe89ea, excluding docs/reviews/**; supplemental v2.0.0rc1..v2.0.0rc2 product diff and bounded release-readiness context at HEAD"
related_plan: "docs/plans/00007-Stable_v2.0.0_Release.md"
files_changed: 5
files_reviewed: 46
diff_additions: 782
diff_deletions: 11
blocking_issues: 0
issues:
  critical: 0
  major: 0
  medium: 1
  low: 0
  info: 0
  total: 1
categories:
  compatibility: 1
verdict: approve-with-comments
review_complete: true
web_research_used: true
confidence: medium
sources:
  - https://doc.rust-lang.org/std/primitive.slice.html#method.as_chunks
  - https://csrc.nist.gov/pubs/sp/800/38/g/r1/2pd
---

# Code Review 00013: Release V2 Comprehensive Re Review

> [!abstract] Verdict: `approve-with-comments`
> No Critical or Major defect was established in the release implementation; one new Medium issue concerns the future crate plan's incompatible minimum Rust version, not the v2.0.0 binaries. Proceed with release preparation only after recording dispositions for the existing Low findings and completing the exact-final-commit release gates.

## Review target

| Field | Value |
|---|---|
| Review mode | Branch, with supplemental candidate-range and release-readiness inspection |
| PR or commit | `0fe89eac31cf5b7281de095f506559c4882f00d2` |
| Base | Inferred default branch `origin/main` = `895c63350e33a17ffa8719b55a2c861baaf24942`; merge base = `b10d3b0e88a425e424b040a925de43364f5ae08d` |
| Head | `0fe89eac31cf5b7281de095f506559c4882f00d2`, verified equal to local HEAD |
| Branch | `release/v2` |
| Triggered by | User: comprehensive current-branch review before preparing v2.0.0 |
| Related plan | [[../plans/00007-Stable_v2.0.0_Release]]; newly added [[../plans/00008-Publish_Rust_Crate_To_Crates_io]] |
| Previous review | [[00012-Release_V2_Branch_Review]], already present as an untracked report when this review began |
| Working-tree scope | No staged or unstaged tracked changes. The pre-existing untracked report 00012 is context only; review reports are excluded as change targets. |

### Comparison boundaries

The request names the **current branch**, identifying its head by commit, rather than asking only for the final commit's first-parent patch. The inferred branch comparison is therefore `b10d3b0..0fe89ea`. Its raw Git statistics are seven files, 1,531 additions and 11 deletions. Excluding the two added review reports leaves the five files and 782/11 statistics recorded in front matter: README, plans 00007/00008, and the interoperability/validation test modules.

That comparison alone would miss the actual release-code changes, because rc2 is already incorporated into the local default-branch reference. Accordingly, the review also inspected the complete **product, test, packaging, CI, and maintained-document diff** in `v2.0.0rc1..v2.0.0rc2`: 22 files, 1,071 additions and 109 deletions. The peeled tag commits are:

- rc1: `89c74b70df569a30adabbffe5a57893a1bd5e514`.
- rc2: `b10d3b0e88a425e424b040a925de43364f5ae08d`.

The supplemental range excludes historical plan/agent-system changes, not product-code hunks. Both runtime cores and the relevant surrounding components were read at HEAD. Git confirms no rc2-to-HEAD difference in `src/`, `rust/`, `.github/`, `pyproject.toml`, or `uv.lock`. No remote was fetched, so remote-tracking refs are local evidence, not a claim about the latest server state.

## Executive summary

**The release implementation has no newly established merge-blocking defect.** The Python and Rust round construction remains consistent under static inspection, including odd-length splits, exact-integer sizing, CBC-MAC, S expansion, inverse-round subtraction, and the conversion optimization. The rc1 legacy-pickle defect is actually repaired, the tweak-length encoding limit is enforced before backend dispatch, and the release workflow now installs every native wheel on its corresponding platform and exercises the shipped abi3 configuration.

The branch-head migration correction is sound for the documented zero-sentinel and positive-bound configurations: `twk_max_len or None` preserves legacy unbounded maximum semantics without changing the new API's literal-zero policy. The installed legacy source was read to confirm that it applies its maximum only when positive. The new tests exercise the corrected recipe through both-backend fixtures and would reject the old direct-copy mapping for a non-empty tweak.

One **new Medium planning/compatibility finding** remains: plan 00008 fixes an MSRV of Rust 1.87 while requiring movement of an existing core that calls `slice::as_chunks`, stabilized in 1.88. Resolve that before executing the future crate plan. Plan 00008 explicitly starts after v2.0.0 publication, and the present extension uses the stable toolchain channel rather than declaring Rust 1.87 support; this is **not a reason to hold the v2.0.0 Python/native artifacts**.

Five previously reported Low issues remain open and are classified in Handoff, not republished as new discoveries. The sole Medium finding from review 00011 is resolved. The four original release-code findings from review 00007 are resolved in source/test/workflow definitions; execution and publication evidence is separately identified below as builder-reported.

This is approval to continue preparation, **not to tag this exact tree as v2.0.0**: both manifests still identify rc2, and final version/lock/documentation updates and release verification are intentionally outstanding.

## Issue summary

Counts below and in front matter describe findings newly recorded by this report. The five carried-forward Low issues retain their original identifiers in Handoff; zero new Low findings does not mean those issues were fixed or waived.

| Severity | Count | Merge impact |
|---|---:|---|
| Critical | 0 | Blocks merge/release |
| Major | 0 | Blocks merge/release |
| Medium | 1 | Changes requested before executing the affected future plan |
| Low | 0 | Non-blocking |
| **Total** | **1** | **No Critical/Major blocking findings** |

## Findings

### Medium

#### REV-00013-MED-01 — The new crate plan chooses an MSRV below an API already used by the core it will move

> [!warning] Changes requested — future crate delivery
> This affects plan 00008 execution and its promised Rust compatibility, not the currently prepared v2.0.0 wheel release.

- **Confidence / category:** High; Compatibility / delivery correctness.
- **Location:** `docs/plans/00008-Publish_Rust_Crate_To_Crates_io.md:139` — decision D8; implementation at `:410` and `:431`; affected existing symbol `rust/fpr-ff1-rust/src/lib.rs:103-120` — `prf`, specifically line 112.
- **What:** D8 requires `rust-version = "1.87"` and an MSRV CI leg, reasoning from the stabilization versions of `is_multiple_of`, `repeat_n`, and `div_ceil`. It omits the existing `data.as_chunks::<16>()` call. Official Rust documentation marks `slice::as_chunks` as stable since **1.88.0**. STEP-01 explicitly moves the PRF into the new core; no compatibility rewrite is specified.
- **Evidence:**

  ```rust
  // Existing prf body that STEP-01 moves into the published core.
  for block in data.as_chunks::<16>().0 {
      for (slot, byte) in chain.iter_mut().zip(block) {
          *slot ^= byte;
      }
  }
  ```

- **Failure scenario / impact:** A builder follows the approved split and D8 literally, retaining this PRF and declaring Rust 1.87 support. The core cannot compile on that compiler, so the mandatory MSRV job fails even if all current-stable conformance jobs succeed. Disabling that job would instead publish incorrect compatibility metadata for users on the advertised minimum. This creates avoidable rework and a concrete compiler-compatibility break in the future delivery.
- **Suggested fix:** Resolve the decision through the repository's approved-plan/superseding-plan process before implementation. Either choose an MSRV of **at least 1.88**, checking dependency floors too, or explicitly authorize a behavior-preserving replacement of this call with an older stable API such as `chunks_exact(16)`, then verify the intended lower floor. Do not silently override a frozen decision or weaken the MSRV gate. No current-release code edit is requested by this report.
- **Suggested verification:** An authorized builder should compile/test the split core and its doctests with the exact declared minimum compiler and locked dependencies. Also run the PRF/AES and full dual-backend conformance checks if the iteration API is changed. This reviewer did not compile a reproduction.
- **References:** Repository evidence; Rust standard-library documentation, `slice::as_chunks`, accessed 2026-09-25 [R1]. The sourced fact is the stabilization version; the resulting plan/compiler conflict is the review inference.

## Open questions

1. **Owner dispositions before final promotion.** Plan 00007 STEP-12 requires remaining findings to be fixed or accepted with reasons. No such disposition for the five carried-forward Low findings is established by the reviewed work log. Record individual decisions, rather than inferring acceptance from earlier `approve` verdicts.
2. **Exact final-source and artifact evidence.** The plan records successful rc2 runs and post-publication checks, but the final version-bump commit does not yet exist. Its CI, audit, package-content, installed-artifact and attestation checks must be tied to that final commit. This review does not replace them.
3. **Soak completion and STEP-12 bookkeeping.** The owner statement is “soak until 2026-09-25”; the work log still labels STEP-12 blocked (`docs/plans/00007-Stable_v2.0.0_Release.md:751,796`). Record the owner's interpretation/completion of that gate and acceptance of this report. This report supplies the previously missing rc1-to-rc2 product-diff inspection, but does not itself update or waive process gates.
4. **Minimum-platform compatibility remains artifact evidence.** The native-wheel test matrix uses current compatible runners, not every advertised minimum OS version. No lower-platform failure was established; published wheel dependencies and baseline-runtime checks, if required for those promises, remain release verification rather than a static-source conclusion.

## Review coverage

### Files and areas reviewed

**46 repository product/configuration/criteria files counted**, excluding instruction guides, prior review reports, and the two local installed-oracle files. All five primary changed files were inspected, including all of the newly added plan 00008. Count breakdown:

| Area | Count | Files / extent |
|---|---:|---|
| Runtime and native unit tests | 5 | Full `src/fpr_ff1/{__init__.py,_exceptions.py,_ff1.py}`; full `rust/fpr-ff1-rust/src/{lib.rs,tests.rs}` |
| Python tests and infrastructure | 20 | Full `tests/conftest.py`; `test_backend_agreement.py`, `test_backend_dispatch.py`, `test_contract.py`, `test_conversion_equivalence.py`, `test_differential.py`, `test_exact_arithmetic.py`, `test_frozen_kat.py`, `test_intermediates.py`, `test_interoperability.py`, `test_nist_vectors.py`, `test_pickle.py`, `test_properties.py`, `test_rust_aes_validation.py`, `test_sequence_validation.py`, `test_smoke.py`, `test_thread_safety.py`, `test_validation.py`; `tests/_oracle/{__init__.py,_m2crypto_shim.py}` |
| Build/release configuration | 9 | Full `.github/workflows/{ci.yml,publish.yml}`, `.github/scripts/assert_installed_wheel.py`, `.github/dependabot.yml`, `pyproject.toml`, `justfile`, `rust-toolchain.toml`, `rust/Cargo.toml`, `rust/fpr-ff1-rust/Cargo.toml` |
| Maintained documentation and criteria | 9 | README, SECURITY, architecture, backlog, configuration, developer guide, plans 00007/00008 in full; CHANGELOG current release sections and complete supplemental diff |
| Lock files | 2 | Complete candidate-range diffs; full `rust/Cargo.lock`; `uv.lock` current runtime/project entries and metadata, not every distribution hash |
| Measurement harness | 1 | Full `benchmarks/timing.py`; measurements not repeated |

Additional context: root and applicable docs/review instructions; prior reports 00010–00012 and review 00007's findings/release criteria. The local `ubiq_security_fpe/ffx.py` and `ff1.py` were read for the maximum-tweak convention; no dependency code was executed.

### Checks performed

- **Target/diff integrity:** resolved HEAD, branch, default reference, merge base and candidate tags; inspected staged/unstaged diffs and untracked status; inspected all primary non-review changes and all 22 supplemental product-file diffs. Rechecked HEAD/status before publication.
- **FF1 correspondence:** traced every public operation through type normalization, bounds, sequence materialization, alphabet mapping and backend dispatch. Compared Python/Rust `b` from `v`, exact bit lengths, P/Q encodings, padding, zero-IV PRF, S counter starting at one, byte truncation, ten rounds, parity/modulus choice and swaps. Rust decrypt's `A + modulus - (y % modulus)` form avoids unsigned subtraction underflow for validated inputs.
- **Conversion reasoning:** checked the 64-digit dispatch threshold, recursive split lengths and power caches, leading-zero preservation and truncation. Power-of-two grouping uses at most 120 bits per accumulator for the supported k=1..15 range, fitting the Rust `u128`; the conversion helpers remain call-local and retain reference loops.
- **Compatibility and failure boundaries:** examined legacy restoration onto uninitialized objects, current pickle/deepcopy/spawn tests, key/tweak snapshots, oversized tweak rejection and the corrected legacy-zero translation. Supported public calls validate before entering the native core; private `_rs` hooks are not treated as a supported independent Rust API.
- **Test capability:** inspected known-answer consumers, all-round trace assertions and their native bridge, direct arbitrary-input decrypt comparisons, oracle-required/native-required collection guards, exhaustive bijectivity and conversion equivalence tests. Reconfirmed the previously reported sensitivity/concurrency assertion weaknesses rather than treating line coverage as correctness proof.
- **Release gate:** followed reusable-workflow dependencies, isolated wheel environments, per-target artifact downloads, the 15 platform/interpreter legs and full installed-abi3 leg, tag/version comparison, and publication of downloaded gated artifacts rather than rebuilt ones. Dependency changes in the supplemental range are only project version entries; no new runtime dependency is introduced.
- **Claims and criteria:** checked README performance rows against recorded benchmark values, Python-versus-Rust coverage wording, support-policy finalization tasks and version lock-step. The NIST publication page still identifies the February 2025 second public draft; no baseline change was established by that lookup [R2].
- **Applicable lenses:** correctness, confidentiality/privacy boundaries, ciphertext integrity/interoperability, serialization, concurrency/reliability, performance, packaging/supply chain, tests and material maintainability. Database migrations, web authentication/tenant isolation, SQL/HTTP injection and UI concerns do not apply to this standalone library.

### Available execution records — not newly verified results

The current plan work log is more complete than the snapshot reviewed in report 00011:

| Recorded evidence | Repository location | Interpretation |
|---|---|---|
| Candidate CI run `35158807685` at `b10d3b0`, recorded 36/36 successful jobs | Plan 00007 line 860 | Includes the native matrix and full installed-abi3 conformance; builder-reported, logs not independently retrieved here |
| Release run `35402901107`, recorded 37/37 successful jobs | Plan 00007 line 862 | Rc2 publication record, not a final-v2.0.0 gate |
| Seven published files, matching artifact digests, verified attestations, installed-native and sdist checks | Plan 00007 lines 863–867 | Useful provenance record; this reviewer did not download or independently verify the files |
| S-expansion negative-control run `35150890829` | Plan 00007 line 847 | Recorded native jobs red and pure-Python jobs green; evidence not re-executed |
| Migration correction: recorded 1,688 passing dual-backend tests, 100% Python coverage and 16 Rust unit tests | Plan 00007 lines 868–869 | Builder-reported checkpoint, not a new result from this review |

The per-platform subset's two failing test functions under the S-expansion mutation must not be confused with only two vector shapes: the frozen-KAT test loops over its fixture set. No new finding about that subset's adequacy was established.

### Checks not performed

- **No project code, tests, collection, builds, linters, formatters, scanners, hooks, package managers, migrations, benchmarks or repository scripts were executed.** No passing-test claim in this report originates from a reviewer run.
- No binary import, wheel/sdist build or unpacking, minimum-platform execution, memory-pressure experiment, independent cryptographic audit, side-channel assessment or formal equivalence proof.
- No live CI-log/attestation verification or remote-ref refresh. Final release provenance and registry state were not independently checked.
- Unchanged vector JSON was not retranscribed, recomputed or independently audited byte by byte; the review inspected its consumers and preservation in the diff. The dependency implementations/advisory universe were not exhaustively audited.
- Historical pre-rc1 changes and internal agent/report-allocation automation were not re-audited. Future crate publication was reviewed as newly added plan text, not as implemented functionality.
- No `.codegraph/` index exists in this checkout, so source was read directly. The native skill tool requested by the caller is not exposed in this session; no skill invocation is claimed. Publication uses the reviewing agent's explicit atomic-lock procedure, not execution of a repository allocation script.

These are limits of a static source review, not inaccessible portions of its declared change scope. They prevent treating `review_complete: true` as certification of final artifacts or completion of plan 00007.

## Positive notes

- The migration correction preserves the new API rather than silently redefining zero, and its regression case actually exercises the published mapping.
- Legacy restoration now stores the backend on an uninitialized object; the regression test checks both state shape and operations, not merely a constructor-populated attribute.
- Native arithmetic changes retain simple reference routines and use per-call caches and owned buffers across GIL release.
- Installed-wheel origin checks and the full abi3 suite materially improve assurance that CI tests what the release workflow publishes.

## External references

- **[R1] “Primitive Type slice — as_chunks,” Rust standard-library documentation, Rust project.** Living documentation; update date not stated. The API is labeled stable since **1.88.0**. Accessed **2026-09-25**. <https://doc.rust-lang.org/std/primitive.slice.html#method.as_chunks>
- **[R2] “SP 800-38G Rev. 1 (2nd Public Draft): Recommendation for Block Cipher Modes of Operation: Methods for Format-Preserving Encryption,” NIST CSRC.** Published **2025-02-03**. Accessed **2026-09-25**. Used for draft status and the headline minimum-domain/FF1-only/forward-AES/no-float baseline, not a fresh derivation of every algorithm step. <https://csrc.nist.gov/pubs/sp/800/38/g/r1/2pd>

## Recommended next actions

1. **Record the release-review dispositions.** Address or explicitly accept the five existing Low findings below. Correct the work-log's wrong migration-finding identifier and update the stale backlog in the authorized documentation work. Record the soak decision and this report's STEP-12 role.
2. **Keep plan 00008 separate from stable 2.0 preparation.** Resolve `REV-00013-MED-01` through an authorized plan revision/superseding plan before that future implementation starts; do not change the current FF1 core merely to satisfy a future MSRV decision.
3. **Complete STEP-13:** bump Python and Cargo manifests together to `2.0.0`; refresh only intended lock edges; add the dated final changelog section and comparison links; finalize the README roadmap and `SECURITY.md:23,29` support dates. Repeat the NIST status check at final freeze if publication occurs later.
4. **Complete the exact-source gate and merge/tag sequence:** preserve the recorded merge-to-main decision at plan 00007 line 815, freeze the final commit, and obtain the complete CI/local/package/audit evidence for it. Do not tag `0fe89ea` as v2.0.0 while its manifests still say rc2.
5. **Owner publication and post-publication verification:** publish the non-prerelease only through the gated workflow, then verify all seven files, artifact digests/attestations, both-backend known-answer behavior, pure fallback and default non-prerelease resolution. Leave published candidate artifacts and old reports untouched.

## Handoff

**Current branch:** suitable for continued release preparation with the comments above. **Release-blocking code findings:** none established. **Stable-release process:** remains the owner's responsibility; this report does not approve a tag or claim final artifacts exist.

### Disposition of previous findings

Each classification below follows current source inspection, not merely a prior report's assertion. Existing Low findings are retained under their original IDs to avoid inflating the new issue count.

| Prior finding | Classification | Current evidence / next action |
|---|---|---|
| `REV-00012-LOW-01` — wrong migration-finding identifier in the work log | **still-open** | Plan 00007 lines 797 and 816 still name `REV-00010-MED-01`; the actual finding is `REV-00011-MED-01`. Correct those references in an authorized work-log update. |
| `REV-00011-MED-01` — legacy zero maximum mistranslated | **resolved** | `README.md:428-437,445,465-470` translates zero to `None`; `tests/test_interoperability.py:111-164` follows that recipe; `tests/test_validation.py:185-199` preserves empty-only literal-zero semantics. The local legacy source applies the maximum only when positive. |
| `REV-00011-LOW-01` — released memoryview bypasses typed errors | **still-open** | `_require_bytes` at `src/fpr_ff1/_ff1.py:116-122` still calls `bytes(value)` without translating an invalid released-buffer `ValueError`. Fix narrowly with sanitized key/tweak-specific errors and regressions, or explicitly accept the edge case. |
| `REV-00011-LOW-02` — ineffective tweak-sensitivity property | **still-open** | `tests/test_properties.py:98-105` still skips on equal outputs and has no failing sensitivity assertion. Its companion key check at line 122 still assumes a universal single-input inequality. Use independent exact cases/appropriate mutation verification rather than declaring legal collisions impossible, or record acceptance. |
| `REV-00011-LOW-03` — concurrency tests discard intermediate results | **still-open** | `tests/test_thread_safety.py:79-93,111-127` overwrites each worker slot twenty times and compares only the last result. Verify every iteration or retain the first mismatch; an early-wrong/last-correct test double should fail. No actual runtime race was established. |
| `REV-00010-LOW-01` — stale release progress in backlog | **still-open** | `docs/backlog.md:14-15` still describes rc2 publication as outstanding while the current work log records publication/verification. Update it during the next authorized release-documentation change. |
| `REV-00007-MAJ-01` — missing backend in legacy restoration | **resolved** | `src/fpr_ff1/_ff1.py:360-380` stores the validated/default backend. `tests/test_backend_dispatch.py:251-328` restores onto an uninitialized object and exercises real legacy-format serialization and all operations. |
| `REV-00007-MED-01` — wrapped tweak-length encoding | **resolved** | Shared checks at `_ff1.py:91-105,395-415`; checked native lengths at `lib.rs:162-166,489-490`; boundary cases at `tests/test_validation.py:98-182` and native unit tests `tests.rs:151-170`. |
| `REV-00007-MED-02` — unexecuted native wheel targets | **resolved** in workflow definitions | `.github/workflows/ci.yml:352-472` defines all 15 native legs and full installed-abi3 conformance; the separate origin assertion rejects checkout imports. Actual run outcomes remain the builder-reported records above. |
| `REV-00007-LOW-01` — omitted accepted-input backend cases | **resolved** for the seven identified cases | The named acceptance/normalization/long-tweak/mutable-buffer cases in `tests/test_validation.py` and bounded interoperability at `tests/test_interoperability.py:167-182` now use `ff1_factory`. This does not assert that every test anywhere in the repository is dual-parameterized. |

This re-review extends report 00012 with the candidate product-range inspection and the new future-plan compatibility finding. It does not alter any prior report or mark existing Low findings accepted on the owner's behalf.

## Confidence

**Medium overall; high for the specific MSRV conflict and source-level dispositions.** The five-file branch change and complete supplemental release-product diff were accessible, both runtime implementations were read in full, and the documented migration semantics were checked against local dependency source. The principal uncertainty is execution/artifact assurance: no code was run and the recorded CI, benchmarks and publication checks were not independently reproduced or verified.
