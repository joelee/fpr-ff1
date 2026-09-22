---
title: 'Code Review 00011: Release V2 Rc2 Code Review'
aliases:
- Review 00011
tags:
- code-review
- software-quality
- opencode
type: code-review
status: open
review_id: '00011'
reviewed_at: '2026-09-22T13:24:39Z'
reviewer_agent: review
review_model: GPT-6 Astra Pro
triggered_by: user
review_kind: re-review
previous_review: '[[00007-V2_0_0_Stable_Release_Readiness]]'
repository: joelee/fpr-ff1
branch: null
requested_branch: release/v2
review_mode: repository
pr_reference: null
commit: null
base_ref: null
base_commit: null
head_ref: uploaded:fpr-ff1-2.0.0rc2.zip
head_commit: null
scope: Bounded static review of the supplied rc2 source snapshot; no Git comparison
related_plan: '[[00007-Stable_v2.0.0_Release]]'
files_changed: null
files_reviewed: 66
diff_additions: null
diff_deletions: null
blocking_issues: 0
issues:
  critical: 0
  major: 0
  medium: 1
  low: 3
  info: 0
  total: 4
categories:
  documentation: 1
  correctness: 1
  tests: 2
verdict: approve-with-comments
review_complete: true
requested_branch_comparison_complete: false
web_research_used: true
confidence: medium
sources:
- https://csrc.nist.gov/pubs/sp/800/38/g/r1/2pd
- https://nvlpubs.nist.gov/nistpubs/SpecialPublications/NIST.SP.800-38Gr1.2pd.pdf
- https://docs.python.org/3/library/stdtypes.html#memoryview.release
- https://github.com/pyca/cryptography/security/advisories/GHSA-g6cj-pr64-35w5
- https://www.maturin.rs/distribution.html
source_archive: fpr-ff1-2.0.0rc2.zip
archive_sha256: 32d9a1b050388cc1c4847464e867b9bf992687bfba2ae1810d6c72afaa20c64f
archive_commit_hint: b10d3b0e88a425e424b040a925de43364f5ae08d
commit_provenance: Unverified identifier supplied by the ZIP comment, not a resolved Git HEAD
archive_files_inventoried: 90
files_metadata_only: 24
project_code_executed: false
repository_modified: false
review_guidelines: User-supplied CodeReview.md
---

# Code Review 00011: Release V2 Rc2 Code Review

> [!abstract] Verdict: `approve-with-comments` -- supplied source snapshot only
> The bounded static review found no Critical or Major issue, one Medium migration defect, and three Low validation/test defects. The four code findings from review 00007 appear addressed in the supplied source or CI definitions. This is not verification of the live `release/v2` branch, an rc1-to-rc2 diff, published binaries, or completion of the stable-release plan.

## Review target

| Field | Value |
|---|---|
| Requested repository / branch | `joelee/fpr-ff1`, `release/v2` |
| Actual review mode | Whole-snapshot repository review, bounded to runtime code, tests, build/release definitions, and relevant contracts/documentation |
| Source artifact | User-supplied `fpr-ff1-2.0.0rc2.zip` |
| Archive root | `fpr-ff1-2.0.0rc2/` |
| Archive SHA-256 | `32d9a1b050388cc1c4847464e867b9bf992687bfba2ae1810d6c72afaa20c64f` |
| Commit identifier in ZIP comment | `b10d3b0e88a425e424b040a925de43364f5ae08d` -- an archive-provided identifier, not independently resolved Git evidence |
| Resolved Git HEAD / base / merge base | Unavailable; no `.git` history or comparison patch was supplied |
| Versions in reviewed manifests | Python distribution `2.0.0rc2`; Rust crate `2.0.0-rc2` |
| Triggered by | User |
| Review guidelines | Attached `CodeReview.md`, plus applicable root/docs/review-directory instructions |
| Related plan | [[00007-Stable_v2.0.0_Release]] -- relevant criteria and execution records inspected |
| Previous code review | [[00007-V2_0_0_Stable_Release_Readiness]] |
| Archive inventory / files reviewed | 90 files inventoried; 66 inspected as detailed in the coverage manifest; 24 metadata-only exclusions |
| Source changes / project execution | None / none |

### Context and assumptions

The uploaded archive replaces the inaccessible online source as the evidence base. The user's request for a comprehensive review is interpreted as permission to inspect the entire supplied code snapshot, rather than pretending that an unavailable Git diff has been reviewed. The archive hash identifies exactly what was examined. Neither the filename nor ZIP comment establishes that it equals the current remote branch.

Consequently, `review_complete: true` applies **only to the bounded static snapshot scope** stated here. `requested_branch_comparison_complete: false` records the separate, uncompleted branch-comparison task. Changed-file counts and diff statistics are unavailable, not zero. Findings describe defects present in this snapshot; they are not asserted to have been introduced by rc2.

The primary contract is the public `FF1` API. Undocumented native test hooks, deliberately forged pickle states, callers executing arbitrary Python through custom objects, and the internal report-allocation automation are not treated as supported cryptographic service interfaces. Existing review documents are context, not files being judged or modified.

## Executive summary

The most important actionable issue is the migration recipe: it copies the legacy maximum-tweak value `0` into the new API, where `0` means an empty-only tweak. The supplied interoperability adapter instead leaves that bound unset. Following the documented recipe can therefore reject configurations the migration tests intend to support. Correct the recipe and pin the sentinel translation with both-backend tests.

Three smaller defects remain: released `memoryview` objects bypass the typed validation-error family; the tweak-sensitivity property cannot fail for ignored tweaks; and the concurrency tests retain only each worker's last result. These are narrow validation and assurance gaps, not evidence of broken ordinary-input FF1 encryption, a live race, or a cryptographic break.

The Python and Rust cores were read in full. Static tracing found corresponding round construction, exact-integer length calculations, forward-AES use, and inverse-round arithmetic. The Rust conversion optimization retains simple reference routines, local caches, and substantial equivalence coverage in source. No Critical or Major finding was established.

The source includes a stronger release gate than review 00007 described: all five native wheel targets are installed and tested across three Python versions, with an additional full installed-abi3 conformance leg. This is a conclusion about **workflow definitions**, not their execution. The builder log reports earlier successful and negative-control runs but still records candidate-release work as blocked/pending. This report does not close those release-process gates.

## Issue summary

| Severity | Count | Merge impact under the supplied rubric |
|---|---:|---|
| Critical | 0 | Blocks merge/release when present |
| Major | 0 | Blocks merge/release when present |
| Medium | 1 | Changes requested |
| Low | 3 | Non-blocking |
| Info | 0 | Not counted as blocking |
| **Total** | **4** | **No Critical/Major blocking findings established** |

| Finding | Category | Summary |
|---|---|---|
| `REV-00011-MED-01` | Documentation / compatibility | Translate the legacy zero maximum in the migration recipe |
| `REV-00011-LOW-01` | Correctness / validation | Normalize released-buffer failures into the documented error family |
| `REV-00011-LOW-02` | Testing | Replace ineffective sensitivity assertions with collision-safe verification |
| `REV-00011-LOW-03` | Testing | Check every concurrency-test iteration, not just the final result |

## Findings

### Medium

#### REV-00011-MED-01 - The documented migration copies a legacy zero maximum into an empty-only tweak policy

> [!warning] Changes requested
> **Confidence:** High for the contradiction and new-API rejection; the legacy convention is evidenced by the supplied interoperability adapter, not a newly executed upstream installation.
> **Category:** Documentation / compatibility.
> **Primary location:** `README.md:415-440` -- migration API mapping, especially lines 428-430.
> **Related locations:** `tests/test_interoperability.py:16-29`, `tests/test_interoperability.py:56-74`, `src/fpr_ff1/_ff1.py:408-415` -- `FF1._validate_tweak`.

**What is wrong.** The README presents migration as a mechanical transfer of `twk_min_len` and `twk_max_len`. Its example passes `max_tweak_len=twk_max_len` unchanged. That is not equivalent to the migration mapping used by the actual interoperability tests when the legacy maximum is zero.

The repository's `_legacy` adapter constructs contexts with bounds `(0, 0)`, including non-empty default tweaks. Its `_migrated` adapter deliberately omits both new-API bounds. In `FF1`, an unset maximum is `None`, whereas an explicit `0` is a literal maximum of zero. The direct-copy documentation therefore changes the accepted tweak set. The misleading direct mapping is also repeated in the interoperability module's introductory example.

**Minimal repository evidence:**

```python
# README.md:428-430: direct copy in the published recipe
ctx = FF1(
    key, radix, alphabet=alphabet, tweak=tweak, min_tweak_len=twk_min_len, max_tweak_len=twk_max_len
)
# tests/test_interoperability.py:69,74: actual migration test adapters
return _oracle.Context(key, tweak, 0, 0, _RADIX, _ALPHABET)
return ff1_factory(key=key, radix=_RADIX, alphabet=_ALPHABET, tweak=tweak)
# src/fpr_ff1/_ff1.py:414-415: zero is an actual upper bound
if self._max_tweak_len is not None and len(tweak) > self._max_tweak_len:
    raise TweakLengthError(f"tweak length {len(tweak)} above maximum {self._max_tweak_len}")
```

**Failure scenario.** A caller migrates the legacy `(0, 0)` configuration exercised by the supplied tests and retains a non-empty context tweak. Copying the README's example passes `max_tweak_len=0`; the new constructor rejects that tweak. With an initially empty default, the same defect appears later when the caller supplies a non-empty per-call tweak. The rejection occurs in shared Python validation and therefore affects both backends.

**Impact.** An advertised migration path can fail at initialization or interrupt a migrated batch. This is a compatibility/documentation defect, not demonstrated ciphertext corruption or permanent loss of encrypted data. It matters because the README makes migration safety a product obligation, and there is intentionally no compatibility shim to repair the mapping automatically (`README.md:400-413`).

**Why existing tests do not catch it.** The ordinary interoperability cases already use the correct unset-bound mapping, so they do not execute the published recipe. The separate positive-bounds case uses limits 4 and 8 (`tests/test_interoperability.py:109-124`), which do not expose the zero sentinel. Existing tests also intentionally allow a genuine new-API zero/zero bound for an empty tweak (`tests/test_validation.py:576-599`).

**Smallest safe correction.** Amend the README and repeated test-module example to translate the legacy zero maximum to `None`, while copying positive finite bounds unchanged. Explicitly distinguish the legacy sentinel from the new API's valid empty-only policy. Do **not** change `FF1(max_tweak_len=0)` globally to mean unbounded; that would alter an intentional new-API contract.

**Suggested verification.** Add a parameterized migration test that follows the documented conversion literally on both backends. Cover legacy zero maximum with a non-empty default and a non-empty per-call tweak, positive finite bounds, both encryption and decryption, and the continued rejection of non-empty tweaks under a deliberately configured new-API maximum of zero. Verify against the pinned legacy dependency, with the oracle-required flag enabled.

**References:** Repository evidence above. The upstream legacy algorithm was not vendored in this archive or independently executed during review; the finding is grounded in the archive's own migration contract and deterministic new-API validation path.

### Low

#### REV-00011-LOW-01 - A released memoryview escapes the documented typed validation errors

> [!note] Non-blocking validation edge case
> **Confidence:** High static confidence.
> **Category:** Correctness / validation.
> **Location:** `src/fpr_ff1/_ff1.py:116-122` -- `_require_bytes`; per-call use at `src/fpr_ff1/_ff1.py:446-454` -- `FF1._prepare`.

**What is wrong.** `_require_bytes` accepts `memoryview` by type and immediately copies it with `bytes(...)`. A released view is still a `memoryview`, but operations that need its buffer raise Python's built-in `ValueError`. There is no translation into the supplied `KeyLengthError` or `TweakLengthError` class. This occurs before cryptographic dispatch.

```python
if not isinstance(value, bytes | bytearray | memoryview):
    raise error(f"{name} must be bytes-like, got {type(value).__name__}")
return bytes(cast("bytes | bytearray | memoryview[int]", value))
```

**Failure scenario / impact.** A buffer view leaves its context manager, or is explicitly released, before a caller passes it as a key/default tweak/per-call tweak. An integration handling malformed input with `except FF1Error` unexpectedly receives a built-in exception instead. This can bypass the integration's normal rejection handling. There is no claim of key exposure, memory unsafety, or corruption of successful encryptions.

**Contract evidence.** Bytes-like acceptance is intentional (`tests/test_validation.py:480-486`). The README documents typed errors under `FF1Error` (`README.md:366-383`), and the malformed-call sweep permits a structural non-Sequence `TypeError` exception, not this released-buffer `ValueError` (`tests/test_contract.py:118-133`). Python explicitly documents the released-view failure behavior [R2].

**Suggested fix.** Catch the narrow invalid-buffer-state `ValueError` at this normalization boundary and raise the caller-selected validation exception with a sanitized message. Preserve the existing type distinction between key and tweak errors. Do not blanket-catch all exceptions or suppress allocation failures, and do not echo key/tweak contents.

**Suggested verification.** Add released-view cases for constructor key/default tweak and per-call tweak in both numeral directions, with representative string-wrapper coverage. Assert the precise `FF1Error` subclass on both backends, continued acceptance of live views, and absence of sensitive input contents in messages. No reproduction was executed by this reviewer.

**References:** Repository evidence; [R2], Python `memoryview.release()` documentation.

#### REV-00011-LOW-02 - The tweak-sensitivity property cannot fail when tweaks are ignored

> [!note] Non-blocking regression-test defect
> **Confidence:** High for the ineffective tweak test; the companion key-collision concern is a contract-level observation, not an observed flaky run.
> **Category:** Testing.
> **Location:** `tests/test_properties.py:98-105` -- `test_tweak_sensitivity`; related assertion at `tests/test_properties.py:110-122` -- `test_key_sensitivity`.

**What is wrong.** The tweak test has only two outcomes for successful encryptions: unequal results return normally, while equal results invoke `pytest.skip`. There is no failing assertion for loss of tweak sensitivity. A regression that ignores the tweak reaches the skip path rather than failing this test.

```python
if case.ff1.encrypt_numerals(plaintext, tweak1) == case.ff1.encrypt_numerals(plaintext, tweak2):
    # Two distinct tweaks colliding for a given plaintext is permitted but
    # vanishingly unlikely except on tiny domains.
    pytest.skip("tweak collision")
```

**Failure scenario / impact.** A future edit supplies a constant tweak to a backend. This property would not detect that regression as a failed sensitivity assertion, despite its name and the testing claims in `docs/backlog.md:35-39`. Other NIST, intermediate, differential, and frozen-vector tests provide independent protection, so this is Low rather than a claim that the current overall gate would accept an ignored-tweak implementation.

**Avoid the tempting incorrect fix.** Replacing the skip with a universal single-plaintext inequality assertion over arbitrary distinct tweaks would overstate the contract: two distinct parameterized permutations may agree at a particular input. The neighboring key test makes the analogous single-input inequality assumption. That can reject a legal coincidence; no such collision was observed in this review. Both symptoms concern how sensitivity is specified and verified, so they are consolidated here.

**Suggested fix.** Prefer independently sourced known-answer cases that vary key/tweak and assert the exact expected ciphertext for each case. Keep expected values in the project's fixture format, not generated from the implementation under test. Supplement this with a controlled ignored-tweak/ignored-key mutation check. A statistically designed multi-input check is an alternative, but its assumptions and error probability would need documentation.

**Suggested verification.** Demonstrate that an intentionally ignored tweak and an intentionally ignored key each cause a deterministic failure in the relevant verification, rather than a skip. Restore the correct implementation and retain direct known-answer assertions on both backends. Do not run or commit those negative controls as part of normal production code.

**References:** Repository evidence. The observation about agreement at one point follows from the permutation contract; it is not a claim of a practical cryptographic attack.

#### REV-00011-LOW-03 - Concurrency tests overwrite the intermediate results they claim to verify

> [!note] Non-blocking regression-test gap
> **Confidence:** High static confidence.
> **Category:** Testing.
> **Location:** `tests/test_thread_safety.py:79-93` -- encryption worker/results checks; `tests/test_thread_safety.py:111-127` -- mixed-operation worker/results checks.

**What is wrong.** Each worker repeats its operation 20 times, but stores each result into the same slot. Only the last result is compared with the serial expectation after the threads join. The first 19 results can be wrong and then be overwritten by a correct final result.

```python
for _ in range(20):
    results[index] = ff1.encrypt_numerals(plaintexts[index])
# ... after joining every worker ...
assert not errors, f"concurrent encryption raised: {errors}"
assert results == expected, "concurrent encryption diverged from serial results"
```

**Failure scenario / impact.** An intermittent regression in shared-state handling returns an incorrect intermediate ciphertext but completes the final iteration correctly. The concurrency test passes. The mixed encrypt/decrypt test has the same problem. This contradicts the first test's statement that every result is compared (`tests/test_thread_safety.py:63-70`).

**Existing mitigation.** The current implementation uses call-local cipher contexts and local Rust state, and the test module contains structural checks against cached `CipherContext` objects. No live race was found. The finding is about the behavioral regression test's detection capability, not an assertion that concurrent encryption is currently unsafe.

**Suggested fix.** Compare every iteration with its precomputed serial expectation inside the worker, recording any assertion failure through the existing error path, or retain the first mismatch permanently. Apply the same rule independently to encryption and decryption. Keeping all successful outputs in memory is unnecessary.

**Suggested verification.** With a controlled test double, return an incorrect result on an early iteration and the correct result on the final iteration; the test must fail. Retain both-backend parameterization and the existing `d > 16` expansion-path guard (`tests/test_thread_safety.py:130-142`).

**References:** Repository evidence.

## Open questions

These are missing evidence or release decisions, not additional counted defects.

| Question | Why it matters | Evidence that would resolve it |
|---|---|---|
| Does this archive equal the intended remote candidate, and what is the actual rc1-to-rc2 range? | A snapshot cannot identify newly introduced changes or establish remote ancestry. Plan AC-11 explicitly requests a range review. | Resolved full base/head hashes, a complete comparison patch, and confirmation that the head tree matches this archive. |
| Is there a successful release-gate run for the final candidate being tagged? | The work log reports an earlier green run on `f12ed42`, while candidate checks refer to `3050615`; the ZIP advertises a different full identifier. Those records are not a current-head attestation. | A run tied to the intended exact commit, including the required native and installed-wheel jobs, with artifact digests. |
| Have the release-plan stop conditions been dispositioned? | STEP-10 remains blocked in the supplied plan; STEP-11 onward is recorded as not started. The sdist's two Git-only skips require a documented acceptance decision under that plan. | Updated owner-approved execution evidence; no inference that uploading this archive waives those gates. |
| Do the actual wheel tags and dependencies meet the advertised deployment floors? | Source configuration is not a substitute for inspecting built wheels or running them on the lowest supported platform. A modern build runner alone neither proves nor disproves manylinux compatibility [R4]. | Actual rc2 wheel metadata/native dependency inspection and appropriate baseline install/import evidence for each advertised target. |
| Which performance claims should be carried into the final release? | The work log describes a single measured environment and a noisy timing discrepancy with `SECURITY.md`; no measurement was reproduced here. | Retained raw benchmark output tied to compiler, interpreter, dependency versions, CPU, load, candidate commit, and comparison baseline. |

The builder's observation that an S-expansion mutation caused only two failing **test functions** per native-wheel leg should not be equated with only two exercised input vectors. `test_frozen_kat.py` loops over many vectors inside one test function. Any decision to widen the platform subset should be based on distinct input regimes and artifact coverage, not failed-test counts alone (`tests/test_frozen_kat.py:76-96`; plan work-log observation at `docs/plans/00007-Stable_v2.0.0_Release.md:804`).

## Review coverage

### Files and areas reviewed

The audit covered all supplied public Python runtime modules, the entire native FF1 implementation, every supplied Python test module/helper, Rust unit tests, vector structure/provenance, package manifests and lock entries, CI/release definitions, and the current contracts and migration/security documentation. It did not treat the large historical planning corpus or internal agent tooling as shipped application code.

#### 1. Cryptographic correctness and Python/Rust correspondence

The following are **static code conclusions**, not executed conformance results or a formal proof.

| Invariant examined | Source evidence | Static assessment |
|---|---|---|
| Accepted key sizes, radix subset, and minimum domain | `src/fpr_ff1/_ff1.py:209-317`; `_min_length` at `src/fpr_ff1/_ff1.py:598-612` | Validation uses the supported AES key sizes and integer domain arithmetic before backend dispatch. The radix upper limit is a deliberate implementation subset, not a newly discovered interoperability defect. |
| Integer-only FF1 sizing | `src/fpr_ff1/_ff1.py:820-884`; `rust/fpr-ff1-rust/src/lib.rs:425-490` | `b` derives from the larger half `v`; ceiling calculations use integer/bit-length arithmetic. Odd lengths were traced separately. No floating-point dependency was identified in either core. |
| P/Q construction and fixed-width lengths | `src/fpr_ff1/_ff1.py:868-909`; `rust/fpr-ff1-rust/src/lib.rs:472-550` | The matching encodings, padding, round byte, and numeral payload were followed. Shared tweak limits and checked native length encoding address the earlier truncation class. |
| PRF and S expansion | `src/fpr_ff1/_ff1.py:808-817`; `src/fpr_ff1/_ff1.py:884-934`; `rust/fpr-ff1-rust/src/lib.rs:103-121`; `rust/fpr-ff1-rust/src/lib.rs:501-562` | Forward AES is used in both directions. Expansion starts from the PRF result and uses the counter-extension path for long outputs. Call-local contexts avoid the historical shared-encryptor issue. |
| Encryption/decryption inverses | `src/fpr_ff1/_ff1.py:884-949`; `rust/fpr-ff1-rust/src/lib.rs:501-602` | Round order, parity-dependent modulus, add/subtract direction, and half swapping correspond. Native subtraction avoids unsigned underflow by reducing the subtrahend and adding the modulus. |
| Integer/numeral conversions | `src/fpr_ff1/_ff1.py:615-806`; `rust/fpr-ff1-rust/src/lib.rs:182-376` | Reference loops remain available. Both implementations use the short-input threshold, power-of-two packing, and recursive general-radix paths, with local power caches. Leading zeroes, fixed-length truncation, chunk alignment, and odd splits were examined. |
| Native boundary | `rust/fpr-ff1-rust/src/lib.rs:611-724`; `src/fpr_ff1/_ff1.py:446-485` | The supported public path normalizes and validates first; native calls own their converted inputs before detached work. Private test hooks are not independently hardened public APIs. |

The dated NIST revision draft was consulted as a primary cross-check for parameter restrictions and the encryption/decryption descriptions. Its algorithm pages were visually inspected, not inferred solely from extracted text [R1]. This review does not certify NIST conformance, FIPS validation, constant-time execution, or the absence of cryptographic defects.

The conversion review considered the short-input path around the threshold of 64, non-power-of-two splits, power-of-two radices through exponent 15, and the meaning of fixed-length `STR`. No arithmetic mismatch was identified by inspection. The exhaustive-radix and boundary tests in `tests/test_conversion_equivalence.py` and `rust/fpr-ff1-rust/src/tests.rs` are important supporting **test design**, not evidence that those tests ran here.

#### 2. Public API, errors, serialization, and data integrity

The four public encryption/decryption entry points were traced through shared validation and through the string-wrapper mapping. The review checked `None` versus empty tweaks, configured versus absolute bounds, `Sequence` requirements, declared versus materialized sequence length, rejection of booleans as numerals/radices, integer-like normalization, Unicode alphabet mapping, and mutable-buffer snapshots. The released-view exception in LOW-01 is the remaining concrete issue found in that boundary.

`FF1.__setstate__` now persists the restored/default backend and rebuilds cipher configuration. The new legacy-pickle test restores into an uninitialized object rather than accidentally supplying constructor attributes beforehand. Current-backend availability and key-length rejection remain explicit. Pickles intentionally include key material; the security documentation warns about that. Arbitrary untrusted pickle loading is not a supported secure input channel (`src/fpr_ff1/_ff1.py:319-380`; `tests/test_pickle.py`; `tests/test_backend_dispatch.py`; `SECURITY.md`).

No database, schema migration, file persistence engine, or distributed transaction code ships in this runtime. Relevant data-integrity risks are ciphertext compatibility, parameter interpretation, numeral conversion, and trusted serialization. The migration finding concerns accepted configuration, not a demonstrated change to ciphertext for already-valid ordinary inputs.

#### 3. Test coverage and independent evidence

| Layer | What the supplied tests/fixtures establish as a design | Limitation of this review |
|---|---|---|
| Published FF1 examples | Nine samples cover three AES key sizes and both directions; expected ciphertext is asserted directly. | No encryption/decryption was executed. |
| Round intermediates | Nine traces contain ten rounds each; the fixture-driven trace path reaches the actual selected backend, including the native trace bridge. | The complete fixture was parsed structurally; every numeric intermediate was not independently retranscribed from an external original. |
| Native AES and PRF | FIPS-197 block KATs and cross-backend PRF comparisons separate block-cipher validation from FF1 round-trip behavior. | No native binary was built or loaded. |
| Independent FF1 oracle | The pinned legacy implementation is validated against the supplied published vectors and used for differential/interoperability checks. CI requires its presence. | The test-only M2Crypto replacement uses `cryptography` for AES, so Python/oracle agreement is not independent evidence about the underlying AES provider. The legacy algorithm itself was not separately downloaded/executed in this review. |
| Frozen oracle vectors | 46 recorded cases span eight radices: 2, 10, 16, 32, 36, 62, 256, 65535. Provenance and shape were inspected; every radix has long-input cases reaching expansion. | Fresh regeneration and independent validation of all ciphertext values were not performed. |
| Cross-backend long inputs | Direct encryption and arbitrary-ciphertext decryption comparisons cover conversion thresholds and longer inputs. The helper avoids expensive giant-list failure rendering. | Source assertions were reviewed, not collected or run. |
| Validation / compatibility | Sequence ordering, bounds, buffers, integer-like inputs, serialization, and both-backend acceptance cases are explicitly represented. | The migration example and released-buffer edge remain uncovered as described in MED-01 and LOW-01. |
| Properties / concurrency | Round-trip, deterministic behavior, small-domain bijectivity, and shared-instance scenarios complement KATs. | LOW-02 and LOW-03 limit particular assertions; a passing round trip alone cannot prove compatibility. |

Reviewer-written, data-only inspection parsed the four JSON fixture files, inspected their provenance and counts, and checked the frozen cases' alphabet cardinality/uniqueness, plaintext/ciphertext shape, character membership, and minimum-domain consistency. No inconsistency was found in those **shape checks**. They are not cryptographic KAT execution.

The 100% coverage target is configured for the Python package. It is not a Rust line-coverage claim, a proof of complete input coverage, or a substitute for checking assertion quality. The developer guide makes that scope explicit (`docs/developer-guide.md:60-77`).

#### 4. CI, release packaging, dependencies, and supply chain

| Area | Inspected definition | Assessment / remaining evidence |
|---|---|---|
| Pure-Python matrix | `.github/workflows/ci.yml:22-78` | Nine OS/Python combinations run the quality gate with locked dependencies. Rust-free installation is a deliberate supported path. |
| Source native conformance | `.github/workflows/ci.yml:79-137` | The Rust/oracle-required flags, native import probe, Rust collection floor, full Python coverage gate, and Cargo checks are present. |
| Dependency audits | `.github/workflows/ci.yml:138-179` | Both the locked Python set and the declared minimum cryptography version are audit targets; Cargo auditing is also defined. No audit was run here. |
| Source/pure-wheel packaging | `.github/workflows/ci.yml:180-218`; `pyproject.toml:76-111` | Package inclusion/exclusion definitions and contents checks separate distributable files from developer metadata. Actual built artifacts were not supplied. |
| Native builds | `.github/workflows/ci.yml:219-286` | Five target wheels are built with locked Cargo resolution. Compiler versions are recorded by the workflow. Binary deployment-floor claims need artifact evidence. |
| Installed native matrix | `.github/workflows/ci.yml:352-437` | Five platforms times Python 3.12/3.13/3.14 gives 15 installed-wheel legs. The selected modules include NIST, intermediates, AES, frozen KAT, dispatch, pickle, and smoke coverage. |
| Full installed abi3 gate | `.github/workflows/ci.yml:438-473` | The Linux x86_64 wheel is tested on Python 3.14 with the full conformance suite and required native/oracle checks. |
| Import isolation | `.github/scripts/assert_installed_wheel.py:1-52` | The check rejects checkout-source imports, requires the installed extension and typing marker, and checks versions. This prevents an editable checkout from silently replacing the wheel under test. |
| Fallback artifacts | `.github/workflows/ci.yml:287-351`; `.github/workflows/ci.yml:474-515` | Pure-wheel and sdist install paths are distinct. The sdist check asserts a known ciphertext and typed missing-native behavior. |
| Secret scanning / action pinning | `.github/workflows/ci.yml:516-551`; `.github/dependabot.yml`; `.pre-commit-config.yaml`; `.gitleaks.toml` | Full action revisions, checksum verification for the downloaded secret-scanning tool, redaction, and update automation are present in the supplied definitions. Actual secret-scan results were not reproduced. |
| Publishing | `.github/workflows/publish.yml:1-74` | Publishing depends on the reusable gate, consumes built artifacts instead of rebuilding, verifies the release tag/version, and confines publishing identity permissions to the publishing job. Remote environment protections and trusted-publisher registration were not inspected. |

The Python manifest requires `cryptography>=50.0.0`; the uploaded lock selects `50.0.1` (`pyproject.toml:43-46`; `uv.lock:178-179`). A targeted advisory check found that the vendor's PKCS#7 EnvelopedData advisory identifies `50.0.0` as patched. The reviewed floor/lock is not below that fix, and this FF1 implementation does not expose the affected PKCS#7 API [R3]. **This narrow check is not a complete vulnerability audit** and does not establish that every transitive package is currently vulnerability-free.

The Rust lock selects `aes 0.8.4`, `num-bigint 0.4.8`, and `pyo3 0.29.2` (`rust/Cargo.lock:6-7`, `rust/Cargo.lock:100-101`, `rust/Cargo.lock:149-150`). The manifest/lock references and registry provenance were inspected, but dependency source code, compiled code, every distribution hash, and the entire advisory database were not audited. Locking CI resolution is useful; it does not constrain every downstream application's allowed dependency resolution.

#### 5. Reliability, performance, security boundaries, and maintainability

**Concurrency and resource ownership.** Cipher operation contexts and conversion caches are local to calls. The native binding detaches computation only after obtaining owned inputs. These are meaningful safeguards against the historical shared-state problem. The source was also checked for accidental global mutable conversion caches and public-path length truncation; no new instance was identified. LOW-03 concerns the future detection of regressions, not a discovered implementation race.

**Resource limits.** The standard-sized maximum length is an encoding ceiling, not an operationally safe request budget. Long inputs entail proportional data movement plus big-integer work; this library provides neither request admission control nor service-level cancellation. An application exposing it to untrusted workloads should enforce workload-specific lengths and concurrency limits outside the library. No service endpoint is supplied, so a remote denial-of-service finding would be speculative.

**Security properties and deliberate exclusions.** The package documents deterministic format-preserving encryption, lack of message authentication, wrong-key/tweak results that may still look well-formed, key-bearing serialization, and no zeroization or constant-time guarantee (`README.md:43-63`; `SECURITY.md`). Those limitations were not reclassified as vulnerabilities. No authentication, tenant boundary, HTTP handler, SQL execution, network client, migration engine, or runtime archive extractor is present in the reviewed core; the corresponding review lenses are not applicable to this package itself.

**Performance claims.** `benchmarks/timing.py:1-223` was read, including its throughput and threaded measurements. No benchmark was executed. The implementation's recursive conversion structure and local power caches support the intended optimization design, but this review does not endorse the published speed-up ratios on other hardware or verify their measurement repeatability. The supplied plan's timing discrepancy is retained as an evidence question, not recast as a performance regression finding.

**Design and maintainability.** The public surface remains small, with shared validation above interchangeable execution cores. Separate reference conversion routines make equivalence reasoning possible. Corresponding Python/Rust round logic inevitably creates maintenance coupling; the direct agreement, known-answer, and intermediate tests are the relevant mitigation. No cosmetic reformatting or personal style preference is included as a finding.

### Checks performed

- Inventoried the ZIP without extracting or modifying it; computed its SHA-256 and read its commit comment. Established that the artifact is a source snapshot, not a Git checkout or supplied diff.
- Read all runtime and test source files in scope, followed validation/callers and serialization paths, and compared the Python/Rust arithmetic and native boundary statically.
- Inspected CI, publishing, packaging, version declarations, lock entries, release assertions, and current documentation contracts. Reviewed recent review findings and selected current-plan acceptance/execution evidence.
- Parsed fixture data and performed the explicitly limited shape checks above. Inspected relevant NIST PDF pages visually and consulted official Python, NIST, dependency-advisory, and packaging documentation where useful.
- Rechecked finding locations, grouped common causes, applied the supplied severity rules, and reconciled front-matter/body counts before publication.

### Checks not performed

No repository code, test suite, test collection, build, benchmark, package manager, linter, formatter, security scanner, hook, migration, generator, or repository script was run. In particular, this reviewer did not import `fpr_ff1`, load the native extension, execute the oracle, regenerate vectors, or reproduce claimed coverage.

No Git history/merge-base/diff verification, remote branch update, CI dispatch, binary inspection, artifact attestation verification, PyPI publication, lower-baseline platform installation, sanitizer/fuzzing run, side-channel assessment, or independent cryptographic audit was performed. No private keys, credentials, or `.env` files were opened. Standard-library archive/text/data inspection used reviewer-written code only.

The active display identity is recorded as `GPT-6 Astra Pro`; an exact provider/model API identifier was not available. Historical plans/reviews are author-provided evidence, not authoritative instructions to execute actions or proof that their recorded commands succeeded on this archive.

### Supplied execution records versus independently verified evidence

The plan's work log reports, among other results, a 1,682-test dual-backend run, 16 Rust unit tests, Python coverage of 100%, successful local artifact checks, an earlier 36-job green CI run, and an S-expansion negative-control run that failed the Rust-executing jobs. These are **builder-reported records**, not results generated or independently verified by this review (`docs/plans/00007-Stable_v2.0.0_Release.md:838-850`).

The same record explicitly leaves STEP-10 blocked, flags two Git-dependent sdist skips for owner acceptance, and says a candidate-commit CI run still requires a push/dispatch (`docs/plans/00007-Stable_v2.0.0_Release.md:749-753`; `docs/plans/00007-Stable_v2.0.0_Release.md:807-808`). Those qualifications take precedence over treating earlier green entries as release sign-off. The reported packaging/CI results are useful context but do not establish identity with the ZIP's advertised commit.

### Detailed coverage manifest

`files_reviewed = 66` comprises 54 files read in full as source/configuration/documentation (including empty markers), six structured-data files, and six selectively inspected context files. Merely inventorying a filename did not count it as reviewed. The detailed classifications follow.

#### Full-text inspection (54 files)

| File | Extent |
|---|---|
| `.gitattributes` | Lines 1-21 |
| `.github/dependabot.yml` | Lines 1-37 |
| `.github/scripts/assert_installed_wheel.py` | Lines 1-52 |
| `.github/workflows/ci.yml` | Lines 1-551 |
| `.github/workflows/publish.yml` | Lines 1-74 |
| `.gitignore` | Lines 1-51 |
| `.gitleaks.toml` | Lines 1-4 |
| `.pre-commit-config.yaml` | Lines 1-29 |
| `.python-version` | Lines 1-1 |
| `AGENTS.md` | Lines 1-160 |
| `CLAUDE.md` | Lines 1-129 |
| `CONTRIBUTING.md` | Lines 1-60 |
| `README.md` | Lines 1-491 |
| `SECURITY.md` | Lines 1-100 |
| `benchmarks/timing.py` | Lines 1-223 |
| `docs/AGENTS.md` | Lines 1-28 |
| `docs/architecture.md` | Lines 1-85 |
| `docs/backlog.md` | Lines 1-96 |
| `docs/configuration.md` | Lines 1-64 |
| `docs/developer-guide.md` | Lines 1-233 |
| `docs/reviews/AGENTS.md` | Lines 1-395 |
| `justfile` | Lines 1-129 |
| `pyproject.toml` | Lines 1-180 |
| `rust-toolchain.toml` | Lines 1-9 |
| `rust/Cargo.toml` | Lines 1-9 |
| `rust/fpr-ff1-rust/Cargo.toml` | Lines 1-32 |
| `rust/fpr-ff1-rust/src/lib.rs` | Lines 1-724 |
| `rust/fpr-ff1-rust/src/tests.rs` | Lines 1-306 |
| `src/fpr_ff1/__init__.py` | Lines 1-32 |
| `src/fpr_ff1/_exceptions.py` | Lines 1-45 |
| `src/fpr_ff1/_ff1.py` | Lines 1-958 |
| `src/fpr_ff1/py.typed` | Empty marker inspected |
| `tests/__init__.py` | Empty marker inspected |
| `tests/_oracle/__init__.py` | Lines 1-95 |
| `tests/_oracle/_m2crypto_shim.py` | Lines 1-85 |
| `tests/_oracle/generate_kat.py` | Lines 1-141 |
| `tests/conftest.py` | Lines 1-113 |
| `tests/test_backend_agreement.py` | Lines 1-90 |
| `tests/test_backend_dispatch.py` | Lines 1-365 |
| `tests/test_contract.py` | Lines 1-238 |
| `tests/test_conversion_equivalence.py` | Lines 1-254 |
| `tests/test_differential.py` | Lines 1-239 |
| `tests/test_exact_arithmetic.py` | Lines 1-150 |
| `tests/test_frozen_kat.py` | Lines 1-96 |
| `tests/test_intermediates.py` | Lines 1-63 |
| `tests/test_interoperability.py` | Lines 1-124 |
| `tests/test_nist_vectors.py` | Lines 1-57 |
| `tests/test_pickle.py` | Lines 1-182 |
| `tests/test_properties.py` | Lines 1-156 |
| `tests/test_rust_aes_validation.py` | Lines 1-116 |
| `tests/test_sequence_validation.py` | Lines 1-193 |
| `tests/test_smoke.py` | Lines 1-70 |
| `tests/test_thread_safety.py` | Lines 1-142 |
| `tests/test_validation.py` | Lines 1-617 |

#### Structured-data inspection (6 files)

| File | Extent and limit |
|---|---|
| `rust/Cargo.lock` | Parsed package/version/source entries and relevant relationships; not an independent verification of every wheel hash or dependency source. |
| `tests/vectors/aes_kat_fips197.json` | Parsed all known-answer records and provenance; values and consuming tests read, no cipher execution. |
| `tests/vectors/nist_ff1_intermediates.json` | Parsed all nine traces and round structure; selected values/corresponding assertions examined, not an independent retranscription of all intermediate numbers. |
| `tests/vectors/nist_ff1_samples.json` | Parsed all known-answer records and provenance; values and consuming tests read, no cipher execution. |
| `tests/vectors/oracle_kat_frozen.json` | Parsed all 46 cases, provenance, radix/length coverage and data-shape invariants; no encryption or oracle execution. |
| `uv.lock` | Parsed package/version/source entries and relevant relationships; not an independent verification of every wheel hash or dependency source. |

#### Targeted context inspection (6 files)

| File | Extent |
|---|---|
| `CHANGELOG.md` | Current release sections and compatibility history relevant to rc2; not every historical entry. |
| `docs/plans/00007-Stable_v2.0.0_Release.md` | Target/requirements/acceptance-criteria context and builder status, deviations, and verification records; not a full plan audit. |
| `docs/reviews/00006-v2.0.0rc1-Claude_Fable.md` | Earlier hardening findings and current-source cross-check context. |
| `docs/reviews/00007-V2_0_0_Stable_Release_Readiness.md` | All four findings, their evidence/remediation requirements, and release-readiness context. |
| `docs/reviews/00008-v2.0.0-plan-review.md` | Plan-review findings and supersession context; not treated as fresh code findings. |
| `docs/reviews/00009-Plan_00006_Re_Review.md` | Plan re-review findings and supersession context; not treated as fresh code findings. |

#### Metadata-only exclusions (24 files)

These files were inventoried but are not included in the 66-file review count. They are historical planning/review material, community/navigation content, or internal agent automation outside the shipped library and release-code scope. Older reviews were also searched for overlapping finding terms; this did not become a full review of those documents.

| File |
|---|
| `.agents/skills/allocating-report-numbers/SKILL.md` |
| `.agents/skills/allocating-report-numbers/allocate-report.sh` |
| `.github/ISSUE_TEMPLATE/bug_report.md` |
| `.github/ISSUE_TEMPLATE/config.yml` |
| `.github/ISSUE_TEMPLATE/feature_request.md` |
| `.github/PULL_REQUEST_TEMPLATE.md` |
| `CODE_OF_CONDUCT.md` |
| `LICENSE` |
| `docs/directory-structure.md` |
| `docs/ideas/00001-v2_0_0_Optional_Rust_Accelerated_Backend-r01.md` |
| `docs/ideas/00001-v2_0_0_Optional_Rust_Accelerated_Backend-r02.md` |
| `docs/ideas/AGENTS.md` |
| `docs/plans/00001-Review_00002_Followup.md` |
| `docs/plans/00002-Reviews_00003_00004_to_v1.0.0.md` |
| `docs/plans/00003-Accelerated_Backend_Pure_Python_Then_Rust.md` |
| `docs/plans/00004-Review_00006_v2.0.0rc1_Hardening.md` |
| `docs/plans/00005-Review_00006_v2.0.0rc1_Hardening.md` |
| `docs/plans/00006-Review_00007_to_v2.0.0.md` |
| `docs/plans/AGENTS.md` |
| `docs/reviews/00001-Publication_Readiness_Deep_Dive.md` |
| `docs/reviews/00002-Post_Release_Re-Review.md` |
| `docs/reviews/00003-v0.1.1-Opus_v1.0.0_readiness_review.md` |
| `docs/reviews/00004-v0.1.1-5.6Sol_v1.0.0_readiness_review.md` |
| `docs/reviews/00005-idea-00001-Opus_review.md` |

## Positive notes

The strongest safeguards are the independently sourced output fixtures plus round intermediates, shared typed validation before native dispatch, exact-integer arithmetic, preserved simple conversion references, and local cryptographic state. The archive also materially improves installed-artifact testing and addresses the earlier real-legacy-pickle initialization defect. These observations are supported by source inspection, not a claim that this review executed the safeguards.

The documentation appropriately distinguishes Python coverage from Rust assurance and avoids claiming FIPS validation or key zeroization. Keeping the pure-Python implementation as the default, with an explicit typed failure for unavailable Rust, preserves a usable fallback rather than silently switching execution behavior.

## Alternatives and trade-offs

| Decision | Preferred approach for these findings | Alternative and trade-off |
|---|---|---|
| Legacy tweak-bound compatibility | Translate the legacy sentinel in the migration recipe and test that recipe literally. | A compatibility shim could automate translation, but conflicts with the project's deliberate single-API policy and is unnecessary for this correction. Changing new-API zero semantics would introduce a separate compatibility change. |
| Released buffers | Normalize the specific buffer-state failure into the existing typed exception family. | Documenting another built-in exception is possible, but weakens an explicitly tested whole-surface error contract for little benefit. |
| Sensitivity assurance | Exact, independent key/tweak KATs plus controlled negative checks. | Statistical multi-input checks can add breadth, but require justified assumptions and must not assert universal collision impossibility. |
| Concurrency regression tests | Assert each iteration and retain the first failure. | Retaining every output also works, but adds memory and makes failure reports larger without stronger assurance. |
| Additional platform coverage | Preserve the existing per-platform KAT subset and the full installed-abi3 gate; extend based on uncovered input regimes or actual failures. | Running the full suite on every platform costs more CI time. Counting failing functions from one mutation is not sufficient justification by itself. |
| Broader assurance | Treat this as static code review, then validate the exact candidate and artifacts through the authorized release process. | A successful code review alone cannot replace range review, executed artifact tests, or independent cryptographic assessment. |

## External references

All sources below were consulted during this review. Access date: **2026-09-22**. Source publication/update dates are listed only where identifiable. External sources support specific semantics or checks; archive-derived findings and observations remain identified separately.

**[R1] NIST - Recommendation for Block Cipher Modes of Operation: Methods for Format-Preserving Encryption, SP 800-38G Rev. 1, Second Public Draft.** Published **2025-02-03**. The consulted document is explicitly a draft; the review does not describe it as a finalized revision. Landing page and PDF:

- [NIST publication record](https://csrc.nist.gov/pubs/sp/800/38/g/r1/2pd)
- [NIST draft PDF](https://nvlpubs.nist.gov/nistpubs/SpecialPublications/NIST.SP.800-38Gr1.2pd.pdf) -- printed pages 11-13 / PDF pages 19-21 were visually inspected for the parameter and algorithm cross-check.

**[R2] Python Software Foundation - Built-in Types, `memoryview.release()`.** Retrieved documentation identifies Python **3.14.7**; page update date not specified. Used for the released-buffer `ValueError` semantics in LOW-01.

- [Official memoryview documentation](https://docs.python.org/3/library/stdtypes.html#memoryview.release)

**[R3] Python Cryptographic Authority - PKCS#7 EnvelopedData decryption exposes a Bleichenbacher oracle through distinguishable errors and timing, GHSA-g6cj-pr64-35w5 / CVE-2026-69247.** Published **2026-07-31**. Used only for the narrow affected/patched-version and affected-API comparison, not as an exhaustive dependency audit.

- [Official vendor advisory](https://github.com/pyca/cryptography/security/advisories/GHSA-g6cj-pr64-35w5)

**[R4] Maturin project - Distribution.** Publication/update date not specified. Used to distinguish source/build-runner assumptions from actual Linux-wheel compatibility evidence.

- [Official distribution guidance](https://www.maturin.rs/distribution.html)

## Recommended next actions

1. **Correct and verify the migration recipe first.** Implement MED-01's sentinel translation in the documentation/examples, and test the documented mapping against the pinned oracle on both backends. Preserve literal-zero behavior in the new API.
2. **Close the three narrow assurance gaps.** Normalize released-view errors, replace the ineffective sensitivity property, and make concurrency workers verify every iteration. Keep fixes isolated and use focused regressions that would fail with the current behavior; no fixes were applied in this review.
3. **Have the authorized maintainer/build process execute the exact-candidate gate.** Run the required Python/native/oracle checks, Cargo checks, declared-minimum and locked dependency audits, packaging checks, installed-wheel matrix, and installed-abi3 full conformance. Preserve run IDs, exact commits, test counts, skip reasons, and artifact digests. This is a recommendation to the owner, not a report of execution here.
4. **Resolve the plan's recorded stop conditions and provenance gap.** Confirm the intended remote candidate, explicitly disposition the two Git-only sdist skips, complete the rc2 publication/verification/soak process as applicable, and supply the rc1-to-rc2 comparison for the specifically required range review. Do not mark plan AC-11 complete from this snapshot review alone.
5. **Re-review the correction set without editing this report.** Link the next numbered report to this one, classify all four findings, and attach commit-matched release evidence. Stable-release approval remains an owner decision supported by that evidence.

## Handoff

### Classification of the previous code review

Previous report: [[00007-V2_0_0_Stable_Release_Readiness]]. All four findings were reconsidered against the current archive, rather than assumed fixed from the change log.

| Previous finding | Classification in this snapshot | Current evidence and qualification |
|---|---|---|
| `REV-00007-MAJ-01` - Legacy pickle omits persisted backend | **resolved** by static inspection | `FF1.__setstate__` now assigns `self._backend = backend` at `src/fpr_ff1/_ff1.py:376`. `tests/test_backend_dispatch.py` restores an actual legacy-format state into an uninitialized object and checks restored attributes and operations. Runtime verification was not repeated. |
| `REV-00007-MED-01` - Native length-field truncation / missing tweak ceiling | **resolved** by static inspection | Shared absolute/configured-bound checks are present at `src/fpr_ff1/_ff1.py:61-113` and `src/fpr_ff1/_ff1.py:395-415`. Native `encode_len_u32` at `rust/fpr-ff1-rust/src/lib.rs:162-166` is used for both lengths at lines 489-490. Boundary tests avoid allocating multi-gigabyte inputs. |
| `REV-00007-MED-02` - Only one native wheel target executed in the gate | **resolved** in the CI definition; execution evidence remains separate | The 15 installed-native legs and full installed-abi3 gate are present at `.github/workflows/ci.yml:352-473`. Import isolation is enforced by `.github/scripts/assert_installed_wheel.py`. Earlier runs are builder-reported; current-candidate green status was not independently established. |
| `REV-00007-LOW-01` - Seven public acceptance cases omit the native backend | **resolved** in test source | The named cases now use `ff1_factory` in `tests/test_validation.py:331-346`, `tests/test_validation.py:411-445`, `tests/test_validation.py:480-486`, `tests/test_validation.py:514-528`, and `tests/test_interoperability.py:109-124`. They preserve assertions while crossing the shared/native path. Collection and execution were not repeated. |

The earlier plan reviews [[00008-v2.0.0-plan-review]] and [[00009-Plan_00006_Re_Review]] concern plan 00006, not an independent set of current runtime findings. Plan 00007 describes itself as the superseding plan. This report does not declare all of that plan's acceptance criteria satisfied or retrospectively validate the historical execution records.

**New findings to disposition:** `REV-00011-MED-01`, `REV-00011-LOW-01`, `REV-00011-LOW-02`, and `REV-00011-LOW-03`. **Critical/Major blockers established by this review:** none. **Release-process/evidence gates:** still require the owner actions described above.

The uploaded source archive and all existing review files remain unchanged. Only this new Markdown report was created. Place it under the repository's `docs/reviews/` directory to retain the intended numbering and Obsidian cross-links; this downloadable copy does not modify or publish to GitHub.

## Confidence

**Medium overall; high for the specific static control-flow defects.** All supplied production Python/Rust code, test source, and release definitions in the declared scope were inspected, and the findings have concrete locations, scenarios, and verification steps. Confidence is limited by absent Git comparison/provenance verification, unexecuted project checks, no supplied compiled artifacts, and the distinction between builder-reported historical results and exact-candidate evidence; this is not proof that the cryptographic implementation or release is defect-free.
