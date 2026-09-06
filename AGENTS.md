# AGENTS.md

Agent contract for this repository. Read fully before any code change.

## Project

Open-source Python implementation of **FF1**, the format-preserving encryption mode from NIST SP 800-38G. Published as a standalone PyPI library (`fpr-ff1`, live on PyPI with Trusted Publishing configured) — no network, accounts, or key-management features. It replaces `ubiq_security_fpe`, deprecated in favour of a SaaS client and no longer maintained.

The design goal: a reviewer can compare the source against SP 800-38G line by line and find no gaps.

### Scope

- **In scope:** FF1 encrypt/decrypt, parameter validation, numeral and string interfaces, alphabet handling, tests, docs.
- **Out of scope, permanently:** FF3/FF3-1, identifier generation, persistence, checksums, key generation/storage/derivation, application-specific defaults or alphabets.
- A private downstream project consumes this library. **Nothing about that consumer may leak into this package.** Reject radix-32 defaults, fixed 13-numeral lengths, or any caller-specific convenience; a feature that only makes sense for one caller belongs in the caller.

### FF1 only

FF3 and FF3-1 are **not** in scope and must never be added. The February 2025 second public draft of SP 800-38G Rev. 1 removes FF3 entirely, following Beyne's tweak-schedule weakness affecting both FF3 and FF3-1. Being FF1-only is a deliberate feature; the README says so.

## Standards baseline

SP 800-38G (2016, updated 2019) is the normative text, plus the Rev. 1 second public draft's tightened limits:

- Minimum domain: `radix ** minlen >= 1_000_000` — stricter than the 2016 text's `>= 100`; a deliberate fail-closed choice noted in the changelog.
- Maximum length: `maxlen < 2**32`, implemented as `2**32 - 1` (fail closed on the boundary).
- Key sizes: 128, 192, 256 bits only.
- Radix: `2 <= radix < 2**16` — a deliberate supported **subset** of the spec's inclusive `[2..2**16]` (NIST permits subsets). Radix 65536 is excluded; widening the domain without changing existing behaviour is a SemVer minor change, not major.
- Forward AES only; no inverse cipher function.
- Exactly 10 rounds.
- **No floating-point arithmetic anywhere in the FF1 core.**

Rev. 1 is still a draft. Track its status; if it is finalised with different limits, that is a breaking change requiring a major version. The README documents the draft baseline.

## Public API

A single `FF1` class:

```python
class FF1:
    def __init__(
        self,
        key: bytes,  # 16, 24 or 32 bytes
        radix: int,
        *,
        alphabet: str | None = None,  # enables the str interface
        tweak: bytes = b"",  # default tweak
        min_tweak_len: int | None = None,
        max_tweak_len: int | None = None,
    ) -> None: ...

    # numeral interface - the primitive
    def encrypt_numerals(self, x: Sequence[int], tweak: bytes | None = None) -> list[int]: ...
    def decrypt_numerals(self, x: Sequence[int], tweak: bytes | None = None) -> list[int]: ...

    # string interface - requires alphabet
    def encrypt(self, s: str, tweak: bytes | None = None) -> str: ...
    def decrypt(self, s: str, tweak: bytes | None = None) -> str: ...

    @property
    def min_length(self) -> int: ...
    @property
    def max_length(self) -> int: ...
```

Rules:

- `encrypt_numerals` / `decrypt_numerals` are the primitive; `encrypt` / `decrypt` are thin string wrappers. Do not duplicate logic between them.
- String methods without an `alphabet` raise, with a message pointing at the numeral interface.
- Validate `alphabet` length and uniqueness at construction.
- No global or module-level state, no implicit default key, no environment-variable configuration.
- Every rejection raises a typed exception rooted at `FF1Error`; never silently truncate, pad, coerce, or clamp.

## Implementation gotchas

These are the failure modes that produce **plausible but wrong output** — every one still runs without raising.

- `b` is derived from `v`, not `u`. They differ when `n` is odd.
- Bit length is `(radix ** v - 1).bit_length()`. Never `math.log2`, `math.log`, `math.ceil`, `**0.5`, or float literals — this is the Bouncy Castle bug class. Leave a comment saying so, or it will be "simplified" later.
- Padding is `(-t - b - 1) % 16`. Python's modulo already returns the non-negative result; do not rewrite it defensively.
- Encrypt and decrypt differ in exactly three places: `Q` built from `B` vs `A`; round order `0..9` vs `9..0`; final assignment `A, B = B, C` vs `B, A = A, C`. The parity rule `m = u if i % 2 == 0 else v` is **identical in both** — do not mirror it.
- `S` is truncated to `d` bytes, not `d` bits.
- The PRF is CBC-MAC with a zero IV over 16-byte-aligned input.
- Cipher contexts: **never cache any encryptor on the instance** — instances are thread-safe and a live context would be shared mutable state. Create the ECB encryptor locally inside the `d > 16` expansion branch (zero cost when `d <= 16`); the PRF already builds a fresh CBC encryptor per call (it carries chaining state).
- Cite spec steps in internal docstrings, e.g. "SP 800-38G Algorithm 7, step 6.iii".

## Local development

- Python `>=3.12,<3.15` (CI matrix: 3.12, 3.13, 3.14 across Linux, macOS, Windows). Local dev on 3.12. Tools: `uv`, `just`. `src/` layout; ships `py.typed`.
- `just setup` — create `.venv` and install deps.
- `just quality` — format check, lint, typecheck, tests with coverage.
- `just build` — quality gate plus `uv build`.
- `just secrets` — gitleaks scan (must be installed locally).

`pyproject.toml` enforces a **100% line and branch coverage floor** on the FF1 module (`fail_under = 100`, branch coverage on). Every raise path must be exercised by a test; delete unreachable branches rather than leaving dead code.

Documentation is maintained under `docs/`. Update the matching doc file in the same change that makes it true; see `docs/AGENTS.md`.

## Tests

Conformance is the product. A change that makes tests pass by weakening them is a defect.

1. **NIST sample vectors:** all 9 published samples, encrypt and decrypt (AES-128/192/256, radix 10 with/without tweak, radix 36).
2. **Per-round intermediates — the real conformance test:** the NIST document publishes `P`, `Q`, `R`, `S`, `y`, `m`, `c`, `C`, plus derived `u`, `v`, `b`, `d` for every round. Transcribe these and assert round-by-round via a **test-only trace hook** (never exported from the public API). Two compensating bugs can pass an output test; they cannot pass an intermediate test.
3. **Parameter validation:** exercise every rejection path — key lengths 0/15/17/23/25/31/33 bytes; radix 0, 1, `2**16`, negative; lengths below `min_length` (and at `min_length` exactly, which must succeed) and above `max_length`; numerals negative or `>= radix`; tweak bounds; alphabet length mismatch, duplicate characters, non-str; string characters absent from the alphabet; string methods without an alphabet. Verify `min_length` across radices: 2 → 20, 10 → 6, 16 → 5, 32 → 4, 36 → 4, 256 → 3.
4. **Exact-arithmetic regression:** radices where `radix ** v` sits exactly on a power-of-two boundary (2, 4, 8, 16, 32, 64, 256) — precisely where float evaluation flips to the wrong integer. Also static-scan (AST or token) the FF1 module for float ops (`math.log`, `math.log2`, `math.ceil`, `math.pow`, `/`, float literals) and fail CI on violation.
5. **Property-based (Hypothesis):** round-trip; length and alphabet preservation; tweak sensitivity; key sensitivity (a one-bit key change produces unrelated output); determinism.
6. **Bijectivity:** for exhaustively enumerable domains (e.g. radix 2 length 20, radix 10 length 6), confirm the image is the full domain — no gaps, no repeats.
7. **Differential testing:** radix 10 and 36 have NIST vectors; **every other radix has none.** Compare against independent oracles (`ubiq-security-fpe`, Rust `fpe` crate), dev dependencies only, pinned. Never commit self-generated outputs as "vectors" — that tests nothing and locks in bugs permanently. Mark oracle tests optional-but-run-in-CI so a missing oracle does not block local development.
8. **Edge cases:** empty tweak vs absent tweak (must be equivalent); very long tweaks; minimum and maximum practical lengths; odd and even `n` (the `u != v` path); all-zero and all-max numerals; radix 2 and radix `2**16 - 1`.
9. **Interoperability:** a documented test matching `ubiq_security_fpe` output for the same inputs, so migrating users can verify ciphertext portability. A correctness obligation to downstream users, not a nicety.

Vector files live in `tests/vectors/` as JSON, never inline literals. Never regenerate NIST fixtures from this implementation.

## Never do

- Never add FF3 or FF3-1.
- Never add key generation, storage, derivation, or management helpers.
- Never claim FIPS validation; passing published vectors is conformance evidence only. The README states this explicitly.
- Never claim key zeroization; Python bytes are immutable and the GC copies them. Document as a known limitation.
- Never regenerate NIST fixtures from this implementation.
- Never add a runtime dependency beyond `cryptography` without explicit approval.
- Never add application-specific defaults, convenience wrappers, or alphabets shaped to one caller.
- Never let a test assert current behaviour where it should assert specified behaviour.

## Conventions

- Full type annotations; ship `py.typed`. Runtime dependency: `cryptography` only.
- Licence: MIT (decided).
- Semantic versioning; any change to accepted inputs or produced outputs is a major version.
- Migration from `ubiq_security_fpe` is **guide only** (decided 2026-08-21); no compatibility shim ships.
- CI matrix across all supported Python versions on Linux, macOS and Windows. Publish via PyPI Trusted Publishing; do not commit tokens.
- README must cover: what FF1 is, why FF3 is excluded, the Rev. 1 constraints applied, the FIPS disclaimer, and a migration section for `ubiq_security_fpe` users. Include `SECURITY.md` with a disclosure contact.
- Prefer clarity over cleverness. This module is read far more often than written, and a subtle bug is invisible without the vectors.
- When writing to `docs/` or any of its subdirectories, read the `AGENTS.md` in that directory first (`docs/AGENTS.md`, `docs/ideas/AGENTS.md`, `docs/reviews/AGENTS.md`, `docs/plans/AGENTS.md`) and follow its rules and format.

## Open decisions

Ask before deciding:

1. Optional accelerated backend (backlogged for post-1.0): whether to build it at all; if built, opt-in only — the pure-Python implementation stays the reference and the default.