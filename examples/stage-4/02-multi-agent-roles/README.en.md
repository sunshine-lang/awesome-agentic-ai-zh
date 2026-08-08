<div align="right">
  <a href="./README.md">繁體中文</a> | <a href="./README.zh-Hans.md">简体中文</a> | <strong>English</strong>
</div>

# Exercise 2: Multi-Agent Role Allocation (CrewAI)

Pairs with [Stage 4 — Agent Frameworks](../../../stages/04-agent-frameworks.en.md) Exercise 2.
> 🎓 **How to use this**: `starter.py` is the **complete solution**, not a TODO skeleton. The active approach works better — `mv starter.py starter_reference.py`, read the signatures but not the bodies, write your own `starter.py` from scratch, then run `python test.py` to check it; if you are stuck for 20 minutes, go back and compare against the reference. Full methodology in [`docs/HOW_TO_USE.md`](../../../docs/HOW_TO_USE.md).

> 📚 **Want the chapter-length version?** The starter in this folder is an illustrative build focused on the core pattern plus two SDK paths — it is not in-depth teaching material. Recommended for depth:
> - [`datawhalechina/hello-agents`](https://github.com/datawhalechina/hello-agents) ⭐ the most complete Chinese-language course out there — chapter by chapter, plus 16 production capabilities. **This exercise maps to hello-agents' multi-agent roles / Crew chapter**
> - [CrewAI Examples repo](https://github.com/crewAIInc/crewAI-examples) (official sequential / hierarchical templates; ⚠️ archived 2026-04, still worth reading as reference)
> - Full references in [Stage 4 Curated Projects](../../../stages/04-agent-frameworks.en.md#-curated-projects)


## Task

Three agents each own one step, collaborating to produce a blog intro:

```
Researcher → Writer → Critic
  (find facts)  (write)  (verify, PASS/ISSUES)
```

Role-based pipelines are **CrewAI's sweet spot** — describe roles / goals / tasks, framework orchestrates.

## How to run — two paths

### Path A (default, free, local)

```bash
pip install -r requirements.txt
ollama pull qwen2.5:3b
ollama serve
python starter.py
```

Budget: **$0**. Three agents sequential ≈ 30-90s on CPU with qwen2.5:3b.

### Path B (Anthropic, cloud-quality)

```bash
pip install -r requirements.txt
export ANTHROPIC_API_KEY=sk-ant-...
python starter_anthropic.py
```

Budget: ~**$0.005-0.01** per run (3 agents × short outputs, claude-haiku-4-5).

## Validate the logic

```bash
python test.py             # tool logic + crew structure
python test_anthropic.py   # starter_anthropic loads
```

CrewAI's `kickoff()` is too opaque for pure mock testing. These tests cover structure (3 agents + 3 tasks + sequential process + context dependencies) and tool logic. For full validation, run starter.py against Ollama.

## Core CrewAI multi-agent concepts

### Agent

```python
researcher = Agent(
    role="Researcher",
    goal="...",          # one line: what does "success" look like
    backstory="...",     # persona context, shapes the prompt
    tools=[search],
    llm=MODEL,
)
```

**Key**: `role` and `goal` dramatically affect prompt quality. Don't write "Agent" — write "Researcher who finds factual data".

### Task

```python
research_task = Task(
    description="Search for X and report findings.",
    expected_output="A 1-2 sentence factual entry.",
    agent=researcher,
)
```

**Key**: `expected_output` is the "passing template" the LLM sees — be specific. "A 2-sentence intro paragraph" is 10× better than "Some text".

### Context dependency

```python
write_task = Task(..., context=[research_task])   # writer sees researcher's output
critic_task = Task(..., context=[research_task, write_task])  # critic sees both
```

**Key**: `context` is CrewAI's dataflow mechanism. `critic_task.context=[a, b]` means the critic sees the output of tasks a and b.

### Sequential vs hierarchical process

```python
Crew(..., process=Process.sequential)    # linear walk-through
Crew(..., process=Process.hierarchical)  # manager + workers, needs manager_llm
```

We use sequential (simplest, deterministic). Hierarchical lets a manager agent dispatch — useful for more complex tasks.

## Observation across both paths

| Observation | Anthropic Claude haiku | Ollama qwen2.5:3b |
|---|---|---|
| Researcher actually calls tool | Stable | Sometimes skips tool, makes things up |
| Writer cites researcher's output | Stable | May go off-memory, deviate from search result |
| Critic catches hallucinations | Sharper | Looser, may PASS when it shouldn't |
| Speed | 10-30s | 30-90s |
| Cost | $0.005-0.01 | $0 |

**Punchline**: multi-agent is more model-quality-sensitive than single-agent — each agent can drop a step, errors compound by the time you reach the critic. Production multi-agent systems almost always use large models (or carefully fine-tuned small ones).

## Common pitfalls

- **`expected_output` too generic**: "Some output" gives the LLM no guide. "A 2-sentence blog intro paragraph in active voice" is 10× better
- **Missing `context`**: writer without `context=[research_task]` doesn't see researcher's output — it'll hallucinate
- **Small model + 3 agents**: qwen2.5:3b on 3-agent crews can take 1+ minute. Switch to `qwen2.5:7b` or Claude
- **`allow_delegation=True` use cautiously**: enables agents to call others, easy to loop. Default `False` for prototypes

## Want smarter answers?

```bash
MODEL=anthropic/claude-sonnet-5 python starter_anthropic.py  # higher quality
MODEL=ollama/qwen2.5:7b python starter.py                       # larger local model
```

## Extensions

- **Add a manager**: `process=Process.hierarchical` + `manager_llm=...` for dynamic delegation
- **Add memory**: CrewAI has `memory=True` for cross-task context
- **Streaming**: `crew.kickoff_for_each(...)` or `crew.kickoff_async(...)`
- **Human-in-the-loop**: see Exercise 3 (LangGraph) — CrewAI's HITL is weaker
