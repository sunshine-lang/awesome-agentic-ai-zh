"""Regression tests for scripts/refresh-stars.py star-line detection + write-back.

Run: python scripts/test_refresh_stars.py   (plain asserts, no pytest needed)
 or: pytest scripts/test_refresh_stars.py

Pins the 2026-07 bug fix: the --apply write-back must target the ★'s own line,
NOT the URL line (entry-block formats — Track A mirrors, branch files, the
mcp-skills-catalog `| Stars |` rows — were silently no-op'd for ~8 weekly runs),
AND Step-2 lookahead must not leak a neighbouring table row's ★.
"""
import importlib.util
from pathlib import Path

_SPEC = importlib.util.spec_from_file_location(
    "refresh_stars", Path(__file__).with_name("refresh-stars.py")
)
rs = importlib.util.module_from_spec(_SPEC)
_SPEC.loader.exec_module(rs)


def _detect(md: str):
    """Return {url_line_idx: (declared, text, star_idx)} for every GitHub URL."""
    lines = md.splitlines()
    out = {}
    for i, line in enumerate(lines):
        if rs.GITHUB_RE.search(line):
            out[i] = rs.detect_stars(lines, i)
    return out


def test_github_dir_excluded_from_scan():
    # .github/outreach drafts carry historical ("week 1 ★525") + cross-repo
    # (Langchain-Chatchat ★37k) star mentions that must NOT be auto-refreshed.
    # 2026-07 incident: the bot rewrote 7 of them to this repo's current count.
    assert ".github" in rs.EXCLUDE_DIRS
    scanned = rs.find_md_files(rs.REPO_ROOT)
    leaked = [fp for fp in scanned if ".github" in fp.parts]
    assert not leaked, f"refresh-stars must not scan .github/: {leaked[:3]}"


def test_same_line_table():
    res = _detect("| [repo](https://github.com/a/b) | desc | ★ 80k+ |")
    declared, text, star_idx = res[0]
    assert declared == 80000
    assert star_idx == 0            # ★ on the same line as the URL
    assert text == "★ 80k+"


def test_entry_block_next_line():
    md = "#### [repo](https://github.com/a/b) ⭐⭐⭐⭐\n★ 23k+ · Apache-2.0 — desc"
    declared, text, star_idx = _detect(md)[0]
    assert declared == 23000
    assert star_idx == 1           # ★ on the line AFTER the URL heading


def test_entry_block_metadata_table_after_blank():
    md = (
        "### [repo](https://github.com/a/b) ⭐⭐⭐⭐\n"
        "\n"
        "| Field | Value |\n"
        "|---|---|\n"
        "| Stars | ★ 34 |\n"
        "| License | MIT |\n"
    )
    declared, text, star_idx = _detect(md)[0]
    assert declared == 34
    assert star_idx == 4           # the `| Stars | ★ 34 |` row, past the blank line


def test_table_row_no_star_does_not_leak_neighbour():
    # repoA's row has no ★; the NEXT table row (repoB) does. The old code looked
    # ahead and stole repoB's ★ for repoA. Now repoA must report no stars.
    md = (
        "| | [repoA](https://github.com/a/aa) | no star here |\n"
        "| | [repoB](https://github.com/b/bb) | ★ 20k+ |\n"
    )
    res = _detect(md)
    assert res[0][0] is None        # repoA: NO leak from repoB
    assert res[1][0] == 20000       # repoB: its own ★
    assert res[1][2] == 1


def test_writeback_targets_star_line_not_url_line():
    # End-to-end: an entry-block drift must rewrite the ★ line, leaving the URL
    # heading untouched. Reproduces the exact silent-no-op bug.
    lines = "#### [repo](https://github.com/a/b) ⭐⭐⭐⭐\n★ 120k+ — old\n".splitlines()
    declared, text, star_idx = rs.detect_stars(lines, 0)
    assert star_idx == 1 and text == "★ 120k+"
    assert text in lines[star_idx]            # the fixed write-back guard passes on the ★ line
    assert text not in lines[0]               # keying on the URL line (old bug) would have no-op'd
    lines[star_idx] = lines[star_idx].replace(text, f"★ {rs.fmt_stars(138000)}", 1)
    assert lines[star_idx] == "★ 138k+ — old"
    assert lines[0] == "#### [repo](https://github.com/a/b) ⭐⭐⭐⭐"  # heading untouched


def test_prose_leak_from_later_unrelated_url_is_blocked():
    # repoA has no ★ of its own; repoB (a different, LATER url) does. repoA must
    # NOT borrow repoB's count. This is the real 2026-07 corruption found live in
    # langchain-ai.md / stages 03,05,06,07 (15 occurrences): with the star-line
    # write-back, borrowing would overwrite repoB's own correct ★ with repoA's count.
    md = (
        "1. [repoA](https://github.com/a/aa) — no star here\n"
        "2. [repoB](https://github.com/b/bb) — ★ 9k+ its own count\n"
    )
    res = _detect(md)
    assert res[0][0] is None       # repoA: no leak from repoB
    assert res[1][0] == 9000       # repoB: its own ★, unaffected


def test_missing_stars_falls_back_to_url_line():
    md = "#### [repo](https://github.com/a/b) ⭐⭐⭐⭐\n\nsome prose, no stars\n"
    declared, text, star_idx = _detect(md)[0]
    assert declared is None
    assert star_idx == 0           # falls back to the URL line for the missing report


if __name__ == "__main__":
    import sys
    tests = [v for k, v in sorted(globals().items()) if k.startswith("test_") and callable(v)]
    failed = 0
    for fn in tests:
        try:
            fn()
            print(f"  PASS  {fn.__name__}")
        except AssertionError as e:
            failed += 1
            print(f"  FAIL  {fn.__name__}: {e}")
    print(f"\n{len(tests) - failed}/{len(tests)} passed")
    sys.exit(1 if failed else 0)
