# Teacher Path Reader-UX Implementation Plan

> **For Codex:** REQUIRED SUB-SKILLS: use `bounded-agent-harness`, `imagegen`, and `verification-before-completion`; keep this PR stacked on PR #175 and do not merge or clean branches without the user’s approval.

**Goal:** Turn the trilingual teacher extension into a safe, current, beginner-readable path that keeps required reading and curated resources visible.

**Architecture:** Preserve the existing teacher-page filenames and legacy anchors, but replace the long catalog-first opening with one visible path: purpose → four goals → core terms → safety rules → one copy-ready practice → required reading → curated resources → completion. Put setup, long use-case surveys, extra prompt templates, automation, and troubleshooting in closed details. Replace the overclaiming classroom-capability image with a localized teacher-review-loop image while keeping the three-branch overview image.

**Tech Stack:** Markdown, semantic HTML tables, MkDocs, Python reader-UX tests, GitHub repository metadata, official education guidance, and built-in image generation.

---

### Task 1: Freeze the teacher-path facts and structure

**Files:**
- Modify: `docs/plans/2026-08-29-teacher-reader-ux.md`
- Inspect: `branches/for-teacher.md`
- Inspect: `branches/for-teacher.en.md`
- Inspect: `branches/for-teacher.zh-Hans.md`
- Inspect: `branches/DESIGN.md`

**Step 1: Verify the base and the existing branch boundary**

Run:

```powershell
git status --short --branch
git merge-base --is-ancestor 71ae6072c434fa7b296291022abcfc692c77b779 HEAD
```

Expected: clean `codex/teacher-reader-ux-stack`; PR #175 head is an ancestor.

**Step 2: Record the visible path**

Keep these sections outside every `<details>` in this order:

1. `📌` what the path helps with.
2. `🎯` four learning goals.
3. `🧩` eight bold core terms.
4. `🛡` five safety rules.
5. `🛠` one copy-ready lesson-draft exercise.
6. `📚` three required readings.
7. `⭐` the full curated resource table.
8. `✅` completion and next stops.

**Step 3: Verify current primary sources**

Use the newest official page when claims conflict. Required evidence:

- UNESCO generative-AI education guidance, updated 2026-01-16.
- European Commission ethical AI/data guidance for educators, updated 2026-06-09.
- TeachAI school-guidance toolkit and teacher route.
- Current official education-product pages and privacy/eligibility notes for Claude, ChatGPT, and Gemini Notebook (formerly NotebookLM).
- GitHub API status, archive flag, license, move target, and default branch for every repository in the curated table.

Do not copy volatile model names, usage counts, GitHub star counts, or fixed prices into the page.

### Task 2: Write failing teacher-path contracts

**Files:**
- Modify: `scripts/test_role_paths.py`
- Modify: `scripts/reader-ux-pages.yml`

**Step 1: Extend the role-path test data**

Add a `teacher` role with:

- three locale paths;
- eight required bold terms;
- the exact ordered URL/rating pairs for the curated table;
- the exact row-group sizes;
- official status/service/license and limitation tokens;
- a `2026-08-29` freshness marker;
- legacy anchors from all three existing pages.

**Step 2: Add behavior assertions**

Assert that all three locales:

- keep `📌 → 🎯 → 🧩 → 🛡 → 🛠 → 📚 → ⭐ → ✅` visible and ordered;
- use no default-open `<details>`;
- keep every resource URL and rating visible;
- include the same copy-ready exercise and explicit `no student data` rule;
- do not claim AI can make final grades, diagnose a learner, or infer a student’s zone of proximal development;
- include one localized review-loop image and no reference to the old classroom-capability image;
- preserve every old deep link at a matching semantic landing.

**Step 3: Enroll the pages in the reader-UX ratchet**

Configure a conservative initial visible-character limit, zero open details, required section order, eight core terms, resource rowspans, URL/rating parity, and literal parity for the verification date and safety phrases.

**Step 4: Run the focused tests and confirm red**

Run:

```powershell
python -m pytest scripts/test_role_paths.py scripts/test_reader_ux.py -q
```

Expected: teacher-specific assertions fail before the content rewrite.

### Task 3: Rewrite the canonical teacher path

**Files:**
- Modify: `branches/for-teacher.md`
- Modify: `branches/DESIGN.md`

**Step 1: Rewrite the visible path in plain Traditional Chinese**

Use short sentences and concrete examples. Preserve the exact professional terms:

- Learning Objective
- Scaffolding
- Rubric
- Formative Assessment
- AI Literacy
- Student Data
- Human Review
- Academic Integrity

Every first definition must be bold and appear before the exercise.

**Step 2: Make the first exercise safe and copy-ready**

Use a fictional lesson topic and no student records. The prompt must request one learning objective, one short activity, one exit ticket, and a list of facts the teacher must verify. Follow it with a five-item human review checklist.

**Step 3: Keep important sources visible**

Keep the three required readings and the full grouped resource table visible. Use real `rowspan`, one `<tbody>` per group, editorial five-star ratings, status/service/license, audience, and a concrete limitation. Do not show GitHub star counts.

**Step 4: Move secondary depth into closed details**

Collapse only time/setup/cost, extended use cases, extra prompt templates, advanced automation, legal-region notes, alternatives, and troubleshooting. Safety rules must remain visible.

**Step 5: Preserve old anchors at semantic landings**

Move each old anchor beside the new heading or detail summary that owns the same meaning. Do not collect anchors at the top of the page.

### Task 4: Replace the misleading classroom-capability diagram

**Files:**
- Create: `resources/diagrams/teacher-ai-review-loop.png`
- Create: `resources/diagrams/teacher-ai-review-loop.en.png`
- Create: `resources/diagrams/teacher-ai-review-loop.zh-Hans.png`
- Modify: `resources/diagrams/locale-variant-prompts.md`
- Remove after reference scan: `resources/diagrams/teacher-ai-classroom-use-cases.png`
- Remove after reference scan: `resources/diagrams/teacher-ai-classroom-use-cases.en.png`
- Remove after reference scan: `resources/diagrams/teacher-ai-classroom-use-cases.zh-Hans.png`

**Step 1: Generate one bright five-step review loop per locale**

Show only this relationship:

`teacher sets goal → AI drafts → teacher checks privacy/facts/bias → learner uses material → teacher observes and revises`

Use large readable text, one direction, high contrast, no product logos, no maturity badges, no watermark, and no claim that AI grades or diagnoses students.

**Step 2: Inspect every image at original resolution**

Reject any output with misspelled labels, extra steps, tiny text, mixed locale text, or an implied autonomous grading decision.

**Step 3: Scan references before removing old assets**

Run:

```powershell
rg -n "teacher-ai-classroom-use-cases|teacher-ai-review-loop" . -g "*.md"
```

Expected: the old image is referenced only by the three teacher pages and prompt history before replacement. Remove it only after all consumers point to the new localized asset.

### Task 5: Mirror the canonical page into English and Simplified Chinese

**Files:**
- Modify: `branches/for-teacher.en.md`
- Modify: `branches/for-teacher.zh-Hans.md`

**Step 1: Translate meaning, not word order**

Keep the same headings, section order, facts, URLs, ratings, dates, safety rules, resource grouping, and image position. Use natural locale wording while preserving exact technical terms.

**Step 2: Check trilingual literals and links**

Run:

```powershell
python scripts/check-mirror-parity.py
python scripts/check-locale-links.py
python scripts/zh-hans-localize.py --check
python scripts/check-hans-chars.py
```

Expected: all commands exit 0.

### Task 6: Update governance and changelog

**Files:**
- Modify: `branches/DESIGN.md`
- Modify: `CHANGELOG.md`
- Modify: `resources/diagrams/locale-variant-prompts.md`

**Step 1: Document the teacher-path contract**

Record the visible safety rules, copy-ready fictional-data exercise, visible required reading/resource table, localized diagram rule, and the rule against autonomous grading/diagnosis claims.

**Step 2: Use GitHub’s UTC date**

Read the `Date` header from `https://api.github.com` immediately before the changelog edit and use its UTC date. Write the changelog from the final diff, not from memory.

### Task 7: Verify, review, commit, and open the stacked PR

**Files:**
- Test all modified paths.

**Step 1: Run focused verification**

```powershell
python -m pytest scripts/test_role_paths.py scripts/test_reader_ux.py -q
```

Expected: all tests pass.

**Step 2: Run the full repository gate**

```powershell
git diff --check
python scripts/check-reader-ux.py
python scripts/check-stage-template.py
python scripts/check-anchors.py --strict
python scripts/test_anchor_slug_parity.py
python scripts/check-mirror-parity.py
python scripts/check-locale-links.py
python scripts/zh-hans-localize.py --check
python scripts/check-hans-chars.py
python scripts/check-image-locale.py --strict
python scripts/check-duplicate-repos.py
python scripts/check-2026-freshness.py
python scripts/check-repository-freshness.py --strict
python -m pytest scripts -q
python scripts/build-docs-tree.py
python -m mkdocs build --quiet
```

Expected: all blocking gates exit 0; informational warnings are reported explicitly.

**Step 3: Stage explicit paths and freeze the fingerprint**

Use `git add <path>` for each final path. Assert the staged count against the frozen file list and confirm zero unstaged/untracked task files.

**Step 4: Run one independent review**

Invoke one `code-reviewer` against the stable staged fingerprint. Any content change invalidates the acknowledgment and requires relevant gates plus review again.

**Step 5: Commit and publish without merging**

Commit subject:

```text
content(teachers): make safe classroom AI use clear
```

Push `codex/teacher-reader-ux-stack` and open its PR against `codex/agent-engineering-route-coherence-stack`. Do not merge, retarget, delete branches, remove worktrees, or prune.
