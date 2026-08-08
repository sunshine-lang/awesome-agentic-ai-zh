#!/usr/bin/env python3
"""Regression tests for scripts/check-mirror-parity.py.

Pins the ratchet semantics, which are the whole point of this gate:

  - a mirror with FEWER structural elements than its canonical is a deficit
  - a deficit already in the baseline is tolerated (the repo has real, legitimate
    ones — an English page may drop a Chinese-only video list)
  - a deficit LARGER than its baseline, or in a place the baseline does not
    mention, FAILS
  - a mirror with MORE than the canonical is NOT a deficit; translations
    legitimately add clarifying notes

If the ratchet ever inverts — tolerating a growing gap, or failing on a shrinking
one — the gate stops doing the one job it exists for, so each direction is tested
explicitly.

Run:  python scripts/test_mirror_parity.py     (plain asserts, no pytest needed)
 or:  pytest scripts/test_mirror_parity.py
"""
import importlib.util
import json
import subprocess
import sys
import tempfile
from pathlib import Path

SCRIPT = Path(__file__).with_name("check-mirror-parity.py")
_SPEC = importlib.util.spec_from_file_location("check_mirror_parity", SCRIPT)
cmp_ = importlib.util.module_from_spec(_SPEC)
_SPEC.loader.exec_module(cmp_)


def _run(files: dict, baseline=None, args=()):
    """Build a temp repo, run the gate in it, return (returncode, stdout)."""
    with tempfile.TemporaryDirectory() as d:
        root = Path(d)
        (root / "scripts").mkdir()
        (root / "scripts" / SCRIPT.name).write_text(
            SCRIPT.read_text(encoding="utf-8"), encoding="utf-8"
        )
        if baseline is not None:
            (root / "scripts" / "mirror-parity-baseline.json").write_text(
                json.dumps({"deficits": baseline}, ensure_ascii=False), encoding="utf-8"
            )
        for name, body in files.items():
            p = root / name
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_text(body, encoding="utf-8")
        r = subprocess.run(
            [sys.executable, str(root / "scripts" / SCRIPT.name), *args],
            capture_output=True, text=True, encoding="utf-8", errors="replace",
            cwd=str(root),
        )
        return r.returncode, r.stdout


def _trio(canon_body, en_body, hans_body, stem="page"):
    return {
        f"{stem}.md": canon_body,
        f"{stem}.en.md": en_body,
        f"{stem}.zh-Hans.md": hans_body,
    }


# --- metrics ----------------------------------------------------------------

def test_metrics_counts_structure():
    with tempfile.TemporaryDirectory() as d:
        p = Path(d) / "x.md"
        p.write_text("## A\n### B\n> q\n| a | b |\n![i](x.png)\n", encoding="utf-8")
        m = cmp_.metrics(p)
    assert m["h2"] == 1 and m["h3"] == 1 and m["blockquote"] == 1
    assert m["table_rows"] == 1 and m["images"] == 1


def test_metrics_ignores_code_fences():
    with tempfile.TemporaryDirectory() as d:
        p = Path(d) / "x.md"
        p.write_text("```\n## not a heading\n> not a quote\n```\n## real\n", encoding="utf-8")
        m = cmp_.metrics(p)
    assert m["h2"] == 1, m
    assert m["blockquote"] == 0, m
    assert m["fences"] == 1, m


# --- the ratchet ------------------------------------------------------------

def test_new_deficit_fails():
    rc, out = _run(_trio("## A\n> q\n", "## A\n", "## A\n> q\n"), baseline={})
    assert rc == 1, out
    assert "blockquote is 1 short" in out


def test_baselined_deficit_passes():
    rc, out = _run(
        _trio("## A\n> q\n", "## A\n", "## A\n> q\n"),
        baseline={"page.md": {"en": {"blockquote": 1}}},
    )
    assert rc == 0, out


def test_worsened_deficit_fails():
    """Baseline tolerates 1 missing blockquote; 2 must fail."""
    rc, out = _run(
        _trio("## A\n> q1\n> q2\n", "## A\n", "## A\n> q1\n> q2\n"),
        baseline={"page.md": {"en": {"blockquote": 1}}},
    )
    assert rc == 1, out
    assert "baseline allowed 1" in out


def test_shrunk_deficit_passes():
    """Closing a gap must never fail, even without regenerating the baseline."""
    rc, out = _run(
        _trio("## A\n> q1\n> q2\n", "## A\n> q1\n> q2\n", "## A\n> q1\n> q2\n"),
        baseline={"page.md": {"en": {"blockquote": 2}}},
    )
    assert rc == 0, out


def test_deficit_in_new_location_fails():
    """Baseline covers en; the same shortfall appearing in zh-Hans must fail."""
    rc, out = _run(
        _trio("## A\n> q\n", "## A\n", "## A\n"),
        baseline={"page.md": {"en": {"blockquote": 1}}},
    )
    assert rc == 1, out
    assert "zh-Hans" in out


def test_mirror_with_MORE_content_is_not_a_deficit():
    """Translations may add clarifying notes — that is not a regression."""
    rc, out = _run(_trio("## A\n", "## A\n> extra note\n", "## A\n> extra note\n"), baseline={})
    assert rc == 0, out


def test_different_metric_not_masked_by_baseline():
    """A baseline for blockquote must not excuse a missing heading."""
    rc, out = _run(
        _trio("## A\n## B\n> q\n", "## A\n", "## A\n## B\n> q\n"),
        baseline={"page.md": {"en": {"blockquote": 1}}},
    )
    assert rc == 1, out
    assert "h2 is 1 short" in out


# --- scoping ----------------------------------------------------------------

def test_canonical_with_NO_mirrors_is_skipped():
    """Never-translated is legitimate — examples/stage-1/04-cross-provider is one."""
    rc, out = _run({"solo.md": "## A\n> q\n"}, baseline={})
    assert rc == 0, out


def test_deleted_mirror_fails():
    """A HALF-present trio means a mirror was deleted: total content loss that
    produces no deficit, because the trio simply stops being compared."""
    rc, out = _run({"page.md": "## A\n> q\n", "page.en.md": "## A\n> q\n"}, baseline={})
    assert rc == 1, out
    assert "MISSING" in out and "zh-Hans" in out


def test_trio_count_drop_fails():
    """Both mirrors deleted leaves no partial trio — caught by the count instead."""
    with tempfile.TemporaryDirectory() as d:
        root = Path(d)
        (root / "scripts").mkdir()
        (root / "scripts" / SCRIPT.name).write_text(
            SCRIPT.read_text(encoding="utf-8"), encoding="utf-8"
        )
        (root / "scripts" / "mirror-parity-baseline.json").write_text(
            json.dumps({"trios": 1, "deficits": {}}), encoding="utf-8"
        )
        (root / "page.md").write_text("## A\n", encoding="utf-8")  # mirrors gone
        r = subprocess.run(
            [sys.executable, str(root / "scripts" / SCRIPT.name)],
            capture_output=True, text=True, encoding="utf-8", errors="replace", cwd=str(root),
        )
    assert r.returncode == 1, r.stdout
    assert "trios dropped" in r.stdout


def test_mismatched_fence_markers_do_not_mis_scope():
    """A ~~~ inside a ``` fence is literal content, not a fence close. A single
    boolean toggle would flip state here and mis-count everything after it."""
    with tempfile.TemporaryDirectory() as d:
        p = Path(d) / "x.md"
        p.write_text("```\n~~~\n## not a heading\n```\n## real\n", encoding="utf-8")
        m = cmp_.metrics(p)
    assert m["h2"] == 1, m
    assert m["fences"] == 1, m


def test_changelog_is_skipped():
    assert "CHANGELOG.md" in cmp_.SKIP_FILES


def test_worktree_dir_is_skipped():
    """Same worktree-pollution class fixed in three other gates on 2026-08-02."""
    assert ".claude" in cmp_.SKIP_DIR_PARTS


# --- baseline round-trip ----------------------------------------------------

def test_update_baseline_then_clean():
    files = _trio("## A\n> q\n", "## A\n", "## A\n")
    with tempfile.TemporaryDirectory() as d:
        root = Path(d)
        (root / "scripts").mkdir()
        (root / "scripts" / SCRIPT.name).write_text(
            SCRIPT.read_text(encoding="utf-8"), encoding="utf-8"
        )
        for name, body in files.items():
            (root / name).write_text(body, encoding="utf-8")
        gate = str(root / "scripts" / SCRIPT.name)
        r1 = subprocess.run([sys.executable, gate], capture_output=True, text=True,
                            encoding="utf-8", errors="replace", cwd=str(root))
        assert r1.returncode == 1, r1.stdout
        r2 = subprocess.run([sys.executable, gate, "--update-baseline"], capture_output=True,
                            text=True, encoding="utf-8", errors="replace", cwd=str(root))
        assert r2.returncode == 0, r2.stdout
        r3 = subprocess.run([sys.executable, gate], capture_output=True, text=True,
                            encoding="utf-8", errors="replace", cwd=str(root))
        assert r3.returncode == 0, r3.stdout


def test_repo_passes_against_committed_baseline():
    """Live assertion against the real corpus."""
    r = subprocess.run(
        [sys.executable, str(SCRIPT)],
        capture_output=True, text=True, encoding="utf-8", errors="replace",
        cwd=str(Path(__file__).resolve().parent.parent),
    )
    assert r.returncode == 0, f"mirror-parity regression:\n{r.stdout}"


def _run_all():
    # The gate's own output contains ❌ and CJK, and a Windows console defaults to
    # cp950 — without this the FAILURE message raises UnicodeEncodeError and hides
    # which assertion actually broke.
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except (AttributeError, ValueError):
        pass
    fns = [v for k, v in sorted(globals().items())
           if k.startswith("test_") and callable(v)]
    failed = 0
    for fn in fns:
        try:
            fn()
            print(f"  PASS  {fn.__name__}")
        except AssertionError as exc:
            failed += 1
            print(f"  FAIL  {fn.__name__}: {exc}")
        except Exception as exc:  # noqa: BLE001
            failed += 1
            print(f"  ERROR {fn.__name__}: {exc!r}")
    print(f"\n{len(fns) - failed}/{len(fns)} passed")
    return failed


if __name__ == "__main__":
    sys.exit(1 if _run_all() else 0)
