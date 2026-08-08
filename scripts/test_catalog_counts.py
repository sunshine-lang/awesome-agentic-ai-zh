#!/usr/bin/env python3
"""Regression tests for scripts/check-catalog-counts.py.

Pins the 2026-08 incident: the catalog's advertised size drifted three separate
ways, and two hand-counts got it wrong differently — one grep keyed on `^### [`
and silently skipped the single entry whose heading has no bracket link.

The first version of this checker then had its OWN coverage hole: its headline
regex required the number to be immediately followed by a fixed keyword, so
prose like "76+ 個**常用**整合" or "76+ **integration** catalog" never matched —
it validated 17 of 36 real claims and would have gone green while the docs
drifted. These tests pin both the entry-counting rule and the claim coverage.

Run:  python scripts/test_catalog_counts.py     (plain asserts, no pytest needed)
 or:  pytest scripts/test_catalog_counts.py
"""
import importlib.util
import tempfile
from pathlib import Path

_SPEC = importlib.util.spec_from_file_location(
    "check_catalog_counts", Path(__file__).with_name("check-catalog-counts.py")
)
ccc = importlib.util.module_from_spec(_SPEC)
_SPEC.loader.exec_module(ccc)


def _parse(body: str):
    with tempfile.TemporaryDirectory() as d:
        fp = Path(d) / "cat.md"
        fp.write_text(body, encoding="utf-8")
        return ccc.parse_catalog(fp)


# --- entry counting -----------------------------------------------------------

def test_counts_entry_without_bracket_link():
    """The bug that made the total read 75 instead of 76."""
    body = "## 1. Things\n\n### [a/b](https://x)\n\n### YIELD INTELLIGENCE MCP（Hosted）\n"
    entries, _ = _parse(body)
    assert entries[1] == 2


def test_not_an_entry_marker_excludes_heading():
    body = ("## 1. Things\n\n### [a/b](https://x)\n\n"
            "<!-- not-an-entry -->\n### How the three skills compose\n")
    entries, _ = _parse(body)
    assert entries[1] == 1


def test_headings_outside_numbered_sections_are_ignored():
    body = "## Some prose section\n\n### 要加新的？\n\n## 1. Things\n\n### [a/b](https://x)\n"
    entries, _ = _parse(body)
    assert entries == {1: 1}


def test_index_parses_both_bracket_styles():
    body = ("### Index\n\n1. [A](#a) (7)\n2. [B](#b)（11）\n\n"
            "## 1. A\n\n### [x/y](https://x)\n")
    _, index = _parse(body)
    assert index == {1: 7, 2: 11}


# --- headline-claim coverage (the checker's own bug) --------------------------

def _claims(line: str):
    """Numbers the checker would actually validate on this line."""
    if not any(mark in line for mark in ccc.CLAIM_LINE_MARKERS):
        return []
    out = []
    for m in ccc.HEADLINE_RE.finditer(line):
        if ccc.NOT_A_CATALOG_COUNT.match(line[m.end():]):
            continue
        out.append(int(m.group(1)))
    return out


def test_catches_claim_with_words_between_number_and_noun():
    """The coverage hole: prose inserts words after the number."""
    assert _claims("見 [`resources/mcp-skills-catalog.md`](x)（76+ 個常用辦公整合工具表）") == [76]
    assert _claims("See [`resources/mcp-skills-catalog.en.md`](x) — 76+ integration catalog") == [76]


def test_catches_catalogs_own_intro_line():
    """The single most important claim — it was never even scanned."""
    line = "> This page is a curated index of 76+ MCP servers / Claude Skills / integrations"
    assert _claims(line) == [76]


def test_catches_readme_scale_table_without_plus():
    assert _claims("| curation | ... | 240+ projects、76 MCP/Skill |") == [76]


def test_project_total_is_not_treated_as_catalog_size():
    """'240+ projects' on the same line is a different number."""
    line = "| **資源 curation** | 每階段精選 **240+** 個 project | 240+ projects、76 MCP/Skill |"
    assert 240 not in _claims(line)


def test_filenames_and_time_ranges_are_not_counted():
    """A bare \\d{2,3} match flagged `05-claude-code-ecosystem` and '30-50 分鐘'."""
    line = "看 [`resources/mcp-skills-catalog.md`](x)，約 30-50 分鐘，見 stages/05-claude-code-ecosystem.md"
    assert _claims(line) == []


def test_ignores_lines_not_about_the_catalog():
    assert _claims("Ollama has 170k+ stars and 16 categories of models") == []


def test_repo_is_consistent():
    """The live repo must pass — this is the CI gate."""
    assert ccc.main.__module__  # sanity: module loaded
    import io, sys
    buf, old = io.StringIO(), sys.stdout
    sys.stdout = buf
    try:
        sys.argv = ["check-catalog-counts.py", "--quiet"]
        rc = ccc.main()
    finally:
        sys.stdout = old
    assert rc == 0, buf.getvalue()


def _run_all():
    fns = [v for k, v in sorted(globals().items())
           if k.startswith("test_") and callable(v)]
    failed = 0
    for fn in fns:
        try:
            fn()
            print(f"  PASS  {fn.__name__}")
        except AssertionError as exc:
            failed += 1
            print(f"  FAIL  {fn.__name__}: {exc}")
        except Exception as exc:  # noqa: BLE001
            failed += 1
            print(f"  ERROR {fn.__name__}: {exc!r}")
    print(f"\n{len(fns) - failed}/{len(fns)} passed")
    return failed


if __name__ == "__main__":
    import sys
    sys.exit(1 if _run_all() else 0)
