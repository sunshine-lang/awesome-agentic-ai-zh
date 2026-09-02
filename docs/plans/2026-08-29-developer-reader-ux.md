# Developer Path Reader-UX Implementation Plan

> **For Codex:** Use `bounded-agent-harness`, official product documentation, GitHub API evidence, delegated locale mirroring, and `verification-before-completion`. Keep this work stacked on PR #176. Do not merge, retarget, delete branches, or clean worktrees without the user’s approval.

**Goal:** Make the trilingual developer extension easy to follow without hiding required reading or curated projects, while keeping every important technical distinction and current tool state.

**Architecture:** Preserve the three filenames and all legacy anchors. The visible path becomes purpose → four goals → eight grouped core terms → tool-identity map → one copy-ready reversible-change exercise → five entry points → required reading → fourteen rated resources → completion. Only setup/cost, advanced workflows, and troubleshooting remain in closed details.

**Evidence date:** GitHub API UTC `2026-08-29`.

---

## Task 1: Freeze facts and the visible learning path

**Files:**

- Inspect: `branches/for-developer.md`
- Inspect: `branches/for-developer.en.md`
- Inspect: `branches/for-developer.zh-Hans.md`
- Modify: `docs/plans/2026-08-29-developer-reader-ux.md`

Keep these sections visible and ordered:

1. `📌` what the path solves.
2. `🎯` four learning goals.
3. `🧩` eight grouped core terms.
4. The OpenCode / Pi / OpenRouter / Ollama identity map.
5. `🛠` one copy-ready reversible-change exercise.
6. `📚` five entry choices.
7. `📖` six required readings.
8. `⭐` the full fourteen-resource table.
9. `✅` completion and next stops.

The eight grouped terms are:

- **IDE／Surface**
- **Coding Agent／Harness**
- **Provider／Router**
- **Model／Runtime**
- **Sandbox**
- **Approval**
- **Diff／Rollback**
- **Eval／Observability**

Grouping related words does not make them synonyms. Each definition must state the difference before the term is used in an exercise or table.

## Task 2: Verify current official sources and project status

Use official product documentation first and GitHub API for repository status, license, default branch, and last push. Do not use GitHub stars as evidence or as page content.

Required current sources:

- Claude Code overview, permissions, and sandboxing.
- OpenAI Codex CLI plus agent approvals and sandbox documentation.
- GitHub Copilot cloud agent versus IDE agent mode.
- OpenCode documentation and repository.
- Pi documentation and security boundary: no built-in permission sandbox.
- OpenRouter provider routing and Ollama local-runtime documentation.
- Official README/status for Continue and GitHub archive state for Roo Code.

The curated table has fourteen rows and four true HTML row groups:

1. Official/commercial coding agents `[4]`: Claude Code, OpenAI Codex, GitHub Copilot, Cursor.
2. Open-source coding agents/harnesses `[6]`: OpenCode, Pi, Aider, Goose, Cline, OpenHands.
3. Workflow support `[2]`: Superpowers, Repomix.
4. Maintenance/history `[2]`: Continue, Roo Code.

Use ratings `[5,5,5,5,5,4,5,4,5,4,4,5,4,3]` in that order. Continue remains useful for learning but must be marked no longer actively maintained/read-only with a final 2.0.0 release. Roo Code must be marked archived on 2026-05-15 and not recommended as a new-project default.

## Task 3: Write the regression contract before the rewrite

**Files:**

- Modify: `scripts/reader-ux-pages.yml`
- Modify: `scripts/test_role_paths.py`

Assert all three locales:

- keep `📌 → 🎯 → 🧩 → 🛠 → 📚 → 📖 → ⭐ → ✅` visible and ordered;
- contain exactly three closed `<details>` and no `open` attribute;
- keep six required-reading URLs and all fourteen resource URL/rating pairs visible;
- use four row groups with `rowspan` values `[4,6,2,2]`;
- define **IDE／Surface** and **Coding Agent／Harness** before the exercise;
- keep OpenCode, Pi, OpenRouter, and Ollama as four different identities;
- preserve every legacy anchor;
- reject stale claims that Continue is active or that Roo Code is maintained;
- reject any instruction that lets an agent push, merge, deploy, expose secrets, or erase a broad worktree without explicit human authorization.

Run the focused tests before the content rewrite and record the expected failures.

## Task 4: Rewrite the Traditional Chinese canonical page

**Files:**

- Modify: `branches/for-developer.md`
- Modify: `branches/DESIGN.md`

Use short, concrete sentences without deleting technical terms. Keep the existing safe exercise and make its sequence explicit:

`read-only plan → human approval → one-file edit → diff → smallest relevant test → human review → rollback if needed`

The exercise remains copy-ready. It must not ask the learner to copy blanks into a separate text file. It must not authorize push, merge, or deploy.

Move only these sections into closed details:

- time, environment, cost, and secret boundary;
- advanced team workflows;
- common mistakes, alternatives, and rollback.

## Task 5: Mirror English and Simplified Chinese

**Files:**

- Modify: `branches/for-developer.en.md`
- Modify: `branches/for-developer.zh-Hans.md`

Delegate the mechanical locale draft to GPT-5.6 Luna. The main agent must reconcile the result and verify that the three pages keep the same facts, order, URLs, ratings, row groups, safety rules, and current project states.

## Task 6: Update governance, changelog, and freshness evidence

**Files:**

- Modify: `branches/DESIGN.md`
- Modify: `CHANGELOG.md`
- Modify as required: `scripts/repository-freshness-snapshot.json`

Document that required readings and curated resources are visible for the developer path, that identity and surface remain separate dimensions, and that discontinued tools live in a maintenance/history group.

Use the GitHub API UTC date immediately before the CHANGELOG edit. Refresh the repository snapshot only if the final resource inventory changes tracked repository coverage.

## Task 7: Verify, review, commit, and open the stacked PR

Run at minimum:

```powershell
git diff --check
python scripts/build-docs-tree.py
python -m pytest scripts -q
python scripts/check-reader-ux.py
python scripts/check-anchors.py --strict
python scripts/check-mirror-parity.py
python scripts/check-locale-links.py
python scripts/zh-hans-localize.py --check
python scripts/check-hans-chars.py
python scripts/check-image-locale.py --strict
python scripts/check-2026-freshness.py
python scripts/check-repository-freshness.py verify-snapshot
python -m mkdocs build --quiet
```

Stage explicit paths, assert the frozen file count, and record the staged fingerprint. Run one independent `code-reviewer`; any content change invalidates its approval.

Commit subject:

```text
content(developers): keep the safe tool map visible
```

Open the PR against `codex/teacher-reader-ux-stack` (PR #176). Do not merge or clean the stack.
