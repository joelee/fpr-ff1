"""Shared fixtures for the test suite."""

import json
import pathlib
from typing import Any

import pytest

_VECTOR_DIR = pathlib.Path(__file__).parent / "vectors"


@pytest.fixture(scope="session")
def nist_samples() -> list[dict[str, Any]]:
    """The nine published NIST SP 800-38G FF1 sample vectors."""
    with (_VECTOR_DIR / "nist_ff1_samples.json").open(encoding="utf-8") as handle:
        data: dict[str, Any] = json.load(handle)
    vectors: list[dict[str, Any]] = data["vectors"]
    return vectors
