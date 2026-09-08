# CLAUDE.md

Guidance for Claude Code when working in this repository.

## Read this first

**`AGENTS.md` in the repository root is the normative agent contract.** Read it fully
before any code change. This file is the Claude Code entry point: it points at the
authoritative documents and records the operational details Claude needs day to day.
Where this file and `AGENTS.md` disagree, `AGENTS.md` wins.

Directory-scoped contracts, each of which must be read before writing in that
directory:

| Path | Contract |
|---|---|
| `docs/` | `docs/AGENTS.md` — which documents exist and when each must be updated |
| `docs/ideas/` | `docs/ideas/AGENTS.md` — immutable idea reports |
| `docs/reviews/` | `docs/reviews/AGENTS.md` — immutable code-review reports |
| `docs/plans/` | `docs/plans/AGENTS.md` — numbered delivery plans, clean-worktree gate, Builder rules |

## What this project is

`fpr-ff1` is a standalone PyPI library implementing **FF1**, the format-preserving
encryption mode of NIST SP 800-38G. The design goal is that a reviewer can compare
the source against SP 800-38G line by line and find no gaps.

Two backends produce **bit-identical** ciphertext:

- `src/fpr_ff1/_ff1.py` — the pure-Python **reference** implementation and the default.
- `rust/fpr-ff1-rust/src/lib.rs` — an **optional, opt-in** compiled backend
  (`FF1(..., backend="rust")`), exposed as `fpr_ff1._rs` via PyO3.

The Rust core mirrors `_ff1.py` step for step. **A change to one core is a change to
both**, proven by the dual-backend test suite.

## Commands

Local development uses `uv` and `just`.

```bash
just setup          # create .venv and install deps
just quality        # format-check + lint + typecheck + coverage (the gate); Rust-free by design
just test-fast      # inner loop: skips the slow bijectivity sweep, no coverage gate
just coverage       # full suite at the 100% line-and-branch floor
just bench          # reproducible timing harness; the source of every published number
just secrets        # gitleaks scan (must be installed locally)
```

Compiled backend (requires a local Rust toolchain; `rust-toolchain.toml` pins the channel):

```bash
just backend-dev    # cargo build --release + copy the cdylib to src/fpr_ff1/_rs.so
just rust-test      # cargo test --manifest-path rust/Cargo.toml
just rust-lint      # cargo fmt --check + cargo clippy --all-targets -- -D warnings
```

The full dual-backend gate — the checkpoint that matters after any core change:

```bash
FPR_FF1_REQUIRE_RUST_BACKEND=1 FPR_FF1_REQUIRE_ORACLE=1 \
  uv run pytest --cov=fpr_ff1 --cov-report=term-missing --cov-fail-under=100
```

Both environment variables turn a *skip* into a *failure*. A silently skipped
conformance suite is indistinguishable from a passing one; never remove them to make a
run go green.

## Non-negotiables

These come from `AGENTS.md`; they are repeated here because violating one produces
plausible-looking but wrong ciphertext, or breaks the project's reason to exist.

- **Never add FF3 or FF3-1.** Being FF1-only is a deliberate, documented feature.
- **No floating-point arithmetic anywhere in the FF1 core.** Bit length is
  `(radix ** v - 1).bit_length()` — never `math.log2`, `math.ceil`, `**0.5`, or a float
  literal. This is the Bouncy Castle bug class; `tests/test_exact_arithmetic.py`
  AST-scans for it.
- **`b` is derived from `v`, not `u`.** They differ when `n` is odd.
- **Never cache a cipher context on the instance.** Instances are thread-safe;
  a live context would be shared mutable state.
- **Never regenerate NIST fixtures from this implementation**, and never commit
  self-generated outputs as "vectors".
- **Never claim FIPS validation or key zeroization.**
- **Never weaken a test to make it pass.** Conformance is the product.
- **Never add a runtime dependency beyond `cryptography`** without explicit approval.
- **100% line and branch coverage** on `fpr_ff1` is a hard floor (`fail_under = 100`).
  Exercise every raise path; delete unreachable branches rather than leaving dead code.
- **Semantic versioning.** Any change to accepted inputs or produced outputs is major.
- The pure-Python path must never depend on Rust being installed. `just quality` stays
  Rust-free.

## Version lock-step

`pyproject.toml` `[project].version` and `rust/fpr-ff1-rust/Cargo.toml`
`[package].version` are bumped together. Cargo requires the semver form, so PEP 440
`2.0.0rc1` is `2.0.0-rc1` in the crate; `tests/test_contract.py` compares them after
normalising with `packaging.version.Version`. Git tags follow `pyproject.toml`
exactly (`v2.0.0rc1`, no hyphen) — `publish.yml` compares against it.

## Tests

`tests/conftest.py` provides `backend`, `ff1_factory`, and `encrypt_traced`. Every
conformance module constructs instances through `ff1_factory` (or draws `backend` from
`tests.conftest.BACKENDS`) so it runs on **both** backends. The per-round intermediate
tests (`tests/test_intermediates.py`) are the real conformance evidence: two
compensating bugs can pass an output test but cannot pass an intermediate test.

Vector files live in `tests/vectors/` as JSON, never inline literals.

## Working with plans

`docs/plans/` holds numbered delivery plans. When executing one as Builder:

- Builder owns **only** the Builder-maintained front-matter keys and the content
  between `<!-- BUILDER_WORK_LOG_START -->` and `<!-- BUILDER_WORK_LOG_END -->`.
  Never edit approved planning content.
- Record every step's status, evidence, and verification result in the work log, with
  UTC timestamps from `date -u +%Y-%m-%dT%H:%M:%SZ` — never estimated.
- Honour each step's **stop conditions**: escalate to the user rather than working
  around one.
- Follow the step order and commit granularity the plan specifies; one revertible
  commit per step keeps the history bisectable for ciphertext questions.

## Documentation

Documentation is part of the product: update the matching document in the same change
that makes it true. `docs/AGENTS.md` maps each kind of change to the document it must
update.
