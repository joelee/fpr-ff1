"""Whole-surface assertions about promises the package makes.

These tests exist because the individual validation tests check cases one at a
time, and the contract's promise is universal: *every* rejection raises a typed
exception from a hierarchy rooted at ``FF1Error``. A case-by-case suite passes
happily while an untested input crashes with an ``AttributeError`` -- which is
exactly what review `45bc40f` found.

The repository-hygiene test is here for the same reason: a required file that
exists on the author's disk but was never committed looks present to every
local check and is missing for everyone else.
"""

# This module exists to feed deliberately wrong types to the public API, so
# argument-type diagnostics are suppressed for the whole file rather than
# annotated away one call at a time.  Every other module stays strictly checked.
# pyright: reportArgumentType=false

import pathlib
import re
import shutil
import subprocess
import tomllib
from decimal import Decimal
from fractions import Fraction
from typing import Any

import pytest

from fpr_ff1 import FF1, FF1Error

_REPO_ROOT = pathlib.Path(__file__).resolve().parents[1]
_VALID_KEY = b"\x00" * 16

#: Files the project contract requires to exist and ship.
_REQUIRED_FILES = ["README.md", "LICENSE", "SECURITY.md", "CHANGELOG.md", "pyproject.toml"]


def _malformed_calls() -> list[tuple[str, Any]]:
    """Every way we can think of to misuse the API, as callables."""
    ff1 = FF1(key=_VALID_KEY, radix=10)
    alpha = FF1(key=_VALID_KEY, radix=10, alphabet="0123456789")
    good = [1, 2, 3, 4, 5, 6]

    return [
        # Constructor: key
        ("key-str", lambda: FF1(key="0" * 16, radix=10)),
        ("key-int", lambda: FF1(key=123, radix=10)),
        ("key-none", lambda: FF1(key=None, radix=10)),
        ("key-short", lambda: FF1(key=b"\x00" * 15, radix=10)),
        ("key-long", lambda: FF1(key=b"\x00" * 33, radix=10)),
        # Constructor: radix
        ("radix-float", lambda: FF1(key=_VALID_KEY, radix=10.0)),
        ("radix-str", lambda: FF1(key=_VALID_KEY, radix="10")),
        ("radix-none", lambda: FF1(key=_VALID_KEY, radix=None)),
        ("radix-bool", lambda: FF1(key=_VALID_KEY, radix=True)),
        ("radix-zero", lambda: FF1(key=_VALID_KEY, radix=0)),
        ("radix-negative", lambda: FF1(key=_VALID_KEY, radix=-10)),
        ("radix-huge", lambda: FF1(key=_VALID_KEY, radix=2**16)),
        # Constructor: alphabet
        ("alphabet-list", lambda: FF1(key=_VALID_KEY, radix=10, alphabet=list("0123456789"))),
        ("alphabet-bytes", lambda: FF1(key=_VALID_KEY, radix=10, alphabet=b"0123456789")),
        ("alphabet-short", lambda: FF1(key=_VALID_KEY, radix=10, alphabet="012")),
        ("alphabet-dupes", lambda: FF1(key=_VALID_KEY, radix=10, alphabet="0123456788")),
        # Constructor: tweak
        ("tweak-str", lambda: FF1(key=_VALID_KEY, radix=10, tweak="abc")),
        ("tweak-int", lambda: FF1(key=_VALID_KEY, radix=10, tweak=1)),
        ("min-tweak-float", lambda: FF1(key=_VALID_KEY, radix=10, min_tweak_len=1.5)),
        ("max-tweak-str", lambda: FF1(key=_VALID_KEY, radix=10, max_tweak_len="4")),
        ("tweak-below-min", lambda: FF1(key=_VALID_KEY, radix=10, tweak=b"", min_tweak_len=4)),
        (
            "bounds-inverted",
            lambda: FF1(key=_VALID_KEY, radix=10, min_tweak_len=8, max_tweak_len=4),
        ),
        ("bounds-min-negative", lambda: FF1(key=_VALID_KEY, radix=10, min_tweak_len=-1)),
        ("bounds-max-negative", lambda: FF1(key=_VALID_KEY, radix=10, max_tweak_len=-1)),
        # Numeral interface: element types
        ("numeral-float", lambda: ff1.encrypt_numerals([1.0] * 6)),
        ("numeral-bool", lambda: ff1.encrypt_numerals([True] * 6)),
        ("numeral-str", lambda: ff1.encrypt_numerals(["1"] * 6)),
        ("numeral-decimal", lambda: ff1.encrypt_numerals([Decimal(1)] * 6)),
        ("numeral-fraction", lambda: ff1.encrypt_numerals([Fraction(1, 1)] * 6)),
        ("numeral-none", lambda: ff1.encrypt_numerals([None] * 6)),
        ("numeral-nested", lambda: ff1.encrypt_numerals([[1]] * 6)),
        # Numeral interface: values and shape
        ("numeral-negative", lambda: ff1.encrypt_numerals([-1, *good[1:]])),
        ("numeral-too-big", lambda: ff1.encrypt_numerals([10, *good[1:]])),
        ("too-short", lambda: ff1.encrypt_numerals([1])),
        ("too-long", lambda: ff1.encrypt_numerals(range(2**32))),
        ("generator", lambda: ff1.encrypt_numerals(v for v in good)),
        ("iterator", lambda: ff1.encrypt_numerals(iter(good))),
        ("numerals-none", lambda: ff1.encrypt_numerals(None)),
        ("numerals-int", lambda: ff1.encrypt_numerals(123456)),
        # Call-time tweak
        ("call-tweak-str", lambda: ff1.encrypt_numerals(good, "abc")),
        ("call-tweak-int", lambda: ff1.encrypt_numerals(good, 1)),
        # String interface
        ("str-no-alphabet", lambda: ff1.encrypt("123456")),
        ("str-int", lambda: alpha.encrypt(123456)),
        ("str-list", lambda: alpha.encrypt(list("123456"))),
        ("str-bytes", lambda: alpha.encrypt(b"123456")),
        ("str-none", lambda: alpha.encrypt(None)),
        ("str-bad-char", lambda: alpha.encrypt("12345x")),
        # Decrypt mirrors encrypt
        ("dec-numeral-float", lambda: ff1.decrypt_numerals([1.0] * 6)),
        ("dec-str-int", lambda: alpha.decrypt(123456)),
        ("dec-generator", lambda: ff1.decrypt_numerals(v for v in good)),
    ]


@pytest.mark.parametrize(
    ("label", "call"), _malformed_calls(), ids=lambda p: p if isinstance(p, str) else ""
)
def test_every_rejection_is_typed(label: str, call: Any) -> None:
    """No malformed input may escape as an untyped builtin exception.

    ``FF1Error`` covers data and configuration faults. ``TypeError`` is
    permitted only for structural API misuse -- passing something that is not a
    ``Sequence`` at all -- because that is a programming error against the
    annotation rather than a bad value.
    """
    with pytest.raises((FF1Error, TypeError)) as excinfo:
        call()

    # AttributeError, ValueError, KeyError etc. are all failures here.
    assert issubclass(excinfo.type, FF1Error | TypeError), (
        f"{label} raised {excinfo.type.__name__}, which is outside the documented hierarchy"
    )
    assert str(excinfo.value), f"{label} raised {excinfo.type.__name__} with an empty message"


def test_typeerror_is_reserved_for_non_sequences() -> None:
    """TypeError must not leak for inputs that are merely bad *data*.

    Guards the boundary drawn above: if a plain wrong-typed value starts
    raising TypeError, the hierarchy promise has quietly weakened.
    """
    ff1 = FF1(key=_VALID_KEY, radix=10)
    for bad in (1.0, True, "1", Decimal(1), None):
        with pytest.raises(FF1Error):
            ff1.encrypt_numerals([bad] * 6)  # pyright: ignore[reportArgumentType]


@pytest.mark.skipif(shutil.which("git") is None, reason="git not available")
@pytest.mark.parametrize("filename", _REQUIRED_FILES)
def test_required_files_are_tracked_by_git(filename: str) -> None:
    """Required files must be committed, not merely present on disk.

    Regression guard: ``SECURITY.md`` was written but never staged, so it was
    absent from the commit while every local check reported it present. The
    README and the ``Security`` project URL both link to it.
    """
    path = _REPO_ROOT / filename
    assert path.is_file(), f"{filename} is missing from the working tree"

    git = shutil.which("git")
    assert git is not None
    result = subprocess.run(  # noqa: S603  # fixed argv, resolved absolute path
        [git, "ls-files", "--error-unmatch", filename],
        cwd=_REPO_ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode == 128 and "not a git repository" in result.stderr.lower():
        pytest.skip("not a git checkout")
    assert result.returncode == 0, (
        f"{filename} exists on disk but is not tracked by git, so it will not ship"
    )


@pytest.mark.skipif(shutil.which("git") is None, reason="git not available")
def test_project_urls_match_the_git_remote() -> None:
    """Declared project URLs must point at the repository that actually exists.

    Regression guard: every URL said ``joelee/py-fpr-ff1`` (the local directory
    name) while the remote was ``joelee/fpr-ff1``. PyPI renders these in the
    sidebar, so a release would have shipped six dead links -- including the
    security disclosure link.
    """
    git = shutil.which("git")
    assert git is not None
    remote = subprocess.run(  # noqa: S603  # fixed argv, resolved absolute path
        [git, "remote", "get-url", "origin"],
        cwd=_REPO_ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    if remote.returncode != 0:
        pytest.skip("no origin remote configured")

    match = re.search(r"github\.com[:/]([^/]+/[^/.]+)", remote.stdout.strip())
    if match is None:
        pytest.skip("origin is not a GitHub remote")
    slug = match.group(1)

    with (_REPO_ROOT / "pyproject.toml").open("rb") as handle:
        urls: dict[str, str] = tomllib.load(handle)["project"]["urls"]

    assert urls, "pyproject declares no project URLs"
    for label, url in urls.items():
        assert f"github.com/{slug}" in url, (
            f"project URL {label}={url!r} does not match the git remote {slug!r}"
        )
