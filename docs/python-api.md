# Python API reference

The complete reference for the `fpr_ff1` Python package: the `FF1` constructor, the numeral and
string interfaces, accepted input types, exceptions and thread safety. The
[README](https://github.com/joelee/fpr-ff1/blob/main/README.md) has the quick start;
[`configuration.md`](configuration.md) has the runtime constraints and length properties. The Rust
crate's API is documented on [docs.rs](https://docs.rs/fpr-ff1).

## `FF1(key, radix, *, alphabet=None, tweak=b"", min_tweak_len=None, max_tweak_len=None, backend="python")`

| Parameter | Description |
|---|---|
| `key` | 16, 24, or 32 bytes. |
| `radix` | Integer base of the numeral system. |
| `alphabet` | Optional string of exactly `radix` unique characters; enables `encrypt`/`decrypt`. |
| `tweak` | Default tweak used when not supplied per call. At most `2**32 - 1` bytes, the limit of FF1's four-byte tweak-length field. |
| `min_tweak_len` / `max_tweak_len` | Optional per-instance tweak length bounds, each at most `2**32 - 1`; a larger bound raises `TweakLengthError` rather than being clamped. |
| `backend` | `"python"` (default, the reference) or `"rust"` (the opt-in compiled backend). See the README's [backends section](https://github.com/joelee/fpr-ff1/blob/main/README.md#backends-and-platforms). |

The package exports `fpr_ff1.__version__` — the version of the installed distribution. Callers
recording which build produced a dataset should capture it alongside their data.

Instances are picklable and deep-copyable (the cipher objects are rebuilt on the far side), so an
`FF1` can be passed to `multiprocessing` workers or broadcast by PySpark. Note that pickling an
instance serialises the key — see [`SECURITY.md`](https://github.com/joelee/fpr-ff1/blob/main/SECURITY.md).

## Numeral interface

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

## String interface

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

alphabet = "0123456789abcde\u0301"  # 16 code points, as read from configuration
alphabet = unicodedata.normalize("NFC", alphabet)  # 15: "é" is now one symbol
assert len(alphabet) == 15
```

## Exceptions

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
| `BackendError` | `backend` is not a known name, or is `"rust"` and the compiled extension is not installed |

`AlphabetError` signals malformed *configuration* (caught at construction); `ValueRangeError`
signals malformed *data* (caught per call). They are deliberately distinct so callers can handle
a programming error differently from a bad input record.

## Thread safety

`FF1` instances **are thread-safe**. No mutable state is shared between calls — every cipher
context is created locally to the call that uses it — so separate calls on one instance may run
concurrently and produce exactly the single-threaded results. There is no module-level or global
state either, so any number of instances may be used concurrently. A web service may freely share
one `FF1` across request threads.

Thread-safe is not the same as parallel. The pure-Python backend holds the GIL throughout, so
concurrent calls interleave rather than overlap. The compiled backend releases the GIL for the
duration of the FF1 computation, so concurrent calls on one instance genuinely run in parallel —
measured 2.17× on four threads (n = 5,000, radix 10) against 0.86× for the pure-Python control
(`just bench`, 2026-09-27).
Releasing the GIL also means a long call no longer stalls unrelated threads in the process.
Reproduce both rows with `just bench`.

