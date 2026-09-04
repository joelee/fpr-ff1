---
title: "Code Review 00001: Publication Readiness Deep Dive"
aliases:
  - "Review 00001"
tags:
  - code-review
  - software-quality
  - opencode
type: code-review
status: open
review_id: "00001"
reviewed_at: "2026-09-03T11:21:15Z"
reviewer_agent: review
review_model: "ollama-cloud/glm-5.3"
triggered_by: "user"
review_kind: initial
previous_review: null
repository: "joelee/fpr-ff1"
branch: null
review_mode: repository
pr_reference: null
commit: null
base_ref: null
base_commit: null
head_ref: null
head_commit: null
scope: "Whole-repository publication-readiness review (working tree, not a git checkout)"
related_plan: "AGENTS.md (agent contract); docs/backlog.md (pre-1.0 items)"
files_changed: 0
files_reviewed: 33
diff_additions: 0
diff_deletions: 0
blocking_issues: 3
issues:
  critical: 0
  major: 3
  medium: 5
  low: 3
  info: 0
  total: 11
categories:
  security: 2
  correctness: 1
  reliability: 2
  tests: 1
  documentation: 2
  packaging: 2
  maintainability: 1
verdict: request-changes
review_complete: true
web_research_used: true
confidence: high
sources:
  - https://github.com/joelee/fpr-ff1
  - https://github.com/joelee/fpr-ff1/actions
  - https://pypi.org/pypi/fpr-ff1/json
  - https://github.com/pyca/cryptography/issues/9110
  - https://github.com/pyca/cryptography/issues/12489
  - https://csrc.nist.gov/CSRC/media/Projects/Cryptographic-Standards-and-Guidelines/documents/examples/FF1samples.pdf
---

# Code Review 00001: Publication Readiness Deep Dive

> [!abstract] Verdict: `request-changes`
> The FF1 core, test suite, and packaging metadata are publication-grade — but the release pipeline is currently broken (the PyPI publish failed and its fix is stranded in an unmerged PR), the local tree has diverged from the published GitHub repo, and the public repo ships local-only tooling artifacts that do not belong in a published open-source project.

## Review target

| Field | Value |
|---|---|
| Review mode | Repository (whole-repo publication-readiness review) |
| PR or commit | Working tree at `/Users/joel/Projects/MyOSS/py-fpr-ff1` — **not a git checkout** (`git status` fails: "not a git repository") |
| Base | n/a (repository review) |
| Head | n/a (repository review) |
| Branch | n/a locally; remote `joelee/fpr-ff1` default branch is `main` |
| Triggered by | user |
| Related plan | `AGENTS.md` (agent contract), `docs/backlog.md` (pre-1.0 items) |

## Executive summary

This is a deep, whole-repository review of `fpr-ff1`'s readiness for GitHub and PyPI publication, requested after the repository had already been made public and a v0.1.0 release attempted. The review covered: the FF1 core implementation (checked line-by-line against every gotcha in `AGENTS.md`), the complete test suite (all 13 test modules), packaging metadata (`pyproject.toml`, `uv.lock`), CI/CD workflows, security posture (`SECURITY.md`, `.gitleaks.toml`, `.gitignore`), and all documentation.

**The single most important finding: GitHub publication has already happened, and PyPI publication has already failed.** The GitHub repo `joelee/fpr-ff1` is public (29 commits, release v0.1.0 published, CI has run 4+ times), but the Publish workflow's release gate broke — `gitleaks/gitleaks-action` rejects `release` events outright (the comment in `ci.yml:95-99` documents this), so the release-time secret scan failed and blocked the publish. The fix (switching to the gitleaks CLI) sits in **open, unmerged PR #2** ("Use the gitleaks CLI so the release gate can run"). Meanwhile PyPI still returns 404 for `fpr-ff1` (verified 2026-09-03), so the package is not installable by the public despite the README's `pip install fpr-ff1` promise.

**The FF1 core itself is in excellent shape.** I verified every implementation gotcha from the agent contract against the source: `b` from `v` not `u` (`_ff1.py:446`), exact integer bit-length (`:446`), padding formula (`:452`), the three encrypt/decrypt differences and unmirrored parity rule (`:464-537`), `S` truncated to `d` bytes (`:492`), CBC-MAC zero-IV PRF with fresh encryptor per call (`:412-421`), the single cached ECB encryptor with no `finalize()` (`:216`, `:489`), and spec-step citations in docstrings. The test suite is exceptional — 9 NIST vectors both directions, 90 rounds of per-round intermediates, differential testing across 8 radices with an oracle validated against NIST first, exhaustive bijectivity over 2M+ points, a 50-case malformed-input sweep, and a 100% line+branch coverage gate enforced in three places. The known failure modes each have a dedicated, well-reasoned test.

The blocking issues are all in the release pipeline and repository hygiene, not in the algorithm:

1. **The publish pipeline is broken and its fix is unmerged** — the v0.1.0 release exists on GitHub but nothing reached PyPI.
2. **The local tree has diverged from the published repo** — it is not even a git checkout, and contains post-release local changes (the CLAUDE.md→AGENTS.md merge, the S-expansion fix history in CHANGELOG) whose sync state to `main` cannot be verified from here.
3. **The public repo ships local tooling artifacts** — `CLAUDE.md`, `opencode.json`, `graphify-out/`, and a live `.codegraph/` SQLite database with daemon logs, none of which belong in a published open-source project.

## Issue summary

| Severity | Count | Merge impact |
|---|---:|---|
| Critical | 0 | Blocks merge/release |
| Major | 3 | Blocks merge/release |
| Medium | 5 | Changes requested |
| Low | 3 | Non-blocking |
| **Total** | **11** | |

## Findings

### Critical

> [!success] None
> No Critical findings. The FF1 core passed a line-by-line conformance check against the agent contract; no correctness or exploitable-security defect was found in the shipped code.

### Major

#### REV-00001-MAJ-01 — PyPI publication is broken: release gate fails, fix stranded in unmerged PR #2

> [!warning] Blocking
> - **Confidence:** High
> - **Category:** Reliability / Packaging
> - **Location:** `.github/workflows/publish.yml:16-18`, `.github/workflows/ci.yml:84-108` — `Publish.quality` / `secrets` job
> - **Evidence:** The Publish workflow reuses `ci.yml` as its release gate (`publish.yml:18`). CI run #1 ("First release: NIST SP 800-38G FF1, conformance-tested", Release v0.1.0) shows the gate failing; `ci.yml:95-99` documents why: "gitleaks/gitleaks-action … rejects `release` events outright ('ERROR: The [release] event is not yet supported') … so the action failed there and blocked publishing." The fix — using the gitleaks CLI directly — is implemented in the local `ci.yml` but exists on the remote only in **open PR #2** ("Use the gitleaks CLI so the release gate can run", opened Aug 21, 2026). PyPI still returns 404 for `fpr-ff1` (verified 2026-09-03), so the v0.1.0 release published on GitHub never reached the index.
> - **Failure scenario:** A user follows the README's `pip install fpr-ff1` and gets `ERROR: No matching distribution found`. The project's core promise — a maintained replacement for a deprecated library — is unfulfillable for every user who cannot install it.
> - **Impact:** The package is publicly announced (README, release) but not publicly installable. Every day unmerged PR #2 sits, the release remains broken.
> - **Recommendation:** Merge PR #2 (or re-apply its change to `main`), then re-run the release: either re-publish the existing v0.1.0 release (re-run the failed Publish workflow via `workflow_dispatch`, which `publish.yml:10` already supports) or cut v0.1.1. Verify `https://pypi.org/pypi/fpr-ff1/json` returns 200 before announcing anything further.
> - **Suggested verification:** A green Publish workflow run and a 200 from the PyPI JSON API.
> - **References:** Repository evidence; PyPI JSON API (404 as of 2026-09-03).

#### REV-00001-MAJ-02 — Local tree is not a git checkout and has diverged from the published repo

> [!warning] Blocking
> - **Confidence:** High
> - **Category:** Reliability / Process
> - **Location:** Repository root — `git status` returns "fatal: not a git repository"
> - **Evidence:** The working directory contains no `.git` directory. The GitHub repo shows 29 commits on `main` including "Merge pull request #1 from joelee/review/45bc40f-input-validation" and the PR #2 branch `fix/gitleaks-release-event`. The local tree contains changes that post-date or diverge from this history — most visibly the CLAUDE.md→AGENTS.md merge performed in this session (CLAUDE.md deleted locally, but **still present in the remote repo's file listing**), and a CHANGELOG "Unreleased" section describing fixes (S-expansion, typed exceptions, `2**32-1` bound) whose commit state on `main` cannot be verified from a non-checkout.
> - **Failure scenario:** Any future local edit is made against an unversioned tree; the divergence between local state and `main` grows silently; the repo-hygiene tests in `tests/test_contract.py:144-169` (which check files are git-tracked) silently skip via their "not a git checkout" path, losing their protection exactly when it is needed most.
> - **Impact:** The published repo and the development tree are different codebases. Work could be lost or duplicated; the contract tests' git-tracking guarantees are void locally.
> - **Recommendation:** Re-clone (or `git init` + add remote + fetch + reset to `origin/main`, then re-apply local work as commits). Before pushing, reconcile: the local AGENTS.md merge must land on `main`, and the remote-only files (CLAUDE.md, opencode.json, graphify-out/, .codegraph/) must be removed (see MAJ-03). The `test_required_files_are_tracked_by_git` skip path is itself evidence this state was noticed and worked around rather than fixed.
> - **Suggested verification:** `git status` clean on a checkout of `main`; `git ls-files` shows no CLAUDE.md; contract tests run without the "not a git checkout" skip.
> - **References:** Repository evidence.

#### REV-00001-MAJ-03 — Public repo ships local-only tooling artifacts and a stale duplicate agent contract

> [!warning] Blocking
> - **Confidence:** High
> - **Category:** Security / Maintainability
> - **Location:** Remote repository file listing: `CLAUDE.md`, `opencode.json`, `graphify-out/`, `.codegraph/`
> - **Evidence:** The GitHub repo's root listing includes `CLAUDE.md` (deleted locally in this session's merge into AGENTS.md — the two had drifted, with CLAUDE.md carrying stale "open decisions" already decided in the repo), `opencode.json`, `graphify-out/`, and `.codegraph/` (a live SQLite database `codegraph.db` plus WAL files, `daemon.log`, `daemon.pid`, `daemon.sock`). None are covered by `.gitignore` (which has no entries for `.codegraph/`, `graphify-out/`, or `opencode.json`). The `.codegraph/daemon.log` grows with every local query and contains filesystem paths.
> - **Failure scenario:** (a) A contributor or agent reads `CLAUDE.md` and follows the stale contract (e.g. the already-decided "open decisions", the wrong `2**32` max-length) — the exact drift this session's merge fixed locally, still live on the remote. (b) `.codegraph/` churn (db, WAL, pid, socket, log) pollutes every future commit/diff and can leak local filesystem paths in `daemon.log`. (c) `graphify-out/` and `opencode.json` are personal tooling config in a public crypto library, confusing contributors about the project's actual entry points.
> - **Impact:** Conflicting agent instructions on the public repo; repo hygiene noise; minor local-path disclosure in shipped logs.
> - **Recommendation:** On `main`: delete `CLAUDE.md` (superseded by the merged AGENTS.md — push the local merge), `opencode.json`, `graphify-out/`; add `.codegraph/`, `graphify-out/`, `opencode.json` to `.gitignore` and `git rm --cached` the tracked ones. Keep AGENTS.md as the single agent contract (it is the file OpenCode and Claude both read via their standard lookup).
> - **Suggested verification:** Remote file listing shows none of the four; `git check-ignore .codegraph` succeeds; gitleaks scan stays clean.
> - **References:** Repository evidence.

### Medium

#### REV-00001-MED-01 — Thread safety of the shared ECB encryptor is undocumented and untested

- **Location:** `src/fpr_ff1/_ff1.py:216` (`self._aes = _Aes(..., ecb_encryptor=...)`), `:489` (`aes.ecb_encryptor.update(xored)`) — `FF1.__init__` / `_ff1`
- **What:** The class caches one ECB encryptor for the instance lifetime and calls `update()` on it from every encrypt/decrypt. Concurrent `update()` calls on a shared `CipherContext` are documented by pyca/cryptography maintainers as producing "inherently indeterminate results" (issue #9110: "while encryptors/decryptors can also be accessed from multiple threads, actual concurrent modification (i.e., `update` calls) produces inherently indeterminate results"; issue #12489 confirms concurrent shared use "should simply raise" under free-threaded builds). Nothing in the README, docs, or docstrings states whether an `FF1` instance may be shared across threads.
- **Why it matters:** A natural usage pattern — one `FF1` instance in a web service encrypting concurrent requests — silently produces wrong ciphertext (or raises) with no warning. For a *format-preserving encryption* library whose entire value proposition is correctness of output, silent wrong output under concurrency is a correctness risk, not a nicety. Python 3.14's free-threaded builds make this more likely to surface as hard errors.
- **Evidence:** `_ff1.py:210-217` comment: "Cipher objects reused across calls. Do not call finalize() …"; no `threading` mention anywhere in `src/`, `docs/`, or `README.md` (grep confirmed). pyca/cryptography #9110 (2023) and #12489 (2025) establish the upstream contract.
- **Suggested fix:** Document the contract explicitly ("`FF1` instances are not thread-safe; create one per thread, or serialise access") in the `FF1` class docstring, README API section, and `docs/configuration.md`. Optionally add a test asserting sequential reuse works (already covered) and a documented note that concurrent use is unsupported. A `threading.Lock` around the S-expansion would also work but adds overhead to every call; documentation is the smaller change consistent with the project's minimalism.
- **References:** pyca/cryptography #9110, #12489 (accessed 2026-09-03).

#### REV-00001-MED-02 — `README.md` claims "708 tests" — an unverifiable and already-stale number

- **Location:** `README.md:49` — "Why you can trust this implementation"
- **What:** The README hardcodes "708 tests. 100% line and branch coverage, enforced". The number is a snapshot of one moment; the suite has already grown (the local tree adds validation tests from the 45bc40f review, and PR #2 exists). Anyone running `pytest` will see a different count, and the claim silently becomes false with every added test.
- **Why it matters:** The README's trust argument is the project's core marketing; a number that doesn't match reality undermines exactly the audience it's written for. It also invites "the README says 708 but I count 712" pedantry in issues.
- **Evidence:** `README.md:49`; test count not enforced or generated anywhere (no CI step captures it).
- **Suggested fix:** Drop the specific number: "The full suite — NIST vectors, per-round intermediates, differential tests against an independent implementation, exhaustive bijectivity sweeps, and a 50-case malformed-input sweep — runs in CI with 100% line and branch coverage enforced." The composition is the claim; the count is trivia.

#### REV-00001-MED-03 — `SECURITY.md` disclosure email is a personal address with no published verification

- **Location:** `SECURITY.md:11` — "Email — oss-dev@joeworks.com"
- **What:** The security policy lists a private disclosure email at a personal domain. `joeworks.com`'s relationship to the project is not established anywhere in the repo, and the address accepts no public verification (no published key, no security.txt).
- **Why it matters:** For a cryptography library, the disclosure channel is part of the security posture. A reporter unsure whether the address is genuine falls back to public issues — the exact outcome the policy tries to prevent. GitHub private vulnerability reporting (also listed, and preferred) mitigates this substantially, which is why this is Medium and not higher.
- **Evidence:** `SECURITY.md:7-11`; no PGP key, security.txt, or domain linkage in the repo.
- **Suggested fix:** Either publish a PGP key for the address (with fingerprint in SECURITY.md), or reorder to make GitHub private reporting the sole channel until the email channel is hardened. A `.well-known/security.txt` on the domain would be the gold standard.

#### REV-00001-MED-04 — Publish workflow lacks attestation and has no release-asset step

- **Location:** `.github/workflows/publish.yml:28-41` — `publish` job
- **What:** The publish job builds and publishes via `pypa/gh-action-pypi-publish@release/v1` but does not enable PyPI trusted-publishing attestations (`attestations: true`, default-on in recent action versions but worth making explicit) and does not upload the sdist/wheel as GitHub release assets.
- **Why it matters:** Attestations are the modern supply-chain signal for PyPI packages (provable provenance: "this file was built by this repo's CI"), increasingly checked by downstream auditors and installers (`pip` verifies them with `--verify-metadata`, and `uv` does by default). A crypto library shipping without provenance attestations is a missed trust signal at odds with the project's evidence-based posture. Release assets matter less but give GitHub-first users a checksummed artefact.
- **Evidence:** `publish.yml:40-41` — bare `uses: pypa/gh-action-pypi-publish@release/v1` with no `with:` block.
- **Suggested fix:** Add `with: attestations: true` (and `print-hash: true` for build transparency). Optionally add an upload-artifact/release-asset step. Verify the `pypi` GitHub environment (referenced at `publish.yml:23-25`) has actually been configured with the Trusted Publishing publisher — the workflow comment at `publish.yml:3-5` assumes it, and the failed release means it has never been exercised end-to-end.

#### REV-00001-MED-05 — `docs/directory-structure.md` is stale: missing test modules, `_oracle/`, and reviews

- **Location:** `docs/directory-structure.md:3-33`
- **What:** The documented tree omits `tests/test_contract.py`, `tests/test_differential.py`, `tests/test_interoperability.py`, `tests/test_smoke.py`, `tests/_oracle/` (with its M2Crypto shim), `tests/conftest.py`, `tests/__init__.py`, and now `docs/reviews/`. It also omits `SECURITY.md`, `CHANGELOG.md`, `.github/`, `.gitleaks.toml`, `.gitattributes` from the root listing.
- **Why it matters:** `docs/AGENTS.md` makes updating the matching doc file part of the change that makes it true ("If … directory structure changes, update `docs/directory-structure.md`"). The tree is already materially out of date, so the rule has already been skipped at least three times. A contributor following the tree gets an incomplete map of the test suite — and the omitted `_oracle/` shim is exactly the non-obvious piece a newcomer needs to know about.
- **Evidence:** Compare `docs/directory-structure.md:18-27` against the actual `tests/` listing (13 files).
- **Suggested fix:** Regenerate the tree to match reality (or reduce it to a prose description of what belongs where, which ages better). Include the `_oracle/` note about the M2Crypto shim.

### Low

#### REV-00001-LOW-01 — `pyproject.toml` URLs match the remote, but the enforcing test is inert locally

- **Location:** `pyproject.toml:39-44`, `tests/test_contract.py:172-204`
- **What / Why / Suggested fix:** The URLs point at `joelee/fpr-ff1`, which exists and matches the remote — and `test_project_urls_match_the_git_remote` enforces this going forward (good). But the local tree is not a git checkout, so that test's skip path is active locally and the enforcement is currently inert. Once the tree is re-established as a checkout (MAJ-02), this is self-maintaining. No action beyond MAJ-02.

#### REV-00001-LOW-02 — `justfile` `secrets` recipe is unpinned locally while CI pins gitleaks 8.30.1

- **Location:** `justfile:61-67`, `.github/workflows/ci.yml:88-104`
- **What / Why / Suggested fix:** The local recipe runs whatever `gitleaks` is on PATH (unpinned), while CI pins `GITLEAKS_VERSION: "8.30.1"` and installs it on demand. Local/CI drift in scanner version can produce "clean locally, red in CI" (or worse, the reverse). Consider a `gitleaks-version` variable in the justfile mirroring CI's pin, or document the pin in the developer guide. Low because the CI pin is the authoritative gate.

#### REV-00001-LOW-03 — `.hypothesis/` directory is not gitignored

- **Location:** `.gitignore` (no `.hypothesis/` entry); `.hypothesis/` exists locally with `constants` and `examples`
- **What / Why / Suggested fix:** Hypothesis' example database is per-machine scratch; committing it would create noise and merge conflicts. It is not currently tracked (the remote listing doesn't show it), so this is preventive: add `.hypothesis/` to `.gitignore` alongside `.pytest_cache/`.

## Open questions

1. **Has the `pypi` GitHub environment actually been configured with the Trusted Publishing publisher?** `publish.yml:3-5` assumes the configuration exists at `https://pypi.org/manage/project/fpr-ff1/settings/publishing/` — but the project has never successfully published, and PyPI's project page doesn't exist yet. Trusted Publishing for a *new* project requires creating the publisher against the (not-yet-existing) project, or publishing once with an API token to establish it. This is a genuine chicken-and-egg that the failed release never got far enough to hit. Resolving it: check the GitHub environment's protection rules and the PyPI publishing configuration before re-running the release.
2. **Does the remote `main` HEAD contain the S-expansion fix and the input-validation fixes?** The CHANGELOG "Unreleased" section describes them, and PR #1 ("Close input-validation gaps from the Kimi K3 review of 45bc40f") was merged before the release. CI run #4 (the merge commit) passed the full matrix, which strongly suggests yes — but this cannot be confirmed from a non-checkout local tree (MAJ-02). Resolving it: `git ls-remote` + diff once the tree is a checkout, or trust the green CI run #4 on the merge commit.
3. **Is `oss-dev@joeworks.com` monitored and reachable?** See MED-03. Resolving it: send a test disclosure to it.

## Review coverage

### Files and areas reviewed

**Core implementation (3 files, fully read):** `src/fpr_ff1/_ff1.py` (549 lines — `FF1` class, `_ff1` core, `_prf`, `_min_length`, `_encode_uint`, all validation helpers), `src/fpr_ff1/_exceptions.py`, `src/fpr_ff1/__init__.py`. Every gotcha in `AGENTS.md` "Implementation gotchas" was checked against the source and found conformant.

**Test suite (13 files, fully read):** `test_nist_vectors.py`, `test_intermediates.py`, `test_differential.py`, `test_interoperability.py`, `test_validation.py`, `test_exact_arithmetic.py`, `test_properties.py`, `test_contract.py`, `test_smoke.py`, `conftest.py`, `_oracle/__init__.py`, `_oracle/_m2crypto_shim.py`, plus the two vector fixtures (`nist_ff1_samples.json` fully read and checked against the NIST source URL; `nist_ff1_intermediates.json` existence and consumption verified).

**Packaging and infra:** `pyproject.toml`, `uv.lock` (oracle pinning verified: `ubiq-security-fpe==2.0.1.1`, hash-pinned), `justfile`, `.github/workflows/ci.yml`, `.github/workflows/publish.yml`, `.gitignore`, `.gitattributes`, `.gitleaks.toml`, `.python-version`.

**Documentation:** `README.md`, `SECURITY.md`, `CHANGELOG.md`, `AGENTS.md`, `docs/AGENTS.md`, `docs/architecture.md`, `docs/backlog.md`, `docs/configuration.md`, `docs/developer-guide.md`, `docs/directory-structure.md`.

**Local-only state:** `.claude/settings.local.json` (read to check for secrets — none; contains only permission grants), `.codegraph/` (SQLite db + daemon artifacts), `.hypothesis/` (scratch).

**External state:** GitHub repo `joelee/fpr-ff1` (public, 29 commits, v0.1.0 release, 1 open PR, CI runs), PyPI JSON API for `fpr-ff1` (404), pyca/cryptography thread-safety issues #9110 and #12489.

### Checks performed

- Line-by-line conformance check of `_ff1.py` against every rule in `AGENTS.md` (gotchas, standards baseline, API contract, exception hierarchy)
- Arithmetic verification of the `min_length` table (2→20, 10→6, 16→5, 32→4, 36→4, 256→3, 65535→2) against `_min_length`
- Cross-check of README claims against the test suite that enforces them (bijectivity sizes, differential radices, malformed-input sweep size)
- Verification that vector fixtures are transcribed-from-NIST (source URL in fixture header) and never self-generated
- Packaging metadata review against PyPI rendering requirements (`twine check` runs in CI; classifiers, keywords, URLs present)
- CI/publish workflow logic review, including the gitleaks-action/release-event incompatibility documented in-repo
- External verification: GitHub repo state, PyPI name availability, cryptography library thread-safety contract
- Grep sweeps for: float operations in the core (none), threading mentions (none — basis for MED-01), `CLAUDE` references (none post-merge), coverage-floor claims (consistent at 100%)

### Checks not performed

- **No tests, builds, linters, or scanners were run** — this is a read-only review agent. The "708 tests / 100% coverage" claims are corroborated by CI history (runs #2–#4 green on the full matrix) but not re-executed here.
- The remote `main` HEAD content was not diffed against the local tree (impossible from a non-checkout; see MAJ-02).
- `nist_ff1_intermediates.json` was verified structurally (consumed by `test_intermediates.py` with strict per-round field assertions) but not byte-for-byte against the NIST PDF (no PDF parse attempted).
- Binary/compiled artefacts (`.codegraph/codegraph.db`) were not opened.

## Positive notes

- **The test suite is the strongest part of this project and is itself the product.** The per-round intermediate conformance test (`test_intermediates.py`) is the right design: it catches compensating bugs that output-level tests mathematically cannot. The differential suite validates its oracle against all nine NIST vectors *before* trusting it — an unusual and exemplary discipline. The exhaustive bijectivity sweeps (2M+ points) in CI are the strongest correctness statement available for a permutation.
- **The known-bug table in the README maps each published FF1 failure mode to the specific test that prevents it** — a genuinely useful piece of documentation that most crypto libraries lack.
- **The `FPR_FF1_REQUIRE_ORACLE` design** (skip locally, hard-fail in CI) solves the optional-dependency test problem correctly: a silent skip looks exactly like a pass, so CI refuses to skip.
- **The M2Crypto shim** (`tests/_oracle/_m2crypto_shim.py`) is a clean, minimal solution to an otherwise-fatal oracle dependency problem, and it deliberately fails closed on anything unexpected.
- **The contract tests** (`test_contract.py`) — every-rejection-is-typed sweep, required-files-tracked-by-git, URLs-match-remote — encode process guarantees as executable tests.
- **`SECURITY.md`'s timing analysis** (measured deltas, value-dependent vs length-dependent, with the honest conclusion that neither is a practical side channel for pure Python) is the kind of measured, non-overclaiming security documentation that builds trust.
- **The FF1 core passed every single gotcha check** — including the subtle ones (parity rule unmirrored, `S` in bytes not bits, fresh CBC encryptor per PRF, no `finalize()` on the cached ECB context). The spec-step citations in docstrings make line-by-line review against SP 800-38G actually possible, fulfilling the project's stated design goal.

## External references

- GitHub repository `joelee/fpr-ff1` — public state, commit count, PR #2, release v0.1.0, CI run history. Accessed 2026-09-03. https://github.com/joelee/fpr-ff1
- GitHub Actions runs for `joelee/fpr-ff1` — Publish #1 failed at the release gate; CI #2–#4 green on the full matrix. Accessed 2026-09-03. https://github.com/joelee/fpr-ff1/actions
- PyPI JSON API for `fpr-ff1` — 404 (name unclaimed / never published). Accessed 2026-09-03. https://pypi.org/pypi/fpr-ff1/json
- pyca/cryptography issue #9110 "Is Cipher thread-safe: Documenting thread-safety" (opened 2023-06-20) — maintainer statement that concurrent `update()` on a shared `CipherContext` produces "inherently indeterminate results". Accessed 2026-09-03. https://github.com/pyca/cryptography/issues/9110
- pyca/cryptography issue #12489 "Support free-threaded CPython (3.14t)" (2025) — concurrent shared use of stateful primitives should raise under free-threaded builds. Accessed 2026-09-03. https://github.com/pyca/cryptography/issues/12489
- NIST SP 800-38G FF1 Sample Vectors (source of `tests/vectors/nist_ff1_samples.json`). https://csrc.nist.gov/CSRC/media/Projects/Cryptographic-Standards-and-Guidelines/documents/examples/FF1samples.pdf

## Recommended next actions

1. **Merge PR #2** (gitleaks CLI fix) to `main` — unblocks the release pipeline (MAJ-01).
2. **Re-establish the local tree as a git checkout** of `main`, re-apply the AGENTS.md merge as a commit, and reconcile divergence (MAJ-02). Verify the `pypi` environment's Trusted Publishing configuration exists before re-releasing (Open question 1).
3. **Remove `CLAUDE.md`, `opencode.json`, `graphify-out/`, `.codegraph/` from the remote** and gitignore the tooling dirs (MAJ-03).
4. **Re-run the release** (re-publish v0.1.0 via `workflow_dispatch` or cut v0.1.1); confirm PyPI returns 200 and `pip install fpr-ff1` works from a clean environment.
5. Document the thread-safety contract (MED-01) and drop the hardcoded test count from the README (MED-02) — both are small doc changes that can ride along with the next release.
6. Address the remaining Mediums (SECURITY.md email hardening, publish attestations, directory-structure refresh) and Lows as follow-ups; none block the release.

## Handoff

The caller asked for a publication-readiness review. The headline: **the code and tests are ready; the pipeline is not.** GitHub publication already happened (repo public, v0.1.0 released, CI green on the full matrix), but PyPI publication failed at the release gate and the fix is stranded in unmerged PR #2 — so the package is announced but not installable. The three Major findings are all pipeline/hygiene, all fixable within a day: merge PR #2, reconcile the local non-checkout tree with `main` (pushing the AGENTS.md merge, removing the four tooling artifacts), and re-run the release after confirming the PyPI Trusted Publishing configuration. The FF1 core itself needs nothing — it passed a line-by-line check against every rule in the agent contract, and its test suite is exemplary. The Mediums are documentation and supply-chain hardening that can ride along with v0.1.1.

## Confidence

**High.** The entire source tree, test suite, packaging metadata, workflows, and documentation were read in full, and the three decisive external facts (GitHub repo state, PyPI 404, cryptography's thread-safety contract) were verified against primary sources. The principal uncertainties are all recorded as Open questions: whether the remote `main` HEAD contains the local tree's fixes (unverifiable from a non-checkout, though green CI run #4 on the merge commit is strong evidence), and whether the PyPI Trusted Publishing publisher is actually configured for a project that has never published. Neither uncertainty affects the verdict: the broken release pipeline is established fact.