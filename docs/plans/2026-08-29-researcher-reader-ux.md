# Researcher Path Reader-UX Modernization Implementation Plan

**Goal:** Make the researcher path usable without opening any menu: readers can verify one paper, see the required reading, choose among current tools, and understand how to preserve evidence and reproduce work.

**Architecture:** Keep the eight core terms, first exercise, legacy anchors, and three locales. Move required reading and the complete curated table into the visible path; keep only setup/privacy/cost, advanced workflow, and troubleshooting in closed `<details>`. Add a distinct reproducibility/evidence group instead of duplicating more generative-research agents.

**Stack:** Branch from PR #177 (`codex/developer-reader-ux-stack`) and open one stacked PR. Do not merge, retarget, prune, or clean up without the user's explicit approval.

## Verified content decisions — 2026-08-29 UTC

- Preserve all existing ten tools. Keep `open_deep_research` only as archived history and lower its editorial rating.
- Correct ChatPaper's repository license to CC BY-NC-ND 4.0 rather than the vague “custom terms.”
- Keep AI Scientist v2 as a research reference and point to its custom source-code license and disclosure restrictions.
- Add ASReview, DVC, MLflow, Zenodo, and repo2docker. They answer five different questions: screening, data/pipeline versions, run/metric records, citable research outputs, and rebuildable environments.
- Display no volatile stars. Ratings remain this roadmap's five-level editorial judgment.

## Task 1 — Write the failing content contract

**Files:**

- Modify `scripts/test_role_paths.py`
- Modify `scripts/reader-ux-pages.yml`

Lock these outcomes before rewriting prose:

- 15 visible resources in real HTML row groups `3／4／5／2／1`.
- Six visible required-reading links.
- Exactly three closed `<details>` and no `open` attribute.
- Visible order: purpose → goals → core terms → first exercise → entry points → required reading → resources → completion.
- All eight bold terms remain before the exercise.
- The paper-verification prompt, three checks, privacy boundary, ratings, current statuses, licenses, limitations, and legacy anchors remain mirrored.
- The five new tools have stable official URLs and honest scope limits; archived or transitioning products cannot be framed as current defaults.

Run:

```powershell
python -m pytest scripts/test_role_paths.py scripts/test_reader_ux.py -q
```

Expected: fail against the current hidden reading/table and ten-resource contract.

## Task 2 — Rewrite zh-TW canonical

**File:** `branches/for-researcher.md`

- Keep the opening purpose, four goals, eight definitions, and first paper exercise.
- Keep the three-entry quick chooser, then show six required readings and the full 15-resource table.
- Use five true `rowspan` groups: start/organize, explore/write, reproducibility/evidence, research automation, history.
- Move the completion checklist after the visible resources so the page reads from learning to action to next stop.
- Keep setup/privacy/cost, the repeatable workflow, and troubleshooting closed.
- Put the quiet UTC verification note with the table, not in the teaching prose.

Run the targeted tests and inspect visible character count before translation.

## Task 3 — Mirror English and Simplified Chinese

**Files:**

- Modify `branches/for-researcher.en.md`
- Modify `branches/for-researcher.zh-Hans.md`

Translate the accepted canonical shape, then compare URL order, status, license, limits, ratings, dates, details state, and legacy anchors. Do not mechanically translate product names or legal labels.

## Task 4 — Update governance and freshness evidence

**Files:**

- Modify `stages/DESIGN.md`
- Modify `scripts/reader-ux-pages.yml`
- Modify `scripts/test_role_paths.py`
- Modify `scripts/repository-freshness-snapshot.json` if the repository inventory changes
- Modify `CHANGELOG.md`

Record that researcher required reading and curated resources are visible, while setup and advanced workflow detail remain folded. Refresh repository evidence only for newly referenced GitHub repositories and derive CHANGELOG content from the final diff.

## Task 5 — Verify, review, and publish the stacked PR

Run the reader-UX, anchor, mirror, locale, Hans, image, freshness, repository, docs-tree, complete `scripts` pytest, and MkDocs build gates. Stage explicit paths only, assert the staged file count, record `git write-tree`, and request one independent `code-reviewer` verdict on the stable fingerprint. Any byte changed after approval invalidates the verdict.

Suggested commit: `content(researchers): keep evidence and resources visible`

Suggested PR title: `docs(researchers): Keep evidence and resources visible`

Base branch: `codex/developer-reader-ux-stack`

Stop with the PR open and green. Do not merge or clean branches/worktrees.
