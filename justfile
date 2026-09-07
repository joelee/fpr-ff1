set shell := ["bash", "-eu", "-o", "pipefail", "-c"]

python_version := `cat .python-version`

# Mirror of GITLEAKS_VERSION in .github/workflows/ci.yml — keep in sync.
gitleaks_version := "8.30.1"

default:
    @just --list

setup:
    @if command -v pyenv >/dev/null 2>&1; then \
        if pyenv versions --bare | sed 's/^[[:space:]]*//' | grep -qx "{{python_version}}"; then \
            pyenv local "{{python_version}}"; \
        else \
            echo "pyenv is installed, but Python {{python_version}} is not. Install it or let uv resolve Python 3.12."; \
        fi; \
    fi
    @if [ -d .venv ]; then \
        echo ".venv already exists; reusing it."; \
    else \
        uv venv --python "{{python_version}}"; \
    fi
    uv sync

sync:
    uv sync

lock:
    uv lock

format:
    uv run ruff format .

format-check:
    uv run ruff format --check .

lint:
    uv run ruff check .

lint-fix:
    uv run ruff check --fix .

typecheck:
    uv run pyright

test:
    uv run pytest

# Full suite with the 100% line-and-branch coverage gate.  The flags live
# here and in CI's test step (not in pyproject addopts) so a bare `pytest`
# from an unpacked sdist does not fail for downstream packagers who have not
# installed pytest-cov.
coverage:
    uv run pytest --cov=fpr_ff1 --cov-report=term-missing --cov-fail-under=100

# Fast inner-loop run: skips the exhaustive bijectivity sweep, no gate.
test-fast:
    uv run pytest -m 'not slow' --no-cov

quality: format-check lint typecheck coverage

build: quality
    uv build

secrets:
    @if command -v gitleaks >/dev/null 2>&1; then \
        installed=$(gitleaks version 2>/dev/null | head -1); \
        if [ "$installed" != "v{{gitleaks_version}}" ] && [ "$installed" != "{{gitleaks_version}}" ]; then \
            echo "warning: gitleaks $installed is running; CI pins v{{gitleaks_version}} (authoritative)."; \
        fi; \
        gitleaks dir . --redact; \
    else \
        echo "gitleaks is not installed. Install it before running secret scans."; \
        exit 127; \
    fi

# Reproducible timing/throughput harness; prints the tables published in
# SECURITY.md and README.md (see benchmarks/timing.py).
bench:
    uv run python benchmarks/timing.py

# Rust core unit tests for the accelerated backend (plan 00003 E2).
# Requires a local Rust toolchain; deliberately NOT part of `quality` —
# the pure-Python path must never depend on Rust being installed.
rust-test:
    cargo test --manifest-path rust/Cargo.toml

# Build the Rust accelerated backend into the project venv as _fpr_ff1_rs
# (plan 00003 E2 dev loop). Uses maturin via uvx with VIRTUAL_ENV pointing
# at the project venv, so no dev-dependency churn in uv.lock. Requires a
# local Rust toolchain.
backend-dev:
    VIRTUAL_ENV=.venv uvx maturin develop -m rust/fpr-ff1-rust/Cargo.toml

ci: sync quality build secrets
