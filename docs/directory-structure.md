# Directory Structure

```text
.
├── .github/workflows/      # CI and release pipelines
│   ├── ci.yml             # Quality matrix (3 OS × 3 Pythons), build, secret scan
│   └── publish.yml        # Release gate + Trusted Publishing to PyPI
├── docs/                   # Maintained project documentation
│   ├── AGENTS.md          # Documentation maintenance rules
│   ├── architecture.md    # System context, modules, and design decisions
│   ├── backlog.md          # High-level feature backlog, decisions, and dropped items
│   ├── configuration.md    # FF1 constructor parameters, runtime constraints, thread safety
│   ├── developer-guide.md  # Setup, workflow, testing, and release notes
│   ├── directory-structure.md # This file
│   └── plans/             # Execution plans derived from review reports
├── src/                    # Python source root
│   └── fpr_ff1/            # FF1 implementation package
│       ├── __init__.py     # Public exports
│       ├── _exceptions.py  # Typed exception hierarchy
│       ├── _ff1.py         # FF1 core implementation
│       └── py.typed        # PEP 561 typed-package marker
├── tests/                  # Pytest test root
│   ├── __init__.py
│   ├── conftest.py         # Shared fixtures (NIST sample loader)
│   ├── _oracle/            # Differential-testing oracle loader
│   │   ├── __init__.py     # ubiq_security_fpe loader; CI-required via FPR_FF1_REQUIRE_ORACLE
│   │   ├── _m2crypto_shim.py # cryptography-backed M2Crypto.EVP shim (the oracle imports
│   │   │                   # M2Crypto, which does not build on current toolchains)
│   │   └── generate_kat.py # Dev-only generator for the frozen KAT vectors (run manually)
│   ├── test_smoke.py       # Construction and validation smoke tests
│   ├── test_nist_vectors.py # NIST sample vector conformance tests
│   ├── test_intermediates.py # Per-round intermediate value conformance tests
│   ├── test_validation.py  # Parameter and input validation tests
│   ├── test_sequence_validation.py # Lying-Sequence / non-Sequence rejection regression tests
│   ├── test_exact_arithmetic.py # Exact-arithmetic regression and AST float scan
│   ├── test_properties.py  # Hypothesis property-based and bijectivity tests
│   ├── test_differential.py # Differential tests against the independent oracle
│   ├── test_frozen_kat.py  # Frozen oracle-derived KAT vectors (runs without the oracle)
│   ├── test_interoperability.py # Bidirectional ubiq_security_fpe compatibility
│   ├── test_pickle.py      # Pickle/deepcopy/multiprocessing round-trip and __version__ tests
│   ├── test_thread_safety.py # Structural and concurrency thread-safety tests
│   ├── test_contract.py    # Whole-surface assertions (typed rejections, repo hygiene)
│   └── vectors/            # External test fixtures (never regenerated from this code)
│       ├── nist_ff1_samples.json
│       ├── nist_ff1_intermediates.json
│       └── oracle_kat_frozen.json # Oracle-generated KAT vectors with provenance header
├── AGENTS.md                # Agent contract for the repository
├── CHANGELOG.md             # Release history, including accepted-input changes
├── README.md                # Project overview and quick start
├── SECURITY.md              # Disclosure process and known limitations
├── LICENSE                  # MIT license
├── pyproject.toml           # Python project metadata and tool configuration
├── uv.lock                  # Locked dependency resolution
├── justfile                 # Local and CI command entry points
├── .gitleaks.toml           # Secret-scan allowlist
├── .gitattributes           # Line-ending normalisation; vector fixtures pinned to LF
└── .gitignore               # Ignore rules (.codegraph/ is self-ignored via its own .gitignore)
```

## Source

Application code belongs under `src/fpr_ff1/`. The public API is exported from `src/fpr_ff1/__init__.py`.

## Tests

Tests belong under `tests/` and should mirror the behavior they validate. Vector files live in `tests/vectors/` as JSON data files, never inline literals. The differential oracle in `tests/_oracle/` is a dev-only dependency; its tests skip locally if the oracle is missing but fail in CI (`FPR_FF1_REQUIRE_ORACLE=1`).

## Documentation

Docs belong under `docs/`. Follow `docs/AGENTS.md` when adding or changing documentation.