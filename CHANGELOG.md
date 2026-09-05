# Changelog

All notable changes to this project are documented here.

The format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).
This project uses [Semantic Versioning](https://semver.org/spec/v2.0.0.html); per the project
contract, **newly rejecting inputs or changing produced outputs is a major version**, while
expanding the accepted domain without changing existing behaviour is a minor version.

## [Unreleased]

## [1.0.0] — 2026-09-04

First stable release, resolving every pre-1.0 finding from reviews 00003 and 00004.
**Ciphertext is unchanged for every input that was valid in 0.1.1** — verified against the NIST
sample vectors, the per-round intermediates, the differential oracle, and the exhaustive
bijectivity sweeps. The input-domain and error-message changes below are why this is a major
version.

### Security

- **Minimum-domain validation bypass closed** (review 00004, MAJ-01). The numeral interfaces
  previously trusted the input's declared `__len__`, so a malformed `Sequence` could encrypt a
  domain below the enforced `radix ** minlen >= 1_000_000` minimum. Inputs must now be true
  `collections.abc.Sequence`s: `dict` and `set` inputs, and `Sequence`s whose `__len__`
  disagrees with the values they yield, are rejected with a typed error. **This changes accepted
  inputs.**
- **Exception messages no longer echo plaintext** (review 00003 B3 / review 00004 MAJ-03).
  Rejected numerals and characters are located by index and failure kind only; the offending
  value never appears in the message, so a malformed record cannot leak into application logs.
- **`cryptography` floor raised to `>=50.0.0`** (review 00004, MAJ-02). The previous `>=44.0.0`
  floor admitted releases affected by PYSEC-2026-3552 (GHSA-g6cj-pr64-35w5, fixed in 50.0.0).

### Changed

- **`FF1` instances are now thread-safe** (review 00003 H2 / review 00004 MED-01). The cached
  ECB encryptor — the shared mutable state behind the 0.1.1 "not thread-safe" caveat — is gone;
  every cipher context is created locally to the call that uses it. Separate calls on one
  instance may run concurrently and produce exactly the single-threaded results. The caveat is
  replaced by a guarantee.
- Tweak validation now runs before the input is walked (review 00003 L5), so a bad tweak on a
  large input rejects in O(1) rather than after the full coercion pass.
- `requires-python` is `>=3.12` with no upper bound (review 00003 B4). A capped `requires-python`
  becomes a hard resolution failure on future interpreters; the versions actually exercised in
  CI (3.12, 3.13, 3.14) are stated by the classifiers.
- The ruff dev floor is `>=0.16`; the formatter now also formats Markdown code blocks (the
  README and AGENTS.md were reformatted accordingly).
- The 100% line-and-branch coverage gate moved out of pytest `addopts` into `just coverage` and
  CI's explicit flags (review 00003 M4), so a bare `pytest` from the unpacked sdist no longer
  fails for downstream packagers who have not installed `pytest-cov`. The floor itself is
  unchanged and still enforced on every CI test execution.
- The sdist contents are pinned explicitly to code, tests, vectors, and user-facing docs; it
  previously shipped agent instructions, planning documents, and editor state.
- **Version policy revised** (review 00004 MED-05): expanding the accepted domain without
  changing existing behaviour — for example a future radix-65536 addition — is a **minor**
  change; newly rejecting inputs or changing ciphertext remains major.

### Added

- **Pickling and deepcopy support.** `FF1` instances survive `pickle`, `copy.deepcopy`, and
  spawn-context `multiprocessing`, so an instance can be passed to workers or broadcast by
  PySpark. The cipher objects are rebuilt on load; pickling an instance serialises the key, which
  SECURITY.md documents as a caller decision.
- `fpr_ff1.__version__` via `importlib.metadata`, exported in `__all__` (review 00003 B2).
- **Frozen oracle-derived KAT vectors** (`tests/vectors/oracle_kat_frozen.json`, with a
  provenance header): the differential evidence for radices without NIST vectors now survives
  `ubiq-security-fpe` — deprecated and unmaintained — ever becoming uninstallable. The live
  differential suite remains primary while the oracle installs (review 00003 H6).
- `benchmarks/timing.py` and `just bench`: the SECURITY.md timing measurements and the new README
  performance section are reproducible on any machine (review 00003 M9/M10).
- Supply-chain hardening (reviews 00003 H4/H5, 00004 MED-02/MED-03): every GitHub Action pinned
  to a full commit SHA, the gitleaks tarball checksum-verified before installation, a
  dependency-audit CI job (`pip-audit` against the lock and the declared minimum), Dependabot,
  `uv sync --locked` in CI, and a publish workflow that downloads and publishes the exact
  artifact the release gate built — with a release-tag-versus-project-version guard.
- CI installs the built wheel into a clean environment and exercises the public surface from it,
  and asserts the sdist contents against a forbidden-path list (review 00003 M3).
- Community files (review 00003 M7/M8): `CONTRIBUTING.md` (vector-provenance rules, quality
  gate, ciphertext-compatibility rules), `CODE_OF_CONDUCT.md`, issue and PR templates, README
  badges, and a `Documentation` project URL.
- README: a "Security notes" section (determinism, confidentiality-only, wrong-key behaviour,
  small-domain guidance), calibrated conformance language, the radix range documented as a
  deliberate supported subset of the spec's inclusive `[2..2**16]`, and a performance section
  (reviews 00004 MED-04/MED-05/MED-06, 00003 L6/M10).
- Pre-commit hooks (`.pre-commit-config.yaml`) wiring ruff, ruff-format, and the pinned gitleaks
  (review 00003 M2).

## [0.1.1] — 2026-09-03

Documentation and repository-hygiene release, resolving the findings of the post-release review.
**No changes to accepted inputs or produced outputs.**

### Fixed

- Restored the changelog for 0.1.0, which was accidentally dropped when the repository history
  was consolidated before the release; the release notes carried the substance but the
  contract-mandated Rev. 1 minimum-domain note belongs here.
- `docs/backlog.md` recorded two now-completed items ("Run CI for the first time", "Claim the
  `fpr-ff1` name on PyPI") as open and one superseded decision ("0.1.0 was never published");
  all three are corrected.
- The README's trust section hardcoded a test count ("708 tests") that drifted as soon as the
  suite grew; it now describes the suite's composition, which is the actual claim.
- The README linked `SECURITY.md` relatively, which 404s from the PyPI project page (PyPI does
  not rewrite relative links); the link is now absolute.
- `docs/directory-structure.md` was missing six test modules, the `_oracle/` M2Crypto shim, the
  workflow files and the changelog/security documents; the tree is regenerated to match the
  repository.

### Added

- **Thread-safety contract, documented.** `FF1` instances are not thread-safe: the instance
  caches a single ECB encryptor for the S-expansion step, and pyca/cryptography documents
  concurrent `update()` calls on a shared `CipherContext` as producing indeterminate results.
  Create one instance per thread or serialise access. There is no global state, so separate
  instances may be used concurrently. Documented in the class docstring, the README, and
  `docs/configuration.md`.
- `SECURITY.md` now names GitHub private vulnerability reporting as the sole disclosure
  channel. The email channel was removed pending a published PGP key; it may return once
  hardened.
- The `justfile` mirrors CI's pinned gitleaks version (`8.30.1`) and `just secrets` warns when a
  locally installed scanner differs from the authoritative CI pin.

## [0.1.0] — 2026-09-03

First published release.

### Fixed

- **FF1 produced no output at all for a large part of its declared domain.** The SP 800-38G
  Algorithm 7 step 6.iii `S`-expansion was implemented as `PRF(R || [j]^4)` instead of the
  specified `CIPH_K(R XOR [j]^16)` — a single forward-cipher block. Because the incorrect input
  was not block-aligned, any input reaching `d > 16` raised
  `ValueError: The length of the provided data is not a multiple of the block length` rather than
  encrypting. Affected every input at or above: **radix 10 → 57 numerals**, radix 36 → 37,
  radix 62 → 33, radix 256 → 25, radix 65535 → 13, radix 2 → 193.

  No NIST sample vector reaches `d > 16` (the maximum published `d` is 12), so the branch was
  never exercised by the conformance suite. It is now covered by differential tests against an
  independent implementation, including cases with one and two expansion blocks.

  **This changes accepted inputs.** No stored data is affected: the affected inputs previously
  raised rather than producing wrong ciphertext, so nothing was ever encrypted incorrectly and
  nothing became undecryptable. Inputs that previously failed now succeed.

- Characters absent from the configured alphabet raised a bare `KeyError` from the string
  interface. They now raise `ValueRangeError` (a subclass of `FF1Error`) identifying the
  offending character and its index, so every rejection comes from the documented hierarchy.

- Over-long input is now rejected before being materialised, so passing a huge sequence raises
  `LengthError` without first allocating a copy of it.

- **Every rejection now comes from the documented hierarchy.** Values that are not integers passed
  validation on comparison alone (`1.0 < 10` is `True`) and crashed later with `AttributeError` or
  `TypeError`. Numerals, `radix`, `tweak`, `key`, `alphabet` and the string interface are all type
  checked now; the numeral gate uses `operator.index()`, so `int`, `IntEnum` and NumPy integers are
  accepted while `float`, `Decimal`, `Fraction` and `str` raise `ValueRangeError`. A generator still
  raises `TypeError`, deliberately — that is API misuse against a `Sequence[int]` annotation, not
  bad data — but the message now says so.

- **`bool` numerals are rejected.** `True`/`False` previously encrypted silently as `1`/`0`, the
  coercion the contract forbids.

- **A `list` alphabet was accepted and worked.** It now raises `AlphabetError`. This was the only
  case that never surfaced an error at all.

- **A `bytearray` key or tweak is now copied at construction.** Previously the instance tracked the
  caller's buffer, so mutating it afterwards silently changed subsequent ciphertext.

- Tweak bound configuration is validated at construction: negative bounds were silently inert and
  now raise, and mutually unsatisfiable bounds (`min_tweak_len > max_tweak_len`) report the
  configuration rather than naming whichever bound the default tweak happened to violate first.

- Corrected the SP 800-38G step citations in the FF1 core. `P` was labelled step 6.i (it is step
  5), steps 2 and 3 were transposed, and the `Q`, `R` and `S` citations were each off by one.
  The package's stated goal is that a reviewer can compare the source against the standard line
  by line; misnumbered citations worked against that.

### Changed

- **`max_length` is now `2**32 - 1`, was `2**32`.** SP 800-38G specifies
  `minlen <= n <= maxlen < 2**32`, so a length of exactly `2**32` was one past the bound. This
  changes accepted inputs and is therefore breaking, but no real caller is affected: a
  `2**32`-element sequence cannot be materialised on any ordinary machine. The package fails
  closed on the boundary, consistent with its stance on the minimum domain.
- `requires-python` is now `>=3.12,<3.15`, was `>=3.12,<3.13`. The old cap was unintended and
  blocked 3.13 entirely; the new one matches the tested CI matrix (3.12, 3.13, 3.14) and is
  raised at release time as new versions go green, rather than being left open and assumed.
- Added PyPI classifiers, keywords, and Changelog/Security project URLs.
- `_trace` is no longer a parameter on the public `encrypt_numerals` / `decrypt_numerals`. The
  per-round conformance hook is now the private `FF1._encrypt_traced`, keeping the public
  signatures exactly as documented. This hook is test-only and not part of the supported API.
- `P` is now built once per call rather than rebuilt on each of the ten rounds, and the PRF reuses
  cached AES/CBC configuration objects. Roughly 1.3x faster; output is unchanged. A CBC
  *encryptor* is still created fresh per call and never cached, so no chaining state persists.

### Added

- Differential tests against `ubiq_security_fpe` covering radices 2, 10, 16, 32, 36, 62, 256 and
  65535. Radices other than 10 and 36 have no published NIST vectors, so agreement with an
  independent implementation is the only correctness evidence available for them.
- Interoperability tests demonstrating bidirectional ciphertext compatibility with
  `ubiq_security_fpe`, so migrating users can verify no data becomes undecryptable.
- Property-based tests now span the full legal radix range (2 … 65535) and lengths up to 26,
  rather than radix 2–10 and length 12. This reaches `d > 16` and independently catches the
  S-expansion defect above without needing the optional oracle.
- `SECURITY.md` with a disclosure contact and a statement of known limitations.
- CI across Python 3.12/3.13/3.14 on Linux, macOS and Windows, with a 100% line and branch
  coverage gate and PyPI Trusted Publishing.

### Notes for users of other FF1 libraries

This package enforces the **SP 800-38G Rev. 1 second public draft** minimum domain,
`radix ** minlen >= 1_000_000`, rather than the 2016 text's `>= 100`. A domain of 100 values is
trivially enumerable, so this package fails closed.

**This rejects inputs that older libraries accept.** `min_length` is 6 for radix 10, 5 for radix
16, 4 for radix 36 and 3 for radix 256; shorter inputs raise `LengthError`. Check
`FF1.min_length` for your radix before migrating.

Rev. 1 remains a draft. If it is finalised with different limits, that will be a breaking change
requiring a major version.

<!-- Keep a Changelog link reference definitions (review 00003 B7): without
     these, the bracketed version headings render as literal brackets. -->
[Unreleased]: https://github.com/joelee/fpr-ff1/compare/v1.0.0...HEAD
[1.0.0]: https://github.com/joelee/fpr-ff1/compare/v0.1.1...v1.0.0
[0.1.1]: https://github.com/joelee/fpr-ff1/compare/v0.1.0...v0.1.1
[0.1.0]: https://github.com/joelee/fpr-ff1/releases/tag/v0.1.0