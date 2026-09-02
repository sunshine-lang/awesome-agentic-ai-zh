"""Regression tests for scripts/refresh-stars.py star-line detection + write-back.

Run: python scripts/test_refresh_stars.py   (plain asserts, no pytest needed)
 or: pytest scripts/test_refresh_stars.py

Pins the 2026-07 bug fix: the --apply write-back must target the ★'s own line,
NOT the URL line (entry-block formats — Track A mirrors, branch files, the
mcp-skills-catalog `| Stars |` rows — were silently no-op'd for ~8 weekly runs),
AND Step-2 lookahead must not leak a neighbouring table row's ★.
"""
import importlib.util
from pathlib import Path

_SPEC = importlib.util.spec_from_file_location(
    "refresh_stars", Path(__file__).with_name("refresh-stars.py")
)
rs = importlib.util.module_from_spec(_SPEC)
_SPEC.loader.exec_module(rs)


def _detect(md: str):
    """Return {url_line_idx: (declared, text, star_idx)} for every GitHub URL."""
    lines = md.splitlines()
    out = {}
    for i, line in enumerate(lines):
        if rs.GITHUB_RE.search(line):
            out[i] = rs.detect_stars(lines, i)
    return out


def test_github_dir_excluded_from_scan():
    # .github/outreach drafts carry historical ("week 1 ★525") + cross-repo
    # (Langchain-Chatchat ★37k) star mentions that must NOT be auto-refreshed.
    # 2026-07 incident: the bot rewrote 7 of them to this repo's current count.
    assert ".github" in rs.EXCLUDE_DIRS
    scanned = rs.find_md_files(rs.REPO_ROOT)
    leaked = [fp for fp in scanned if ".github" in fp.parts]
    assert not leaked, f"refresh-stars must not scan .github/: {leaked[:3]}"


def test_same_line_table():
    res = _detect("| [repo](https://github.com/a/b) | desc | ★ 80k+ |")
    declared, text, star_idx = res[0]
    assert declared == 80000
    assert star_idx == 0            # ★ on the same line as the URL
    assert text == "★ 80k+"


def test_entry_block_next_line():
    md = "#### [repo](https://github.com/a/b) ⭐⭐⭐⭐\n★ 23k+ · Apache-2.0 — desc"
    declared, text, star_idx = _detect(md)[0]
    assert declared == 23000
    assert star_idx == 1           # ★ on the line AFTER the URL heading


def test_entry_block_metadata_table_after_blank():
    md = (
        "### [repo](https://github.com/a/b) ⭐⭐⭐⭐\n"
        "\n"
        "| Field | Value |\n"
        "|---|---|\n"
        "| Stars | ★ 34 |\n"
        "| License | MIT |\n"
    )
    declared, text, star_idx = _detect(md)[0]
    assert declared == 34
    assert star_idx == 4           # the `| Stars | ★ 34 |` row, past the blank line


def test_table_row_no_star_does_not_leak_neighbour():
    # repoA's row has no ★; the NEXT table row (repoB) does. The old code looked
    # ahead and stole repoB's ★ for repoA. Now repoA must report no stars.
    md = (
        "| | [repoA](https://github.com/a/aa) | no star here |\n"
        "| | [repoB](https://github.com/b/bb) | ★ 20k+ |\n"
    )
    res = _detect(md)
    assert res[0][0] is None        # repoA: NO leak from repoB
    assert res[1][0] == 20000       # repoB: its own ★
    assert res[1][2] == 1


def test_writeback_targets_star_line_not_url_line():
    # End-to-end: an entry-block drift must rewrite the ★ line, leaving the URL
    # heading untouched. Reproduces the exact silent-no-op bug.
    lines = "#### [repo](https://github.com/a/b) ⭐⭐⭐⭐\n★ 120k+ — old\n".splitlines()
    declared, text, star_idx = rs.detect_stars(lines, 0)
    assert star_idx == 1 and text == "★ 120k+"
    assert text in lines[star_idx]            # the fixed write-back guard passes on the ★ line
    assert text not in lines[0]               # keying on the URL line (old bug) would have no-op'd
    lines[star_idx] = lines[star_idx].replace(text, f"★ {rs.fmt_stars(138000)}", 1)
    assert lines[star_idx] == "★ 138k+ — old"
    assert lines[0] == "#### [repo](https://github.com/a/b) ⭐⭐⭐⭐"  # heading untouched


def test_prose_leak_from_later_unrelated_url_is_blocked():
    # repoA has no ★ of its own; repoB (a different, LATER url) does. repoA must
    # NOT borrow repoB's count. This is the real 2026-07 corruption found live in
    # langchain-ai.md / stages 03,05,06,07 (15 occurrences): with the star-line
    # write-back, borrowing would overwrite repoB's own correct ★ with repoA's count.
    md = (
        "1. [repoA](https://github.com/a/aa) — no star here\n"
        "2. [repoB](https://github.com/b/bb) — ★ 9k+ its own count\n"
    )
    res = _detect(md)
    assert res[0][0] is None       # repoA: no leak from repoB
    assert res[1][0] == 9000       # repoB: its own ★, unaffected


def test_missing_stars_falls_back_to_url_line():
    md = "#### [repo](https://github.com/a/b) ⭐⭐⭐⭐\n\nsome prose, no stars\n"
    declared, text, star_idx = _detect(md)[0]
    assert declared is None
    assert star_idx == 0           # falls back to the URL line for the missing report


def test_is_real_drift_ignores_render_noop():
    """Over-threshold but rendering to the SAME text must not count as drift.

    Calls the same predicate main() calls, so reverting the guard fails this test.
    pct is computed on the parsed int ("10k+" -> 10000) while write-back emits
    fmt_stars(latest) — "10k+" again below 11000. Measured 2026-08-10: 24 of 110.
    """
    assert rs.fmt_stars(10000) == rs.fmt_stars(10900)
    # 9% over threshold, but both render "10k+" -> not drift
    assert rs.is_real_drift(10000, 10900, 5) is False
    # a change that actually alters the rendered string IS drift
    assert rs.is_real_drift(10000, 12000, 5) is True
    # below threshold and identical rendering -> not drift
    assert rs.is_real_drift(10000, 10100, 5) is False
    # declared == 0 is always drift (nothing sensible to compare)
    assert rs.is_real_drift(0, 500, 5) is True


def test_apply_replacements_counts_only_real_changes():
    """Calls rs.apply_replacements directly — reverting the guard fails this test.

    The old code wrote and incremented files_changed unconditionally, which is how
    the tool self-reported "110 fixes across 44 files" when the truth was 86/38.
    """
    import tempfile, pathlib
    d = pathlib.Path(tempfile.mkdtemp())
    changed = d / "a.md"
    changed.write_text("| Stars | ★ 10k+ |\n", encoding="utf-8")
    untouched = d / "b.md"
    untouched.write_text("| Stars | ★ 12k+ |\n", encoding="utf-8")
    before_mtime = untouched.stat().st_mtime_ns

    applied, files_changed = rs.apply_replacements({
        changed:   [(1, "★ 10k+", "★ 12k+")],   # real change
        untouched: [(1, "★ 12k+", "★ 12k+")],   # queued, but a no-op
    })

    assert applied == 1, f"expected 1 real replacement, got {applied}"
    assert files_changed == 1, f"expected 1 file rewritten, got {files_changed}"
    assert "12k+" in changed.read_text(encoding="utf-8")
    assert untouched.stat().st_mtime_ns == before_mtime, "no-op file must not be rewritten"


def test_apply_replacements_skips_out_of_range_and_stale_lines():
    """A line number past EOF, or whose text has moved, must not be counted."""
    import tempfile, pathlib
    d = pathlib.Path(tempfile.mkdtemp())
    fp = d / "c.md"
    fp.write_text("★ 10k+\n", encoding="utf-8")

    applied, files_changed = rs.apply_replacements({
        fp: [(99, "★ 10k+", "★ 12k+"),      # past EOF
             (1, "★ 40k+", "★ 41k+")],      # text not on that line any more
    })
    assert (applied, files_changed) == (0, 0)
    assert fp.read_text(encoding="utf-8") == "★ 10k+\n"

def test_changelog_is_never_scanned():
    """CHANGELOG.md records what a count WAS; refreshing it falsifies history.

    Same class as the .github exclusion (2026-07: the bot overwrote historical
    launch stats and other repos' counts with this repo's current number). At
    at the v2026.08.11 tag CHANGELOG.md held 30 historical ★ with 0 bound to a
    repo, so --apply could not reach them yet; this pins it shut before a future
    entry pairs a repo URL with a ★ on one line. (The ★ total climbs with every
    changelog entry — "0 bound" is the figure that describes the exposure.)
    """
    assert "CHANGELOG.md" in rs.EXCLUDE_FILES
    scanned = rs.find_md_files(rs.REPO_ROOT)
    assert not [p for p in scanned if p.name == "CHANGELOG.md"], \
        "CHANGELOG.md must not be scanned"
    # The real file exists — otherwise this test would pass vacuously.
    assert (rs.REPO_ROOT / "CHANGELOG.md").is_file()


def test_excluded_file_is_never_rewritten_by_apply():
    """The exclusion has to hold on the WRITE path, not just the report.

    A filter that only hides a file from the report while --apply still edits it
    is the worst of both worlds: silent history corruption with no evidence in
    the log.

    Routes through the REAL find_md_files by pointing rs.REPO_ROOT at a temp
    corpus, rather than mocking find_md_files. The first version of this test
    mocked it with an inline copy of the exclusion check, which made it blind to
    exactly the regression that matters: deleting the filter from
    find_md_files() left this test passing, because it never called that
    function. It only caught an emptied EXCLUDE_FILES — which the simpler
    test_changelog_is_never_scanned already catches — so it was pure redundancy
    dressed up as write-path coverage.
    """
    import io, tempfile, pathlib, shutil, sys as _s
    from contextlib import redirect_stdout, redirect_stderr
    root = pathlib.Path(tempfile.mkdtemp())
    changelog = root / "CHANGELOG.md"
    # A repo URL and a ★ on ONE line — the shape that becomes rewritable the
    # moment the exclusion is gone. A sibling .md proves the corpus is live.
    changelog.write_text(
        "- bumped [alpha](https://github.com/acme/alpha) ★ 5k+ that week\n",
        encoding="utf-8")
    sibling = root / "page.md"
    sibling.write_text(
        "- [alpha](https://github.com/acme/alpha) ★ 5k+\n", encoding="utf-8")
    before = changelog.read_bytes()

    orig_root, orig_fetch, orig_argv = rs.REPO_ROOT, rs.fetch_stars, _s.argv
    rs.REPO_ROOT = root                                  # real find_md_files runs
    rs.fetch_stars = lambda repo, retries=2: 50_000      # 10x -> genuine drift
    _s.argv = ["refresh-stars.py", "--apply"]
    buf = io.StringIO()
    try:
        with redirect_stdout(buf), redirect_stderr(io.StringIO()):
            try:
                rs.main()
            except SystemExit:
                pass
        out = buf.getvalue()
        after = changelog.read_bytes()
        sibling_text = sibling.read_text(encoding="utf-8")
    finally:
        rs.REPO_ROOT, rs.fetch_stars, _s.argv = orig_root, orig_fetch, orig_argv
        shutil.rmtree(root, ignore_errors=True)

    assert after == before, "an excluded file was rewritten by --apply"
    # The sibling MUST have been rewritten — otherwise this test would pass
    # simply because nothing was ever eligible, and prove nothing at all.
    assert "★ 50k+" in sibling_text, f"corpus was not actually live: {sibling_text}"
    assert "Applied 1 drift fixes across 1 files" in out, out


def test_prose_stars_re_matches_every_locale_wording():
    """Prose counts must be seen in all three locales, ★-form must not be eaten.

    browser-use was documented as "86k stars" in 21 places across all three
    locales while the repo was at 108,651 (2026-08-10). No gate reported it,
    because STARS_RE only ever matched the `★ Nk+` render convention. My own
    first audit pass repeated the same blind spot in miniature: the scan regex
    used `顆星` and silently missed every zh-Hans `星`, under-reporting 33 as 24.
    """
    def val(s):
        m = rs.PROSE_STARS_RE.search(s)
        if not m:
            return None
        return int(float(m.group(1)) * {"k": 1_000, "m": 1_000_000}[m.group(2).lower()])

    assert val("OSS, 108k+ stars") == 108_000        # en
    assert val("OSS、108k+ stars") == 108_000        # zh-TW keeps the English word
    assert val("开源，108k+ 星") == 108_000          # zh-Hans
    assert val("開源，108k+ 顆星") == 108_000        # zh-TW long form
    assert val("1.5m stars") == 1_500_000
    assert val("8.8k+ stars") == 8_800

    # No star word -> not a count. "5 lines of Python" must never be read as one.
    assert val("5 lines of Python, 3k of docs") is None
    assert val("★ 12k+") is None                     # the STARS_RE path owns this


def test_prose_threshold_without_a_repo_url_is_not_a_count():
    """The catalog's "> 30k stars" inclusion bar names no repo — never a drift.

    Requiring the GitHub URL on the SAME line is what exempts it. This pins the
    exemption at the level main() actually applies it, not just the regex.
    """
    policy = "- CLI 工具市場變化快（門檻：> 30k stars + 維護中 + 真的 CLI 不是 IDE）"
    assert rs.PROSE_STARS_RE.search(policy), "the regex alone does match the bar..."
    assert not rs.GITHUB_RE.search(policy), "...but no repo URL, so main() skips it"

    entry = "| [**browser-use**](https://github.com/browser-use/browser-use) | 108k+ stars |"
    assert rs.GITHUB_RE.search(entry) and rs.PROSE_STARS_RE.search(entry)


def test_prose_drift_uses_the_same_predicate_as_star_drift():
    """A prose count that renders to the same string is not drift either."""
    assert rs.is_real_drift(86_000, 108_651, 10) is True      # the real case
    assert rs.is_real_drift(108_000, 108_651, 10) is False    # both render 108k+


def test_prose_threshold_is_decoupled_from_the_star_threshold():
    """The originating bug is a 26% gap, and CI runs the ★ path at 50%.

    lint.yml's star-drift job invokes `--threshold 50 --check`. If prose drift
    inherited that, browser-use (86k written, 108,651 live = 26%) would report
    ZERO — the new detector would be dead on the exact case it was built for.
    So prose gets its own default, and a STRICTER one: a ★ count self-heals on
    the next --apply, a prose count waits for a human, so the bar to tell the
    human has to be lower. UI-TARS (36k written, 38,545 live) is only 7% and
    needs the 5% default to surface at all.
    """
    assert rs.is_real_drift(86_000, 108_651, 50) is False   # what CI's ★ bar sees
    assert rs.is_real_drift(86_000, 108_651, 5) is True     # what prose must see
    assert rs.is_real_drift(36_000, 38_545, 10) is False    # 7% — a 10% bar hides it
    assert rs.is_real_drift(36_000, 38_545, 5) is True


def _run_main(argv, md_text, stars):
    """Drive the real main() over a one-file corpus. Returns (exit_code, stdout).

    Asserting on --help text (what the first version of these tests did) proves
    only that I wrote a help string. This runs the actual code path, so rewiring
    the prose comparison back to args.threshold — or letting the default drift
    from 5 to 10 while the help text still says 5 — fails here. Both of those
    survived the --help version.
    """
    import io, sys as _s
    from contextlib import redirect_stdout, redirect_stderr
    tmpdir = rs.REPO_ROOT / "_test_tmp_prose"      # inside REPO_ROOT: main() does
    tmpdir.mkdir(exist_ok=True)                    # fp.relative_to(REPO_ROOT)
    fp = tmpdir / "fixture.md"
    fp.write_text(md_text, encoding="utf-8")
    orig_find, orig_fetch, orig_argv = rs.find_md_files, rs.fetch_stars, _s.argv
    rs.find_md_files = lambda _root: [fp]
    rs.fetch_stars = lambda repo, retries=2: stars
    _s.argv = ["refresh-stars.py"] + argv
    buf = io.StringIO()
    try:
        with redirect_stdout(buf), redirect_stderr(io.StringIO()):
            try:
                rs.main()
                code = 0
            except SystemExit as e:
                code = e.code or 0
        return code, buf.getvalue()
    finally:
        rs.find_md_files, rs.fetch_stars, _s.argv = orig_find, orig_fetch, orig_argv
        fp.unlink(missing_ok=True)
        tmpdir.rmdir()


def test_prose_path_really_reads_prose_threshold_not_threshold():
    """End-to-end through main(), at CI's literal flags.

    Reviewer demonstrated the --help-based version of this test passed even after
    `is_real_drift(..., args.prose_threshold)` was rewired back to `args.threshold`.
    This one does not: with --threshold 50 the 26% browser-use gap must still be
    reported, which is only true if the prose path has its own bar.
    """
    md = "- [browser-use](https://github.com/browser-use/browser-use) — OSS, 86k+ stars\n"

    code, out = _run_main(["--threshold", "50", "--check"], md, 108_651)
    assert code == 1, "26% prose gap must fail --check even when ★ bar is 50"
    assert "Prose-form drift:      1" in out, out

    # And the flag must actually control it in the other direction.
    code, out = _run_main(["--threshold", "50", "--prose-threshold", "50", "--check"],
                          md, 108_651)
    assert code == 0, "--prose-threshold 50 must suppress a 26% gap"
    assert "Prose-form drift:      0" in out, out


def test_bind_re_matches_the_name_but_not_lookalikes():
    """Name-binding is how the no-URL prose counts got under the gate.

    12 counts in stage 08 (4 per locale) were prose sentences with no GitHub
    link, so the URL-anchored pass structurally could not see them: a table cell
    naming the tool without linking it, a bullet whose only link is the docs
    site, and two "why is it popular" sentences.
    """
    rx = rs.bind_re("browser-use/browser-use")
    assert rx.search("Why is browser-use so popular (108k stars)?")
    assert rx.search("為什麼 browser-use 這麼火")            # CJK neighbours
    assert rx.search("Comet / browser-use (OSS, 108k stars)")
    assert rx.search("[**browser-use docs**](https://docs.browser-use.com/)")
    # Lookalikes must NOT match — a false bind publishes repo B's count as A's.
    assert not rx.search("mcp-server-browserbase is archived")
    assert not rx.search("browser-useful things")
    assert not rx.search("my-browser-use-fork")

    # Short names are the risky case: 'cua' must not match inside another word.
    cua = rs.bind_re("trycua/cua")
    assert cua.search("cua is an open toolkit, 21k+ stars")
    assert not cua.search("cuatro")
    assert not cua.search("focus on this")


def test_generic_repo_names_never_bind():
    """"agents 12k+ stars" identifies nothing — this repo links several.

    Binding a generic short name would attribute one project's count to another,
    which is the exact failure the ★ path already had to fix (15 live leaks).
    """
    for repo in ("livekit/agents", "openai/agents", "anthropics/skills"):
        assert not rs.bind_re(repo).search(f"{repo.split('/')[-1]} has 12k+ stars"), repo
    # A distinctive name still binds.
    assert rs.bind_re("browser-use/browser-use").search("browser-use 12k+ stars")


def test_a_line_naming_two_repos_is_reported_not_guessed():
    """The `len(hits) == 1` rule, exercised through main() with a real fixture.

    The corpus-scan test above passes whether or not that rule exists, because
    no live line is ambiguous today — so it cannot catch a regression to "bind
    to whichever repo matched first". This one can: relaxing the rule to
    `>= 1` makes the ambiguous line bind and report drift, failing here.
    """
    md = (
        "- [alpha](https://github.com/acme/alpha) ★ 12k+\n"
        "- [beta](https://github.com/acme/beta) ★ 12k+\n"
        "Comparing alpha and beta: it sits around 5k+ stars today.\n"
    )
    code, out = _run_main(["--check"], md, 12_000)
    assert "Prose, unbindable:     1" in out, out
    assert "Prose-form drift:      0" in out, out
    assert "ambiguous" in out, out
    assert code == 0, "an unbindable count must not fail the check"


def test_binding_does_not_leak_across_files():
    """A repo linked only in file A must not bind a bare mention in file B.

    `file_repos` is built fresh inside the per-file loop. Hoisting it out — the
    kind of thing a "don't rebuild the set every iteration" refactor does — makes
    binding global, and then a file that merely NAMES a tool inherits a repo it
    never linked. That fails silently: no warning, no red exit, just someone
    else's star count published under the wrong project.

    Uses two fixture files, since _run_main's single-file corpus cannot express
    "linked over there, mentioned over here".
    """
    import tempfile, pathlib, io, sys as _s
    from contextlib import redirect_stdout, redirect_stderr
    d = rs.REPO_ROOT / "_test_tmp_scope"
    d.mkdir(exist_ok=True)
    linked = d / "linked.md"
    mentions = d / "mentions.md"
    # alpha is linked ONLY here.
    linked.write_text("- [alpha](https://github.com/acme/alpha) ★ 12k+\n", encoding="utf-8")
    # ...and merely named here, with a count. Must NOT bind.
    mentions.write_text("alpha is great, about 5k+ stars now.\n", encoding="utf-8")

    orig_find, orig_fetch, orig_argv = rs.find_md_files, rs.fetch_stars, _s.argv
    rs.find_md_files = lambda _root: [linked, mentions]
    rs.fetch_stars = lambda repo, retries=2: 12_000
    _s.argv = ["refresh-stars.py", "--check"]
    buf = io.StringIO()
    try:
        with redirect_stdout(buf), redirect_stderr(io.StringIO()):
            try:
                rs.main()
                code = 0
            except SystemExit as e:
                code = e.code or 0
        out = buf.getvalue()
    finally:
        rs.find_md_files, rs.fetch_stars, _s.argv = orig_find, orig_fetch, orig_argv
        linked.unlink(missing_ok=True)
        mentions.unlink(missing_ok=True)
        d.rmdir()

    assert "Prose, unbindable:     1" in out, out
    assert "Prose-form drift:      0" in out, out
    assert "names no linked repo" in out, out
    assert code == 0, "a cross-file mention must not be bound, so must not fail"


def test_no_repo_in_corpus_binds_a_prose_count_ambiguously():
    """Every prose count in the live corpus binds to 0 or 1 repo, never 2+.

    A 2+ case would mean main() had to choose, and it deliberately refuses —
    but this pins that the corpus has not drifted into needing that choice.
    """
    ambiguous = []
    for fp in rs.find_md_files(rs.REPO_ROOT):
        lines = fp.read_text(encoding="utf-8").splitlines()
        known = {}
        for line in lines:
            m = rs.GITHUB_RE.search(line)
            if m:
                r = rs.normalize_repo(m.group(1), m.group(2))
                if r:
                    known[r] = rs.bind_re(r)
        for n, line in enumerate(lines, 1):
            if "★" in line or rs.GITHUB_RE.search(line):
                continue
            if not rs.PROSE_STARS_RE.search(line):
                continue
            hits = [r for r, rx in known.items() if rx.search(line)]
            if len(hits) > 1:
                ambiguous.append(f"{fp}:{n} -> {hits}")
    assert not ambiguous, f"prose count naming 2+ linked repos: {ambiguous}"


def test_prose_threshold_default_is_5_not_10():
    """A 7% gap (UI-TARS 36k -> 38,545) must surface with no flag passed.

    Pins the default through real argparse. Changing `default=5` to `default=10`
    while leaving the help text saying 5 passed the previous version of this test.
    """
    md = "- [UI-TARS](https://github.com/bytedance/UI-TARS-desktop) — 36k+ stars\n"
    code, out = _run_main(["--check"], md, 38_545)
    assert code == 1, "7% prose gap must fail --check under the default bar"
    assert ">=5%" in out, f"default prose bar must print as 5%: {out}"


def test_prose_count_is_not_attributed_across_two_repos_on_one_line():
    """main() binds the prose count to GITHUB_RE's FIRST match on the line.

    The ★ path already learned this the hard way (15 live cross-entry leaks
    pre-fix). Nothing in the corpus hits it today — this pins the assumption so
    a future two-URL line fails loudly here instead of publishing repo B's star
    count under repo A's name.
    """
    two = ("- [a/aa](https://github.com/a/aa) vs "
           "[b/bb](https://github.com/b/bb) — 108k+ stars")
    urls = rs.GITHUB_RE.findall(two)
    assert len(urls) == 2
    assert len(rs.PROSE_STARS_RE.findall(two)) == 1
    # The count sits next to the SECOND repo but would bind to the first.
    first = rs.normalize_repo(*urls[0])
    assert first == "a/aa", "if this ever changes, re-check the binding in main()"

    # Live corpus must contain no such line, or the guarantee above is void.
    offenders = []
    for fp in rs.find_md_files(rs.REPO_ROOT):
        for n, line in enumerate(fp.read_text(encoding="utf-8").splitlines(), 1):
            if "★" in line:
                continue
            if len(rs.GITHUB_RE.findall(line)) > 1 and rs.PROSE_STARS_RE.search(line):
                offenders.append(f"{fp}:{n}")
    assert not offenders, f"multi-URL line with a prose star count: {offenders}"


def test_fetch_stars_retries_transient_failure_but_not_404():
    """A timeout must not be reported as a missing repo.

    Before the fix both outcomes were None, the caller printed None as "Repo not
    found (404)", and --check exited non-zero on it — so one transient blip turned
    CI red with a false public claim about a live repo (21st-dev/magic-mcp,
    2026-08-10 — live at 5,630 stars, reported not-found). Now a real 404 is
    FETCH_GONE and "could not determine" stays None.
    """
    calls = {"n": 0}

    class _R:
        def __init__(self, rc, out="", err=""):
            self.returncode, self.stdout, self.stderr = rc, out, err

    def flaky(*a, **k):
        calls["n"] += 1
        return _R(1, err="timeout") if calls["n"] == 1 else _R(0, "4242\n")

    orig_run, orig_sleep = rs.subprocess.run, rs.time.sleep
    rs.subprocess.run, rs.time.sleep = flaky, lambda *_: None
    try:
        assert rs.fetch_stars("a/b") == 4242, "transient failure should be retried"
        assert calls["n"] == 2

        calls["n"] = 0
        rs.subprocess.run = lambda *a, **k: (calls.__setitem__("n", calls["n"] + 1),
                                             _R(1, err="gh: Not Found (HTTP 404)"))[1]
        assert rs.fetch_stars("a/gone") is rs.FETCH_GONE, "a real 404 is terminal"
        assert calls["n"] == 1, "a 404 must not be retried"

        # And the exhausted-retry path must NOT masquerade as a 404.
        calls["n"] = 0
        rs.subprocess.run = lambda *a, **k: (calls.__setitem__("n", calls["n"] + 1),
                                             _R(1, err="HTTP 403 secondary rate limit"))[1]
        assert rs.fetch_stars("a/flaky") is None, "unknown must not collapse into FETCH_GONE"
        assert calls["n"] == 3, "non-404 failures are retried to exhaustion"
    finally:
        rs.subprocess.run, rs.time.sleep = orig_run, orig_sleep


if __name__ == "__main__":
    import sys
    tests = [v for k, v in sorted(globals().items()) if k.startswith("test_") and callable(v)]
    failed = 0
    for fn in tests:
        try:
            fn()
            print(f"  PASS  {fn.__name__}")
        except AssertionError as e:
            failed += 1
            print(f"  FAIL  {fn.__name__}: {e}")
    print(f"\n{len(tests) - failed}/{len(tests)} passed")
    sys.exit(1 if failed else 0)
