<div align="right">
  <a href="./README.md">繁體中文</a> | <a href="./README.zh-Hans.md">简体中文</a> | <strong>English</strong>
</div>

# Exercise 1: Same Agent, Two Frameworks (LangGraph + CrewAI)

Pairs with [Stage 4 — Agent Frameworks](../../../stages/04-agent-frameworks.en.md) Exercise 1.
> 🎓 **How to use this**: `starter.py` is the **complete solution**, not a TODO skeleton. The active approach works better — `mv starter.py starter_reference.py`, read the signatures but not the bodies, write your own `starter.py` from scratch, then run `python test.py` to check it; if you are stuck for 20 minutes, go back and compare against the reference. Full methodology in [`docs/HOW_TO_USE.md`](../../../docs/HOW_TO_USE.md).

> 📚 **Want the chapter-length version?** The starter in this folder is an illustrative build focused on the core pattern plus two SDK paths — it is not in-depth teaching material. Recommended for depth:
> - [`datawhalechina/hello-agents`](https://github.com/datawhalechina/hello-agents) ⭐ the most complete Chinese-language course out there — chapter by chapter, plus 16 production capabilities. **This exercise maps to hello-agents' framework comparison / orchestration chapter**
> - [LangGraph official tutorial](https://langchain-ai.github.io/langgraph/tutorials/) + [CrewAI official docs](https://docs.crewai.com/)
> - Full references in [Stage 4 Curated Projects](../../../stages/04-agent-frameworks.en.md#-curated-projects)


## Task

A minimal search + summarize agent:

- Given a query (e.g. "summarize Taipei")
- Agent uses a `search` tool to hit a knowledge base
- LLM summarizes the result in 1-2 sentences

Built once in **LangGraph** and once in **CrewAI** — compare styles.

## How to run — two paths + two frameworks

### Path A (default, free, local)

```bash
pip install -r requirements.txt
ollama pull qwen2.5:3b
ollama serve

python starter.py         # LangGraph + Ollama
python starter_crewai.py  # CrewAI + Ollama (comparison)
```

Budget: **$0**.

### Path B (Anthropic, cloud-quality)

```bash
pip install -r requirements.txt
export ANTHROPIC_API_KEY=sk-ant-...
python starter_anthropic.py   # LangGraph + Claude
```

Budget: ~**$0.001** per run (claude-haiku-4-5).

## Validate the logic (mock-based)

```bash
python test.py             # LangGraph + mock LLM
python test_anthropic.py   # starter_anthropic loads + ChatAnthropic constructs
python test_crewai.py      # CrewAI tool + module loads
```

## Side-by-side framework comparison

| Dimension | LangGraph | CrewAI |
|---|---|---|
| Core abstraction | `StateGraph` + node + edge | `Agent` + `Task` + `Crew` |
| Mental model | "How does state flow?" | "Who plays what role?" |
| Loop control | Explicit conditional edges | Hidden inside `Crew.kickoff()` |
| Lines of code (this task) | ~50 | ~25 |
| Debug path | Inspect graph state, time-travel | Verbose logs, hard to step |
| Best for | Complex branching, production, audit | Multi-agent prototypes, role-based tasks |
| Learning curve | Medium-high | Low |

### LangGraph style (condensed)

```python
g = StateGraph(State)
g.add_node("agent", agent_node)
g.add_node("tools", tool_node)
g.add_conditional_edges("agent", should_continue, {"tools": "tools", END: END})
g.add_edge("tools", "agent")
```

"I tell the system explicitly: state shape, nodes, edges, branching via `should_continue`."

### CrewAI style (condensed)

```python
researcher = Agent(role="Researcher", goal="...", tools=[search], llm=MODEL)
task = Task(description=query, expected_output="...", agent=researcher)
crew = Crew(agents=[researcher], tasks=[task])
crew.kickoff()
```

"I describe: who plays this role, what task, what tools. Framework decides how to run."

## What to observe

1. **Abstraction cost**: CrewAI hides more, writes less code; but stack depth grows when debugging
2. **Small-model friendliness**: LangGraph is more stable with qwen2.5:3b; CrewAI's denser prompts can confuse small models
3. **Controllability**: LangGraph exposes state transitions; CrewAI is "result-oriented"
4. **When to pick**: production / audit → LangGraph. Multi-agent prototypes / role-based → CrewAI

## Common pitfalls

- **LangGraph `bind_tools`**: must `llm.bind_tools([search])` to expose tool schema. Without it the model doesn't know the tool exists
- **CrewAI model spec**: needs LiteLLM format (`"ollama/qwen2.5:3b"`, not `"qwen2.5:3b"`). Misspell and framework silently falls back to OpenAI default
- **CrewAI return type**: `crew.kickoff()` returns a `CrewOutput` object; `str(result)` to get text. Bare `print(result)` may show repr

## Want smarter answers?

```bash
MODEL=claude-sonnet-5 python starter_anthropic.py    # more stable
MODEL=qwen2.5:7b python starter.py                      # larger local model
```

## Extensions

- **Streaming**: LangGraph `graph.stream(...)`, CrewAI `crew.kickoff(stream=True)`
- **Checkpointing**: LangGraph + `MemorySaver` for time-travel debug
- **Human-in-the-loop**: see Exercise 3
