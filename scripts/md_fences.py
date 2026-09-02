#!/usr/bin/env python3
"""One fenced-code-block parser for every gate in this repo.

WHY THIS MODULE EXISTS (issues #95, #97)

Seven scripts here needed to know "which lines are code", and six of them had
written their own version of the rule. Every one of those six was wrong in at
least one way, and one of them shipped a defect: four `##` headings rendered as
code on the published site in all three locales while every gate read green,
because `check-anchors.py` and the renderer disagreed about which lines were
code. A gate that disagrees with the renderer is validating a document nobody
publishes.

The rules the naive "toggle on any ``` line" version gets wrong:

1. **A closing fence may not carry an info string.** Given

       ```                <- opens
       ```python          <- info string, so CONTENT, not a closer
       ...
       ```                <- closes the block opened on line 1
       ```                <- OPENS a new one

   a toggler pairs 1-2 and 3-4; the renderer pairs 1-3 and leaves 4 opening an
   unterminated block. That is #95 verbatim.

2. **A closing fence must be at least as long as its opener.** This is how a
   block legitimately contains a shorter fence, and it is how the file in #95
   was fixed (outer fence widened to ````).

3. **A fence can live inside a blockquote.** None of the six line-based
   parsers handled `> ```bash`; only `zh-hans-localize.py`'s DOTALL regex did,
   by ignoring line structure entirely. So the shared parser has to be at least
   as good as the BEST of the six on every axis, not the average — hence the
   blockquote support here.

4. **`~~~` fences exist**, and a backtick fence cannot be closed by a tilde one
   (or vice versa).

5. **A backtick info string may not itself contain a backtick.** ```foo`bar is
   not a fence opener. CommonMark says so and pymdownx.superfences agrees (its
   language class is a word/#/./+/- class with no backtick).

KNOWN DEVIATIONS, deliberate. This follows CommonMark, which is what GitHub
renders and what `check-anchors.py` validates against. The site's renderer
(pymdownx.superfences) differs in corners; each is listed so nobody reads
"follows CommonMark" as "matches the site exactly":

  * 1-3 space indent at top level — CommonMark/GitHub treat it as a fence;
    superfences only honours indentation matching the container's content
    indent, so at top level it renders as a paragraph. Inside a list item both
    agree it is code, and that case IS live in this repo (CLAUDE.md).
  * Unterminated fence at EOF — runs to end of document, as GitHub does;
    superfences declines to make a block. Warns when a source is named.
  * 4-space indented code blocks — not handled. No fence marker in this repo is
    indented that far.

Usage:  from md_fences import strip_code_blocks, code_line_flags, fence_marker_count
Tests:  scripts/test_check_anchors.py
"""
from __future__ import annotations

import re

__all__ = [
    "strip_code_blocks",
    "code_line_flags",
    "fence_marker_count",
    "FENCE_RE",
    "BLOCKQUOTE_PREFIX_RE",
]

# Leading blockquote markers, e.g. "> ", ">> ", "  > > ". Captured separately so
# a fence inside a quote is recognised and only closed at the same quote depth.
BLOCKQUOTE_PREFIX_RE = re.compile(r"^(\s*(?:>\s?)*)(.*)$")

# A fence marker: 3+ backticks or tildes, up to 3 leading spaces, then the info
# string (which must be empty for a closer).
FENCE_RE = re.compile(r"^ {0,3}(`{3,}|~{3,})(.*)$")


def _split_quote(line: str) -> tuple[int, str]:
    """Return (blockquote depth, the line with its quote markers removed).

    When there is no quote marker the line is returned UNCHANGED, indentation
    included. BLOCKQUOTE_PREFIX_RE's leading whitespace class matches even with
    zero `>`, so stripping unconditionally would hand FENCE_RE a left-trimmed
    line and its up-to-3-space bound would never fire — a lone fence indented
    four spaces (an indented code block, not a fence) would then open a block
    and swallow the rest of the document.
    """
    m = BLOCKQUOTE_PREFIX_RE.match(line)
    prefix, body = m.group(1), m.group(2)
    depth = prefix.count(">")
    if depth == 0:
        return 0, line
    return depth, body


class _Walk:
    """One pass: per-line (is_code, is_marker), plus any still-open fence."""

    __slots__ = ("rows", "unterminated")

    def __init__(self, rows, unterminated):
        self.rows = rows
        self.unterminated = unterminated


def _walk(content: str) -> _Walk:
    """THE state machine, in one place.

    `code_line_flags` and `fence_marker_count` both wrap this. They were briefly
    two hand-transcribed copies of the same rules — precisely the drift shape
    this module exists to eliminate, reintroduced inside the module written to
    hold one copy. Review caught it. Neither caller re-walks anything now.

    `is_marker` is True only for a line that OPENS or CLOSES a block. A fence
    line that is merely content — a shorter nested fence, or one carrying an
    info string where a closer is required — is (is_code=True, is_marker=False).
    """
    rows: list[tuple[bool, bool]] = []
    fence_char: str | None = None
    fence_len = 0
    fence_depth = 0

    for line in content.split("\n"):
        depth, body = _split_quote(line)

        if fence_char is not None and fence_depth > 0 and depth < fence_depth:
            # The quote ended, so the fence inside it ended too. Two things this
            # must NOT do:
            #   * require the line to be non-blank — a BLANK line ends a
            #     blockquote as surely as prose does, and treating it as
            #     continuation left the rest of the file masked, silently.
            #   * skip the line — the bail line may itself be a fence opener,
            #     and consuming it turns a closer into an opener one line later.
            # So: close the fence and fall through to normal handling.
            fence_char, fence_len, fence_depth = None, 0, 0

        m = FENCE_RE.match(body)
        if m:
            marker, rest = m.group(1), m.group(2)
            char = marker[0]

            if fence_char is None:
                # Opening fence. An info string is allowed here, except that a
                # backtick info string may not contain a backtick. Treating
                # ```foo`bar as an opener would hide the rest of the file from
                # the caller while the renderer keeps rendering it — the same
                # divergence shape as #93/#95.
                if char == "`" and "`" in rest:
                    rows.append((False, False))
                    continue
                fence_char, fence_len, fence_depth = char, len(marker), depth
                rows.append((True, True))
                continue

            # Inside a block: only a bare fence of the same character, at least
            # the opener's length, at the same quote depth, closes it.
            if (
                char == fence_char
                and len(marker) >= fence_len
                and not rest.strip()
                and depth == fence_depth
            ):
                fence_char, fence_len, fence_depth = None, 0, 0
                rows.append((True, True))
                continue

            rows.append((True, False))
            continue

        rows.append((fence_char is not None, False))

    unterminated = (fence_char, fence_len) if fence_char is not None else None
    return _Walk(rows, unterminated)


def code_line_flags(content: str, source: str | None = None) -> list[bool]:
    """One bool per line: is this line part of a fenced code block?

    The primitive most consumers share. Fence marker lines count as code, so a
    caller that blanks or masks by flag removes the whole construct.

    Callers differ in what they DO with it — check-anchors blanks the lines,
    zh-hans-localize masks and later restores them — so the shared piece is the
    classification, not the transformation.

    `source` names the file for the unterminated-fence warning. Left as None
    (the default) this is silent, so unit-test fixtures that use unterminated
    fences on purpose do not emit CI annotations.
    """
    walk = _walk(content)

    if walk.unterminated is not None and source is not None:
        char, length = walk.unterminated
        # stdout, matching the ::warning:: convention used elsewhere in these
        # gates. An unterminated fence means everything after it was skipped;
        # doing that silently is how a gate validates less and still prints its
        # success line.
        print(
            f"::warning::{source}: unterminated {char * length} fence — "
            f"the caller skipped everything after it"
        )

    return [is_code for is_code, _ in walk.rows]


def fence_marker_count(content: str) -> int:
    """How many fence MARKER lines the document has (openers + closers).

    Exposed here rather than left to callers, because deriving it from
    `code_line_flags` is wrong: two blocks with no blank line between them are
    one contiguous run of True, so a run-boundary count reports 1 block where
    there are 2. check-mirror-parity uses this as a structural metric, and a
    metric that drops on one side of a trio is either a false deficit or a
    masked real one.

    An unterminated fence contributes its opener only, which is honest — there
    is no closer. Note the consequence for a caller that halves this to get a
    block count: an odd total rounds the last block away, so this and
    `code_line_flags` CAN disagree about whether a block exists. It only ever
    under-reports, so it cannot manufacture a deficit that is not there.
    """
    return sum(1 for _, is_marker in _walk(content).rows if is_marker)


def strip_code_blocks(content: str, source: str | None = None) -> str:
    """Blank out fenced code blocks, leaving everything else untouched.

    Lines are blanked rather than deleted so line numbers stay correct for
    diagnostics that cite them.
    """
    lines = content.split("\n")
    return "\n".join(
        "" if in_code else line
        for line, in_code in zip(lines, code_line_flags(content, source))
    )
