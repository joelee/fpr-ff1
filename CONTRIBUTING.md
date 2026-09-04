# Contributing to fpr-ff1

Thank you for considering a contribution. This is a small cryptographic library whose entire
value is correctness, so the bar for changes is deliberately high and most of this document is
about not breaking conformance.

## Getting started

```bash
just setup    # create .venv and install dependencies
just quality  # format check, lint, typecheck, full test suite with the coverage gate
```

You need Python 3.12, [`uv`](https://docs.astral.sh/uv/), and [`just`](https://just.systems/).
See `docs/developer-guide.md` for the full workflow.

## The quality gate

Every change must pass `just quality`: ruff format check, ruff lint, pyright strict, and the full
test suite with **100% line and branch coverage enforced** — the build fails below it. Every
raise path must be exercised by a test; if a branch cannot be reached, delete it rather than
excluding it.

## Vector provenance rules (non-negotiable)

- **Never regenerate the NIST fixtures** (`tests/vectors/nist_ff1_samples.json`,
  `nist_ff1_intermediates.json`) from this implementation. They are transcriptions of the
  published standard; regenerating them turns a record of the standard into a record of whatever
  the code currently does.
- **Never commit self-generated expected values as test vectors.** Expected outputs authored from
  this package test nothing and lock in bugs permanently.
- The differential oracle (`ubiq-security-fpe`, dev-only) is the reference for radices without
  published vectors. The frozen KAT file (`tests/vectors/oracle_kat_frozen.json`) is
  **oracle-generated** with a provenance header — it is regenerated only by
  `uv run python -m tests._oracle.generate_kat`, never by hand.

## Ciphertext compatibility

Output is byte-identical to `ubiq_security_fpe`, and that compatibility is a correctness
obligation to downstream users, enforced by `tests/test_interoperability.py` in both directions.
Any change that alters ciphertext for any currently valid input is a major version and needs a
compelling reason — open an issue to discuss before investing in a PR.

## Security

Do not open public issues for security problems. Report privately through
[GitHub private vulnerability reporting](https://github.com/joelee/fpr-ff1/security/advisories/new).
See [`SECURITY.md`](SECURITY.md) for the full policy, including what counts as a security issue
here (incorrect FF1 output and validation that fails open both do).

## Pull requests

- Keep the public API surface small. FF3/FF3-1, key management, and application-specific
  defaults or alphabets are permanently out of scope — see `AGENTS.md`.
- Full type annotations; the package ships `py.typed` and pyright runs in strict mode.
- Update the matching documentation in the same change that makes it true
  (`docs/AGENTS.md` lists which document owns what).
- Add a changelog entry under `[Unreleased]` in `CHANGELOG.md` for user-visible changes.
- New tests belong in the existing suite structure; long-running tests get
  `@pytest.mark.slow`.