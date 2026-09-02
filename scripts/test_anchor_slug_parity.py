#!/usr/bin/env python3
"""Pins the three anchor bugs that check-anchors.py was structurally unable to see.

Background — the divergence (issue #93). scripts/check-anchors.py validates
anchors against GitHub's github-slugger rules, which is correct for people
reading this repo on github.com. The published MkDocs site used python-markdown's
default slugify, which STRIPS non-ASCII. So:

    ### Loop Engineering（迴圈工程）
        GitHub / check-anchors.py  ->  loop-engineering迴圈工程
        python-markdown default    ->  loop-engineering

151 distinct fragments were dead on the published site while the gate reported
"All internal anchors valid". Emoji-prefixed ASCII headings diverged too, because
GitHub keeps the leading separator that python-markdown strips.

Fix: mkdocs.yml now configures pymdownx.slugs.slugify(case="lower") for toc.
TEST 1 proves that choice still reproduces check-anchors.py exactly. If someone
changes either slugifier, this fails instead of silently reopening the gap.

TEST 2 is a second, independent blind spot found while fixing the first.
check-anchors.py:154 does `anchor_slug = slugify(anchor)` — it normalises the
LINK as well as the heading, so `#📋-playbook-4...` matches a heading whose real
id has no emoji. A browser does no normalisation; it matches the id byte for
byte. 16 links were valid to the gate and dead in a browser. TEST 2 requires
every internal fragment to be LITERALLY correct.

TEST 3 covers the one divergence that configuration cannot fix. GitHub KEEPS
Unicode combining marks (Mn/Me) in a slug; check-anchors.py and the site both
strip them. So a heading carrying one has two valid anchors and no fragment
works in both renderers — it has to be prevented at the heading, not the link.
Six headings were in that state; `resources/setup-guide.*` shows why the rule
must cover the whole Mn/Me class rather than U+FE0F alone. See TEST 3's own
docstring for the live github.com evidence.

Run:  python scripts/test_anchor_slug_parity.py     (plain asserts, no pytest needed)
 or:  pytest scripts/test_anchor_slug_parity.py
"""
from __future__ import annotations

import importlib.util
import re
import subprocess
import sys
import unicodedata
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent

_SPEC = importlib.util.spec_from_file_location(
    "check_anchors", Path(__file__).with_name("check-anchors.py")
)
ca = importlib.util.module_from_spec(_SPEC)
_SPEC.loader.exec_module(ca)

# Same exclusions the gate uses, plus generated/build/cache trees. A stray .md
# under a cache dir is not content and must not be able to fail a content test.
_SKIP = ca.EXCLUDE_DIRS | {
    "site",
    "_site",
    ".pytest_cache",
    ".mypy_cache",
    ".ruff_cache",
    ".venv",
    "venv",
}

ANCHOR_LINK_RE = re.compile(r"\[([^\]]+)\]\(([^)]*?)#([^)]+)\)")


def _md_files() -> list[Path]:
    """Tracked .md files only.

    A plain rglob pulls in UNTRACKED local files, so this gate's input differed
    between a laptop and CI — a stray `.mirror-sync-comment.md` was enough to
    shift the repo's heading count by one and make a published figure
    unreproducible (issue #97). Directory filters cannot fix that: the file sits
    at the repo root.

    Falls back to the rglob walk when git is unavailable, so the test still runs
    outside a checkout; the fallback is the old, slightly-wider behaviour rather
    than a silent empty set.
    """
    try:
        listed = subprocess.run(
            ["git", "-C", str(REPO), "ls-files", "-z", "*.md"],
            capture_output=True,
            check=True,
            timeout=30,
        ).stdout.decode("utf-8")
        candidates = [REPO / n for n in listed.split("\0") if n]
        if not candidates:
            # `git -C <dir> ls-files` in a directory that is not itself a repo
            # walks UP, finds the enclosing one, and exits 0 with empty stdout.
            # That never raises, so without this the walk returns [] and two of
            # the tests below pass vacuously while printing green — the exact
            # "scans 0 files, reports success" class this repo keeps paying for.
            raise FileNotFoundError("git ls-files returned no .md paths")
    except (OSError, subprocess.SubprocessError):
        candidates = sorted(REPO.rglob("*.md"))

    out = []
    for p in candidates:
        rel = p.relative_to(REPO)
        if any(part in _SKIP for part in rel.parts):
            continue
        if p.exists():  # `git ls-files` lists deleted-but-staged paths too
            out.append(p)
    return sorted(out)


def _site_slugify():
    """The slugify callable mkdocs.yml actually configures for toc.

    Loaded from the real config rather than hardcoded, so that editing
    mkdocs.yml is what this test reacts to.
    """
    from mkdocs.config import load_config

    cfg = load_config(str(REPO / "mkdocs.yml"))
    for ext in cfg["markdown_extensions"]:
        # mkdocs normalises to a list of extension names; configs live alongside
        if ext == "toc":
            fn = cfg["mdx_configs"].get("toc", {}).get("slugify")
            assert fn is not None, (
                "mkdocs.yml no longer sets an explicit toc.slugify. "
                "python-markdown's default strips non-ASCII and silently kills "
                "every CJK anchor on the site — see issue #93."
            )
            return fn
    raise AssertionError("mkdocs.yml has no 'toc' markdown extension")


def test_site_slugify_matches_github_slugify() -> None:
    """Every heading in the repo must slug identically for the site and the gate."""
    site = _site_slugify()
    mismatches = []
    total = 0
    for p in _md_files():
        for m in ca.HEADER_RE.finditer(p.read_text(encoding="utf-8")):
            heading = m.group(2)
            total += 1
            want = ca.slugify(heading)
            got = site(heading, "-")
            if want != got:
                mismatches.append((p.relative_to(REPO), heading, want, got))

    assert total > 0, "scanned zero headings — the file walk is broken"
    if mismatches:
        lines = [
            f"{len(mismatches)}/{total} headings slug differently on the site "
            f"than check-anchors.py expects:"
        ]
        for rel, h, want, got in mismatches[:10]:
            lines.append(f"  {rel}: {h!r}\n    gate={want!r}\n    site={got!r}")
        raise AssertionError("\n".join(lines))


def test_internal_fragments_are_literally_correct() -> None:
    """No fragment may depend on the gate normalising it.

    check-anchors.py slugifies the anchor before comparing, so a link carrying
    a stray emoji or the wrong case passes the gate and still fails in a browser.
    """
    offenders = []
    for p in _md_files():
        text = ca.strip_code_blocks(p.read_text(encoding="utf-8"))
        for lineno, line in enumerate(text.split("\n"), 1):
            for m in ANCHOR_LINK_RE.finditer(line):
                target, anchor = m.group(2).strip(), m.group(3).strip()
                if target.startswith(("http://", "https://")):
                    continue
                tp = p if target == "" else (p.parent / target)
                if not tp.exists() or tp.suffix != ".md":
                    continue  # missing-file case is check-anchors.py's job
                heads = ca.collect_anchors(tp.read_text(encoding="utf-8"))
                if anchor in heads:
                    continue
                canon = ca.slugify(anchor)
                if canon in heads:
                    offenders.append((p.relative_to(REPO), lineno, anchor, canon))

    if offenders:
        lines = [
            f"{len(offenders)} fragment(s) resolve only after normalisation, "
            f"i.e. they are dead in a browser:"
        ]
        for rel, ln, got, want in offenders[:10]:
            lines.append(f"  {rel}:{ln}\n    is   #{got}\n    want #{want}")
        raise AssertionError("\n".join(lines))


def test_no_link_target_heading_carries_a_combining_mark() -> None:
    """A linked-to heading must not contain a combining mark (Unicode Mn or Me).

    This is the one place GitHub and the site genuinely CANNOT be reconciled,
    so it is guarded by construction instead of by configuration.

    check-anchors.py:88 (`[^\\w\\s\\-一-鿿]`) strips combining marks, and pymdownx's
    slugify strips them too, so gate and site agree. GitHub's github-slugger
    KEEPS them. Both verified against live github.com HTML:

        ## 🗺️ 學習地圖（兩條學習路徑）
            GitHub  id="user-content-️-學習地圖兩條學習路徑"   <- U+FE0F (Mn) survives
        ### 1️⃣ 網頁版（最簡單，免費可試，零 setup）
            GitHub  id="user-content-1️⃣-網頁版最簡單免費可試零-setup"
                    <- U+FE0F (Mn) AND U+20E3 (Me) both survive

    So a heading carrying any such mark has two different valid anchors and no
    single fragment works in both renderers.

    It must be the whole Mn/Me class, not just U+FE0F. A keycap like `1️⃣` is
    U+0031 U+FE0F U+20E3: removing only the variation selector leaves `1⃣`,
    which STILL diverges — the guard would go green while the link stayed dead
    on GitHub. `resources/setup-guide.*` has 15 such keycap headings, exactly
    the "step 1 / step 2" targets someone will deep-link to.

    Non-ASCII whitespace (Zs: U+00A0, U+3000, …) also diverges, but there the
    SITE and the GATE disagree too, so test 1 already fails closed on it.

    53 headings in this repo carry a mark. That is harmless while nothing links
    to them, and stripping them wholesale is NOT safe: bare `⚠` (U+26A0) has
    Emoji_Presentation=No, so its default rendering is a monochrome text glyph.
    So the rule is narrow — do not LINK to one. The six that were linked had
    their marks removed (see the 2026-08-13 CHANGELOG entry).

    Known tradeoff on those six: `🗺` (U+1F5FA) is ALSO Emoji_Presentation=No
    (checked against unicode.org's emoji-data.txt, same class as `⚠`), so bare
    it may render text-style rather than in colour on a strict renderer. That
    was accepted over changing the icon, because the anchor break was real and
    measurable while the rendering difference is cosmetic and font-dependent.
    If those headings ever look wrong, swap the emoji for one with
    Emoji_Presentation=Yes (`🧭` U+1F9ED, `📍` U+1F4CD) rather than putting the
    variation selector back — that would re-break the anchors.
    """
    linked: dict[Path, set[str]] = {}
    for p in _md_files():
        text = ca.strip_code_blocks(p.read_text(encoding="utf-8"))
        for m in ANCHOR_LINK_RE.finditer(text):
            target, anchor = m.group(2).strip(), m.group(3).strip()
            if target.startswith(("http://", "https://")):
                continue
            tp = p if target == "" else (p.parent / target)
            if not tp.exists() or tp.suffix != ".md":
                continue
            linked.setdefault(tp.resolve(), set()).add(anchor)

    offenders = []
    for tp, fragments in linked.items():
        for m in ca.HEADER_RE.finditer(tp.read_text(encoding="utf-8")):
            heading = m.group(2)
            marks = [c for c in heading if unicodedata.category(c) in {"Mn", "Me"}]
            if not marks:
                continue
            if ca.slugify(heading) in fragments:
                offenders.append((tp.relative_to(REPO), heading, marks))

    if offenders:
        lines = [
            f"{len(offenders)} heading(s) are link targets AND carry a combining "
            f"mark, so no fragment can work on both GitHub and the site:"
        ]
        for rel, h, marks in offenders:
            cps = " ".join(f"U+{ord(c):04X}({unicodedata.category(c)})" for c in marks)
            lines.append(f"  {rel}: {h!r}\n      marks: {cps}")
        lines.append(
            "GitHub keeps combining marks (variation selectors, enclosing keycaps, "
            "combining accents) in its slug; check-anchors.py and the site strip "
            "them. Either remove EVERY such mark from the heading — for a keycap "
            "that means U+20E3 as well as U+FE0F, since dropping only the "
            "selector leaves the link dead on GitHub — or stop linking to it."
        )
        raise AssertionError("\n".join(lines))


def main() -> int:
    if hasattr(sys.stdout, "reconfigure"):
        try:
            sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        except Exception:
            pass

    failed = 0
    for name, fn in sorted(globals().items()):
        if not name.startswith("test_") or not callable(fn):
            continue
        try:
            fn()
        except AssertionError as e:
            failed += 1
            print(f"FAIL {name}\n{e}\n")
        except BaseException as e:
            # Anything non-assertion (mkdocs.exceptions.Abort when docs_dir is
            # missing, an ImportError, a SystemExit from a dependency) must fail
            # LOUDLY. Letting it escape printed one green "ok" line for the other
            # test and no summary, which reads like a pass.
            failed += 1
            print(f"ERROR {name}: {type(e).__name__}: {e}\n")
        else:
            print(f"ok   {name}")
    if failed:
        print(f"\n{failed} test(s) failed.")
        return 1
    print("\n✓ Site and gate agree on every heading; every fragment is literal.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
