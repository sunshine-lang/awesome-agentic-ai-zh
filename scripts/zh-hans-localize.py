#!/usr/bin/env python3
"""
zh-Hans mainland-localization pass — part of the mirror process.

The zh-Hans mirrors are produced from the zh-TW canonical via opencc
`tw2s` (character-level 繁→簡 only). `tw2s` does NOT localize Taiwan
vocabulary to Mainland vocabulary, so the mirrors read like
"simplified-character Taiwan Chinese". This script applies a CURATED,
blanket-SAFE Taiwan→Mainland substitution table + mainland quote
convention, so the localization PERSISTS across future mirror regens.

Motivated by + sourced from community PR #18 (Rain120,
"使中文简体更加贴合大陆的阅读习惯"). Each pair below was grep-verified
against the whole zh-Hans corpus to have a single unambiguous meaning
in THIS repo (zero/negligible false positives).

DELIBERATELY EXCLUDED (context-sensitive — a blanket map corrupts them;
needs OpenCC `tw2sp` curated dict or per-occurrence human judgment):
  预设  → 默认 (software default) vs 假定/假设 (assume) — split by meaning
  教学  → 教程 (tutorial) vs 教学 (teaching/instruction) — split by meaning
  走完/往下走/差别/涵盖 — stylistic, not Taiwan-isms (no localization value)
  English `script`/`词` — context-dependent

Usage:
    python scripts/zh-hans-localize.py [--apply]   # default = dry-run
    python scripts/zh-hans-localize.py --check     # exit 1 if any drift

Only touches *.zh-Hans.md. Skips fenced ``` code blocks and inline
`code` spans (a Taiwan term inside a code sample / string literal must
stay verbatim).
"""
from __future__ import annotations

import argparse
import io
import re
import sys
from pathlib import Path

# Curated blanket-safe Taiwan→Mainland vocabulary (grep-verified, this repo)
VOCAB = {
    "呼叫": "调用",      # programming call/invoke (mainland: 调用)
    "印出": "打印",      # print output
    "出包": "搞砸",      # Taiwan slang "screw up"
    "软体": "软件",      # software
    "网路": "网络",      # network
    "档案": "文件",      # file (tech context)
    "字串": "字符串",    # string (programming)
    "函式": "函数",      # function (programming)
    "程式": "程序",      # program / code
    "品质": "质量",      # quality
    "回应": "响应",      # response (LLM/API output)
    # --- batch 2 (grep-verified, 2026-05; sourced from PR #18 / residue scan) ---
    "使用者": "用户",    # user (all prose occ = "user"; meta tables PROTECTed)
    "命令列": "命令行",  # command line
    "字元": "字符",      # character (text/encoding)
    "物件": "对象",      # object (programming / 3D — mainland tech standard)
    # EXCLUDED on purpose (grep-verified unsafe — do NOT add):
    #   介面→界面  : appears in the Stage 8 H1 + README link text →
    #                changing it shifts the anchor slug & breaks inbound
    #                `#…操作介面…` links (anchor-corruption risk).
    #   影片→视频  : substring of 投影片 (slides) → 投影片→投视频 (wrong).
    #   軟體/專案/腳本/連結/設定/飛書/資料/預設 : only occur inside the
    #                PROTECTed reference docs (nothing to localize).
    #   预设/教学  : context-sensitive (default vs assume / tutorial vs
    #                teaching) — no single mainland equivalent.
}
# Mainland quote convention: 「」 (Japanese/Taiwan corner brackets)
# → “ ” (GB/T fullwidth curly double quotes).
QUOTES = {"「": "“", "」": "”"}

# Reference / policy docs that INTENTIONALLY contain TW↔Mainland term
# pairs as documentation — substituting there corrupts the reference
# (e.g. `| 使用者 | 用户 |` → `| 用户 | 用户 |`). Mirrors lint.yml's own
# zh-Hans residue-check exclusion list (project-established convention).
PROTECT = {
    "resources/style-guide.zh-Hans.md",
    "resources/glossary.zh-Hans.md",
}

REPO = Path(__file__).resolve().parent.parent
FENCE_RE = re.compile(r"```.*?```", re.DOTALL)
INLINE_RE = re.compile(r"`[^`\n]*`")


def _mask(text: str):
    """Replace fenced + inline code with placeholders so substitutions
    never touch code. Returns (masked_text, restore_map)."""
    store: list[str] = []

    def stash(m: re.Match) -> str:
        store.append(m.group(0))
        return f"\x00{len(store) - 1}\x00"

    text = FENCE_RE.sub(stash, text)
    text = INLINE_RE.sub(stash, text)
    return text, store


def _unmask(text: str, store: list[str]) -> str:
    for i, original in enumerate(store):
        text = text.replace(f"\x00{i}\x00", original)
    return text


def localize(text: str) -> tuple[str, dict[str, int]]:
    masked, store = _mask(text)
    counts: dict[str, int] = {}
    for tw, cn in {**VOCAB, **QUOTES}.items():
        c = masked.count(tw)
        if c:
            masked = masked.replace(tw, cn)
            counts[f"{tw}→{cn}"] = c
    return _unmask(masked, store), counts


def main() -> int:
    if hasattr(sys.stdout, "reconfigure"):
        try:
            sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        except Exception:
            pass
    ap = argparse.ArgumentParser(description=__doc__)
    # --check and --apply are semantically exclusive: --check is the CI
    # gate (read-only, exit 1 on drift); --apply writes. Don't combine.
    ap.add_argument("--apply", action="store_true", help="write changes (default: dry-run)")
    ap.add_argument("--check", action="store_true", help="exit 1 if any file would change (CI gate, read-only)")
    args = ap.parse_args()

    # `.claude` holds git worktrees (`.claude/worktrees/<name>/`), which contain a
    # full second copy of the tree. Without this the gate scans those copies and
    # reports drift that does not exist in the working tree — and worse, the
    # PROTECT list below never matches them, because it is keyed on repo-relative
    # paths like "resources/style-guide.zh-Hans.md" while the worktree copy is at
    # ".claude/worktrees/<name>/resources/style-guide.zh-Hans.md". A protected file
    # therefore becomes unprotected the moment a worktree exists. Found 2026-08-02
    # when a stray worktree made this gate fail on a file it is meant to skip.
    SKIP_PARTS = {".ai", ".claude", "node_modules", "_build", "_site", "book"}
    files = sorted(
        p for p in REPO.rglob("*.zh-Hans.md")
        # Intersect against the REPO-RELATIVE parts. Using p.parts tests the
        # ABSOLUTE path, and SKIP_PARTS contains ".claude" — so from a checkout
        # under `.claude/worktrees/<name>/` this matched every file and the gate
        # scanned 0 of 68 zh-Hans files while printing "✓ zh-Hans localization
        # clean — no drift". Eighth instance of the 2026-08-02 bug class; pinned
        # by test_repo_scan_excludes.py.
        if not SKIP_PARTS & set(p.relative_to(REPO).parts)
        and p.relative_to(REPO).as_posix() not in PROTECT
    )
    total = 0
    changed_files = 0
    agg: dict[str, int] = {}
    for fp in files:
        src = fp.read_text(encoding="utf-8")
        out, counts = localize(src)
        if out != src:
            changed_files += 1
            n = sum(counts.values())
            total += n
            for k, v in counts.items():
                agg[k] = agg.get(k, 0) + v
            rel = fp.relative_to(REPO).as_posix()
            print(f"  {rel}: {n} ({', '.join(f'{k}×{v}' for k, v in counts.items())})")
            if args.apply:
                fp.write_text(out, encoding="utf-8")

    print()
    print(f"=== {total} substitutions across {changed_files} file(s) ===")
    for k, v in sorted(agg.items(), key=lambda x: -x[1]):
        print(f"  {k}: {v}")
    if args.check:
        print("❌ zh-Hans localization drift detected — run "
              "`python scripts/zh-hans-localize.py --apply`"
              if total else "✓ zh-Hans localization clean — no drift")
        return 1 if total else 0
    if not args.apply:
        print("\n(dry-run — pass --apply to write)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
