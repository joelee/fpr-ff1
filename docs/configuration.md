# Configuration

`fpr-ff1` is a stateless library. It does not load configuration files, environment variables, or secrets. All behavior is determined by the arguments passed to the `FF1` class at construction time.

## `FF1` Constructor Parameters

| Parameter | Type | Required | Description |
|---|---|---|---|
| `key` | `bytes` | Yes | AES key; must be 16, 24, or 32 bytes. |
| `radix` | `int` | Yes | Numeral base, `2 <= radix < 2**16`. |
| `alphabet` | `str \| None` | No | String of exactly `radix` unique characters; enables `encrypt`/`decrypt`. |
| `tweak` | `bytes` | No | Default tweak used when not provided per call. |
| `min_tweak_len` | `int \| None` | No | Inclusive minimum tweak length. |
| `max_tweak_len` | `int \| None` | No | Inclusive maximum tweak length. |

## Runtime Constraints

- Minimum domain: `radix ** minlen >= 1_000_000`
- Maximum length: `2 ** 32 - 1` — SP 800-38G specifies `minlen <= n <= maxlen < 2 ** 32`, so
  `2 ** 32` itself is excluded.
- Key sizes: 128, 192, 256 bits only
- Forward AES only; no inverse cipher function
- Exactly 10 Feistel rounds
- No floating-point arithmetic in the FF1 core

## Secrets

The library does not generate, store, derive, or manage keys. Callers are responsible for key material. Python `bytes` are immutable and the interpreter may copy them during garbage collection; the library makes no key-zeroization claims.
