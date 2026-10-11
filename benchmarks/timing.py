"""Reproducible timing and throughput harness (review 00003 M9).

Run manually via `just bench`; never imported by the test suite.

SECURITY.md publishes a value-dependent timing table (all-zero vs all-max
plaintext, median of batches) as a falsifiable empirical claim, and the
README publishes the backend comparison.  The throughput table sizes batch
jobs and the GIL probe backs the thread-parallelism figure in the docs.  This
harness is how those numbers are produced and reproduced: re-run it on your
interpreter and hardware instead of trusting one machine's measurements.

Methodology matches SECURITY.md: median of 25 batches, all-zero vs all-max
plaintext at the same length, delta as a percentage of the all-zero time.
The batch size adapts to the per-call cost so every measurement takes a
similar wall-clock time regardless of input length.  The value table runs an
untimed warm-up first and times every pair in both orders, reporting the mean
of the two deltas, so no case gains from its position (plan 00011 STEP-03).
"""

from __future__ import annotations

import importlib
import statistics
import threading
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

#: Throughput/per-numeral cases, for sizing batch jobs.
_LENGTH_CASES = [100, 1_000, 5_000, 20_000]

#: Backend-comparison cases behind the README performance table. Two radices,
#: because the conversion work that dominates long inputs scales with the
#: numeral count *and* the radix, and power-of-two radices take a faster path.
_BACKEND_CASES = [
    (10, (6, 100, 1_000, 5_000, 20_000)),
    (256, (100, 1_000, 5_000, 20_000)),
]

_BATCHES = 25
#: Untimed warm-up before the value table's first measurement (plan 00011
#: STEP-03).  The cheapest case hits the batch cap, so its whole measurement
#: lasts well under a second, and when it ran first it absorbed the
#: interpreter and CPU start-up transient: one run published -28.6% for
#: radix 10, length 10, where the same case measured later reads under 1%.
_WARMUP_SECONDS = 0.5
_BATCH_SECONDS = 0.1
_MAX_INNER = 500

#: GIL-probe shape: long enough per call that thread scheduling overhead is
#: negligible, short enough that the whole probe stays a few seconds.
_GIL_LENGTH = 5_000
_GIL_CALLS = 80
_GIL_THREADS = 4


def _rust_built() -> bool:
    try:
        importlib.import_module("fpr_ff1._rs")
    except ImportError:
        return False
    return True


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


def _warm_up(fn: Callable[[], object], seconds: float) -> None:
    """Call ``fn`` untimed until ``seconds`` have elapsed."""
    deadline = time.perf_counter() + seconds
    while time.perf_counter() < deadline:
        fn()


def value_dependent_table() -> None:
    """Reproduce the SECURITY.md table: all-zero vs all-max timing delta.

    After an untimed warm-up, each pair is timed twice -- all-zero then
    all-max, then all-max then all-zero -- and the row is the mean of the two
    deltas, so neither input benefits from being measured second.
    """
    print("## Value-dependent timing (all-zero vs all-max, both orders, median of 25 batches)\n")
    first_radix, first_n = _VALUE_CASES[0]
    warm = FF1(key=_KEY, radix=first_radix)
    _warm_up(lambda: warm.encrypt_numerals([0] * first_n), _WARMUP_SECONDS)

    print("| radix | length | delta |")
    print("|---|---|---|")
    for radix, n in _VALUE_CASES:
        ff1 = FF1(key=_KEY, radix=radix)
        zero, top = [0] * n, [radix - 1] * n
        t_zero_first = _timed_encrypt(ff1, zero)
        t_max_second = _timed_encrypt(ff1, top)
        t_max_first = _timed_encrypt(ff1, top)
        t_zero_second = _timed_encrypt(ff1, zero)
        delta_zero_first = (t_max_second - t_zero_first) / t_zero_first
        delta_max_first = (t_max_first - t_zero_second) / t_zero_second
        delta = (delta_zero_first + delta_max_first) / 2 * 100
        print(f"| {radix} | {n} | {delta:+.1f}% |")


def throughput_table() -> None:
    """Small-input ops/s, construction and per-numeral cost, for sizing batch jobs."""
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


def backend_comparison_table() -> None:
    """Plan 00003 STEP-13: the compiled backend vs the E1 pure-Python baseline.

    The small-input regime is E2's case (review 00005: ~55% of an n=6 call
    is per-call cipher-context construction that a full Rust core with
    in-process AES eliminates; estimated ceiling ~8x). The long-input rows
    are context: E1 already removed the conversion cliff, so parity there
    is the expected result, not the target. The park rule (idea r02 section
    10): a measured speedup below 2x on the small-input cases means the
    backend is not worth shipping and the plan escalates.

    Two radices and several lengths, because the ratio varies with both; the
    README publishes every row rather than one remembered number (review
    00006 found an earlier published crossover roughly 10x too low).
    """
    if not _rust_built():
        print("\n## Backend comparison\n")
        print("Rust backend not built; run `just backend-dev` (or a release\n")
        print("maturin develop for meaningful numbers) to include this table.\n")
        return

    print("\n## Backend comparison (python = E1 reference, rust = compiled)\n")
    print("| Case | python µs/op | rust µs/op | speedup |")
    print("|---|---:|---:|---:|")

    for radix, lengths in _BACKEND_CASES:
        py = FF1(key=_KEY, radix=radix, backend="python")
        rs = FF1(key=_KEY, radix=radix, backend="rust")
        for n in lengths:
            plaintext = [i % radix for i in range(n)]
            t_py = _timed_encrypt(py, plaintext)
            t_rs = _timed_encrypt(rs, plaintext)
            print(
                f"| n = {n:,}, radix {radix} | {t_py * 1e6:.1f} | "
                f"{t_rs * 1e6:.1f} | {t_py / t_rs:.2f}x |"
            )


def gil_probe_table() -> None:
    """Review 00006 MED-01: does a backend run FF1 calls in parallel?

    The pure-Python backend is GIL-bound by construction, so its speedup is
    the control: at or a little below 1x however many threads are used --
    the threads cannot overlap, and switching between them costs. The
    compiled backend releases the GIL for the duration of the ten-round
    computation (`Python::detach` in `lib.rs`), so its threaded run should
    scale with the core count until memory bandwidth or the FF1 call's own
    Python-side validation becomes the limit.

    The same total work is done both ways -- `_GIL_CALLS` encrypt calls at
    n = `_GIL_LENGTH` -- so serial and threaded wall times are directly
    comparable.
    """
    print("\n## GIL probe (same total work, serial vs 4 threads)\n")
    print(f"n = {_GIL_LENGTH:,}, radix 10, {_GIL_CALLS} encrypt calls\n")
    print("| backend | serial ms/call | 4 threads ms/call | speedup |")
    print("|---|---:|---:|---:|")

    plaintext = [i % 10 for i in range(_GIL_LENGTH)]
    backends = ["python"] + (["rust"] if _rust_built() else [])
    for name in backends:
        ff1 = FF1(key=_KEY, radix=10, backend=name)

        def run(count: int, cipher: FF1 = ff1) -> None:
            for _ in range(count):
                cipher.encrypt_numerals(plaintext)

        start = time.perf_counter()
        run(_GIL_CALLS)
        serial = time.perf_counter() - start

        per_thread = _GIL_CALLS // _GIL_THREADS
        threads = [threading.Thread(target=run, args=(per_thread,)) for _ in range(_GIL_THREADS)]
        start = time.perf_counter()
        for thread in threads:
            thread.start()
        for thread in threads:
            thread.join()
        parallel = time.perf_counter() - start

        serial_ms = serial / _GIL_CALLS * 1e3
        parallel_ms = parallel / (per_thread * _GIL_THREADS) * 1e3
        print(f"| {name} | {serial_ms:.2f} | {parallel_ms:.2f} | {serial / parallel:.2f}x |")


def main() -> None:
    print(f"# fpr-ff1 timing harness ({time.strftime('%Y-%m-%d %H:%M %Z')})\n")
    print(f"Batches per measurement: {_BATCHES} (adaptive inner batch size)\n")
    value_dependent_table()
    throughput_table()
    backend_comparison_table()
    gil_probe_table()


if __name__ == "__main__":
    main()
