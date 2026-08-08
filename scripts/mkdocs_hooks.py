"""mkdocs build hooks for the awesome-agentic-ai-zh docs site.

Strips the hand-written GitHub-style language switcher from the
README pages when rendered by mkdocs.

Why: README.md / README.en.md / README.zh-Hans.md open with a
``<div align="right"> 繁體中文 | 简体中文 | English </div>`` block
whose links point at the *raw* sibling files (`./README.zh-Hans.md`
…). That is correct for GitHub file browsing, but on the rendered
mkdocs site those `.md` paths 404 (mkdocs builds them into
pages/dirs, and the block is raw HTML so mkdocs does not rewrite the
links). The site already has the proper in-site language selector
in the Material header (populated by mkdocs-static-i18n's
`extra.alternate`), so the inline block is both redundant and
broken there.

This hook removes ONLY the first ``<div align="right">…</div>``
block, and ONLY on the three README pages — so the GitHub-rendered
README is completely untouched (hooks run at mkdocs build time
only), and no tri-locale content edit is needed.
"""
from __future__ import annotations

import re

# The switcher is always the very first element of the README; the
# banner that follows is <div align="center"> (different), so a
# non-greedy first-match on align="right" is safe.
#
# Smoke test (local):
#   python scripts/build-docs-tree.py && python -m mkdocs build
#   grep -c 'align="right"' _build/site/index.html   # expect 0
# If the README switcher markup ever changes (e.g. gains a NESTED
# <div>, or becomes <p align="right">), this non-greedy pattern would
# stop at the inner </div> / not match — update it then. Failure mode
# is benign: the old (broken-on-site) switcher reappears, no build break.
_SWITCHER = re.compile(r'<div align="right">.*?</div>\s*', re.DOTALL)
# The root README is staged as `about.md` (see build-docs-tree.py), so the
# switcher-strip now targets the renamed page.
_ABOUT_BASENAMES = {"about.md", "about.en.md", "about.zh-Hans.md"}

# Rewrite in-content links to the root README (now `about.md`) -> about, so
# they resolve on the site. A leading `examples/` breaks the `(?:\.\./)*`
# prefix match, so examples/.../README.md links are left untouched.
_README_LINK = re.compile(r'(\]\((?:\.\./)*)README((?:\.en|\.zh-Hans)?\.md)')


def on_page_markdown(markdown: str, *, page, config, files) -> str:
    src = (getattr(page.file, "src_path", "") or "").replace("\\", "/")
    basename = src.rsplit("/", 1)[-1]
    markdown = _README_LINK.sub(r"\1about\2", markdown)
    if basename in _ABOUT_BASENAMES:
        markdown = _SWITCHER.sub("", markdown, count=1)
    return markdown
