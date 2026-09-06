---
title: "Code Review 00005: Idea 00001 v2.0.0 Optional Rust Accelerated Backend"
aliases:
  - "Review 00005"
  - "Idea 00001 review"
tags:
  - code-review
  - software-quality
  - idea-review
  - performance
  - opencode
type: code-review
status: open
review_id: "00005"
reviewed_at: "2026-09-05T14:38:38Z"
reviewer_agent: general
review_model: "anthropic/claude-opus-5"
triggered_by: "user"
review_kind: initial
previous_review: null
repository: "joelee/fpr-ff1"
branch: "plan/v2.0.0"
review_mode: working-tree
pr_reference: null
commit: "9bf6c3ae13d1b5004f961c5f7640f36fd9cbc6a1"
base_ref: "main"
base_commit: "9bf6c3ae13d1b5004f961c5f7640f36fd9cbc6a1"
head_ref: "plan/v2.0.0"
head_commit: "9bf6c3ae13d1b5004f961c5f7640f36fd9cbc6a1"
scope: "untracked working-tree file docs/ideas/00001-v2_0_0_Optional_Rust_Accelerated_Backend-r01.md, reviewed against src/fpr_ff1/_ff1.py at HEAD"
related_plan: null
files_changed: 1
files_reviewed: 8
diff_additions: 489
diff_deletions: 0
blocking_issues: 2
issues:
  critical: 0
  major: 2
  medium: 4
  low: 2
  info: 0
  total: 8
categories:
  correctness: 3
  performance: 3
  tests: 0
  style: 0
  documentation: 2
verdict: request-changes
review_complete: true
web_research_used: false
confidence: high
sources: []
---

# Code Review 00005: Idea 00001 v2.0.0 Optional Rust Accelerated Backend

> [!abstract] Verdict: `request-changes`
> The idea is well-structured and its risk register is honest, but its load-bearing premise — that the `NUM`/`STR` quadratic cost is *inherent* and only Rust can address it — is measurably false: a pure-Python divide-and-conquer conversion delivers **17.9× at n=20,000 radix 10** (10–18× across radices 2/36/62/65535, 112× at radix 256), bit-exact across 84 conformance tests, at zero build or supply-chain cost. That exceeds the idea's own success threshold for the Rust backend. Revise to r02 with an optimised pure-Python control as the baseline before approving any spike.

## Review target

| Field | Value |
|---|---|
| Review mode | Working tree (untracked file) |
| PR or commit | `9bf6c3a` (`plan/v2.0.0`) |
| Base | `main` @ `9bf6c3a` |
| Head | `plan/v2.0.0` @ `9bf6c3a` |
| Branch | `plan/v2.0.0` |
| Triggered by | user |
| Related plan | None |
| Reviewed artefact | `docs/ideas/00001-v2_0_0_Optional_Rust_Accelerated_Backend-r01.md` |

## Executive summary

Idea 00001 proposes an opt-in Rust backend for `v2.0.0`, staged through a NUM/STR-only port, targeting ≥5× on small inputs and ≥3× at n=20,000. The document's structure is strong: the assumption ledger is explicit, the conformance risk (MAJ-02) is correctly identified as the dominant hazard, and the "pure-Python stays the reference and default" constraint is faithfully carried through.

The problem is the evidence layer. Assumption **A1** is recorded as a `verified-fact` — "the quadratic `NUM`/`STR` conversion is the dominant cost for large inputs" — and this review confirms it (85% of runtime at n=20,000). But the idea then treats that quadratic behaviour as *irreducible in Python* and builds the entire large-input case for Rust on top of it (`MAJ-01`: "the quadratic term is inherent to the algorithm, so Rust cannot remove it — only shrink the constant"). That inference is wrong. Base conversion is not inherently quadratic; divide-and-conquer conversion is standard, and in CPython 3.12 it rides Karatsuba multiplication to roughly **O(n^1.2)–O(n^1.3)** in practice.

Measured on this repository, at HEAD, with the shipped `_num_radix`/`_str_radix` swapped for a ~25-line pure-Python divide-and-conquer pair (see [Review coverage](#checks-performed) for method):

| Case | Shipped v1.0.0 | Pure-Python D&C | Speedup | Bit-exact |
|---|---:|---:|---:|:--|
| radix 10, n=6 | 30.4 µs | 30.9 µs | 1.0× | yes |
| radix 10, n=100 | 117.9 µs | 119.9 µs | 1.0× | yes |
| radix 10, n=1,000 | 1.50 ms | 0.93 ms | 1.6× | yes |
| radix 10, n=5,000 | 33.0 ms | 5.4 ms | 6.1× | yes |
| radix 10, n=20,000 | 506 ms | 28.3 ms | **17.9×** | yes |
| radix 2, n=20,000 | 148 ms | 14.5 ms | 10.2× | yes |
| radix 62, n=20,000 | 916 ms | 49.5 ms | 18.5× | yes |
| radix 65535, n=20,000 | 2,464 ms | 159 ms | 15.5× | yes |
| radix 256, n=20,000 (`to_bytes` fast path) | 1,114 ms | 9.9 ms | **112×** | yes |

The idea's own large-input success threshold is "≥3× (≤9 µs/numeral)" at n=20,000. Pure Python reaches **1.41 µs/numeral** — about 6× better than the target it set for Rust — with no toolchain, no wheel matrix, no second AES, and no loss of the "one code path" property the README advertises.

The two Major findings follow from this: the premise is wrong (`MAJ-01`), and because the premise is wrong, both the success measures and the staged experiment are aimed at the wrong hypothesis (`MAJ-02`). The Medium findings correct three specific claims that do not survive contact with the code (batch-API rationale, the already-dropped Rust oracle, the mis-ranked power-of-two work) and one published README claim that is now known to be false.

This is not a verdict against a Rust backend. It is a verdict that the idea, as written, cannot support a go/no-go decision — and that the **decision-relevant baseline changed**. Against an optimised pure-Python path, Rust's remaining case is the *small-input* regime, where measurement shows 55% of an n=6 call is `cryptography`'s per-call `Cipher(...).encryptor()` construction and the theoretical ceiling for a full Rust core is roughly 8×. That is a real case, but it is a different case than the one the idea argues, and it points at Option A (the highest-risk option) rather than Option B.

## Issue summary

| Severity | Count | Merge impact |
|---|---:|---|
| Critical | 0 | Blocks merge/release |
| Major | 2 | Blocks merge/release |
| Medium | 4 | Changes requested |
| Low | 2 | Non-blocking |
| **Total** | **8** | |

## Findings

### Critical

None.

### Major

#### REV-00005-MAJ-01 — The idea's central premise is false: the `NUM`/`STR` quadratic cost is an implementation choice, not an algorithmic invariant

> [!warning] Blocking
> - **Confidence:** High
> - **Category:** Correctness (of the analysis) / Performance
> - **Location:** `docs/ideas/00001-v2_0_0_Optional_Rust_Accelerated_Backend-r01.md:135-137` (§3), `:250-259` (`IDEA-00001-R01-MAJ-01`), `:357` (Option C row), `:66` (abstract) — and the source claim at `README.md:229-234`
> - **Evidence:** The idea states the opportunity is "a constant-factor speedup (**not an asymptotic one** — the algorithm's `NUM`/`STR` steps are inherently quadratic)" (§3) and, in its own `MAJ-01`, "The quadratic term is inherent to the algorithm, so Rust cannot remove it — only shrink the constant and the per-round overhead." The shipped implementation is a digit-at-a-time loop:
>   ```python
>   # src/fpr_ff1/_ff1.py:471-477
>   def _str_radix(value: int, radix: int, length: int) -> list[int]:
>       out = [0] * length
>       for i in range(length - 1, -1, -1):
>           out[i] = value % radix
>           value //= radix
>       return out
>   ```
>   That loop is quadratic. Base conversion is not. Replacing both helpers with textbook divide-and-conquer (recursive split, `divmod` by a memoised `radix**k`, naive loop below a 64-numeral threshold) measures **O(n^1.29)** for `STR` and **O(n^1.21)** for `NUM` across v = 2,500 → 25,000, against the shipped loop's clean O(n²) (16.3× cost for 4× input). Per-half at v = 10,000: `_str_radix` 36,234 µs → 953 µs (**38.0×**); `_num_radix` 7,084 µs → 645 µs (**11.0×**). End to end the effect is the table in the executive summary. All 84 tests in `test_nist_vectors`, `test_intermediates`, `test_frozen_kat`, `test_exact_arithmetic`, `test_properties` and `test_interoperability` pass unmodified against the D&C conversion, so the result is bit-exact including per-round intermediates.
> - **Failure or attack scenario:** The idea is approved on its stated premise. A 1–2 day Rust spike is run, reports (say) 4× at n=20,000 against the v1.0.0 baseline, and is read as a success against the "≥3×" threshold. `v2.0.0` then ships a Rust toolchain, a platform wheel matrix, a second AES implementation and a permanent two-implementation maintenance burden — to deliver **less than a quarter** of what a 25-line pure-Python change delivers for free, on a path the conformance suite already covers.
> - **Impact:** Mis-directed major-version investment; permanent expansion of build and supply-chain surface for a security library whose stated selling point is "one code path, and it is the one the vectors test" (`README.md:205`); and a strategic miss — the 17.9× is available **now**, ciphertext-identical, and therefore shippable as a SemVer *minor* (arguably patch) release rather than being gated behind a major version.
> - **Recommendation:** Revise to r02. Reclassify A1's corollary from `verified-fact` to `refuted`: keep "NUM/STR dominates at large n" (confirmed), drop "therefore only Rust can help". Promote Option C from "bounded speedup / no win for general radices" to the measured baseline, and re-derive §5, §11, §12 and §14 against it. Do **not** apply the optimisation as part of this review.
> - **Suggested verification:** Land the D&C conversion behind the existing suite and confirm all 84 conformance tests plus the differential and bijectivity suites remain green; add a boundary test at the recursion threshold (lengths 63/64/65/128/129) and a differential test asserting D&C output equals the naive loop across every supported radix. Re-run `just bench` and compare against the published README table.
> - **References:** `src/fpr_ff1/_ff1.py:463-477`; `benchmarks/timing.py`; `README.md:215-234`; repository measurement (CPython 3.12.13, macOS Apple Silicon, this working tree).

#### REV-00005-MAJ-02 — The staged experiment tests the wrong hypothesis against the wrong baseline, so it cannot produce the go/no-go it promises

> [!warning] Blocking
> - **Confidence:** High
> - **Category:** Feasibility / Testing methodology
> - **Location:** `docs/ideas/00001-v2_0_0_Optional_Rust_Accelerated_Backend-r01.md:167-174` (§5 success measures), `:406-431` (§14 experiment), `:356` (Option B), `:362-364` (§12)
> - **Evidence:** §14 stages the spike as "(1) port `_num_radix`/`_str_radix` to Rust and benchmark in isolation; (2) port the full Algorithm 7 core", and §12 selects "Option A as the target, staged through Option B (NUM/STR first) to measure where the time actually goes". Profiling shows where the time actually goes, and it is regime-dependent:
>   ```text
>   n=6, radix 10 (total 31.09 µs/op)
>     10 × _prf                     19.39 µs   62.4%
>       of which Cipher().encryptor() ctor  17.10 µs   55.0%   <- cryptography binding overhead
>     remaining Python core         10.57 µs   34.0%
>     _prepare validation            1.13 µs    3.6%
>     _num_radix + _str_radix        ~1.5 µs    ~5%     <- what stage 1 ports
>
>   n=20,000, radix 10 (total 506 ms)
>     _str_radix (×10)              363 ms     70%
>     _num_radix (×10)               71 ms     14%
>     everything else                72 ms     16%
>   ```
>   Stage 1 therefore addresses ~5% of the small-input cost — it will measure ≈1.0× against the ≥5× target — and at large n it will be *compared against a baseline that pure Python already beats by 17.9×* (MAJ-01). Every §5 target is anchored to the v1.0.0 published numbers ("~32,000 ops/s", "26.8 µs"), which after MAJ-01 is no longer the decision-relevant control.
> - **Failure or attack scenario:** The spike runs as specified. Stage 1 returns ≈1.0× on small inputs and a large-looking multiple at n=20,000; the multiple is read against the stale v1.0.0 baseline and the project proceeds to Option A. Alternatively stage 1 returns ≈1.0× overall, the idea is parked under its own "<2× → park" rule, and the *genuine* small-input opportunity — 55% of an n=6 call spent constructing `cryptography` cipher contexts, which a full Rust core with in-process AES would eliminate — is discarded along with it. Either way 1–2 developer-days produce a decision that does not follow from the data.
> - **Impact:** The single experiment the idea nominates as decision-enabling (§14 "Decision enabled: Go/no-go on the full Rust backend") cannot discharge that role. A wrong go or a wrong no-go both cost the project a major version.
> - **Recommendation:** Restructure §14 into two experiments with an explicit control. **E1 (do first, ~half a day, no Rust):** land D&C conversion + a power-of-two `to_bytes`/`from_bytes` fast path in pure Python, run the full conformance suite, re-run `just bench`; this both delivers value and establishes the real baseline. **E2 (only if E1 leaves a gap worth closing):** a Rust spike scoped to the *small-input* regime and to Option A only (full core with Rust AES), since Option B is now known to be inert there. Re-state §5 targets as multiples of the **E1** numbers, not the v1.0.0 numbers, and record the Amdahl floor from `REV-00005-LOW-01`.
> - **Suggested verification:** Before approving E2, require a stated hypothesis of the form "≥N× over the E1 pure-Python path at n ∈ {6, 100}" with N justified against the measured ~8× ceiling (31.09 µs → ~1.13 µs validation + ~2.3 µs real AES + PyO3 boundary).
> - **References:** `src/fpr_ff1/_ff1.py:480-489` (`_prf`), `:307-346` (`_prepare`); `benchmarks/timing.py`; repository profiling (cProfile + adaptive-batch median timing, method as `benchmarks/timing.py`).

### Medium

#### REV-00005-MED-01 — The batch API's stated rationale does not hold against the code

- **Location:** `docs/ideas/00001-v2_0_0_Optional_Rust_Accelerated_Backend-r01.md:383-387` (§12 candidate feature 1), `:182`
- **What:** The idea ranks a batch API (`encrypt_many`/`decrypt_many`) as the top candidate 2.0 feature because it "amortises the AES schedule and P-block construction across many inputs". Both amortisations already exist or cannot be had.
- **Why it matters:** This is the highest-ranked new *public API* in the proposal — a permanent surface addition with its own conformance story (the idea says so) — justified by a benefit that is not there. Public API added on a false premise is expensive to remove later.
- **Evidence:**
  ```python
  # src/fpr_ff1/_ff1.py:223-227 — AES schedule is built once per INSTANCE, already
  # amortised across every call; a batch API amortises nothing further.
  algorithm = algorithms.AES(key)
  self._aes = _Aes(algorithm=algorithm, cbc_zero_iv=modes.CBC(b"\x00" * 16))
  ```
  The P block is already loop-invariant and built once per call (`_ff1.py:522-530`), but it depends on `n` and `len(tweak)`, so it is shareable across inputs only when every input has identical length and tweak. The one per-call cost a batch API could genuinely amortise is Python method-dispatch and `_prepare`, measured at 1.13 µs of a 31.09 µs n=6 call — a ceiling of about **1.05×** in pure Python. (A batch API does have a real rationale under a Rust backend, where it amortises PyO3 boundary crossings; that is a different argument and the idea does not make it.)
- **Suggested fix:** In r02, either drop the batch API from the candidate list or re-justify it on its actual merit — boundary-crossing amortisation for an accelerated path, and caller ergonomics — with a measured ceiling. Note that it is a new public API and therefore in tension with the "small surface" rule that killed the migration shim (`docs/backlog.md`, Decided).

#### REV-00005-MED-02 — The Rust `fpe` second oracle was already evaluated and dropped; the idea re-proposes it without reconciling the recorded rationale

- **Location:** `docs/ideas/00001-v2_0_0_Optional_Rust_Accelerated_Backend-r01.md:390-393` (§12 candidate feature 3), `:182`, `:243-246`, `:269`
- **What:** The idea proposes adding the Rust `fpe` crate as a second differential oracle "at near-zero marginal cost once Rust is in the build", and leans on it as mitigation in two of its own findings (`MAJ-02`, `MED-02`). `docs/backlog.md` already records this under **Dropped Items** with a specific rationale, and the idea's own §2 acknowledges the note exists ("`docs/backlog.md` (2.0 item + dropped Rust-oracle note)") without ever addressing it.
- **Why it matters:** A dropped decision that reappears as an unqualified recommendation erodes the value of the backlog as a decision record, and here it is doing structural work: it is cited as the mitigation for the highest-impact risk in the document (bit-exact divergence, whose impact the idea rates Critical).
- **Evidence:**
  ```markdown
  # docs/backlog.md — Dropped Items
  - **Rust `fpe` crate as a second differential oracle.** The Python oracle is validated
    against all nine NIST vectors before use and agrees byte-exact across every supported
    radix; a Rust toolchain across nine matrix legs is disproportionate cost. Revisit only
    if `ubiq-security-fpe` becomes uninstallable.
  ```
  The "revisit only if" condition has not been met. The idea's counter-argument — that the cost calculus changes once Rust is in the build anyway — is reasonable but is never stated as a reversal, and it is circular when used to *justify* putting Rust in the build.
- **Suggested fix:** In r02, state explicitly that this reverses a recorded drop, give the condition under which the reversal holds (Rust already required for the backend — i.e. it is a *consequence* of the go decision, never an input to it), and remove it from the mitigation column of `MAJ-02`/`MED-02` so those risks are costed against mitigations that exist today. If 2.0 lands without Rust, the drop stands unchanged.

#### REV-00005-MED-03 — The power-of-two fast path is ranked Low and framed as "not a driver", but it is the largest measured win in the entire proposal

- **Location:** `docs/ideas/00001-v2_0_0_Optional_Rust_Accelerated_Backend-r01.md:327-336` (`IDEA-00001-R01-LOW-02`), `:136-137`, `:388-390`
- **What:** The idea correctly spots that power-of-two radices admit an O(n) bit-manipulation conversion (§3), then files the associated work as `LOW-02` titled "Radix 65536 is a natural 2.0 addition but **is a minor change, not a driver**", with impact "Minor scope/versioning confusion".
- **Why it matters:** The severity is inverted relative to the evidence. Power-of-two radices are currently the library's **worst**-performing configurations, and the fix is the cheapest available.
- **Evidence:** At n=20,000 the shipped implementation takes **1,114 ms** for radix 256 versus 506 ms for radix 10 — power-of-two radices are 2.2× *slower* than radix 10, because `radix**v` is a larger integer. Substituting `int.from_bytes`/`int.to_bytes` (exact, no float, no new dependency) for the conversion at radix 256:
  ```text
  _str_radix, v=10,000, radix 256:   78,440 µs  ->  to_bytes  21 µs   (3,730×)
  full encrypt, n=20,000, radix 256:  1,114 ms  ->     9.9 ms         (  112×)
  ```
  Bit-exact; round-trip verified. Radix 65536 generalises this to 2-byte units and completes the set.
- **Suggested fix:** In r02, promote this from `LOW-02` to a first-class workstream alongside the D&C conversion, and separate its two halves: the **fast path** (pure optimisation, no behaviour change, ships in a minor/patch release) from the **radix 65536 domain widening** (accepts new inputs — a SemVer minor per `docs/backlog.md` version policy, review 00004 MED-05). Only the second half is a versioning question; the idea currently conflates them.

#### REV-00005-MED-04 — The published README performance claim is now known to be false and steers users toward a 2.0 that may not be needed

- **Location:** `README.md:229-234`
- **What:** The README tells users the quadratic conversion "is inherent to the algorithm's `NUM`/`STR` steps, not an implementation defect" and that "the 2.0 optional accelerated backend in the roadmap exists precisely for this regime". `MAJ-01` refutes the first clause; the second then misdirects.
- **Why it matters:** This text is published on PyPI and is the origin of the idea document's premise — the idea inherited the error rather than introducing it, so fixing the idea alone leaves the source in place. It also has a user-facing cost: a caller sizing a nightly batch job today is being told the only remedy is to wait for a major version, when a 17.9× improvement is available without one.
- **Evidence:**
  ```markdown
  # README.md:229-234
  The per-numeral cost climbs sharply past ~1,000 numerals: ... and that conversion is
  quadratic in pure Python. This is inherent to the algorithm's `NUM`/`STR` steps, not an
  implementation defect.
  ```
  Contradicted by the measurements in `MAJ-01` (pure Python, same interpreter, bit-exact).
- **Suggested fix:** Correct the claim in the same change that lands the D&C conversion, per `docs/AGENTS.md` ("Update docs in the same change that makes them true"): state that the *current* conversion is quadratic and that subquadratic conversion is available, and re-run `just bench` to refresh the table. Until that change lands, soften "inherent to the algorithm" to "quadratic in the current implementation". The roadmap sentence should not promise 2.0 as the remedy for a regime a 1.x release can address.

### Low

#### REV-00005-LOW-01 — The Python-side validation floor is unaccounted for in the §5 targets

- **Location:** `docs/ideas/00001-v2_0_0_Optional_Rust_Accelerated_Backend-r01.md:167-174` (§5)
- **What / Why / Suggested fix:** `_prepare` runs entirely in Python for both backends — `_coerce_numerals` calls `_require_int` once per numeral (`src/fpr_ff1/_ff1.py:286-305`). Measured: **643 µs at n=5,000 and 2,586 µs at n=20,000**. Against the D&C pure-Python total of 28.3 ms that is a 9.2% Amdahl floor; against a hypothetical zero-cost core it is the *entire* remaining cost. Any §5 target expressed as a multiple must therefore be stated against a stated floor, and the idea should note that moving validation into Rust to escape the floor would change exception messages and the `FF1Error` type mapping — a compatibility question the "bit-exact, same exceptions" non-negotiable (§2) does not currently cover.

#### REV-00005-LOW-02 — `docs/ideas/AGENTS.md` is referenced as a maintained contract but does not exist

- **Location:** `docs/AGENTS.md:13`; `docs/ideas/`
- **What / Why / Suggested fix:** `docs/AGENTS.md` lists "`docs/ideas/AGENTS.md`: contract for any agent writing idea reports under `docs/ideas/`" among maintained documents, but the directory contains only the idea report itself. The `docs/reviews/` and `docs/plans/` siblings both have their contract file. Idea 00001 is consequently the first artefact in a directory with no written contract governing numbering, revision suffixes (`-r01`), immutability, or the front-matter schema it nonetheless uses — so there is nothing to check its `revision_kind`, `root_revision` or `status` transitions against. Write `docs/ideas/AGENTS.md` before r02, or remove the line from `docs/AGENTS.md`.

## Open questions

1. **Is the "one code path" property worth more than the small-input win?** After `MAJ-01`, the residual Rust case is roughly 8× on short inputs. `README.md:205` sells 1.0 as "one code path, and it is the one the vectors test", and `AGENTS.md` sets the goal that "a reviewer can compare the source against SP 800-38G line by line and find no gaps". Resolved by the maintainer, not by measurement — but it should be decided *after* E1 rather than before, because E1 changes what is being traded away.
2. **Does the D&C conversion itself violate "prefer clarity over cleverness"?** Recursive conversion with a memoised power cache is materially less line-by-line comparable to SP 800-38G than the current five-line loop. Resolvable by keeping the naive loop in the module as the documented reference implementation and asserting equivalence in a differential test across every supported radix — worth deciding explicitly rather than discovering in review.
3. **Where does the power cache live?** In the prototype the `radix**k` cache is call-local and passed down the recursion. Hoisting it to the instance would be an obvious optimisation and would introduce **shared mutable state**, breaking the thread-safety contract that `_ff1.py:106-118` and `:120-129` were specifically written to guarantee. Any r02 or plan must state this constraint; it is exactly the class of "plausible but wrong" change `AGENTS.md` warns about.
4. **Do the Rust crates named in §9 actually fit?** The idea records `cosmian_fpe` as using `crypto_bigint`, which is fixed-width; whether it can represent an n = 20,000 numeral half at all is unverified, and `fpe`'s `num-bigint` is not established as faster than CPython's `int` for these sizes. A2 is `hypothesis`-classified so this is not a defect in the idea, but it is the assumption most likely to collapse E2 and no cheap test for it is recorded. Resolved by a 30-minute crate-level microbenchmark of `num-bigint` divmod at 33k-bit operands versus CPython, before committing to E2.
5. **Recursion depth is not a constraint** — confirmed, not an open risk: D&C depth is ~9 at n=20,000 and ~14 at n=2²⁰, against a default `recursionlimit` of 1000. Recorded here so r02 need not re-litigate it.

## Review coverage

### Files and areas reviewed

- `docs/ideas/00001-v2_0_0_Optional_Rust_Accelerated_Backend-r01.md` (full, 489 lines) — the review target
- `src/fpr_ff1/_ff1.py` (full, 631 lines) — every claim in §3, §4 and §10 traced to source
- `README.md` §Roadmap and §Performance (lines 201–234)
- `AGENTS.md` — scope, standards baseline, "Never do", open decision 1
- `docs/backlog.md` — 2.0 item, Decided, Dropped Items
- `docs/AGENTS.md`, `docs/reviews/AGENTS.md` — directory contracts
- `benchmarks/timing.py` — baseline methodology, reused for this review's measurements
- `tests/` — suite inventory; six conformance modules executed (see below)

### Checks performed

- Claim-by-claim tracing of the idea's §3/§5/§10/§12 assertions to `_ff1.py` and to `docs/backlog.md`
- **cProfile** of `FF1.encrypt_numerals` at n=6 (20,000 calls) and n=20,000 (20 calls), radix 10
- **Component timing** with the harness methodology from `benchmarks/timing.py` (adaptive batch size, median of batches): `_num_radix`, `_str_radix`, `_prf`, `Cipher(...).encryptor()`, `_prepare`, `radix**v`
- **Prototype comparison:** a ~25-line pure-Python divide-and-conquer `_num_radix`/`_str_radix` pair (threshold 64, memoised `radix**k`) plus a power-of-two `to_bytes`/`from_bytes` fast path, monkeypatched over the module globals; end-to-end timing and ciphertext equality at radices 2/10/36/62/256/65535 across n = 6 … 20,000, with `decrypt_numerals` round-trip verification
- **Conformance execution:** 84 tests across `test_nist_vectors.py`, `test_intermediates.py`, `test_frozen_kat.py`, `test_exact_arithmetic.py`, `test_properties.py`, `test_interoperability.py`, run against the D&C prototype — all passed, establishing bit-exactness including per-round `P/Q/R/S/y/m/c/C` intermediates
- Scaling-exponent fit for the D&C conversions across v = 2,500 → 25,000
- Review numbering allocated under `docs/reviews/.review-number-lock` per `docs/reviews/AGENTS.md`

### Checks not performed

- **No source file was modified.** All prototype work was monkeypatched in a scratch directory; `src/`, `tests/`, `README.md`, `docs/backlog.md` and the idea document are untouched by this review.
- No Rust prototype was built, so the idea's central quantitative question — how fast Rust actually is here — remains unmeasured by this review. `MAJ-01` and `MAJ-02` are claims about the *pure-Python control*, not disproofs of the Rust case.
- Single machine, single interpreter (CPython 3.12.13, macOS Apple Silicon, this working tree). Not reproduced across the 3.12/3.13/3.14 × Linux/macOS/Windows matrix; CPython's big-integer paths differ by version, so the exact multiples will vary. The 3.13/3.14 direction is untested and could move the numbers either way.
- Linters, type checkers, the full `just quality` gate, the coverage floor and the differential/bijectivity suites were not run against the prototype (the six conformance modules above were).
- No external research; crates.io and PyO3 claims in the idea's §9 were not independently verified (see Open question 4).
- The prototype is a correctness-and-timing probe, not a production candidate: it has no type annotations, no threshold tuning, and no test coverage of its own.

## Positive notes

- The idea's risk register is genuinely good. `IDEA-00001-R01-MAJ-02` correctly identifies bit-exact conformance across a second implementation as the dominant hazard and reaches for the right evidence (per-round intermediates, not just output equality) — that is the project's own hard-won lesson applied properly.
- `IDEA-00001-R01-MAJ-03` self-reports the AGENTS.md contract conflict rather than routing around it, and the "Conditions to revise, park, or reject" section (§10) pre-commits to a park threshold. Both are the marks of an honest proposal; the park rule in particular is what makes this review's evidence actionable rather than adversarial.
- The assumption ledger's classification discipline is what made this review tractable: A2 and A6 are correctly marked `hypothesis` and `unknown` with Low/Medium confidence, which is precisely why the false inference sits in A1's *corollary* rather than in the ledger itself.
- The constant-time caveat in §10 ("a Rust backend may reduce but cannot eliminate value-dependent timing... claiming otherwise would be a security misrepresentation") is exactly right and consistent with `SECURITY.md`'s published posture.
- On the code side: `_ff1.py`'s spec-step comments and the explicit "never `math.log2`" warning at `:512-514` made every §3 claim checkable in minutes. The `_Aes` NamedTuple docstring explaining *why* no encryptor is cached is what let this review flag Open question 3 without re-deriving the thread-safety argument.

## External references

None. All findings rest on repository evidence and on measurements taken against this working tree; the idea's own external sources (PyO3, maturin, crates.io) were not re-verified.

## Recommended next actions

1. **Do not approve the §14 spike as written** (`MAJ-02`). It cannot discharge the go/no-go role assigned to it.
2. **Revise Idea 00001 to r02** (`MAJ-01`): reclassify the A1 corollary, promote Option C to the measured control, and re-derive §5, §11, §12 and §14 against it. Fold in `MED-01` through `MED-04` and `LOW-01`. Record in §16/§17 that r01's premise was refuted by this review, per the idea's own revision protocol.
3. **Run E1 first** — pure-Python D&C conversion plus a power-of-two fast path, behind the full conformance suite, with a threshold-boundary test and a differential test against the retained naive loop (`MAJ-01`, `MED-03`). Ship it as a **1.x** release: ciphertext is unchanged for every input valid in 1.0.0, so this is not a major version. Update `README.md` §Performance in the same change (`MED-04`) and `docs/backlog.md`.
4. **Then re-ask the 2.0 question** with the new baseline (`MAJ-02`, Open question 1). Scope E2 to the small-input regime and to Option A only; settle Open question 4 with a crate-level microbenchmark before spending the spike budget.
5. **Write `docs/ideas/AGENTS.md`** before r02 lands (`LOW-02`).
6. Carry Open questions 2 and 3 into whichever plan implements E1 — particularly the power-cache/thread-safety constraint, which is a `AGENTS.md` "Never do" class hazard.

## Handoff

To the maintainer: this review's substantive request is a **re-baselining**, not a rejection of the Rust backend. The `v2.0.0` roadmap line as written — "an opt-in faster path for high-throughput callers" — is very likely satisfiable as a `1.1.0` for the long-input regime the README specifically calls out, which would leave `2.0` free to be decided on the small-input case alone, on its merits, with real numbers on both sides.

Idea 00001 r01 should move to `status: superseded` when r02 is written; it is otherwise sound work whose conclusion changed when the control was measured. No code, test, or documentation file was modified by this review, so nothing here needs reverting. The concrete next artefact is either Idea 00001 r02 or a delivery plan for E1 — E1 is independently valuable and does not depend on the 2.0 decision, so it can start immediately.

Note on this file's name: `docs/reviews/AGENTS.md` specifies `Title_Case_With_Underscores` for the description segment; the filename `00005-idea-00001-Opus_review.md` was specified explicitly by the user and is used as given. The `00005` allocation followed the locking protocol.

## Confidence

**High.** The two Major findings rest on direct measurement against this working tree, cross-checked six ways (cProfile, component timing, end-to-end timing, scaling-exponent fit, ciphertext equality, and 84 passing conformance tests including per-round intermediates), and the effect size — 17.9× at n=20,000, 112× at radix 256 — is far too large to be measurement noise or an artefact of one machine. The principal uncertainty is not whether pure Python wins here but *by how much on other interpreters and platforms*: CPython's big-integer division and multiplication paths changed in 3.12 and are not identical on 3.13/3.14, and all measurements come from one macOS Apple Silicon machine. That uncertainty affects the size of the multiple, not the direction of the finding or the conclusion that r01's premise cannot stand.
