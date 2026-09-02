#!/usr/bin/env python3
"""
refresh-stars.py — 用 `gh api` 把所有 GitHub repo 的星數抓最新值，比對 markdown 內標註的 `★ Xk+`。

用法：
    python scripts/refresh-stars.py              # 列出所有有變化的 entry
    python scripts/refresh-stars.py --threshold 20  # 只列差距 > 20% 的
    python scripts/refresh-stars.py --check      # 退出 code 1 如果任何 entry 真的過時

「真的過時」= 差距超過門檻 **而且**算繪後的 `★ Xk+` 字串會改變。只有百分比超標
但四捨五入後字串一樣的（`10k+` → `10k+`）不算，否則 `--check` 永遠不會綠。

環境需求：
    pip install requests
    PATH 上要有 `gh` (GitHub CLI) 並且已 `gh auth login`
"""

import argparse
import json
import re
import subprocess
import sys
import time
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

# Same reasoning as .github, one level down: these files DISCUSS star counts
# rather than DECLARING them, so every number in them is a quotation, not a
# claim to keep fresh.
#   CHANGELOG.md — records what a count WAS on a date ("★ 25 → 29", "★ 11k+").
#     Rewriting those falsifies the history they exist to preserve. Measured
#     at the v2026.08.11 tag: 30 historical ★, 0 currently bound to a repo, so
#     --apply could not reach them yet — this closes it before a future entry
#     pairs a repo URL with a ★ on one line and quietly makes them rewritable.
#     (The ★ total moves every time anyone writes a changelog entry; "0 bound"
#     is the number that actually characterises the exposure.)
#   It also generates its own false advisories: writing the 2026-08-11 entry, a
#     sentence *describing* a counter-example ("a line saying `agents <N>k+
#     stars` identifies nothing") was itself counted as a prose star claim.
#     Rewording sentence-by-sentence is whack-a-mole — a changelog about star
#     counts will always contain star-count-shaped text.
EXCLUDE_FILES = {"CHANGELOG.md"}

# 抓 GitHub repo URL：https://github.com/owner/repo
GITHUB_RE = re.compile(r"https://github\.com/([\w.-]+)/([\w.-]+?)(?:[#?/)\s]|$)")
# 抓 markdown 內標註的 stars：`| Stars | ★ 12k+ |` 或 inline `★ 12k+`
STARS_RE = re.compile(r"★\s*([\d.]+)\s*([kKmM]?)\+?")

# A count written as prose ("108k+ stars" / "108k+ 星") is invisible to STARS_RE,
# so it drifts for exactly as long as it takes a human to notice the sentence:
# browser-use sat at "86k stars" across 21 places in all three locales while the
# repo was actually at 108,651 (found 2026-08-10, by reading — no gate reported it).
#
# This pattern makes those VISIBLE. It deliberately does NOT make them
# auto-rewritable: the --apply write-back emits `★ {fmt_stars(n)}` in place of the
# matched text, which would eat the trailing word and turn "Why is browser-use so
# popular (86k stars)?" into "... (★ 108k+)?" — and would have to guess the right
# word per locale (stars / 星). Report it; a human edits the sentence.
PROSE_STARS_RE = re.compile(r"(?<![\d.])([\d.]+)\s*([kKmM])\+?\s*(?:stars?|顆星|颗星|星)", re.I)

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
        # Matched on the basename, so a CHANGELOG.md in any subdirectory is
        # skipped too — they are all release history, wherever they sit.
        if fp.name in EXCLUDE_FILES:
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


#: Returned when the API says the repo is really gone (404). Distinct from None,
#: which means "could not determine" — see fetch_stars.
FETCH_GONE = object()


def fetch_stars(repo: str, retries: int = 2) -> "int | object | None":
    """gh api repos/<owner>/<repo>. Three outcomes, deliberately distinct.

    * ``int``          — the live star count.
    * ``FETCH_GONE``   — the API returned 404. The repo really is gone/renamed/private.
    * ``None``         — we could NOT determine. 403 secondary rate limit, 401 bad
      credentials, 451, 5xx, `gh` not logged in, or a malformed body all land here.

    The three-way split matters because the caller publishes the result. Collapsing
    "could not determine" into "not found" prints a false public claim about someone
    else's repository and fails --check. Measured 2026-08-10: a clean scan reported
    21st-dev/magic-mcp as not-found while it was live at 5,630 stars and an immediate
    re-query returned it fine. Retrying narrows that window but cannot close it — with
    MAX_WORKERS parallelism across ~275 repos a 403 secondary rate limit is the
    realistic failure, and it will not clear in a few seconds of backoff. So the
    unknown case is reported as unknown rather than guessed at.
    """
    for attempt in range(retries + 1):
        try:
            result = subprocess.run(
                ["gh", "api", f"repos/{repo}", "--jq", ".stargazers_count"],
                capture_output=True, text=True, timeout=20
            )
            if result.returncode == 0:
                return int(result.stdout.strip())
            # A real 404 is terminal; anything else is worth another try.
            if "404" in result.stderr or "Not Found" in result.stderr:
                return FETCH_GONE
        except (subprocess.SubprocessError, ValueError):
            pass
        if attempt < retries:
            time.sleep(1.5 * (attempt + 1))
    return None


def is_real_drift(declared: int, latest: int, threshold: float) -> bool:
    """True only if the entry is over threshold AND the rendered text would change.

    pct_diff is computed on the parsed int ("10k+" -> 10000) while the write-back
    emits fmt_stars(latest) — "10k+" again for anything under 11000. Without the
    second clause such an entry is re-flagged and re-written on every run and
    --check can never go green. Measured 2026-08-10: 24 of 110 reported entries.
    """
    if declared == 0:
        return True
    pct_diff = abs(latest - declared) / declared * 100
    return pct_diff >= threshold and fmt_stars(latest) != fmt_stars(declared)


def fmt_stars(n: int) -> str:
    if n >= 1_000_000:
        return f"{n/1_000_000:.1f}m+"
    if n >= 10_000:
        return f"{n//1000}k+"
    if n >= 1_000:
        return f"{n/1000:.1f}k+".replace(".0k", "k")
    return str(n)


def prose_value(m: "re.Match") -> int:
    """`108k+ stars` / `108k+ 星` -> 108000. Shared by both prose passes."""
    return int(float(m.group(1)) * {"k": 1_000, "m": 1_000_000}[m.group(2).lower()])


#: Repo short names too generic to bind a prose count by name. A line saying
#: "agents 12k+ stars" tells us nothing about WHICH agents repo, and this repo
#: links several (livekit/agents, openai/agents, ...). Binding those by name
#: would attribute one project's count to another. Ambiguity is reported instead.
GENERIC_REPO_NAMES = {
    "agents", "agent", "skills", "docs", "cookbook", "examples", "api",
    "cli", "sdk", "mcp", "core", "app", "web", "ai", "chat", "tools",
}


def bind_re(repo: str) -> "re.Pattern":
    """Match a repo's short name as a standalone token in prose.

    ``browser-use/browser-use`` -> matches "browser-use" in "Why is browser-use
    so popular", but not inside "browser-useful" or "mcp-server-browserbase".
    The boundaries are ASCII-class rather than ``\\b`` on purpose: these names sit
    inside CJK sentences ("為什麼 browser-use 這麼火"), where ``\\b`` behaves
    differently around non-ASCII neighbours.

    Short names in GENERIC_REPO_NAMES get a pattern that never matches, so they
    fall through to the "ambiguous / unbindable" report rather than binding.
    """
    short = repo.split("/")[-1]
    if short.lower() in GENERIC_REPO_NAMES:
        return re.compile(r"(?!)")          # never matches
    return re.compile(r"(?<![A-Za-z0-9_-])" + re.escape(short) + r"(?![A-Za-z0-9_-])",
                      re.IGNORECASE)


def apply_replacements(by_file: "dict[Path, list[tuple[int, str, str]]]") -> tuple[int, int]:
    """Rewrite the given ``{path: [(line_no, old_text, new_text)]}`` in place.

    Returns ``(replacements_applied, files_rewritten)``. Both counters move only on
    text that actually changed: a queued replacement whose ``new_text`` equals what
    is already on the line is a no-op and must not be counted, and a file whose every
    replacement is a no-op must not be rewritten or counted.

    This is what the tool prints as its own summary, so an over-count is a false
    public claim about what was edited — on 2026-08-10 an unconditional write
    reported "110 fixes across 44 files" when the truth was 86 across 38. It lives
    out here rather than inline in main() so a test can exercise the real counting
    path instead of a copy of it.
    """
    applied = files_changed = 0
    for fp, replacements in by_file.items():
        lines = fp.read_text(encoding="utf-8").splitlines(keepends=True)
        applied_here = 0
        for line_no, old_text, new_text in replacements:
            idx = line_no - 1
            if 0 <= idx < len(lines) and old_text in lines[idx]:
                before = lines[idx]
                lines[idx] = lines[idx].replace(old_text, new_text, 1)
                if lines[idx] != before:
                    applied_here += 1
        if applied_here:
            fp.write_text("".join(lines), encoding="utf-8")
            files_changed += 1
            applied += applied_here
    return applied, files_changed


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
    parser.add_argument("--prose-threshold", type=int, default=5,
                        help="散文星數的獨立門檻（預設 5,比 --threshold 更嚴）。刻意不跟"
                             " --threshold 綁在一起,而且刻意更低:★ 格式的 drift 跑一次"
                             " --apply 就自己好了,所以 CI 用寬門檻（50%%）只挑嚴重的沒關係;"
                             "散文格式**修不動**、只能等人改句子,門檻放寬等於永遠不會有人知道。"
                             "實測:browser-use 卡在 86k / 實際 108,651 是 26%% 落差,在"
                             " --threshold 50 之下完全不會被報出來;UI-TARS 36k / 實際 38,545"
                             "是 7%%,連 10%% 都擋不住。")
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
    # Prose-form counts, reported but never auto-rewritten — see PROSE_STARS_RE.
    prose: list[tuple[str, Path, int, str, int]] = []
    # Prose counts naming no repo we could pin down. Reported, never failed on.
    prose_unbound: list[tuple[Path, int, str, str]] = []

    for fp in find_md_files(REPO_ROOT):
        text = fp.read_text(encoding="utf-8")
        # For each GitHub URL, detect_stars() finds its declared `★ Xk+`
        # (same-line, or entry-block on a later line) and returns the ★'s own
        # line for the write-back target — see that function's docstring.
        lines = text.splitlines()
        # MUST stay inside the per-file loop. The name-binding pass below trusts
        # this to mean "linked in THIS file"; hoisting it out (a natural-looking
        # "don't rebuild the set each iteration" tidy-up) makes binding global,
        # so a file that merely NAMES a tool inherits a repo it never linked —
        # and publishes that repo's star count as its own, silently.
        # Pinned by test_binding_does_not_leak_across_files.
        file_repos: set[str] = set()
        for i, line in enumerate(lines):
            m_repo = GITHUB_RE.search(line)
            if not m_repo:
                continue
            repo = normalize_repo(m_repo.group(1), m_repo.group(2))
            if repo is None:
                continue
            file_repos.add(repo)
            declared, declared_text, star_idx = detect_stars(lines, i)
            # Record the ★'s own line (star_idx), NOT the URL line — the
            # --apply write-back keys on this, so entry-block formats
            # (★ on a separate line) now actually get rewritten.
            entries.setdefault(repo, []).append(
                (fp, declared, star_idx + 1, declared_text or "(no stars line)")
            )

            # Prose-form counts, same line as the URL only. Requiring the URL on
            # the SAME line is what exempts a threshold like the catalog's
            # "> 30k stars" inclusion bar, which names no repo. Skip lines that
            # already carry a ★ — those are the STARS_RE path's job, and counting
            # both would double-report the one entry.
            if "★" not in line:
                for pm in PROSE_STARS_RE.finditer(line):
                    prose.append((repo, fp, i + 1, pm.group(0).strip(),
                                  prose_value(pm)))

        # Second pass: prose counts on lines with NO GitHub URL at all.
        # These are the sentences the URL-anchored pass structurally cannot see
        # ("Why is browser-use so popular (108k stars)?", a comparison-table cell
        # naming the tool without linking it, a bullet whose only link is the
        # project's docs site rather than its repo). 12 of them sat in stage 08
        # across three locales, which is 40% of this file's prose counts.
        #
        # Binding is by NAME, and only when the line names exactly one repo that
        # is linked somewhere else in the SAME file. Ambiguity is reported, never
        # guessed: attributing repo B's count to repo A would publish a false
        # claim about someone's project, which is the failure the ★ path already
        # had to fix once (15 live cross-entry leaks).
        known = {r: bind_re(r) for r in file_repos}
        for i, line in enumerate(lines):
            if "★" in line or GITHUB_RE.search(line):
                continue  # owned by the pass above
            for pm in PROSE_STARS_RE.finditer(line):
                hits = [r for r, rx in known.items() if rx.search(line)]
                if len(hits) == 1:
                    prose.append((hits[0], fp, i + 1, pm.group(0).strip(),
                                  prose_value(pm)))
                else:
                    why = "names no linked repo" if not hits else f"ambiguous: {hits}"
                    prose_unbound.append((fp, i + 1, pm.group(0).strip(), why))

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
    not_found = []      # real 404 — the repo is gone/renamed/private
    unresolved = []     # could not determine (rate limit, auth, 5xx, timeout)

    for repo, occurrences in entries.items():
        latest = actual[repo]
        if latest is FETCH_GONE:
            not_found.append(repo)
            continue
        if latest is None:
            # Do NOT claim this repo is missing — we simply could not ask.
            unresolved.append(repo)
            continue

        for fp, declared, line_no, declared_text in occurrences:
            if declared is None:
                missing.append((repo, fp, line_no))
                continue

            pct_diff = 100 if declared == 0 else abs(latest - declared) / declared * 100

            if is_real_drift(declared, latest, args.threshold):
                drift.append((
                    repo, fp, line_no, declared, latest, pct_diff, declared_text
                ))

    # Prose-form counts, evaluated with the same predicate but never auto-fixed.
    prose_drift = []
    for repo, fp, line_no, text, declared in prose:
        latest = actual.get(repo)
        if not isinstance(latest, int):
            continue  # 404 / could-not-query are already reported by repo
        if is_real_drift(declared, latest, args.prose_threshold):
            prose_drift.append((repo, fp, line_no, text, declared, latest))

    # 報告
    print()
    print("=" * 60)
    print(f"Total repos checked:   {len(unique_repos) - len(not_found) - len(unresolved)}")
    print(f"Drift (>={args.threshold}%):     {len(drift)}")
    print(f"Prose-form drift:      {len(prose_drift)} (>={args.prose_threshold}%, manual fix)")
    print(f"Prose, unbindable:     {len(prose_unbound)} (advisory)")
    print(f"Missing stars line:    {len(missing)}")
    print(f"Repo not found (404):  {len(not_found)}")
    print(f"Could not query:       {len(unresolved)}")
    print()

    if drift:
        print("=== Drifted entries ===")
        for repo, fp, line_no, declared, latest, pct, text in sorted(drift, key=lambda x: -x[5]):
            rel = fp.relative_to(REPO_ROOT)
            arrow = "↑" if latest > declared else "↓"
            print(f"  {repo}  declared={text} actual={fmt_stars(latest)} "
                  f"(diff {arrow}{pct:.0f}%)  →  {rel}:{line_no}")

    if prose_drift:
        print()
        print("=== Prose-form counts — STALE, and --apply will NOT fix these ===")
        for repo, fp, line_no, text, declared, latest in prose_drift:
            rel = fp.relative_to(REPO_ROOT)
            arrow = "↑" if latest > declared else "↓"
            print(f"  {repo}  written as \"{text}\" actual={fmt_stars(latest)} "
                  f"({arrow})  →  {rel}:{line_no}")
        print("  Rewriting these would eat the trailing word and the locale's wording.")
        print("  Edit the sentences by hand, then re-run.")

    if prose_unbound:
        print()
        print("=== Prose counts we could NOT tie to a repo (advisory, not a failure) ===")
        for fp, line_no, text, why in prose_unbound:
            print(f"  \"{text}\"  {why}  →  {fp.relative_to(REPO_ROOT)}:{line_no}")
        print("  Not failed on: with no repo identified there is nothing to compare against.")
        print("  To bring one under the gate, link the repo on that line or name it exactly once.")

    if unresolved:
        print()
        print("=== Could not query (rate limit / auth / network — NOT a 404) ===")
        for repo in unresolved:
            print(f"  {repo}")
        print("  These are NOT reported as missing; re-run when the API settles.")

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
            # Repos that 404'd or could not be queried never reach `missing` (they
            # `continue` above), so this is an int in practice — but don't hand a
            # sentinel to fmt_stars if that ever changes.
            star_str = f"★{fmt_stars(latest)}" if isinstance(latest, int) else "(unresolved)"
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

        applied, files_changed = apply_replacements(by_file)

        print()
        print(f"=== Applied {applied} drift fixes across {files_changed} files ===")
        sys.exit(0 if applied else 2)

    if args.check and (drift or not_found or prose_drift):
        # CI 模式：只有真的 drift 或真的 404 算失敗。
        # `missing` 是 by design（article / spec / catalog entry 不需要 Stars row，見 style-guide §1）。
        # `unresolved`（rate limit / auth / 5xx / timeout）**刻意不算失敗**——我們無法判定，
        # 讓 CI 因為查不到而變紅，只會訓練大家忽略這個 gate，而且會把「查不到」誤導成
        # 「repo 不見了」。它會印在報告裡讓人看見，但不影響 exit code。
        # `prose_drift` **算失敗**：數字是真的過時了,只是 --apply 修不動、要人去改句子。
        # 這是這個 gate 唯一「報紅但自動修不了」的類別,訊息裡已寫明怎麼收尾。
        sys.exit(1)


if __name__ == "__main__":
    main()
