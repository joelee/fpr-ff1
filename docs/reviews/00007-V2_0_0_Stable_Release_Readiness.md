---
title: "Code Review 00007: V2.0.0 Stable Release Readiness"
aliases:
  - "Review 00007"
  - "V2.0.0 stable release checklist"
tags:
  - code-review
  - software-quality
  - opencode
  - release-readiness
type: code-review
status: open
review_id: "00007"
reviewed_at: "2026-09-09T13:36:20Z"
reviewer_agent: review
review_model: "openai/gpt-6-astra"
triggered_by: "user"
review_kind: re-review
previous_review: "docs/reviews/00006-v2.0.0rc1-Claude_Fable.md"
repository: "joelee/fpr-ff1"
branch: "main"
review_mode: repository
pr_reference: null
commit: "89c74b70df569a30adabbffe5a57893a1bd5e514"
base_ref: "v1.1.0"
base_commit: "67cf45a19131b46cce70ec83a61a6e0b82e94770"
head_ref: "v2.0.0rc1"
head_commit: "89c74b70df569a30adabbffe5a57893a1bd5e514"
scope: "v1.1.0..v2.0.0rc1, plus bounded repository-wide stable-release readiness review at the tagged HEAD; docs/reviews excluded as change targets"
related_plan: "docs/plans/00005-Review_00006_v2.0.0rc1_Hardening.md"
files_changed: 44
files_reviewed: 49
diff_additions: 3971
diff_deletions: 173
blocking_issues: 1
issues:
  critical: 0
  major: 1
  medium: 2
  low: 1
  info: 0
  total: 4
categories:
  correctness: 1
  data-integrity: 1
  tests: 2
verdict: request-changes
review_complete: true
web_research_used: true
confidence: medium
sources:
  - https://docs.python.org/3/library/pickle.html
  - https://csrc.nist.gov/pubs/sp/800/38/g/r1/2pd
  - https://www.maturin.rs/distribution.html
  - https://doc.rust-lang.org/cargo/commands/cargo-build.html
  - https://pypi.org/pypi/fpr-ff1/2.0.0rc1/json
  - https://github.com/joelee/fpr-ff1/pull/8
  - https://github.com/joelee/fpr-ff1/actions/runs/34345720285
---

# Code Review 00007: V2.0.0 Stable Release Readiness

> [!abstract] Verdict: `request-changes`
> The earlier release-hardening findings are addressed in the source, but an actual 1.x pickle restoration is broken; repair that compatibility regression and finish the boundary, artifact-validation, and release tasks below before publishing stable `v2.0.0`.

## Review target

| Field | Value |
|---|---|
| Review mode | Bounded repository-wide release-readiness review, including the complete relevant 2.0 release diff |
| PR or commit | `89c74b70df569a30adabbffe5a57893a1bd5e514` |
| Base | `v1.1.0` → `67cf45a19131b46cce70ec83a61a6e0b82e94770` |
| Head | `v2.0.0rc1` → `89c74b70df569a30adabbffe5a57893a1bd5e514` |
| Branch | `main`, initially clean; no staged, unstaged, or relevant untracked changes |
| Triggered by | User: comprehensive review of current `v2.0.0rc1` and tasks for stable `v2.0.0` |
| Related plan | `docs/plans/00005-Review_00006_v2.0.0rc1_Hardening.md`; original backend requirements in plan 00003 |
| Previous review | [[00006-v2.0.0rc1-Claude_Fable]] |

**Target resolution matters here:** the annotated tag object is `cab566257fc355de46e3144eb879506183b07862`, but its peeled commit is the current HEAD, `89c74b7`. This is **not** the earlier candidate commit `54a6dc0` reviewed in report 00006. The current tag contains the hardening merge and the packaging 26.3 development-dependency update. `git diff v2.0.0rc1 HEAD` is empty. No clarification was necessary because the current source and the tag coincide.

The comparison base is inferred as the last stable 1.1 release, not the tag's first parent: the caller requested readiness of the whole release, rather than review of its final dependency-bump commit. The bounded audit covers both algorithm implementations, public Python interfaces, validation, serialization, concurrency, relevant tests, packaging, CI/publishing, dependency controls, and maintained release documentation. It is not a cryptographic certification or an exhaustive audit of dependency implementations.

## Executive summary

**Do not promote rc1 by changing only the version strings.** There is one blocking compatibility defect and three smaller actionable findings:

1. **Major — restored 1.x instances lack `_backend`.** `__setstate__` computes a default but never stores it. Real unpickling bypasses `__init__`, so subsequent encryption and decryption raise `AttributeError`. The regression test accidentally supplies the missing attribute by constructing its destination normally.
2. **Medium — an oversized tweak is silently narrowed by the Rust core.** Shared validation has no absolute limit matching the four-byte tweak-length field. At 4 GiB and above, Rust wraps the length while Python refuses to encode it. This is an extreme-input backend-parity and fail-closed defect, not evidence of wrong ciphertext for ordinary tweaks.
3. **Medium — four of the five native wheel targets are never installed or executed by the release gate.** Full conformance now runs, but on a Linux source-tree build; only the Linux x86_64 packaged wheel receives a runtime smoke test. The abi3 distribution build also uses a different PyO3 feature configuration from the full-conformance build.
4. **Low — some acceptance and normalization tests remain Python-only**, contrary to the new dual-backend testing rule.

The underlying FF1 code is substantially stronger than the previous report's release gate. Both cores visibly preserve the important invariants: exact integer `b` from `v`, ten rounds, zero-IV CBC-MAC, the correct S expansion, byte truncation, and the same parity rule in both directions. Rust now expands the AES key once per call and detaches from Python while operating on owned Rust buffers. No new shared cipher state was found. The Python arithmetic core is unchanged from 1.1.0.

### Evidence available now

- GitHub's PR #8 check rollup reports **all 21 checks successful**, including full Rust conformance, dependency audit, the nine Python/OS legs, wheel builds, and the three distribution smoke jobs, in run `34345720285`. This is PR-check evidence, not independently inspected logs for the final release event.
- Plan 00005's work log records **1,406 passing tests, 100% Python line/branch coverage, and eight Rust unit tests** for its hardening verification. These are historical builder-reported results; this reviewer did not execute or independently reproduce them.
- The PyPI release JSON confirms **rc1 is already published**, not yanked, with **seven files**: five `cp312-abi3` platform wheels, one `py3-none-any` wheel, and one sdist. Uploads are dated 2026-09-09, approximately 12:52 UTC. Metadata declares Python `>=3.12`, MIT, and the sole Python runtime dependency `cryptography>=50.0.0`.
- Linux wheels actually published are tagged **`manylinux_2_34`** for x86_64 and aarch64. The two macOS tags are `macosx_10_12_x86_64` and `macosx_11_0_arm64`; Windows is `win_amd64`. These are artifact-selection facts, not proof that all supported runtime combinations work.
- The NIST page still labels Rev. 1 as the **second public draft**, published February 3, 2025, and describes the increased minimum domain, removal of FF3, forward-AES requirement, and prohibition of floating-point FF1 implementations. No baseline change was established by that status check.

### What remains beyond defect fixes

Two existing commitments must not disappear during promotion: the **Rust divide-and-conquer work targeted at rc2** in `docs/backlog.md:14-17`, and **plan 00005 AC-02's deliberate-break CI evidence**, explicitly still outstanding in its completion summary. The optimization is a roadmap commitment, not an intrinsic requirement for correct FF1: an owner-authorized deferral can remove it from this release, but this review does not make that decision.

## Issue summary

| Severity | Count | Merge impact |
|---|---:|---|
| Critical | 0 | Blocks merge/release |
| Major | 1 | Blocks merge/release |
| Medium | 2 | Changes requested |
| Low | 1 | Non-blocking |
| **Total** | **4** | |

## Findings

### Major

#### REV-00007-MAJ-01 — Real 1.x pickles restore without the backend required by every operation

> [!warning] Blocking
> - **Confidence:** High
> - **Category:** Correctness / compatibility
> - **Location:** `src/fpr_ff1/_ff1.py:333-352` — `FF1.__setstate__`; `tests/test_backend_dispatch.py:251-261` — `test_legacy_pickle_state_defaults_to_python`.
> - **Evidence:** `__setstate__` copies the old state into `self.__dict__`, then computes `backend = state.get("_backend", "python")` and validates it, but never assigns `self._backend = backend`. There is no class-level default. Both `encrypt_numerals` and `decrypt_numerals` now read `self._backend` unconditionally at lines 484 and 506. The 1.1.0 implementation was inspected and its saved state contains no such field.
> - **Failure scenario:** An application serializes an ordinary FF1 instance under 1.0/1.1, upgrades to 2.0, and restores the trusted payload. Pickle creates an uninitialized instance and calls `__setstate__`, without calling `__init__`. Restoration appears to succeed, but either numeral method, and therefore either string method, then raises `AttributeError`. Persisted batch configuration or a previously serialized worker payload becomes unusable after upgrade.
> - **Impact:** A deterministic failure of the explicitly intended legacy-pickle compatibility path, even for callers that never request Rust. It contradicts the additive/no-existing-caller-affected framing. This does not demonstrate loss of ciphertext; reconstructing an instance from the original configuration is a workaround.
> - **Recommendation:** Persist the validated backend/default in the restored instance. Keep the existing fail-fast availability check for a saved Rust backend. Fix the regression test to restore onto `FF1.__new__(FF1)` rather than a destination already initialized with `_backend="python"`, and add an actual serialized legacy-state round trip.
> - **Suggested verification:** Restore representative 1.1-format states with and without an alphabet, non-empty default and per-call tweaks, and all supported key sizes. Assert `_backend == "python"`, exercise all applicable encrypt/decrypt methods, then pickle and restore again. Keep current-format Python and Rust round trips and missing-extension rejection covered. Use only public test keys; never commit real serialized key material.
> - **References:** Repository evidence; Python documentation, “Pickling Class Instances,” explicitly states that unpickling normally bypasses `__init__`.

The existing test hides the defect with this destination construction:

```python
del state["_backend"]
clone = FF1(key=_KEY, radix=10)  # Supplies the attribute real unpickling lacks.
clone.__setstate__(state)
assert clone._backend == "python"
```

The test exercises the default-selection line, so a 100% coverage result cannot detect the missing assignment.

### Medium

#### REV-00007-MED-01 — Rust wraps the tweak length where the reference refuses to encode it

> [!warning] Changes requested
> This requires an exceptionally large tweak; it is not a finding about ordinary FPE record lengths.

- **Confidence / category:** High static confidence; Data integrity / validation.
- **Location:** `rust/fpr-ff1-rust/src/lib.rs:284-301` — `ff1_impl`, P-block construction; `src/fpr_ff1/_ff1.py:367-371` — `FF1._validate_tweak`; reference encoding at `src/fpr_ff1/_ff1.py:803-814,908-914`.
- **What:** The constructor and `_prepare` validate only user-configured tweak bounds. With the defaults, a tweak whose length is at least `2**32` passes this gate. Rust casts that length to `u32`, silently discarding high bits, while Python's four-byte `int.to_bytes` raises `OverflowError`. Validation staying in Python does not establish parity when an encoding invariant is absent there.
- **Evidence:**

  ```rust
  let t = tweak.len();
  // ...
  p_block.extend_from_slice(&(t as u32).to_be_bytes());
  ```

  ```python
  # _validate_tweak checks configured min/max only.
  # The reference later encodes the actual length without truncating:
  + _encode_uint(t, 4)
  ```

- **Failure scenario / impact:** On a sufficiently large-memory 64-bit machine, a caller supplies a multi-gigabyte context blob as a tweak, with no maximum configured. For a length of exactly `2**32`, the Rust P field says zero while Q still includes the actual tweak. If the computation completes, the native backend produces output that the reference cannot reproduce or decrypt with the same parameters. Even where memory pressure prevents completion, the promised early, identical typed rejection is missing. This is not a claim that the entire tweak is discarded or that it collides with an empty tweak.
- **Suggested fix:** Enforce an absolute four-byte-encodable tweak-length ceiling (`2**32 - 1`) in shared Python validation for default and per-call tweaks; define how configured bounds interact with that ceiling without silently clamping. Add a checked Rust conversion as defense in depth. Document the actual limit and changed rejection behavior before stable 2.0; do not silently change existing ordinary-input ciphertext.
- **Suggested verification:** Test the numeric length boundary at `2**32 - 1`, `2**32`, and above without allocating gigabytes, using a factored length check or a test-only length double. Verify public-path ordering with a small test limit or controlled validation seam, identical `TweakLengthError` type/message on both backends, and an independent checked-encoding test in Rust. Retain real empty/short/long-tweak conformance cases.
- **References:** Repository encoding and no-silent-truncation/backend-parity contracts. No fresh interpretation of the unreadable PDF is required for the demonstrated divergence.

#### REV-00007-MED-02 — The release gate executes only one of the five packaged native targets

> [!warning] Changes requested
> A successful wheel build and metadata check are not runtime compatibility evidence.

- **Confidence / category:** High; Testing / release reliability.
- **Location:** `.github/workflows/ci.yml:329-373` — `wheel-test-platform`; related build at `.github/workflows/ci.yml:218-274`, full-conformance build at lines 107-126, and `pyproject.toml:105-108` — maturin features.
- **What:** Five targets are built and published, but the installation job is hard-coded to Ubuntu and downloads only `wheels-x86_64-unknown-linux-gnu`. Linux aarch64, both macOS variants, and Windows never import their built extensions in this gate. Moreover, the full suite uses plain `cargo build` and a source-tree copy, whereas distribution wheels enable `pyo3/abi3-py312` through maturin. Only the one Linux smoke vector currently exercises the packaged ABI configuration.
- **Evidence:**

  ```yaml
  wheel-test-platform:
    runs-on: ubuntu-latest
    needs: wheel-build
    # ...
    with:
      name: wheels-x86_64-unknown-linux-gnu
  ```

- **Failure scenario / impact:** A wheel with an import/linking defect, wrong deployment assumption, or an ABI-specific binding regression on one of the other targets can build and pass `twine check`, then be published. Selecting `backend="rust"` fails for that platform despite a green gate. The pure-Python fallback reduces impact, but does not validate the advertised optional backend. Plan 00003 REQ-20 specifically names wheel-build **and wheel-test** evidence on all decided platforms (`docs/plans/00003-Accelerated_Backend_Pure_Python_Then_Rust.md:534-546`).
- **Suggested fix:** Install each exact wheel artifact on a compatible runner, including a native Intel macOS runner or an explicitly configured compatible execution environment for the cross-built Intel wheel. Run an installed-package conformance subset on Python 3.12, 3.13, and 3.14; include published AES/FF1 KATs, both directions, and frozen/differential cases reaching `d > 16`. Also run the full conformance suite against at least the release-built abi3 wheel rather than relying exclusively on the source-tree extension.
- **Suggested verification:** Verify imports resolve to the clean environment's installed artifact, not an editable source tree. Check `py.typed`, public exports, distribution/extension versions, and both backends. Make every target's test job required by the publishing gate. Keep pure-wheel and sdist fallback checks separately.
- **References:** Workflow evidence; plan 00003 REQ-20; PyPI JSON confirms all five native targets are actually distributed.

### Low

#### REV-00007-LOW-01 — Complete the dual-backend sweep for accepted input shapes and tweak-bound interoperability

> [!note] Non-blocking test gap

- **Location:** `tests/test_validation.py:244-259,324-358,393-441` — tweak, integer-like, and mutable-buffer acceptance tests; `tests/test_interoperability.py:109-124` — `test_tweak_bounds_map_across_apis`; `AGENTS.md:124` — new dual-backend conformance rule.
- **What / why:** Several tests that perform real encryption still construct `FF1` directly, so they run only on Python even with the Rust-required flag set. In particular the real 4,096-byte tweak, `IntEnum`/`__index__`, bytes-like normalization, mutable-input snapshot, and configured-tweak-bound interoperability cases do not cross the new FFI boundary. Shared validation materially reduces risk, so this is Low rather than a claim that those accepted inputs are currently broken.
- **Suggested fix:** Parameterize backend-independent public acceptance/conformance cases through `ff1_factory` or `BACKENDS`, including the remaining interoperability case. Audit the remaining direct constructions and distinguish intentional Python-helper tests from public contracts; do not blindly parameterize tests of Python-only conversion internals or backend-selection tests.
- **Suggested verification:** Collection should show both backends for each selected public-contract case, and both should pass without changing the expected outcomes. A global `-k rust` count floor is not evidence that each required case was parameterized.
- **References:** Repository evidence; plan 00003 REQ-18 and the current agent contract.

## Open questions

1. **Will the recorded rc2 optimization ship before stable?** The user-approved deferral was “to rc2,” not “indefinitely.” The code still uses quadratic Rust `num_radix`/`str_radix`; this is honestly documented and is not re-raised as a performance defect. Resolve with an approved rc2 delivery scope, or explicit owner authorization to defer beyond 2.0 and update the active backlog accordingly.
2. **Where is plan 00005 AC-02's CI negative-control result?** Its work log at lines 639 and 648 explicitly says it was performed locally, not in CI. Supply the run showing the intended long-input mutation fails Rust conformance, or obtain an explicit acceptance-criterion waiver. Once installed-wheel conformance is expanded, those jobs should also fail the same mutation; do not insist that only one job can fail merely to preserve an obsolete expectation.
3. **What is the intended Linux binary compatibility floor?** Published rc1 native wheels require glibc 2.34 or newer by their tags. Hosts with an older glibc, or musl, must use the pure fallback. This is not treated as a defect because no lower floor was promised. Confirm that support decision and document it; if broader native coverage is wanted, use a chosen manylinux baseline/build environment rather than accidental host-derived compatibility.
4. **What security-support window is intended after final?** `SECURITY.md:22-29` simultaneously describes support until the next minor and lists both 1.0.x and 1.1.x supported. Decide the actual 1.x maintenance/backport window and replace the rc row with the final policy. This is a release-policy decision, not permission for the reviewer to drop supported users.
5. **Were the published files built from the exact tagged source and attested by the intended workflow?** Registry metadata confirms file presence, names, and reported digests, but this review did not retrieve/verify attestations or compare the remote binaries to CI artifacts. Preserve that as a release-verification task rather than assuming `core-metadata` or `has_sig` fields prove provenance.

## Review coverage

### Files and areas reviewed

**49 files counted:** 41 changed product/configuration/maintained-document files, two related plans inspected for applicable requirements and execution evidence, and six unchanged contextual files. Counts exclude review reports and directory instruction guides as reviewed product files. The 44-file diff statistic includes the superseded plan 00004; that historical draft was not audited as a release requirement.

- **Python runtime, full read:** `src/fpr_ff1/_ff1.py`, `src/fpr_ff1/__init__.py`, `src/fpr_ff1/_exceptions.py`. Also inspected the reference module at `v1.1.0` to validate serialization history and unchanged arithmetic.
- **Rust runtime/build, full read:** `rust/Cargo.toml`, `rust/Cargo.lock`, `rust/fpr-ff1-rust/Cargo.toml`, `rust/fpr-ff1-rust/src/lib.rs`, `rust/fpr-ff1-rust/src/tests.rs`, and the complete new `rust-toolchain.toml` diff.
- **Changed tests and fixtures:** `tests/conftest.py`, `test_backend_dispatch.py`, `test_contract.py`, `test_differential.py`, `test_exact_arithmetic.py`, `test_frozen_kat.py`, `test_intermediates.py`, `test_interoperability.py`, `test_nist_vectors.py`, `test_pickle.py`, `test_properties.py`, `test_rust_aes_validation.py`, `test_thread_safety.py`, and the complete added `tests/vectors/aes_kat_fips197.json` diff. Non-trivial test files were read in full, not just their changed assertions.
- **Build/release/dependencies:** `.github/workflows/ci.yml`, `.github/workflows/publish.yml`, `.github/dependabot.yml`, `pyproject.toml`, `justfile`, `.gitignore` diff, and `uv.lock` diff. Reviewed versions/features, source-vs-distribution separation, artifact naming/download dependencies, and OIDC permission placement.
- **Changed documentation/measurement:** `AGENTS.md`, `CLAUDE.md`, `README.md`, `CHANGELOG.md`, `SECURITY.md`, `benchmarks/timing.py`, `docs/architecture.md`, `docs/backlog.md`, `docs/configuration.md`, `docs/developer-guide.md`, `docs/directory-structure.md`.
- **Criteria:** plan 00005 read in full; plan 00003's relevant release changes, E2 requirements, verification strategy, acceptance criteria, and recorded execution outcomes inspected. Older plan history was not audited for process compliance.
- **Six unchanged contextual files:** `CONTRIBUTING.md`, `.pre-commit-config.yaml`, `tests/test_validation.py`, `tests/test_sequence_validation.py`, `tests/test_conversion_equivalence.py`, `tests/_oracle/__init__.py`.
- **Prior review:** report 00006 read in full and each of its nine findings independently revisited; older reviews searched for related boundary/serialization findings to avoid duplication.

### Checks performed

- Resolved local annotated tags to full commits; checked branch/status, staged and unstaged diffs, and the empty tag-to-worktree comparison. Rechecked HEAD before publication.
- Inspected relevant source, test, packaging, and documentation diffs against 1.1.0. Long tool outputs were read from their captured output files where needed; no product-code hunk was intentionally omitted due to truncation.
- Traced every public method through normalization/validation and dispatch; searched `_backend` and `__setstate__` references and inspected all serialization consumers/tests before reporting the missing field.
- Compared the two FF1 loops and CBC-MAC/S-expansion constructions statically, including odd/even splits, endianness, modular subtraction, integer widths, and owned-buffer lifetime across `Python::detach`.
- Inspected conformance fixtures' consumers, oracle availability behavior, the release job dependency graph, and source-tree versus abi3 build features.
- Obtained PR #8 check status with read-only `gh pr view`; checked current PyPI release metadata, official Python pickle semantics, NIST draft status, and maturin/Cargo distribution controls.
- Review lenses applied: correctness, compatibility, data integrity, security/privacy, concurrency/reliability, performance, supply chain, tests, and materially relevant maintainability. Database/schema migrations, network authentication/authorization, tenant isolation, service observability, and UI/accessibility are not applicable to this standalone library.

### Checks not performed

- **No project code, tests, builds, linters, formatters, security scanners, hooks, package managers, migrations, benchmarks, or generators were executed by this read-only reviewer.** Reported historic counts are not a fresh test result.
- No native artifacts were downloaded, unpacked, imported, or compared byte-for-byte; no CI job logs or release attestations were independently verified. Current GitHub evidence is the PR check rollup, not the final release-event run.
- The unchanged large NIST/oracle fixtures were not retranscribed or re-derived from the standards, and the oracle/AES/PyO3 dependency implementations were not independently audited. The NIST PDF fetch returned binary content rather than usable extracted text; no finding relies on interpreting that response. The readable NIST publication page was used only for the documented baseline/status.
- No timing side-channel assessment, target-specific hardware AES assessment, proof of bijectivity outside tested domains, or 4-GiB runtime experiment was performed.
- Ignored build outputs, caches, `.venv`, private consumer behavior, and the review/agent system itself are outside this bounded review. No secret stores or `.env` files were read.
- The requested native skill tool was unavailable in this tool set; no skill invocation or independent subagent execution is claimed.

These limits do not prevent a dependable **static source-review verdict**: MAJ-01 follows directly from the supported restoration contract, and the remaining findings have concrete source/workflow evidence. They do prevent treating this report as certification of the installed release artifacts.

## Positive notes

- **The old missing-Rust-gate blocker is genuinely corrected.** Required-extension collection, full conformance, `cargo test`, fmt, and clippy now participate in the reusable release gate. Fake-extension tests remain separate plumbing coverage rather than a replacement for real conformance.
- **The cryptographic implementation remains reviewable.** Rust mirrors the reference's steps rather than introducing an opaque alternative algorithm. The shared traced/untraced Rust loop avoids a second implementation that tests could accidentally validate instead of production.
- **Concurrency changes preserve ownership boundaries.** Inputs are normalized before dispatch; Rust receives owned buffers and an immutable, call-local key schedule. Both production bindings detach for the calculation.
- **Distribution design preserves the default.** Installing a native wheel does not automatically select Rust. The pure wheel/sdist, typed missing-backend error, and single Python runtime dependency remain intact.
- **Performance and security claims are mostly calibrated.** The README admits the long-input Rust slowdown, states a measured crossover band, and distinguishes thread safety from parallel speedup. The security text does not claim FIPS validation, key zeroization, or a constant-time Rust backend.

## External references

All sources below were accessed **2026-09-09**. Publication/update dates are included where exposed; undated living documentation is not assigned an invented date.

1. **“pickle — Python object serialization,” Python Software Foundation**, Python 3.14 documentation; living documentation, update date not established. Used for uninitialized-instance restoration and the trusted-pickle boundary. <https://docs.python.org/3/library/pickle.html>
2. **“SP 800-38G Rev. 1 (2nd Public Draft),” NIST CSRC**, published **2025-02-03**. Used for status and the four headline technical changes, not a complete independent re-derivation of FF1. <https://csrc.nist.gov/pubs/sp/800/38/g/r1/2pd>
3. **“Distribution,” Maturin User Guide, PyO3/maturin project**, living documentation, date not stated. Explains manylinux portability, compatibility tags, and available `--locked`/build options. <https://www.maturin.rs/distribution.html>
4. **“cargo build,” The Cargo Book, Rust project**, living documentation, date not stated. `--locked` fails if Cargo would change dependency resolution or the lock file is missing. Used for the release-control recommendation below, not an allegation of existing dependency drift. <https://doc.rust-lang.org/cargo/commands/cargo-build.html>
5. **`fpr-ff1` 2.0.0rc1 release JSON, PyPI / Python Software Foundation**, file uploads **2026-09-09**. Used for published file inventory, version, tags, dependency metadata, and yank status. Registry fields are not binary-conformance or provenance verification. <https://pypi.org/pypi/fpr-ff1/2.0.0rc1/json>
6. **PR #8 check rollup and CI run, GitHub / joelee/fpr-ff1**, checks completed **2026-09-09**. Retrieved through `gh pr view`; 21 successful check records returned. <https://github.com/joelee/fpr-ff1/pull/8> · <https://github.com/joelee/fpr-ff1/actions/runs/34345720285>

## Recommended next actions

### Stable v2.0.0 release task list

This is the requested release inventory, **not an approved implementation plan**. Tasks belong to the maintainer/Builder and release owner; this reviewer has performed none of the implementation or publication actions. Items are ordered by dependency. Existing safeguards are to be retained and verified, not rebuilt unnecessarily.

#### A. Fix the identified defects and complete the acceptance coverage

- [ ] **STABLE-01 — Repair legacy-pickle restoration (blocking).** Persist the validated/default backend in `FF1.__setstate__` and correct the test that currently initializes its destination. **Done when:** a real 1.1-format payload restores on an uninitialized object and all applicable operations plus a second serialization cycle succeed. Include a changelog entry. Source: MAJ-01.
- [ ] **STABLE-02 — Make tweak-length encoding fail closed on both backends.** Add the shared absolute ceiling, checked native encoding, boundary tests that do not allocate gigabytes, and matching parameter documentation. **Done when:** default/per-call over-limit tweaks reject identically before FF1 calculation and ordinary-input outputs remain unchanged. Source: MED-01.
- [ ] **STABLE-03 — Test the actual release wheels on every promised target.** Expand installed-artifact testing across Linux x86_64/aarch64, macOS Intel/Arm, and Windows x64, and exercise the supported CPython 3.12/3.13/3.14 ABI combinations. Include NIST cases, AES validation, long-expansion fixtures, typed errors, and version/typing-marker checks. Run full conformance against at least one abi3 distribution build. **Done when:** artifact-origin checks and all required platform tests are green and gate publishing. Source: MED-02 and plan 00003 REQ-20.
- [ ] **STABLE-04 — Finish public-contract dual-backend parameterization.** Cover the remaining accepted numeral/byte-source types, snapshot behavior, default/long tweaks, and bounded-tweak interoperability without duplicating validation logic or weakening assertions. **Done when:** case-level collection proves both backends are exercised. Source: LOW-01.

#### B. Close the existing rc2 scope and hardening commitments

- [ ] **STABLE-05 — Resolve the recorded rc2 deliverable before freezing scope.** The current owner decision targets a Rust divide-and-conquer conversion at `2.0.0rc2`. Obtain a scoped delivery plan for it, or explicit approval to defer it beyond stable 2.0; record the decision in maintained backlog/release material. **Done when:** there is no ambiguous “rc2” promise left to silently bypass. Do not change the Python default or re-open the already-decided choice to offer Rust.
- [ ] **STABLE-06 — If retained in this release, deliver and independently verify the Rust conversion optimization.** Preserve spec-comparable reference logic; test fast/reference equivalence, leading zeros, truncation, odd splits, representative and full supported radix coverage, recursion thresholds, and realistic long inputs. Use call-local scratch/cache state. Add direct same-input Python/Rust encryption **and decryption** comparisons, not round trips alone, with all key sizes and varied tweaks. **Done when:** conformance remains bit-exact and measured long-input behavior justifies revised guidance. The power-of-two path and thresholds should be deliberate parts of that plan, not unreviewed extra scope.
- [ ] **STABLE-07 — Complete the negative-control CI evidence.** On a disposable, non-release test branch authorized by the owner, demonstrate that a controlled S-expansion error fails real Rust/installed-wheel conformance and prevents the gate from succeeding; retain the run reference and restore correct source before any candidate. Never tag or publish the mutated revision. **Done when:** plan 00005 AC-02 has the intended evidence, or an explicit owner waiver. Do not mistake the recorded local probe for the missing CI result.
- [ ] **STABLE-08 — Refresh performance evidence after any native-core change.** Re-run `just bench` with a release-built extension and record machine, interpreter, toolchain, package/extension versions, per-case timings, and the GIL probe. Retain short inputs as well as 1k/5k/20k lengths, radix 10 and a non-decimal radix; compare decrypt as well if making claims about it. **Done when:** README/changelog guidance matches the final candidate's recorded measurements. No universal speedup or constant-time claim is justified by one machine's table.

#### C. Assemble a candidate that can be promoted safely

- [ ] **STABLE-09 — Re-run the complete quality and conformance gates on the selected source.** Keep a Rust-free Python matrix as well as the real required-Rust path. Required commands include `just quality`, `just rust-test`, `just rust-lint`, and `FPR_FF1_REQUIRE_RUST_BACKEND=1 FPR_FF1_REQUIRE_ORACLE=1 uv run pytest --cov=fpr_ff1 --cov-report=term-missing --cov-fail-under=100`. **Done when:** all nine Python matrix legs and required native jobs are green, all NIST/intermediate/frozen/live-oracle suites are active, and exhaustive bijectivity is not omitted via the fast-test selector. Record results at the exact candidate commit; do not hard-code 1,406 as a permanent target.
- [ ] **STABLE-10 — Verify dependency and build-input consistency.** Run the existing Python locked/minimum-dependency audits, Cargo audit, and secret gate on the candidate. Check both lock files after version/manifest edits. Add or use `--locked` for release Cargo/maturin builds so a stale manifest/lock pair fails instead of being silently resolved independently of the audit job. **Done when:** the audited lock resolution matches the release builds and no unresolved applicable advisory remains. This is a preventative release control; this review did not establish an existing vulnerable or drifted resolution. Preserve the deliberate stable-channel toolchain policy, but record the actual compiler version used.
- [ ] **STABLE-11 — Verify package contents and fallback paths, not just source-tree imports.** Build in a clean release environment; inspect sdist, pure wheel, and native wheels for source/metadata/license/`py.typed`, extension placement, and absence of caches, agent instructions, plans/reviews, or dev binaries in the pure wheel. Prove sdist installation remains Rust-free and Rust selection fails clearly there. Run the packaged tests from an unpacked sdist with the documented test dependencies where applicable. **Done when:** distribution checks use installed artifacts, import origins are explicit, and downstream source packaging remains viable.
- [ ] **STABLE-12 — Make support and deployment statements precise.** Recheck NIST draft status at final freeze; retain the chosen subset and no-float/forward-AES rules. State native wheel OS/architecture/libc coverage, including the observed glibc 2.34 floor or its approved replacement and the pure fallback elsewhere. Resolve the post-final 1.x support/backport window. **Done when:** README/configuration/developer/security documents describe the release being shipped, without implying native support on untested platforms or 100% Rust line coverage from Python's coverage result.
- [ ] **STABLE-13 — Publish and evaluate a new candidate if release code changes.** The current rc1 is already on PyPI; do not overwrite it or move its tag. For rc2, use Python `2.0.0rc2`, Cargo `2.0.0-rc2`, matching lock entries, and tag `v2.0.0rc2`. **Done when:** the corrected/optimized candidate has green artifact tests, its own immutable release evidence, and representative consumer smoke results without leaking consumer-specific identifiers, keys, or defaults into this library. The owner sets any soak duration; no arbitrary waiting period is prescribed here.
- [ ] **STABLE-14 — Obtain a re-review of the final change set.** Request an independent read-only review with this report as the predecessor and current CI/artifact evidence attached. **Done when:** MAJ-01 is resolved, remaining findings are fixed or explicitly dispositioned, rc2 scope is closed, and no Critical/Major issue remains. Create a new report; do not edit this one or previous reports to indicate progress.

#### D. Prepare and publish stable metadata and artifacts

- [ ] **STABLE-15 — Bump final versions and lock entries together.** Set `pyproject.toml` to `2.0.0` and `rust/fpr-ff1-rust/Cargo.toml` to `2.0.0`; update the local-project entries in `uv.lock` and `rust/Cargo.lock`. **Done when:** the manifest contract test, installed `fpr_ff1.__version__`, native `_rs.__version__`, wheel metadata, and native SBOM agree on the final version. A version-only edit that leaves `uv.lock` stale fails the current locked CI sync.
- [ ] **STABLE-16 — Finish the final release documentation.** Add a dated `[2.0.0]` changelog section summarizing the delivered 2.0 feature and post-rc fixes; add its comparison link and point `[Unreleased]` at `v2.0.0...HEAD`. Update the README's “Shipped as rc1” roadmap text, supported-version table, resolved rc2 backlog item, compatibility notes, and any changed performance/validation guidance. **Done when:** historical candidate entries remain intact and final docs make neither a false migration promise nor a false certification claim. Keep the decided Production/Stable classifier; no classifier churn is needed.
- [ ] **STABLE-17 — Freeze and gate the exact final commit.** Ensure only reviewed release changes are included, verify the two version manifests and locks, and run the full CI/packaging gates after the final metadata edits. Confirm the `pypi` environment and Trusted Publisher still bind to the intended repository/workflow/environment; retain the release-only trigger and restricted publishing permissions. **Done when:** final source, version, and tested artifact set are unambiguous and no gate is skipped or red.
- [ ] **STABLE-18 — Have the release owner publish `v2.0.0`.** Create the new final tag at the reviewed commit and publish a non-prerelease GitHub release. The expected tag is **exactly `v2.0.0`**. Let `publish.yml` rerun the reusable gate and upload its downloaded artifacts; do not substitute a local rebuild or bypass failed checks. **Done when:** the release workflow succeeds, including every new native artifact-test job. Tagging and publication remain owner actions, not actions performed by this reviewer.
- [ ] **STABLE-19 — Verify the public release end to end.** Confirm PyPI exposes the intended seven-file set (or the explicitly approved revised matrix), final metadata and dependencies, non-yanked status, and attestations whose identities/subject digests match the intended workflow and files. Install stable from PyPI in clean representative environments, check versions/`py.typed`, and repeat the NIST plus long-expansion smoke checks on both backends and the pure fallback. **Done when:** stable is discoverable without prerelease opt-in and public artifact behavior matches the gated candidate. Metadata presence alone is insufficient.
- [ ] **STABLE-20 — Record the handoff and recovery procedure.** Preserve commit/tag, workflow/run references, artifact digests, support policy, and verification outcome in maintained release records. Monitor early import/conformance reports. For a defective release, stop further promotion, notify affected users, and consider yanking plus a new corrected version; never replace already published files or retag history. **Done when:** the owner has an explicit response path and knows whether any issue concerns availability only or ciphertext compatibility before recommending rollback/re-encryption.

### Not required merely to call this release stable

Do not add FF3/FF3-1, key management, consumer-specific alphabets/defaults, a compatibility shim, automatic backend switching, or a new runtime dependency. An independent cryptographic audit can improve assurance, but was not an existing acceptance condition and must not be falsely represented as completed by this review. Free-threaded Python, extra native architectures, and lower-glibc native wheels require separately agreed scope. The documented long-input slowdown is not itself a reason to reject an otherwise correct short-input accelerator if the owner explicitly defers rc2 optimization.

## Handoff

**Next step:** hand STABLE-01 through STABLE-04 to Builder, resolve the existing rc2/negative-control commitments with the release owner, then request a new review with exact candidate and artifact evidence. The runtime and workflow source should change only through that implementation workflow. This review writes no implementation, plan, backlog update, tag, or release.

### Disposition of every finding from review 00006

| Prior finding | Disposition | Current evidence |
|---|---|---|
| `REV-00006-MAJ-01` — missing Rust conformance release gate | **resolved** | `.github/workflows/ci.yml:78-135` builds and runs both backends, requires the extension, runs Rust unit/hygiene gates; publish reuses that workflow. PR #8 reports its conformance job successful. AC-02's additional negative-control evidence remains a separate task, and MED-02 here covers the remaining artifact/platform gap. |
| `REV-00006-MED-01` — production PyO3 bindings hold the GIL | **resolved** | Both production bindings call `py.detach` at `lib.rs:448-465`; owned buffers cross that boundary. The updated harness and documentation are present. This reviewer did not remeasure speedup. |
| `REV-00006-LOW-01` — stale backend names/contracts/security version text | **resolved** | Current agent/API contract, test availability docstrings, maturin comment, and 2.x security-policy wording reflect the shipped backend. Historical source references and legitimate Cargo artifact names are not stale imports. |
| `REV-00006-LOW-02` — inaccurate crossover guidance | **resolved** | `README.md:253-277` now has radix-10/256 rows and the 1k–5k band; `benchmarks/timing.py:47-50,126-163` reproduces those shapes. The work log records the quoted measurements. |
| `REV-00006-LOW-03` — repeated Rust AES schedule expansion | **resolved** | `lib.rs:257` constructs once per call; PRF and expansion receive `&cipher` at lines 333 and 347. Raw-key wrappers remain test-only consumers. |
| `REV-00006-LOW-04` — no Cargo Dependabot ecosystem | **resolved** | `.github/dependabot.yml:28-37` watches `/rust`, grouped weekly; Cargo audit remains in CI. |
| `REV-00006-LOW-05` — unpickled key length raises outside the hierarchy | **resolved** | `_ff1.py:329-332` raises `KeyLengthError`; `test_pickle.py:128-142` restores onto an uninitialized instance and checks the invalid key. This is distinct from the newly identified missing-backend bug. |
| `REV-00006-LOW-06` — hard-coded/misaligned extension version | **resolved** | `lib.rs:428` uses `CARGO_PKG_VERSION`; both manifests/locks agree; `test_contract.py:209-235` and `test_backend_dispatch.py:284-298` enforce normalized manifest/runtime agreement. |
| `REV-00006-LOW-07` — Rust hygiene gates and Windows dev-loop gap | **resolved** | CI runs fmt/clippy; `justfile:93-127` provides the local gates and Windows `.dll`→`.pyd` copy; unnecessary broad allow removed, spec arithmetic allowances remain narrow. Platform execution evidence for the distributed Windows wheel is requested separately in MED-02. |

The prior report's fixed issues are not counted again. This review does **not** retroactively validate all historical process claims, nor does it supersede prior vector-provenance evidence with locally generated data.

## Confidence

**Medium overall; high for the reported static defects.** The relevant release source and workflow paths were accessible, the tag exactly matched the clean worktree, and the blocking restoration bug can be established without executing code. Confidence in stable-release readiness is lower than confidence in that finding because native artifact behavior, final-event provenance, and the proposed fixes still require fresh execution evidence; successful PR checks and historical builder logs do not replace those checks.
