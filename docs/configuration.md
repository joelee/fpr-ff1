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
- Radix: `2 <= radix < 2**16` — a deliberate supported subset of the spec's inclusive
  `[2..2**16]` (NIST permits subsets); radix 65536 is excluded.
- Forward AES only; no inverse cipher function
- Exactly 10 Feistel rounds
- No floating-point arithmetic in the FF1 core

## Length Properties

The effective input-length domain is exposed per instance:

- `FF1.min_length` — the smallest `n` with `radix ** n >= 1_000_000` (e.g. 6 for radix 10, 4 for
  radix 36, 3 for radix 256, 20 for radix 2). Inputs shorter than this raise `LengthError`.
- `FF1.max_length` — always `2 ** 32 - 1`, the SP 800-38G upper bound. Inputs longer raise
  `LengthError`.

Check `min_length` before migrating data from a library using the 2016 `>= 100` bound.

## Secrets

The library does not generate, store, derive, or manage keys. Callers are responsible for key material. Python `bytes` are immutable and the interpreter may copy them during garbage collection; the library makes no key-zeroization claims.

## Thread safety

`FF1` instances **are thread-safe**. No mutable state is shared between calls — every cipher context is created locally to the call that uses it — so separate calls on one instance may run concurrently and produce exactly the single-threaded results. There is no module-level or global state, so any number of instances may be used concurrently.
