---
title: "Plan 00001: Resolve Review 00002 Findings and Release v0.1.1"
type: plan
plan_id: "00001"
status: approved
created_at: "2026-09-03T13:02:34Z"
author_agent: opencode
author_model: "ollama-cloud/glm-5.3"
triggered_by: "user"
source_review: "docs/reviews/00002-Post_Release_Re-Review.md"
review_verdict: approve-with-comments
related_plan: "AGENTS.md (agent contract); docs/AGENTS.md (documentation rules)"
base_commit: "ccf8c23f6f4c8f02a57078898012733df7f51844"
work_items: 8
target_version: "0.1.1"
owner_decisions:
  - "Cut v0.1.1 immediately after fixes land (refreshes the PyPI project page)"
  - "SECURITY.md becomes GitHub-only disclosure channel (no email until PGP-hardened)"
  - "docs/reviews/ stays local-only (review reports not committed)"
findings_addressed:
  - REV-00002-MED-01
  - REV-00002-MED-02
  - REV-00002-MED-03
  - REV-00002-MED-04
  - REV-00002-MED-05
  - REV-00002-LOW-01
  - REV-00002-LOW-02
findings_closed_without_action:
  - REV-00002-INFO-01
plan_complete: true
---

# Plan 00001: Resolve Review 00002 Findings and Release v0.1.1

**Source:** `docs/reviews/00002-Post_Release_Re-Review.md` (verdict: approve-with-comments)
**Base commit:** `ccf8c23` on `main` (the attested v0.1.0 release commit)
**Owner decisions (2026-09-03):** cut v0.1.1 after fixes land; SECURITY.md becomes GitHub-only disclosure; `docs/reviews/` stays local-only (no plan item).

## Context

v0.1.0 is correctly published (PyPI live, full provenance attestations). All 8 open findings from review 00002 are documentation and hygiene debt — none touch the algorithm, none change accepted inputs or produced outputs, so **v0.1.1 is a patch release**. The one urgency: `CHANGELOG.md` was gutted before the release and the squashed single-commit history makes it the *only* recoverable record — it must be restored from the content preserved in review 00001's evidence and the session record (Appendix A below).

## Work items

### W1 — Restore `CHANGELOG.md` (REV-00002-MED-01, urgent)

Rebuild the file as: existing header (lines 1–7) + a new `## [0.1.0] — 2026-09-03` section containing the **verbatim content from Appendix A** (the former Unreleased section, which is the shipped 0.1.0 substance per the backlog's "stages 1–4 fold into the first published release" decision) + an empty `## [Unreleased]` heading. Do not paraphrase — this is the historical record. Note the review's Open Question 1 (deliberate drop vs. accident) is resolved in favor of restoration by owner decision to cut v0.1.1 with a corrected record.

### W2 — Correct `docs/backlog.md` (REV-00002-MED-01)

- **Delete** from "Before 1.0" (leaving the heading removed if empty): the "Run CI for the first time…" item and the "Claim the `fpr-ff1` name on PyPI…" item.
- **Add** to "Completed": `CI executed across the full 9-leg matrix; first green release-gate run at v0.1.0.` and `Claimed fpr-ff1 on PyPI, configured Trusted Publishing, and published v0.1.0 (2026-09-03) with provenance attestations on both artifacts.`
- **Replace** the "Decided" entry `**\`0.1.0\` was never published** (verified 2026-08-21)…` with: `**v0.1.0 shipped the C1/S-expansion fix** (published 2026-09-03), so no disclosure framing was needed; stages 1–4 folded into the first published release as planned.`

### W3 — Document the thread-safety contract (REV-00002-MED-02)

Add identical-substance text in three places:

1. **`FF1` class docstring** (`src/fpr_ff1/_ff1.py:123`) — append:

   > Thread safety: instances are **not** thread-safe. The instance caches a single ECB encryptor for the step 6.iii S-expansion, and pyca/cryptography documents concurrent ``update()`` calls on a shared ``CipherContext`` as producing indeterminate results. Create one instance per thread, or serialise access with a lock. There is no module-level or global state, so any number of *separate* instances may be used concurrently.

2. **`README.md`** — new `### Thread safety` subsection at the end of the API section (after Exceptions), same wording plus the practical note: "a web service handling concurrent requests should construct one `FF1` per thread (construction is cheap) rather than sharing one."
3. **`docs/configuration.md`** — new `## Thread safety` section, same wording.

**Caution:** the AST float-scan test does substring checks on `_ff1.py` source — do not include the tokens `math.log`, `math.ceil`, or float literals in the docstring text (the wording above is clean).

### W4 — `README.md` public-page fixes (REV-00002-MED-03, LOW-01)

- **Line 49** — replace `**708 tests. 100% line and branch coverage, enforced — the build fails below it.**` with:

   > **The full suite — NIST sample vectors, per-round intermediate-value conformance for every round of every sample, differential tests against an independent implementation, exhaustive bijectivity sweeps, and a malformed-input sweep — runs in CI with 100% line and branch coverage enforced. The build fails below it.**

- **Line 105** — replace `[`SECURITY.md`](SECURITY.md)` with `[`SECURITY.md`](https://github.com/joelee/fpr-ff1/blob/main/SECURITY.md)` (PyPI does not rewrite relative links; the current one 404s from the project page).

### W5 — `SECURITY.md`: GitHub-only disclosure (REV-00002-MED-04)

Restructure "Reporting a vulnerability" to a single channel: GitHub private vulnerability reporting ([draft advisory](https://github.com/joelee/fpr-ff1/security/advisories/new)). Remove the `oss-dev@joeworks.com` email line; add a note that an email channel may be added once it has a published PGP key. Keep the response-time commitments (7-day ack, 30-day assessment) and the "include version, radix, key size, reproducer" guidance unchanged. This satisfies AGENTS.md's "disclosure contact" requirement (the advisory link is the contact).

### W6 — Refresh `docs/directory-structure.md` (REV-00002-MED-05)

Replace the stale tree with one matching `git ls-files` at execution time. Required inclusions currently missing: `.github/workflows/` (ci.yml, publish.yml), `tests/test_contract.py`, `tests/test_differential.py`, `tests/test_interoperability.py`, `tests/test_smoke.py`, `tests/conftest.py`, `tests/__init__.py`, `tests/_oracle/` (note the M2Crypto shim explicitly — it is the least obvious piece), `SECURITY.md`, `CHANGELOG.md`, `AGENTS.md`, `.gitleaks.toml`, `.gitattributes`, `docs/plans/`. Omit `docs/reviews/` (local-only by owner decision) and `.codegraph/` contents (note only that the directory is self-ignored).

### W7 — Mirror the gitleaks pin in `justfile` (REV-00002-LOW-02)

Add `gitleaks_version := "8.30.1"` at the top (comment: `# mirror of GITLEAKS_VERSION in .github/workflows/ci.yml — keep in sync`). In the `secrets` recipe, before scanning, warn (not fail) if `gitleaks version` reports a different version, pointing at the CI pin as authoritative. Also add the pin to the developer guide's CI/CD section.

### W8 — Release v0.1.1 (owner-approved)

1. `pyproject.toml`: `version = "0.1.1"`, then `uv lock` (refreshes the lock's self-reference).
2. `CHANGELOG.md`: add under a new `## [0.1.1] — <date>` — documentation-only release: changelog restoration + backlog correction, thread-safety contract documented, README test-count claim replaced and SECURITY.md link made absolute, GitHub-only disclosure channel, directory-structure refresh, local gitleaks pin. End with: `No changes to accepted inputs or produced outputs.`
3. Full gate: `just quality` then `just build` (must pass — the `_ff1.py` docstring change means the whole suite, including the AST scan and 100% coverage floor, runs).
4. Commit and push; confirm the 9-leg CI matrix is green.
5. Tag `v0.1.1` and create the GitHub Release — **Title:** `v0.1.1 — Documentation release: thread-safety contract, changelog restoration, PyPI-page fixes`; **Notes:** the 0.1.1 changelog section verbatim, plus "Documentation only — no changes to accepted inputs or produced outputs."
6. The release event triggers `publish.yml` (gate → build → twine check → Trusted Publishing).
7. **Post-publish verification:** PyPI JSON API serves 0.1.1; project page renders the new README (no "708", SECURITY.md link absolute); attestation bundles present on both new artifacts.

## Execution sequence and commits

| Order | Items | Suggested commit |
|---|---|---|
| 1 | W1 + W2 | `Restore the 0.1.0 changelog and correct the backlog for the release` |
| 2 | W3 | `Document the FF1 thread-safety contract` |
| 3 | W4 + W5 + W6 + W7 | `Public-docs and repo-hygiene fixes (review 00002)` |
| 4 | W8 steps 1–3 | `Release v0.1.1` |

Run `just test-fast` after each commit for feedback; full `just quality` before push. The plan file itself (`docs/plans/00001-…md`) is committed with the work in commit 1 (it is project record; `docs/plans/` is not ignored).

## Verification checklist

- [ ] `rg -c "708" README.md` → no matches
- [ ] `rg "SECURITY.md\]\(" README.md` → absolute URL only
- [ ] `rg -i "thread" src/fpr_ff1/_ff1.py README.md docs/configuration.md` → present in all three
- [ ] `rg "joeworks.com" SECURITY.md` → no matches
- [ ] `CHANGELOG.md` contains `[0.1.0]` with the Appendix-A substance and the Rev. 1 minimum-domain note
- [ ] `docs/backlog.md` contains no "never executed" / "unclaimed" / "never published" claims
- [ ] `just quality` and `just build` pass at HEAD
- [ ] After release: PyPI JSON returns `"version": "0.1.1"` with attestations

## Out of scope (explicitly)

- `tests/test_contract.py`'s dangling "review `45bc40f`" comment references (review 00002 Open Question 2) — deferred until that file is next touched for a real reason.
- `docs/reviews/` remains local-only per owner decision (INFO-01 closed).
- No FF1 code changes of any kind; docstring text only in `src/`.

## Appendix A — Restored `[0.1.0]` changelog content (transcribe verbatim)

**Fixed**

- **FF1 produced no output at all for a large part of its declared domain.** The SP 800-38G Algorithm 7 step 6.iii `S`-expansion was implemented as `PRF(R || [j]^4)` instead of the specified `CIPH_K(R XOR [j]^16)` — a single forward-cipher block. Because the incorrect input was not block-aligned, any input reaching `d > 16` raised `ValueError` rather than encrypting. Affected every input at or above: **radix 10 → 57 numerals**, radix 36 → 37, radix 62 → 33, radix 256 → 25, radix 65535 → 13, radix 2 → 193. No NIST sample vector reaches `d > 16` (max published `d` is 12), so the branch was never exercised by the conformance suite; it is now covered by differential tests against an independent implementation, including cases with one and two expansion blocks. **This changes accepted inputs** (previously-raising inputs now succeed); no stored data is affected — nothing was ever encrypted incorrectly.
- Characters absent from the configured alphabet raised a bare `KeyError`; now `ValueRangeError` (a subclass of `FF1Error`) identifying the character and index.
- Over-long input is rejected before being materialised (`LengthError` without allocating a copy).
- **Every rejection now comes from the documented hierarchy.** Non-integer values passed validation on comparison alone; numerals, `radix`, `tweak`, `key`, `alphabet` and the string interface are type-checked, with the numeral gate using `operator.index()` (int, IntEnum, NumPy integers accepted; float, Decimal, Fraction, str raise). Generators raise `TypeError` deliberately (API misuse, not bad data) with an actionable message.
- **`bool` numerals are rejected** (previously encrypted silently as 1/0 — the coercion the contract forbids).
- A `list` alphabet was silently accepted; now raises `AlphabetError`.
- A `bytearray` key or tweak is copied at construction (mutation afterwards no longer changes ciphertext).
- Tweak bound configuration validated at construction: negative bounds raise; mutually unsatisfiable bounds report the configuration rather than blaming the default tweak.
- Corrected the SP 800-38G step citations in the FF1 core (P is step 5, steps 2/3 un-transposed, Q/R/S citations fixed).

**Changed**

- **`max_length` is `2**32 - 1`, was `2**32`.** SP 800-38G specifies `maxlen < 2**32`; the package fails closed on the boundary. Breaking by contract, but unconstructable in practice (a `2**32`-element sequence needs tens of GB).
- `requires-python` is `>=3.12,<3.15`, matching the tested CI matrix (3.12, 3.13, 3.14); raised at release time as new versions go green.
- Added PyPI classifiers, keywords, and Changelog/Security project URLs.
- `_trace` is no longer a parameter on the public methods; the per-round conformance hook is the private, test-only `FF1._encrypt_traced`.
- `P` is built once per call and the PRF reuses cached AES/CBC configuration objects (~1.3x faster; output unchanged). The CBC encryptor is still created fresh per PRF call; a CBC encryptor is never cached.

**Added**

- Differential tests against `ubiq_security_fpe` covering radices 2, 10, 16, 32, 36, 62, 256 and 65535 (agreement with an independent implementation is the only correctness evidence for radices without published vectors).
- Bidirectional interoperability tests with `ubiq_security_fpe` (all three key sizes, tweaked and untweaked) — migration strands no data.
- Property-based tests spanning the full legal radix range and lengths reaching `d > 16`.
- `SECURITY.md` with disclosure process and known limitations.
- CI across Python 3.12/3.13/3.14 on Linux, macOS and Windows, 100% line and branch coverage gate, PyPI Trusted Publishing.

**Notes for users of other FF1 libraries**

This package enforces the **SP 800-38G Rev. 1 second public draft** minimum domain, `radix ** minlen >= 1_000_000`, rather than the 2016 text's `>= 100` — a deliberate fail-closed choice. **This rejects inputs that older libraries accept** (`min_length`: 6 for radix 10, 5 for radix 16, 4 for radix 36, 3 for radix 256). Rev. 1 remains a draft; if finalised with different limits, that will be a breaking change requiring a major version.