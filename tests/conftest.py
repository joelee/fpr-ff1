"""Shared fixtures for the test suite."""

import importlib
import json
import os
import pathlib
from collections.abc import Callable
from typing import Any, cast

import pytest

from fpr_ff1 import FF1

_VECTOR_DIR = pathlib.Path(__file__).parent / "vectors"

#: Mirrors the differential-oracle availability contract (AGENTS.md tests
#: section 7): the rust backend parameterisation skips locally when the
#: extension is not built and fails hard when required. CI's
#: `rust-conformance` job sets FPR_FF1_REQUIRE_RUST_BACKEND=1, so a missing
#: extension fails the release gate rather than silently halving the suite.
_RUST_REQUIRED = os.environ.get("FPR_FF1_REQUIRE_RUST_BACKEND", "").strip() not in {"", "0"}


def _rust_available() -> bool:
    try:
        importlib.import_module("fpr_ff1._rs")
    except ImportError:
        return False
    return True


_RUST_BUILT = _rust_available()

if _RUST_REQUIRED and not _RUST_BUILT:
    raise ImportError("FPR_FF1_REQUIRE_RUST_BACKEND is set but fpr_ff1._rs is not built")

#: Both backends, or just the one that is available. The python backend is
#: the reference and always runs; the rust parameterisation is the plan
#: 00003 STEP-11 dual-backend conformance (REQ-16).
BACKENDS: list[str] = ["python"] + (["rust"] if _RUST_BUILT else [])


@pytest.fixture(params=BACKENDS)
def backend(request: pytest.FixtureRequest) -> str:
    """The FF1 backend under test: the reference, and the compiled core."""
    return str(request.param)


@pytest.fixture
def ff1_factory(backend: str) -> Callable[..., FF1]:
    """Build FF1 instances pinned to the parameterised backend.

    Conformance modules use this instead of calling ``FF1`` directly so
    every assertion runs unchanged against both backends.
    """

    def _make(**kwargs: Any) -> FF1:
        return FF1(**kwargs, backend=backend)

    return _make


@pytest.fixture
def encrypt_traced(backend: str) -> Callable[..., tuple[list[int], list[dict[str, Any]]]]:
    """The per-round trace hook, uniform across both backends (REQ-16).

    The python backend uses the private ``FF1._encrypt_traced`` method; the
    rust backend uses the extension's test-only ``_test_encrypt_traced``
    binding, whose byte and big-int fields are normalized here so both
    traces share the Python hook's shape. The returned callable takes an
    FF1 instance, a numeral sequence, and an optional tweak.
    """
    if backend == "python":

        def traced_python(
            ff1: FF1, x: list[int], tweak: bytes | None = None
        ) -> tuple[list[int], list[dict[str, Any]]]:
            return ff1._encrypt_traced(x, tweak)  # pyright: ignore[reportPrivateUsage]

        return traced_python

    # The compiled extension has no stubs; every access is deliberately
    # Any-typed at this single boundary, mirroring the STEP-09 validation
    # module's approach.
    rs = cast("Any", importlib.import_module("fpr_ff1._rs"))

    def traced_rust(
        ff1: FF1, x: list[int], tweak: bytes | None = None
    ) -> tuple[list[int], list[dict[str, Any]]]:
        t = ff1._default_tweak if tweak is None else tweak  # pyright: ignore[reportPrivateUsage]
        ct, raw = rs._test_encrypt_traced(ff1._key, ff1._radix, x, t)  # pyright: ignore[reportPrivateUsage]
        trace: list[dict[str, Any]] = []
        for rec in cast("list[dict[str, Any]]", raw):
            normalized = dict(rec)
            # The Python hook's shape: byte fields as list[int], big-int
            # fields as int. The Rust binding carries them as bytes.
            for field in ("P", "Q", "R", "S"):
                normalized[field] = list(cast("bytes", rec[field]))
            normalized["y"] = int.from_bytes(cast("bytes", rec["y"]), "big")
            normalized["c"] = int.from_bytes(cast("bytes", rec["c"]), "big")
            trace.append(normalized)
        return list(cast("list[int]", ct)), trace

    return traced_rust


@pytest.fixture(scope="session")
def nist_samples() -> list[dict[str, Any]]:
    """The nine published NIST SP 800-38G FF1 sample vectors."""
    with (_VECTOR_DIR / "nist_ff1_samples.json").open(encoding="utf-8") as handle:
        data: dict[str, Any] = json.load(handle)
    vectors: list[dict[str, Any]] = data["vectors"]
    return vectors
