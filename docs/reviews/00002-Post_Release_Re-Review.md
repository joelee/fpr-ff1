---
title: "Code Review 00002: Post-Release Re-Review"
aliases:
  - "Review 00002"
tags:
  - code-review
  - software-quality
  - opencode
type: code-review
status: open
review_id: "00002"
reviewed_at: "2026-09-03T13:02:34Z"
reviewer_agent: review
review_model: "ollama-cloud/glm-5.3"
triggered_by: "user"
review_kind: re-review
previous_review: "docs/reviews/00001-Publication_Readiness_Deep_Dive.md"
repository: "joelee/fpr-ff1"
branch: main
review_mode: working-tree
pr_reference: null
commit: "ccf8c23f6f4c8f02a57078898012733df7f51844"
base_ref: null
base_commit: null
head_ref: main
head_commit: "ccf8c23f6f4c8f02a57078898012733df7f51844"
scope: "Post-v0.1.0-release re-review: delta verification of prior findings plus release-state checks (local working tree at HEAD, compared against review 00001)"
related_plan: "AGENTS.md (agent contract); docs/backlog.md (pre-1.0 items)"
files_changed: 0
files_reviewed: 15
diff_additions: 0
diff_deletions: 0
blocking_issues: 0
issues:
  critical: 0
  major: 0
  medium: 5
  low: 2
  info: 1
  total: 8
categories:
  documentation: 3
  security: 1
  correctness: 1
  reliability: 1
  maintainability: 2
verdict: approve-with-comments
review_complete: true
web_research_used: true
confidence: high
sources:
  - https://pypi.org/pypi/fpr-ff1/json
  - https://pypi.org/project/fpr-ff1/
  - https://github.com/joelee/fpr-ff1
  - https://raw.githubusercontent.com/joelee/fpr-ff1/main/.github/workflows/ci.yml
  - https://raw.githubusercontent.com/joelee/fpr-ff1/main/.github/workflows/publish.yml
  - https://raw.githubusercontent.com/joelee/fpr-ff1/main/.gitignore
  - https://raw.githubusercontent.com/joelee/fpr-ff1/main/AGENTS.md
---

# Code Review 00002: Post-Release Re-Review

> [!abstract] Verdict: `approve-with-comments`
> v0.1.0 is properly published — PyPI is live with complete Trusted Publishing provenance, and all three Major findings from review 00001 are resolved — but the release was cut without the documentation pass the repository's own rules require: the changelog is now an empty stub behind a live PyPI sidebar link, and the backlog still asserts two now-false facts.

## Review target

| Field | Value |
|---|---|
| Review mode | Working tree (post-release delta re-review) |
| PR or commit | `ccf8c23f6f4c8f02a57078898012733df7f51844` — clean checkout, `main` tracking `origin/main`, no local changes |
| Base | Review 00001 state (pre-release working tree, not a git checkout) |
| Head | `ccf8c23` — identical to the commit attested on both PyPI artifacts (`refs/tags/v0.1.0`) |
| Branch | `main` (remote history recreated: 1 squashed commit, was 29) |
| Triggered by | user |
| Related plan | `AGENTS.md`, `docs/backlog.md` |
| Previous review | [[00001-Publication_Readiness_Deep_Dive]] |

## Executive summary

This re-review verifies the state of the project after the v0.1.0 release, against review 00001. The transformation is substantial and almost entirely positive:

**The publication pipeline works end-to-end now.** PyPI serves `fpr-ff1` 0.1.0 (wheel 16.3 kB + sdist 92.5 kB, uploaded 2026-09-03T12:46Z via Trusted Publishing, owner `joeworks`). Both artifacts carry **full provenance attestations** — in-toto statements with Sigstore transparency-log entries, publisher `publish.yml on joelee/fpr-ff1`, trigger `release`, tag `refs/tags/v0.1.0`, source permalink `joelee/fpr-ff1@ccf8c23` — and that commit is exactly the local `HEAD`. The supply-chain posture (verified provenance from repo to artifact, no tokens, pinned gitleaks in the release gate) is better than most 1.0 libraries ship with.

**All three Major findings from 00001 are resolved.** The gitleaks CLI fix is on `main` and the release gate passed (MAJ-01). The local tree is a clean git checkout whose HEAD matches the attested release commit (MAJ-02). `CLAUDE.md`, `opencode.json`, and `graphify-out/` are gone from the remote; the merged AGENTS.md is the single agent contract; `.codegraph/` now ships only a self-ignoring `.gitignore` so the database and daemon files can never be tracked (MAJ-03). Two Mediums and two Lows are also resolved (attestations, URL-matching test active again, `.hypothesis/` ignored).

**What remains is a documentation-debt tail plus one new gap created by the release itself.** The new gap: the release was cut without the docs pass that `AGENTS.md` and `docs/AGENTS.md` mandate. `CHANGELOG.md` was gutted to a 9-line stub — the entire Unreleased section (the S-expansion fix, the `max_length` `2**32-1` breaking change, the typed-exception overhaul, the Rev. 1 fail-closed note that the contract says must be "noted in the changelog") is gone, with no `[0.1.0]` section replacing it, while PyPI's sidebar "Changelog" link now lands on that empty file. `docs/backlog.md` still lists "Run CI for the first time" and "Claim the `fpr-ff1` name on PyPI" as open items and records "0.1.0 was never published" as a decided fact — all three now false. The carried-over findings (thread-safety documentation, the stale "708 tests" claim — now rendered on PyPI itself — the unverified disclosure email, the stale directory-structure doc, the gitleaks pin drift) are unchanged.

Nothing blocks the released artifact; the code at `ccf8c23` is the same tree that passed the line-by-line conformance check in review 00001. The findings below are about the record around the release, not the release itself.

## Issue summary

| Severity | Count | Merge impact |
|---|---:|---|
| Critical | 0 | Blocks merge/release |
| Major | 0 | Blocks merge/release |
| Medium | 5 | Changes requested |
| Low | 2 | Non-blocking |
| **Total** | **8** | |

## Findings

### Critical

> [!success] None
> No Critical findings. The published v0.1.0 artifacts match the source at the attested commit, which is the tree that passed the full conformance check in review 00001.

### Major

> [!success] None
> All three Major findings from review 00001 are resolved (see Handoff). No new Major findings.

### Medium

#### REV-00002-MED-01 — Release cut without the mandated docs pass: changelog gutted, backlog now false

- **Location:** `CHANGELOG.md:1-9` (entire file), `docs/backlog.md:9-12` ("Before 1.0"), `docs/backlog.md:50-51` ("Decided")
- **What:** Two documents the repository's own rules require to be updated "in the same change that makes it true" were not updated for the release, and one was actively emptied:
  - `CHANGELOG.md` now contains only its header — no `[0.1.0]` section, and the entire former Unreleased content is gone: the step 6.iii S-expansion fix, the `max_length` `2**32 → 2**32-1` breaking change, the typed-exception overhaul, the `requires-python` widening, the differential/interoperability test additions, and the Rev. 1 minimum-domain note that `AGENTS.md` explicitly requires to be "noted in the changelog". Because the remote history was squashed to a single commit, this content is not recoverable from git.
  - `docs/backlog.md` still lists as open: "Run CI for the first time. The 3.13 and 3.14 legs and the macOS and Windows legs have never executed" (they have — the release gate ran the full 9-leg matrix) and "Claim the `fpr-ff1` name on PyPI… currently unclaimed (verified 2026-08-21… 404)" (it is claimed and published). Its "Decided" section still records "`0.1.0` was never published (verified 2026-08-21)" — now false.
- **Why it matters:** The changelog is the canonical public record of behaviour changes — the README tells users (and PyPI's sidebar links directly to it) that it documents "behaviour changes that affect accepted inputs", and the project contract mandates the fail-closed minimum-domain note live there. A user clicking **Changelog** on the PyPI project page gets a file with no content. The backlog's false "Decided" entry is worse than stale — it records a verification that the release itself falsified, which misleads any future contributor or auditor reconstructing the release history. The squashed single-commit history makes the changelog the *only* surviving record, and it is empty.
- **Evidence:** `CHANGELOG.md` (9 lines, header only); `docs/backlog.md:9-12,50-51`; `AGENTS.md` ("a deliberate fail-closed choice noted in the changelog"); `docs/AGENTS.md` ("If a feature is added, dropped, blocked, or completed, update `docs/backlog.md`"); PyPI project page sidebar ("Changelog" → `CHANGELOG.md` on `main`); remote history showing "1 Commit".
- **Suggested fix:** Restore a `[0.1.0] — 2026-09-03` section to `CHANGELOG.md` (the release notes published on the GitHub release contain the substance; the prior Unreleased content is quoted in review 00001's evidence and in the release notes), including the Rev. 1 minimum-domain note and the `max_length` boundary change. Update `docs/backlog.md`: move the CI-run and PyPI-name items to Completed, and correct or remove the "0.1.0 was never published" decision entry. Both are small, purely additive doc changes suitable for one commit.

#### REV-00002-MED-02 — Thread-safety contract of `FF1` instances still undocumented

- **Location:** `src/fpr_ff1/_ff1.py:216` (`_Aes(..., ecb_encryptor=...)`), `:489` (`aes.ecb_encryptor.update(xored)`)
- **What / Why / Suggested fix:** Unchanged from review 00001 MED-01, now with higher visibility because the package is publicly installable: the class caches one ECB encryptor and calls `update()` on it from every operation; pyca/cryptography maintainers state concurrent `update()` on a shared `CipherContext` produces "inherently indeterminate results" (#9110) and should raise under free-threaded builds (#12489). A user sharing one `FF1` instance across request-handler threads gets silently wrong ciphertext. Document "instances are not thread-safe; create one per thread or serialise access" in the class docstring, README API section, and `docs/configuration.md`.
- **References:** pyca/cryptography #9110, #12489 (accessed 2026-09-03).

#### REV-00002-MED-03 — README's hardcoded "708 tests" claim is now rendered on PyPI

- **Location:** `README.md:49` — rendered verbatim on the PyPI project page
- **What / Why / Suggested fix:** Unchanged from review 00001 MED-02, but the stakes rose: the PyPI description is the README, so the unverifiable, already-drifting "708 tests" figure is now on the package's public page where it cannot be corrected without a re-release. Fix before the next release: drop the count, keep the composition ("NIST vectors, per-round intermediates, differential tests, exhaustive bijectivity, 100% enforced coverage").

#### REV-00002-MED-04 — Disclosure email still lacks published verification

- **Location:** `SECURITY.md:11` — "Email — oss-dev@joeworks.com"
- **What / Why / Suggested fix:** Unchanged from review 00001 MED-03. The PyPI ownership (`joeworks`) is now publicly visible, which slightly strengthens the address's plausibility, but it still has no published key or `security.txt`. Publish a PGP fingerprint in SECURITY.md or make GitHub private vulnerability reporting the sole channel.

#### REV-00002-MED-05 — `docs/directory-structure.md` still stale

- **Location:** `docs/directory-structure.md:3-33`
- **What / Why / Suggested fix:** Unchanged from review 00001 MED-05: the tree omits `test_contract.py`, `test_differential.py`, `test_interoperability.py`, `tests/_oracle/` (the M2Crypto shim — the least obvious piece of the suite), `conftest.py`, `SECURITY.md`, `CHANGELOG.md`, and the workflow files. Regenerate or convert to prose.

### Low

#### REV-00002-LOW-01 — `SECURITY.md` relative link is broken on the PyPI project page

- **Location:** `README.md:105` — `[SECURITY.md](SECURITY.md)`
- **What:** PyPI does not rewrite repo-relative links; on the project page this renders as a link to `pypi.org/project/SECURITY.md`, which 404s. The same applies to the `[Migrating](#migrating-from-ubiq_security_fpe)` anchor (that one works — same-page anchors are fine).
- **Why it matters:** The FIPS/limitations disclaimer directs users to `SECURITY.md` for the full statement of limitations; from PyPI that path is dead.
- **Suggested fix:** Use the absolute URL (`https://github.com/joelee/fpr-ff1/blob/main/SECURITY.md`) in the README, or accept it and fix on the next release. Cheap to fix alongside MED-03 since both require a re-release to update PyPI's rendered description.

#### REV-00002-LOW-02 — Local `justfile` gitleaks recipe remains unpinned against CI's 8.30.1

- **Location:** `justfile:61-67`, `.github/workflows/ci.yml:88-104`
- **What / Why / Suggested fix:** Unchanged from review 00001 LOW-02. CI pins `GITLEAKS_VERSION: "8.30.1"`; the local `just secrets` runs whatever is on PATH. Mirror the pin in the justfile or document it. Non-blocking: the CI pin is the authoritative gate.

### Info

#### REV-00002-INFO-01 — Review reports are local-only (untracked and git-ignored)

- **Location:** `docs/reviews/` (git-ignored locally — `git status --porcelain --ignored` shows `!! docs/reviews/`; the root `.gitignore` has no such entry, so the ignore is local, e.g. `.git/info/exclude`)
- **What:** Both review reports exist on disk but are neither tracked nor committable in the current configuration. Report 00001 survived the repository re-creation (the working tree was re-initialized in place, not re-cloned), but as untracked-and-ignored files the reports are one `git clean -fdx` or careless directory operation away from loss, and no one else can see the review history. If review history should persist, commit `docs/reviews/` (and remove the local ignore); if local-only is deliberate, keep backups. Recorded so the policy is a conscious choice rather than an accident.

## Open questions

1. **Was the changelog content deliberately dropped or accidentally lost?** The release notes on the GitHub release carry the substance, but the repo's changelog — the contract-mandated location — is empty. If the removal was deliberate (e.g. "the release notes are the record now"), the contract's "noted in the changelog" requirement and the README's description of `CHANGELOG.md` should be updated to match; if accidental, restore the content (MED-01).
2. **Is the squashed single-commit history intentional?** The 29-commit history (including PR #1's review trail) is gone; `tests/test_contract.py` comments still reference "review `45bc40f`", a commit that no longer exists in the repo's history. Harmless, but dangling references are worth a sweep whenever the file is next touched.

## Review coverage

### Files and areas reviewed

**Delta verification against review 00001 (this round, ~15 files/external sources):**
- Local tree state: `git status` (clean checkout, `main` = `origin/main`), `git rev-parse HEAD` (`ccf8c23`), `git ls-files` (full tracked listing — confirms `CLAUDE.md`/`opencode.json`/`graphify-out/` gone, `.codegraph/.gitignore` tracked, `docs/reviews/` untracked)
- `.codegraph/.gitignore` (self-ignoring pattern — MAJ-03 resolution mechanism)
- `.gitignore` (local; `.hypothesis/` entry present — LOW-03 resolved)
- `CHANGELOG.md` (full read — gutted; new finding MED-01)
- `docs/backlog.md` (full read — false pre-1.0 items; MED-01)
- `README.md` (grep: "708 tests" still present; SECURITY.md relative link)
- `SECURITY.md` (grep: disclosure email unchanged)
- `docs/directory-structure.md` (unchanged stale tree)
- Remote `main` via raw.githubusercontent.com: `AGENTS.md` (merged version confirmed live), `.gitignore`, `ci.yml` (gitleaks CLI fix confirmed), `publish.yml`
- PyPI: JSON API (metadata, digests, requires-python, ownership) and project page (rendered description, **Provenance/attestation bundles for both files**, Trusted Publishing confirmation, release history)
- GitHub repo page (file listing, 1-commit history, 0 open PRs, release published)

**Carried forward from review 00001:** the full line-by-line conformance check of `src/fpr_ff1/_ff1.py` and the complete test-suite review (13 modules) — the code at `ccf8c23` is the tree that review covered; no source file changed between that review and this release.

### Checks performed

- Release-artifact provenance verification: attestation subject digests match the published file hashes; source permalink commit matches local `HEAD`; publisher workflow and trigger event match `publish.yml`
- Prior-finding re-testing (all 11 findings from 00001 re-verified against current evidence — see Handoff)
- PyPI metadata review: classifiers, keywords, project URLs (all live), license expression, `requires-python` `<3.15,>=3.12`
- PyPI-rendered README inspection (basis for LOW-01 and the MED-03 visibility note)
- Remote-vs-local consistency: tracked file listing, AGENTS.md content, workflow content

### Checks not performed

- No tests, builds, linters, or scanners were run (read-only agent). The release gate's green run is accepted as evidence the matrix passed at `ccf8c23`.
- The wheel and sdist were not downloaded and unpacked; contents are inferred from the build config (`[tool.hatch.build.targets.wheel] packages = ["src/fpr_ff1"]`) and the passing `twine check` in the gate.
- `.git/info/exclude` was not read (permission-denied path); the `docs/reviews/` ignore is inferred from `git status --ignored` output.

## Positive notes

- **The provenance chain is exemplary.** Both PyPI artifacts carry in-toto attestations with Sigstore transparency-log entries, tied to the release tag and the exact source commit, published via Trusted Publishing with no tokens in the repo. For a v0.1.0, this is a supply-chain posture most libraries never reach.
- **All three Major findings from 00001 were resolved decisively** — the pipeline fix merged, the tree re-established as a clean checkout whose HEAD is the attested release commit, and the public repo scrubbed of tooling artifacts with a self-ignoring `.codegraph/.gitignore` as a tidy mechanism to keep it that way.
- **The merged AGENTS.md is live on the remote** — the stale duplicate contract is gone; there is now exactly one agent contract, and it is the corrected one.
- The GitHub release notes (drafted from the review's recommendation) correctly present the Unreleased fixes as first-release features per the backlog's "stages 1–4 fold into the first published release" decision — the changelog gap (MED-01) is a repo-side omission, not a release-notes one.

## External references

- PyPI JSON API for `fpr-ff1` 0.1.0 — metadata, digests, ownership (`joeworks`), upload 2026-09-03T12:46Z. Accessed 2026-09-03. https://pypi.org/pypi/fpr-ff1/json
- PyPI project page — rendered README, Trusted Publishing confirmation, attestation bundles (publisher `publish.yml on joelee/fpr-ff1`, tag `refs/tags/v0.1.0`, commit `ccf8c23`, Sigstore entries 2699377343/2699377417). Accessed 2026-09-03. https://pypi.org/project/fpr-ff1/
- GitHub repository `joelee/fpr-ff1` — file listing, 1-commit history, 0 open PRs, release state. Accessed 2026-09-03. https://github.com/joelee/fpr-ff1
- Remote `main` file contents (AGENTS.md, `.gitignore`, `ci.yml`, `publish.yml`) via raw.githubusercontent.com. Accessed 2026-09-03.
- pyca/cryptography #9110, #12489 — carried from review 00001 for MED-02. https://github.com/pyca/cryptography/issues/9110

## Recommended next actions

1. **Restore the changelog and correct the backlog** (MED-01) — one small docs commit; the contract-mandated Rev. 1 note and the `max_length` boundary change belong in a `[0.1.0]` section, and the backlog's three false statements need fixing. This is the only finding that touches the project's own recorded history, and the squashed history makes the changelog the only recoverable record — do it before the record is forgotten.
2. **Queue the README/SECURITY.md fixes for the next release** (MED-03, LOW-01): drop "708 tests", absolute-URL the SECURITY.md link. Both only reach PyPI on a re-release, so batch them.
3. **Document the thread-safety contract** (MED-02) — class docstring + README + `docs/configuration.md`; also rides along with the next release.
4. Harden the disclosure email (MED-04) and refresh `docs/directory-structure.md` (MED-05) at leisure.
5. Decide the fate of `docs/reviews/` (Info-01): commit it or accept local-only — and if local-only, note that the reports are one `git clean` away from loss.

## Handoff

Verdict: **approve-with-comments** — the release itself is sound and properly published; the findings are documentation debt, none of which taints the shipped artifacts.

Classification of all review-00001 findings against current evidence:

| Prior finding | Status | Evidence |
|---|---|---|
| MAJ-01 — PyPI publication broken (gitleaks-action rejects `release`; fix in unmerged PR #2) | **Resolved** | PyPI serves 0.1.0 (wheel + sdist, 2026-09-03T12:46Z); gitleaks CLI fix confirmed on remote `main` (`ci.yml:95-104`); release gate passed; PR list now 0 |
| MAJ-02 — Local tree not a git checkout, diverged from remote | **Resolved** | Clean checkout of `main` at `ccf8c23`, tracking `origin/main`, no local changes; HEAD matches the attested release commit exactly |
| MAJ-03 — Public repo ships tooling artifacts (`CLAUDE.md`, `opencode.json`, `graphify-out/`, `.codegraph/` db) | **Resolved** | `git ls-files` and the remote listing show the first three gone; `.codegraph/` tracked only as a self-ignoring `.gitignore` (`*` / `!.gitignore`), so db/daemon files can never be committed; remote AGENTS.md is the merged single contract |
| MED-01 — Thread safety undocumented | **Still open** | No threading mention in `src/`, `docs/`, or README; re-reported as MED-02 |
| MED-02 — "708 tests" hardcoded | **Still open, higher visibility** | Now rendered on the PyPI project page; re-reported as MED-03 |
| MED-03 — Disclosure email unverified | **Still open** | `SECURITY.md:11` unchanged; re-reported as MED-04 |
| MED-04 — Publish workflow lacks attestations | **Resolved** | Attestation bundles present on both artifacts with full provenance (the action's default-on behaviour, as the finding anticipated) |
| MED-05 — `docs/directory-structure.md` stale | **Still open** | File unchanged; re-reported as MED-05 |
| LOW-01 — URL-matching test inert locally | **Resolved** | Tree is a checkout; the contract tests' git paths are active again |
| LOW-02 — gitleaks pin drift local vs CI | **Still open** | Justfile unchanged; re-reported as LOW-02 |
| LOW-03 — `.hypothesis/` not gitignored | **Resolved** | `.gitignore:18-19` carries the entry, confirmed on remote `main` |

New findings this round: MED-01 (changelog gutted + backlog falsehoods — the release docs pass), LOW-01 (SECURITY.md relative link broken on PyPI), INFO-01 (review reports local-only and git-ignored).

## Confidence

**High.** The decisive facts were verified against primary sources: PyPI's JSON API and project page (including the attestation bundles), the remote repository's actual file contents via raw.githubusercontent.com, and the local git state (`git ls-files`, `git rev-parse`, clean status). The code itself is unchanged from review 00001's full conformance check — the local HEAD is the attested release commit. The principal residual uncertainty is the same as 00001's open question 2, now resolved in substance: the release commit demonstrably contains the fixes (it passed the full matrix and produced conformant artifacts), and the only open questions are matters of project record (changelog intent, review-history policy), not correctness.