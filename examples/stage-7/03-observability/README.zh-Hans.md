<div align="right">
  <a href="./README.md">繁體中文</a> | <strong>简体中文</strong> | <a href="./README.en.md">English</a>
</div>

# 练习 3：Observability（4 个 production telemetry）

对应 [Stage 7 — Multi-Agent & Production](../../../stages/07-multi-agent-production.zh-Hans.md) 练习 3。
> 🎓 **学习模式**：这份 `starter.py` 是**完整解答**、不是 TODO skeleton。建议用**主动模式**——`mv starter.py starter_reference.py`、看 signature 不看 body、自己重写一份 `starter.py`、跑 `python test.py` 验证；卡 20 分钟再回去对照 reference。完整方法论看 [`docs/HOW_TO_USE.md`](../../../docs/HOW_TO_USE.md)。

> 📚 **想要 chapter-length 深入版？** 本 folder 的 starter 是 illustrative 版、聚焦核心 pattern + 两条 SDK path，不是进阶深度教材。深度教材推荐：
> - [`datawhalechina/hello-agents`](https://github.com/datawhalechina/hello-agents) ⭐ 中文圈最完整、章节式 + 16 种 production 能力。**本练习对应 hello-agents 的 observability / tracing 章节（Extra Chapter）**
> - [Langfuse](https://github.com/langfuse/langfuse) + [Arize Phoenix](https://github.com/Arize-ai/phoenix)（OpenTelemetry-native）
> - 完整 references 见 [Stage 7 精选 Projects](../../../stages/07-multi-agent-production.zh-Hans.md#-精选-projects范本--sdk--工具-collection)

## 任务

Production agent 必备 4 个 telemetry：

1. **Latency**：每个 step 多久（p50/p95/p99）
2. **Token usage**：input / output（追 cost）
3. **Trace**：multi-step agent 每一步（debug + audit）
4. **Errors**：exception + retry count

实作：`TraceContext` + `trace_span` context manager + 在 LLM call 之间 instrument。

## 怎么跑

```bash
pip install -r requirements.txt
ollama pull qwen2.5:3b
ollama serve
python starter.py
```

预算：**$0**（Path A）。Path B 用 Claude：~$0.0001/run。

```bash
python test.py             # 5 个 test
python test_anthropic.py
```

## 4 个 primitive

### Latency（用 contextmanager）

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

- **Anthropic**：`usage.input_tokens` / `usage.output_tokens` 精确
- **OpenAI/Ollama**：`usage.prompt_tokens` / `usage.completion_tokens`、Ollama 偶尔不返回 usage

### Trace

```python
ctx = TraceContext("req_42")
with trace_span(ctx, "search"): ...
with trace_span(ctx, "llm_call"): ...
print(ctx.summary())  # 看整个 request 的 timeline
```

### Errors

```python
@contextmanager
def trace_span(ctx, name):
    try:
        yield
    except Exception as e:
        ctx.add_error(f"{name}: {e}")
        raise   # 重要：raise 出去、不要吞 exception
```

## Production tools（不要自己写）

实作 primitive 是学原理。Production 用 OpenTelemetry + 托管平台：

- **[Langfuse](https://langfuse.com/)**：open-source、self-host、tracing + eval + prompt management 一条龙
- **[LangSmith](https://smith.langchain.com/)**：LangChain ecosystem
- **[Helicone](https://www.helicone.ai/)**：proxy mode、零 code change
- **[Arize Phoenix](https://github.com/Arize-ai/phoenix)**：open-source、OpenTelemetry-native
- **[Datadog LLM Observability](https://www.datadoghq.com/product/llm-observability/)**：integrate with general APM
- **[Anthropic API Console](https://console.anthropic.com/)**：Claude usage / cost 内建 dashboard

## Production checklist

对每个 production agent 至少要回答：

```
[ ] p50 / p95 / p99 latency 多少？
[ ] 每 request 平均花多少 token？($)
[ ] 哪几个 step 最慢？
[ ] 错误率多少？哪一类错最多？
[ ] retry 后 success rate 多少？
[ ] cost / request 趋势（每月）？
[ ] 哪些 query 答错？(连到 eval、练习 2)
```

回答不出来 = 没 observability。

## 两个 path 观察重点

| 观察项 | Anthropic Claude | Ollama qwen2.5:3b |
|---|---|---|
| `usage.tokens` 精确度 | ✅ 完整（含 cache_*） | ⚠ 偶尔没返回 |
| Cost tracking | 直接 cost = token × pricing | $0、但 GPU 时间有成本 |
| Latency 来源 | Network + queue + inference | 纯 inference |
| Production deploy 观察 | 看 Anthropic console | 自己跑 prometheus / grafana |

## 常见坑

- **Token usage 没记**：上线一个月才发现 cost 漏记、无法 forecast
- **Span 不够细**：只记 "agent_call" 整体、没拆 "search" / "rerank" / "generate"、debug 时看不到瓶颈
- **Error swallowed**：context manager 吃掉 exception、上层以为成功
- **production 直接 print()**：应该用 structured logging（JSON / OpenTelemetry）、写去 cloud
- **没 sample 机制**：高 QPS 全量 trace 会塞爆 backend、要 sampling（譬如 10% trace + 100% error）

## 延伸

- **OpenTelemetry 整合**：把 `trace_span` 改成 `tracer.start_as_current_span(...)` 就能丢去 Jaeger / Datadog
- **Langfuse SDK**：3 行接上 Anthropic Claude、自动 trace
- **Prometheus metrics**：counter（request_count）、histogram（latency）、gauge（active_sessions）
- **接 eval（练习 2）**：eval failure 自动 alert 到 Slack
