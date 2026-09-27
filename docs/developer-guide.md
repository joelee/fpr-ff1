# Developer Guide

## Requirements

- Python 3.12.x. The package supports CPython 3.12, 3.13 and 3.14, the versions CI exercises and
  the trove classifiers state. `requires-python` is `>=3.12` with no upper bound: a cap would be a
  hard resolution failure on future interpreters, so the floor rises as the CI matrix grows instead.
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
just crate-test      # the fpr-ff1 crate's tests, plus the exhaustive bijectivity sweeps
just crate-msrv      # the crate on Rust 1.89 (rustup toolchain install 1.89 --profile minimal)
just crate-package   # crate docs with warnings denied, package contents, publish dry run
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
  rather than excluding it. The figure measures the Python package only: the Rust core has no
  line-coverage number, and is covered instead by the full dual-backend conformance suite and
  `cargo test`. Do not describe the 100% as covering both backends.
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
- `tests/test_docs.py` guards the two READMEs as they are rendered and copied. `README.md` (the
  PyPI page) and `rust/fpr-ff1/README.md` (the crates.io page and docs.rs crate root) may link only
  to absolute `https://` URLs or same-page anchors. The crate README may not use rustdoc's hidden
  `# ` doctest lines or intra-doc links, both of which crates.io shows verbatim: write complete
  examples with `fn main() -> Result<(), fpr_ff1::Error>` and docs.rs URLs instead. Every Python
  block in `README.md` runs, in order, in one namespace, and every Rust block in it must be a
  verbatim copy of text in the crate README, whose blocks `cargo test --doc` runs. A Python block
  that cannot run (for example, one importing a legacy library) is preceded by
  `<!-- docs-test: skip (reason) -->`. The reason is required, and the test warns with it.
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
`rust/fpr-ff1-rust`, a thin binding over the core in the `rust/fpr-ff1` crate. The conformance suite is parameterised over both backends via the
`backend`/`ff1_factory`/`encrypt_traced` fixtures in `tests/conftest.py`; the rust-parameterised
tests skip locally when the extension is not built and fail hard when
`FPR_FF1_REQUIRE_RUST_BACKEND=1` (the same contract as the oracle).

- `just backend-dev` builds the extension and copies it into `src/fpr_ff1/` (gitignored) so the
  editable install can import it — no pip involvement, so `uv sync` never strips it. Cargo names
  the artifact per platform and CPython requires a per-platform import suffix, so the recipe
  copies `lib_fpr_ff1_rs.so` → `_rs.so` on Linux, `lib_fpr_ff1_rs.dylib` → `_rs.so` on macOS, and
  `_fpr_ff1_rs.dll` → `_rs.pyd` on Windows.
- `just rust-test` runs the Rust tests for the whole workspace (`cargo test`), with
  `FPR_FF1_REQUIRE_FIXTURES=1` so the crate's fixture-backed tests fail rather than skip.
- `just rust-lint` runs the Rust hygiene gates: `cargo fmt --check` and `cargo clippy
  --all-targets -- -D warnings`. Like `rust-test` it is deliberately outside `just quality`, which
  stays Rust-free; CI's `rust-conformance` job runs both commands on every push.

**Run `rustup update stable` before trusting a green `just rust-lint`.** `rust-toolchain.toml`
pins the *channel*, not a version, so CI always lints with the newest stable while a local
toolchain can be months behind — and `-D warnings` means a lint introduced in the interim is a
red gate. That is a deliberate trade (a version pin would force every contributor onto one
release); the cost is that a stale local toolchain can pass a check CI fails. When it happens,
fix the lint or add a narrowly scoped `#[allow]` — never weaken the gate. Prefer the fix: an
`#[allow]` naming a lint that does not exist yet on an older toolchain trips `unknown_lints`
there, which `-D warnings` turns into an error, so the workaround breaks the contributors it was
meant to help.
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
surface from it, builds the platform wheels (maturin, abi3-py312, the five-platform matrix, with
`--locked` and the `rustc`/`cargo` versions printed in each build log), and installs the sdist to
prove the pure-Python fallback and the `BackendError` contract.

Two jobs test the platform wheels as shipped artifacts rather than as source-tree builds:

- **`wheel-test-native`** installs each of the five wheels on a runner of its own platform
  (`ubuntu-24.04`, `ubuntu-24.04-arm`, `macos-latest`, `macos-15-intel`, `windows-latest`) on
  CPython 3.12, 3.13 and 3.14, and runs the NIST, per-round intermediate, AES KAT, frozen KAT,
  dispatch, pickle and smoke modules on both backends. That is 15 legs.
- **`wheel-conformance-abi3`** installs the linux x86_64 wheel on Python 3.14 and runs the full
  suite held to the `rust-conformance` bar: required backend and oracle, the `-k rust` floor and
  100% coverage, measured on the installed package.

Both build their environment the same way: a fresh venv, `uv python install` then
`uv venv --python <version>+gil` (an abi3 wheel cannot load into a free-threaded interpreter), the
locked dev requirements from `uv export --frozen --no-emit-project --no-hashes`, and the one wheel.
They never run `uv sync` or `uv run`, which would install the editable checkout over the wheel.
`.github/scripts/assert_installed_wheel.py` then fails the job unless `fpr_ff1` and `fpr_ff1._rs`
import from the venv's `site-packages`. It also checks the abi3 build, `py.typed` and
`__version__`. Keep that check strict: without it these jobs can test `src/` and still look green.
A deliberate S-expansion defect on a disposable branch turned `rust-conformance`, the abi3 leg and
all 15 native legs red while the pure-Python matrix stayed green (plan 00007 STEP-07,
run 35150890829).

When comparing long numeral lists in tests, do not use a bare `assert a == b`. pytest renders a
full sequence diff for a failing comparison whenever it is verbose or detects CI, and on CPython
3.12 that diff can take hours for thousands of elements, so a failing gate stalls instead of
failing. Report the first diverging index instead, as `tests/test_backend_agreement.py` does. Every action is pinned to a full commit SHA with the
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

**Bump the version in three files together:** `pyproject.toml` `[project].version`,
`rust/fpr-ff1/Cargo.toml` and `rust/fpr-ff1-rust/Cargo.toml` `[package].version`. Cargo cannot parse PEP 440 pre-release
spellings, so the crate carries the semver equivalent — `2.0.0-rc1` for `2.0.0rc1` — and
`tests/test_contract.py::test_crate_version_matches_project_version` compares them after
normalising with `packaging.version.Version`. That test reads both manifests without importing the
extension, so it runs on every CI leg. The Git tag follows `pyproject.toml` exactly (`v2.0.0rc1`,
no hyphen); `publish.yml` verifies it before publishing.

### The Rust crate

CI's `crate-test`, `crate-msrv` and `crate-package` jobs gate the `fpr-ff1` crate: its tests on
Linux, macOS and Windows plus the exhaustive sweeps, its tests on Rust 1.89, and its docs, package
contents (`.github/scripts/assert_crate_contents.py`), publish dry run and, once a version exists,
`cargo-semver-checks` against it. `crate-package` uploads the exact `.crate` it built; `cargo
package` is reproducible, and the digest differs between commits only through the commit hash in
`.cargo_vcs_info.json`.

Publication differs from PyPI in one way. crates.io Trusted Publishing cannot create a crate, so:

1. **The first publication is manual** (plan 00009 D11): the owner downloads the `.crate` built by
   CI at the tagged commit, checks its SHA-256, and runs `cargo publish` with a crates.io token
   scoped to publishing new crates, then revokes the token.
2. **The owner then adds the Trusted Publisher** on crates.io: owner `joelee`, repository
   `fpr-ff1`, workflow `publish.yml`, environment `crates-io`.
3. **Every later release, release candidates included** (plan 00010 D1), is published by
   `publish.yml`'s `publish-crate` job, after PyPI succeeds, with a short-lived token from
   `rust-lang/crates-io-auth-action`. The job's tag check maps the crate's semver pre-release
   suffix (`-rc2`) to the tag's PEP 440 spelling (`rc2`) and refuses any other mismatch. If the job
   fails after PyPI has published, the owner can publish that run's CI-built `.crate` by hand, as
   in step 1, so the two registries still hold the same release.

A published crate version can be yanked but never replaced; recovery is a new patch version.
