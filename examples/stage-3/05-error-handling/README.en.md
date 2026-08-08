<div align="right">
  <a href="./README.md">繁體中文</a> | <a href="./README.zh-Hans.md">简体中文</a> | <strong>English</strong>
</div>

# Exercise 5: Tool Error Handling

Corresponds to [Stage 3 — Tool Use & Agent Intro](../../../stages/03-tool-use-and-hello-agent.en.md) Exercise 5.
> 🎓 **How to use this**: `starter.py` is the **complete solution**, not a TODO skeleton. The active approach works better — `mv starter.py starter_reference.py`, read the signatures but not the bodies, write your own `starter.py` from scratch, then run `python test.py` to check it; if you are stuck for 20 minutes, go back and compare against the reference. Full methodology in [`docs/HOW_TO_USE.md`](../../../docs/HOW_TO_USE.md).

> 📚 **Want the chapter-length version?** The starter in this folder is a 70-150 line illustrative build focused on `the core pattern + two SDK paths` — it is not in-depth teaching material. Recommended for depth:
> - [`datawhalechina/hello-agents`](https://github.com/datawhalechina/hello-agents) ⭐ the most complete Chinese-language course out there — chapter-based, covering 16 production capabilities. **this exercise maps to hello-agents' Extra Chapter on error handling / circuit breakers**
> - [Rule 5 — structured error returns](../../../resources/schema-design-cheatsheet.en.md) (the cheatsheet already in this repo)
> - Full references in [Stage 3 Curated Projects](../../../stages/03-tool-use-and-hello-agent.en.md#-curated-projects)


## Why this matters

Real agents rarely walk the happy path only: APIs time out, third parties go down, users send bad inputs. This exercise deliberately makes `fetch_weather(city)` return a **structured error** on the first call (`{"error": "network timeout", "retry_hint": "try again in 1s"}`) and succeed on the second; you observe how the ReAct loop hands the error observation back to the LLM and lets the model decide whether to retry, change the query, or give up.

Core idea: **tool errors are data, not exceptions**. Return structured dicts, don't raise.

## How to run — two paths

### Path A (default, free, local)

```bash
pip install -r requirements.txt
ollama pull qwen2.5:3b
ollama serve
python starter.py
```

Budget: **$0**. A 3-round loop takes ~10-60s.

### Path B (Anthropic, cloud-quality comparison)

```bash
pip install -r requirements.txt
export ANTHROPIC_API_KEY=sk-ant-...
python starter_anthropic.py
```

Budget: ~**$0.003** per run (claude-haiku-4-5, 3 rounds of accumulating messages).

Expected output (Path A, local, ideal retry-then-succeed path):

```
❓ Question: Will it rain in Taipei today? (using Ollama qwen2.5:3b)
------------------------------------------------------------
[step 0] tool: fetch_weather({'city': 'Taipei'}) → {'error': 'network timeout', 'retry_hint': 'try again in 1s'}
[step 1] tool: fetch_weather({'city': 'Taipei'}) → {'city': 'Taipei', 'forecast': 'rain', 'temperature_c': 24}
------------------------------------------------------------
✅ Final answer: It will rain in Taipei today (24°C).
✅ Exercise 5 passed — tool errors are data, not exceptions, $0/run
```

## Validate the logic without API credits (mock-based)

```bash
python test.py            # validates Path A (Ollama) starter.py logic
python test_anthropic.py  # validates Path B (Anthropic) starter_anthropic.py logic
```

Both test suites use `unittest.mock`, no real API call, $0/run.

## Design reminders

Errors should be structured data, so the LLM has context to make decisions:

| Bad | Good |
|---|---|
| `raise Exception("failed")` | `return {"error": "network timeout", "retry_hint": "try again in 1s"}` |
| `return "failed"` | `return {"error": "...", "category": "transient", "retry_hint": "..."}` |
| Unbounded retry | `max_iter` safety + business-layer retry quota |

Returning just `"failed"` leaves the model with nothing to act on. Adding `retry_hint`, error category, and recovery suggestions gives the model enough context to choose. And cap your retries — otherwise the agent loops forever on a broken tool.

## What to watch on each path

**Side observation**: small models (qwen2.5:3b) follow `retry_hint` less reliably than Claude — they might give up immediately or ignore the hint and repeat the same call. **That's exactly the teaching point**: in production, the same retry pattern produces different behaviors depending on how well a model reads structured errors — a real consideration when picking a model (we'll revisit in Stage 7).

| Observation | Anthropic Claude haiku | Ollama qwen2.5:3b |
|---|---|---|
| Retries on `retry_hint` | High | Medium (may give up) |
| Graceful end after repeated failure | Stable | May retry a third time |
| Distinguishing transient vs permanent | Finer | Coarser |

## Want smarter answers?

Default is `claude-haiku-4-5` (cheapest). Try Sonnet:

```bash
MODEL=claude-sonnet-5 python starter_anthropic.py
```

Or on the Ollama path, swap to a larger model:

```bash
MODEL=qwen2.5:7b python starter.py
```

## Extensions

- **Add a retry quota** — track `error_count` and give up after N
- **Add a circuit breaker** — after consecutive failures, stop calling for a while (avoids wave-after-wave on a broken downstream)
- **Classify errors** — transient (429 / connection) vs permanent (401 / 400) get different handling
- **Production tier** — see [`../../stage-1/05-error-handling/`](../../stage-1/05-error-handling/) for an API-level retry wrapper with exponential backoff + jitter
