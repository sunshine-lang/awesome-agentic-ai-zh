<div align="right">
  <a href="./README.md">繁體中文</a> | <a href="./README.zh-Hans.md">简体中文</a> | <strong>English</strong>
</div>

# Exercise 5: Long-term Memory (remember across turns)

Pairs with [Stage 6 — Memory & RAG](../../../stages/06-memory-rag.en.md) Exercise 5.
> 🎓 **How to use this**: `starter.py` is the **complete solution**, not a TODO skeleton. The active approach works better — `mv starter.py starter_reference.py`, read the signatures but not the bodies, write your own `starter.py` from scratch, then run `python test.py` to check it; if you are stuck for 20 minutes, go back and compare against the reference. Full methodology in [`docs/HOW_TO_USE.md`](../../../docs/HOW_TO_USE.md).

> 📚 **Want the chapter-length version?** The starter in this folder is an illustrative build focused on the core pattern plus two SDK paths — it is not in-depth teaching material. Recommended for depth:
> - [`datawhalechina/hello-agents`](https://github.com/datawhalechina/hello-agents) ⭐ The most complete chapter-based course in Chinese — 16 production capabilities. **This exercise maps to hello-agents' long-term memory chapter**
> - [mem0](https://github.com/mem0ai/mem0) (auto fact extraction + forgetting) + [Letta / MemGPT](https://github.com/letta-ai/letta) (two-tier memory pattern)
> - Full references in [Stage 6 Curated Projects](../../../stages/06-memory-rag.en.md#-featured-projects-templates--specs--example-collections)

## Task

Agent remembers things across conversation turns. Implementation:

```
Turn 1: user: "I live in Taipei and prefer Python."
        → maybe_remember_fact() catches "I + verb...", stores in vector store
Turn 2: user: "What's 2+2?"        → recall returns nothing relevant, pure arithmetic
Turn 3: user: "Recommend a language for me."
        → recall pulls "prefer Python", drops it into the system prompt → LLM recommends Python
```

This is **RAG's other side** — what you retrieve isn't documents, it's conversation history.

## How to run

### Path A (default, free, local)

```bash
pip install -r requirements.txt
ollama pull qwen2.5:3b
ollama serve
python starter.py
```

Budget: **$0**.

### Path B (Anthropic)

```bash
pip install -r requirements.txt
export ANTHROPIC_API_KEY=sk-ant-...
python starter_anthropic.py
```

Budget: ~**$0.001** per run.

## Validate the logic

```bash
python test.py             # 5 tests with mock LLM
python test_anthropic.py   # Anthropic mock
```

## MemoryStore + chat flow

```python
class MemoryStore:
    def remember(self, fact: str) -> str:   # add to vector store
    def recall(self, query: str) -> list:    # top-k semantic search

def chat(user_msg, memory):
    memories = memory.recall(user_msg, top_k=3)   # 1. fetch relevant memories
    system = f"Relevant memories: {memories}"      # 2. put them in system prompt
    return llm.invoke(system + user_msg)           # 3. LLM uses them
```

**Key**: don't store memory as "context window history" (would blow the limit) — store as "semantic search index" — LLM only sees relevant ones.

## vs. plain chat history

| Dimension | Chat history (in-context) | Vector memory store |
|---|---|---|
| Stored where | messages array | ChromaDB |
| Capacity | Context window (200k-2M tokens) | Unbounded (millions of facts) |
| Cross-session | ❌ Session ends, gone | ✅ Persistent |
| Retrieval | All history in prompt (eats tokens) | top-k semantic search (precise) |
| Good for | Short conversations, single session | Long-term user relationships, multi-session, persona |

**Production**: use both — last N turns in-context, beyond N + cross-session via vector memory.

## What's a "memory-worthy fact"

This demo uses a heuristic: user says "I + verb..." → store. Production is more sophisticated:

1. **Explicit trigger**: user says "remember that..."
2. **Profile facts**: location / language / role / preferences
3. **Past decisions**: how the agent handled some situation before
4. **Negative feedback**: "don't suggest X" must persist
5. **LLM-extracted**: each turn, use an LLM to extract facts (mem0 / Letta / MemGPT all do this)

## What to watch on each path

| Observation | Anthropic Claude haiku | Ollama qwen2.5:3b |
|---|---|---|
| Weaving memory into the answer | Natural (cites the memory) | Sometimes ignores memory, falls back on a generic answer |
| Not forcing it when no memory is relevant | Follows the rule | Looser |
| Integrating multiple memories | Good | Medium |

## Common pitfalls

- **Add to memory every turn**: vector store explodes. Filter with fact extraction
- **No dedup**: user says "I live in Taipei" 5 turns in a row, 5 copies stored. Add dedup (similarity > 0.95 = duplicate)
- **No forget / update mechanism**: user moved — "I now live in Tokyo". Old "Taipei" memory? Need a supersede concept
- **No context size control**: top-k too big, context bloats, LLM distracted
- **Privacy / GDPR**: user requests deletion; need `forget(user_id)` API

## Production-ready tools

- **[mem0](https://github.com/mem0ai/mem0)**: full memory pipeline — auto-fact-extraction, forgetting, user-scoped namespaces
- **[Letta (formerly MemGPT)](https://github.com/letta-ai/letta)**: two-tier memory (working + archival), OS-paging concept for LLMs
- **CrewAI memory**: built-in short / long-term memory
- **LangGraph checkpointer + persistent storage**: thread-level memory out of the box

## Extensions

- **Dedup**: `if similarity(new, existing) > 0.95: skip`
- **LLM-based fact extraction**: each turn, a small LLM extracts facts — beats heuristics
- **user_id scoping**: MemoryStore takes `user_id` filter so users don't contaminate each other
- **Plug into [mem0](https://github.com/mem0ai/mem0)**: don't roll your own memory pipeline in production
