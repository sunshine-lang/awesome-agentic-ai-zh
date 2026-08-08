#!/usr/bin/env python3
"""Regression tests for scripts/check-hans-chars.py.

Pins the 2026-08 gap: zh-hans-localize.py checks Taiwan VOCABULARY and quote style
only. Character-level 繁→簡 was assumed to have happened upstream at mirror-creation
time, so a Traditional character that was never converted was invisible to every gate
in the repo, permanently. 13 real residues were sitting in the corpus.

Two failure modes are pinned here because both were hit while building this:

  1. The tw2s trap. opencc's `tw2s` maps the Taiwan variant 么 -> 幺, so running it
     over correct Simplified text mangles 什么 -> 什幺 and produces ~880 false
     positives. The checker must use `t2s`. test_does_not_flag_simplified_me covers it.

  2. Over-eager flagging. Traditional characters are legitimate inside code blocks,
     inside markdown link targets (an anchor pointing at a zh-TW heading MUST keep that
     heading's Traditional spelling or the link 404s), in the locale proper name
     繁體中文, and in the shields.io badge block that is byte-identical across all three
     READMEs on purpose. Each exemption has a test.

Run:  python scripts/test_hans_chars.py     (plain asserts, no pytest needed)
 or:  pytest scripts/test_hans_chars.py
"""
import importlib.util
import tempfile
from pathlib import Path

_SPEC = importlib.util.spec_from_file_location(
    "check_hans_chars", Path(__file__).with_name("check-hans-chars.py")
)
chc = importlib.util.module_from_spec(_SPEC)
_SPEC.loader.exec_module(chc)

try:
    import opencc

    _CONVERT = opencc.OpenCC("t2s").convert
    _HAVE_OPENCC = True
except ImportError:  # pragma: no cover - CI installs it
    _CONVERT = None
    _HAVE_OPENCC = False


def _residue(body: str):
    """Write body to a temp .zh-Hans.md and return the checker's findings."""
    with tempfile.TemporaryDirectory() as d:
        fp = Path(d) / "page.zh-Hans.md"
        fp.write_text(body, encoding="utf-8")
        return chc.residue_in_file(fp, _CONVERT)


# --- the core invariant -----------------------------------------------------

def test_flags_traditional_in_prose():
    hits = _residue("最重要的是**不要跳过 動手練習**，光读过去会卡住。\n")
    assert len(hits) == 1, hits
    assert set("動練習") <= set(hits[0][1]), hits[0][1]


def test_clean_simplified_passes():
    assert _residue("每个 stage 的动手练习都是不动手就学不会的东西。\n") == []


def test_flags_single_stray_char():
    # The catalog's real residue: 正規 inside otherwise-Simplified prose.
    hits = _residue("等正規 MCP 出现再加进来。\n")
    assert len(hits) == 1 and "規" in hits[0][1]


def test_reports_line_number():
    hits = _residue("第一行没问题。\n\n第三行有 邏輯 问题。\n")
    assert len(hits) == 1 and hits[0][0] == 3, hits


# --- the tw2s trap ----------------------------------------------------------

def test_does_not_flag_simplified_me():
    """什么/怎么 are correct Simplified. tw2s would mangle them to 什幺/怎幺."""
    assert _residue("这是什么？怎么用这份文件？为什么要这样做？\n") == []


# --- exemptions -------------------------------------------------------------

def test_ignores_fenced_code():
    body = "正常的简体行。\n\n```bash\n# 這是繁體的範例輸出\necho 檔案\n```\n\n又一行简体。\n"
    assert _residue(body) == []


def test_ignores_inline_code():
    assert _residue("设定项叫 `動手練習` 这个 key。\n") == []


def test_ignores_link_targets():
    """An anchor pointing at a zh-TW heading must keep its Traditional spelling."""
    body = "详见 [Stage 5.3](05-claude-code-ecosystem.md#53--skillsclaude-code-的行為層)。\n"
    assert _residue(body) == []


def test_flags_traditional_in_link_DISPLAY_text():
    """Only the target is exempt — visible link text still has to be Simplified."""
    hits = _residue("详见 [動手練習](exercises.zh-Hans.md)。\n")
    assert len(hits) == 1 and "動" in hits[0][1]


def test_ignores_locale_proper_name():
    body = "> [繁體中文](./README.md) | **简体中文** | [English](./README.en.md)\n"
    assert _residue(body) == []


def test_ignores_shields_badge_line():
    body = "[![繁中](https://img.shields.io/badge/語言-繁體中文-red?style=flat)](README.md)\n"
    assert _residue(body) == []


def test_badge_exemption_is_line_scoped():
    """A badge on one line must not exempt Traditional prose on another."""
    body = (
        "[![繁中](https://img.shields.io/badge/語言-繁體中文-red)](README.md)\n"
        "这一行有 選定 的问题。\n"
    )
    hits = _residue(body)
    assert len(hits) == 1 and hits[0][0] == 2 and "選" in hits[0][1]


# --- config wiring ----------------------------------------------------------

def test_style_guide_exemption_is_scoped_to_table_rows():
    """Its conversion table's left column is Traditional on purpose — but ONLY
    the table. Prose elsewhere in that file must still be checked."""
    pat = chc.EXEMPT_FILES["resources/style-guide.zh-Hans.md"]
    assert pat.match("| 專案 | 项目 |"), "table row should be exempt"
    assert not pat.match("這句繁體散文不該被豁免。"), "prose must NOT be exempt"


def test_exempt_line_predicate_applies():
    """A file-scoped exemption skips matching lines and nothing else."""
    import re as _re
    with tempfile.TemporaryDirectory() as d:
        fp = Path(d) / "page.zh-Hans.md"
        fp.write_text("| 專案 | 项目 |\n這行繁體散文要被抓到。\n", encoding="utf-8")
        hits = chc.residue_in_file(fp, _CONVERT, _re.compile(r"^\s*\|"))
    assert len(hits) == 1 and hits[0][0] == 2, hits


def test_scrub_strips_all_three_spans():
    out = chc.scrub("a `碼` b [x](y.md#檔案) c 繁體中文 d")
    assert "碼" not in out and "檔案" not in out and "繁體中文" not in out
    assert "a " in out and " d" in out


def test_repo_is_currently_clean():
    """The corpus itself must stay clean — this is the gate's live assertion."""
    import subprocess
    import sys

    script = Path(__file__).with_name("check-hans-chars.py")
    r = subprocess.run(
        [sys.executable, str(script), "--quiet"],
        capture_output=True,
        text=True,
        # Explicit utf-8: the child prints CJK and ✓/❌, and a Windows console
        # defaults to cp950 here — without this the failure message itself
        # raises UnicodeDecodeError and hides what actually went wrong.
        encoding="utf-8",
        errors="replace",
        cwd=str(Path(__file__).resolve().parent.parent),
    )
    assert r.returncode == 0, f"residue present:\n{r.stdout}\n{r.stderr}"


def _run_all(require_opencc: bool = False):
    if not _HAVE_OPENCC:
        print("  SKIP  opencc not installed (pip install opencc-python-reimplemented)")
        # Without --require-opencc this exits 0 so a contributor without the dep
        # is not blocked. CI passes --require-opencc so a broken/absent install
        # fails loudly instead of turning the whole suite into a silent no-op —
        # a test runner that exits green having run zero tests is worse than none.
        return 1 if require_opencc else 0
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
    sys.exit(1 if _run_all("--require-opencc" in sys.argv) else 0)
