"""Reproducible timing and throughput harness (review 00003 M9).

Run manually via `just bench`; never imported by the test suite.

SECURITY.md publishes a value-dependent timing table (all-zero vs all-max
plaintext, median of batches) as a falsifiable empirical claim, and the
README publishes a throughput baseline to size batch jobs against and to
justify the 2.0 accelerated-backend roadmap.  This harness is how those
numbers are produced and reproduced: re-run it on your interpreter and
hardware instead of trusting one machine's measurements.

Methodology matches SECURITY.md: median of 25 batches, all-zero vs all-max
plaintext at the same length, delta as a percentage of the all-zero time.
The batch size adapts to the per-call cost so every measurement takes a
similar wall-clock time regardless of input length.
"""

from __future__ import annotations

import statistics
import time
from collections.abc import Callable

from fpr_ff1 import FF1

_KEY = bytes(range(16))

#: The (radix, length) cases behind the SECURITY.md value-dependent table.
_VALUE_CASES = [
    (10, 10),
    (10, 60),
    (10, 200),
    (256, 32),
    (2**16 - 1, 12),
]

#: Throughput/per-numeral cases from the README performance table.
_LENGTH_CASES = [100, 1_000, 5_000, 20_000]

_BATCHES = 25
_BATCH_SECONDS = 0.1
_MAX_INNER = 500


def _median_seconds_per_call(fn: Callable[[], object]) -> float:
    """Median seconds per call, from 25 timed batches of adaptive size."""
    # Warm up and estimate the per-call cost so the batch size can adapt.
    start = time.perf_counter()
    fn()
    fn()
    estimate = max((time.perf_counter() - start) / 2, 1e-9)
    inner = max(1, min(_MAX_INNER, int(_BATCH_SECONDS / estimate)))

    samples: list[float] = []
    for _ in range(_BATCHES):
        start = time.perf_counter()
        for _ in range(inner):
            fn()
        samples.append((time.perf_counter() - start) / inner)
    return statistics.median(samples)


def _timed_encrypt(ff1: FF1, plaintext: list[int]) -> float:
    """Median seconds per encrypt_numerals call on a fixed input."""
    return _median_seconds_per_call(lambda: ff1.encrypt_numerals(plaintext))


def value_dependent_table() -> None:
    """Reproduce the SECURITY.md table: all-zero vs all-max timing delta."""
    print("## Value-dependent timing (all-zero vs all-max, median of 25 batches)\n")
    print("| radix | length | delta |")
    print("|---|---|---|")
    for radix, n in _VALUE_CASES:
        ff1 = FF1(key=_KEY, radix=radix)
        t_zero = _timed_encrypt(ff1, [0] * n)
        t_max = _timed_encrypt(ff1, [radix - 1] * n)
        delta = (t_max - t_zero) / t_zero * 100
        print(f"| {radix} | {n} | {delta:+.1f}% |")


def throughput_table() -> None:
    """The README performance table: small-input ops/s, construction, per-numeral cost."""
    print("\n## Throughput\n")
    print("| Input | Throughput | Per numeral |")
    print("|---|---|---|")

    ff1 = FF1(key=_KEY, radix=10)
    t_short = _timed_encrypt(ff1, [1, 2, 3, 4, 5, 6])
    print(f"| 6 numerals, radix 10 | ~{1 / t_short:,.0f} ops/s | {t_short * 1e6:.1f} µs/op |")

    t_construct = _median_seconds_per_call(lambda: FF1(key=_KEY, radix=10))
    print(f"| Instance construction | ~{1 / t_construct:,.0f} /s | {t_construct * 1e6:.1f} µs |")

    for n in _LENGTH_CASES:
        plaintext = [i % 10 for i in range(n)]
        t = _timed_encrypt(ff1, plaintext)
        print(f"| n = {n:,}, radix 10 | — | {t / n * 1e6:.1f} µs |")


def main() -> None:
    print(f"# fpr-ff1 timing harness ({time.strftime('%Y-%m-%d %H:%M %Z')})\n")
    print(f"Batches per measurement: {_BATCHES} (adaptive inner batch size)\n")
    value_dependent_table()
    throughput_table()


if __name__ == "__main__":
    main()
