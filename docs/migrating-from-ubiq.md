# Migrating from `ubiq_security_fpe`

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

## API mapping

```python
# before
from ubiq_security_fpe import ff1

ctx = ff1.Context(key, tweak, twk_min_len, twk_max_len, radix, alphabet)
ciphertext = ctx.Encrypt(plaintext, None)
plaintext = ctx.Decrypt(ciphertext, None)

# after
from fpr_ff1 import FF1

ctx = FF1(
    key,
    radix,
    alphabet=alphabet,
    tweak=tweak,
    min_tweak_len=twk_min_len,
    # `twk_max_len=0` meant "no maximum" in the legacy library; here that is
    # `None`. A positive bound copies across unchanged. See note 5 below.
    max_tweak_len=twk_max_len or None,
)
ciphertext = ctx.encrypt(plaintext)
plaintext = ctx.decrypt(ciphertext)
```

| `ubiq_security_fpe` | `fpr-ff1` |
|---|---|
| `ff1.Context(key, twk, twk_min_len, twk_max_len, radix, alpha)` | `FF1(key, radix, alphabet=..., tweak=..., min_tweak_len=..., max_tweak_len=...)` |
| `twk_max_len=0` (means *no maximum*) | `max_tweak_len=None` — **not** `0`, which means *empty tweaks only* |
| `ctx.Encrypt(pt, twk)` | `ctx.encrypt(pt, twk)` |
| `ctx.Decrypt(ct, twk)` | `ctx.decrypt(ct, twk)` |
| — | `ctx.encrypt_numerals(...)` / `ctx.decrypt_numerals(...)` (no alphabet needed) |
| `RuntimeError` for every rejection | typed exceptions under `FF1Error` |

## Behaviour changes to check before you switch

1. **Shorter inputs are rejected.** `fpr-ff1` enforces the Rev. 1 draft's `radix ** minlen >=
   1_000_000`; `ubiq_security_fpe` enforced the same rule, so ciphertext produced by the legacy
   library decrypts unchanged. But if your data contains values that only ever passed under the
   2016 text's weaker `>= 100` bound — through another library or a manual path — those inputs
   now raise `LengthError`. Before switching, check your shortest values against
   `ctx.min_length` for your radix (6 for radix 10, 4 for radix 36, 3 for radix 256).
2. **Errors are typed.** Rejections raise `KeyLengthError`, `RadixError`, `LengthError`,
   `ValueRangeError`, `TweakLengthError` or `AlphabetError` — all subclasses of `FF1Error` —
   rather than bare `RuntimeError`. Catch `FF1Error` if you want the old catch-all behaviour.
3. **No `M2Crypto` dependency.** `fpr-ff1` depends only on `cryptography`.
4. **Alphabet is validated at construction.** A wrong-length alphabet or one with duplicate
   characters raises `AlphabetError` immediately rather than misbehaving later.
5. **A zero maximum tweak length means the opposite of what it did.** `ubiq_security_fpe`
   applied `twk_max_len` only when it was positive, so `0` meant "no maximum" — and `(0, 0)` was
   the usual way to say "any tweak". In `fpr-ff1` the bounds are literal: `max_tweak_len=0`
   accepts only an empty tweak, and `None` means unbounded. Translate a legacy `0` to `None`, as
   the recipe above does; copy positive bounds unchanged. Copying a literal `0` makes the
   constructor raise `TweakLengthError` for any non-empty tweak.

