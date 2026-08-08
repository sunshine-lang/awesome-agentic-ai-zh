#!/usr/bin/env python3
"""Regression tests for the 2026-08-02 "silent false all-clear" bug class.

Every gate here walks the repo and skips excluded directories. Six of them
matched `EXCLUDE_DIRS` against `path.parts` — the **absolute** path — so a
checkout living under a directory named like an excluded one skipped every file
in the repo and still printed its success line.

That is not hypothetical. `.claude/worktrees/<name>/` is this repo's standard
worktree location (per CLAUDE.md), and `.claude` is in several exclude sets.
From such a checkout `check-catalog-counts.py` scanned **0 of 248** markdown
files and printed `✓ Catalog counts consistent` with exit 0 — as a BLOCKING
gate. CI never caught it: the runner path (`/home/runner/work/<repo>/<repo>`)
has no excluded component, so the gates only went blind locally, which is the
one place they run before a commit.

The fix is to match against the path RELATIVE to the repo root. That also keeps
the behaviour the exclude set is actually for: scanning from the main checkout,
a worktree copy at `<root>/.claude/worktrees/x/a.md` still has `.claude` in its
relative path and is still skipped.

Two layers of protection:
  1. `test_no_script_matches_excludes_on_absolute_path` — a source-level scan
     that fails if ANY script reintroduces the pattern. This is the one that
     stops a seventh occurrence.
  2. Per-script behavioural tests for the walkers with a callable entry point.

Run:  python scripts/test_repo_scan_excludes.py     (plain asserts, no pytest)
 or:  pytest scripts/test_repo_scan_excludes.py
"""
import importlib.util
import re
import tempfile
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parent
REPO_ROOT = SCRIPTS.parent

# Any reference to `.parts`. The guard is deliberately DUMB and broad, because
# two narrower versions were defeated in a single afternoon:
#
#   v1 required "EXCLUDE" on the line     -> missed check-mirror-parity.py,
#                                            whose set is SKIP_DIR_PARTS (7th).
#   v2 matched only `for X in Y.parts`    -> missed zh-hans-localize.py, which
#                                            writes `SKIP & set(p.parts)` (8th),
#                                            live in a blocking gate scanning
#                                            0 of 68 files.
#
# So: flag every `.parts` use, and require each safe one to say WHY, either by
# calling `.relative_to(...)` on the same line or by carrying the opt-out marker
# below. Guessing which spellings are dangerous does not work — three different
# syntaxes expressed the same bug.
PARTS_RE = re.compile(r"\.parts\b")
SAFE_MARKER = "abs-parts-ok:"


def _load(name: str):
    spec = importlib.util.spec_from_file_location(
        name.replace("-", "_"), SCRIPTS / f"{name}.py"
    )
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _worktree_root(tmp: str) -> Path:
    """A repo root that itself lives under `.claude/worktrees/` — the real case."""
    root = Path(tmp) / ".claude" / "worktrees" / "vibrant-example"
    root.mkdir(parents=True)
    return root


# --- layer 1: stop the pattern coming back ----------------------------------

def test_no_script_matches_excludes_on_absolute_path():
    """Source-level guard covering every current and future script.

    Every `.parts` use must either call `.relative_to(...)` on the same line, or
    carry an `abs-parts-ok: <reason>` marker stating why the path is already
    repo-relative. Both current markers are on `glob.glob(root_dir=REPO_ROOT)`
    walkers, which yield relative names by construction.
    """
    offenders = []
    for py in sorted(SCRIPTS.glob("*.py")):
        # Only the walkers. Test files use .parts to make assertions ABOUT
        # paths, which is not the same thing and would be noise here.
        if py.name.startswith("test_"):
            continue
        for i, line in enumerate(py.read_text(encoding="utf-8").split("\n"), 1):
            stripped = line.strip()
            if stripped.startswith("#") or not PARTS_RE.search(line):
                continue
            if "relative_to" in line or SAFE_MARKER in line:
                continue
            offenders.append(f"{py.name}:{i}: {stripped}")
    assert offenders == [], (
        "These test path components against what may be the ABSOLUTE path. From "
        "a checkout under `.claude/worktrees/`, that skips the whole repo and "
        "the gate reports a silent all-clear (it did, in 8 scripts, one of them "
        "a blocking gate scanning 0 of 68 files). Either use "
        "`.relative_to(<repo_root>).parts`, or append a trailing comment "
        f"`# {SAFE_MARKER} <why this path is already relative>`:\n  "
        + "\n  ".join(offenders)
    )


# --- layer 2: behavioural, per walker ---------------------------------------

def test_check_anchors_scans_a_worktree_checkout():
    m = _load("check-anchors")
    with tempfile.TemporaryDirectory() as d:
        root = _worktree_root(d)
        f = root / "a.md"
        f.write_text("# t", encoding="utf-8")
        assert m.should_skip(f, root) is False


def test_check_anchors_still_skips_a_nested_worktree_copy():
    """The exclude set's real purpose must survive the fix."""
    m = _load("check-anchors")
    with tempfile.TemporaryDirectory() as d:
        root = Path(d)
        nested = root / ".claude" / "worktrees" / "copy"
        nested.mkdir(parents=True)
        f = nested / "a.md"
        f.write_text("# t", encoding="utf-8")
        assert m.should_skip(f, root) is True


def test_check_links_finds_files_in_a_worktree_checkout():
    m = _load("check-links")
    with tempfile.TemporaryDirectory() as d:
        root = _worktree_root(d)
        (root / "a.md").write_text("# t", encoding="utf-8")
        assert len(m.find_md_files(root)) == 1


def test_refresh_stars_finds_files_in_a_worktree_checkout():
    m = _load("refresh-stars")
    with tempfile.TemporaryDirectory() as d:
        root = _worktree_root(d)
        (root / "a.md").write_text("# t", encoding="utf-8")
        assert len(m.find_md_files(root)) == 1


def test_check_locale_links_scans_a_worktree_checkout():
    m = _load("check-locale-links")
    with tempfile.TemporaryDirectory() as d:
        root = _worktree_root(d)
        (root / "p.en.md").write_text("[x](t.md)\n", encoding="utf-8")
        assert len(list(m.iter_mirror_files(root))) == 1


def test_mirror_parity_scans_a_worktree_checkout():
    """The seventh instance — found only because its ratchet failed loudly.

    check-mirror-parity.py spells its exclude set SKIP_DIR_PARTS, so the first
    version of the source guard above (which keyed on the name "EXCLUDE") did
    not see it. Its trio-count ratchet turned the blindness into a hard failure
    ("complete trios dropped 67 -> 0") instead of a silent pass — which is the
    design every one of these walkers should have.
    """
    m = _load("check-mirror-parity")
    assert ".claude" in m.SKIP_DIR_PARTS
    src = (SCRIPTS / "check-mirror-parity.py").read_text(encoding="utf-8")
    assert "canon.relative_to(REPO_ROOT).parts" in src


def test_catalog_counts_exclude_set_is_named():
    """It was an inline literal at the scan site, unreferencable and drift-prone."""
    m = _load("check-catalog-counts")
    assert ".claude" in m.SCAN_EXCLUDE_DIRS


# --- the live incident, pinned ----------------------------------------------

def test_catalog_counts_actually_scans_this_repo():
    """The gate that was live-firing: it must scan a non-zero number of files.

    This test file lives inside the repo it guards, so if the walker goes blind
    again this assertion fails wherever the suite runs — including from the
    worktree checkout where the original bug was found.
    """
    m = _load("check-catalog-counts")
    scanned = [
        fp for fp in REPO_ROOT.rglob("*.md")
        if not any(p in m.SCAN_EXCLUDE_DIRS
                   for p in fp.relative_to(REPO_ROOT).parts)
    ]
    assert len(scanned) > 100, (
        f"catalog-counts would scan only {len(scanned)} markdown files from "
        f"{REPO_ROOT} — the walker is blind again (it was 0/248 in 2026-08)."
    )


if __name__ == "__main__":
    tests = [(n, f) for n, f in sorted(globals().items())
             if n.startswith("test_") and callable(f)]
    failed = 0
    for name, fn in tests:
        try:
            fn()
            print(f"  PASS  {name}")
        except AssertionError as e:
            print(f"  FAIL  {name}: {e}")
            failed += 1
    print(f"\n{len(tests) - failed}/{len(tests)} passed")
    raise SystemExit(1 if failed else 0)
