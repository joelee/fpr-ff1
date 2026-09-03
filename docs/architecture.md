# Architecture

`fpr-ff1` is a small, single-purpose library: an implementation of the FF1 format-preserving encryption mode from NIST SP 800-38G.

## System Context

```mermaid
flowchart LR
    Caller["Caller code"] --> FF1["fpr_ff1.FF1"]
    FF1 --> AES["cryptography AES/CBC PRF"]
```

## Design Principles

- **FF1 only.** FF3 and FF3-1 are permanently out of scope.
- **No floating-point arithmetic in the core.** Bit lengths and rounding use integer operations only.
- **Single runtime dependency.** The package depends only on `cryptography`.
- **Small public API.** One class, two primitive interfaces, two string wrappers, and a typed exception hierarchy.
- **Conformance is the product.** Correctness is established against published NIST sample vectors, per-round intermediates, and independent oracles — never against self-generated outputs.

## Modules

- `fpr_ff1._ff1`: `FF1` class and the Algorithm 7 core.
- `fpr_ff1._exceptions`: typed exceptions rooted at `FF1Error`.
- `fpr_ff1.__init__`: public exports and `py.typed` marker.

## Public API

```python
from fpr_ff1 import FF1

ff1 = FF1(
    key=b"\x00" * 16,
    radix=10,
    alphabet="0123456789",
    tweak=b"",
)

encrypted = ff1.encrypt("123456789012")
decrypted = ff1.decrypt(encrypted)
```

The primitive numeral interface (`encrypt_numerals` / `decrypt_numerals`) is the underlying implementation. The string interface (`encrypt` / `decrypt`) is a thin wrapper that maps alphabet characters to numerals and back.

## Boundaries

- Parameter validation happens in `FF1.__init__` and per-call methods.
- All rejections raise typed exceptions derived from `FF1Error`.
- The package does not generate, store, derive, or manage keys.
- The package does not persist data or provide application-specific alphabets.

## Key Implementation Details

- `b` is derived from `v`, not `u`.
- Bit length uses `(radix ** v - 1).bit_length()`, never `math.log2`.
- Padding is `(-(t + b + 1)) % 16`.
- The PRF is CBC-MAC with a zero IV over 16-byte-aligned input.
- `S` is truncated to `d` bytes.
- Encrypt and decrypt differ only in `Q` source, round order, and the final assignment.
