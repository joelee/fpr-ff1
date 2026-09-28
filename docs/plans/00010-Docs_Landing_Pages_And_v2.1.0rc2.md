---
title: "Delivery Plan 00010: Docs Landing Pages And v2.1.0rc2"
aliases:
  - "Plan 00010"
tags:
  - delivery-plan
  - documentation
  - claude-code
  - release
type: delivery-plan
plan_id: "PLAN-00010"
plan_status: approved
plan_kind: superseding
created_at: "2026-09-27T11:05:41Z"
approved_at: "2026-09-27T11:14:29Z"
planner_agent: claude-code
planner_model: "anthropic/claude-opus-5-5"
triggered_by: user
request_kind: direct
repository: "joelee/fpr-ff1"
baseline_branch: "release/v2.1"
baseline_commit: "1d860d12b7334a5ac58fd12d4a3bdaf651c9f2ac"
source_ideas: []
source_reviews: []
previous_plan: "docs/plans/00009-Crate_And_v2.1.0_Release.md"
requirements_count: 13
steps_count: 11
acceptance_criteria_count: 14
blocking_decisions: 0
build_ready: true
web_research_used: false
confidence: high

# Builder-maintained front matter. Builder may update only these keys after
# explicit user approval; Delivery Planner initializes them.
implementation_status: blocked
builder_agent: claude-code
builder_model: "anthropic/claude-opus-5-5"
execution_branch: "release/v2.1"
execution_started_at: "2026-09-27T11:24:04Z"
execution_updated_at: "2026-09-28T12:15:17Z"
execution_completed_at: null
current_step: "PLAN-00010-STEP-10"
---

# Delivery Plan 00010: Docs Landing Pages And v2.1.0rc2

> [!abstract] Plan status: `approved`
> `README.md` becomes a landing page that makes the case for the library in both Python and
> Rust. The crate README becomes a landing page for Rust users. Both render correctly on
> GitHub, PyPI, crates.io and docs.rs, and are held there by tests. These changes ship as
> `2.1.0rc2` on both registries, followed by one re-review and `2.1.0`. This plan supersedes
> plan 00009's STEP-15 to STEP-17. Decisions D1 to D4 are resolved (A in each); Builder-ready.

## 1. Objective and outcome

`2.1.0rc1` is live on PyPI and crates.io. Its two READMEs are what a prospective user reads first,
and they are the pages this release is judged by. A review of them, below, finds that they
undersell the library, bury the Rust crate, and render incorrectly on both registries.

The outcome:
- A README that a Python or Rust developer can read top to bottom in a few minutes, and come away
  knowing:
  - what FF1 is for;
  - why this implementation deserves trust;
  - how to install and call it in their language;
  - what it will not do for them.
- A crate README written for Rust users rather than as a footnote to the Python package.
- Both pages correct on every site that renders them, with tests that stop them regressing.
- `2.1.0rc2` on both registries, so the rendered pages can be checked in place before `2.1.0`. The
  crate is published by CI through Trusted Publishing, so that path is exercised before the final
  release depends on it.
- The re-review and the `2.1.0` release that plan 00009 would have done, now covering rc2.

The Python package's accepted inputs, ciphertext, public API and default backend do not change.
Neither does the crate's API.

### README review (the evidence for this plan)

The planner reviewed `README.md` at `1d860d1` as a landing page, together with how it renders on
PyPI and how the crate README renders on crates.io and docs.rs.

| # | Observation | Where | Effect on a prospective user |
|---|---|---|---|
| R1 | The tagline reads "A small, correct **Python** implementation". The Rust crate first appears around line 330 of 528, after Performance and Backends | `README.md` lines 8, 330 | A Rust developer arriving from GitHub or a search does not learn the crate exists; a Python developer does not learn there is a native core behind the same API until deep in the page |
| R2 | There is no statement of what format-preserving encryption is for. The crate README has one ("a 16-digit card number to 16 digits"); the main README does not | `README.md` top; `rust/fpr-ff1/README.md` line 5 | A developer who has not met FPE cannot tell whether it solves their problem |
| R3 | The quick start does not run. It calls an undefined `load_key_from_your_secret_store()`, and its comment describes "the all-zero key here", which the code no longer uses | `README.md` lines 21–41 | The first code a user copies fails, and the comment contradicts the code |
| R4 | The page shows no known answer. Nothing lets a reader check the library against NIST in a minute | whole page | The strongest claim on the page, conformance, cannot be verified without cloning the repository |
| R5 | There are two performance tables from two machines and two eras: macOS Apple Silicon (1.1-era text, "Before 1.1.0…") and Linux x86_64 (`2.0.0`) | "Performance", "Backends" | Readers cannot compare figures, and the history reads as changelog rather than a reason to choose the library |
| R6 | Reference and history material dominates the page: the full API reference, a 60-line migration guide, the domain-limits rationale, a four-version roadmap, and the `requires-python` policy | about 300 of 528 lines | The case for the library is spread over a long page, and a reader looking for the quick answers has to wade through reference detail |
| R7 | Disclaimers are duplicated: "What this is *not*", "FIPS disclaimer" and "Key material" say overlapping things in three places | lines 138, 481, 485 | Repetition dilutes rather than strengthens them |
| R8 | The badges and licence say MIT and Python only: no crates.io, docs.rs or MSRV badge, and the licence badge omits the crate's dual licence | lines 3–6 | The first line of the page describes half the project |
| R9 | **PyPI:** two relative links, `LICENSE` and `rust/fpr-ff1/README.md`, are broken on pypi.org, which does not resolve them | `https://pypi.org/pypi/fpr-ff1/2.1.0rc1/json` `description` | Dead links on the page most Python users see |
| R10 | **crates.io:** rustdoc's hidden lines (`# let key = …`, `# Ok::<(), fpr_ff1::Error>(())`, three occurrences) and intra-doc links (`[`Error`]` renders as literal `[Error]`) appear verbatim | `https://static.crates.io/readmes/fpr-ff1/fpr-ff1-2.1.0-rc1.html` | The Rust landing page shows scaffolding and broken link syntax |
| R11 | The PyPI summary is "Format-preserving encryption: NIST SP 800-38G FF1 for Python." PyPI's project links do not include the crate | `pyproject.toml` `[project]`, `[project.urls]` | Search results and the PyPI sidebar describe half the project |
| R12 | The crate README introduces the crate as "the Rust core of the `fpr-ff1` Python package". It has no `cargo add` line, no MSRV and no docs.rs link | `rust/fpr-ff1/README.md` lines 9–12 | Reads as a by-product rather than a crate to depend on |
| R13 | The architecture diagram fails to render on GitHub (`Parse error on line 3`): an unquoted edge label contains parentheses. Fixed on `fix/architecture-mermaid` at `153aa22`, not yet merged | `docs/architecture.md` line 10 | A broken diagram on a linked page |

What the README already does well, and must keep:
- It leads with operational security consequences.
- It explains why conformance is the product.
- It names the known FF1 failure modes and the test for each.
- It is candid about what the library is not.
- The migration guide's `twk_max_len=0` trap is exactly the kind of detail that earns trust.

The plan reorganises this content. It does not soften it.

## 2. Source traceability

| Requirement | Source | Source location | Interpretation |
|---|---|---|---|
| PLAN-00010-REQ-01 | User; review R1, R8 | Request of 2026-09-27: "review `README.md` as a promotional page to entice user to consider this library, and to cover both Python and Rust implementation" | Both languages presented at the top of the page, on equal footing |
| PLAN-00010-REQ-02 | User; review R2, R4 | Same request; README top | State what FF1 is for, and show a known answer in both languages |
| PLAN-00010-REQ-03 | User; review R3 | Same request; `README.md` Quick start | Examples that run as written |
| PLAN-00010-REQ-04 | `AGENTS.md` non-negotiables; `SECURITY.md`; review R7 | "Never claim FIPS validation or key zeroization" | Every security statement and disclaimer kept, consolidated, never weakened |
| PLAN-00010-REQ-05 | User; review R6; `docs/AGENTS.md` | "`README.md`: project overview, quick start, common commands, and links to deeper docs" | Reference material moves to `docs/`; the README links to it |
| PLAN-00010-REQ-06 | Review R5; `CLAUDE.md` "`just bench` … the source of every published number" | README Performance, Backends | One performance table, from a fresh `just bench` run |
| PLAN-00010-REQ-07 | User ("cover both … Rust"); review R10, R12 | `rust/fpr-ff1/README.md` | A crate README written for Rust users that renders cleanly on crates.io and docs.rs |
| PLAN-00010-REQ-08 | Review R9, R10 | PyPI and crates.io rendered pages | Rendering constraints enforced by tests |
| PLAN-00010-REQ-09 | Review R3, R4 | README code blocks | Every example on both pages is executed or compiled by a test |
| PLAN-00010-REQ-10 | Review R8, R11 | `pyproject.toml`; README badges | Package metadata and badges describe both artifacts |
| PLAN-00010-REQ-11 | Review R13 | `docs/architecture.md`; branch `fix/architecture-mermaid` | The diagram renders |
| PLAN-00010-REQ-12 | User ("Plan for RC2"); plan 00009 REQ-12 | `.github/workflows/publish.yml` `publish-crate` | `2.1.0rc2` on both registries, rendered pages verified |
| PLAN-00010-REQ-13 | Plan 00009 REQ-12, REQ-14, STEP-15 to STEP-17 | `docs/plans/00009-Crate_And_v2.1.0_Release.md` §11 | Re-review, then `2.1.0` on both registries by CI, carried forward |

## 3. Repository baseline

| Field | Value |
|---|---|
| Repository | `joelee/fpr-ff1` |
| Branch | `release/v2.1` (4 local work-log commits ahead of `origin/release/v2.1`; its base `d3f1f97` is `main` and tag `v2.1.0rc1`) |
| HEAD | `1d860d12b7334a5ac58fd12d4a3bdaf651c9f2ac` |
| Working tree at publication | Clean |
| Published | PyPI `2.1.0rc1` (7 files, attested); crates.io `fpr-ff1` `2.1.0-rc1` (checksum `3e3b832f…0f84d25`, published by token bootstrap; Trusted Publisher configured by the owner, not yet exercised) |
| Plan 00009 | STEP-01 to STEP-14 completed; STEP-15 blocked on the owner commissioning the re-review; evidence bundle for `v2.0.0..v2.1.0rc1` in the Builder's session scratchpad |
| Other branch | `fix/architecture-mermaid` at `153aa22` (one commit on `origin/main`, unpushed) |
| Applicable instructions | `AGENTS.md`; `CLAUDE.md`; `docs/AGENTS.md`; `docs/plans/AGENTS.md`; `docs/reviews/AGENTS.md` |

## 4. Scope

### In scope

- Restructure `README.md` as a landing page for both artifacts.
- Rewrite `rust/fpr-ff1/README.md`, which is also the crate's docs.rs front page through
  `#![doc = include_str!("../README.md")]`.
- Add `docs/python-api.md` and `docs/migrating-from-ubiq.md` to hold the reference material moved
  out of the README (subject to D3).
- Update `docs/configuration.md`, `docs/architecture.md`, `docs/directory-structure.md`,
  `docs/developer-guide.md`, `docs/AGENTS.md` and `docs/backlog.md` where the moves make them
  stale.
- Update comments and docstrings in `tests/test_interoperability.py` and `tests/test_validation.py`
  that cite "the README migration recipe" or "README note 5", so they cite the new location. These
  are comment-only changes.
- New guard tests for rendering and for examples.
- `pyproject.toml` `description` and `[project.urls]`.
- `publish.yml` `publish-crate`: publish pre-releases, and a tag check that accepts the PEP 440 tag
  (subject to D1).
- The architecture-diagram fix.
- `2.1.0rc2` on both registries, the re-review, and `2.1.0`.

### Out of scope

- Any change to the FF1 core, validation, public API, accepted inputs or ciphertext in either
  language.
- A hosted documentation site (MkDocs, Sphinx, GitHub Pages).
- Automated Mermaid validation in CI. It would need Node in CI; the fix is verified locally with
  mermaid-cli.
- Plan 00003's diagram (`docs/plans/00003-…md` line 255), which has the same defect. Approved
  planning content is frozen.
- Changing any review report.
- A named-competitor comparison, unless D4 chooses it.

## 5. Constraints and preserved decisions

- **Claims must be evidenced.** No FIPS validation, constant-time behaviour, key zeroization or
  audit may be claimed or implied. The pure-Python implementation stays "the reference" and the
  default; the crate stays "the same core, bit for bit", never "the reference".
- **Numbers come only from `just bench`**, with the machine, interpreter and rustc stated beside
  them. The benchmark measures the crate through the Python binding. Do not publish native-Rust
  figures that no harness produced.
- **No example uses a published key without saying so.** A NIST sample key may appear only in a
  "check it against NIST" example that is labelled as such.
- **The migration recipe stays test-backed.** `tests/test_interoperability.py` builds contexts
  "exactly as the migration recipe says". Wherever the recipe moves, the test's docstring points
  there, and the recipe's text does not change meaning.
- **The crate README is compiled.** Its Rust blocks are doctests. Removing hidden lines means
  writing complete examples, not deleting the scaffolding.
- **Semantic versioning.** Documentation, metadata and workflow changes are not API changes.
  `2.1.0rc2` and `2.1.0` carry no change to inputs or outputs.
- **Version lock-step and release convention** (`CLAUDE.md`; the user's memory rule): three
  manifests move together. The owner merges each release branch into `main` by PR with a merge
  commit, and the tag goes on that merge commit.
- **Push, tag, merge and publication each need the owner's per-action authorisation.**
- **100% line and branch coverage on `fpr_ff1`.** `just quality` stays Rust-free: the new guard
  tests read files and must not need the compiled backend or a Rust toolchain.

## 6. Assumptions

None. Unresolved matters are recorded as decisions and block approval when material.

## 7. Decisions and blockers

| ID | Decision or blocker | Resolution | Owner | Status |
|---|---|---|---|---|
| D1 | How `fpr-ff1` `2.1.0-rc2` reaches crates.io | **Chosen, A:** `publish-crate` also publishes pre-releases through Trusted Publishing. Its tag check compares versions after PEP 440 normalisation; today it compares `v2.1.0rc2` with `v2.1.0-rc2` and would fail. This exercises Trusted Publishing on rc2 instead of for the first time on `2.1.0`. **B:** keep the pre-release skip and bootstrap rc2 by hand with another short-lived token. **C:** PyPI-only rc2, with the crate left at rc1. This breaks the stated lock-step ("the crate's version always matches this package's"). | User | Resolved: A ("D1-D4 as recommended", 2026-09-27) |
| D2 | Scope of the independent re-review | **Chosen, A:** one review of `v2.0.0..v2.1.0rc2`, replacing plan 00009 STEP-15's `v2.0.0..v2.1.0rc1`. The prepared bundle is extended with the rc2 delta. **B:** commission the rc1 review now, and review the rc1-to-rc2 delta separately. | User | Resolved: A ("D1-D4 as recommended", 2026-09-27) |
| D3 | README shape | **Chosen, A:** a landing page of about 200–250 lines. The full Python API reference moves to `docs/python-api.md`, the migration guide to `docs/migrating-from-ubiq.md`, the domain-limits rationale into `docs/configuration.md`, and version history to `CHANGELOG.md`. The README keeps short sections that link to each, by absolute URL. **B:** keep all content in the README and only reorder it, add the Rust material and fix the defects. PyPI then shows the full reference, but the page stays at 500+ lines. | User | Resolved: A ("D1-D4 as recommended", 2026-09-27) |
| D4 | Comparison with other FF1 libraries | **Chosen, A:** no named-competitor table. State differentiators as verifiable facts about this library, each linked to its evidence. **B:** a dated comparison table with named Python and Rust libraries, each claim sourced. It would need re-checking every release, and could be unfair to projects that change. | User | Resolved: A ("D1-D4 as recommended", 2026-09-27) |
| D5 | Soak for `2.1.0rc2` | The owner states "soak until <date>" or "soak waived" in the work log after STEP-08's verification, as for `2.1.0rc1` | User (at STEP-08) | Resolved |

## 8. Affected architecture and components

No runtime component changes. The documentation surface, where each page is rendered, and the
changed parts:

| Artifact | Rendered at | Changes |
|---|---|---|
| `README.md` | GitHub; PyPI project page (`readme = "README.md"`) | Restructured (REQ-01 to REQ-06); relative links forbidden |
| `rust/fpr-ff1/README.md` | GitHub; crates.io; docs.rs crate root (`include_str!`) | Rewritten (REQ-07); no rustdoc-only syntax; blocks remain doctests |
| `docs/python-api.md` (new), `docs/migrating-from-ubiq.md` (new) | GitHub | Receive the README's reference sections (D3 A) |
| `docs/configuration.md`, `architecture.md`, `directory-structure.md`, `developer-guide.md`, `AGENTS.md`, `backlog.md` | GitHub | Consistency with the moves; diagram fix |
| `pyproject.toml` | PyPI summary and sidebar | `description`; a crates.io project URL |
| `.github/workflows/publish.yml` | — | `publish-crate` pre-release condition and tag check (D1 A) |
| `tests/test_docs.py` (new) | — | Rendering and example guards (REQ-08, REQ-09) |

`tests/test_contract.py` already asserts the release-document set. The new guards live in
their own module, so that contract stays about packaging.

## 9. Requirement catalogue

### PLAN-00010-REQ-01 — Both artifacts at the top

- **Requirement:** Before the first `##` heading, `README.md` names both artifacts: the Python
  package on PyPI and the `fpr-ff1` crate on crates.io.
  - It gives one install line for each (`pip install fpr-ff1`, `cargo add fpr-ff1`).
  - Its badges cover CI, PyPI version, supported Python versions, crates.io version, docs.rs and
    licence. The licence badge must not say "MIT" alone.
  - A "Quick start" shows Python and Rust side by side, or one after the other, in consecutive
    sections.
- **Rationale:** Review R1, R8.
- **Source:** User request; review R1, R8.
- **Acceptance evidence:** AC-01.

### PLAN-00010-REQ-02 — What FF1 is for, and a known answer

- **Requirement:** The README says in plain words what format-preserving encryption does. It gives
  at least three concrete uses (for example card numbers, national identifiers, and masking test
  data while keeping schemas and validators intact) and at least one thing it is not (not a
  hash, not tokenisation with a vault, no integrity).
  - A "Check it against NIST" example in Python and in Rust reproduces NIST SP 800-38G sample 2 and
    shows its output, `6124200773`. The example states that the key is a published test key.
- **Rationale:** Review R2, R4. A reader can verify the central claim in a minute.
- **Source:** User request; review R2, R4.
- **Acceptance evidence:** AC-02, AC-06.

### PLAN-00010-REQ-03 — Examples run as written

- **Requirement:** Every Python example in `README.md` runs without any function the reader has to
  write. The quick start uses a key from `secrets.token_bytes(32)`, commented to say production
  keys come from a secret store. No comment describes code that is not there.
- **Rationale:** Review R3.
- **Source:** Review R3.
- **Acceptance evidence:** AC-06.

### PLAN-00010-REQ-04 — Security statements kept, consolidated

- **Requirement:** All five numbered security notes stay on the README, at or before the midpoint
  of the page. Their substance is unchanged: determinism and tweak use, no integrity, a wrong
  key does not raise, the domain floor, and exceptions never echo data.
  - One "What this is not" section replaces the three overlapping ones. It covers not FIPS
    validated, no independent audit, not constant-time, no key zeroization (with the Python
    `bytes` and Rust heap reasons), and no key management, and it links to `SECURITY.md`.
  - "FF1 only" keeps its statement that FF3/FF3-1 will never be added.
- **Rationale:** Review R7. Honesty is part of the pitch.
- **Source:** `AGENTS.md` non-negotiables; `SECURITY.md`.
- **Acceptance evidence:** AC-03.

### PLAN-00010-REQ-05 — Reference material in `docs/`, linked

- **Requirement (per D3):** Each section named in D3 moves to its destination with its meaning
  unchanged, and the README links to each destination by absolute URL.
  - The migration guide's API mapping, the `twk_max_len=0` note and the five behaviour changes move
    verbatim in meaning.
  - `tests/test_interoperability.py` and `tests/test_validation.py` comments cite the new location.
  - `docs/AGENTS.md`'s maintained-documents list and `docs/directory-structure.md` name the new
    files.
- **Rationale:** Review R6; `docs/AGENTS.md`.
- **Source:** `docs/AGENTS.md`; review R6.
- **Acceptance evidence:** AC-04.

### PLAN-00010-REQ-06 — One performance table

- **Requirement:** The README has one performance table, from a `just bench` run made during this
  plan, with its machine, OS, CPython and rustc stated. It covers both backends at the shapes
  `just bench` reports.
  - The macOS table and the "Before 1.1.0" history are removed; `CHANGELOG.md` already holds the
    history.
  - The GIL-release parallelism figure is re-measured in the same run or removed.
  - `SECURITY.md`'s figures are untouched unless the same run re-measures them.
- **Rationale:** Review R5; `CLAUDE.md`.
- **Source:** Review R5.
- **Acceptance evidence:** AC-05.

### PLAN-00010-REQ-07 — A crate README for Rust users

- **Requirement:** `rust/fpr-ff1/README.md` opens with what FF1 is for and why this crate is
  trustworthy: the shared conformance evidence, exact integer arithmetic, FF1 only. It then
  gives:
  - `cargo add fpr-ff1`;
  - the MSRV (1.89);
  - a docs.rs link;
  - complete examples (`fn main() -> Result<(), fpr_ff1::Error>`) for the builder, the numeral
    interface, and error handling by `ErrorKind`;
  - "Limits", "What this is not", "Testing" and the licence.

  The Python package appears as a sibling artifact ("also available for Python"), not as the
  crate's reason to exist. The statement that the pure-Python implementation is the reference
  stays. The page contains no hidden doctest line and no intra-doc link syntax.
- **Rationale:** Review R10, R12.
- **Source:** User request; review R10, R12.
- **Acceptance evidence:** AC-07, AC-08.

### PLAN-00010-REQ-08 — Rendering guards

- **Requirement:** `tests/test_docs.py` fails if any of these hold:
  - (a) `README.md` contains a Markdown link or image whose target is neither an absolute
    `https://` URL nor a same-page `#anchor`. PyPI renders the file and cannot resolve relative
    targets.
  - (b) A fenced `rust` block in `rust/fpr-ff1/README.md` contains a line whose first
    non-whitespace characters are `# ` or which is exactly `#`. crates.io shows these hidden lines
    literally.
  - (c) The crate README contains rustdoc intra-doc link syntax: a bracketed link whose target is
    not a URL or `#anchor`, or a bare `` [`Name`] `` reference.

  The module runs in `just quality`, without Rust.
- **Rationale:** Review R9, R10. Each defect was invisible on GitHub and shipped.
- **Source:** Review R9, R10.
- **Acceptance evidence:** AC-08.

### PLAN-00010-REQ-09 — Examples are executed

- **Requirement:**
  - (a) `tests/test_docs.py` executes every fenced `python` block in `README.md`, in order, in one
    namespace. A block may opt out only with an HTML comment `<!-- docs-test: skip (reason) -->`
    on the line immediately before it, and the test lists skipped blocks by reason.
  - (b) Every fenced `rust` block in `README.md` appears verbatim in `rust/fpr-ff1/README.md`,
    whose blocks `cargo test --doc` compiles and runs.
  - (c) The NIST example asserts `6124200773` in both languages.
- **Rationale:** Review R3, R4. The quick start broke without anything noticing.
- **Source:** Review R3, R4.
- **Acceptance evidence:** AC-06.

### PLAN-00010-REQ-10 — Metadata and badges

- **Requirement:**
  - `pyproject.toml` `description` names FF1 and SP 800-38G and mentions the optional compiled
    backend, in no more than 90 characters.
  - `[project.urls]` gains `"Rust crate" = "https://crates.io/crates/fpr-ff1"`.
  - The crate's `description`, keywords and categories are reviewed and changed only where the
    review finds an inaccuracy.
- **Rationale:** Review R11.
- **Source:** Review R11.
- **Acceptance evidence:** AC-09.

### PLAN-00010-REQ-11 — The architecture diagram renders

- **Requirement:** `docs/architecture.md`'s Mermaid block parses. Commit `153aa22`
  (`fix/architecture-mermaid`) is cherry-picked or merged into the execution branch, and every
  Mermaid block in the non-plan, non-review documents parses with mermaid-cli.
- **Rationale:** Review R13.
- **Source:** Review R13.
- **Acceptance evidence:** AC-10.

### PLAN-00010-REQ-12 — `2.1.0rc2` on both registries

- **Requirement:**
  - All three manifests move to `2.1.0rc2` / `2.1.0-rc2`, with a dated changelog section.
  - The full gate passes and CI is green at the release commit.
  - The owner merges by PR with a merge commit, tags `v2.1.0rc2` on it, and publishes a GitHub
    pre-release.
  - PyPI is published by `publish.yml`. The crate is published per D1: under A, by `publish-crate`
    through Trusted Publishing, and crates.io then shows Trusted Publishing data for the version.
  - The Builder verifies what plan 00009 STEP-14 verified, and also checks the rendered pages:
    - the PyPI description has no relative link;
    - the crates.io README HTML has no hidden-line or intra-doc syntax;
    - docs.rs builds.
- **Rationale:** User request; the pages can only be judged where they are rendered.
- **Source:** User; plan 00009 REQ-12.
- **Acceptance evidence:** AC-11, AC-12.

### PLAN-00010-REQ-13 — Re-review and `2.1.0`, carried forward

- **Requirement (per D2):**
  - An independent re-review of the chosen range returns no Critical or Major finding, and the
    owner dispositions every finding.
  - Then `2.1.0` follows in all three manifests, with a dated changelog section, the gate and CI
    green, and the owner's merge, tag and release.
  - `publish.yml` publishes both registries: the crate through Trusted Publishing, and
    `cargo semver-checks` runs against the published baseline.
  - The Builder verifies both registries as in REQ-12.
  - `docs/backlog.md` records plan 00009 (STEP-01 to STEP-14) and plan 00010 as completed.
- **Rationale:** Plan 00009 STEP-15 to STEP-17, superseded here.
- **Source:** Plan 00009 REQ-12, REQ-14.
- **Acceptance evidence:** AC-13, AC-14.

## 10. Delivery strategy

Documentation first, release second:

1. **Hand-over from plan 00009 (STEP-01).** Record the supersession in 00009's work log, and bring
   in the diagram fix.
2. **Guards before content (STEP-02).**
   - Write the guard tests first. They should go red on today's pages: the two PyPI relative links,
     the crate README's hidden lines and intra-doc links, and the undefined quick-start function.
   - Then fix exactly those defects, so the step leaves the tree green.
   - Every later rewrite happens under the guards.
3. **Rust page, then main page (STEP-03, STEP-04).** The crate README's doctested blocks are what
   the main README's Rust examples must copy verbatim. Writing the crate page first gives the main
   page a compiled source to quote.
4. **Numbers and metadata (STEP-05, STEP-06).** A fresh bench, and the D1 workflow change.
5. **Candidate and publication (STEP-07, STEP-08).** As plan 00009 STEP-13/14, plus a check of the
   rendered pages.
6. **Promotion (STEP-09 to STEP-11).** Re-review, bump, release: plan 00009 STEP-15 to STEP-17,
   carried forward.

One revertible commit per step. The full dual-backend gate runs after STEP-02, STEP-04, STEP-07
and STEP-10. `just crate-test` runs after every step that touches the crate README.

## 11. Detailed implementation steps

### PLAN-00010-STEP-01 — Take over from plan 00009; bring in the diagram fix

- **Status placeholder:** `not-started`
- **Objective:** A single live plan, and a rendering architecture diagram.
- **Requirements:** `PLAN-00010-REQ-11`, `PLAN-00010-REQ-13`
- **Depends on:** None
- **Affected components:** `docs/plans/00009-Crate_And_v2.1.0_Release.md` (work log and
  Builder front matter only); `docs/architecture.md`
- **Preconditions:** Plan approved; clean worktree on `release/v2.1`.
- **Test or evidence first:** Render `docs/architecture.md`'s Mermaid block with mermaid-cli
  (`npx -y -p @mermaid-js/mermaid-cli mmdc`). It should fail with `Parse error on line 3`.
- **Implementation tasks:**
  1. In plan 00009's work log, mark STEP-15, STEP-16 and STEP-17 `skipped`, with the evidence
     "superseded by PLAN-00010, approved <approval commit>". This approval is the user approval a
     skipped step requires. Set 00009 `implementation_status: completed`, and write a completion
     summary that names REQ-12 (2.1.0) and REQ-14 as carried into PLAN-00010 REQ-12/13.
  2. Cherry-pick `153aa22` onto `release/v2.1`.
  3. Render every Mermaid block in `README.md`, `docs/*.md`, `SECURITY.md` and
     `rust/fpr-ff1/README.md` with mermaid-cli.
- **Documentation/configuration/operations:** Work logs of both plans.
- **Verification:** Every Mermaid block renders to SVG, with no parse error.
- **Completion criteria:** Both commits on `release/v2.1`; 00009's work log accounts for every
  step.
- **Rollback or recovery:** Revert the commits.
- **Builder stop conditions:** A cherry-pick conflict; a Mermaid block that still fails to parse.

### PLAN-00010-STEP-02 — Guard tests, and the defects they find today

- **Status placeholder:** `not-started`
- **Objective:** The rendering and example guards exist, and pass.
- **Requirements:** `PLAN-00010-REQ-03`, `PLAN-00010-REQ-08`, `PLAN-00010-REQ-09`
- **Depends on:** STEP-01
- **Affected components:** `tests/test_docs.py` (new); `README.md`; `rust/fpr-ff1/README.md`
- **Preconditions:** STEP-01 committed.
- **Test or evidence first:** Write `tests/test_docs.py` against the current pages and record
  the red run. At least these must fail: relative links `LICENSE` and `rust/fpr-ff1/README.md`;
  hidden lines and `` [`Error`] `` in the crate README; the quick start's
  `load_key_from_your_secret_store`.
- **Implementation tasks:**
  1. Guards (a) to (c) from REQ-08, and (a) to (b) from REQ-09.
  2. A probe for each guard: re-introduce one defect, see the guard fail naming the file and
     line, then revert.
  3. The smallest fixes that turn the guards green:
     - absolute URLs for the two links;
     - complete, hidden-line-free crate README examples;
     - plain text or docs.rs links in place of intra-doc links;
     - a runnable quick start.
- **Documentation/configuration/operations:** `docs/developer-guide.md` names the new module and
  the `docs-test: skip` marker.
- **Verification:**
  - `uv run pytest tests/test_docs.py -v`;
  - `just crate-test` (the doctests still pass);
  - `just quality` with `src/fpr_ff1/_rs.so` moved aside;
  - the full dual-backend gate at 100%.
- **Completion criteria:** Red run, probes and green run recorded in the work log.
- **Rollback or recovery:** Revert.
- **Builder stop conditions:** A guard that cannot be made to fail by its probe; a doctest that
  cannot be written without hidden lines.

### PLAN-00010-STEP-03 — The crate README

- **Status placeholder:** `not-started`
- **Objective:** The Rust landing page.
- **Requirements:** `PLAN-00010-REQ-07`
- **Depends on:** STEP-02
- **Affected components:** `rust/fpr-ff1/README.md`
- **Preconditions:** STEP-02 green.
- **Test or evidence first:** The STEP-02 guards and the doctests.
- **Implementation tasks:**
  1. Write the page to REQ-07, in this order: pitch, install and MSRV, quick start, "check it
     against NIST", numerals, errors, what makes it trustworthy, limits, what this is not,
     testing, also available for Python, licence.
  2. Badges: crates.io, docs.rs, MSRV, licence.
- **Documentation/configuration/operations:** None beyond the page.
- **Verification:**
  - `just crate-test`;
  - `just crate-package` (the contents check still passes; `RUSTDOCFLAGS=-D warnings` docs are
    clean);
  - `uv run pytest tests/test_docs.py`;
  - a grep over the page for "reference" shows it applied only to the pure-Python implementation.
- **Completion criteria:** All four pass.
- **Rollback or recovery:** Revert.
- **Builder stop conditions:** Any sentence that claims more than `SECURITY.md` supports.

### PLAN-00010-STEP-04 — The main README and the moved reference pages

- **Status placeholder:** `not-started`
- **Objective:** The landing page for both languages, per D3 and D4.
- **Requirements:** `PLAN-00010-REQ-01`, `PLAN-00010-REQ-02`, `PLAN-00010-REQ-04`,
  `PLAN-00010-REQ-05`
- **Depends on:** STEP-03
- **Affected components:** `README.md`; `docs/python-api.md`, `docs/migrating-from-ubiq.md` (new,
  under D3 A); `docs/configuration.md`; `docs/AGENTS.md`; `docs/directory-structure.md`;
  comments in `tests/test_interoperability.py` and `tests/test_validation.py`
- **Preconditions:** STEP-03 committed.
- **Test or evidence first:** Before editing, list every README section and its destination
  (kept, condensed, moved to <file>, or removed as duplicate or history) in the work log. After
  editing, check that list: nothing is dropped unaccounted for.
- **Implementation tasks:**
  1. Page order (D3 A):
     - title, one-paragraph pitch, badges;
     - install (both languages);
     - what FF1 is for;
     - quick start in Python and Rust;
     - check it against NIST;
     - security notes;
     - why you can trust it (condensed, each claim linked to its test or document);
     - FF1 only;
     - backends and platforms;
     - performance (placeholder until STEP-05);
     - limits (short table, linking to `docs/configuration.md`);
     - migrating from `ubiq_security_fpe` (the three-line value proposition and a link);
     - what this is not;
     - documentation links;
     - development;
     - licence.
  2. Move the reference sections verbatim in meaning, and update the pointers named in REQ-05.
  3. Under D4 A, the differentiators are statements about this library only.
- **Documentation/configuration/operations:** As listed.
- **Verification:**
  - the section-disposition list is complete;
  - `uv run pytest tests/test_docs.py tests/test_interoperability.py`;
  - `just quality` Rust-free;
  - the full dual-backend gate at 100%;
  - a check that every absolute `https://github.com/joelee/fpr-ff1/blob/main/...` link names a
    file that exists in the tree, allowing for files this change creates that `main` gains at the
    merge.
- **Completion criteria:** The README is at most 260 lines under D3 A; every moved section is
  reachable in one click.
- **Rollback or recovery:** Revert.
- **Builder stop conditions:** A security note or disclaimer would have to be weakened to fit;
  the migration recipe's meaning would change.

### PLAN-00010-STEP-05 — One performance table from a fresh bench

- **Status placeholder:** `not-started`
- **Objective:** Current, comparable numbers.
- **Requirements:** `PLAN-00010-REQ-06`
- **Depends on:** STEP-04
- **Affected components:** `README.md` performance section
- **Preconditions:** A quiet machine; release-built extension (`just backend-dev`).
- **Test or evidence first:** The `just bench` output and its environment (CPU, OS, CPython,
  rustc, load average), saved in the work log.
- **Implementation tasks:** Replace the placeholder with one table for both backends. Include the
  parallelism row only if this run measures it.
- **Documentation/configuration/operations:** None.
- **Verification:** Every figure in the table appears in the recorded output.
- **Completion criteria:** No figure on the page lacks a recorded source.
- **Rollback or recovery:** Revert.
- **Builder stop conditions:** A figure more than 25% worse than plan 00009 STEP-02's run for the
  same shape. That is a performance question, not a documentation one: escalate.

### PLAN-00010-STEP-06 — Metadata, and CI publication of pre-release crates

- **Status placeholder:** `not-started`
- **Objective:** Metadata describes both artifacts; rc2's crate can be published by CI (D1 A).
- **Requirements:** `PLAN-00010-REQ-10`, `PLAN-00010-REQ-12`
- **Depends on:** STEP-05
- **Affected components:** `pyproject.toml`; `.github/workflows/publish.yml` `publish-crate`;
  `rust/fpr-ff1/Cargo.toml` (only if REQ-10's review finds an inaccuracy)
- **Preconditions:** D1 resolved.
- **Test or evidence first:** A local run of the tag-check logic against `v2.1.0rc2` with crate
  version `2.1.0-rc2`: it fails as written today, and passes after the change. It must also fail
  for `v2.1.0rc3` against `2.1.0-rc2`, and for `v2.1.0` against `2.1.0-rc2`.
- **Implementation tasks:**
  1. The `description` and `[project.urls]` changes.
  2. Under D1 A:
     - remove `if: ${{ !github.event.release.prerelease }}`;
     - make the tag check normalise both sides with `packaging.version.Version` (as
       `tests/test_contract.py` does), or map `-rcN` to `rcN` exactly;
     - keep `needs: [quality, publish]`, so PyPI must succeed first.
  3. `actionlint` on the workflow.
- **Documentation/configuration/operations:** `docs/developer-guide.md` release section: both
  registries are published by CI for every release, pre-releases included.
- **Verification:** The tag-check cases above; `actionlint`; `tests/test_contract.py`.
- **Completion criteria:** As verified.
- **Rollback or recovery:** Revert. A failed `publish-crate` on rc2 leaves PyPI published and the
  crate unpublished; the owner can then publish that exact CI-built `.crate` by hand, as in
  plan 00009 STEP-14.
- **Builder stop conditions:** D1 unresolved; any change that would let a tag publish a crate
  whose version it does not name.

### PLAN-00010-STEP-07 — Cut `2.1.0rc2`

- **Status placeholder:** `not-started`
- **Objective:** A green candidate.
- **Requirements:** `PLAN-00010-REQ-12`
- **Depends on:** STEP-06
- **Affected components:** `pyproject.toml`; `rust/fpr-ff1/Cargo.toml`;
  `rust/fpr-ff1-rust/Cargo.toml`; `rust/Cargo.lock`; `CHANGELOG.md`
- **Preconditions:** STEP-01 to STEP-06 committed.
- **Test or evidence first:** `tests/test_contract.py` lock-step tests.
- **Implementation tasks:**
  1. Three manifests at `2.1.0rc2` / `2.1.0-rc2`; update the lock.
  2. A `[2.1.0rc2]` changelog section: documentation, metadata, the rendering fixes, the workflow
     change; "no change to accepted inputs, ciphertext or API".
  3. Local gate:
     - full dual-backend gate;
     - Rust-free quality;
     - `just crate-test`, `just crate-msrv` and `just crate-package`;
     - `tests/test_docs.py`.
  4. **Owner authorisation:** push `release/v2.1`; the Builder dispatches `ci.yml` and records the
     run.
- **Documentation/configuration/operations:** Changelog.
- **Verification:** CI green on every job. The crate-package semver step now has a baseline
  (`2.1.0-rc1`); it must pass or its outcome must be recorded and explained.
- **Completion criteria:** A green run at the candidate.
- **Rollback or recovery:** Fix forward on the branch.
- **Builder stop conditions:** Any red job; `cargo semver-checks` reporting a breaking change; no
  push authorisation.

### PLAN-00010-STEP-08 — Owner publishes `2.1.0rc2`; Builder verifies the rendered pages

- **Status placeholder:** `not-started`
- **Objective:** rc2 public on both registries, with correct pages.
- **Requirements:** `PLAN-00010-REQ-12`
- **Depends on:** STEP-07
- **Affected components:** None (owner actions; Builder verification)
- **Preconditions:** STEP-07 complete.
- **Test or evidence first:** This step is the evidence.
- **Implementation tasks:**
  1. **Owner:** PR `release/v2.1` into `main`, merge with a merge commit, tag `v2.1.0rc2` on it,
     and publish a GitHub pre-release.
  2. **CI:** `publish.yml` publishes PyPI, then (D1 A) `publish-crate` publishes the crate.
  3. **Builder:**
     - PyPI: files and digests against the run's artifacts, attestations, clean installs on both
       backends.
     - crates.io: checksum equal to the run's `crate` artifact; Trusted Publishing data present
       for the version.
     - docs.rs: the build succeeds.
     - A scratch project on `=2.1.0-rc2`, reproducing a NIST vector and a `d > 16` case.
     - **Rendered pages:**
       - the PyPI JSON `description` has no relative link, and every link on it resolves;
       - the crates.io README HTML contains no `# let`, no `Ok::<` hidden line and no literal
         `[` + backticked name + `]`;
       - the docs.rs crate root shows the same examples.
  4. **Owner:** the D5 soak statement.
- **Documentation/configuration/operations:** Work log.
- **Verification:** All of task 3.
- **Completion criteria:** rc2 verified on both registries; soak stated.
- **Rollback or recovery:** A defective candidate is left in place (yanked if harmful) and fixed in
  `2.1.0rc3`, never overwritten.
- **Builder stop conditions:** A digest mismatch; a rendering defect on either registry;
  `publish-crate` failing.

### PLAN-00010-STEP-09 — Independent re-review

- **Status placeholder:** `not-started`
- **Objective:** Independent verification before promotion (plan 00009 STEP-15, carried).
- **Requirements:** `PLAN-00010-REQ-13`
- **Depends on:** STEP-08 and the soak
- **Affected components:** `docs/reviews/` (the reviewer's report)
- **Preconditions:** Soak elapsed or waived.
- **Test or evidence first:** The review is the evidence.
- **Implementation tasks:**
  1. Builder extends the prepared `v2.0.0..v2.1.0rc1` bundle to the D2 range, adding:
     - the rc2 commits;
     - the README review above and its resolution;
     - the guard tests and their probes;
     - the D1 workflow change and its first run;
     - the rc2 registry verification.
  2. **Owner** commissions the review.
  3. Owner dispositions every finding in the work log.
- **Documentation/configuration/operations:** None by Builder.
- **Verification:** No Critical or Major finding; every finding dispositioned.
- **Completion criteria:** A clean review recorded.
- **Rollback or recovery:** A Critical or Major finding sends the work to `2.1.0rc3`.
- **Builder stop conditions:** Any Critical or Major finding.

### PLAN-00010-STEP-10 — Bump to `2.1.0`

- **Status placeholder:** `not-started`
- **Objective:** The release commit.
- **Requirements:** `PLAN-00010-REQ-13`
- **Depends on:** STEP-09
- **Affected components:** Three manifests; `rust/Cargo.lock`; `CHANGELOG.md`; `SECURITY.md`
  supported-versions table; `docs/backlog.md`
- **Preconditions:** STEP-09 clean.
- **Test or evidence first:** Lock-step tests.
- **Implementation tasks:**
  1. The three manifests at `2.1.0`.
  2. The `[2.1.0]` changelog section, summarising `2.1.0rc1` and `2.1.0rc2`.
  3. The `SECURITY.md` support table; backlog entries for plans 00009 and 00010.
  4. The local gate as in STEP-07.
  5. **Owner authorisation:** push, then CI.
- **Documentation/configuration/operations:** As listed.
- **Verification:** CI green; `cargo semver-checks` against `2.1.0-rc2` passes.
- **Completion criteria:** A green run at the release commit.
- **Rollback or recovery:** Fix forward.
- **Builder stop conditions:** As STEP-07.

### PLAN-00010-STEP-11 — Owner releases `2.1.0`; Builder verifies; plan closes

- **Status placeholder:** `not-started`
- **Objective:** `2.1.0` on both registries by CI.
- **Requirements:** `PLAN-00010-REQ-13`
- **Depends on:** STEP-10
- **Affected components:** None (owner actions; Builder verification); plan work log
- **Preconditions:** STEP-10 green.
- **Test or evidence first:** This step is the evidence.
- **Implementation tasks:**
  1. **Owner:** PR into `main` with a merge commit, tag `v2.1.0` on it, and publish a GitHub
     release (not a pre-release).
  2. **CI:** PyPI, then `publish-crate` through Trusted Publishing.
  3. **Builder:** STEP-08's verification for `2.1.0`, including the rendered pages. Also confirm
     `pip install fpr-ff1` and `cargo add fpr-ff1` resolve to `2.1.0` without `--pre`.
  4. **Builder:** close the plan in the work log. Record the outcome in `docs/backlog.md` in a
     closeout commit, submitted by PR per the release convention.
- **Documentation/configuration/operations:** Work log; backlog.
- **Verification:** As task 3.
- **Completion criteria:** `2.1.0` public and verified on both registries.
- **Rollback or recovery:** A defective release is yanked if harmful and fixed in `2.1.1`, never
  overwritten.
- **Builder stop conditions:** As STEP-08.

## 12. Cross-cutting concerns

| Area | Applicability | Planned action or reason not applicable | Step or requirement |
|---|---|---|---|
| Compatibility and APIs | Not applicable | No API, input or output change in either artifact | §5 |
| Data and migration | Applicable | The migration guide moves (D3 A) with its meaning intact and its test pointer updated | REQ-05, STEP-04 |
| Security and privacy | Applicable | Every disclaimer kept; examples use random keys, except a labelled NIST check | REQ-02 to REQ-04 |
| Performance and scale | Applicable | One fresh, sourced table | REQ-06, STEP-05 |
| Reliability and failure handling | Applicable | A failed `publish-crate` leaves a documented manual path | STEP-06 |
| Observability and operations | Not applicable | No runtime component | — |
| Dependencies and supply chain | Applicable | The crate publishes by OIDC for pre-releases too; the tag check is tightened, not loosened. No new runtime or test dependency: the guards use the standard library | REQ-12, STEP-06 |
| Accessibility and UX | Applicable | Headings in order; tables have header rows; badges have alt text; code blocks carry language tags | STEP-03, STEP-04 |
| Documentation and release | Applicable | This plan | All |
| Deployment and rollback | Applicable | Registry versions are immutable: rc3 or 2.1.1, never an overwrite | STEP-08, STEP-11 |

## 13. Verification strategy

| Level | Evidence or command | When | Required result |
|---|---|---|---|
| Guards | `uv run pytest tests/test_docs.py -v`, plus one probe per guard | STEP-02 onward | Red on the old pages; each probe caught; green after |
| Doctests | `just crate-test` | STEP-02, STEP-03, STEP-07, STEP-10 | All pass, with fixtures required |
| Full gate | `FPR_FF1_REQUIRE_RUST_BACKEND=1 FPR_FF1_REQUIRE_ORACLE=1 uv run pytest --cov=fpr_ff1 --cov-fail-under=100` | STEP-02, STEP-04, STEP-07, STEP-10 | Pass, 100% |
| Rust-free | `just quality` with `_rs.so` moved aside | Same | Pass, 100% |
| Diagrams | mermaid-cli render of every non-plan, non-review Mermaid block | STEP-01 | No parse error |
| Workflow | `actionlint`; the tag-check cases | STEP-06 | Clean; the cases behave as specified |
| CI | `ci.yml` | STEP-07, STEP-10 | Green on every job |
| Registries | Digests, attestations, Trusted Publishing data, docs.rs, scratch project, rendered-page checks | STEP-08, STEP-11 | All pass |
| Review | Independent re-review | STEP-09 | No Critical or Major |

## 14. Acceptance criteria

- [ ] `PLAN-00010-AC-01` Before its first `##` heading, `README.md` names the PyPI package and the crates.io crate, with an install line for each and badges for PyPI, crates.io and docs.rs. Its licence badge shows both licences.
- [ ] `PLAN-00010-AC-02` `README.md` states what FF1 is for with at least three concrete uses and at least one explicit non-use, and shows a NIST sample 2 check in Python and Rust with output `6124200773`.
- [ ] `PLAN-00010-AC-03` All five security notes appear in `README.md` with unchanged substance, before the midpoint of the page. A single "What this is not" section covers FIPS, audit, constant-time, zeroization and key management. No overlapping disclaimer section remains.
- [ ] `PLAN-00010-AC-04` Every README section is accounted for in STEP-04's disposition list. Each moved section exists at its destination and is linked from the README by absolute URL. Test comments cite the new locations.
- [ ] `PLAN-00010-AC-05` `README.md` contains exactly one performance table. Every figure in it appears in a `just bench` output recorded in the work log during this plan, with the machine details stated.
- [ ] `PLAN-00010-AC-06` `tests/test_docs.py` executes every `README.md` Python block (skips listed with reasons) and checks every README Rust block appears verbatim in the doctested crate README. Both pass.
- [ ] `PLAN-00010-AC-07` `rust/fpr-ff1/README.md` contains `cargo add fpr-ff1`, the MSRV, a docs.rs link and complete examples. It names the pure-Python implementation as the reference, and `just crate-test` passes.
- [ ] `PLAN-00010-AC-08` The rendering guards fail on each recorded probe and pass on the final pages.
- [ ] `PLAN-00010-AC-09` The PyPI summary for `2.1.0rc2` mentions the compiled backend, and PyPI's project links include the crates.io page.
- [ ] `PLAN-00010-AC-10` Every Mermaid block outside `docs/plans/` and `docs/reviews/` renders with mermaid-cli, and `docs/architecture.md`'s diagram renders on GitHub.
- [ ] `PLAN-00010-AC-11` `2.1.0rc2` is on PyPI and crates.io with digests equal to the publish run's artifacts. Under D1 A, crates.io shows Trusted Publishing data for `2.1.0-rc2`.
- [ ] `PLAN-00010-AC-12` The rc2 pages as rendered by PyPI, crates.io and docs.rs pass STEP-08's rendered-page checks.
- [ ] `PLAN-00010-AC-13` An independent re-review of the D2 range exists with no Critical or Major finding, and every finding is dispositioned.
- [ ] `PLAN-00010-AC-14` `2.1.0` is on both registries, published by CI (the crate through Trusted Publishing), verified as in STEP-08, and resolvable without pre-release flags.

## 15. Risks and mitigations

| Risk | Likelihood | Impact | Mitigation or test | Owner/step |
|---|---|---|---|---|
| Promotional rewriting overstates a guarantee | Medium | High | Constraint §5; STEP-03/04 stop conditions; the re-review reads the pages | Builder; reviewer |
| A moved section loses meaning (the migration recipe especially) | Low | High | Disposition list; the interoperability tests still build the recipe | STEP-04 |
| A README example drifts from the code | Medium | Medium | REQ-09 executes Python blocks; Rust blocks must match doctested text | STEP-02 |
| `publish-crate` fails on its first Trusted Publishing run | Medium | Medium | Runs on rc2, not on `2.1.0`; a manual fallback with the CI-built `.crate` | STEP-06, STEP-08 |
| `cargo semver-checks` misreads a pre-release baseline | Medium | Low | Its first real run is at STEP-07; the outcome is recorded; a stop on a reported break | STEP-07 |
| Rendering differs between GitHub, PyPI and crates.io in ways the guards miss | Medium | Low | STEP-08 inspects the registry-rendered HTML itself | STEP-08 |
| Registry versions are immutable | Certain | Medium | rc2 exists to find page defects before `2.1.0` | STEP-08 |

## 16. Builder hand-off

- **Start condition:** User approval (given) with D1 to D4 resolved (A in each), and a clean
  repository on `release/v2.1`.
- **First step:** STEP-01.
- **Required sequence:** STEP-01 → STEP-02 → STEP-03 → STEP-04 → STEP-05 → STEP-06 → STEP-07 →
  STEP-08 → STEP-09 → STEP-10 → STEP-11.
- **Parallel-safe work:** STEP-06's metadata edits are independent of STEP-03 to STEP-05, but keep
  the sequence for one commit per step.
- **Do not change:** approved scope, requirements, steps, acceptance criteria, or content outside
  Builder's permitted work-log area; plan 00009's planning content; any review report; the FF1
  core, validation or public API of either artifact.
- **Escalate when:** any stop condition triggers; a page needs a claim the evidence does not
  support; any push, tag, merge or publication is required.
- **Completion hand-off:** `2.1.0` verified on both registries; plan closed in the work log and
  the backlog.

<!-- BUILDER_WORK_LOG_START -->
## 17. Builder Work Log

> [!warning] Builder-maintained section
> Delivery Planner creates this section. After approval, Builder may update only
> this delimited section and the Builder-maintained front-matter fields. Builder
> must preserve prior entries and use UTC timestamps.

### Step status

| Step | Status | Started (UTC) | Completed (UTC) | Evidence | Builder notes |
|---|---|---|---|---|---|
| PLAN-00010-STEP-01 | completed | 2026-09-27T11:24:04Z | 2026-09-27T11:24:30Z | acc02bd (diagram fix); plan 00009 closed as superseded; mermaid-cli render | fix/architecture-mermaid (153aa22, unpushed) is now redundant; keep or delete at the owner's choice |
| PLAN-00010-STEP-02 | completed | 2026-09-27T11:26:19Z | 2026-09-27T11:37:47Z | Commit (this one); red run, 9 probes, checkpoint-112806 | Guards run Rust-free and from the sdist (README.md and rust/ ship in it) |
| PLAN-00010-STEP-03 | completed | 2026-09-27T11:37:47Z | 2026-09-27T11:39:59Z | Commit (this one) | 168 lines; examples untouched since STEP-02, so the README's copy still matches |
| PLAN-00010-STEP-04 | completed | 2026-09-27T11:40:22Z | 2026-09-27T11:54:32Z | Commit (this one); checkpoint-114550 | README 565 -> 260 lines; interim performance table is the 2.0.0 Linux run until STEP-05 |
| PLAN-00010-STEP-05 | completed | 2026-09-27T11:54:41Z | 2026-09-27T11:57:02Z | Commit (this one); bench-10.txt | SECURITY.md value-timing row flagged for the re-review |
| PLAN-00010-STEP-06 | completed | 2026-09-27T11:57:11Z | 2026-09-27T12:07:11Z | Commit (this one); checkpoint-115849 | publish-crate's first CI run will be rc2 (STEP-08) |
| PLAN-00010-STEP-07 | completed | 2026-09-27T12:07:18Z | 2026-09-27T16:00:25Z | 0345b0d; local gate checkpoint-120805; CI run 36330546176 green 41/41 | Semver step vacuous across pre-releases (see Deviations); left for the re-review, the user not having chosen to amend ci.yml |
| PLAN-00010-STEP-08 | completed | 2026-09-27T16:00:25Z | 2026-09-27T22:59:30Z | PR #15 merge 6379af8 tagged v2.1.0rc2; publish run 36355953834 43/43; crate by Trusted Publishing; both registries and rendered pages verified; soak waived | Soak statement given with the release, before verification (recorded as given) |
| PLAN-00010-STEP-09 | completed | 2026-09-27T22:59:40Z | 2026-09-28T12:02:10Z | Review 00015 (approve); bundle; dispositions | Review covered part 2 lightly; the owner chose to proceed |
| PLAN-00010-STEP-10 | blocked | 2026-09-28T12:02:10Z | — | 3600eac; local gate checkpoint-120312 | Waiting on owner: review 00015 commit and push authorization |
| PLAN-00010-STEP-11 | not-started | — | — | — | — |

Allowed status values: `not-started`, `in-progress`, `blocked`, `completed`,
`skipped`. A skipped step requires explicit user approval recorded in Evidence.

### Execution log

| Timestamp (UTC) | Step | Event | Evidence or reference | Next action |
|---|---|---|---|---|
| 2026-09-27T11:24:04Z | — | Builder started on approved plan 00010 (approval commit 74977911) on release/v2.1 | git status clean at 74977911b83f28a278fded41b92a56b1d3a231b8; D1-D4 resolved A | STEP-01 |
| 2026-09-27T11:24:30Z | PLAN-00010-STEP-01 | Evidence first: mermaid-cli on docs/architecture.md's block before the fix failed 'Parse error on line 3' at the unquoted label \|backend=python (default)\| (reproduced 2026-09-27 on fix/architecture-mermaid). Cherry-picked 153aa22 with -x as acc02bd. Plan 00009: STEP-15 to STEP-17 marked skipped (superseded, approval 74977911), implementation_status completed, completion summary names the carried requirements | acc02bd; docs/plans/00009 work log | Verify every Mermaid block |
| 2026-09-27T11:26:19Z | PLAN-00010-STEP-02 | Evidence first: tests/test_docs.py written against the 2.1.0rc1 pages. Red run: 7 failed, 1 passed (the skip-marker reason check, vacuous with no markers). Failures: README.md:6 link target 'LICENSE' and the rust/fpr-ff1/README.md link; crate README:50 link target 'Error::kind'; 6 hidden doctest lines in the crate README (first: line 33 '# Ok::<(), fpr_ff1::Error>(())'); crate README:50 intra-doc link [`Error`]; the quick start's NameError 'load_key_from_your_secret_store' (README.md:20); README.md:307's Rust block not in the crate README; no NIST sample 2 check in either language. One guard defect found and fixed while writing: the empty-bracket check matched a backticked inline link ([`fpr-ff1`](https://...)); it now excludes brackets followed by a link target | tests/test_docs.py | Smallest fixes to turn the guards green |
| 2026-09-27T11:37:47Z | PLAN-00010-STEP-02 | Smallest fixes. README.md: LICENSE and the crate README link made absolute; the quick start takes its key from secrets.token_bytes(32) with a comment that real keys come from a secret store (the stale 'all-zero key' comment is gone); a 'Check it against NIST' subsection reproduces sample 2 ('6124200773') with the published key labelled for checking only; the Rust section's example is replaced by the crate README's sample 2 program verbatim; the Unicode normalisation example defines its alphabet (16 code points NFC-normalised to 15); the migration example carries '<!-- docs-test: skip (...) -->' (it imports the legacy library; tests/test_interoperability.py builds the recipe). rust/fpr-ff1/README.md: three examples rewritten as complete fn main() -> Result<(), fpr_ff1::Error> programs with no hidden lines; [`Error`] and [`kind`](Error::kind) replaced by docs.rs URLs. docs/developer-guide.md: Testing Standards names tests/test_docs.py and the skip marker | README.md; rust/fpr-ff1/README.md; docs/developer-guide.md | Probes, then checkpoint |
| 2026-09-27T11:39:59Z | PLAN-00010-STEP-03 | rust/fpr-ff1/README.md rewritten as the Rust landing page, in the plan's order: pitch with three concrete uses and what FF1 is not; cargo add, MSRV 1.89, docs.rs; quick start (NIST sample 2, doubling as the conformance check, with the published key labelled); numerals (sample 1); errors by ErrorKind; Clone + Send + Sync (tests/api.rs instances_are_send_and_sync); 'Why trust it' (9 NIST samples both ways, every per-round intermediate, 46 frozen oracle vectors over radices 2..65535 up to 193 numerals covering d > 16, FIPS 197, exhaustive sweeps radix 2 len 20 and radix 10 len 6, property tests, the float scan); limits incl. FF1 only; what this is not (no integrity, not FIPS validated, not audited, not constant-time, no zeroization, no key management); testing; 'Also available for Python' naming the pure-Python implementation as the reference; licence. Badges: crates.io, docs.rs, MSRV, licence. Claims checked against the tree before commit and three narrowed: CI wording (the MSRV job skips the ignored sweeps), the float scan (types, functions and literals, per conformance_tests.rs assert_no_float), 'anyone holding the key can decrypt' instead of an exclusivity claim. The three example blocks are unchanged from STEP-02 | rust/fpr-ff1/README.md | Verify |
| 2026-09-27T11:54:32Z | PLAN-00010-STEP-04 | Section disposition, old README (565 lines at 2786a1b..9653c37) -> new (260 lines). Title/tagline/badges: rewritten for both artifacts (badges CI, PyPI, Python, crates.io, docs.rs, licence 'Python: MIT · Rust: MIT OR Apache-2.0'). Install: kept, pip and cargo. Quick start: kept (Python) plus the crate README's sample 2 program verbatim. Check it against NIST: kept. Security notes: kept, byte-identical (diff). Features: dissolved (single dependency and compiled backend -> intro and Backends; NIST conformance and no-float -> trust section and failure-mode table; limits -> Limits; typed exceptions -> API at a glance). Why you can trust: condensed to five bullets; the failure-mode table kept byte-identical (diff); 'migration safe by construction' -> Migrating; its 'What this is not' -> What this is not. Why FF1 only: condensed, same facts and the never-add statement. Domain limits: short table in README; full comparison table and rationale moved to docs/configuration.md#domain-limits-are-stricter-than-the-2016-text. Scope: folded into What this is not ('permanently') and FF1 only. Supported Python versions: versions in Install and Backends; the uncapped requires-python rationale moved to docs/developer-guide.md Requirements. Roadmap: removed as history (CHANGELOG holds each release). Performance (macOS 1.1-era table and 'Before 1.1.0' history): removed; CHANGELOG [1.1.0] holds the 19x figure. Backends: condensed; the wheel table moved to docs/configuration.md#distribution-and-backend-availability with its 'installed and tested on its own platform' statement; the Linux both-backend table stays as the interim performance table until STEP-05. Rust: merged into the intro, Install and Quick start. API (constructor, __version__, pickling, numerals, strings, exceptions, thread safety): moved verbatim to docs/python-api.md; README keeps an executed 'API at a glance' block and summary (incl. 'pickling serialises the key'). Migrating: full guide moved verbatim to docs/migrating-from-ubiq.md; README keeps identical-ciphertext claim, its test, the twk_max_len=0 trap and a link. FIPS disclaimer and Key material: merged into What this is not (FIPS, audit, constant-time, zeroization for Python and Rust, key management). Development: setup and quality kept; build and secrets remain in the developer guide. Documentation: kept, absolute URLs, new pages added; backlog and directory-structure left to the developer docs. License: kept, shortened. D4 A: no competitor named | README.md; docs/python-api.md; docs/migrating-from-ubiq.md; docs/configuration.md | Pointers and checks |
| 2026-09-27T11:54:32Z | PLAN-00010-STEP-04 | Pointers: tests/test_interoperability.py (module docstring, recipe comment 'migration guide note 5', _migrated_by_the_documented_recipe docstring names docs/migrating-from-ubiq.md) and tests/test_validation.py (two comments) cite the new locations, comment-only; docs/AGENTS.md lists python-api.md and migrating-from-ubiq.md and notes the README/crate README render sites; docs/directory-structure.md lists both new pages and tests/test_docs.py (missed at STEP-02); pyproject.toml sdist include gains both pages; docs/configuration.md and docs/python-api.md link the README's #backends-and-platforms. One example changed while writing: 'API at a glance' first asserted that two tweaks give different ciphertext, which fails with probability 1e-6 under a random key; replaced by a deterministic per-call-tweak round trip | tests/test_interoperability.py; tests/test_validation.py; docs/AGENTS.md; docs/directory-structure.md; docs/developer-guide.md; pyproject.toml | Verify |
| 2026-09-27T11:57:02Z | PLAN-00010-STEP-05 | just bench at 2026-09-27T11:54:47Z (load 0.89 1.83 1.95), AMD RYZEN AI MAX+ PRO 395, Linux 7.2.5, CPython 3.12.13, rustc 1.98.1, release extension via just backend-dev. Backend comparison µs/op python/rust/speedup: r10 n6 28.2/4.6/6.20x; n100 108.7/39.0/2.79x; n1000 937.8/397.5/2.36x; n5000 5212.3/2117.5/2.46x; n20000 26770.3/9774.2/2.74x; r256 n100 141.0/51.3/2.75x; n1000 2542.9/211.4/12.03x; n5000 13105.2/1046.2/12.53x; n20000 52585.5/4167.8/12.62x. GIL probe (n=5000 r10, 80 calls): python serial 5.24 ms, 4 threads 6.10 ms, 0.86x; rust 2.10 / 0.97, 2.17x. Also printed: throughput (n6 ~35,231 ops/s 28.4 µs; construction ~697,685/s 1.4 µs; per numeral 1.1/0.9/1.0/1.4 µs) and value-dependent deltas (r10 len10 -28.6%, len60 -0.1%, len200 +2.6%, r256 len32 +0.9%, r65535 len12 +2.2%). README: one table of this run's figures, copied as printed (µs, speedups to two decimals), with the GIL figure in the same run; the 2.0.0 table removed. docs/python-api.md and docs/configuration.md: parallelism figure 2.9x/0.96x replaced by this run's 2.17x/0.86x, dated. benchmarks/timing.py: comments no longer describe a README throughput table or crossover claim (comment-only). SECURITY.md untouched: its value-dependent table is outside this step, and this run's radix-10 length-10 delta (-28.6%) again disagrees with the published +0.8%, as observed at plan 00007 STEP-12; recorded for the re-review, not changed here | README.md; docs/python-api.md; docs/configuration.md; benchmarks/timing.py; raw output bench-10.txt in the session scratchpad | Verify |
| 2026-09-27T12:07:11Z | PLAN-00010-STEP-06 | Evidence first: a harness (session scratchpad tagcheck.py) extracts the run script of publish.yml's 'Verify tag matches crate version' step and runs it in a temporary tree against seven (crate version, tag) cases. Against the old step: 2 wrong outcomes, crate 2.1.0-rc2 with tag v2.1.0rc2 failed (would have blocked rc2) and tag v2.1.0-rc2 passed (a spelling the project never tags). Change (D1 A): publish-crate's 'if: !prerelease' removed; needs: [quality, publish] kept; the tag check maps exactly one -aN/-bN/-rcN suffix to PEP 440 and compares against the whole tag; job comment rewritten. pyproject.toml: description 'NIST SP 800-38G FF1 format-preserving encryption, with an optional Rust backend.' (80 characters); project URL 'Rust crate' = https://crates.io/crates/fpr-ff1. The crate's description, keywords and category were reviewed and are accurate, so unchanged. docs/developer-guide.md: crate publication covers release candidates, the tag mapping, and the manual fallback if publish-crate fails after PyPI | .github/workflows/publish.yml; pyproject.toml; docs/developer-guide.md; tests/test_contract.py | Verify |
| 2026-09-27T12:19:39Z | PLAN-00010-STEP-07 | Candidate 0345b0d: pyproject.toml 2.1.0rc2; rust/fpr-ff1 and rust/fpr-ff1-rust 2.1.0-rc2; rust/Cargo.lock (cargo update -w: both workspace members only) and uv.lock (project version only); CHANGELOG [2.1.0rc2] — 2026-09-27 (documentation, metadata and release automation; 'no change to accepted inputs, produced ciphertext or the public API') with its compare link. git diff v2.1.0rc1 over src/, rust/*/src and rust/fpr-ff1/tests is empty, as the changelog states | 0345b0d | Local gate |
| 2026-09-27T15:43:16Z | PLAN-00010-STEP-07 | User authorized the push ('push authorised.'). Builder pushed release/v2.1 (ae5acdb..3ab241e, fast-forward; includes the v2.1.0rc1 merge d3f1f97 from main) and dispatched ci.yml. The user did not answer the --release-type minor question; per the Builder's stated default, ci.yml is unchanged and the observation goes to the re-review | origin/release/v2.1 = 3ab241e1de12dd4a69e3ab441c0f1f750f8ad6b0; run https://github.com/joelee/fpr-ff1/actions/runs/36330546176 | Watch the run |
| 2026-09-27T15:43:16Z | PLAN-00010-STEP-07 | The session scratchpad was emptied between turns (/tmp cleared). Recovered from this session's transcript: the work-log helper, the checkpoint script and the v2.1.0rc1 re-review evidence bundle (needed at STEP-09). Lost: raw bench output bench-10.txt (every figure is transcribed in the STEP-05 rows) and the tag-check harness (its seven cases and outcomes are in the STEP-06 rows) | Session scratchpad | None |
| 2026-09-27T16:00:25Z | PLAN-00010-STEP-08 | Hand-off to owner. (1) Push the work-log commits on release/v2.1 (or authorize the Builder to), open a PR release/v2.1 -> main and merge it with a MERGE COMMIT. (2) Tag exactly v2.1.0rc2 on that merge commit; publish a GitHub PRE-RELEASE (notes: session scratchpad v2.1.0rc2-release-notes.md). (3) publish.yml then publishes PyPI and, for the first time, runs publish-crate for a pre-release through Trusted Publishing (environment crates-io). No token is needed. If publish-crate fails after PyPI succeeds, do not retry blindly: report it; the fallback is a manual publish of that run's 'crate' artifact after checking its digest, as in plan 00009 STEP-14. Then the Builder verifies PyPI, crates.io (checksum vs the run's artifact, Trusted Publishing data present), docs.rs, a scratch project, and the rendered pages; owner states the D5 soak | Frozen candidate: origin/release/v2.1 at 3ab241e | Owner release actions |
| 2026-09-27T22:40:00Z | PLAN-00010-STEP-08 | Owner merged PR #15 (release/v2.1 -> main) as merge commit 6379af8, tagged v2.1.0rc2 on it, and published a GitHub pre-release (2026-09-27T22:37:52Z). publish.yml run 36355953834 started on the release event | tag v2.1.0rc2 -> 6379af82bce8de54ac0ac02c065594e4ace92c1b = origin/main head; run https://github.com/joelee/fpr-ff1/actions/runs/36355953834 | Watch the publish run; verify |
| 2026-09-27T22:40:00Z | PLAN-00010-STEP-08 | Owner's D5 statement for 2.1.0rc2: 'soak waived'. Given with the release announcement, before the Builder's registry verification rather than after it as the plan's task order puts it; the statement is recorded as given, and the verification below still gates STEP-09 | User message: 'Released, CI publish is running. Soak waived.' | Verification |
| 2026-09-27T23:00:50Z | PLAN-00010-STEP-09 | Task 1 (D2 A): evidence bundle for v2.0.0..v2.1.0rc2 (0ac0877..6379af8) in the session scratchpad, v2.1.0rc2-review-evidence-bundle.md (321 lines). Part 1 is the v2.0.0..v2.1.0rc1 bundle prepared at plan 00009 STEP-14 (recovered from the session transcript after the scratchpad loss), unchanged apart from headings. Part 2 covers v2.1.0rc1..v2.1.0rc2: the README review (plan 00010 §1 R1-R13) and its resolution; the per-step commit table; five focus areas (claims against evidence, completeness of the moves, soundness of the guards, the publish-crate change, the contract-test refinement); the evidence (CI 36330546176, publish 36355953834, Trusted Publishing data, rendered-page checks, PyPI, installs, scratch consumer, bench); eight deviations and open observations (contract-test refinement; semver-checks vacuous across pre-releases; parallelism 2.17x vs 2.9x; SECURITY.md timing row; two work-log corrections; scratchpad loss; both soaks waived, rc2's before verification; plan 00003's frozen diagram). Predecessor: review 00014 | Session scratchpad v2.1.0rc2-review-evidence-bundle.md | Owner: commission the independent review (task 2) |
| 2026-09-27T23:44:03Z | PLAN-00010-STEP-09 | Review received: docs/reviews/00015-V2_1_0rc2_Release_Review.md (untracked in the worktree; the owner commits review reports), range v2.0.0..v2.1.0rc2 at 6379af8, reviewer model ollama-cloud/deepseek-v4-pro, read-only and static (no builds or tests run), verdict approve: 0 Critical, 0 Major, 0 Medium, 1 Low (REV-00015-LOW-01), 2 open questions. The gate (no Critical or Major) is met | docs/reviews/00015-V2_1_0rc2_Release_Review.md | Builder evaluation; owner dispositions |
| 2026-09-27T23:44:04Z | PLAN-00010-STEP-09 | Builder evaluation. LOW-01 confirmed: the Python trace hook emits A_before/B_before (src/fpr_ff1/_ff1.py:942-943) and the Rust TraceRecord (rust/fpr-ff1/src/engine.rs:380-394) does not; grep finds no test reading them; tests/conftest.py's encrypt_traced docstring says both traces 'share the Python hook's shape', which is inaccurate. Pre-existing (Python since v0.1.0 ccf8c23; the Rust record lacked them at v2.0.0), carried through the split, test-only, no effect on ciphertext. Open question 1 resolved by execution, premise false: bytes() of a multi-byte-format (array 'i', 'd') or non-contiguous memoryview returns its raw bytes on CPython 3.12.13 and 3.14.3; FF1 accepts such a 16-byte view as a key and encrypts; nothing escapes FF1Error. Open question 2 resolved by CI run 36330546176: the semver step reports 'major change', 0 of 254 checks, as recorded at STEP-07; the owner's --release-type minor decision remains open. Coverage: the review's file list and checks cover part 1 and the tag mapping and crate README facts (46 vectors; the 193-numeral vector is radix 2, confirmed), but it does not address part 2 focus areas 1, 2, 3 and 5 (README claims against evidence, completeness of the moves, soundness of the guards, the test_contract refinement) or the bundle's open observations (SECURITY.md timing row, parallelism figure, soak waivers) | Execution of open question 1 on 3.12 and 3.14; grep; git show v2.0.0 | Owner: disposition LOW-01 and the open questions; decide whether the uncovered part 2 items need review before 2.1.0 |
| 2026-09-28T12:02:10Z | PLAN-00010-STEP-09 | Owner dispositions (user: 'Defer LOW-01 to backlog, proceed to STEP-10'). REV-00015-LOW-01: accepted, deferred to docs/backlog.md (recorded at STEP-10); the real fix changes crate source, so it follows 2.1.0. Open questions 1 and 2: closed on the Builder's evidence (question 1's premise disproved by execution; question 2 answered by CI run 36330546176), with no separate owner statement. Part 2 coverage: the owner chose to proceed on review 00015 as it stands. The semver --release-type minor question was not answered; ci.yml stays unchanged. Review 00015 remains untracked in the worktree for the owner to commit | User message | STEP-10 |
| 2026-09-28T12:15:17Z | PLAN-00010-STEP-10 | Release commit 3600eac: pyproject.toml, rust/fpr-ff1 and rust/fpr-ff1-rust at 2.1.0; rust/Cargo.lock (workspace members) and uv.lock (project) updated; CHANGELOG [2.1.0] — 2026-09-28 summarising both candidates, with compare link; SECURITY.md support table: 2.1.x bug and security fixes, 2.0.x superseded (upgrade to 2.1.x), 1.1.x security fixes until 2027-03-25 (the 'until 2.1.0 ships or 2027-03-25, whichever is later' window resolves to the date), 1.0.x unsupported, crate's first stable release 2.1.0 after two pre-releases; docs/backlog.md: the plan 00009/00010 item updated to rc1, rc2 and review 00015 with 2.1.0 still to come, and REV-00015-LOW-01 deferred as a backlog item. No other text still describes 2.1.0 as future (grep) | 3600eac | Local gate |

### Deviations and blockers

| Timestamp (UTC) | Step | Deviation or blocker | Impact | Decision required from |
|---|---|---|---|---|
| 2026-09-27T11:40:22Z | PLAN-00010-STEP-03 | Correction (applied in ff5f258): the Builder first entered STEP-03's start as 2026-09-27T11:38:30Z, typed rather than taken from date -u, which the plan rules forbid. Replaced by 2026-09-27T11:37:47Z, the recorded completion of STEP-02, after which STEP-03 began; the completion time came from date -u | Timestamp provenance only; no effect on the work | None |
| 2026-09-27T11:54:32Z | PLAN-00010-STEP-04 | The plan asks for the section-disposition list in the work log before editing. The Builder drew it up before editing (the section inventory and slices were taken from the pre-edit file, saved as README.before.md in the session scratchpad) but wrote it into the log only at completion, in the row above | Ordering of the record only; the list was checked against the pre-edit file, and the verbatim sections were diffed against it | None |
| 2026-09-27T12:07:11Z | PLAN-00010-STEP-06 | REQ-10's crates.io project URL failed tests/test_contract.py::test_project_urls_match_the_git_remote, which required every project URL to contain github.com/<remote slug>. The test was refined, not relaxed: the single label 'Rust crate' must equal exactly https://crates.io/crates/<name>, with <name> read from rust/fpr-ff1/Cargo.toml, and every other URL keeps the GitHub rule. Probes: a mistyped crate URL (fpr_ff1) and a stale repository slug (py-fpr-ff1) each fail with their own message | A test assertion changed to admit one non-repository URL, with an exact-match check in its place; flagged for the re-review | None; recorded for the re-review |
| 2026-09-27T12:19:39Z | PLAN-00010-STEP-07 | CI's cargo-semver-checks step passes vacuously across pre-releases (0 of 254 checks run), and will for 2.1.0, whose baseline is 2.1.0-rc2. Its first real comparison would be 2.1.1 or 2.2.0. Passing --release-type minor in CI would make the rc2 and 2.1.0 runs meaningful (196 checks pass locally today). Changing ci.yml is outside this plan's steps | AC-level evidence unaffected (STEP-07's criterion is that the step passes or its outcome is recorded and explained); the protection the step implies does not yet exist | User: whether to add --release-type minor to ci.yml's semver step (a small plan amendment) or leave it for the re-review |
| 2026-09-27T12:19:39Z | PLAN-00010-STEP-07 | BLOCKER: task 4 needs release/v2.1 pushed so CI runs at the candidate. Pushing is an outward action needing per-action authorization | STEP-07 cannot complete; STEP-08 onward wait | User: authorize 'git push origin release/v2.1' (Builder then dispatches ci.yml and records the run) |
| 2026-09-28T12:15:17Z | PLAN-00010-STEP-10 | BLOCKER: task 5 needs release/v2.1 pushed so CI runs at the release commit. Also, docs/reviews/00015-V2_1_0rc2_Release_Review.md is untracked in the worktree; the owner commits review reports, and it should be on release/v2.1 before the 2.1.0 PR | STEP-10 cannot complete; STEP-11 waits | User: commit review 00015, and authorize pushing release/v2.1 (Builder then dispatches ci.yml and records the run) |

### Verification results

| Timestamp (UTC) | Step | Command or check | Result | Evidence |
|---|---|---|---|---|
| 2026-09-27T11:24:30Z | PLAN-00010-STEP-01 | mermaid-cli (npx @mermaid-js/mermaid-cli mmdc) over every Mermaid block in README.md, SECURITY.md, CHANGELOG.md, CONTRIBUTING.md, docs/*.md and rust/fpr-ff1/README.md | Pass | One block exists outside docs/plans and docs/reviews (docs/architecture.md); it renders to SVG with no parse error |
| 2026-09-27T11:37:47Z | PLAN-00010-STEP-02 | Guard probes (each re-introduced, run, restored; cmp confirmed byte-identical) | Pass | 9/9 caught, each naming file and line: relative link in README (README.md:12 'docs/developer-guide.md'); relative link in crate README (README.md:75 'LICENSE-MIT'); hidden line (README.md:37 '# fn hidden() {}'); [`ErrorKind`] (README.md:75 intra-doc link); [ErrorKind] (README.md:75 '[ErrorKind]'); broken Python example (NameError 'undefined_helper'); empty skip reason ([' ']); README Rust block drifted from the crate README (README.md:326); NIST assertion removed ({'python','rust'} <= {'rust'}). After restore: 8 passed |
| 2026-09-27T11:37:47Z | PLAN-00010-STEP-02 | ruff format/check; pyright; cargo test --doc; just crate-test; full checkpoint | Pass | ruff clean; pyright 0 errors (after annotating empty containers); doctests 3 passed; crate-test 43 + 9 + 3, sweeps 2 passed; dual gate 1816 passed in 320.31s, TOTAL 345 stmts 120 branches 100%, -k rust 638; Rust-free 942 passed, 245 skipped, 100%; the one warning is test_docs naming the skipped migration example; logs checkpoint-112806 |
| 2026-09-27T11:39:59Z | PLAN-00010-STEP-03 | just crate-test; RUSTDOCFLAGS=-D warnings cargo doc; assert_crate_contents.py --allow-dirty and cargo publish --dry-run --allow-dirty (the clean-tree cargo package --list refuses uncommitted files, so crate-package is rerun after this commit); tests/test_docs.py; grep 'reference' | Pass | crate-test 43 + 9 + 3, sweeps 2 passed; docs clean; 'crate package: 19 entries, 0 problems'; dry run packaged 19 files 127.4KiB and aborted before upload ('fpr-ff1@2.1.0-rc1 already exists' warning expected until STEP-07); guards 8 passed; 'reference' appears twice, both naming the pure-Python implementation |
| 2026-09-27T11:54:32Z | PLAN-00010-STEP-04 | Disposition check; diff of verbatim sections; line count; absolute-link existence; tests/test_docs.py and tests/test_interoperability.py; ruff; sdist contents and guards from the unpacked sdist; full checkpoint | Pass | Every old section accounted for (row above); security notes and failure-mode table byte-identical to the pre-edit README; README 260 lines (criterion: at most 260); all 16 repository links in README, crate README, python-api, migrating and configuration name existing files; test_docs + interoperability 50 passed; ruff clean (one docstring rewrapped for E501); sdist ships docs/python-api.md, docs/migrating-from-ubiq.md, both READMEs and tests/test_docs.py, whose 8 tests pass from the unpacked sdist; dual gate 1816 passed in 259.99s, 100%, -k rust 638; Rust-free 942 passed, 245 skipped, 100%; logs checkpoint-114550 |
| 2026-09-27T11:57:02Z | PLAN-00010-STEP-05 | Every README performance figure against the recorded output (script); stop condition vs plan 00009 STEP-02's run; guards; ruff | Pass | 9 rows, 29 figures, none missing from the output. Largest change against STEP-02's run: rust r10 n6 4.4 -> 4.6 µs (+4.5%), r256 n1000 202.7 -> 211.4 (+4.3%); all within 5%, far inside the 25% stop condition. The parallelism speedup is lower than the 2.9x previously published (2.17x); published as measured. tests/test_docs.py 8 passed; ruff clean; README 260 lines |
| 2026-09-27T12:07:11Z | PLAN-00010-STEP-06 | Tag-check harness (7 cases); actionlint; uv lock --check; twine check; tests/test_contract.py with probes; pyright; ruff; full checkpoint | Pass | Tag check: 7/7 as specified (pass v2.1.0rc2 for 2.1.0-rc2 and v2.1.0 for 2.1.0; fail v2.1.0rc3, v2.1.0, v2.1.0-rc2 for 2.1.0-rc2; v2.1.0rc2 for 2.1.0; v2.1.0a1 for 2.1.0-alpha1, which fails closed). actionlint clean on publish.yml and ci.yml; lock consistent; twine PASSED on sdist and wheel; contract 63 passed, both URL probes caught; pyright 0 errors; dual gate 1816 passed in 258.98s, 100%; Rust-free 942 passed, 100%; logs checkpoint-115849 |
| 2026-09-27T12:19:39Z | PLAN-00010-STEP-07 | Local gate at 0345b0d: full checkpoint; just crate-test; just crate-msrv; just crate-package; tests/test_contract.py and tests/test_docs.py; installed versions | Pass | dual gate 1816 passed in 262.31s, TOTAL 345 stmts 120 branches 100%, -k rust 638; Rust-free 942 passed, 245 skipped, 100%; crate-test 43 + 9 + 3, sweeps 2; crate-msrv (1.89) 43 + 9 + 3; crate-package: docs clean, '19 entries, 0 problems', dry run aborted before upload, fpr-ff1-2.1.0-rc2.crate sha256 71f08a8cc683dc504f976c719818db3686f9ffc82c60a9cf518c41aff81405b8 at 0345b0d; contract + docs 71 passed; fpr_ff1.__version__ 2.1.0rc2, _rs.__version__ 2.1.0-rc2; logs checkpoint-120805 |
| 2026-09-27T12:19:39Z | PLAN-00010-STEP-07 | cargo-semver-checks 0.50.0 (the CI pin), as CI runs it: -p fpr-ff1 --default-features against the crates.io baseline; then with --release-type minor | Pass | As CI runs it: 'fpr-ff1 v2.1.0-rc1 -> v2.1.0-rc2 (major change)', 0 checks, 254 skipped, exit 0: the tool treats any change between pre-releases as permitted to break, so the step passes vacuously, and will again for 2.1.0 against the 2.1.0-rc2 baseline. Forced with --release-type minor: 196 checks pass, 58 skip, 'no semver update required', so the API is compatible with rc1 in fact. CI unchanged (not in this plan); recorded for the re-review |
| 2026-09-27T16:00:25Z | PLAN-00010-STEP-07 | CI run 36330546176 at 3ab241e (candidate 0345b0d + work-log commit) https://github.com/joelee/fpr-ff1/actions/runs/36330546176 | Pass | completed/success, 41/41 jobs. tests/test_docs.py 8 passed on every quality leg (Linux, macOS, Windows; 3.12-3.14) and in rust-conformance. crate-package: 'crate package: 19 entries, 0 problems'; fpr-ff1-2.1.0-rc2.crate sha256 c64b200592ed88bcda30c21ec0b911db38347a074504a23d2f17b2dc37298c04 at 3ab241e (differs from 0345b0d's only through the embedded commit hash); semver step now runs against the crates.io baseline: 'fpr-ff1 v2.1.0-rc1 -> v2.1.0-rc2 (major change)', '0 checks: 0 pass, 254 skip', 'no semver update required', as previewed locally |
| 2026-09-27T22:59:29Z | PLAN-00010-STEP-08 | publish.yml run 36355953834 on v2.1.0rc2 (6379af8) https://github.com/joelee/fpr-ff1/actions/runs/36355953834 | Pass | completed/success, 43/43 jobs, including publish (PyPI) and, for the first time on a pre-release, publish-crate through Trusted Publishing (the D1 A change and the normalised tag check, live) |
| 2026-09-27T22:59:29Z | PLAN-00010-STEP-08 | crates.io fpr-ff1 2.1.0-rc2: checksum vs the run's 'crate' artifact and the downloaded .crate; Trusted Publishing data; metadata | Pass | All three sha256 36a2724a3be8ebf212fc7992bb0b7bc355f3a64db88aff7ffb5d86137b593d22. trustpub_data {provider: github, repository: joelee/fpr-ff1, run_id: 36355953834, sha: 6379af82bce8de54ac0ac02c065594e4ace92c1b}, published_by null (no personal token); license MIT OR Apache-2.0, rust_version 1.89, not yanked. The first Trusted Publishing run is proven (AC-11) |
| 2026-09-27T22:59:29Z | PLAN-00010-STEP-08 | Rendered pages: crates.io README HTML (static.crates.io/readmes/fpr-ff1/fpr-ff1-2.1.0-rc2.html); docs.rs; PyPI JSON description and every link in it | Pass | crates.io: no '# let', no hidden 'Ok::<' line, no literal [Error] or [`Error`]; 18 hrefs, all absolute or #anchor; shows 6124200773 and 'cargo add fpr-ff1'. docs.rs: status.json doc_status true for 2.1.0-rc2; index, struct.FF1, enum.ErrorKind 200; __internal 404; crate root shows the README examples (6124200773, 'Why trust it') and no hidden line. PyPI: summary 'NIST SP 800-38G FF1 format-preserving encryption, with an optional Rust backend.'; project URLs include 'Rust crate'; 25 description links, none relative; all 25 return 200 (crates.io/crates/fpr-ff1 answers 404 to a non-browser request and 200 with Accept: text/html, a property of its web app, not a dead link) (AC-09, AC-12) |
| 2026-09-27T22:59:29Z | PLAN-00010-STEP-08 | PyPI fpr-ff1 2.1.0rc2: files vs run artifacts; attestations; clean installs | Pass | 7 files, 7/7 SHA-256 equal to the run's distributions and wheels, none yanked; pypi-attestations verify OK for all 7 against https://github.com/joelee/fpr-ff1. Installs: 3.12.13 and 3.14.7 (GIL) abi3 manylinux x86_64 wheel, python and rust; 3.14.3 free-threaded py3-none-any, python only (BackendError for rust); --no-binary sdist builds on 3.12 and 3.14, python only. Each passes NIST sample 2 through encrypt() and a radix-10 n=60 (d > 16) case whose ciphertext 3634...77333 equals the value recorded for 2.1.0rc1 at plan 00009 STEP-14: output unchanged across the release |
| 2026-09-27T22:59:29Z | PLAN-00010-STEP-08 | Scratch Cargo project outside the repository on fpr-ff1 = '=2.1.0-rc2' from crates.io (public API only) | Pass | Cargo.lock source registry+crates.io-index, registry-cache .crate sha256 36a2724a...593d22; NIST sample 1 (numerals) and sample 2 (builder, alphabet, tweak -> 6124200773); the same d > 16 case equals PyPI; a 15-byte key -> ErrorKind::KeyLength |
| 2026-09-28T12:02:10Z | PLAN-00010-STEP-09 | Re-review gate: independent review of v2.0.0..v2.1.0rc2 with no Critical or Major finding, every finding dispositioned | Pass | Review 00015 verdict approve, 0 Critical, 0 Major, 0 Medium, 1 Low; LOW-01 deferred to backlog by the owner; open questions closed on evidence (AC-13) |
| 2026-09-28T12:15:17Z | PLAN-00010-STEP-10 | Local gate at 3600eac: tests/test_contract.py and tests/test_docs.py; full checkpoint; just crate-test; just crate-msrv; just crate-package; installed versions | Pass | contract + docs 71 passed; dual gate 1816 passed in 446.44s, TOTAL 345 stmts 120 branches 100%, -k rust 638; Rust-free 942 passed, 245 skipped, 100%; crate-test 43 + 9 + 3, sweeps 2; crate-msrv (1.89) 43 + 9 + 3; crate-package '19 entries, 0 problems', dry run aborted before upload, fpr-ff1-2.1.0.crate sha256 13ad6279a6eac7ce61f0c2a43950ee938a1a418fe7afe48627e246af447917da at 3600eac; fpr_ff1.__version__ 2.1.0, _rs.__version__ 2.1.0; logs checkpoint-120312. cargo-semver-checks against 2.1.0-rc2 is left to CI (expected to report a major change with 0 checks, as for rc2) |

### Completion summary

- **Implementation status:** `blocked`
- **Completed requirements:** PLAN-00010-REQ-01 to REQ-12; REQ-13 re-review passed (review 00015, approve), 2.1.0 release commit gated locally
- **Incomplete requirements:** REQ-13: CI at the release commit, publication of 2.1.0 on both registries and verification
- **Outstanding blockers:** Owner: commit review 00015; authorize the push for STEP-10
- **Review request:** Not ready
<!-- BUILDER_WORK_LOG_END -->

## 18. Planning change log

| Timestamp (UTC) | Plan status | Change | Reason | Requested/approved by |
|---|---|---|---|---|
| 2026-09-27T11:14:29Z | approved | D1 to D4 resolved as recommended (A in each: CI publishes pre-release crates through Trusted Publishing with a normalised tag check; one re-review of `v2.0.0..v2.1.0rc2`; README as a landing page with reference material in `docs/`; no named-competitor table). Plan approved: `plan_status: approved`, `build_ready: true`, `blocking_decisions: 0`, `approved_at` set. Planning content frozen. | Explicit user decision and approval ("D1-D4 as recommended. Commited and Approved.") after the draft was committed in 9b05d7f | User |
| 2026-09-27T11:05:41Z | draft | Initial draft superseding plan 00009 STEP-15 to STEP-17. Adds a documentation release, `2.1.0rc2`, before the re-review and `2.1.0`. It is based on a README review (§1, R1 to R13), which included the PyPI and crates.io rendered pages. | User request of 2026-09-27 to plan an RC2 that improves the documentation, reviewing `README.md` as a landing page covering both implementations | User |

## 19. External references

None. Rendered-page observations (R9, R10) come from the registries' own APIs and static pages,
fetched 2026-09-27: `https://pypi.org/pypi/fpr-ff1/2.1.0rc1/json` and
`https://static.crates.io/readmes/fpr-ff1/fpr-ff1-2.1.0-rc1.html`.

## 20. Confidence

**High.** Every observation in the README review is tied to a line in the tree or to a registry's
own rendering of the published `2.1.0rc1`. The remaining steps repeat a release path that plan
00009 has just exercised. The principal uncertainty is the first Trusted Publishing run and
`cargo semver-checks` against a pre-release baseline. D1 A deliberately moves both onto rc2,
where a failure costs an rc3 rather than the final release.
