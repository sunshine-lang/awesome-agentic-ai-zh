#!/usr/bin/env python3
"""
sync-language-switchers.py — 統一三語檔案頂部的 language switcher

3 語版 repo 結構：
  <file>.md         = zh-TW canonical
  <file>.en.md      = English mirror
  <file>.zh-Hans.md   = zh-Hans mirror

每個檔案的頂部都需要 3-way switcher，把目前 active 的語言粗體、其他兩個連結。

執行：
  python scripts/sync-language-switchers.py            # dry run，列出要改的
  python scripts/sync-language-switchers.py --apply    # 實際寫入檔案
  python scripts/sync-language-switchers.py --check    # CI 用，發現不同步就 exit 1

支援兩種 switcher 格式：
  1. README.md 用 <div align="right">...</div> 區塊
  2. 一般檔案用 `> [...](./...) | **...**` 一行 blockquote
"""

import argparse
import re
import sys
from pathlib import Path
from typing import Optional

# Force UTF-8 stdout on Windows (cp950 default can't handle CJK)
if sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

REPO_ROOT = Path(__file__).resolve().parent.parent

# 哪些 .md 檔需要 switcher（zh-TW canonical）
# 排除：DESIGN.md、CONTRIBUTORS.md、CONTRIBUTING.md（內部 / 規則性質）
# 排除：.github/、scripts/、book/
EXCLUDE_PATHS = {
    "branches/DESIGN.md",
    "stages/DESIGN.md",
    "CONTRIBUTORS.md",  # 名單性質，不一定有 zh-Hans 翻譯
    # Landing pages: mkdocs-only (index.md is the site home; GitHub shows
    # README.md, not index.md). They use Material's header language selector,
    # so the GitHub-style inline switcher would be broken + ugly here.
    "index.md",
    "index.en.md",
    "index.zh-Hans.md",
}
EXCLUDE_DIRS = {".github", "scripts", "book", ".ai", ".claude", "node_modules", "_build"}


def find_paired_files() -> list[tuple[Path, Optional[Path], Optional[Path]]]:
    """找所有 (zh-TW, en, zh-Hans) 三檔組合。"""
    triples = []
    for md_path in sorted(REPO_ROOT.rglob("*.md")):
        # 跳過 .en.md / .zh-Hans.md 自己（它們是 mirror，不是 canonical）
        if md_path.name.endswith(".en.md") or md_path.name.endswith(".zh-Hans.md"):
            continue
        # 跳過 EXCLUDE_DIRS
        if any(part in EXCLUDE_DIRS for part in md_path.relative_to(REPO_ROOT).parts):
            continue
        # 跳過 EXCLUDE_PATHS
        rel = md_path.relative_to(REPO_ROOT).as_posix()
        if rel in EXCLUDE_PATHS:
            continue

        en_path = md_path.with_suffix(".en.md")
        zh_hans_path = md_path.with_suffix(".zh-Hans.md")
        if not en_path.exists():
            en_path = None
        if not zh_hans_path.exists():
            zh_hans_path = None

        # 至少要有 zh-TW + 一個 mirror 才算需要 switcher
        if en_path is None and zh_hans_path is None:
            continue

        triples.append((md_path, en_path, zh_hans_path))
    return triples


def make_readme_switcher(active: str, has_en: bool, has_zh_hans: bool) -> str:
    """README.md / README.en.md / README.zh-Hans.md 用的 div 區塊 switcher。"""
    parts = []
    label_map = {"zh-TW": "繁體中文", "en": "English", "zh-Hans": "简体中文"}

    for lang in ("zh-TW", "zh-Hans", "en"):
        if lang == "zh-Hans" and not has_zh_hans:
            continue
        if lang == "en" and not has_en:
            continue
        label = label_map[lang]
        if lang == active:
            parts.append(f"<strong>{label}</strong>")
        else:
            href_map = {"zh-TW": "./README.md", "en": "./README.en.md", "zh-Hans": "./README.zh-Hans.md"}
            parts.append(f'<a href="{href_map[lang]}">{label}</a>')

    return f'<div align="right">\n  {" | ".join(parts)}\n</div>'


def make_inline_switcher(active: str, base_name: str, has_en: bool, has_zh_hans: bool) -> str:
    """一般檔 blockquote 一行 switcher。"""
    parts = []
    label_map = {"zh-TW": "繁體中文", "en": "English", "zh-Hans": "简体中文"}

    for lang in ("zh-TW", "zh-Hans", "en"):
        if lang == "zh-Hans" and not has_zh_hans:
            continue
        if lang == "en" and not has_en:
            continue
        label = label_map[lang]
        if lang == active:
            parts.append(f"**{label}**")
        else:
            href_map = {
                "zh-TW": f"./{base_name}.md",
                "en": f"./{base_name}.en.md",
                "zh-Hans": f"./{base_name}.zh-Hans.md",
            }
            parts.append(f"[{label}]({href_map[lang]})")

    return "> " + " | ".join(parts)


def detect_switcher_block(content: str) -> tuple[Optional[int], Optional[int], str]:
    """
    找出檔案頂部的 switcher 區塊位置。
    回傳 (start_line, end_line, kind) 或 (None, None, '')。
    kind = 'div' 或 'inline' 或 ''。
    """
    lines = content.split("\n")

    # 嘗試找 <div align="right">...</div> 區塊
    for i, line in enumerate(lines):
        if line.strip().startswith('<div align="right">'):
            # 找 </div>
            for j in range(i, min(i + 5, len(lines))):
                if "</div>" in lines[j]:
                    return i, j, "div"
            break  # 找到 <div> 但找不到 </div>，放棄

    # 嘗試找 inline `> [English](./xxx.en.md) | **繁體中文**` 之類
    for i, line in enumerate(lines[:10]):  # 只看前 10 行
        if line.startswith("> ") and ("](./") in line and (
            "繁體中文" in line or "English" in line or "简体中文" in line
        ):
            return i, i, "inline"

    return None, None, ""


# Locale tokens that appear inside a switcher line. 繁体中文 (simplified glyphs)
# is included because some old/mirror files wrote "Traditional Chinese" that way.
LOCALE_TOKENS = ("繁體中文", "繁体中文", "简体中文", "English")

# Known placeholder/stub markers that stand in for a real switcher
# (e.g. `> **繁體中文** | (zh-Hans / en mirror defer 中)`).
STUB_MARKERS = ("mirror defer",)


def _rel(path: Path) -> str:
    """repo-relative path for logging; falls back to the name for temp/selftest files."""
    try:
        return path.relative_to(REPO_ROOT).as_posix()
    except ValueError:
        return path.name


def _first_h1(lines: list[str]) -> Optional[int]:
    """Index of the first `# ` H1 line, or None."""
    for i, line in enumerate(lines):
        if line.startswith("# "):
            return i
    return None


def _looks_like_switcher(line: str) -> bool:
    """
    True if a single line is a switcher-ish line in ANY form — canonical,
    old/reordered, no-`./`-prefix, bare (no `> `), or a known stub. This is
    deliberately broader than detect_switcher_block (which only recognises the
    canonical inline / div forms) so the ADD path can strip whatever switcher-
    like junk is already there instead of leaving a double switcher.

    Rule: a known stub marker, OR a line containing `|` plus >= 2 distinct
    locale tokens AND at least one switcher-specific shape (a markdown link to
    a `.md` mirror, or a **bold** locale = the active-language marker).

    The >=2-locale threshold keeps prose that merely mentions "English" (with
    an unrelated `|`) from matching. The extra link/bold requirement keeps a
    markdown TABLE row whose cells happen to be locale names — e.g.
    `| English | 简体中文 | notes |` — from being misread as a switcher and
    silently deleted (a table row has no `](...md)` link and no `**locale**`).
    Every real 3-/2-way switcher bolds its active locale and/or links the
    others; the only single-locale case (the `mirror defer` placeholder) is
    caught by the stub branch above.
    """
    s = line.strip()
    if not s:
        return False
    if any(marker in s for marker in STUB_MARKERS):
        return True
    # strip an optional leading blockquote marker
    body = s
    if body.startswith(">"):
        body = body[1:].lstrip()
    if "|" not in body:
        return False
    if sum(1 for tok in LOCALE_TOKENS if tok in body) < 2:
        return False
    has_link = re.search(r"\[[^\]]+\]\([^)]*\.md\)", body) is not None
    has_bold_locale = any(f"**{tok}**" in body for tok in LOCALE_TOKENS)
    return has_link or has_bold_locale


def update_file(path: Path, lang: str, has_en: bool, has_zh_hans: bool, apply: bool) -> bool:
    """更新單一檔案的 switcher。回傳 True 表示有改動需要寫入。"""
    content = path.read_text(encoding="utf-8")
    lines = content.split("\n")

    # README 用 div block（位置在檔案最頂、banner/H1 之前），一般檔用 inline。
    # README 的 div 偵測/替換歷史上是正確的；本次回報的 double-switcher 缺陷
    # 全部發生在非-README inline 檔（stages/08-* x3, stages/04-* x2），故
    # README 走原本未改動的 detect→ADD/UPDATE 流程以保證對乾淨 repo 零差異，
    # inline 走下方重建頭部的新邏輯（會移除任何 switcher-ish 殘行）。
    is_readme = path.name.startswith("README")

    if is_readme:
        new_switcher = make_readme_switcher(lang, has_en, has_zh_hans)
        start, end, kind = detect_switcher_block(content)

        if start is None:
            for i, line in enumerate(lines):
                if line.startswith("# "):
                    new_lines = (
                        lines[: i + 1] + [""] + new_switcher.split("\n") + [""] + lines[i + 1 :]
                    )
                    new_content = "\n".join(new_lines)
                    if apply:
                        path.write_text(new_content, encoding="utf-8")
                    print(f"[ADD] {_rel(path)} ← (no existing switcher, inserted after H1)")
                    return True
            new_lines = new_switcher.split("\n") + [""] + lines
            new_content = "\n".join(new_lines)
            if apply:
                path.write_text(new_content, encoding="utf-8")
            print(f"[ADD] {_rel(path)} ← (no existing switcher, inserted at top)")
            return True

        old_switcher = "\n".join(lines[start : end + 1])
        if old_switcher.strip() == new_switcher.strip():
            return False
        new_lines = lines[:start] + new_switcher.split("\n") + lines[end + 1 :]
        new_content = "\n".join(new_lines)
        if apply:
            path.write_text(new_content, encoding="utf-8")
        print(f"[UPDATE] {_rel(path)}:{start + 1}")
        print(f"  - {old_switcher[:100]}")
        print(f"  + {new_switcher[:100]}")
        return True

    # ---- non-README inline path: rebuild the head, removing ANY switcher-ish
    #      line(s) and inserting exactly one canonical switcher ----
    name = path.name
    if name.endswith(".en.md"):
        base_name = name[: -len(".en.md")]
    elif name.endswith(".zh-Hans.md"):
        base_name = name[: -len(".zh-Hans.md")]
    else:
        base_name = name[: -len(".md")]
    new_switcher = make_inline_switcher(lang, base_name, has_en, has_zh_hans)

    h1 = _first_h1(lines)
    if h1 is None:
        # no H1: canonical goes at the very top; skip leading blanks / switchers
        cs = 0
        while cs < len(lines) and (
            lines[cs].strip() == "" or _looks_like_switcher(lines[cs])
        ):
            cs += 1
        sw_idx = [i for i in range(cs) if _looks_like_switcher(lines[i])]
        rebuilt = [new_switcher, ""] + lines[cs:]
    else:
        # first real content = first non-blank, non-switcher line after H1
        cs = h1 + 1
        while cs < len(lines) and (
            lines[cs].strip() == "" or _looks_like_switcher(lines[cs])
        ):
            cs += 1
        sw_idx = [i for i in range(h1) if _looks_like_switcher(lines[i])] + [
            i for i in range(h1 + 1, cs) if _looks_like_switcher(lines[i])
        ]
        # keep everything up to & including H1 except stray pre-H1 switcher lines
        prefix = [lines[i] for i in range(h1 + 1) if i == h1 or not _looks_like_switcher(lines[i])]
        rebuilt = prefix + ["", new_switcher, ""] + lines[cs:]

    # already-clean fast path: exactly one switcher-ish line and (stripped) it
    # already equals canonical. Mirrors the pre-fix blank-line-agnostic
    # "no change" predicate so the 59 currently-clean files stay untouched.
    if len(sw_idx) == 1 and lines[sw_idx[0]].strip() == new_switcher.strip():
        return False

    new_content = "\n".join(rebuilt)
    if new_content == content:
        return False
    if apply:
        path.write_text(new_content, encoding="utf-8")

    n = len(sw_idx)
    rel = _rel(path)
    if n == 0:
        print(f"[ADD] {rel} ← (no existing switcher, inserted after H1)")
    elif n >= 2:
        print(
            f"[DEDUP] {rel} ← removed {n} switcher-ish line(s), inserted 1 canonical "
            f"(was a double/multi switcher)"
        )
    else:
        print(f"[UPDATE] {rel} ← replaced non-canonical switcher with canonical")
    return True


def _run_selftest() -> int:
    """
    Regression test for the ADD double-switcher defect. Builds throw-away
    fixtures reproducing every old/stub shape, runs --apply, and asserts:
      * exactly ONE canonical switcher remains (no double),
      * head shape is H1 / blank / switcher / blank / content,
      * a second --apply is a no-op (idempotent),
      * a pre-existing double IS detected as needing change (the --check
        blind spot is closed),
      * an already-canonical file is left untouched.
    """
    import tempfile

    canonical = make_inline_switcher("zh-TW", "08-x", True, True)
    canonical_en = make_inline_switcher("en", "04-x", True, True)
    canonical_hans = make_inline_switcher("zh-Hans", "08-x", True, True)

    H1 = "# Stage X — Title"
    BODY = "⏱ **時間估算**：2-3 週\n\n本文開始。\n"

    # (filename, lang, content, expected_canonical, must_change, must_keep)
    # must_keep = a substring that MUST still be present after --apply
    #             (None = no extra survival assertion)
    cases = [
        # stub placeholder, no links
        ("08-x.md", "zh-TW",
         f"{H1}\n\n> **繁體中文** | (zh-Hans / en mirror defer 中)\n\n{BODY}",
         canonical, True, None),
        # bare line, no `> ` prefix
        ("04-x.en.md", "en",
         f"# Stage 4 — Agent Frameworks\n\n"
         f"[繁體中文](./04-x.md) | [简体中文](./04-x.zh-Hans.md) | **English**\n\n{BODY}",
         canonical_en, True, None),
        # `> ` prefix, locale names, but links without `./`
        ("08-x.zh-Hans.md", "zh-Hans",
         f"{H1}\n\n> [繁体中文](08-x.md) | **简体中文** | [English](08-x.en.md)\n\n{BODY}",
         canonical_hans, True, None),
        # PRE-EXISTING DOUBLE: canonical + orphan stub (the --check blind spot)
        ("08-x.md", "zh-TW",
         f"{H1}\n\n{canonical}\n\n> **繁體中文** | (zh-Hans / en mirror defer 中)\n\n{BODY}",
         canonical, True, None),
        # already-canonical: must NOT change
        ("08-x.md", "zh-TW",
         f"{H1}\n\n{canonical}\n\n{BODY}",
         canonical, False, None),
        # P2 regression: a markdown table whose header cells are locale names,
        # sitting right after H1, must NOT be eaten as a switcher. (No switcher
        # present → ADD inserts canonical; the table header MUST survive.)
        ("08-x.md", "zh-TW",
         f"{H1}\n\n| English | 简体中文 | notes |\n|---|---|---|\n| a | b | c |\n\n{BODY}",
         canonical, True, "| English | 简体中文 | notes |"),
    ]

    failures: list[str] = []
    with tempfile.TemporaryDirectory() as td:
        for idx, (fname, lang, content, want_sw, must_change, must_keep) in enumerate(cases):
            # each case in its own subdir so the filename (hence derived
            # base_name / switcher links) stays exactly `fname`
            case_dir = Path(td) / f"c{idx}"
            case_dir.mkdir()
            p = case_dir / fname
            p.write_text(content, encoding="utf-8")

            changed1 = update_file(p, lang, True, True, apply=True)
            if changed1 != must_change:
                failures.append(
                    f"case{idx} {fname}: first --apply changed={changed1}, expected {must_change}"
                )

            out = p.read_text(encoding="utf-8")
            out_lines = out.split("\n")
            if must_keep is not None and must_keep not in out:
                failures.append(
                    f"case{idx} {fname}: required line was consumed; missing {must_keep!r}"
                )
            sw_lines = [ln for ln in out_lines if _looks_like_switcher(ln)]
            if len(sw_lines) != 1:
                failures.append(
                    f"case{idx} {fname}: expected exactly 1 switcher line, got {len(sw_lines)}: {sw_lines!r}"
                )
            elif sw_lines[0].strip() != want_sw.strip():
                failures.append(
                    f"case{idx} {fname}: switcher = {sw_lines[0]!r}, expected {want_sw!r}"
                )

            # head shape: H1 / "" / switcher / "" / content
            h1i = _first_h1(out_lines)
            if h1i is not None:
                shape_ok = (
                    len(out_lines) > h1i + 3
                    and out_lines[h1i + 1] == ""
                    and out_lines[h1i + 2].strip() == want_sw.strip()
                    and out_lines[h1i + 3] == ""
                )
                if not shape_ok:
                    failures.append(
                        f"case{idx} {fname}: head shape not H1/blank/switcher/blank, got "
                        f"{out_lines[h1i:h1i + 4]!r}"
                    )

            # idempotent: a second --apply must be a no-op
            changed2 = update_file(p, lang, True, True, apply=True)
            if changed2:
                failures.append(f"case{idx} {fname}: second --apply was NOT idempotent")

    if failures:
        print("✗ selftest FAILED:")
        for f in failures:
            print(f"  - {f}")
        return 1
    print(
        f"✓ selftest passed ({len(cases)} cases: stub / bare / no-./ / double / clean / table)."
    )
    return 0


def main():
    parser = argparse.ArgumentParser(description="Sync 3-way language switchers across .md / .en.md / .zh-Hans.md")
    parser.add_argument("--apply", action="store_true", help="actually write changes (default: dry-run)")
    parser.add_argument(
        "--check", action="store_true", help="exit 1 if any switcher is out of sync (CI use)"
    )
    parser.add_argument(
        "--selftest", action="store_true", help="run the double-switcher regression test and exit"
    )
    args = parser.parse_args()

    if args.selftest:
        sys.exit(_run_selftest())

    triples = find_paired_files()
    print(f"Found {len(triples)} canonical zh-TW files with at least one mirror.\n")

    changed = 0
    for zh_tw, en, zh_hans in triples:
        has_en = en is not None
        has_zh_hans = zh_hans is not None

        if update_file(zh_tw, "zh-TW", has_en, has_zh_hans, args.apply):
            changed += 1
        if has_en and update_file(en, "en", has_en, has_zh_hans, args.apply):
            changed += 1
        if has_zh_hans and update_file(zh_hans, "zh-Hans", has_en, has_zh_hans, args.apply):
            changed += 1

    print()
    print("=" * 60)
    print(f"Total {len(triples)} files inspected, {changed} need updating.")

    if args.check:
        sys.exit(1 if changed > 0 else 0)
    elif not args.apply and changed > 0:
        print("\nDry-run mode. Re-run with --apply to write changes.")


if __name__ == "__main__":
    main()
