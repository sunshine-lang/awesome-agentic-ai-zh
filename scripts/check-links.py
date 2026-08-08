#!/usr/bin/env python3
"""
check-links.py — 掃描所有 markdown 檔案的 URL，回報 4xx / 5xx / timeout。

用法：
    python scripts/check-links.py            # 檢查所有 .md 檔
    python scripts/check-links.py --fast     # 只查 GitHub repos（最容易 404）
    python scripts/check-links.py --quiet    # 只印失敗

環境需求：
    pip install requests
"""

import argparse
import re
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from typing import Iterable

try:
    import requests
except ImportError:
    print("ERROR: 需要 requests。請先執行：pip install requests", file=sys.stderr)
    sys.exit(1)

REPO_ROOT = Path(__file__).resolve().parent.parent
MD_GLOB = "**/*.md"
EXCLUDE_DIRS = {".git", ".ai", "node_modules", "_build", ".venv"}

# 抓 markdown link [text](url) 的正則。處理 url 內可能含巢狀 ()。
# 用「至少 1 個非空白非右括號字元，後接任意可選 (...) 對」的策略。
LINK_RE = re.compile(
    r"\[([^\]]+)\]"
    r"\((https?://[^\s()]+(?:\([^\s()]*\))?[^\s)]*)\)"
)

TIMEOUT = 15
MAX_WORKERS = 10


def find_md_files(root: Path) -> list[Path]:
    files = []
    for fp in root.glob(MD_GLOB):
        # Relative to `root`, not fp.parts — matching the ABSOLUTE path makes a
        # checkout under an excluded-looking directory (e.g. `.ai/`, `book/`,
        # `.claude/worktrees/`) skip everything and report a silent all-clear.
        # Same bug as the 2026-08-02 check-locale-links.py fix.
        if any(part in EXCLUDE_DIRS for part in fp.relative_to(root).parts):
            continue
        files.append(fp)
    return files


def extract_urls(md_path: Path) -> list[tuple[int, str]]:
    """回傳 [(line_no, url), ...]，跳過程式碼區塊內的 URL。"""
    urls = []
    text = md_path.read_text(encoding="utf-8")
    in_fenced_code = False
    for line_no, line in enumerate(text.splitlines(), start=1):
        # Toggle fenced code block state on ``` or ~~~
        stripped = line.lstrip()
        if stripped.startswith("```") or stripped.startswith("~~~"):
            in_fenced_code = not in_fenced_code
            continue
        if in_fenced_code:
            continue
        # 也跳過 inline code（粗略：只在 ` ` 之間的 URL 不算）
        # Markdown 規範允許 inline code 內含 link 但通常不是真 link
        for match in LINK_RE.finditer(line):
            url = match.group(2).rstrip(".,;:!?")
            urls.append((line_no, url))
    return urls


def check_url(url: str, fast_mode: bool = False) -> tuple[str, int | None, str]:
    """回傳 (url, final_status_code or None, message)。allow_redirects=True 表示
    final_status 不會是 3xx（會被 follow 到 2xx 或 4xx/5xx）。"""
    if fast_mode and "github.com" not in url:
        return url, None, "skipped (--fast)"
    try:
        r = requests.head(url, timeout=TIMEOUT, allow_redirects=True,
                          headers={"User-Agent": "awesome-agentic-ai-zh-link-check/1.0"})
        # 有些 server 不接受 HEAD，fallback 用 GET
        if r.status_code in (405, 403):
            r = requests.get(url, timeout=TIMEOUT, allow_redirects=True, stream=True,
                             headers={"User-Agent": "awesome-agentic-ai-zh-link-check/1.0"})
            r.close()
        return url, r.status_code, ""
    except requests.exceptions.RequestException as e:
        return url, None, str(e)[:80]


def main():
    parser = argparse.ArgumentParser(description="Check markdown links for rot.")
    parser.add_argument("--fast", action="store_true", help="只查 GitHub URL")
    parser.add_argument("--quiet", action="store_true", help="只印失敗")
    args = parser.parse_args()

    files = find_md_files(REPO_ROOT)
    print(f"Scanning {len(files)} markdown files...", file=sys.stderr)

    # 收集所有 URL（去重，但記下出現位置）
    occurrences: dict[str, list[tuple[Path, int]]] = {}
    for fp in files:
        for line_no, url in extract_urls(fp):
            occurrences.setdefault(url, []).append((fp, line_no))

    print(f"Found {len(occurrences)} unique URLs.", file=sys.stderr)

    failures = []
    ok_count = 0
    skipped = 0

    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as ex:
        futures = {ex.submit(check_url, url, args.fast): url for url in occurrences}
        for i, fut in enumerate(as_completed(futures), start=1):
            url, status, msg = fut.result()
            if status is None and msg.startswith("skipped"):
                skipped += 1
                continue
            if status is None:
                failures.append((url, f"ERROR: {msg}"))
                if not args.quiet:
                    print(f"[{i}/{len(occurrences)}] ❌ {url} — {msg}")
            elif status >= 400:
                failures.append((url, f"HTTP {status}"))
                if not args.quiet:
                    print(f"[{i}/{len(occurrences)}] ❌ {url} — HTTP {status}")
            else:
                # 200-299 (3xx 已被 allow_redirects 跟過去 → final 是 2xx 或 4xx/5xx)
                ok_count += 1
                if not args.quiet:
                    print(f"[{i}/{len(occurrences)}] ✓ {url}")

    # 報告
    print()
    print("=" * 60)
    print(f"Total checked:   {len(occurrences) - skipped}")
    print(f"OK (2xx):        {ok_count}")
    print(f"Failed:          {len(failures)}")
    if args.fast:
        print(f"Skipped (--fast): {skipped}")
    print()

    if failures:
        print("=== Failures by file ===")
        for url, reason in failures:
            print(f"\n❌ {url}  [{reason}]")
            for fp, line_no in occurrences[url]:
                rel = fp.relative_to(REPO_ROOT)
                print(f"   {rel}:{line_no}")

    sys.exit(1 if failures else 0)


if __name__ == "__main__":
    main()
