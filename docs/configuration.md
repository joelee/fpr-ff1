# Configuration

`fpr-ff1` is a stateless library. It does not load configuration files, environment variables, or secrets. All behavior is determined by the arguments passed to the `FF1` class at construction time.

## `FF1` Constructor Parameters

| Parameter | Type | Required | Description |
|---|---|---|---|
| `key` | `bytes` | Yes | AES key; must be 16, 24, or 32 bytes. |
| `radix` | `int` | Yes | Numeral base, `2 <= radix < 2**16`. |
| `alphabet` | `str \| None` | No | String of exactly `radix` unique characters; enables `encrypt`/`decrypt`. |
| `tweak` | `bytes` | No | Default tweak used when not provided per call. |
| `min_tweak_len` | `int \| None` | No | Inclusive minimum tweak length; at most `2 ** 32 - 1`. |
| `max_tweak_len` | `int \| None` | No | Inclusive maximum tweak length; at most `2 ** 32 - 1`. |
| `backend` | `str` | No | `"python"` (default, the reference) or `"rust"` (the opt-in compiled backend). Both produce identical ciphertext and exceptions; see the README Backends section for when to use each. |

## Runtime Constraints

- Minimum domain: `radix ** minlen >= 1_000_000`
- Maximum length: `2 ** 32 - 1` — SP 800-38G specifies `minlen <= n <= maxlen < 2 ** 32`, so
  `2 ** 32` itself is excluded.
- Maximum tweak length: `2 ** 32 - 1` bytes — Algorithm 7 step 5 encodes the tweak length in the
  four-byte `[t]^4` field of `P`, so a longer tweak cannot be expressed. A default or per-call tweak
  above it raises `TweakLengthError` on both backends before any FF1 computation, and so does a
  `min_tweak_len` or `max_tweak_len` above it at construction (rejected, never clamped). New in
  `2.0.0rc2`; previously the reference raised `OverflowError` and the compiled backend wrapped the
  length.
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

## Distribution and backend availability

`backend="rust"` needs the compiled extension, which ships only in the native wheels: Linux x86_64
and aarch64 (`manylinux_2_34`, glibc 2.34 or newer), macOS x86_64 (10.12 or newer) and arm64 (11 or
newer), and Windows x64, all `abi3` for CPython 3.12 to 3.14. Any other environment — older glibc,
musl, another architecture, a free-threaded interpreter — installs the pure-Python wheel or sdist.
There the default `backend="python"` works unchanged, and `backend="rust"` raises `BackendError`.
The backend choice is never made implicitly, so the same code runs everywhere and fails loudly only
where the compiled backend was explicitly requested but is absent.

## Secrets

The library does not generate, store, derive, or manage keys. Callers are responsible for key material. Python `bytes` are immutable and the interpreter may copy them during garbage collection; the library makes no key-zeroization claims.

## Thread safety

`FF1` instances **are thread-safe**, on both backends. No mutable state is shared between calls — every cipher context is created locally to the call that uses it — so separate calls on one instance may run concurrently and produce exactly the single-threaded results. The compiled backend is stateless by construction (free functions, per-call immutable key schedules, call-local contexts). There is no module-level or global state, so any number of instances may be used concurrently.

Thread-safe is not the same as parallel. The pure-Python backend holds the GIL throughout, so concurrent calls interleave. The compiled backend releases the GIL for the duration of the FF1 computation, so concurrent calls genuinely overlap — measured 2.9× on four threads at n=5,000, against 0.96× for the pure-Python control — and a long call does not stall unrelated threads. `just bench` reproduces both figures.
