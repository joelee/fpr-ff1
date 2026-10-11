"""Print the release type ``cargo semver-checks`` should check the crate under.

Run by the ``crate-package`` job in ci.yml (plan 00011 STEP-04) as::

    python3 .github/scripts/semver_release_type.py <current> <baseline>

``<current>`` is the ``fpr-ff1`` crate's manifest version and ``<baseline>``
is crates.io's ``max_stable_version`` for the crate, the version the check
compares against. Left to itself, ``cargo semver-checks`` derives the release
type from the version number, which made every release candidate a "major
change" with nothing checked: at ``2.1.0rc2`` and ``2.1.0`` it ran 0 of 254
checks. Passing the type explicitly makes a candidate answer to the release it
precedes.

The rule compares release numbers, ignoring the current version's
pre-release suffix: a different major is ``major``, a different minor is
``minor``, anything else is ``patch``. An unbumped manifest after a release is
therefore checked as a patch, so an API break on ``main`` fails until the
version says so. A current version that precedes the baseline -- lower
release numbers, or a pre-release of the baseline itself -- exits 1, naming
both. Malformed arguments, including a pre-release or missing baseline, exit
2. The output is the type alone on stdout. Standard library only; no network.
"""

import re
import sys

#: Semantic Versioning 2.0.0 core numbers (no leading zeros) with an optional
#: pre-release, as Cargo spells it. Build metadata never appears here.
_VERSION = re.compile(
    r"(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)(?:-([0-9A-Za-z-]+(?:\.[0-9A-Za-z-]+)*))?"
)

_USAGE = "usage: semver_release_type.py <current-crate-version> <baseline-stable-version>"


def _parse(label: str, text: str) -> tuple[tuple[int, int, int], str | None]:
    match = _VERSION.fullmatch(text)
    if match is None:
        sys.stderr.write(f"{label} version {text!r} is not a semver version\n")
        raise SystemExit(2)
    major, minor, patch, pre = match.groups()
    return (int(major), int(minor), int(patch)), pre


def main(argv: list[str]) -> int:
    if len(argv) != 2:  # noqa: PLR2004  # exactly <current> <baseline>
        sys.stderr.write(_USAGE + "\n")
        return 2
    current_text, baseline_text = argv
    current, current_pre = _parse("current", current_text)
    baseline, baseline_pre = _parse("baseline", baseline_text)
    if baseline_pre is not None:
        sys.stderr.write(f"baseline {baseline_text} must be a stable release\n")
        return 2
    if current < baseline or (current == baseline and current_pre is not None):
        sys.stderr.write(
            f"crate version {current_text} precedes the published baseline {baseline_text}\n"
        )
        return 1
    if current[0] != baseline[0]:
        release_type = "major"
    elif current[1] != baseline[1]:
        release_type = "minor"
    else:
        release_type = "patch"
    sys.stdout.write(release_type + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
