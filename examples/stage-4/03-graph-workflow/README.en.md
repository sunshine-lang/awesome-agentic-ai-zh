<div align="right">
  <a href="./README.md">繁體中文</a> | <a href="./README.zh-Hans.md">简体中文</a> | <strong>English</strong>
</div>

# Exercise 3: Graph Workflow (LangGraph conditional branching + HITL)

Pairs with [Stage 4 — Agent Frameworks](../../../stages/04-agent-frameworks.en.md) Exercise 3.
> 🎓 **How to use this**: `starter.py` is the **complete solution**, not a TODO skeleton. The active approach works better — `mv starter.py starter_reference.py`, read the signatures but not the bodies, write your own `starter.py` from scratch, then run `python test.py` to check it; if you are stuck for 20 minutes, go back and compare against the reference. Full methodology in [`docs/HOW_TO_USE.md`](../../../docs/HOW_TO_USE.md).

> 📚 **Want the chapter-length version?** The starter in this folder is an illustrative build focused on the core pattern plus two SDK paths — it is not in-depth teaching material. Recommended for depth:
> - [`datawhalechina/hello-agents`](https://github.com/datawhalechina/hello-agents) ⭐ the most complete Chinese-language course out there — chapter by chapter, plus 16 production capabilities. **This exercise maps to hello-agents' graph workflow + HITL chapter**
> - [LangGraph HITL tutorial](https://langchain-ai.github.io/langgraph/tutorials/human-in-the-loop/) + [LangGraph time-travel docs](https://langchain-ai.github.io/langgraph/concepts/time-travel/)
> - Full references in [Stage 4 Curated Projects](../../../stages/04-agent-frameworks.en.md#-curated-projects)


## Task

`classify → [search?] → respond → [HITL] → final`

- **`classify_node`**: decides `needs_search` from the query
- **Conditional branch**: `needs_search=True` → `search`, otherwise `respond`
- **HITL checkpoint**: after `respond`, interrupt — wait for a human to write `approved` into state
- **`final_node`**: `approved=True` → PUBLISHED, else REJECTED

This is **LangGraph's sweet spot**: graph state + checkpointing + `interrupt_before` is the signature combo. CrewAI's HITL support is weaker.

## How to run

```bash
pip install -r requirements.txt
python starter.py
```

Budget: **$0**. The nodes here are deterministic logic — no LLM calls. To wire in a real LLM, replace `respond_node` with `llm.invoke(...)`.

```bash
python test.py             # 6 tests for routing + HITL
python test_anthropic.py   # Path B concept demo
```

## LangGraph structure (condensed)

```python
g = StateGraph(State)
g.add_node("classify", classify_node)
g.add_node("search", search_node)
g.add_node("respond", respond_node)
g.add_node("final", final_node)

g.add_edge(START, "classify")
g.add_conditional_edges("classify", should_search, {"search": "search", "respond": "respond"})
g.add_edge("search", "respond")
g.add_edge("respond", "final")
g.add_edge("final", END)

graph = g.compile(checkpointer=InMemorySaver(), interrupt_before=["final"])
```

## How HITL works

```python
# Phase 1: run up to (but not into) final — interrupt_before=["final"] pauses it
state_before = graph.invoke({"query": ...}, config={"configurable": {"thread_id": "demo"}})
# Show state_before["draft"] to a human and ask "publish?"

# Human's decision: write `approved` into state
graph.update_state(config, {"approved": True})

# Phase 2: resume from final (None means "no new input, use checkpoint")
state_after = graph.invoke(None, config=config)
```

**Key**: `interrupt_before=["final"]` tells the graph "stop before entering final". In production, wire this to a webhook / Slack / frontend button, and resume after the user approves.

## Why this pattern matters

| Scenario | Without HITL | With HITL |
|---|---|---|
| Agent sends email | Send directly (risky) | Show draft, human approves |
| Agent changes prod config | Apply directly | Dry-run, wait for approval |
| Agent issues refund | Auto-refund | Refund over $X waits for review |

**Any production agent with side effects should include HITL.** LangGraph's `interrupt_before` is designed for this.

## What to watch on each path

Nodes are deterministic (no LLM), so Path A and Path B run identically. **The focus is the graph structure.** To wire in a real LLM:

```python
# In respond_node:
from langchain_openai import ChatOpenAI  # Path A
# from langchain_anthropic import ChatAnthropic  # Path B
llm = ChatOpenAI(base_url="http://localhost:11434/v1", api_key="ollama", model="qwen2.5:3b")
draft = llm.invoke(state["query"]).content
return {"draft": draft}
```

## Common pitfalls

- **No `checkpointer`**: `graph.compile(interrupt_before=[...])` without a checkpointer raises. You need one to pause/resume
- **`thread_id` mismatch**: phase-1 invoke + update_state + phase-2 invoke must share `config={"configurable": {"thread_id": "..."}}`; otherwise checkpoint not found
- **`interrupt_before` vs `interrupt_after`**: before = pause entering the node; after = pause after the node finishes. **HITL usually wants `before`** (so the human sees full state)
- **`conditional_edges` function must return a string**: `should_search`'s return value must be a key in the third dict of `add_conditional_edges` — can't return a literal node name

## Want smarter answers?

Wire a real LLM into `respond_node`. Production setups also swap the checkpointer to SQLite / Redis (`SqliteSaver` / `RedisSaver`) for persistence.

## Extensions

- **Add retry**: in `search_node` failures, retry via LangGraph's `error` edge
- **Multiple HITL stops**: `interrupt_before=["draft", "publish"]`
- **Time-travel debug**: `graph.get_state_history(config)` gives all checkpoints — fork from any of them
- **Streaming**: `for state in graph.stream(...)` to watch state evolve
