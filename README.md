# fpr-ff1

A small, correct Python implementation of **FF1**, the format-preserving encryption mode from NIST SP 800-38G.

This package is intentionally just the algorithm: no accounts, no network, no key management, and no FF3/FF3-1 modes.

## Install

```bash
pip install fpr-ff1
```

## Quick start

```python
from fpr_ff1 import FF1

ff1 = FF1(
    key=b"\x00" * 16,
    radix=10,
    alphabet="0123456789",
    tweak=b"",
)

encrypted = ff1.encrypt("123456")
decrypted = ff1.decrypt(encrypted)
assert decrypted == "123456"
```

## Features

- Pure Python with a single runtime dependency: `cryptography`.
- Conformance-tested against the NIST SP 800-38G sample vectors.
- No floating-point arithmetic in the FF1 core.
- Tightened domain limits from the SP 800-38G Rev. 1 second public draft:
  - radix range `2 <= radix < 2**16`
  - minimum domain `radix ** minlen >= 1_000_000`
  - maximum length `2 ** 32 - 1` (SP 800-38G specifies `maxlen < 2 ** 32`)
  - AES keys of 128, 192, or 256 bits only
- Strongly typed public API with typed exceptions rooted at `FF1Error`.

## Why you can trust this implementation

Format-preserving encryption is unusually easy to get *almost* right. A subtly wrong FF1 still
round-trips perfectly — `decrypt(encrypt(x)) == x` — while producing ciphertext no conformant
implementation can read. By the time anyone notices, the data is written. So conformance here is
not a checkbox; it is the entire product, and it is evidenced rather than asserted.

**The full suite — NIST sample vectors, per-round intermediate-value conformance for every round of every sample, differential tests against an independent implementation, exhaustive bijectivity sweeps, and a malformed-input sweep — runs in CI with 100% line and branch coverage enforced. The build fails below it.**

### Conformance is proven at the round level, not just the output level

All nine published NIST sample vectors pass in both directions. That alone is a weak statement:
nine input/output pairs can be satisfied by two bugs that cancel out.

So this package also asserts the **per-round intermediate values** the NIST sample document
publishes — `P`, `Q`, `R`, `S`, `y`, `m`, `c` and `C`, plus the derived `u`, `v`, `b` and `d` — for
**every round of every sample**, 90 rounds in total. Compensating bugs survive an output test. They
do not survive this one.

The vectors are transcribed from the NIST document and stored as data files. They are never
regenerated from this implementation, which would make them a record of whatever the code does
rather than of what the standard requires.

### Radices without published vectors are proven against an independent implementation

NIST publishes vectors for radix 10 and 36 only. Every other radix has none, so agreement with an
independent implementation is the only correctness evidence available — expected values authored
from this code would test nothing and lock in any bug permanently.

`fpr-ff1` is therefore differential-tested against `ubiq_security_fpe` across radices **2, 10, 16,
32, 36, 62, 256 and 65535**, including every length where the algorithm's internal block structure
changes. The oracle is itself validated against all nine NIST vectors before a single comparison is
trusted.

### Bijectivity is verified exhaustively, not sampled

For two domains small enough to enumerate completely — radix 2 at length 20 (1,048,576 values) and
radix 10 at length 6 (1,000,000 values) — every point is encrypted and the image checked to be the
full domain, with no gaps and no collisions. That is the strongest correctness statement available
for a permutation, and it is run in CI rather than kept as a manual check.

### The known failure modes are tested for by name

Published FF1 bugs cluster in a few places. Each has a dedicated test:

| Known failure mode | How it is prevented |
|---|---|
| Floating-point `ceil(v · log₂(radix))` — the Bouncy Castle bug class | Exact integer arithmetic; an AST scan fails the build if `math.log`, `ceil`, `/` or any float literal appears in the core |
| `b` derived from `u` instead of `v` | Asserted against the traced value, not a round-trip — which passes either way |
| Wrong `S` expansion when `d > 16` | Differential cases at each block-count transition; no NIST sample reaches this branch |
| Mirrored parity rule in decrypt | Encrypt and decrypt share one code path for it |
| Silent coercion of bad input | Every rejection raises a typed exception; a 50-case sweep asserts nothing escapes as a bare `AttributeError` or `KeyError` |

### Migration is safe by construction

Output is byte-identical to `ubiq_security_fpe`, verified in **both** directions — old ciphertext
decrypts with this library, and new ciphertext decrypts with the old one. Existing encrypted data
stays readable, and a rollback strands nothing. See [Migrating](#migrating-from-ubiq_security_fpe).

### What this is *not*

Passing the published sample vectors is **conformance evidence, not FIPS validation**. This package
is not FIPS 140 validated and makes no such claim. It also does not attempt key zeroization, and
offers no constant-time guarantee — see [`SECURITY.md`](https://github.com/joelee/fpr-ff1/blob/main/SECURITY.md) for the full statement of
limitations.

## Why FF1 only — and why FF3 is excluded

SP 800-38G originally specified two modes, FF1 and FF3. FF3 was revised to FF3-1 after an attack
on the original construction, but Beyne subsequently demonstrated a weakness in the **tweak
schedule** that affects FF3 and FF3-1 alike — the repair did not address the underlying problem.

The **February 2025 second public draft of SP 800-38G Rev. 1 removes FF3 entirely**, leaving FF1
as the only approved format-preserving mode.

`fpr-ff1` will therefore never implement FF3 or FF3-1. This is a deliberate feature, not an
omission: there is no configuration flag, no opt-in, and no plan to add one. If you need FF3 you
need a different library, and you should first satisfy yourself that you actually need a mode
NIST has withdrawn.

## Domain limits are stricter than the 2016 text

This package implements SP 800-38G (2016, updated 2019) as the normative algorithm, but enforces
the **tightened constraints from the Rev. 1 second public draft**:

| Constraint | This package | SP 800-38G (2016) |
|---|---|---|
| Minimum domain | `radix ** minlen >= 1_000_000` | `radix ** minlen >= 100` |
| Maximum length | `2 ** 32 - 1` | `2 ** 32 - 1` |
| Key sizes | 128, 192, 256 bits | same |
| Radix | `2 <= radix < 2 ** 16` | same |
| Rounds | exactly 10 | same |

The minimum-domain rule is the one that will bite. A domain of only 100 values is trivially
enumerable, so this package **fails closed** and rejects it. Concretely, `min_length` is 6 for
radix 10 and 4 for radix 36 — inputs shorter than that raise `LengthError`, even though some
older libraries (including `ubiq_security_fpe`) accept them.

Rev. 1 is still a draft. If it is finalised with different limits, that will be a breaking change
and a major version.

## Scope

- **In scope:** FF1 encryption and decryption, numeral and string interfaces, alphabet handling, parameter validation, tests, documentation.
- **Out of scope, permanently:** FF3/FF3-1, identifier generation, persistence, checksums, key generation/storage/derivation, application-specific defaults or alphabets.

## Supported Python versions

**3.12, 3.13 and 3.14.** The upper bound in `requires-python` is deliberate: it matches the
versions actually exercised in CI on Linux, macOS and Windows. It is raised as part of a release
once a newer Python is in the matrix and green, rather than being left open and assumed to work.

## Roadmap

| Version | Focus |
|---|---|
| **1.0** | **Pure Python.** Conformance, a stable API, and a single runtime dependency (`cryptography`). No compiled extension, no optional backends — one code path, and it is the one the vectors test. |
| **2.0** | **Optional accelerated backend.** An opt-in faster path for high-throughput callers, with the pure-Python implementation retained as the reference and the default. |

The 2.0 backend is explicitly *not* a 1.0 concern. An accelerated path is only worth having once
the reference implementation is settled and there is a conformance suite strong enough to prove
the two agree bit for bit — which is the point of the differential and interoperability tests.

Nothing in the roadmap changes the scope boundary above. FF3 and FF3-1 remain permanently out of
scope, and no release will add key management.

## API

### `FF1(key, radix, *, alphabet=None, tweak=b"", min_tweak_len=None, max_tweak_len=None)`

| Parameter | Description |
|---|---|
| `key` | 16, 24, or 32 bytes. |
| `radix` | Integer base of the numeral system. |
| `alphabet` | Optional string of exactly `radix` unique characters; enables `encrypt`/`decrypt`. |
| `tweak` | Default tweak used when not supplied per call. |
| `min_tweak_len` / `max_tweak_len` | Optional per-instance tweak length bounds. |

The package exports `fpr_ff1.__version__` — the version of the installed distribution. Callers
recording which build produced a dataset should capture it alongside their data.

Instances are picklable and deep-copyable (the cipher objects are rebuilt on the far side), so an
`FF1` can be passed to `multiprocessing` workers or broadcast by PySpark. Note that pickling an
instance serialises the key — see [`SECURITY.md`](https://github.com/joelee/fpr-ff1/blob/main/SECURITY.md).

### Numeral interface

The primitive interface works on integers in `[0, radix)`.

```python
ciphertext = ff1.encrypt_numerals([1, 2, 3, 4, 5, 6])
plaintext = ff1.decrypt_numerals(ciphertext)
```

**Accepted numeral types.** Anything losslessly integral — `int`, `IntEnum`, and integers from
other numeric libraries such as NumPy, which are normalised to Python `int` so fixed-width values
cannot overflow in the internal big-integer arithmetic.

`float`, `Decimal`, `Fraction` and `str` are **rejected** with `ValueRangeError`, even when they
compare equal to a valid numeral: `1.0 < 10` is `True`, so comparison alone is not a type check.

`bool` is **rejected deliberately**. `True` would otherwise encrypt silently as `1`, and a list of
booleans arriving here is a caller mistake, not an intent to encrypt ones and zeros.

The input must be a `Sequence` — something with a known length. A generator raises `TypeError`
(not `FF1Error`), because that is misuse of the API rather than bad data; wrap it in `list(...)`.
The `Sequence` contract is enforced: mappings and sets are rejected, and a `Sequence` whose
`__len__` disagrees with the values it yields raises `LengthError` rather than encrypting a
domain smaller than the enforced minimum.

### String interface

When `alphabet` is provided, the string interface maps characters to numerals and back.

```python
ff1.encrypt("123456")
ff1.decrypt("654321")
```

**Alphabet uniqueness is by Unicode code point.** FF1 operates on code points, so normalisation is
the caller's responsibility. Precomposed `é` (U+00E9) and decomposed `é` (U+0065 U+0301) are
visually identical but count as two distinct symbols, and an alphabet containing both is accepted.
If your alphabet comes from user input or an external source, normalise it first:

```python
import unicodedata

alphabet = unicodedata.normalize("NFC", alphabet)
```

### Exceptions

Every rejection raises a typed exception derived from `FF1Error`. Nothing is silently truncated,
padded, coerced or clamped.

| Exception | Raised when |
|---|---|
| `KeyLengthError` | key is not 16, 24 or 32 bytes |
| `RadixError` | radix outside `2 <= radix < 2**16` |
| `LengthError` | input length outside `[min_length, max_length]` |
| `ValueRangeError` | a numeral outside `[0, radix)`, or a character absent from the alphabet |
| `TweakLengthError` | tweak outside the configured bounds |
| `AlphabetError` | alphabet length mismatched to radix, or containing duplicates |

`AlphabetError` signals malformed *configuration* (caught at construction); `ValueRangeError`
signals malformed *data* (caught per call). They are deliberately distinct so callers can handle
a programming error differently from a bad input record.

### Thread safety

`FF1` instances **are thread-safe**. No mutable state is shared between calls — every cipher
context is created locally to the call that uses it — so separate calls on one instance may run
concurrently and produce exactly the single-threaded results. There is no module-level or global
state either, so any number of instances may be used concurrently. A web service may freely share
one `FF1` across request threads.

## Migrating from `ubiq_security_fpe`

`fpr-ff1` exists to replace `ubiq_security_fpe`, which was deprecated in favour of a SaaS client
and is no longer maintained. **The two produce identical ciphertext for identical inputs**, so
existing encrypted data stays readable — no re-encryption, no migration window, no rollback risk.

That claim is enforced by `tests/test_interoperability.py`, which checks both directions (old
ciphertext decrypts with the new library and vice versa) across all three key sizes, tweaked and
untweaked. Migration safety is treated as a correctness obligation, not a promise.

**No compatibility shim ships, deliberately.** A `Context(...)` / `.Encrypt()` drop-in would mean
maintaining a permanent second API, in a naming style this project does not use, mirroring a
library that is itself deprecated. The migration below is three mechanical edits per call site,
and the part that would actually be hard — identical ciphertext — is already done.

### API mapping

```python
# before
from ubiq_security_fpe import ff1

ctx = ff1.Context(key, tweak, twk_min_len, twk_max_len, radix, alphabet)
ciphertext = ctx.Encrypt(plaintext, None)
plaintext = ctx.Decrypt(ciphertext, None)

# after
from fpr_ff1 import FF1

ctx = FF1(
    key, radix, alphabet=alphabet, tweak=tweak, min_tweak_len=twk_min_len, max_tweak_len=twk_max_len
)
ciphertext = ctx.encrypt(plaintext)
plaintext = ctx.decrypt(ciphertext)
```

| `ubiq_security_fpe` | `fpr-ff1` |
|---|---|
| `ff1.Context(key, twk, twk_min_len, twk_max_len, radix, alpha)` | `FF1(key, radix, alphabet=..., tweak=..., min_tweak_len=..., max_tweak_len=...)` |
| `ctx.Encrypt(pt, twk)` | `ctx.encrypt(pt, twk)` |
| `ctx.Decrypt(ct, twk)` | `ctx.decrypt(ct, twk)` |
| — | `ctx.encrypt_numerals(...)` / `ctx.decrypt_numerals(...)` (no alphabet needed) |
| `RuntimeError` for every rejection | typed exceptions under `FF1Error` |

### Behaviour changes to check before you switch

1. **Shorter inputs are rejected.** `fpr-ff1` enforces `radix ** minlen >= 1_000_000`; the legacy
   library used the same rule, but if you relied on any library using the 2016 `>= 100` bound,
   inputs below `ctx.min_length` now raise `LengthError`. Check `ctx.min_length` for your radix.
2. **Errors are typed.** Rejections raise `KeyLengthError`, `RadixError`, `LengthError`,
   `ValueRangeError`, `TweakLengthError` or `AlphabetError` — all subclasses of `FF1Error` —
   rather than bare `RuntimeError`. Catch `FF1Error` if you want the old catch-all behaviour.
3. **No `M2Crypto` dependency.** `fpr-ff1` depends only on `cryptography`.
4. **Alphabet is validated at construction.** A wrong-length alphabet or one with duplicate
   characters raises `AlphabetError` immediately rather than misbehaving later.

## FIPS disclaimer

Passing the published NIST sample vectors is evidence of conformance. It is **not** FIPS validation. This package makes no claims of FIPS 140 conformance.

## Key material

`fpr-ff1` does not attempt to zeroize key material. Python `bytes` are immutable and the interpreter may copy them during garbage collection.

## Development

Requires Python 3.12, `uv`, and `just`.

```bash
just setup    # create venv and install deps
just quality  # format check, lint, typecheck, tests
just build    # quality gate + uv build
just secrets  # gitleaks scan (must be installed locally)
```

## Documentation

- `docs/architecture.md` — design and module overview
- `docs/developer-guide.md` — setup, commands, testing, and CI
- `docs/directory-structure.md` — repository layout
- `docs/configuration.md` — `FF1` constructor parameters and runtime constraints
- `docs/backlog.md` — active and completed work
- `CHANGELOG.md` — release history, including behaviour changes that affect accepted inputs
- `SECURITY.md` — disclosure process and known limitations

## License

MIT
