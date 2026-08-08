<div align="right">
  <a href="./README.md">繁體中文</a> | <a href="./README.zh-Hans.md">简体中文</a> | <strong>English</strong>
</div>

# Exercise 3: Observability (4 production telemetry primitives)

Pairs with [Stage 7 — Multi-Agent & Production](../../../stages/07-multi-agent-production.en.md) Exercise 3.
> 🎓 **How to use this**: `starter.py` is the **complete solution**, not a TODO skeleton. The active approach works better — `mv starter.py starter_reference.py`, read the signatures but not the bodies, write your own `starter.py` from scratch, then run `python test.py` to check it; if you are stuck for 20 minutes, go back and compare against the reference. Full methodology in [`docs/HOW_TO_USE.md`](../../../docs/HOW_TO_USE.md).

> 📚 **Want the chapter-length version?** The starter in this folder is an illustrative build focused on the core pattern plus two SDK paths — it is not in-depth teaching material. Recommended for depth:
> - [`datawhalechina/hello-agents`](https://github.com/datawhalechina/hello-agents) ⭐ the most complete Chinese-language resource — chapter-by-chapter, covering 16 production capabilities. **This exercise maps to hello-agents' observability / tracing chapter (Extra Chapter)**
> - [Langfuse](https://github.com/langfuse/langfuse) + [Arize Phoenix](https://github.com/Arize-ai/phoenix) (OpenTelemetry-native)
> - Full references in [Stage 7 Curated Projects](../../../stages/07-multi-agent-production.en.md#-featured-projects-templates--sdks--tool-collections)

## Task

Production agents need 4 telemetry primitives:

1. **Latency** — per-step timing (p50/p95/p99)
2. **Token usage** — input/output (cost tracking)
3. **Trace** — every step of a multi-step agent (debug + audit)
4. **Errors** — exceptions + retry count

Implementation: `TraceContext` + `trace_span` context manager wrapping LLM calls.

## How to run

```bash
pip install -r requirements.txt
ollama pull qwen2.5:3b
ollama serve
python starter.py
```

Budget: **$0** (Path A). Path B with Claude: ~$0.0001/run.

```bash
python test.py             # 5 tests
python test_anthropic.py
```

## The 4 primitives

### Latency (via contextmanager)

```python
@contextmanager
def trace_span(ctx, name, **extras):
    t0 = time.perf_counter()
    try:
        yield
    finally:
        latency_ms = (time.perf_counter() - t0) * 1000
        ctx.add_span(name, latency_ms, **extras)

with trace_span(ctx, "search_step"):
    result = expensive_search(query)
```

### Token usage

```python
resp = client.messages.create(...)
ctx.add_tokens(input_t=resp.usage.input_tokens, output_t=resp.usage.output_tokens)
```

- **Anthropic**: `usage.input_tokens` / `usage.output_tokens` are precise
- **OpenAI/Ollama**: `usage.prompt_tokens` / `usage.completion_tokens`; Ollama occasionally omits usage

### Trace

```python
ctx = TraceContext("req_42")
with trace_span(ctx, "search"): ...
with trace_span(ctx, "llm_call"): ...
print(ctx.summary())  # full request timeline
```

### Errors

```python
@contextmanager
def trace_span(ctx, name):
    try:
        yield
    except Exception as e:
        ctx.add_error(f"{name}: {e}")
        raise   # critical: re-raise, don't swallow
```

## Production tools (don't roll your own)

These primitives are for learning. In production use OpenTelemetry + a managed platform:

- **[Langfuse](https://langfuse.com/)** — open source, self-hostable, tracing + eval + prompt management
- **[LangSmith](https://smith.langchain.com/)** — LangChain ecosystem
- **[Helicone](https://www.helicone.ai/)** — proxy mode, zero code change
- **[Arize Phoenix](https://github.com/Arize-ai/phoenix)** — open source, OpenTelemetry-native
- **[Datadog LLM Observability](https://www.datadoghq.com/product/llm-observability/)** — integrates with APM
- **[Anthropic API Console](https://console.anthropic.com/)** — built-in Claude cost dashboard

## Production checklist

For every production agent you must be able to answer:

```
[ ] What's the p50 / p95 / p99 latency?
[ ] Average tokens per request? ($)
[ ] Which step is slowest?
[ ] Error rate? Most common error?
[ ] Retry success rate?
[ ] Cost/request trend (monthly)?
[ ] Which queries get wrong answers? (connects to eval, Exercise 2)
```

Can't answer = no observability.

## Path observations

| Observation | Anthropic Claude | Ollama qwen2.5:3b |
|---|---|---|
| `usage.tokens` precision | ✅ Complete (incl. cache_*) | ⚠ Sometimes missing |
| Cost tracking | Direct: tokens × pricing | $0 but GPU time has cost |
| Latency source | Network + queue + inference | Pure inference |
| Production observation | Anthropic console | Self-host prometheus/grafana |

## Common pitfalls

- **No token tracking**: a month into production you can't forecast cost
- **Spans too coarse**: only logging "agent_call" hides the bottleneck (search vs rerank vs generate)
- **Swallowed errors**: context manager eats exception, caller thinks success
- **Production using `print()`**: use structured logging (JSON / OpenTelemetry), ship to cloud
- **No sampling**: high QPS = trace backend overwhelmed; sample (e.g., 10% of traces, 100% of errors)

## Extensions

- **OpenTelemetry**: replace `trace_span` with `tracer.start_as_current_span(...)` — ship to Jaeger / Datadog
- **Langfuse SDK**: 3-line integration with Anthropic Claude, automatic tracing
- **Prometheus metrics**: counter (request_count), histogram (latency), gauge (active_sessions)
- **Wire to eval (Exercise 2)**: eval failures auto-alert to Slack
