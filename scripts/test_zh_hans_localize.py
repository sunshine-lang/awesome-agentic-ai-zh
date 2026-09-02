#!/usr/bin/env python3
"""Regression tests for scripts/zh-hans-localize.py's substitution rules.

This script is a BLOCKING CI gate that REWRITES tracked files, and until now
nothing tested its substitution logic at all — the same shape as issue #102,
where the link checker's verdict lived in an untested function.

What that cost, concretely: 影片→视频 was excluded from `VOCAB` entirely,
because 影片 is a substring of 投影片 (projected slides) and a blanket
`str.replace` would produce 投视频. The exclusion was correct about the
collision and wrong about the remedy — it left FIVE genuine Taiwan residues in
tracked zh-Hans files while this gate reported "clean — no drift". The
warn-only lint job could see them the entire time.

An exclusion is invisible. A guarded rule is testable. These tests pin both
halves: the term IS localized, and the host word is NOT corrupted.

Run:  python scripts/test_zh_hans_localize.py     (plain asserts, no pytest)
 or:  pytest scripts/test_zh_hans_localize.py
"""
from __future__ import annotations

import importlib.util
import re
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO / "scripts"))

_SPEC = importlib.util.spec_from_file_location(
    "zh_hans_localize", Path(__file__).with_name("zh-hans-localize.py")
)
zhl = importlib.util.module_from_spec(_SPEC)
_SPEC.loader.exec_module(zhl)


def _localize(text: str) -> str:
    return zhl.localize(text)[0]


def _counts(text: str) -> dict[str, int]:
    return zhl.localize(text)[1]


# --- the guarded rule: both halves -----------------------------------------

def test_video_is_localized() -> None:
    assert _localize("先看 1-2 个影片") == "先看 1-2 个视频"
    assert _localize("影片优先") == "视频优先"


def test_slides_are_not_corrupted() -> None:
    """THE collision. 投影片 contains 影片; a blanket replace yields 投视频.

    This is not hypothetical — the zh-TW canonical
    stages/03-tool-use-and-hello-agent.md has 影片優先 on line 63 and 投影片 on
    line 67, four lines apart in one section. The zh-Hans mirror carried the
    same pair until it was localized; the canonical still does, so any future
    port of that section brings the collision straight back.
    """
    assert _localize("官方页含投影片 + YouTube 链接") == "官方页含投影片 + YouTube 链接", (
        "投影片 (slides) was corrupted — this is exactly why the rule used to be "
        "dropped entirely instead of guarded"
    )
    assert "投视频" not in _localize("投影片"), "produced the 投视频 corruption"


def test_slides_survive_ordinary_markdown_between_the_two_halves() -> None:
    """A literal-adjacency lookbehind is not enough, and the gap is plain
    markdown rather than anything exotic.

    Review found every one of these produced 投视频 under `(?<!投)影片`:
    bolding or italicising half a compound word, linking half of it, or simply
    wrapping the line between the two characters. All are normal edits in a
    docs repo whose prose is full of `**emphasis**`.
    """
    for src in [
        "投**影片**格式",
        "投*影片*格式",
        "投_影片_格式",
        "投~影片~格式",
        "投[影片](https://x)格式",
        "投\n影片",
        "投 影片",
        "投(影片)格式",
    ]:
        got = _localize(src)
        assert "视频" not in got, (
            f"{src!r} -> {got!r}: the slides word was split by markdown and the "
            "guard missed it, producing the 投视频 corruption"
        )


def test_slides_survive_an_inline_code_span_between_the_two_halves() -> None:
    """The nastiest variant: `_mask` replaces inline code with a \\x00N\\x00
    placeholder, so the guard no longer sees literal adjacency at all."""
    got = _localize("投`x`影片")
    assert "视频" not in got, f"masked-span split defeated the guard: {got!r}"
    assert "`x`" in got, "inline code was not restored"


def test_a_paragraph_break_ends_the_separator() -> None:
    """"Protect when unsure" must not decay into "never substitute".

    Without a boundary, a separator run stops meaning "emphasis around half a
    word" and starts joining sentences: a paragraph ending in a bare 投, then a
    horizontal rule or a bullet, then a genuine 影片 — all read as one word and
    left in Taiwan form.

    The boundary is a BLANK LINE, not a character budget. A length bound was
    tried first and was measurably worse: at {0,3} the ordinary
    `投 **[影片](url)**` needs four separator characters, falls out of the guard,
    and comes out as 投 **[视频](url)**. Narrowing does not make the guard safer
    — it makes it protect less, and under-protection is what silently rewrites
    files. Markdown emphasis never spans a blank line, so that is the honest cut.
    """
    for src in [
        "值得投\n\n***\n\n影片",
        "值得投\n\n* 影片教學",
        "值得投\n\n---\n\n影片",
        "值得投\n  \n影片",        # blank line carrying trailing spaces
        "值得投\r\n\r\n影片",      # CRLF
    ]:
        got = _localize(src)
        assert "视频" in got, (
            f"{src!r} -> {got!r}: the separator bridged a paragraph break, so a "
            "genuine 影片 was wrongly treated as part of 投影片"
        )


def test_long_but_unbroken_markdown_still_protects_the_slides_word() -> None:
    """The other half of the same decision: no ceiling below a paragraph break.

    `投 **[影片](url)**` is four separator characters and entirely ordinary. A
    length-bounded separator corrupted exactly this.
    """
    for src in [
        "投 **[影片](x)**",
        "投  **_[影片](x)_**  ",
        "投\r\n影片",
    ]:
        got = _localize(src)
        assert "视频" not in got, (
            f"{src!r} -> {got!r}: legitimate markdown around the second half of "
            "投影片 was not recognised, corrupting the word"
        )


def test_guard_protects_rather_than_guesses() -> None:
    """The two errors are not symmetric. A missed substitution leaves a visible
    Taiwan word that the warn-only lint job still reports; a wrong one silently
    corrupts a word in a gate that REWRITES tracked files. So when the context
    is ambiguous the guard must decline, not guess."""
    assert _localize("投 影片") == "投 影片", "guessed instead of protecting"
    # ...but an unambiguous standalone occurrence must still be localized,
    # otherwise "protect when unsure" degenerates into "never substitute".
    assert _localize("這個影片") == "這個视频"


def test_both_in_one_line_are_handled_independently() -> None:
    """The guard must be per-occurrence, not per-line: a line containing the
    host word must still get its OTHER occurrences localized."""
    got = _localize("投影片和影片不一样")
    assert got == "投影片和视频不一样", got


def test_guarded_rule_is_actually_registered() -> None:
    """Positive assertion, not a loop over the structure under test.

    Iterating GUARDED_VOCAB to check its contents would pass vacuously the
    moment someone empties it — the exact shape that let a mutation survive in
    scripts/test_check_links.py twice.
    """
    labels = [label for _, _, label in zhl.GUARDED_VOCAB]
    assert "影片→视频" in labels, (
        f"the guarded 影片 rule is gone; removing it silently stops localizing "
        f"a term that has real occurrences in this repo. got {labels!r}"
    )
    assert any(isinstance(p, re.Pattern) for p, _, _ in zhl.GUARDED_VOCAB), (
        "guarded rules must be regexes — a plain string here would reintroduce "
        "the blanket-replace corruption the guard exists to prevent"
    )


def test_video_is_not_in_the_blanket_vocab() -> None:
    """Moving it back into VOCAB would reintroduce the 投视频 corruption, and
    the guard above would no longer be reached first."""
    assert "影片" not in zhl.VOCAB, (
        "影片 is in the blanket VOCAB again; str.replace cannot express the "
        "投影片 exception, so this corrupts every 投影片 in the tree"
    )


# --- the rules the guard must not have broken ------------------------------

def test_core_vocabulary_still_applies() -> None:
    # Spelled out, not iterated — emptying VOCAB must fail this.
    for tw, cn in [("呼叫", "调用"), ("印出", "打印"), ("函式", "函数"),
                   ("使用者", "用户"), ("命令列", "命令行")]:
        assert _localize(f"這裡{tw}那裡") == f"這裡{cn}那裡", f"{tw}→{cn} regressed"


def test_corner_brackets_become_curly_quotes() -> None:
    assert _localize("他說「好」") == "他說“好”"


def test_code_is_never_rewritten() -> None:
    """The script writes files, so a substitution landing inside a sample is
    silent corruption of shipped code, not a cosmetic issue."""
    fenced = "文字影片\n\n```python\nx = '影片'  # 呼叫\n```\n"
    got = _localize(fenced)
    assert "x = '影片'" in got, "a fenced code sample was rewritten"
    assert "# 呼叫" in got, "a comment inside a fence was rewritten"
    assert "文字视频" in got, "prose outside the fence was NOT localized"

    inline = "看 `影片` 這個字，還有影片"
    got = _localize(inline)
    assert "`影片`" in got, "inline code was rewritten"
    assert "還有视频" in got, "prose after inline code was not localized"


def test_counts_report_what_changed() -> None:
    c = _counts("影片影片投影片")
    assert c.get("影片→视频") == 2, (
        f"count must exclude the guarded occurrence, got {c!r}"
    )
    assert _counts("没有任何要改的") == {}


def test_protect_list_is_exact() -> None:
    """These two files intentionally contain TW↔mainland PAIRS as reference
    tables; localizing them turns `| 使用者 | 用户 |` into `| 用户 | 用户 |`.
    Exact equality — widening this set silently stops localizing real files."""
    assert zhl.PROTECT == {
        "resources/style-guide.zh-Hans.md",
        "resources/glossary.zh-Hans.md",
    }, f"got {zhl.PROTECT!r}"


# --- the tree itself --------------------------------------------------------

def test_repo_is_currently_clean() -> None:
    """--check must pass on the committed tree. Runs the real gate."""
    r = subprocess.run(
        [sys.executable, str(REPO / "scripts" / "zh-hans-localize.py"), "--check"],
        cwd=REPO, capture_output=True, text=True, encoding="utf-8",
        errors="replace",
    )
    assert r.returncode == 0, (
        f"zh-hans-localize --check reports drift:\n{r.stdout[-1500:]}"
    )


def test_no_tracked_zh_hans_file_still_says_video_the_taiwan_way() -> None:
    """Per-file diagnostic for the 影片 rule, using the REAL rule.

    This deliberately does NOT re-derive "is this occurrence protected". The
    first version did — it hardcoded a single-character lookback (`text[i-1] ==
    "投"`) copied from the original guard — and the moment the guard widened to
    tolerate markdown between the two halves, the two disagreed: `localize()`
    correctly leaves `投**影片**` alone while that check called it unlocalized
    residue. A green `--check` and a red unit test, on content that is fine.

    Two implementations of one rule drift the moment one of them changes; the
    copy is always the one that gets forgotten. So the rule is consulted, not
    reimplemented.

    That makes this NOT an independent check of the rule — if `localize()` is
    wrong, this agrees with it. (The independent checks are the hand-written
    input/output pairs above.) What it still covers that
    `test_repo_is_currently_clean` does not is the FILE-DISCOVERY path: that one
    shells out to the CLI and exercises `REPO.rglob()` plus the worktree
    exclusions, this one uses `git ls-files`. A mismatch between the two would
    show up here and nowhere else — and a worktree copy shadowing the file list
    is a bug class this repo has already been bitten by.
    """
    files = subprocess.run(
        ["git", "ls-files", "*.zh-Hans.md"],
        cwd=REPO, capture_output=True, text=True, encoding="utf-8",
        errors="replace",
    ).stdout.split()
    bad = {}
    for rel in files:
        if rel in zhl.PROTECT:
            continue
        text = (REPO / rel).read_text(encoding="utf-8")
        n = zhl.localize(text)[1].get("影片→视频", 0)
        if n:
            bad[rel] = n
    assert not bad, (
        f"unlocalized 影片 (Taiwan) in tracked zh-Hans files: {bad} — run "
        "`python scripts/zh-hans-localize.py --apply`"
    )


def main() -> int:
    if hasattr(sys.stdout, "reconfigure"):
        try:
            sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        except Exception:
            pass
    tests = [(n, f) for n, f in sorted(globals().items())
             if n.startswith("test_") and callable(f)]
    failed = 0
    for name, fn in tests:
        try:
            fn()
        except AssertionError as e:
            failed += 1
            print(f"FAIL {name}\n  {e}")
        except BaseException as e:
            failed += 1
            print(f"ERROR {name}: {type(e).__name__}: {e}")
    if failed:
        print(f"\n{failed}/{len(tests)} failed.")
        return 1
    print(f"{len(tests)}/{len(tests)} passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
