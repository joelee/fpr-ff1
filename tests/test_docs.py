"""The two README files as they are rendered and copied (plan 00010 REQ-08, REQ-09).

``README.md`` is the PyPI project page as well as the GitHub front page, and
PyPI cannot resolve a relative link.  ``rust/fpr-ff1/README.md`` is the
crates.io page and, through ``include_str!``, the docs.rs crate root: rustdoc
hides a doctest line that starts with ``#`` and resolves intra-doc links, but
crates.io shows both verbatim.  Each of those defects was invisible on GitHub
and shipped in 2.1.0rc1, so they are checked here rather than by eye.

The examples are checked too: every Python block in ``README.md`` runs, in
order, in one namespace, and every Rust block in it is a verbatim copy of text
in the crate README, whose blocks ``cargo test --doc`` compiles and runs.

These tests read files only; they need neither the compiled backend nor a Rust
toolchain, so they run in ``just quality`` and from an unpacked sdist.
"""

from __future__ import annotations

import re
import warnings
from dataclasses import dataclass
from pathlib import Path

import pytest

_ROOT = Path(__file__).resolve().parent.parent
_README = _ROOT / "README.md"
_CRATE_README = _ROOT / "rust" / "fpr-ff1" / "README.md"

# NIST SP 800-38G sample 2: the known answer both languages must show.
_NIST_SAMPLE_2_CIPHERTEXT = "6124200773"

_FENCE = re.compile(r"^```(?P<lang>[\w-]*)[^\n]*\n(?P<body>.*?)^```[ \t]*$", re.M | re.S)
_SKIP_MARKER = re.compile(r"<!--\s*docs-test:\s*skip\s*\((?P<reason>[^)]*)\)\s*-->")
_INLINE_CODE = re.compile(r"`[^`\n]*`")
# Inline links and images, reference definitions, and HTML attributes.
_LINK_TARGETS = (
    re.compile(r"\]\((?P<target>[^)\s]*)(?:\s+\"[^\"]*\")?\)"),
    re.compile(r"^\s{0,3}\[[^\]]+\]:\s*(?P<target>\S+)", re.M),
    re.compile(r"\b(?:href|src)=\"(?P<target>[^\"]*)\""),
)
# A bracketed span not opening an inline link: a rustdoc intra-doc link
# ([`Error`], [Error]) or a reference-style link, neither of which crates.io
# can render.
_BARE_BRACKETS = re.compile(r"\[(?P<text>[^\[\]\n]+)\](?![(\[:])")
_EMPTY_BRACKETS = re.compile(r"\[\](?![(\[:])")


@dataclass(frozen=True)
class _Block:
    lang: str
    body: str
    line: int  # 1-based line of the opening fence
    skip_reason: str | None


def _blocks(path: Path) -> list[_Block]:
    text = path.read_text(encoding="utf-8")
    blocks: list[_Block] = []
    for match in _FENCE.finditer(text):
        line = text.count("\n", 0, match.start()) + 1
        preceding = text[: match.start()].rstrip("\n").rsplit("\n", 1)[-1]
        marker = _SKIP_MARKER.fullmatch(preceding.strip())
        blocks.append(
            _Block(
                lang=match["lang"],
                body=match["body"],
                line=line,
                skip_reason=marker["reason"].strip() if marker else None,
            )
        )
    return blocks


def _prose_lines(path: Path) -> list[tuple[int, str]]:
    """Every line outside fenced blocks, with inline code removed."""
    text = path.read_text(encoding="utf-8")
    fenced: set[int] = set()
    for match in _FENCE.finditer(text):
        first = text.count("\n", 0, match.start()) + 1
        last = text.count("\n", 0, match.end()) + 1
        fenced.update(range(first, last + 1))
    return [
        (number, _INLINE_CODE.sub("", line))
        for number, line in enumerate(text.splitlines(), start=1)
        if number not in fenced
    ]


def _non_absolute_links(path: Path) -> list[str]:
    problems: list[str] = []
    for number, line in _prose_lines(path):
        for pattern in _LINK_TARGETS:
            for match in pattern.finditer(line):
                target = match["target"]
                if not (target.startswith(("https://", "#"))):
                    problems.append(f"{path.name}:{number}: link target {target!r}")
    return problems


@pytest.mark.parametrize("path", [_README, _CRATE_README], ids=["README", "crate-README"])
def test_every_link_is_absolute_or_a_same_page_anchor(path: Path) -> None:
    # PyPI renders README.md without a base URL, so a relative target is a
    # dead link there; crates.io and docs.rs show the crate README away from
    # the repository in the same way.
    assert _non_absolute_links(path) == []


def test_crate_readme_rust_blocks_have_no_hidden_doctest_lines() -> None:
    # rustdoc hides "# line" in a doctest; crates.io renders it verbatim.
    problems = [
        f"{_CRATE_README.name}:{block.line + offset}: {line.strip()!r}"
        for block in _blocks(_CRATE_README)
        if block.lang == "rust"
        for offset, line in enumerate(block.body.splitlines(), start=1)
        if line.strip() == "#" or line.strip().startswith("# ")
    ]
    assert problems == []


def test_crate_readme_has_no_intra_doc_or_reference_links() -> None:
    problems = [
        f"{_CRATE_README.name}:{number}: {match.group(0)!r}"
        for number, line in _prose_lines(_CRATE_README)
        for match in _BARE_BRACKETS.finditer(line)
        # The image half of a badge, "[![alt](img)](link)", is an inline link.
        if not match["text"].startswith("!")
    ]
    # Inline code was stripped, so a backticked name in brackets such as
    # [`Error`] leaves "[]" behind; catch that shape too, unless an inline
    # link target follows it, as in [`fpr-ff1`](https://...).
    problems += [
        f"{_CRATE_README.name}:{number}: intra-doc link"
        for number, line in _prose_lines(_CRATE_README)
        if _EMPTY_BRACKETS.search(line)
    ]
    assert problems == []


def test_every_readme_python_example_runs() -> None:
    namespace: dict[str, object] = {"__name__": "readme_examples"}
    skipped: list[str] = []
    for block in _blocks(_README):
        if block.lang != "python":
            continue
        if block.skip_reason is not None:
            skipped.append(f"README.md:{block.line}: {block.skip_reason}")
            continue
        code = compile(block.body, f"README.md:{block.line}", "exec")
        exec(code, namespace)  # noqa: S102 -- the README's own examples, by design
    for entry in skipped:
        warnings.warn(f"README example not executed: {entry}", stacklevel=1)


def test_every_skip_marker_gives_a_reason() -> None:
    markers = _SKIP_MARKER.findall(_README.read_text(encoding="utf-8"))
    assert all(reason.strip() for reason in markers), markers


def test_every_readme_rust_example_is_a_doctested_crate_readme_example() -> None:
    crate_readme = _CRATE_README.read_text(encoding="utf-8")
    missing = [
        f"README.md:{block.line}"
        for block in _blocks(_README)
        if block.lang == "rust" and block.body not in crate_readme
    ]
    assert missing == []


def test_readme_checks_nist_sample_2_in_python_and_rust() -> None:
    languages = {
        block.lang
        for block in _blocks(_README)
        if block.skip_reason is None and _NIST_SAMPLE_2_CIPHERTEXT in block.body
    }
    assert {"python", "rust"} <= languages
