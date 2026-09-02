#!/usr/bin/env python3
"""Keep catalog entries in sync without publishing a number that will drift.

The machine may count entries. Reader-facing pages should describe what the
catalog helps with, not advertise a total that becomes stale after the next PR.
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parent.parent

# Always compare relative path parts. An absolute checkout under
# ``.claude/worktrees`` must not make the gate skip the whole repository.
SCAN_EXCLUDE_DIRS = {
    ".git",
    ".claude",
    ".ai",
    ".coord",
    "_build",
    "_site",
    "archives",
    "book",
    "node_modules",
}

CATALOGS = (
    "resources/mcp-skills-catalog.md",
    "resources/mcp-skills-catalog.en.md",
    "resources/mcp-skills-catalog.zh-Hans.md",
)

SECTION_RE = re.compile(r"^## (\d+)\.")
ENTRY_RE = re.compile(r"^### ")
INDEX_COUNT_RE = re.compile(r"^\s*\d+\.\s+\[.*?\]\(#[^)]+\)\s*[（(]\d+[）)]\s*$")
NOT_AN_ENTRY = "<!-- not-an-entry -->"

CATALOG_CONTEXT_RE = re.compile(
    r"mcp-skills-catalog|MCP\s*/\s*Skills?\s+(?:catalog|目錄|目录)|"
    r"(?:entry\s+)?integration\s+catalog|integrations?\s+grouped\s+by\s+use\s+case|"
    r"Catalog\s+includes",
    re.IGNORECASE,
)

ADVERTISED_TOTAL_RE = re.compile(
    r"(?<![\d.])(\d{2,4})(?:\+|\s*(?:curated\s+)?"
    r"(?:entries?|integrations?|tools?|servers?|resources?|projects?|"
    r"個|个|條|条))",
    re.IGNORECASE,
)

VOLATILE_PUBLIC_TOTAL_RE = re.compile(
    r"(?<![\d.])(\d{2,4})\+\s*(?:curated\s+)?"
    r"(?:entr(?:y|ies)|integrations?|resources?|projects?|repos?|tools?|servers?|"
    r"個\s*(?:資源|專案|項目|entr(?:y|ies)|repos?|projects?)|"
    r"个\s*(?:资源|项目|entr(?:y|ies)|repos?|projects?)|資源|资源|專案|项目|條|条)",
    re.IGNORECASE,
)

APPROX_PUBLIC_TOTAL_RE = re.compile(
    r"(?:~|≈|about|around|roughly|approximately|約|约)\s*(\d{2,4})\s*"
    r"(?:curated\s+)?(?:entries?|integrations?|resources?|projects?|repos?|tools?|servers?)",
    re.IGNORECASE,
)

CATEGORY_PUBLIC_TOTAL_RE = re.compile(
    r"(?<![\d.])(\d{1,3})\s+(?:use[- ]case\s+categor(?:y|ies)|"
    r"使用情境分類|使用场景分类)",
    re.IGNORECASE,
)

OUTREACH_STALE_ROUTE_RE = re.compile(
    r"(?:\b7\s*[- ]?\s*stages?\b|7\s*(?:階段|阶段))|"
    r"(?:(?:8[- ]stage|8\s*(?:個|个)?\s*(?:階段|阶段)|Stage\s*0).{0,120}"
    r"multi-agent\s+production)|"
    r"(?:Stage\s*8\s*(?:\([^)]*(?:production|multi-agent|multi agent|多代理|多\s*Agent)[^)]*\)|"
    r"(?:的|：|:|-)\s*(?:production|multi-agent|multi agent|多代理|多\s*Agent)))",
    re.IGNORECASE,
)

OUTREACH_POPULARITY_METRIC_RE = re.compile(
    r"(?:[★⭐]\s*(?:≈|~)?\s*\*{0,2}\d[\d,.]*[kKmM]?\+?\*{0,2})|"
    r"(?<![\w.])\*{0,2}\d[\d,.]*[kKmM]?\+?\*{0,2}\s*"
    r"(?:stars?|stargazers?|views?|(?:unique\s+)?visitors?|forks?|clones?|"
    r"(?:unique\s+)?cloners?)\b",
    re.IGNORECASE,
)


def parse_catalog(path: Path) -> dict[int, int]:
    """Return the number of real entry headings in each numbered section."""
    entries: dict[int, int] = {}
    section: int | None = None
    lines = path.read_text(encoding="utf-8").splitlines()

    for index, line in enumerate(lines):
        section_match = SECTION_RE.match(line)
        if section_match:
            section = int(section_match.group(1))
            entries.setdefault(section, 0)
            continue
        if line.startswith("## "):
            section = None
            continue
        if not ENTRY_RE.match(line) or section is None:
            continue

        previous = index - 1
        while previous >= 0 and not lines[previous].strip():
            previous -= 1
        if previous >= 0 and NOT_AN_ENTRY in lines[previous]:
            continue
        entries[section] = entries.get(section, 0) + 1

    return entries


def advertised_catalog_totals(line: str) -> list[int]:
    """Return reader-facing catalog-size claims found on one line."""
    if not CATALOG_CONTEXT_RE.search(line):
        return []
    return [int(match.group(1)) for match in ADVERTISED_TOTAL_RE.finditer(line)]


def advertised_public_inventory_totals(line: str) -> list[int]:
    """Return volatile exact, approximate, or ``NN+`` public inventory claims."""
    plain_text = re.sub(r"<[^>]+>", " ", line)
    matches = (
        list(VOLATILE_PUBLIC_TOTAL_RE.finditer(plain_text))
        + list(APPROX_PUBLIC_TOTAL_RE.finditer(plain_text))
        + list(CATEGORY_PUBLIC_TOTAL_RE.finditer(plain_text))
    )
    return [int(match.group(1)) for match in matches]


def has_stale_outreach_route(line: str) -> bool:
    """Return whether active outreach maps an old stage count or Stage 8 role."""
    return bool(OUTREACH_STALE_ROUTE_RE.search(line))


def has_outreach_popularity_metric(line: str) -> bool:
    """Return whether outreach freezes a popularity or traffic snapshot."""
    return bool(OUTREACH_POPULARITY_METRIC_RE.search(line))


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--quiet", action="store_true")
    args = parser.parse_args()

    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except (AttributeError, ValueError):
        pass

    problems: list[str] = []
    counts: dict[str, dict[int, int]] = {}

    for relative in CATALOGS:
        path = REPO_ROOT / relative
        sections = parse_catalog(path)
        counts[relative] = sections
        expected_sections = list(range(1, 18))
        if sorted(sections) != expected_sections:
            problems.append(
                f"{relative}: numbered sections are {sorted(sections)}, "
                f"expected {expected_sections}"
            )
        if not args.quiet:
            print(f"{relative}: {sum(sections.values())} entries across {len(sections)} sections")

        for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
            if INDEX_COUNT_RE.match(line):
                problems.append(
                    f"{relative}:{line_number}: remove the per-category count from the index"
                )

    if counts:
        first_relative = CATALOGS[0]
        reference = counts[first_relative]
        for relative in CATALOGS[1:]:
            if counts[relative] != reference:
                problems.append(
                    f"{relative}: section entry counts differ from {first_relative}: "
                    f"{counts[relative]} != {reference}"
                )

    for path in sorted(REPO_ROOT.rglob("*.md")):
        relative_parts = path.relative_to(REPO_ROOT).parts
        if any(part in SCAN_EXCLUDE_DIRS for part in relative_parts):
            continue
        if path.name.startswith("CHANGELOG"):
            continue
        relative = path.relative_to(REPO_ROOT).as_posix()
        is_outreach = relative_parts[:2] == (".github", "outreach")
        for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
            claims = sorted(
                set(
                    advertised_catalog_totals(line)
                    + advertised_public_inventory_totals(line)
                )
            )
            if claims:
                problems.append(
                    f"{relative}:{line_number}: remove advertised public inventory total(s) {claims}; "
                    "the machine count is intentionally not reader-facing"
                )
            if is_outreach and has_stale_outreach_route(line):
                problems.append(
                    f"{relative}:{line_number}: update the outreach route: Stage 7 covers "
                    "multi-agent production; Stage 8 covers Agent Interfaces"
                )
            if is_outreach and has_outreach_popularity_metric(line):
                problems.append(
                    f"{relative}:{line_number}: remove the cached popularity or traffic metric; "
                    "recheck live target rules and links instead"
                )

    if problems:
        print("\n".join(f"❌ {problem}" for problem in problems))
        print(f"\nFound {len(problems)} catalog-integrity problem(s).")
        return 1

    total = sum(next(iter(counts.values())).values()) if counts else 0
    print(
        f"\n✓ Catalog structure consistent across three locales "
        f"({total} machine-counted entries; no public total claim)."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
