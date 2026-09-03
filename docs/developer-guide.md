# Developer Guide

## Requirements

- Python 3.12.x
- `uv`
- `just`
- `gitleaks` (for `just secrets`)

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
just test            # Full suite with the 100% coverage gate
just test-fast       # Inner loop: skips the slow bijectivity sweeps, no gate
just coverage        # Same as `just test` (gate lives in pyproject addopts)
just quality         # format-check + lint + typecheck + full test run
just build           # quality gate + uv build
just secrets         # gitleaks secret scan (must be installed locally)
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

- **Coverage is 100% line and branch, enforced.** The gate lives in `pyproject.toml` `addopts`, so
  a bare `pytest` is gated too. Every raise path must be exercised. If a branch cannot be reached,
  delete it rather than excluding it.
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

## Type Checking

`pyright` runs in strict mode. Keep source and tests fully typed.

## Formatting and Linting

`ruff` owns formatting and linting. Run `just quality` before review.

## CI/CD

Use the portable command sequence in GitHub Actions, GitLab CI, Gitea Actions, or another runner:

```bash
uv sync --locked
uv run ruff format --check .
uv run ruff check .
uv run pyright
FPR_FF1_REQUIRE_ORACLE=1 uv run pytest   # coverage gate is in pyproject addopts
uv build
gitleaks dir . --redact
```

The secret scan is pinned to **gitleaks 8.30.1** in CI (`GITLEAKS_VERSION` in
`.github/workflows/ci.yml`, mirrored as `gitleaks_version` in the `justfile` — keep the two in
sync). The CI pin is authoritative; `just secrets` warns if a locally installed version differs.

## Release Notes

Releases follow Semantic Versioning. Any change to accepted inputs or produced outputs is a major version bump.
