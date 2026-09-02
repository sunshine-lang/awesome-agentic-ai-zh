#!/usr/bin/env python3
"""check-locale-links.py — keep mirror pages linking to their OWN locale.

An `.en.md` / `.zh-Hans.md` page that links to a bare `foo.md` sends its reader
to the zh-TW canonical, even when `foo.en.md` / `foo.zh-Hans.md` exists right
next to it. That silently drops non-Traditional readers onto a page they may not
read. Nothing else in CI catches this: check-anchors only validates that targets
resolve, and sync-language-switchers only manages the switcher row.

Usage:
    python scripts/check-locale-links.py            # report (exit 1 if any found)
    python scripts/check-locale-links.py --apply    # rewrite them in place
    python scripts/check-locale-links.py --quiet     # only the summary line

Rule (deliberately conservative — a link is only rewritten when ALL hold):
  1. the file is a mirror (`*.en.md` or `*.zh-Hans.md`),
  2. the link target is a relative `.md` path with no locale suffix,
  3. the same-locale sibling of that target EXISTS on disk,
  4. the line is not the language-switcher row (which links across locales on
     purpose), and the link is not inside a fenced code block,
  5. if the link carries an `#anchor`, that anchor must ALSO exist in the
     sibling. Headings are translated, so a zh-TW anchor does not survive a
     retarget to `.en.md` — rewriting those produced 5 dead links in the first
     run of this sweep. When the anchor does not resolve, the canonical link is
     the only correct one and is left alone.
Anything failing a condition is left alone — cross-locale links can be
deliberate, and a target whose sibling does not exist must keep pointing at the
canonical.
"""

import argparse
import importlib.util
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from md_fences import strip_code_blocks  # noqa: E402

REPO_ROOT = Path(__file__).resolve().parent.parent
EXCLUDE_DIRS = {".git", ".github", ".claude", ".ai", "_build", "node_modules", "book", ".venv"}
LOCALES = [(".en.md", "*.en.md"), (".zh-Hans.md", "*.zh-Hans.md")]

# [display](target[#anchor]) — relative .md targets only (no scheme, no protocol)
LINK_RE = re.compile(r"\[(`?)([^\]\n]*?)\1\]\((?!https?:|mailto:)([^)\s#]+?\.md)((?:#[^)\s]*)?)\)")
# Lines that deliberately offer BOTH locales, so a bare `.md` target on them is
# correct and must not be retargeted:
#   - the language-switcher row at the top of every mirror page, and
#   - inline dual citations like "see FILE (zh) or FILE (en)". CONTRIBUTING.en.md
#     uses that form; an early version of this script "fixed" the (zh) link to
#     point at the English file, so both links landed on the same page and the
#     zh-TW style guide became unreachable from that bullet.
SWITCHER_RE = re.compile(
    r"繁體中文|简体中文|\[English\]|\*\*English\*\*"
    r"|[(（]\s*zh(-Hans|-TW)?\s*[)）].*[(（]\s*en\s*[)）]"
)
HEADING_RE = re.compile(r"^#{1,6}\s+(.*?)\s*$")

# Reuse the repo's canonical slugger instead of re-implementing it. A second
# copy WILL drift: an early version here collapsed consecutive whitespace and
# stripped edge hyphens, so `## 5.7 — Title` slugged to `57-title` while
# check-anchors.py (correctly, per github-slugger) produces `57--title`. That
# made rule 5 silently under-detect exactly the anchored links it exists for.
_CA_SPEC = importlib.util.spec_from_file_location(
    "check_anchors", Path(__file__).with_name("check-anchors.py")
)
_check_anchors = importlib.util.module_from_spec(_CA_SPEC)
_CA_SPEC.loader.exec_module(_check_anchors)
slugify = _check_anchors.slugify


def anchors_of(fp: Path) -> set[str]:
    """All heading anchors in a markdown file, ignoring fenced code."""
    found = set()
    for line in strip_code_blocks(
        fp.read_text(encoding="utf-8"), source=str(fp)
    ).split("\n"):
        m = HEADING_RE.match(line)
        if m:
            found.add(slugify(m.group(1)))
    return found


def iter_mirror_files(root: Path):
    for suffix, glob in LOCALES:
        for fp in sorted(root.rglob(glob)):
            # Match on the path RELATIVE to the repo root. Testing fp.parts
            # instead matches directory names anywhere in the absolute path, so
            # a checkout living under e.g. `.claude/worktrees/<name>/` excludes
            # every file in the repo and this gate reports a silent all-clear —
            # green locally for the wrong reason, while CI (whose runner path has
            # no excluded component) is the only place it actually runs.
            if any(part in EXCLUDE_DIRS for part in fp.relative_to(root).parts):
                continue
            yield suffix, fp


def scan_file(suffix: str, fp: Path):
    """Yield (line_no, whole_link, target, fixed_target) for each fixable link."""
    # Fenced code blanked by the shared parser (md_fences), not a local toggle —
    # see #95/#97. This gate REWRITES link targets, so a false positive creates a
    # dead link; a sample link inside a ```markdown template must stay untouched.
    lines = strip_code_blocks(
        fp.read_text(encoding="utf-8"), source=str(fp)
    ).split("\n")
    for i, line in enumerate(lines, start=1):
        if SWITCHER_RE.search(line):
            continue
        for m in LINK_RE.finditer(line):
            target, anchor = m.group(3), m.group(4)
            if target.endswith(".en.md") or target.endswith(".zh-Hans.md"):
                continue
            sibling_rel = target[: -len(".md")] + suffix
            sibling = fp.parent / sibling_rel
            if not sibling.exists():
                continue  # no same-locale sibling — canonical link is correct
            if anchor:
                # Headings are translated: a zh-TW anchor will not exist in the
                # .en.md sibling. Retargeting those creates dead links.
                if anchor.lstrip("#") not in anchors_of(sibling):
                    continue
            yield i, m.group(0), target, sibling_rel


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--apply", action="store_true", help="rewrite links in place")
    ap.add_argument("--quiet", action="store_true", help="summary line only")
    args = ap.parse_args()

    # Report contains ✓ and CJK paths; make stdout UTF-8 so a Windows console
    # (cp950/cp1252) can print it. CI on ubuntu-latest is already UTF-8.
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except (AttributeError, ValueError):
        pass

    total = 0
    files_touched = 0
    for suffix, fp in iter_mirror_files(REPO_ROOT):
        hits = list(scan_file(suffix, fp))
        if not hits:
            continue
        total += len(hits)
        files_touched += 1
        rel = fp.relative_to(REPO_ROOT).as_posix()
        if not args.quiet:
            print(f"--- {rel} ({len(hits)})")
            for line_no, whole, target, fixed in hits[:3]:
                print(f"    {line_no}: {target}  ->  {fixed}")
            if len(hits) > 3:
                print(f"    ... +{len(hits) - 3} more")
        if args.apply:
            text = fp.read_text(encoding="utf-8")
            for _, whole, target, fixed in hits:
                # Replace only this exact link, preserving display text + anchor.
                text = text.replace(whole, whole.replace(f"]({target}", f"]({fixed}"), 1)
            fp.write_text(text, encoding="utf-8")

    verb = "Rewrote" if args.apply else "Found"
    print(f"\n{verb} {total} cross-locale link(s) in {files_touched} mirror file(s).")
    if total and not args.apply:
        print("Mirror pages should link to their own locale when a sibling exists.")
        print("Fix with: python scripts/check-locale-links.py --apply")
        return 1
    if not total:
        print("✓ All mirror links point at their own locale.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
