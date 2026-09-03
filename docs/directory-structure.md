# Directory Structure

```text
.
├── docs/                   # Maintained project documentation
│   ├── AGENTS.md         # Documentation maintenance rules
│   ├── architecture.md   # System context, modules, and design decisions
│   ├── backlog.md        # High-level feature backlog
│   ├── configuration.md  # Non-secret configuration and secret handling
│   ├── developer-guide.md # Setup, workflow, testing, and release notes
│   └── directory-structure.md # This file
├── src/                   # Python source root
│   └── fpr_ff1/          # FF1 implementation package
│       ├── __init__.py   # Public exports
│       ├── _exceptions.py # Typed exception hierarchy
│       ├── _ff1.py       # FF1 core implementation
│       └── py.typed       # PEP 561 typed-package marker
├── tests/                 # Pytest test root
│   ├── test_smoke.py     # Construction and validation smoke tests
│   ├── test_nist_vectors.py # NIST sample vector conformance tests
│   ├── test_intermediates.py # Per-round intermediate value conformance tests
│   ├── test_validation.py # Parameter and input validation tests
│   ├── test_exact_arithmetic.py # Exact-arithmetic regression tests
│   ├── test_properties.py # Hypothesis property-based and bijectivity tests
│   └── vectors/          # External test fixtures
│       ├── nist_ff1_samples.json
│       └── nist_ff1_intermediates.json
├── justfile               # Local and CI command entry points
├── pyproject.toml         # Python project metadata and tool configuration
├── uv.lock                # Locked dependency resolution
├── README.md              # Project overview and quick start
└── LICENSE                # MIT license
```

## Source

Application code belongs under `src/fpr_ff1/`. The public API is exported from `src/fpr_ff1/__init__.py`.

## Tests

Tests belong under `tests/` and should mirror the behavior they validate. Vector files live in `tests/vectors/` as JSON data files, never inline literals.

## Documentation

Docs belong under `docs/`. Follow `docs/AGENTS.md` when adding or changing documentation.
