<div align="right">
  <a href="./README.md">繁體中文</a> | <a href="./README.zh-Hans.md">简体中文</a> | <strong>English</strong>
</div>

# Exercise 4: Advanced SDK (streaming + prompt caching)

Pairs with [Stage 7 — Multi-Agent & Production](../../../stages/07-multi-agent-production.en.md) Exercise 4.
> 🎓 **How to use this**: `starter.py` is the **complete solution**, not a TODO skeleton. The active approach works better — `mv starter.py starter_reference.py`, read the signatures but not the bodies, write your own `starter.py` from scratch, then run `python test.py` to check it; if you are stuck for 20 minutes, go back and compare against the reference. Full methodology in [`docs/HOW_TO_USE.md`](../../../docs/HOW_TO_USE.md).

> 📚 **Want the chapter-length version?** The starter in this folder is an illustrative build focused on the core pattern plus two SDK paths — it is not in-depth teaching material. Recommended for depth:
> - [`datawhalechina/hello-agents`](https://github.com/datawhalechina/hello-agents) ⭐ the most complete Chinese-language resource — chapter-by-chapter, covering 16 production capabilities. **This exercise maps to hello-agents' advanced SDK features chapter**
> - [Anthropic Prompt Caching docs](https://docs.anthropic.com/en/docs/build-with-claude/prompt-caching) + [Anthropic Batch API](https://docs.anthropic.com/en/docs/build-with-claude/batch-processing)
> - Full references in [Stage 7 Curated Projects](../../../stages/07-multi-agent-production.en.md#-featured-projects-templates--sdks--tool-collections)

## Two SDK features production needs

1. **Streaming** — send tokens to UI as they're generated; user sees first token in 0.3-1s instead of waiting for full answer
2. **Prompt caching** (Anthropic-only) — repeated long system prompts / tools / context save 90% cost

## How to run

### Path A (default, free, local, streaming demo)

```bash
pip install -r requirements.txt
ollama pull qwen2.5:3b
ollama serve
python starter.py
```

### Path B (Anthropic, streaming + caching)

```bash
pip install -r requirements.txt
export ANTHROPIC_API_KEY=sk-ant-...
python starter_anthropic.py
```

Budget: streaming + caching demo ≈ **$0.005** (2 calls + cached ~2000 tokens).

## Validate the logic

```bash
python test.py             # 3 tests, mock OpenAI streaming
python test_anthropic.py   # mock Anthropic streaming + cache_control
```

## Streaming

### OpenAI / Ollama

```python
stream = client.chat.completions.create(
    model=..., messages=[...],
    stream=True,
)
for chunk in stream:
    delta = chunk.choices[0].delta.content
    if delta:
        print(delta, end="", flush=True)
```

### Anthropic

```python
with client.messages.stream(
    model=..., max_tokens=300, messages=[...]
) as stream:
    for text in stream.text_stream:
        print(text, end="", flush=True)
```

**UX impact**: non-streaming = 5s wait for the answer; streaming = first token in 0.5s. **Perception is dramatically different.**

## Prompt caching (Anthropic-only)

```python
resp = client.messages.create(
    model="claude-haiku-4-5",
    system=[
        {
            "type": "text",
            "text": "[2000-token reference material...]",
            "cache_control": {"type": "ephemeral"},
        }
    ],
    messages=[{"role": "user", "content": "..."}]
)
```

First call: `cache_creation_input_tokens=2000` (25% write premium)
Subsequent calls within 5 min: `cache_read_input_tokens=2000` (10% cost = 90% off)

**When to use**:

- Long system prompts called repeatedly (chatbots)
- Tool schemas reused across calls (multi-tool agents)
- Same document queried multiple times (RAG on a fixed doc)

**When not**:

- Every prompt is unique
- Fewer than 1 call per 5 min (cache expires)

## Production math

For an agent at 1000 req/min with 5000-token system prompt:

| Mode | Input cost / req | Monthly (30 days) |
|---|---|---|
| No caching | 5000 × $1/M = $0.005 | $216,000 |
| With caching | 500 × $1/M = $0.0005 | $21,600 |

**90% savings** — this is why production agents universally use caching.

## Path observations

| Observation | Anthropic Claude | Ollama qwen2.5:3b |
|---|---|---|
| Streaming | ✅ smooth | ✅ smooth |
| First-token latency | 0.3-0.8s | 0.5-2s (CPU) |
| Prompt caching | ✅ 90% off | ❌ no API |
| Production fit | Full caching + streaming | Mostly for dev / local demo |

## Common pitfalls

### Streaming
- **Forgetting `flush=True`**: buffered output, user still waits
- **Not handling None deltas**: first/last chunks may have `delta.content is None` — skip them
- **Mid-stream disconnection**: catch + restart
- **Token counting**: streaming responses may not include `usage` — tokenize or sum chunks yourself

### Prompt caching
- **`cache_control` in the wrong place**: attach to the segment you want cached. Can cache system + tools + first few messages simultaneously
- **Cache key includes model name**: switching haiku → sonnet invalidates
- **5-minute TTL**: low-QPS scenarios expire often, pay 25% premium without saving
- **Minimum 1024 tokens**: shorter content won't cache

## Extensions

- **Streaming + tool use**: tool_use blocks also stream; use `event_type` to dispatch
- **Anthropic Batch API**: non-realtime work, batch costs 50% less, 24h turnaround (great for eval, bulk processing)
- **Files API**: upload 100MB+ docs, combine with cache_control
- **OpenAI Responses API**: OpenAI also has prompt caching (different API, automatic) — different rules
- **Wire to observability (Exercise 3)**: log `cache_read_input_tokens` to track cache hit rate
