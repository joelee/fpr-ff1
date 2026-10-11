"""Tests for the pure helper scripts CI runs from ``.github/scripts/``.

``semver_release_type.py`` chooses the release type ``cargo semver-checks``
compares the crate under, against the last stable crates.io version (plan
00011 STEP-04). Deriving it from the version alone made every release
candidate a "major change" with zero checks run, so this arithmetic is now
part of the release gate and is tested like the rest of it.

The scripts live outside the package and are not in the sdist, which ships
``tests/``: a downstream packager running ``pytest`` from an unpacked sdist
skips this module rather than failing. In the repository the scripts are
always present, so every local and CI run executes it.
"""

import pathlib
import subprocess
import sys

import pytest

_ROOT = pathlib.Path(__file__).resolve().parents[1]
_SCRIPT = _ROOT / ".github" / "scripts" / "semver_release_type.py"

pytestmark = pytest.mark.skipif(
    not _SCRIPT.is_file(), reason="CI scripts are not shipped in the sdist"
)


def _run(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(  # noqa: S603  # fixed argv: this interpreter and a repository script
        [sys.executable, str(_SCRIPT), *args],
        capture_output=True,
        text=True,
        check=False,
        cwd=_ROOT,
    )


@pytest.mark.parametrize(
    ("current", "baseline", "expected"),
    [
        ("2.1.1", "2.1.0", "patch"),
        # An unbumped manifest after a release is still checked, as a patch:
        # an API break on main fails until the version says so.
        ("2.1.0", "2.1.0", "patch"),
        ("2.2.0-rc1", "2.1.0", "minor"),
        ("2.2.0-rc2", "2.1.0", "minor"),
        ("2.2.0", "2.1.0", "minor"),
        ("2.1.2-rc1", "2.1.1", "patch"),
        ("3.0.0-rc1", "2.1.0", "major"),
        ("3.0.0", "2.9.9", "major"),
    ],
)
def test_release_type(current: str, baseline: str, expected: str) -> None:
    result = _run(current, baseline)
    assert result.returncode == 0, result.stderr
    assert result.stdout == f"{expected}\n"
    assert result.stderr == ""


@pytest.mark.parametrize(
    ("current", "baseline"),
    [
        ("2.0.9", "2.1.0"),
        ("1.9.0", "2.1.0"),
        # Same release numbers, but a pre-release precedes its release.
        ("2.1.0-rc1", "2.1.0"),
    ],
)
def test_current_below_baseline_fails_naming_both(current: str, baseline: str) -> None:
    result = _run(current, baseline)
    assert result.returncode == 1
    assert result.stdout == ""
    assert current in result.stderr
    assert baseline in result.stderr


@pytest.mark.parametrize(
    "args",
    [
        ("2.1", "2.1.0"),
        ("2.1.0", "None"),  # crates.io max_stable_version is null with no stable release
        ("v2.1.0", "2.1.0"),
        ("2.1.0rc1", "2.1.0"),  # PEP 440 spelling; the crate manifest uses semver
        ("02.1.0", "2.1.0"),
        ("2.1.0", "2.1.0-rc1"),  # the baseline must be a stable release
        ("2.1.0",),
        ("2.1.0", "2.1.0", "2.1.0"),
    ],
)
def test_malformed_arguments_fail(args: tuple[str, ...]) -> None:
    result = _run(*args)
    assert result.returncode == 2
    assert result.stdout == ""
    assert result.stderr
