"""Fail unless the fpr-ff1 crate package contains exactly what it should.

Run from the repository root (plan 00009 STEP-10). It lists the package with
``cargo package --list`` -- the same file set ``cargo publish`` uploads -- and
checks every entry against an allow-list and a list of forbidden patterns.
A crates.io version cannot be replaced, so this runs before any publication,
mirroring the sdist contents check in ci.yml. ``--allow-dirty`` is the only
accepted argument, for use in an uncommitted working tree.
"""

import re
import shutil
import subprocess
import sys

_CARGO_ARGS = [
    "package",
    "--list",
    "--locked",
    "-p",
    "fpr-ff1",
    "--manifest-path",
    "rust/Cargo.toml",
]

#: Every entry must match one of these.
_ALLOWED = re.compile(
    r"^(\.cargo_vcs_info\.json|Cargo\.lock|Cargo\.toml(\.orig)?|README\.md"
    r"|LICENSE-(MIT|APACHE)|src/[A-Za-z0-9_/]+\.rs|tests/[A-Za-z0-9_/]+\.rs)$"
)

#: Belt and braces: never shipped, whatever the allow-list says.
_FORBIDDEN = re.compile(
    r"(AGENTS\.md|CLAUDE\.md|(^|/)docs/|(^|/)\.github/|(^|/)\.agents/|(^|/)target/"
    r"|\.py$|\.pyc$|__pycache__|\.(so|pyd|dll|dylib)$|pyproject\.toml|\.env"
    # Fixtures stay in tests/vectors/; Cargo's own .cargo_vcs_info.json is expected.
    r"|(?<!^\.cargo_vcs_info)\.json$)"
)

_REQUIRED = {
    "Cargo.toml",
    "Cargo.toml.orig",
    "README.md",
    "LICENSE-MIT",
    "LICENSE-APACHE",
    "src/lib.rs",
    "src/engine.rs",
    "src/ff1.rs",
    "src/validate.rs",
    "src/error.rs",
}


def main() -> int:
    extra = sys.argv[1:]
    if extra not in ([], ["--allow-dirty"]):
        sys.stderr.write(f"unexpected arguments {extra}; only --allow-dirty is accepted\n")
        return 2
    cargo = shutil.which("cargo")
    if cargo is None:
        sys.stderr.write("cargo is not on PATH\n")
        return 2
    listing = subprocess.run(  # noqa: S603  # fixed argv, resolved absolute path
        [cargo, *_CARGO_ARGS, *extra], check=True, capture_output=True, text=True
    ).stdout.split()
    problems = [f"not allowed: {entry}" for entry in listing if not _ALLOWED.match(entry)]
    problems += [f"forbidden: {entry}" for entry in listing if _FORBIDDEN.search(entry)]
    problems += [f"missing: {entry}" for entry in sorted(_REQUIRED - set(listing))]
    for line in problems:
        sys.stderr.write(line + "\n")
    sys.stdout.write(f"crate package: {len(listing)} entries, {len(problems)} problems\n")
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
