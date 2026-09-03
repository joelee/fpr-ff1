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

# Full suite including slow tests (bijectivity), with the 100% coverage gate.
# Coverage flags live in pyproject addopts so a bare `pytest` is gated too.
coverage:
    uv run pytest

# Fast inner-loop run: skips the exhaustive bijectivity sweep, no gate.
test-fast:
    uv run pytest -m 'not slow' --no-cov

quality: format-check lint typecheck coverage

build: quality
    uv build

secrets:
    @if command -v gitleaks >/dev/null 2>&1; then \
        installed=$$(gitleaks version 2>/dev/null | head -1); \
        if [ "$$installed" != "v{{gitleaks_version}}" ] && [ "$$installed" != "{{gitleaks_version}}" ]; then \
            echo "warning: gitleaks $$installed is running; CI pins v{{gitleaks_version}} (authoritative)."; \
        fi; \
        gitleaks dir . --redact; \
    else \
        echo "gitleaks is not installed. Install it before running secret scans."; \
        exit 127; \
    fi

ci: sync quality build secrets
