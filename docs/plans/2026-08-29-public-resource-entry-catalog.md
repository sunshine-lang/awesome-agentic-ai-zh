# Public Resource Entry and Catalog Implementation Plan

**Goal:** Turn the public resource pages into a task-first, beginner-readable entry point while keeping the complete trilingual MCP／Skills catalog searchable, rated, current, and safe.

**Architecture:** Keep five official or high-quality starting points, the 16-item highlighted resource table, and the full category headings visible. Put the complete 83-entry catalog and secondary explanations behind closed disclosures, remove volatile stars／counts／time promises, and preserve editorial ratings, anchors, status, licenses, and limits. Write and verify zh-TW first, then use a bounded Codex delegate for the en／zh-Hans mirrors; the parent owns facts, diff review, tests, and release gates.

**Tech Stack:** Trilingual Markdown, HTML `tbody`／`rowspan`, PyYAML reader-UX config, pytest regression tests, repository freshness snapshot, MkDocs, stacked GitHub PRs.

---

## Scope and fixed decisions

This layer changes only the public resource entry and catalog surface:

- `RESOURCES.md`, `RESOURCES.en.md`, `RESOURCES.zh-Hans.md`
- `resources/README.md`, `resources/README.en.md`, `resources/README.zh-Hans.md`
- `resources/mcp-skills-catalog.md`, `resources/mcp-skills-catalog.en.md`, `resources/mcp-skills-catalog.zh-Hans.md`
- `scripts/test_public_entry_resources.py`
- `scripts/reader-ux-pages.yml`
- `scripts/check-catalog-counts.py`, `scripts/test_catalog_counts.py`
- `docs/TESTING_PLAN.md`, `stages/DESIGN.md`, `CHANGELOG.md`
- current README, site-card, outreach, and repository-contract surfaces where stale public inventory totals must be removed
- the repository-freshness snapshot because the final link inventory and source locations change

The full cookbook rewrite, glossary convergence, broader README／home copy, and agent-engineering chapter-title layer are separate stacked PRs. This PR does not merge or clean branches without explicit user approval.

## Official fact pack

Use the following current primary sources. Recheck them before staging:

- MCP Registry: `https://registry.modelcontextprotocol.io/`
- MCP reference servers: `https://github.com/modelcontextprotocol/servers`
- Agent Skills specification: `https://agentskills.io/specification`
- Anthropic Skills examples: `https://github.com/anthropics/skills`
- Notion hosted MCP: `https://developers.notion.com/guides/mcp/overview`
- GitHub MCP server: `https://github.com/github/github-mcp-server`
- Google Workspace MCP: `https://developers.google.com/workspace/guides/configure-mcp-servers`
- Atlassian Rovo MCP: `https://support.atlassian.com/atlassian-rovo-mcp-server/docs/getting-started-with-the-atlassian-remote-mcp-server/`
- Linear MCP: `https://linear.app/docs/mcp`
- Slack MCP: `https://docs.slack.dev/ai/mcp-overview/`
- Canva MCP: `https://www.canva.dev/docs/mcp/`
- Gemini Notebook: `https://support.google.com/gemininotebook/answer/17003757`

Facts that must be explicit:

- `modelcontextprotocol/servers` contains educational reference implementations, not a production-server catalog. Discovery points to the official MCP Registry.
- Notion recommends its hosted OAuth MCP. The open-source `notion-mcp-server` package is no longer actively maintained and is only a headless／token alternative.
- Google Workspace MCP is Developer Preview.
- Linear exposes a current Streamable HTTP endpoint and a read-only endpoint; do not recommend the stale community server as the default.
- Slack and Atlassian can write real workspace data; least privilege and human confirmation stay visible.
- Canva features and plan availability vary; do not freeze a tool count.
- Display `Gemini Notebook（舊名 NotebookLM）`; keep `notebooklm` only where it is an exact package, URL, import, or compatibility identifier.

## Task 1: Write the public-entry regression first

**Files:**

- Create: `scripts/test_public_entry_resources.py`
- Modify: `scripts/reader-ux-pages.yml`

**Step 1: Add a test helper that removes closed `<details>` bodies**

The helper keeps the `<summary>` text but removes the hidden body. Every “visible” assertion must use this helper, so a required resource cannot pass while hidden.

**Step 2: Lock the `RESOURCES` visible entry**

Assert for all three locales:

- five task-first internal choices are visible;
- five starting resources and five editorial ratings are visible;
- MCP, Skill, and Plugin are bold and defined before the long catalog;
- the visible highlight table has exact rowgroups `4／3／4／4／1` and trilingual URL／rating parity;
- only the longer supplemental lists are closed by default.

**Step 3: Lock the resource index**

Assert the seven reference destinations remain visible without line counts, fixed totals, or reading-time promises. Require at least two closed disclosures for overlap, contribution, and maintenance detail.

**Step 4: Lock the full catalog landing points**

Assert all 17 numbered H2 category headings remain outside disclosures, exactly 17 closed `<details>` elements hold the category entries, and at least five safe official starts with ratings and a permission warning remain visible.

**Step 5: Lock volatile and stale patterns**

Reject numeric GitHub-star claims, `81+`／`76+` catalog claims, fixed tool counts, the community Linear／Slack servers as defaults, and unqualified “NotebookLM” display names in the scoped files.

**Step 6: Run the test and capture the expected red result**

Run:

```powershell
python -m pytest scripts/test_public_entry_resources.py -q
```

Expected: failures for missing task-first entries, visible overload, volatile claims, old service names, and absent disclosures.

## Task 2: Retire advertised catalog counts without losing integrity checks

**Files:**

- Modify: `scripts/check-catalog-counts.py`
- Modify: `scripts/test_catalog_counts.py`

**Step 1: Write failing unit tests**

Require the checker to count real entries and compare three locales, but stop requiring public prose or index rows to advertise the total. A numeric size claim that remains must fail with a message telling the writer to remove the claim.

**Step 2: Simplify the checker**

Keep the explicit numbered-section and entry parsing rules. Remove the “headline must equal real total” contract. Replace it with a scoped ban on advertised totals outside changelog／plans; the actual count remains machine output only.

**Step 3: Run focused tests**

```powershell
python -m pytest scripts/test_catalog_counts.py scripts/test_public_entry_resources.py -q
python scripts/check-catalog-counts.py --quiet
```

Expected: checker tests pass; public-entry tests remain red until content changes.

## Task 3: Rewrite the zh-TW resource landing page

**Files:**

- Modify: `RESOURCES.md`

**Step 1: Add the visible task-first table**

Keep five choices visible: start the curriculum, look up a term, choose a CLI agent, connect a tool, and build a small recipe. Preserve editorial ratings.

**Step 2: Define MCP／Skill／Plugin in plain language**

Use one short paragraph each. State that MCP is a protocol, a Skill is reusable instructions plus optional resources, and a Plugin is a host-specific installation bundle. Do not imply all hosts implement plugins the same way.

**Step 3: Add five visible starting resources**

Use the MCP Registry, MCP reference servers, Anthropic Skills examples, GitHub MCP, and Hello-Agents. Explain that reference servers teach protocol behavior and are not production recommendations.

**Step 4: Build the visible highlight table**

Use exact rowgroups `4／3／4／4／1`, true `scope="rowgroup" rowspan="N"`, current official URLs, editorial ratings, and a status／limit column. Prefer hosted Notion／Linear／Slack／Atlassian official entries over stale community defaults.

**Step 5: Keep the next actions visible**

Glossary, cookbook, style guide, and contributing links remain outside disclosures.

## Task 4: Rewrite the zh-TW resource index

**Files:**

- Modify: `resources/README.md`

**Step 1: Lead with the job map**

Show the seven reference destinations and “when to use it” without line counts, catalog totals, or time estimates.

**Step 2: Keep the beginner route visible**

State that readers do not need to read the reference area in order. Stage 0 is the learning start; glossary and cookbook are lookup／practice tools.

**Step 3: Fold secondary governance detail**

Put overlap rationale, trilingual maintenance, and rules for adding a new reference into at least two closed disclosures. Keep contribution links visible.

## Task 5: Make the zh-TW MCP／Skills catalog progressive and current

**Files:**

- Modify: `resources/mcp-skills-catalog.md`

**Step 1: Add a five-start visible landing block**

Define MCP Server, Skill, Plugin, Remote MCP, and permission boundary before the category list. Show the MCP Registry, reference servers, Notion, GitHub, and Anthropic Skills as visible safe starts with editorial ratings.

**Step 2: Keep all 17 category headings visible**

Each numbered `## N.` heading stays outside `<details>`. Immediately below it, add one sentence explaining when to use the category, then a closed details body containing the existing entries.

**Step 3: Preserve entry anchors and editorial ratings**

Do not rename `###` entry headings or remove rated projects solely to shorten the page. Remove `| Stars |` rows and volatile popularity wording. Keep license, maintenance, archive, Preview, permission, and data-write limits.

**Step 4: Replace stale defaults**

Make hosted Notion, current Linear, official Slack, Atlassian Rovo, GitHub, Google Workspace, and Canva entries current. Historical or community alternatives may stay only with a clear status／reason.

**Step 5: Run the zh-TW tests**

```powershell
python -m pytest scripts/test_public_entry_resources.py scripts/test_catalog_counts.py -q
python scripts/check-reader-ux.py
python scripts/check-catalog-counts.py --quiet
```

## Task 6: Delegate exact en／zh-Hans mirrors

**Files:**

- Create: `.ai/codex_task_public_resources_locale_mirrors.md`
- Modify: the six `.en.md`／`.zh-Hans.md` mirrors in scope

**Step 1: Freeze the canonical facts and structure**

The brief must list exact URLs, rowgroups, 17 category IDs, ratings, required status words, forbidden stale patterns, and the no-extra-files rule.

**Step 2: Run the bounded Codex delegate**

First run `codex --version`. Then invoke the installed `run_codex.sh` with `--brief-file` and the worktree as `--repo`. The delegate may translate and mirror structure only; it may not research, change ratings, add projects, edit tests, stage, commit, or push.

**Step 3: Read the structured result and reject drift**

Compare `files_changed` against the six-file allowlist. Review every URL, status, rating, details boundary, heading, and anchor before accepting.

## Task 7: Documentation, full gates, review, and stacked PR

**Files:**

- Modify: `docs/TESTING_PLAN.md`
- Modify: `stages/DESIGN.md`
- Modify: `CHANGELOG.md`
- Modify: current README, site-card, outreach, and repository-contract surfaces only to remove stale public totals
- Modify: `scripts/repository-freshness-snapshot.json` because the current link inventory and source locations changed

**Step 1: Record the public-resource design contract**

Document visible task-first choices, visible curated starts, category-heading landings, closed long bodies, editorial ratings, and the no-volatile-count rule.

**Step 2: Recheck current sources and GitHub API UTC date**

Any changed fact invalidates the prior content review. CHANGELOG uses the API response date and the final diff, not memory.

**Step 3: Run ordered verification**

```powershell
git diff --check
python -m pytest scripts/test_public_entry_resources.py scripts/test_catalog_counts.py -q
python scripts/check-reader-ux.py
python scripts/check-catalog-counts.py --quiet
python scripts/check-anchors.py --strict
python scripts/test_anchor_slug_parity.py
python scripts/check-mirror-parity.py
python scripts/check-locale-links.py
python scripts/zh-hans-localize.py --check
python scripts/check-hans-chars.py
python scripts/check-image-locale.py --strict
python scripts/check-duplicate-repos.py
python scripts/check-2026-freshness.py
python -m pytest scripts -q
python scripts/build-docs-tree.py
python -m mkdocs build
```

Use the current formal command from `scripts/README.md` if a listed script exposes a different CLI.

**Step 4: Perform the human landing audit**

- A new reader can choose one next action without opening details.
- Required／curated starts and ratings are visible.
- Every hidden item has a visible category landing and a useful summary.
- All 17 catalog categories remain searchable by heading／anchor.
- The three locales say the same facts and warnings.
- No important concept, project, rating, or deep link vanished.

**Step 5: Freeze, review, commit, and push**

Stage explicit files only and assert the staged count against the frozen allowlist. Record `git write-tree`; run exactly one independent `code-reviewer` because the diff exceeds 50 lines, changes more than three files, and includes delegated output. Any byte change invalidates the review. Commit with:

```text
content(resources): make the public catalog task-first
```

Push and open a PR based on `codex/everyday-user-reader-ux-stack`. Keep the PR unmerged and preserve all branches／worktrees until the user explicitly approves merge and cleanup.

## Acceptance criteria

- `RESOURCES` shows five task choices, five safe starts, and current MCP／Skill／Plugin definitions without opening anything.
- Its long highlight table is closed, uses exact `4／3／4／4／1` rowgroups, and has trilingual URL／rating parity.
- The resource index is task-first and contains no fixed line, total, or reading-time claims.
- The catalog keeps all 17 numbered H2 anchors visible, has exactly 17 closed category bodies, and preserves all retained entry headings and editorial ratings.
- Numeric GitHub stars, `81+`／`76+` marketing counts, fixed Canva tool totals, stale Notion／Linear／Slack defaults, and unqualified NotebookLM display names are absent from the scoped public pages.
- Current official status and permission limits are stated accurately.
- All machine gates, rendered builds, human landing audit, and independent review pass on the final staged fingerprint.
- The PR remains open and unmerged for user inspection.
