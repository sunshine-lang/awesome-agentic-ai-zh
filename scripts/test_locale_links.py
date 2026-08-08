#!/usr/bin/env python3
"""Regression tests for scripts/check-locale-links.py.

Pins the 2026-08 sweep: mirror pages (.en.md / .zh-Hans.md) were linking to the
zh-TW canonical even when a same-locale sibling existed, dropping non-Traditional
readers onto a page they may not read. 111 such links across 37 files were fixed.

The checker must stay CONSERVATIVE — it rewrites link targets, so a false
positive creates a dead link. These tests pin every exemption.

Run:  python scripts/test_locale_links.py     (plain asserts, no pytest needed)
 or:  pytest scripts/test_locale_links.py
"""
import importlib.util
import tempfile
from pathlib import Path

_SPEC = importlib.util.spec_from_file_location(
    "check_locale_links", Path(__file__).with_name("check-locale-links.py")
)
cll = importlib.util.module_from_spec(_SPEC)
_SPEC.loader.exec_module(cll)


def _scan(body: str, suffix: str = ".en.md", siblings=("target.en.md",)):
    """Write body to a temp mirror file, create siblings, return findings."""
    with tempfile.TemporaryDirectory() as d:
        root = Path(d)
        for s in siblings:
            (root / s).parent.mkdir(parents=True, exist_ok=True)
            (root / s).write_text("# sibling", encoding="utf-8")
        fp = root / f"page{suffix}"
        fp.write_text(body, encoding="utf-8")
        return list(cll.scan_file(suffix, fp))


def test_flags_bare_md_when_sibling_exists():
    hits = _scan("See [docs](target.md) for more.\n")
    assert len(hits) == 1
    assert hits[0][2] == "target.md" and hits[0][3] == "target.en.md"


def test_ignores_when_sibling_missing():
    # No target.en.md on disk -> the canonical link is the only correct one.
    assert _scan("See [docs](target.md).\n", siblings=()) == []


def test_ignores_already_locale_suffixed():
    assert _scan("See [docs](target.en.md).\n") == []


def test_ignores_language_switcher_row():
    # The switcher deliberately links across locales.
    body = "> [繁體中文](./target.md) | [简体中文](./target.zh-Hans.md) | **English**\n"
    assert _scan(body, siblings=("target.en.md",)) == []


def test_ignores_links_inside_fenced_code():
    body = "```markdown\n[docs](target.md)\n```\n"
    assert _scan(body) == []


def test_ignores_external_urls():
    assert _scan("[docs](https://example.com/target.md)\n") == []


def test_skips_anchor_missing_from_sibling():
    """The bug that produced 5 dead links on this sweep's first run.

    Headings are translated, so a zh-TW anchor does not exist in the .en.md
    sibling. Retargeting such a link silently breaks it — leave it canonical.
    """
    with tempfile.TemporaryDirectory() as d:
        root = Path(d)
        (root / "target.en.md").write_text("## English Heading\n", encoding="utf-8")
        fp = root / "page.en.md"
        fp.write_text("See [x](target.md#繁中標題).\n", encoding="utf-8")
        assert list(cll.scan_file(".en.md", fp)) == []


def test_rewrites_when_anchor_exists_in_sibling():
    with tempfile.TemporaryDirectory() as d:
        root = Path(d)
        (root / "target.en.md").write_text("## Shared Anchor\n", encoding="utf-8")
        fp = root / "page.en.md"
        fp.write_text("See [x](target.md#shared-anchor).\n", encoding="utf-8")
        hits = list(cll.scan_file(".en.md", fp))
        assert len(hits) == 1 and hits[0][3] == "target.en.md"


def test_slugify_matches_check_anchors_on_em_dash():
    """Regression: this script must NOT re-implement slugify.

    A local copy collapsed consecutive whitespace, so `## 5.7 — Title` slugged to
    `57-title` while check-anchors.py (correctly, per github-slugger) yields
    `57--title` — an em-dash leaves two spaces once stripped. That made rule 5
    silently under-detect the very anchored links it exists to guard.
    """
    heading = "5.7 — Claude Code Source"
    assert cll.slugify(heading) == cll._check_anchors.slugify(heading)
    assert "--" in cll.slugify(heading), "each space must map to its own hyphen"


def test_ignores_inline_dual_citation():
    """Regression: 'see FILE (zh) or FILE (en)' offers both locales on purpose.

    The first run retargeted the (zh) link in CONTRIBUTING.en.md, so both links
    pointed at the English file and the zh-TW page became unreachable.
    """
    body = ("- See [`style-guide.md`](style-guide.md) (zh) or "
            "[`style-guide.en.md`](style-guide.en.md) (en) for the rules.\n")
    assert _scan(body, siblings=("style-guide.en.md",)) == []


def test_preserves_anchor():
    """--apply must re-emit the anchor untouched (sibling has the anchor)."""
    with tempfile.TemporaryDirectory() as d:
        root = Path(d)
        (root / "target.en.md").write_text("## Some Anchor\n", encoding="utf-8")
        fp = root / "page.en.md"
        fp.write_text("See [docs](target.md#some-anchor).\n", encoding="utf-8")
        hits = list(cll.scan_file(".en.md", fp))
        assert len(hits) == 1
        # the whole-link capture keeps the anchor so --apply can re-emit it
        assert "#some-anchor" in hits[0][1]


def test_zh_hans_locale():
    hits = _scan("看 [文档](target.md)。\n", suffix=".zh-Hans.md",
                 siblings=("target.zh-Hans.md",))
    assert len(hits) == 1 and hits[0][3] == "target.zh-Hans.md"


def test_relative_parent_path():
    hits = _scan("See [docs](../target.md).\n", siblings=("target.en.md",))
    # page lives at root, ../target.md escapes the temp dir -> no sibling -> skip
    assert hits == []


def test_repo_is_clean():
    """The live repo must have zero cross-locale links (this is the CI gate)."""
    found = 0
    for suffix, fp in cll.iter_mirror_files(cll.REPO_ROOT):
        found += len(list(cll.scan_file(suffix, fp)))
    assert found == 0, f"{found} cross-locale link(s); run check-locale-links.py --apply"


def _run_all():
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
    import sys
    sys.exit(1 if _run_all() else 0)
