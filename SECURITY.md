# Security Policy

## Reporting a vulnerability

**Please do not open a public issue for security problems.**

Report privately through **GitHub private vulnerability reporting** —
[open a draft advisory](https://github.com/joelee/fpr-ff1/security/advisories/new).

An email disclosure channel may be added once it has a published PGP key; until then, GitHub
private reporting is the only accepted channel.

Please include the version, the radix, key size and input length involved, and a reproducer if
you have one. A correctness bug that produces wrong ciphertext counts as a security issue here:
non-conformant output can render data undecryptable by a conformant implementation.

You can expect an acknowledgement within 7 days and an assessment within 30. If a fix is
warranted, disclosure will be coordinated with you.

## Supported versions

The latest `1.x` release receives fixes. A minor release is supported until the next minor ships;
security fixes are backported to the most recent minor where practical.

| Version | Supported |
|---|---|
| 1.0.x | ✅ |
| 0.1.x | ✅ (until 1.0.0 ships, per the pre-1.0 policy) |

## Scope

In scope:

- Incorrect FF1 output — any deviation from NIST SP 800-38G Algorithm 7 or 8.
- Validation that fails open: accepting a key size, radix, length, tweak or alphabet the
  documented constraints say must be rejected.
- Anything that causes plaintext or key material to be logged, raised in a message, or otherwise
  exposed.

Out of scope:

- **Key management.** This package does not generate, store, derive or rotate keys, by design.
- **Key zeroization.** See the limitation below.
- Weaknesses inherent to FF1 itself, or to small domains. FF1 with a small domain is inherently
  vulnerable to enumeration; that is a property of format-preserving encryption, not a bug here.
  This is why the package enforces `radix ** minlen >= 1_000_000`.
- FF3 / FF3-1. Not implemented, and never will be — see the README.

## Known limitations

**Pickling an instance serialises the key.** `FF1` instances support `pickle` and `copy.deepcopy` (rebuilt on the far side from the serialised key), so they can be passed to `multiprocessing` workers or broadcast by PySpark. That convenience has an inherent consequence: the AES key crosses the pickle boundary and may land in a temp file, a socket, or worker memory. Pickling an instance is the caller's decision to expose key material through that channel; if your threat model does not allow it, construct a fresh instance per process from your secret store instead.

**Key material is not zeroized.** Python `bytes` are immutable and the garbage collector may copy
them, so a key cannot be reliably erased from process memory. This package makes no attempt to do
so and no claim that it does. If your threat model includes memory disclosure, keep key material
outside the Python heap.

**No FIPS validation.** Passing the published NIST sample vectors is conformance evidence, not
validation. This package is not FIPS 140 validated and makes no such claim.

**Timing is not constant, and cannot be in pure Python.** Two distinct effects:

1. **Value-dependent — small.** FF1 converts each half of the input to an arbitrary-precision
   integer and does modular arithmetic on it. CPython's big-integer routines take time proportional
   to the limbs actually in use, so a small numeric value is marginally faster than a large one at
   the same length. Measured on CPython 3.12 (median of 25 batches, all-zero vs all-max plaintext):

   | radix | length | delta |
   |---|---|---|
   | 10 | 10 | +0.8% |
   | 10 | 60 | +2.6% |
   | 10 | 200 | +2.6% |
   | 256 | 32 | +1.9% |
   | 65535 | 12 | +0.6% |

   This is at or near the noise floor for a pure-Python implementation. It is reported as measured
   rather than estimated, and it is not a guarantee — treat it as an observation about one
   interpreter on one machine.

2. **Length-dependent — larger, but public.** The step 6.iii `S`-expansion loop runs
   `ceil(d / 16) - 1` extra AES blocks, where `d` derives from the radix and input length. At radix
   10 that is 0 extra blocks up to length 56, 1 from length 57, and 2 from length 135, which shows
   up plainly in wall-clock time. It varies with the *length* of the input — which a
   format-preserving cipher reveals by definition — so it leaks nothing an observer did not already
   have.

Neither is a practical side channel for a pure-Python library: interpreter dispatch, allocation and
garbage collection all produce far more timing noise than the arithmetic does. But no constant-time
guarantee is offered, and if your threat model includes a local timing adversary, this is not the
right implementation for you.
