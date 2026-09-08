# Directory Structure

```text
.
├── .github/
│   ├── workflows/          # CI and release pipelines
│   │   ├── ci.yml         # Quality matrix (3 OS × 3 Pythons), rust-conformance, audit,
│   │   │                  # build, wheel-build/test, sdist-test, secret scan
│   │   └── publish.yml    # Release gate + Trusted Publishing to PyPI (publishes the gated artifact)
│   ├── dependabot.yml     # Automated updates for pinned actions and dependencies
│   ├── ISSUE_TEMPLATE/    # Bug report, feature request, security redirect
│   └── PULL_REQUEST_TEMPLATE.md
├── benchmarks/
│   └── timing.py          # Reproducible timing/throughput harness (just bench)
├── docs/                   # Maintained project documentation
│   ├── AGENTS.md          # Documentation maintenance rules
│   ├── architecture.md    # System context, modules, and design decisions
│   ├── backlog.md          # High-level feature backlog, decisions, and dropped items
│   ├── configuration.md    # FF1 constructor parameters, runtime constraints, thread safety
│   ├── developer-guide.md  # Setup, workflow, testing, and release notes
│   ├── directory-structure.md # This file
│   ├── ideas/             # Immutable idea reports (see ideas/AGENTS.md)
│   │   └── AGENTS.md      # Contract for any agent writing to ideas/
│   ├── reviews/           # Immutable code-review reports (see reviews/AGENTS.md)
│   │   └── AGENTS.md      # Contract for any agent writing to reviews/
│   └── plans/             # Delivery plans (see plans/AGENTS.md)
│       └── AGENTS.md      # Contract for any agent writing to plans/
├── src/                    # Python source root
│   └── fpr_ff1/            # FF1 implementation package
│       ├── __init__.py     # Public exports and __version__
│       ├── _exceptions.py  # Typed exception hierarchy
│       ├── _ff1.py         # FF1 core implementation (the reference backend)
│       └── py.typed        # PEP 561 typed-package marker
├── rust/                    # Optional compiled backend (plan 00003 E2)
│   ├── Cargo.toml          # Workspace manifest
│   ├── Cargo.lock          # Locked Rust dependencies (committed, like uv.lock)
│   └── fpr-ff1-rust/       # The PyO3 crate (module fpr_ff1._rs)
│       ├── Cargo.toml
│       └── src/
│           ├── lib.rs      # Algorithm 7 core + PRF + PyO3 bindings
│           └── tests.rs    # Rust unit tests
├── tests/                  # Pytest test root
│   ├── __init__.py
│   ├── conftest.py         # Shared fixtures (NIST loader, backend/ff1_factory/encrypt_traced)
│   ├── _oracle/            # Differential-testing oracle loader
│   │   ├── __init__.py     # ubiq_security_fpe loader; CI-required via FPR_FF1_REQUIRE_ORACLE
│   │   ├── _m2crypto_shim.py # cryptography-backed M2Crypto.EVP shim (the oracle imports
│   │   │                   # M2Crypto, which does not build on current toolchains)
│   │   └── generate_kat.py # Dev-only generator for the frozen KAT vectors (run manually)
│   ├── test_smoke.py       # Construction and validation smoke tests
│   ├── test_nist_vectors.py # NIST sample vector conformance tests (both backends)
│   ├── test_intermediates.py # Per-round intermediate value conformance tests (both backends)
│   ├── test_validation.py  # Parameter and input validation tests
│   ├── test_sequence_validation.py # Lying-Sequence / non-Sequence rejection regression tests
│   ├── test_exact_arithmetic.py # Exact-arithmetic regression and AST float scan
│   ├── test_properties.py  # Hypothesis property-based and bijectivity tests
│   ├── test_differential.py # Differential tests against the independent oracle
│   ├── test_frozen_kat.py  # Frozen oracle-derived KAT vectors (runs without the oracle)
│   ├── test_interoperability.py # Bidirectional ubiq_security_fpe compatibility
│   ├── test_pickle.py      # Pickle/deepcopy/multiprocessing round-trip and __version__ tests
│   ├── test_thread_safety.py # Structural and concurrency thread-safety tests
│   ├── test_backend_dispatch.py # backend keyword, dispatch, and BackendError tests
│   ├── test_rust_aes_validation.py # Rust AES KAT + PRF-equality validation
│   ├── test_contract.py    # Whole-surface assertions (typed rejections, repo hygiene,
│   │                       # the pyproject/Cargo version lock-step)
│   ├── test_conversion_equivalence.py # Divide-and-conquer NUM/STR_radix vs the
│   │                       # spec-reference implementations
│   └── vectors/            # External test fixtures (never regenerated from this code)
│       ├── nist_ff1_samples.json
│       ├── nist_ff1_intermediates.json
│       ├── aes_kat_fips197.json # NIST FIPS 197 Appendix C AES KAT vectors
│       └── oracle_kat_frozen.json # Oracle-generated KAT vectors with provenance header
├── AGENTS.md                # Agent contract for the repository
├── CLAUDE.md                # Claude Code entry point; defers to AGENTS.md
├── CHANGELOG.md             # Release history, including accepted-input changes
├── CODE_OF_CONDUCT.md       # Contributor Covenant
├── CONTRIBUTING.md          # Contribution rules (vector provenance, quality gate, security)
├── README.md                # Project overview and quick start
├── SECURITY.md              # Disclosure process and known limitations
├── LICENSE                  # MIT license
├── pyproject.toml           # Python project metadata and tool configuration (incl. [tool.maturin])
├── uv.lock                  # Locked dependency resolution
├── rust-toolchain.toml      # Rust toolchain pin (stable, minimal) for the compiled backend
├── justfile                 # Local and CI command entry points
├── .gitleaks.toml           # Secret-scan allowlist
├── .gitattributes           # Line-ending normalisation; vector fixtures pinned to LF
├── .pre-commit-config.yaml  # Local hooks mirroring `just quality` (ruff, ruff-format, gitleaks)
└── .gitignore               # Ignore rules (includes the tool-local .codegraph/ index)
```

## Source

Application code belongs under `src/fpr_ff1/`. The public API is exported from `src/fpr_ff1/__init__.py`.

## Tests

Tests belong under `tests/` and should mirror the behavior they validate. Vector files live in `tests/vectors/` as JSON data files, never inline literals. The differential oracle in `tests/_oracle/` is a dev-only dependency; its tests skip locally if the oracle is missing but fail in CI (`FPR_FF1_REQUIRE_ORACLE=1`).

## Documentation

Docs belong under `docs/`. Follow `docs/AGENTS.md` when adding or changing documentation.