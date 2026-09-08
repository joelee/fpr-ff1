# Architecture

`fpr-ff1` is a small, single-purpose library: an implementation of the FF1 format-preserving encryption mode from NIST SP 800-38G.

## System Context

```mermaid
flowchart LR
    Caller["Caller code"] --> FF1["fpr_ff1.FF1"]
    FF1 -->|backend=python (default)| Py["_ff1 pure-Python core"]
    FF1 -->|backend=rust| Rs["fpr_ff1._rs compiled core"]
    Py --> AES["cryptography AES/CBC PRF"]
    Rs --> RustAES["RustCrypto aes PRF"]
```

## Design Principles

- **FF1 only.** FF3 and FF3-1 are permanently out of scope.
- **No floating-point arithmetic in the core.** Bit lengths and rounding use integer operations only, in both the Python and Rust cores.
- **Single runtime dependency.** The pure-Python path depends only on `cryptography`; the compiled backend is part of this package, not a new PyPI dependency.
- **Small public API.** One class, two primitive interfaces, two string wrappers, and a typed exception hierarchy.
- **Conformance is the product.** Correctness is established against published NIST sample vectors, per-round intermediates, and independent oracles — never against self-generated outputs. The conformance suite runs against *both* backends.

## Modules

- `fpr_ff1._ff1`: `FF1` class and the Algorithm 7 core (the reference implementation).
- `fpr_ff1._exceptions`: typed exceptions rooted at `FF1Error`.
- `fpr_ff1.__init__`: public exports and `py.typed` marker.
- `fpr_ff1._rs`: the optional compiled backend (a PyO3 extension built from `rust/fpr-ff1-rust`), present only in the platform wheels. The pure-Python path never imports it; `backend="rust"` without it raises `BackendError`.

## Public API

```python
from fpr_ff1 import FF1

ff1 = FF1(
    key=b"\x00" * 16,
    radix=10,
    alphabet="0123456789",
    tweak=b"",
    backend="python",  # or "rust" for the opt-in compiled backend
)

encrypted = ff1.encrypt("123456789012")
decrypted = ff1.decrypt(encrypted)
```

The primitive numeral interface (`encrypt_numerals` / `decrypt_numerals`) is the underlying implementation. The string interface (`encrypt` / `decrypt`) is a thin wrapper that maps alphabet characters to numerals and back.

## Boundaries

- Parameter validation happens in `FF1.__init__` and per-call methods, in Python, for **both** backends — so exception types and messages are identical regardless of `backend`.
- All rejections raise typed exceptions derived from `FF1Error`.
- The package does not generate, store, derive, or manage keys.
- The package does not persist data or provide application-specific alphabets.
- The compiled backend is stateless: free functions, per-call immutable key schedules, call-local cipher contexts — no shared mutable state, so instances are thread-safe by construction on both backends.
- The compiled backend releases the GIL for the duration of the FF1 computation (`Python::detach`), so concurrent calls on one instance run in parallel rather than merely interleaving, and a long call does not stall unrelated threads. The pure-Python backend is GIL-bound.

## Key Implementation Details

- `b` is derived from `v`, not `u`.
- Bit length uses `(radix ** v - 1).bit_length()`, never `math.log2`.
- Padding is `(-(t + b + 1)) % 16`.
- The PRF is CBC-MAC with a zero IV over 16-byte-aligned input.
- `S` is truncated to `d` bytes.
- Encrypt and decrypt differ only in `Q` source, round order, and the final assignment.
