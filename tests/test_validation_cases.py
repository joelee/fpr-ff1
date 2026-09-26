"""Shared validation cases, Python side (plan 00009 STEP-08).

``tests/vectors/validation_cases.json`` is read by this module and by the
``fpr-ff1`` Rust crate's test suite. Both must reach the same outcome for
every case: accepted, or rejected with the named exception class and exactly
the recorded message. That holds the Python package's validation and the
crate's independent port of it in step, which a change to either side would
otherwise silently break.

Cases run on both backends: validation happens in Python for both, so the
outcome must not depend on the backend.
"""

import json
import pathlib
from typing import Any

import pytest

import fpr_ff1
from fpr_ff1 import FF1Error

_CASES_PATH = pathlib.Path(__file__).parent / "vectors" / "validation_cases.json"
_CASES: list[dict[str, Any]] = json.loads(_CASES_PATH.read_text(encoding="utf-8"))["cases"]


def _key(construct: dict[str, Any]) -> object:
    key = bytes(range(construct["key_len"]))
    if construct.get("key_form") == "released_memoryview":
        view = memoryview(key)
        view.release()
        return view
    return key


def _outcome(ff1_factory: Any, case: dict[str, Any]) -> tuple[str, str | None]:
    construct = case["construct"]
    kwargs: dict[str, Any] = {"key": _key(construct), "radix": construct["radix"]}
    for name in ("alphabet", "min_tweak_len", "max_tweak_len"):
        if name in construct:
            kwargs[name] = construct[name]
    if "tweak_hex" in construct:
        kwargs["tweak"] = bytes.fromhex(construct["tweak_hex"])
    try:
        ff1 = ff1_factory(**kwargs)
        call = case.get("call")
        if call is not None:
            tweak = bytes.fromhex(call["tweak_hex"]) if "tweak_hex" in call else None
            operand = call["x"] if "x" in call else call["s"]
            getattr(ff1, call["op"])(operand, tweak)
    except FF1Error as exc:
        return type(exc).__name__, str(exc)
    return "accepted", None


@pytest.mark.parametrize("case", _CASES, ids=[c["id"] for c in _CASES])
def test_shared_validation_case(ff1_factory: Any, case: dict[str, Any]) -> None:
    kind, message = _outcome(ff1_factory, case)
    assert kind == case["expect"], f"{case['id']}: {kind}: {message}"
    if kind != "accepted":
        assert message == case["message"], case["id"]


def test_cases_cover_every_exception_class() -> None:
    """Every documented exception class appears, except BackendError: backend
    selection is Python-only and has no counterpart in the crate."""
    classes = {
        name
        for name in dir(fpr_ff1)
        if isinstance(getattr(fpr_ff1, name), type) and issubclass(getattr(fpr_ff1, name), FF1Error)
    }
    expected = classes - {"BackendError"}
    assert expected <= {c["expect"] for c in _CASES}, expected - {c["expect"] for c in _CASES}
    assert "accepted" in {c["expect"] for c in _CASES}


def test_case_ids_are_unique_and_python_only_cases_say_why() -> None:
    ids = [c["id"] for c in _CASES]
    assert len(ids) == len(set(ids))
    for case in _CASES:
        if "python_only" in case:
            assert case["python_only"].strip(), f"{case['id']}: python_only needs a reason"
