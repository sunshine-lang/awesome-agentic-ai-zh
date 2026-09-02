#!/usr/bin/env python3
"""check-mirror-parity.py — a mirror must not silently lose content the canonical has.

The recurring failure in this repo is not a bad translation, it is a MISSING one: a
section, a code sample, a blockquote that exists in the zh-TW canonical and simply
never made it into `.en.md` / `.zh-Hans.md`. In a single 2026-08 sweep that class
turned up five separate times — the catalog's composition section, the A2/A3 entry
conditions, five expected-output blocks in stages/01, the entire free local Ollama
path in a stage-3 example, and 202 blockquote lines across 21 example READMEs.

Nothing caught any of it. check-anchors only proves links resolve, check-locale-links
only proves they point at the right locale, zh-hans-localize only checks vocabulary,
check-hans-chars only checks characters. All of them are happy with a mirror that is
simply shorter.

So this gate compares STRUCTURE per trio and fails when a mirror has FEWER of
something than the canonical.

It is a RATCHET, not an absolute check. The repo has real, legitimate deltas (a
translation may merge two tables, an English page may drop a Chinese-only video list
that has no English equivalent). Those live in a baseline file. The gate fails only
when a deficit gets WORSE than its baseline or appears somewhere new. Deficits can
therefore only shrink over time, and shrinking one without updating the baseline is
harmless — `--update-baseline` re-snapshots and is meant to be run when you have
genuinely closed a gap.

WHAT THIS GATE DOES NOT DO — read before trusting it alone. It counts, it does not
compare identity. A mirror that swaps in a *wrong* blockquote of the same shape still
passes: this proves "5 blockquote lines are present", never "the right 5". Reviewing a
port still means diffing the actual bullets, URLs and anchors against the canonical.
Likewise, changing `mirror-parity-baseline.json` is how a real regression would be
silenced, so any diff touching that file warrants full review regardless of its size.

Usage:
    python scripts/check-mirror-parity.py                 # exit 1 on a new/worse deficit
    python scripts/check-mirror-parity.py --report        # show every current deficit
    python scripts/check-mirror-parity.py --update-baseline
"""

import argparse
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from md_fences import code_line_flags, fence_marker_count  # noqa: E402

REPO_ROOT = Path(__file__).resolve().parent.parent
BASELINE = REPO_ROOT / "scripts" / "mirror-parity-baseline.json"
LOCALES = {"en": ".en.md", "zh-Hans": ".zh-Hans.md"}
SKIP_DIR_PARTS = {".git", ".claude", ".ai", "_build", "_site", "node_modules", "book", "archives"}
SKIP_FILES = {"CHANGELOG.md"}

IMAGE_RE = re.compile(r"!\[[^\]]*\]\(")


def metrics(path: Path) -> dict:
    """Count reader-visible structural elements, ignoring anything inside code fences."""
    h2 = h3 = blockquote = fences = images = table_rows = 0
    # Both "which lines are code" and "how many fence markers" come from the
    # shared parser (md_fences). The local version tracked the marker CHARACTER —
    # better than a plain toggle — but still ignored the two rules #95 turned up:
    # a closer may not carry an info string, and it must be at least as long as
    # its opener, so a nested ```python counted as two markers it should not.
    #
    # fence_marker_count rather than counting code-run boundaries: two blocks
    # with no blank line between them are ONE contiguous run, so boundaries
    # report 1 block where there are 2 — and in this gate a metric that drops on
    # one side of a trio is either a false deficit or a masked real one.
    text = path.read_text(encoding="utf-8")
    lines = text.split("\n")
    flags = code_line_flags(text)
    fences = fence_marker_count(text)
    for line, in_code in zip(lines, flags):
        if in_code:
            continue
        if line.startswith("## "):
            h2 += 1
        elif line.startswith("### "):
            h3 += 1
        if line.startswith("> "):
            blockquote += 1
        if line.lstrip().startswith("|"):
            table_rows += 1
        images += len(IMAGE_RE.findall(line))
    return {
        "h2": h2, "h3": h3, "blockquote": blockquote,
        "fences": fences // 2, "images": images, "table_rows": table_rows,
    }


def trios():
    """Yield (rel_canonical, canonical_path, {locale: mirror_path}) for complete trios."""
    for canon, mirrors, complete in _scan():
        if complete:
            yield canon.relative_to(REPO_ROOT).as_posix(), canon, mirrors


def _scan():
    """Yield (canonical_path, {locale: mirror_path}, is_complete) for every canonical."""
    for canon in sorted(REPO_ROOT.rglob("*.md")):
        # Match on the path RELATIVE to REPO_ROOT. Matching canon.parts tests
        # the ABSOLUTE path, and SKIP_DIR_PARTS contains ".claude" — so from a
        # checkout under `.claude/worktrees/<name>/` every file is skipped. Here
        # the trio-count ratchet turns that into a loud failure rather than a
        # silent pass, but the walker is still blind. Same bug as the 2026-08-02
        # sweep across six other gates; pinned by test_repo_scan_excludes.py.
        if any(p in SKIP_DIR_PARTS for p in canon.relative_to(REPO_ROOT).parts):
            continue
        name = canon.name
        if name in SKIP_FILES or name.endswith((".en.md", ".zh-Hans.md")):
            continue
        stem = str(canon)[: -len(".md")]
        mirrors = {loc: Path(stem + suf) for loc, suf in LOCALES.items()}
        yield canon, mirrors, all(m.exists() for m in mirrors.values())


def partial_trios():
    """Canonicals with SOME but not all mirrors — i.e. a mirror was deleted.

    Deleting a mirror is 100% content loss, yet the deficit check cannot see it:
    an incomplete trio simply stops being compared. A canonical with zero mirrors
    is legitimate (examples/stage-1/04-cross-provider has never been translated),
    but a canonical with exactly one is a file that went missing.
    """
    out = []
    for canon, mirrors, complete in _scan():
        if complete:
            continue
        present = [loc for loc, m in mirrors.items() if m.exists()]
        if present:
            missing = [loc for loc, m in mirrors.items() if not m.exists()]
            out.append((canon.relative_to(REPO_ROOT).as_posix(), present, missing))
    return out


def deficits() -> dict:
    """{rel: {locale: {metric: how many FEWER than canonical}}} — only shortfalls."""
    out = {}
    for rel, canon, mirrors in trios():
        cm = metrics(canon)
        for loc, mp in mirrors.items():
            mm = metrics(mp)
            short = {k: cm[k] - mm[k] for k in cm if mm[k] < cm[k]}
            if short:
                out.setdefault(rel, {})[loc] = short
    return out


def load_baseline() -> dict:
    if not BASELINE.exists():
        return {}
    return json.loads(BASELINE.read_text(encoding="utf-8")).get("deficits", {})


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--report", action="store_true", help="list every current deficit")
    ap.add_argument("--update-baseline", action="store_true",
                    help="re-snapshot; run this after genuinely closing a gap")
    args = ap.parse_args()
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except (AttributeError, ValueError):
        pass

    cur = deficits()
    n_trios = sum(1 for _ in trios())

    if args.update_baseline:
        total = sum(v for locs in cur.values() for m in locs.values() for v in m.values())
        BASELINE.write_text(
            json.dumps(
                {
                    "_comment": (
                        "Accepted mirror-vs-canonical structural deficits. This is a RATCHET "
                        "baseline: check-mirror-parity.py fails when a deficit grows or appears "
                        "somewhere new, never when one shrinks. Regenerate with "
                        "`python scripts/check-mirror-parity.py --update-baseline` ONLY after "
                        "genuinely closing a gap — never to silence a new one."
                    ),
                    "trios": n_trios,
                    "total_deficit": total,
                    "deficits": cur,
                },
                ensure_ascii=False, indent=2, sort_keys=True,
            ) + "\n",
            encoding="utf-8",
        )
        print(f"baseline written: {len(cur)} trio(s) with deficits, {total} total across {n_trios} trios")
        return 0

    base = load_baseline()

    if args.report:
        total = sum(v for locs in cur.values() for m in locs.values() for v in m.values())
        print(f"{n_trios} trio(s) checked; {len(cur)} with a deficit, {total} total")
        for rel in sorted(cur):
            for loc in sorted(cur[rel]):
                print(f"  {rel} [{loc}]: {cur[rel][loc]}")
        return 0

    regressions = []
    for rel, locs in cur.items():
        for loc, short in locs.items():
            allowed = base.get(rel, {}).get(loc, {})
            for metric, n in short.items():
                if n > allowed.get(metric, 0):
                    regressions.append((rel, loc, metric, n, allowed.get(metric, 0)))

    print(f"checked {n_trios} trio(s) against the parity baseline")

    # A deleted mirror is total content loss but produces NO deficit — the trio
    # just stops being compared. Catch it two ways: a half-present trio, and a
    # drop in the total trio count vs the baseline.
    partial = partial_trios()
    for rel, present, missing in partial:
        print(f"❌ {rel}: has {present} but is MISSING {missing} — a mirror was deleted")
    baseline_trios = 0
    if BASELINE.exists():
        baseline_trios = json.loads(BASELINE.read_text(encoding="utf-8")).get("trios", 0)
    if baseline_trios and n_trios < baseline_trios:
        print(f"❌ complete trios dropped {baseline_trios} -> {n_trios}: a canonical or both "
              f"its mirrors were removed")
        partial = partial or [("<trio count>", [], [])]

    if regressions or partial:
        for rel, loc, metric, n, was in regressions:
            print(f"❌ {rel} [{loc}]: {metric} is {n} short of the canonical (baseline allowed {was})")
        print(f"\nFound {len(regressions)} deficit regression(s) and "
              f"{len(partial)} missing-mirror problem(s).")
        print("A mirror lost content the canonical has. Port the missing section, or —")
        print("if the difference is genuinely correct — run --update-baseline and say why in CHANGELOG.")
        return 1

    print("\n✓ No mirror lost content relative to the canonical (vs baseline).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
