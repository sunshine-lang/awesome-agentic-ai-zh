#!/usr/bin/env python3
"""
Mirror sync reminder.

當 PR 改了 zh-TW canonical .md 檔（path 內含 stages/ branches/ tracks/ resources/
walkthroughs/ examples/ 或 README.md / CONTRIBUTING.md）、但沒同時改對應的 .en.md / .zh-Hans.md
mirror、產生一個 PR comment body 寫到 .mirror-sync-comment.md、提示 contributor。

Soft reminder — 不擋 PR。zh-TW canonical、mirror sync 是 Path B（slower cadence）。

Usage:
    python scripts/check-mirror-sync.py --pr-base origin/main

GitHub Actions integration:
    Sets GitHub Actions output `gap_detected=true|false`.
    Workflow uses sticky comment action to keep one comment per PR.
"""

from __future__ import annotations

import argparse
import os
import subprocess
import sys
from pathlib import Path


MIRROR_SUFFIXES = ['.en.md', '.zh-Hans.md']


def get_changed_files(base_ref: str) -> list[Path]:
    """Get list of files changed in PR vs base_ref."""
    try:
        out = subprocess.check_output(
            ['git', 'diff', '--name-only', f'{base_ref}...HEAD'],
            encoding='utf-8',
            stderr=subprocess.STDOUT,
        )
    except subprocess.CalledProcessError as e:
        print(f'⚠ git diff failed: {e}', file=sys.stderr)
        # Fall back to single-commit diff
        try:
            out = subprocess.check_output(
                ['git', 'diff', '--name-only', 'HEAD~1'],
                encoding='utf-8',
            )
        except Exception:
            return []
    return [Path(f.strip()) for f in out.splitlines() if f.strip()]


def is_canonical_md(path: Path) -> bool:
    """zh-TW canonical = .md but not .en.md / .zh-Hans.md."""
    name = str(path)
    if not name.endswith('.md'):
        return False
    for suffix in MIRROR_SUFFIXES:
        if name.endswith(suffix):
            return False
    return True


def detect_sync_gaps(
    changed: list[Path], repo_root: Path
) -> list[tuple[str, list[str]]]:
    """
    Return list of (canonical_file_changed, [missing_mirror_files]) tuples.
    Only flag canonical files whose mirrors EXIST in repo (so contributor
    isn't asked to create a new mirror from scratch).
    """
    changed_set = {str(p) for p in changed}
    gaps: list[tuple[str, list[str]]] = []

    for f in changed:
        s = str(f).replace('\\', '/')  # normalize for Windows
        if not is_canonical_md(Path(s)):
            continue

        # For X.md, compute X.en.md and X.zh-Hans.md candidate paths
        stem = s[:-3]  # strip .md
        candidates = [(suf, stem + suf) for suf in MIRROR_SUFFIXES]

        missing = []
        for suf, candidate_path in candidates:
            cand_full = repo_root / candidate_path
            if not cand_full.exists():
                continue  # no mirror exists yet — don't pressure contributor
            # Mirror exists. Check if it was also changed in this PR.
            normalized = candidate_path.replace('\\', '/')
            if normalized not in changed_set and candidate_path not in changed_set:
                missing.append(candidate_path)

        if missing:
            gaps.append((s, missing))

    return gaps


def write_comment_body(gaps: list[tuple[str, list[str]]], out_path: Path) -> None:
    """Write GitHub PR comment body listing the sync gaps."""
    lines = [
        '## 🌐 Mirror Sync Reminder',
        '',
        'zh-TW canonical files were updated in this PR, but the following mirror',
        'files were **not** updated in the same change set:',
        '',
    ]
    for canonical, missing in gaps:
        lines.append(f'- **`{canonical}`** modified — missing sync to:')
        for m in missing:
            lines.append(f'  - `{m}`')
    lines.extend(
        [
            '',
            '> 💡 **This is a soft reminder, not a blocker.** zh-TW is the canonical',
            '> version of this repo. Mirror files (`.en.md` / `.zh-Hans.md`) sync',
            '> is on a slower cadence (Path B). Update when convenient — or open a',
            '> separate sync PR later.',
            '',
            '> If the canonical change is purely cosmetic (typo, whitespace, etc.),',
            '> mirror sync can be safely skipped.',
            '',
        ]
    )
    out_path.write_text('\n'.join(lines), encoding='utf-8')


def set_gh_output(name: str, value: str) -> None:
    """Set a GitHub Actions output variable."""
    out_file = os.environ.get('GITHUB_OUTPUT')
    if out_file:
        with open(out_file, 'a', encoding='utf-8') as fh:
            fh.write(f'{name}={value}\n')
    # Also print for local debug
    print(f'{name}={value}')


def main() -> int:
    # Force UTF-8 stdout
    if hasattr(sys.stdout, 'reconfigure'):
        try:
            sys.stdout.reconfigure(encoding='utf-8', errors='replace')
        except Exception:
            pass

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        '--pr-base',
        default='origin/main',
        help='Base ref to diff against (default: origin/main)',
    )
    parser.add_argument(
        '--comment-out',
        default='.mirror-sync-comment.md',
        help='Path to write PR comment body',
    )
    args = parser.parse_args()

    repo_root = Path(__file__).resolve().parent.parent
    changed = get_changed_files(args.pr_base)

    if not changed:
        print('No changed files detected.')
        set_gh_output('gap_detected', 'false')
        return 0

    gaps = detect_sync_gaps(changed, repo_root)

    if not gaps:
        print('✓ All canonical changes have synced mirrors (or no mirror exists yet).')
        set_gh_output('gap_detected', 'false')
        return 0

    print(f'⚠ Detected {len(gaps)} canonical file(s) with unsynced mirrors:')
    for canonical, missing in gaps:
        print(f'  - {canonical}: missing {", ".join(missing)}')

    write_comment_body(gaps, repo_root / args.comment_out)
    set_gh_output('gap_detected', 'true')
    return 0


if __name__ == '__main__':
    sys.exit(main())
