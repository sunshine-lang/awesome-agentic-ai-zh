#!/usr/bin/env python3
"""check-hans-chars.py — catch Traditional characters that survived into zh-Hans mirrors.

`scripts/zh-hans-localize.py` deliberately checks only two things: Taiwan VOCABULARY
(檔案 -> 文件) and quote style (「」 -> ""). Character-level 繁 -> 簡 is assumed to have
already happened upstream, when the mirror was produced with opencc.

That assumption leaves a permanent hole: a Traditional character that was never converted
in the first place is invisible to every gate in this repo, forever. In 2026-08 that hole
was holding 13 real residues — `動手練習` sitting in the middle of a Simplified sentence in
README.zh-Hans.md, `邏輯`/`區別`/`選定` in three stage files, `等正規 MCP` in the catalog,
`用語說明` in RESOURCES — plus a corrupted `对, 应的`. A hand-written list of "Traditional
glyphs to look for" was tried first and was worse than useless: it missed 檔/個/體/專/點
while flagging 叫 (identical in both scripts).

So the check asserts the actual invariant instead of approximating it:

    converting a zh-Hans file with opencc t2s must be a no-op

If conversion changes a character, that character was Traditional. No curated list, no
guessing, no drift.

Why `t2s` and not `tw2s`: `tw2s` maps the Taiwan variant 么 -> 幺, so running it over
already-correct Simplified text mangles 什么 -> 什幺 and reports ~880 false positives.
`t2s` leaves 什么 alone and still converts 動手練習 -> 动手练习.

Exclusions (all deliberate, each one a real construct in this repo):
  - fenced code blocks and inline `code` — may legitimately show zh-TW sample text
  - markdown link TARGETS `](...)` — an anchor pointing at a zh-TW heading must keep that
    heading's Traditional spelling or the link breaks
  - the literal 繁體中文 — the proper name of the other locale, in switcher rows (68x)
  - shields.io badge lines — the badge block is byte-identical across all three READMEs by
    design; localizing it in only one would create the very drift this gate exists to stop
  - resources/style-guide.zh-Hans.md — its conversion table's left column is Traditional
    on purpose ("write 项目, not 專案")

Usage:
    python scripts/check-hans-chars.py            # report, exit 1 on residue
    python scripts/check-hans-chars.py --quiet     # summary only
    python scripts/check-hans-chars.py --require-opencc   # fail if opencc is missing (CI)
"""

import argparse
import glob
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from md_fences import strip_code_blocks  # noqa: E402

REPO_ROOT = Path(__file__).resolve().parent.parent

INLINE_CODE_RE = re.compile(r"`[^`\n]*`")
LINK_TARGET_RE = re.compile(r"\]\([^)]*\)")
BADGE_MARKER = "img.shields.io/badge"
LOCALE_PROPER_NAME = "繁體中文"
TABLE_ROW_RE = re.compile(r"^\s*\|")
# Files with intentionally-Traditional content, scoped to the construct that needs
# it rather than the whole file. style-guide.zh-Hans.md documents the conversion
# rules, so its table's LEFT column is Traditional on purpose ("write 项目, not
# 專案") — but only the table rows. Exempting the entire file would mean prose
# added anywhere else in it is invisible to this gate forever, which is the exact
# class of blind spot this script exists to remove.
EXEMPT_FILES = {"resources/style-guide.zh-Hans.md": TABLE_ROW_RE}
SKIP_DIR_PARTS = {".git", ".claude", "_build", "_site", "node_modules", "book", ".ai"}


def scrub(line: str) -> str:
    """Strip the spans where Traditional characters are legitimate."""
    line = LINK_TARGET_RE.sub("]()", line)
    line = INLINE_CODE_RE.sub("", line)
    return line.replace(LOCALE_PROPER_NAME, "")


def residue_in_file(fp: Path, convert, exempt_line=None) -> list:
    """Return [(lineno, offending_chars, line)] for one file.

    exempt_line: optional compiled regex; matching lines are skipped. Used to
    scope a per-file exemption to one construct instead of the whole file.
    """
    out = []
    # Fenced code is blanked by the shared parser (md_fences) rather than by a
    # local toggle. The local toggle got the rules wrong — see #95/#97 — and for
    # THIS gate the consequence is a false positive that blocks CI: a nested
    # ```python whose body holds a Traditional-character comment gets scanned as
    # prose and reported as residue. Blanking keeps line numbers intact.
    text = strip_code_blocks(fp.read_text(encoding="utf-8"), source=str(fp))
    for i, line in enumerate(text.split("\n"), 1):
        if BADGE_MARKER in line:
            continue
        if exempt_line is not None and exempt_line.match(line):
            continue
        stripped = scrub(line)
        converted = convert(stripped)
        if converted == stripped:
            continue
        # Same length is guaranteed for t2s char mapping, but do not rely on it.
        bad = "".join(sorted({a for a, b in zip(stripped, converted) if a != b}))
        if bad:
            out.append((i, bad, line.strip()))
    return out


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--quiet", action="store_true")
    ap.add_argument(
        "--require-opencc",
        action="store_true",
        help="exit 1 if opencc is unavailable (use in CI so the check cannot silently skip)",
    )
    args = ap.parse_args()
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except (AttributeError, ValueError):
        pass

    try:
        import opencc
    except ImportError:
        msg = (
            "opencc not installed — cannot verify character-level 繁→簡.\n"
            "  install: pip install opencc-python-reimplemented"
        )
        if args.require_opencc:
            print(f"❌ {msg}")
            return 1
        print(f"⚠️  skipped: {msg}")
        return 0

    convert = opencc.OpenCC("t2s").convert

    problems = []
    checked = 0
    for name in sorted(glob.glob("**/*.zh-Hans.md", recursive=True, root_dir=REPO_ROOT)):
        rel = Path(name).as_posix()
        if any(p in SKIP_DIR_PARTS for p in Path(name).parts):  # abs-parts-ok: glob(root_dir=REPO_ROOT) yields relative names
            continue
        checked += 1
        for lineno, bad, text in residue_in_file(
            REPO_ROOT / name, convert, EXEMPT_FILES.get(rel)
        ):
            problems.append((rel, lineno, bad, text))

    if not args.quiet:
        print(f"checked {checked} zh-Hans file(s) for Traditional-character residue")

    if problems:
        for rel, lineno, bad, text in problems:
            print(f"❌ {rel}:{lineno}: Traditional character(s) [{bad}] → {convert(bad)}")
            print(f"     {text[:120]}")
        print(f"\nFound {len(problems)} line(s) with Traditional residue.")
        print("These are characters that were never converted when the mirror was made;")
        print("zh-hans-localize.py checks vocabulary and quotes only and cannot see them.")
        return 1

    print("\n✓ No Traditional-character residue in zh-Hans mirrors.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
