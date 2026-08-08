# Outreach: LangChain ecosystem (langchain-ai / kyrolabs/awesome-langchain)

> ⚠️ **Send content is now canonical in [`_send-day-packages.md`](_send-day-packages.md)** (package C — current numbers: 8 stages / 240+ resources). This file is kept for positioning rationale; do not paste its older entry/stats blocks directly.

> **Status**: not contacted · **Channel**: GitHub PR
> **Primary lang**: en (with zh as bonus)
> **Last updated**: 2026-05-26 (refreshed — stats, 8-stage structure, correct section target)
> **Repos**:
> - https://github.com/langchain-ai/langchain (main repo)
> - https://github.com/kyrolabs/awesome-langchain (community awesome list ★9k+)

**Why this target**: LangChain is the gateway agent framework for ~80% of zh-language developers. Our Stage 4 covers it; our §11 catalog now includes Langchain-Chatchat (★37k) and the Chinese LangChain getting-started guide (which **already lives in the same section** we're targeting — see below). Cross-link is natural.

**Pitch angle**:

- For `langchain-ai/langchain` itself: too big a target; aim instead at the **community awesome list** (`kyrolabs/awesome-langchain`).
- For `kyrolabs/awesome-langchain`: we're a multilingual learning-order complement to their flat catalog.
- **Target section confirmed (2026-05-26)**: `## Learn → ### Notebooks`. Precedent: `liaokongVFX/LangChain-Chinese-Getting-Started-Guide` already sits there. There is **no** "Tutorials & Learning Resources" section in the current README; do not propose one.

**Their counter-value**: ★9k exposure to LangChain-curious developers worldwide.

---

## Variant 1 — Social post (X / LinkedIn, ~280 chars)

```
LangChain learners often ask: "I have the docs, but where do I actually start?"

Built an 8-stage trilingual learning roadmap (zh-TW · zh-Hans · en). Stage 4
walks through LangChain / LangGraph / AutoGen / CrewAI / Smolagents with
prerequisites and time estimates. 145+ projects · MIT · ★1.7k.

🔗 github.com/WenyuChiou/awesome-agentic-ai-zh
```

## Variant 2 — GitHub PR to kyrolabs/awesome-langchain (200-300 words)

**PR title**: Add awesome-agentic-ai-zh (trilingual learning roadmap) to Learn → Notebooks

**Diff** (against `## Learn → ### Notebooks`, after the `liaokongVFX/LangChain-Chinese-Getting-Started-Guide` line — keeps the two zh-ecosystem learning resources adjacent):

```diff
  - [LangChain Chinese Getting Started Guide](https://github.com/liaokongVFX/LangChain-Chinese-Getting-Started-Guide): Chinese LangChain Tutorial for Beginners ![GitHub Repo stars](https://img.shields.io/github/stars/liaokongVFX/LangChain-Chinese-Getting-Started-Guide?style=social)
+ - [WenyuChiou/awesome-agentic-ai-zh](https://github.com/WenyuChiou/awesome-agentic-ai-zh): Trilingual (zh-TW / zh-Hans / en) 8-stage learning roadmap for agentic AI — Stage 4 walks through LangChain, LangGraph, AutoGen, CrewAI, Smolagents with prerequisites, time estimates, and hands-on exercises ![GitHub Repo stars](https://img.shields.io/github/stars/WenyuChiou/awesome-agentic-ai-zh?style=social)
```

**PR description**:

```markdown
Hi kyrolabs maintainers,

Proposing addition of [WenyuChiou/awesome-agentic-ai-zh](https://github.com/WenyuChiou/awesome-agentic-ai-zh) to **Learn → Notebooks**, next to the existing `liaokongVFX/LangChain-Chinese-Getting-Started-Guide` entry (same zh-learning surface).

**Why this is a good fit**:
- Trilingual (zh-TW canonical · zh-Hans · en — all three fully maintained, not MT) — fills a gap for non-English learners
- **Stage 4 (Agent Frameworks)** walks new developers through **LangChain / LangGraph / AutoGen / CrewAI / Smolagents** with prerequisites, time estimates, and hands-on exercises
- §11 of the catalog has 7 Chinese-ecosystem entries including `chatchat-space/Langchain-Chatchat` (★37k) and the LangChain Chinese Getting Started Guide that's already in your list
- Stage 5 covers the Claude Code / MCP / Skills layer; Stage 8 covers Agent Interfaces (Computer Use / Browser / Sandbox). Together with the catalog this is the complement-to-LangChain-docs that doesn't currently exist in zh

**Stats (2026-05-26)**: ★1.7k · 191 forks · 5,090 unique visitors (14d) · 1,316 unique cloners (14d) · 3 community contributors. MIT licensed. Rendered docs at https://wenyuchiou.github.io/awesome-agentic-ai-zh/. CI runs banned-word + link-rot + anchor-integrity lints on every PR.

If a different section or shape works better, happy to redirect. Thanks for maintaining awesome-langchain.

— Wenyu Chiou (individual maintainer)
```

## Variant 3 — Email to LangChain DevRel (150 words)

```
Hi LangChain team,

I built awesome-agentic-ai-zh — a trilingual (zh-TW / zh-Hans / en) 8-stage
learning roadmap for agentic AI. ★1.7k, 5k unique visitors / 14 days, heavy
zh-language community traction (top external referrer is Threads).

Stage 4 walks new developers through LangChain → LangGraph → AutoGen →
CrewAI → Smolagents with prerequisites and time estimates per step.
Designed to bridge "I know Python" to "I can build a working agent."

Two questions:
1. Is there a LangChain-side surface where this would fit (Learn, blog,
   docs sidebar)?
2. Any specific LangChain features I should cover better in Stage 4? Open
   to feedback.

No expectation, just opening dialogue.

— Wenyu
```

---

## Notes

- **First target**: kyrolabs/awesome-langchain (community awesome list, lower
  barrier to merge). **Section: `Learn → Notebooks`**, not "Tutorials" (no such
  section exists in the current README — verified 2026-05-26).

- **Second target**: LangChain blog/docs (higher signal but harder to land)
- Avoid pitching `langchain-ai/langchain` itself directly — too big, signal is
  drowned out

- LangSmith / LangGraph teams are separate — different DevRel; don't pitch all
  three at once

- **Stat snapshot is per-PR-day** — refresh `★`, `forks`, `unique visitors`,
  `clones` with `gh repo view --json stargazerCount,forkCount` + `gh api
  repos/.../traffic/views,clones` on the day you submit. Stale stats in a PR
  body read as careless.
