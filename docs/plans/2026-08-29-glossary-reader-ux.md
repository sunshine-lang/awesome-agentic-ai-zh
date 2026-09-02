# Glossary Reader UX Implementation Plan

> **For Codex:** REQUIRED SUB-SKILL: Use `technical-writer` while implementing this plan task by task.

**Goal:** Turn the trilingual glossary into a calm, beginner-first lookup page without deleting important terms or breaking published anchors.

**Architecture:** Keep every term heading visible so deep links still land on a readable definition. Put only maintainer-only terminology tables, source notes, and secondary detail in closed `<details>` blocks. Remove volatile model snapshots and fixed token conversions from the glossary; route those facts to Stage 01, while current product and protocol identities remain protected by freshness checks.

**Tech Stack:** Markdown, MkDocs Material `<details markdown="1">`, Python/pytest content contracts, YAML reader-UX and freshness manifests.

---

### Task 1: Freeze the reader and anchor contract

**Files:**
- Create: `scripts/test_glossary_content.py`
- Modify: `scripts/reader-ux-pages.yml`
- Modify: `docs/TESTING_PLAN.md`

**Step 1: Write the failing content contract**

Require all three locale pages to keep:

- a visible “how to use this page” sentence;
- a visible 12-term quick map;
- a visible five-identity table that separates Provider API, Router, Local Runtime, Coding Agent, and Agent Framework;
- all existing 68 term headings plus new **Model Runtime**, **Workflow Graph**, and **Agent Harness** headings;
- category headings, the “term not found” route, and all published Subagent anchors;
- exactly two closed details blocks and no `open` attribute;
- no empty `""`, fixed token-to-character conversions, frozen frontier-model lists, or unqualified historical product facts.

**Step 2: Run the test and confirm it fails**

Run: `python -m pytest scripts/test_glossary_content.py -q`

Expected: FAIL because the current pages have no disclosures, no quick map, and preserve volatile snapshots.

**Step 3: Enrol the glossary in the generic reader-UX gate**

Add a `glossary` page contract with:

- visible section order: `quick-map → identities → categories → missing-term`;
- all important terms bold on first visible definition;
- two required closed details;
- zero allowed open details;
- a visible minimum of 12 internal jump links and five official identity links;
- trilingual URL/date/literal parity.

**Step 4: Document the gate**

Add the glossary contract and test command to `docs/TESTING_PLAN.md`.

### Task 2: Build a current official fact pack

**Files:**
- Modify: `scripts/freshness-models.yml`
- Test: `scripts/test_glossary_content.py`

**Step 1: Record canonical facts**

Use first-party sources only for changeable claims:

- OpenRouter FAQ and provider-routing docs: router/unified API, not a model or coding agent;
- Ollama API docs: model runtime/API, not a coding agent;
- OpenCode docs and Pi canonical repository: terminal coding agents/harnesses;
- MCP specification: hosts/clients/servers plus Prompts, Resources, and Tools;
- A2A latest specification: communication between independent agents; do not freeze a version number in reader prose;
- Agent Skills specification and current Anthropic docs: a Skill directory contains `SKILL.md` and optional supporting files;
- Claude Code docs: Subagent, Hooks, and project-instruction behavior; do not freeze an event count;
- OpenAI Harness Engineering, IBM Loop Engineering, and Microsoft Agent Framework workflow docs for current responsibility boundaries.

**Step 2: Add glossary-specific stale patterns**

Block:

- fixed “characters/words per token” equations;
- a dated “frontier model” roster, price, context, or availability snapshot;
- A2A `v1.0` / `150+ organisations` claims;
- fixed Claude Code hook-event counts;
- “Context Engineering replaces Prompt Engineering” ladder language;
- claims that Harness, Loop, and Graph are mutually exclusive generations.

**Step 3: Add a quiet freshness marker**

Use one ISO date on all three pages with scope `protocols,product-identities,terminology,official-links` and `max_age_days=90`. The date belongs in the closed source note, not the visible opening.

### Task 3: Rewrite the canonical zh-TW glossary

**Files:**
- Modify: `resources/glossary.md`

**Step 1: Replace the wall of maintenance data with a reader entry**

Keep visible:

1. what the glossary solves;
2. a 12-term jump map;
3. a five-identity comparison table;
4. all category and term headings;
5. the final route back to the curriculum.

Move the 37-row project naming table into a closed maintainer disclosure using a real HTML table with semantic row groups where categories repeat.

**Step 2: Rewrite each definition in three layers**

For every important term:

1. start with the **bold exact term**;
2. give one plain-language sentence;
3. keep one precise boundary or example and a route to the teaching Stage.

Do not delete Zero-shot/One-shot/Few-shot, Chain-of-Thought, Tool Schema/Call/Result, RAG/Memory terms, MCP primitives, Subagent/Hook/Skill boundaries, Eval/Observability/Guardrails, or Agent engineering terms.

**Step 3: Remove volatile glossary snapshots**

- Replace token conversion estimates with “tokenisation depends on the model and text; use the provider tokenizer/counter.”
- Replace the context-window roster with the stable definition and Stage 01 link.
- Replace the frontier-model roster with a stable “frontier changes over time” definition and Stage 01 link.
- Remove fixed chunk-size, latency, adoption, benchmark, and universal-product claims.

**Step 4: Clarify the engineering order**

Keep course order and responsibility questions separate:

- course: Prompt → Agent Loop → Workflow Graph/Framework → MCP/Skills → Context/RAG → Production Engineering;
- responsibilities: Prompt, Context, Agent Harness, Agent Loop/Loop Engineering, and Workflow Graph can overlap;
- Loop Engineering does not replace Harness;
- Graph Engineering is an emerging label, while Workflow Graph is the stable object taught in Stage 04.

### Task 4: Mirror English and Simplified Chinese

**Files:**
- Modify: `resources/glossary.en.md`
- Modify: `resources/glossary.zh-Hans.md`

**Step 1: Mirror structure and meaning**

Keep the same term order, heading count, official URLs, quick-map destinations, identity rows, disclosure count, freshness date, and technical boundaries.

**Step 2: Preserve locale routes**

Every internal link must point to its locale sibling. Existing external deep links to Subagent headings must continue to resolve.

**Step 3: Check locale quality**

Run Hans-character and OpenCC residue gates. Manually compare model names, protocol names, code identifiers, numbers, and status words across all locales.

### Task 5: Record the reusable design rule and release evidence

**Files:**
- Modify: `stages/DESIGN.md`
- Modify: `resources/style-guide.md`
- Modify: `resources/style-guide.en.md`
- Modify: `resources/style-guide.zh-Hans.md`
- Modify: `CHANGELOG.md`

**Step 1: Add the reference-page rule**

Document that glossary/reference pages differ from Stage pages: term headings and definitions stay visible for search and deep links; only maintenance tables, provenance, and optional depth are collapsed.

**Step 2: Update CHANGELOG from the final diff**

Use the UTC date returned by `api.github.com` immediately before staging. Record only actual changes and named factual corrections.

### Task 6: Verify, review, and publish as a stacked draft PR

**Files:** all frozen files from Tasks 1–5.

**Step 1: Run targeted tests**

Run:

```powershell
python -m pytest scripts/test_glossary_content.py scripts/test_reader_ux.py scripts/test_2026_freshness.py -q
```

Expected: all pass.

**Step 2: Run repository gates**

Run `git diff --check`, strict anchors, anchor parity, mirror parity, locale links, Hans characters, image locale, duplicate repositories, freshness strict, `python scripts/build-docs-tree.py`, full `python -m pytest scripts -q`, and `python -m mkdocs build`.

**Step 3: Freeze the diff**

Stage explicit paths only. Assert the cached path count equals the written freeze list and record the staged tree fingerprint.

**Step 4: Run one independent review**

Invoke `code-reviewer` once on the stable staged fingerprint because the change exceeds three files and 50 lines. Any edit invalidates the acknowledgement and requires targeted gates plus review again.

**Step 5: Commit and open the next stacked draft PR**

Commit message: `docs(glossary): make key terms easy to find`

Base the draft PR on `codex/courses-reader-ux-stack`. Do not merge, close upstream PRs, or clean branches/worktrees without explicit user approval.
