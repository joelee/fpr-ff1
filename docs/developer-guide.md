# Developer Guide

## Requirements

- Python 3.12.x
- `uv`
- `just`
- `gitleaks` (for `just secrets`)
- A Rust toolchain (for the optional compiled backend; `rustup` recommended — see `rust-toolchain.toml`)

## Setup

```bash
just setup
```

This reads `.python-version` (currently 3.12.13), creates `.venv`, and installs dependencies.

## Development Commands

```bash
just format          # Run ruff formatter
just format-check    # Check formatting without writing
just lint            # Run ruff linter
just lint-fix        # Auto-fix ruff issues where possible
just typecheck       # Run pyright in strict mode
just test            # Full suite (no coverage gate; see coverage below)
just test-fast       # Inner loop: skips the slow bijectivity sweeps, no gate
just coverage        # Full suite with the 100% line-and-branch coverage gate
just quality         # format-check + lint + typecheck + full test run
just build           # quality gate + uv build
just secrets         # gitleaks secret scan (must be installed locally)
just bench           # reproducible timing/throughput tables (benchmarks/timing.py)
just rust-test       # Rust core unit tests (cargo test)
just rust-lint       # cargo fmt --check + cargo clippy --all-targets -- -D warnings
just backend-dev     # build the compiled backend into src/fpr_ff1/_rs.so (dev loop)
just ci              # sync + quality + build + secrets
```

## Testing Standards

### Which command to run

**Use `just test-fast` as your inner loop.** It skips the two exhaustive bijectivity sweeps
(radix 2 at length 20, and radix 10 at length 6 — about 2 million encryptions, ~85 s) and disables
coverage, so it completes in well under a second.

Run `just test` or `just quality` before pushing. Those include the bijectivity sweeps *and* the
100% coverage gate. The full run takes roughly 3.5 minutes, and that is deliberate: exhaustive
bijectivity is the strongest correctness statement available for a permutation, so it belongs in
the gate rather than in a checklist nobody runs.

```bash
just test-fast   # edit-test loop
just quality     # before pushing
```

### Standards

- **Coverage is 100% line and branch, enforced.** The gate is invoked by `just coverage`, `just
  quality`, and CI's explicit pytest flags — not by `pyproject.toml` `addopts`, so a bare `pytest`
  from an unpacked sdist stays runnable for downstream packagers who have not installed
  `pytest-cov`. Every raise path must be exercised. If a branch cannot be reached, delete it
  rather than excluding it.
- Conformance fixtures belong in `tests/vectors/` as JSON. **Never inline self-generated expected
  values**, and never regenerate the NIST fixtures from this implementation — that turns a record
  of the standard into a record of whatever the code currently does.
- Radices without published NIST vectors are covered by differential tests against an independent
  oracle, never by expected values authored here. See `tests/test_differential.py`.
- Per-round intermediates are asserted through the private `FF1._encrypt_traced` hook. It is a
  private method rather than a parameter on the public methods, so the documented API surface stays
  exactly as specified. Do not expose it publicly.
- `tests/test_contract.py` holds whole-surface assertions — that every rejection is typed, and that
  required files are tracked by git. Add new malformed-input cases to the sweep there rather than
  only as one-off tests; a case-by-case suite passes happily while an untested input escapes.
- Register long-running tests with `@pytest.mark.slow` so `just test-fast` can exclude them. They
  still run in `just test`, `just quality` and CI.

### The differential oracle

`ubiq-security-fpe` is a dev-only dependency used as an independent reference. It imports
`M2Crypto`, which does not build on current toolchains, so `tests/_oracle/` vendors a small
`cryptography`-backed shim.

Oracle-backed tests **skip** if the package is missing, so a broken local install does not block
development. In CI, `FPR_FF1_REQUIRE_ORACLE=1` turns that skip into a hard failure — otherwise a
silent skip would look exactly like a pass, and the differential suite is the only coverage for
most radices.

### The compiled backend

The optional `backend="rust"` path is a PyO3 extension (`fpr_ff1._rs`) built from
`rust/fpr-ff1-rust`. The conformance suite is parameterised over both backends via the
`backend`/`ff1_factory`/`encrypt_traced` fixtures in `tests/conftest.py`; the rust-parameterised
tests skip locally when the extension is not built and fail hard when
`FPR_FF1_REQUIRE_RUST_BACKEND=1` (the same contract as the oracle).

- `just backend-dev` builds the extension and copies it into `src/fpr_ff1/` (gitignored) so the
  editable install can import it — no pip involvement, so `uv sync` never strips it. Cargo names
  the artifact per platform and CPython requires a per-platform import suffix, so the recipe
  copies `lib_fpr_ff1_rs.so` → `_rs.so` on Linux, `lib_fpr_ff1_rs.dylib` → `_rs.so` on macOS, and
  `_fpr_ff1_rs.dll` → `_rs.pyd` on Windows.
- `just rust-test` runs the Rust unit tests (`cargo test`).
- `just rust-lint` runs the Rust hygiene gates: `cargo fmt --check` and `cargo clippy
  --all-targets -- -D warnings`. Like `rust-test` it is deliberately outside `just quality`, which
  stays Rust-free; CI's `rust-conformance` job runs both commands on every push.
- The Rust AES core is validated against the NIST FIPS 197 Appendix C vectors and the Python
  path's PRF output in `tests/test_rust_aes_validation.py`; the per-round intermediates are
  asserted on both backends in `tests/test_intermediates.py` via the trace bridge.

The pure-Python path never imports the extension, so the package builds, installs, and passes the
full suite without a Rust toolchain; `backend="rust"` then raises `BackendError`.

### Frozen oracle KAT vectors

The oracle is deprecated and unmaintained; the day it stops installing, the live differential
suite goes dark. `tests/vectors/oracle_kat_frozen.json` is the durability layer: known-answer
vectors **generated by the oracle** (`uv run python -m tests._oracle.generate_kat`, run manually,
never in CI), with a provenance header recording the oracle version and generation date.
`tests/test_frozen_kat.py` asserts this implementation reproduces every vector and runs with no
oracle dependency at all. The live suite stays primary while the oracle installs; the frozen
vectors carry the evidence when it cannot. This does not weaken the no-self-authored-vectors
rule — every expected value comes from the independent implementation.

## Type Checking

`pyright` runs in strict mode. Keep source and tests fully typed.

## Formatting and Linting

`ruff` owns formatting and linting. Run `just quality` before review.

## Pre-commit Hooks

`.pre-commit-config.yaml` wires the same tools as the CI gate — ruff, ruff-format, and the pinned
gitleaks (via the locally installed binary, so no Go toolchain) — so formatter drift and leaked
secrets are caught at commit time. Install the hooks once per clone:

```bash
uv run pre-commit install      # hook into git's commit action
uv run pre-commit run --all-files   # run everything once, CI-style
```

The hook revs are pinned to full commit SHAs; `uv run pre-commit autoupdate` refreshes them.

## CI/CD

Use the portable command sequence in GitHub Actions, GitLab CI, Gitea Actions, or another runner:

```bash
uv sync --locked
uv run ruff format --check .
uv run ruff check .
uv run pyright
FPR_FF1_REQUIRE_ORACLE=1 uv run pytest --cov=fpr_ff1 --cov-report=term-missing --cov-fail-under=100
uv build
gitleaks dir . --redact
```

CI also runs a `rust-conformance` job (`ubuntu-latest`): it builds the extension with the same two
commands as `just backend-dev`, then runs the full suite on **both** backends with
`FPR_FF1_REQUIRE_RUST_BACKEND=1` at the 100% coverage floor, asserts that `-k rust` still selects at
least 500 tests (a collapsed parameterisation is a silent failure), and runs `cargo test`,
`cargo fmt --check` and `cargo clippy --all-targets -- -D warnings`. Before it existed the only
Rust execution in the pipeline was a single NIST vector, so a defect reachable only at `d > 16`
could have passed the gate. `publish.yml` reuses the whole workflow, so this job gates releases.

CI additionally runs a dependency-audit job (`pip-audit` against `uv.lock` and against the declared
minimum dependency set, plus `cargo-audit` against `rust/Cargo.lock`), installs gitleaks only after
verifying the release tarball against the published checksums, asserts the sdist contents against a
forbidden-path list, installs the built wheel into a clean environment to exercise the public
surface from it, builds the platform wheels (maturin, abi3-py312, the five-platform matrix) and
installs the linux wheel to exercise both backends, and installs the sdist to prove the pure-Python
fallback and the `BackendError` contract. Every action is pinned to a full commit SHA with the
version in a trailing comment; Dependabot (`.github/dependabot.yml`) covers three ecosystems —
`github-actions`, `uv`, and `cargo` for `/rust` — and raises PRs when a pinned action or a
dependency in either lock file moves. The publish workflow downloads the distributions and wheels artifacts built
and checked by the release gate rather than rebuilding, and it verifies the release tag matches the
project version before publishing.

The secret scan is pinned to **gitleaks 8.30.1** in CI (`GITLEAKS_VERSION` in
`.github/workflows/ci.yml`, mirrored as `gitleaks_version` in the `justfile` — keep the two in
sync). The CI pin is authoritative; `just secrets` warns if a locally installed version differs.

## Release Notes

Releases follow Semantic Versioning. Any change to accepted inputs or produced outputs is a major version bump.

**Bump the version in two files together:** `pyproject.toml` `[project].version` and
`rust/fpr-ff1-rust/Cargo.toml` `[package].version`. Cargo cannot parse PEP 440 pre-release
spellings, so the crate carries the semver equivalent — `2.0.0-rc1` for `2.0.0rc1` — and
`tests/test_contract.py::test_crate_version_matches_project_version` compares them after
normalising with `packaging.version.Version`. That test reads both manifests without importing the
extension, so it runs on every CI leg. The Git tag follows `pyproject.toml` exactly (`v2.0.0rc1`,
no hyphen); `publish.yml` verifies it before publishing.
