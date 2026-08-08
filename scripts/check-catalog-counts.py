#!/usr/bin/env python3
"""check-catalog-counts.py — keep the MCP catalog's advertised counts honest.

`resources/mcp-skills-catalog.*.md` advertises its size in two places that drift
independently from the actual content:

  1. the per-section counts in the Index, e.g. `11. [中文圈專用](#…)（11）`
  2. the headline "NN+ MCP servers / Skills" repeated across README, RESOURCES,
     branches, stages and tracks

Both drifted in 2026-08: the Index summed to 73 while the file held 76 entries,
and 39 places still advertised a long-stale number. Worse, two hand-counts got it
wrong in different ways — one grep keyed on `^### [` and silently skipped the one
entry whose heading carries no bracket link.

So the count is computed here once, from the file, and everything else is checked
against it.

An ENTRY is a `###` heading inside a numbered `## N.` section. A `###` heading
that is commentary rather than a catalog entry must carry an explicit
`<!-- not-an-entry -->` marker on the line above — that is deliberate: an opt-out
you can see beats a heuristic that guesses.

Usage:
    python scripts/check-catalog-counts.py           # report (exit 1 on mismatch)
    python scripts/check-catalog-counts.py --quiet    # summary only
"""

import argparse
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
# Named rather than inlined at the scan site so it can't drift out of sync with
# the other gates' exclude sets unnoticed.
SCAN_EXCLUDE_DIRS = {".git", ".claude", "_build", "node_modules", "book"}
CATALOGS = [
    "resources/mcp-skills-catalog.md",
    "resources/mcp-skills-catalog.en.md",
    "resources/mcp-skills-catalog.zh-Hans.md",
]
SECTION_RE = re.compile(r"^## (\d+)\.")
ENTRY_RE = re.compile(r"^### ")
# Index row: `11. [Label](#anchor) (11)` or full-width `（11）`
INDEX_RE = re.compile(r"^(\d+)\.\s+\[.*?\]\(#[^)]*\)\s*[（(](\d+)[）)]\s*$")
NOT_AN_ENTRY = "<!-- not-an-entry -->"
# Lines that advertise the catalog's size. Keyed on the catalog being referenced,
# NOT on the phrasing around the number — an earlier version listed the exact
# suffixes ("個 MCP", "integrations", …) and missed 19 of 36 real claims, because
# prose inserts words in between ("76+ 個**常用**整合", "76+ **integration** catalog").
# A gate that silently passes is worse than no gate.
CLAIM_LINE_MARKERS = (
    "mcp-skills-catalog",          # any link to the catalog
    "MCP server / Skill",          # zh-TW / zh-Hans shorthand
    "MCP servers / Claude Skills",  # the catalogs' own intro line (en)
    "MCP server / Claude Skill",    # the catalogs' own intro line (zh)
    "MCP/Skill",                   # README scale table
    "integration catalog",         # .github/outreach drafts
    "Catalog includes",            # .github/outreach drafts
    "integrations grouped",        # .github/outreach drafts
)
# On a claim line, a size claim is a 2-3 digit number that is either suffixed
# with "+" (every prose form uses this: "76+ 個整合", "76+ entry catalog",
# "76+ MCP servers / Claude Skills") or directly labelled "MCP/Skill" (the README
# scale table, the one form without a "+"). Requiring one of those two shapes is
# what keeps filenames (`05-claude-code-ecosystem`), anchors and time ranges
# ("30-50 分鐘") from being mistaken for counts — a bare \d{2,3} match flagged
# all of those.
HEADLINE_RE = re.compile(r"(?<!\d)(\d{2,3})(?:\+|\s*MCP/Skill)")
# The README scale row counts BOTH things on one line ("240+ projects、76 MCP/Skill").
# The project total is a different number and must not be compared to the catalog size.
# `[*_\s]*` because the number is usually bolded: "**240+** 個 project".
NOT_A_CATALOG_COUNT = re.compile(r"[*_\s]*(?:個|个)?\s*projects?\b")


def parse_catalog(fp: Path):
    """Return (entries_per_section, index_per_section)."""
    lines = fp.read_text(encoding="utf-8").split("\n")
    entries, index = {}, {}
    section = None
    for i, line in enumerate(lines):
        m = SECTION_RE.match(line)
        if m:
            section = int(m.group(1))
            entries.setdefault(section, 0)
            continue
        if line.startswith("## "):
            section = None  # a non-numbered H2 ends the entry region
            continue
        mi = INDEX_RE.match(line.strip())
        if mi:
            index[int(mi.group(1))] = int(mi.group(2))
            continue
        if ENTRY_RE.match(line) and section is not None:
            # Look back past blank lines: a contributor adding one for
            # readability must not silently re-enable the double count.
            j = i - 1
            while j >= 0 and not lines[j].strip():
                j -= 1
            if j >= 0 and NOT_AN_ENTRY in lines[j]:
                continue
            entries[section] = entries.get(section, 0) + 1
    return entries, index


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--quiet", action="store_true")
    args = ap.parse_args()
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except (AttributeError, ValueError):
        pass

    problems = []
    totals = {}

    for rel in CATALOGS:
        fp = REPO_ROOT / rel
        entries, index = parse_catalog(fp)
        total = sum(entries.values())
        totals[rel] = total
        for sec in sorted(set(entries) | set(index)):
            got, said = entries.get(sec, 0), index.get(sec)
            if said is None:
                problems.append(f"{rel}: §{sec} has {got} entries but no Index row")
            elif got != said:
                problems.append(f"{rel}: §{sec} Index says ({said}) but section has {got} entries")
        if sum(index.values()) != total:
            problems.append(
                f"{rel}: Index rows sum to {sum(index.values())} but the file has {total} entries"
            )
        if not args.quiet:
            print(f"{rel}: {total} entries, Index sums to {sum(index.values())}")

    if len(set(totals.values())) > 1:
        problems.append(f"locales disagree on entry count: {totals}")

    # The headline claim must match the real total.
    real = max(totals.values()) if totals else 0
    stale, checked = [], 0
    for fp in sorted(REPO_ROOT.rglob("*.md")):
        # Match on the path RELATIVE to REPO_ROOT. Matching fp.parts tests the
        # ABSOLUTE path, and this set contains ".claude" — so a checkout under
        # `.claude/worktrees/<name>/` skipped all 248 markdown files while this
        # BLOCKING gate still printed its ✓. Found 2026-08-02 alongside the same
        # bug in check-locale-links.py.
        if any(p in SCAN_EXCLUDE_DIRS for p in fp.relative_to(REPO_ROOT).parts):
            continue
        if fp.name.startswith("CHANGELOG"):
            continue  # history legitimately records older numbers
        rel = fp.relative_to(REPO_ROOT).as_posix()
        for i, line in enumerate(fp.read_text(encoding="utf-8").split("\n"), 1):
            if not any(mark in line for mark in CLAIM_LINE_MARKERS):
                continue
            for m in HEADLINE_RE.finditer(line):
                if NOT_A_CATALOG_COUNT.match(line[m.end():]):
                    continue  # e.g. "240+ projects" — that is the project total
                checked += 1
                if int(m.group(1)) != real:
                    stale.append(f"{rel}:{i}: says {m.group(1)}, real total is {real}")
    problems.extend(stale)
    if not args.quiet:
        print(f"checked {checked} size claim(s) against the real total ({real})")

    if problems:
        print("\n".join(f"❌ {p}" for p in problems))
        print(f"\nFound {len(problems)} catalog-count problem(s).")
        return 1
    print(f"\n✓ Catalog counts consistent ({real} entries, Index + headline claims agree).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
