#!/usr/bin/env python3
"""
refresh-stars.py — 用 `gh api` 把所有 GitHub repo 的星數抓最新值，比對 markdown 內標註的 `★ Xk+`。

用法：
    python scripts/refresh-stars.py              # 列出所有有變化的 entry
    python scripts/refresh-stars.py --threshold 20  # 只列差距 > 20% 的
    python scripts/refresh-stars.py --check      # 退出 code 1 如果任何 entry 過時超過門檻

環境需求：
    pip install requests
    PATH 上要有 `gh` (GitHub CLI) 並且已 `gh auth login`
"""

import argparse
import json
import re
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
MD_GLOB = "**/*.md"
# .github holds outreach drafts + policy docs whose ★ counts are HISTORICAL
# (launch "week 1 ★525" stats) or belong to OTHER repos mentioned in prose
# (e.g. Langchain-Chatchat ★37k). Auto-refreshing them corrupts the record —
# the bot mis-associates this repo's URL with a nearby prose ★ and overwrites it
# with this repo's current count (2026-07 incident). Never scan .github.
# '.claude' holds git worktrees (.claude/worktrees/<name>/), each a full second copy
# of the tree. This walker uses Path.rglob, which descends into dot-directories, so
# without this a refresh REWRITES the stale worktree copy as well as the real files —
# worse than the read-only double-counting the same bug caused in the other gates.
# Fourth script found with this hole (after zh-hans-localize, check-2026-freshness,
# check-anchors), 2026-08-03.
EXCLUDE_DIRS = {".git", ".github", ".ai", ".claude", "node_modules", "_build", "_site", ".venv"}

# 抓 GitHub repo URL：https://github.com/owner/repo
GITHUB_RE = re.compile(r"https://github\.com/([\w.-]+)/([\w.-]+?)(?:[#?/)\s]|$)")
# 抓 markdown 內標註的 stars：`| Stars | ★ 12k+ |` 或 inline `★ 12k+`
STARS_RE = re.compile(r"★\s*([\d.]+)\s*([kKmM]?)\+?")

# 排除的假 / 範本 repo
PLACEHOLDER_REPOS = {
    "owner/repo",
    "example/repo",
    "your-org/your-repo",
    "user/repo",
}

# GitHub 上不是 repo 的特殊路徑（settings、marketplace、login 等）
NON_REPO_OWNERS = {
    "settings", "marketplace", "login", "logout", "join",
    "topics", "trending", "collections", "events", "explore",
    "issues", "pulls", "notifications", "search", "new",
    "organizations", "users", "blog", "about", "pricing",
    "features", "security", "enterprise", "customer-stories",
    "sponsors", "apps", "orgs",
}

MAX_WORKERS = 10


def normalize_repo(owner: str, name: str) -> str | None:
    """正規化 repo identifier。回傳 None 表示應該跳過。"""
    # 去掉 .git 後綴
    name = name.removesuffix(".git")
    repo_id = f"{owner}/{name}"
    if repo_id in PLACEHOLDER_REPOS:
        return None
    # 排除 GitHub 上非 repo 的特殊路徑（settings/tokens 等）
    if owner in NON_REPO_OWNERS:
        return None
    # 如果 owner 或 name 太短 / 看起來不像真 repo，跳過
    if len(owner) < 1 or len(name) < 1:
        return None
    return repo_id


def find_md_files(root: Path) -> list[Path]:
    files = []
    for fp in root.glob(MD_GLOB):
        # Relative to `root`, not fp.parts — matching the ABSOLUTE path makes a
        # checkout under an excluded-looking directory (e.g. `.ai/`, `book/`,
        # `.claude/worktrees/`) skip everything and silently find no star lines.
        # Same bug as the 2026-08-02 check-locale-links.py fix.
        if any(part in EXCLUDE_DIRS for part in fp.relative_to(root).parts):
            continue
        files.append(fp)
    return files


def parse_stars_text(s: str) -> int | None:
    """`12k+` -> 12000, `1.5k+` -> 1500"""
    m = STARS_RE.match(s)
    if not m:
        return None
    num = float(m.group(1))
    unit = m.group(2).lower()
    if unit == "k":
        num *= 1000
    elif unit == "m":
        num *= 1_000_000
    return int(num)


def fetch_stars(repo: str) -> int | None:
    """gh api repos/<owner>/<repo>"""
    try:
        result = subprocess.run(
            ["gh", "api", f"repos/{repo}", "--jq", ".stargazers_count"],
            capture_output=True, text=True, timeout=15
        )
        if result.returncode != 0:
            return None
        return int(result.stdout.strip())
    except (subprocess.SubprocessError, ValueError):
        return None


def fmt_stars(n: int) -> str:
    if n >= 1_000_000:
        return f"{n/1_000_000:.1f}m+"
    if n >= 10_000:
        return f"{n//1000}k+"
    if n >= 1_000:
        return f"{n/1000:.1f}k+".replace(".0k", "k")
    return str(n)


def detect_stars(lines: list[str], i: int) -> tuple[int | None, str | None, int]:
    """Given a GitHub URL on ``lines[i]``, find its declared ``★ Xk+`` count.

    Returns ``(declared_stars, declared_text, star_line_idx)`` where
    ``star_line_idx`` is the 0-based line the ★ actually sits on — this MUST be
    the write-back target, not the URL line (the two differ for entry-block
    formats, and using the URL line silently no-ops every entry-block rewrite).

    - Step 1: same line as the URL (markdown table cells, inline bullets).
    - Step 2: entry-block formats where the ★ is on a later line
      (``#### [repo](url)`` heading + ``★ 12k+`` next line; ``### [repo](url)``
      + a ``| Stars | ★ 34 |`` metadata row). Scans the next ≤12 lines up to a
      heading / rule boundary OR the next GitHub URL (a second repo's entry —
      its ★ is not ours).
      **Step 2 is also skipped for table-row URLs** (line starts with ``|``):
      each table row is a self-contained entry. Both boundaries exist because,
      combined with a correct star-line write-back, a cross-entry ★ leak would
      overwrite the wrong repo's count (langchain-ai.md / stages 03,05,06,07
      had 15 such live leaks pre-fix).

    When no ★ is found, ``star_line_idx`` falls back to the URL line ``i`` so
    the "missing stars" report still points somewhere sensible.
    """
    line = lines[i]
    m_stars = STARS_RE.search(line)
    if m_stars:  # Step 1: same-line
        return parse_stars_text(m_stars.group(0)), m_stars.group(0), i
    if not line.lstrip().startswith("|"):  # Step 2: entry-block only, never table rows
        for j in range(i + 1, min(i + 12, len(lines))):
            stripped = lines[j].lstrip()
            if stripped.startswith(("### ", "#### ", "## ", "---", "# ")):
                break  # next entry boundary (heading / horizontal rule)
            if GITHUB_RE.search(lines[j]):
                break  # another repo's entry started here — its ★ is not ours
            m_stars = STARS_RE.search(lines[j])
            if m_stars:
                return parse_stars_text(m_stars.group(0)), m_stars.group(0), j
    return None, None, i


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--threshold", type=int, default=10,
                        help="只列出星數差距百分比超過此值的 entry（預設 10）")
    parser.add_argument("--check", action="store_true",
                        help="若有任何 entry 過時則退出 code 1")
    parser.add_argument("--show-missing", action="store_true",
                        help="列出所有有 URL 但沒附 stars 的 entry（用來盤點哪些該補 stars）")
    parser.add_argument("--apply", action="store_true",
                        help="把 drift 的 entry 直接寫回 .md（exit 0 if applied, 2 if nothing to apply）")
    args = parser.parse_args()

    # 找所有 GitHub repo + 它在每個檔案中的標註 stars
    # entries: {repo: [(file_path, declared_stars_int, line_no, declared_text)]}
    entries: dict[str, list[tuple[Path, int | None, int, str]]] = {}

    for fp in find_md_files(REPO_ROOT):
        text = fp.read_text(encoding="utf-8")
        # For each GitHub URL, detect_stars() finds its declared `★ Xk+`
        # (same-line, or entry-block on a later line) and returns the ★'s own
        # line for the write-back target — see that function's docstring.
        lines = text.splitlines()
        for i, line in enumerate(lines):
            m_repo = GITHUB_RE.search(line)
            if not m_repo:
                continue
            repo = normalize_repo(m_repo.group(1), m_repo.group(2))
            if repo is None:
                continue
            declared, declared_text, star_idx = detect_stars(lines, i)
            # Record the ★'s own line (star_idx), NOT the URL line — the
            # --apply write-back keys on this, so entry-block formats
            # (★ on a separate line) now actually get rewritten.
            entries.setdefault(repo, []).append(
                (fp, declared, star_idx + 1, declared_text or "(no stars line)")
            )

    # 去重 repo（每個 repo 只查一次）
    unique_repos = list(entries.keys())
    print(f"Found {len(unique_repos)} unique GitHub repos referenced.", file=sys.stderr)
    print(f"Querying gh api...", file=sys.stderr)

    # 並行查 stars
    actual: dict[str, int | None] = {}
    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as ex:
        futures = {ex.submit(fetch_stars, r): r for r in unique_repos}
        for i, fut in enumerate(as_completed(futures), start=1):
            repo = futures[fut]
            actual[repo] = fut.result()
            if i % 10 == 0:
                print(f"  {i}/{len(unique_repos)}", file=sys.stderr)

    # 比對
    drift = []
    missing = []
    not_found = []

    for repo, occurrences in entries.items():
        latest = actual[repo]
        if latest is None:
            not_found.append(repo)
            continue

        for fp, declared, line_no, declared_text in occurrences:
            if declared is None:
                missing.append((repo, fp, line_no))
                continue

            if declared == 0:
                pct_diff = 100
            else:
                pct_diff = abs(latest - declared) / declared * 100

            if pct_diff >= args.threshold:
                drift.append((
                    repo, fp, line_no, declared, latest, pct_diff, declared_text
                ))

    # 報告
    print()
    print("=" * 60)
    print(f"Total repos checked:   {len(unique_repos) - len(not_found)}")
    print(f"Drift (>={args.threshold}%):     {len(drift)}")
    print(f"Missing stars line:    {len(missing)}")
    print(f"Repo not found (404):  {len(not_found)}")
    print()

    if drift:
        print("=== Drifted entries ===")
        for repo, fp, line_no, declared, latest, pct, text in sorted(drift, key=lambda x: -x[5]):
            rel = fp.relative_to(REPO_ROOT)
            arrow = "↑" if latest > declared else "↓"
            print(f"  {repo}  declared={text} actual={fmt_stars(latest)} "
                  f"(diff {arrow}{pct:.0f}%)  →  {rel}:{line_no}")

    if not_found:
        print()
        print("=== Repos not found / private / renamed ===")
        for repo in not_found:
            print(f"  {repo}")
            for fp, _, line_no, _ in entries[repo]:
                rel = fp.relative_to(REPO_ROOT)
                print(f"    {rel}:{line_no}")

    if args.show_missing and missing:
        print()
        print("=== URLs without stars (could be article / docs / org / curated repo) ===")
        # Group by repo so we don't print the same repo 5 times
        by_repo: dict[str, list[tuple[Path, int]]] = {}
        for repo, fp, line_no in missing:
            by_repo.setdefault(repo, []).append((fp, line_no))
        for repo in sorted(by_repo):
            latest = actual.get(repo)
            star_str = f"★{fmt_stars(latest)}" if latest is not None else "(404)"
            occs = by_repo[repo]
            print(f"  {repo}  {star_str}  ({len(occs)} occurrence(s))")
            for fp, ln in occs[:3]:
                rel = fp.relative_to(REPO_ROOT)
                print(f"    {rel}:{ln}")
            if len(occs) > 3:
                print(f"    ... +{len(occs) - 3} more")

    if args.apply:
        # Write-back mode: replace `declared_text` with `★ {new}` in-place.
        # Group drift by file so we only do one read/write per file.
        by_file: dict[Path, list[tuple[int, str, str]]] = {}
        for repo, fp, line_no, declared, latest, pct, text in drift:
            # STARS_RE's `\s*` after the digits consumes the trailing space
            # for the bare-number case (no k/m suffix), e.g. it matches
            # "★ 60 " in "★ 60 — desc". Re-emit that exact trailing
            # whitespace so we don't glue the count to the next token
            # ("★ 70—"). For "★ 12k+" the match has no trailing ws → no-op.
            trail = text[len(text.rstrip()):]
            new_text = f"★ {fmt_stars(latest)}" + trail
            by_file.setdefault(fp, []).append((line_no, text, new_text))

        files_changed = 0
        for fp, replacements in by_file.items():
            content = fp.read_text(encoding="utf-8")
            lines = content.splitlines(keepends=True)
            for line_no, old_text, new_text in replacements:
                idx = line_no - 1
                if 0 <= idx < len(lines) and old_text in lines[idx]:
                    lines[idx] = lines[idx].replace(old_text, new_text, 1)
            fp.write_text("".join(lines), encoding="utf-8")
            files_changed += 1

        print()
        print(f"=== Applied {len(drift)} drift fixes across {files_changed} files ===")
        sys.exit(0 if drift else 2)

    if args.check and (drift or not_found):
        # CI 模式：只有 drift 或 404 算失敗。
        # `missing` 是 by design（article / spec / catalog entry 不需要 Stars row，見 style-guide §1）
        sys.exit(1)


if __name__ == "__main__":
    main()
