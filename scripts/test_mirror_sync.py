#!/usr/bin/env python3
"""Cross-platform regression tests for check-mirror-sync.py."""

from __future__ import annotations

import importlib.util
import tempfile
from pathlib import Path, PurePath, PurePosixPath, PureWindowsPath


SCRIPT = Path(__file__).with_name("check-mirror-sync.py")
_SPEC = importlib.util.spec_from_file_location("check_mirror_sync", SCRIPT)
cms = importlib.util.module_from_spec(_SPEC)
_SPEC.loader.exec_module(cms)


def _write_trio(repo_root: Path) -> None:
    for name in ("guide.md", "guide.en.md", "guide.zh-Hans.md"):
        target = repo_root / "docs" / name
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text("# Guide\n", encoding="utf-8")


def _assert_synced_trio(path_type: type[PurePath]) -> None:
    with tempfile.TemporaryDirectory() as directory:
        repo_root = Path(directory)
        _write_trio(repo_root)
        changed = [
            path_type("docs/guide.md"),
            path_type("docs/guide.en.md"),
            path_type("docs/guide.zh-Hans.md"),
        ]

        assert cms.detect_sync_gaps(changed, repo_root) == []


def test_synced_mirrors_are_recognized_with_posix_paths() -> None:
    _assert_synced_trio(PurePosixPath)


def test_synced_mirrors_are_recognized_with_windows_paths() -> None:
    _assert_synced_trio(PureWindowsPath)


def test_only_the_unchanged_existing_mirror_is_reported() -> None:
    with tempfile.TemporaryDirectory() as directory:
        repo_root = Path(directory)
        _write_trio(repo_root)
        changed = [
            PureWindowsPath("docs/guide.md"),
            PureWindowsPath("docs/guide.en.md"),
        ]

        assert cms.detect_sync_gaps(changed, repo_root) == [
            ("docs/guide.md", ["docs/guide.zh-Hans.md"])
        ]


if __name__ == "__main__":
    test_synced_mirrors_are_recognized_with_posix_paths()
    test_synced_mirrors_are_recognized_with_windows_paths()
    test_only_the_unchanged_existing_mirror_is_reported()
    print("mirror-sync path regressions passed")
