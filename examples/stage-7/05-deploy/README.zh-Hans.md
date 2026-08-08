<div align="right">
  <a href="./README.md">繁體中文</a> | <strong>简体中文</strong> | <a href="./README.en.md">English</a>
</div>

# 练习 5：Deploy（FastAPI + Docker）

对应 [Stage 7 — Multi-Agent & Production](../../../stages/07-multi-agent-production.zh-Hans.md) 练习 5。
> 🎓 **学习模式**：这份 `starter.py` 是**完整解答**、不是 TODO skeleton。建议用**主动模式**——`mv starter.py starter_reference.py`、看 signature 不看 body、自己重写一份 `starter.py`、跑 `python test.py` 验证；卡 20 分钟再回去对照 reference。完整方法论看 [`docs/HOW_TO_USE.md`](../../../docs/HOW_TO_USE.md)。

> 📚 **想要 chapter-length 深入版？** 本 folder 的 starter 是 illustrative 版、聚焦核心 pattern + 两条 SDK path，不是进阶深度教材。深度教材推荐：
> - [`datawhalechina/hello-agents`](https://github.com/datawhalechina/hello-agents) ⭐ 中文圈最完整、章节式 + 16 种 production 能力。**本练习对应 hello-agents 的 production deploy / harness 章节**
> - [FastAPI official tutorial](https://fastapi.tiangolo.com/tutorial/) + [awesome-harness-engineering](https://github.com/ai-boost/awesome-harness-engineering)（harness pattern 全集）
> - 完整 references 见 [Stage 7 精选 Projects](../../../stages/07-multi-agent-production.zh-Hans.md#-精选-projects范本--sdk--工具-collection)

## 任务

把 agent 包进 production-style HTTP API：

- FastAPI app with `/health` + `/chat` endpoints
- Structured logging with request_id
- Proper HTTP status codes (200 / 422 / 429 / 503 / 500)
- Pydantic schema validation (FastAPI 自动验）
- Dockerfile（含 Ollama 跟 Anthropic 两个 deploy 模式）

## 怎么跑

### Local Ollama

```bash
pip install -r requirements.txt
ollama pull qwen2.5:3b
ollama serve

uvicorn starter:app --reload --port 8000

curl -X POST http://localhost:8000/chat \
  -H 'Content-Type: application/json' \
  -d '{"message": "hi"}'
```

### Local Anthropic

```bash
pip install -r requirements.txt
export ANTHROPIC_API_KEY=sk-ant-...
uvicorn starter_anthropic:app --reload --port 8000
```

### Docker

```bash
docker build -t agent-api .

docker run -p 8000:8000 \
  -e OLLAMA_API_BASE=http://host.docker.internal:11434/v1 \
  agent-api

docker run -p 8000:8000 \
  -e APP_MODULE=starter_anthropic:app \
  -e ANTHROPIC_API_KEY=$ANTHROPIC_API_KEY \
  agent-api
```

## 不启 server 验证

```bash
python test.py             # 5 个 test、用 fastapi.TestClient
python test_anthropic.py   # 3 个 test（含 429 rate limit）
```

## Production 必备

| 元素 | 为什么 | 在这份 starter |
|---|---|---|
| `/health` endpoint | K8s liveness / readiness probe | ✅ |
| `request_id` per call | trace / debug 必备 | ✅ uuid4 |
| Structured logging | ELK / Datadog / Loki 看得懂 | ✅ |
| Pydantic schema validation | malformed JSON 自动 422 | ✅ FastAPI 内建 |
| Specific exception → HTTP status | 503 ≠ 500，client 知道该不该 retry | ✅ APIConnectionError → 503 |
| Token tracking response | cost / token usage 透明 | ✅ Path B 含 input_tokens / output_tokens |

## Status code 对照

| 情况 | HTTP code | client 该怎样 |
|---|---|---|
| LLM 答了 | 200 | 用答案 |
| user 没传 message field | 422 | 修 request、别 retry |
| Anthropic rate limit (429) | 429 | exponential backoff retry |
| LLM 服务断线 (APIConnectionError) | 503 | retry（transient） |
| 其他 unexpected | 500 | log + alert、别自动 retry |

## Deploy targets

| Target | 适合 | 注意 |
|---|---|---|
| **Local uvicorn** | dev | 1 worker、不适 production |
| **Docker + uvicorn** | small prod | 加 `--workers N`、reverse proxy（nginx）前面 |
| **K8s** | scalable prod | liveness/readiness probe 用 `/health` |
| **AWS Lambda + API Gateway** | sporadic traffic | cold start 慢、适合轻量 agent |
| **Cloud Run / Fargate** | 中规模 prod | scale-to-zero、简单 |
| **Anthropic Computer Use / Skills** | very specific use cases | 看 Stage 5 |

## 常见坑

- **没 health check**：load balancer 不知道 instance 死了、流量继续送
- **`/health` 太重**：去打 LLM 确认 = 耗 cost、且 cold start 慢就被踢
- **`request_id` 没记**：trace 散在各 log 里找不到对应
- **All errors → 500**：client 无法分辨 transient（retry）vs permanent（don't retry）。要分 status code
- **synchronous LLM call**：FastAPI 用 `def` 而非 `async def`、会 block event loop。Production 应该用 `async def` + `await client.messages.create(...)` 或 thread pool
- **No rate limiting**：被攻击或 client bug 会打爆 LLM bill。前面加 `slowapi` / nginx rate limit
- **Hard-coded secret**：API key 直接写 code = git 流出。用 env var + secret manager

## 接前面 stages

- **练习 3 observability**：把 `TraceContext` 加进 endpoint、每 request 记 latency / tokens / errors
- **练习 2 eval**：deploy 后跑 CI eval、`pass_rate < 90%` 就 rollback
- **练习 4 caching**：把 system prompt 加 `cache_control`、production cost 立刻减 90%
- **Stage 6 RAG**：endpoint 接 vector DB + memory store

## 延伸

- **加 streaming endpoint**：`@app.post("/chat/stream")` 配 `StreamingResponse` + SSE format
- **加 auth**：FastAPI `Depends(verify_token)` + JWT / API key
- **加 cost limit**：每 user / day 上限 X token、超过 reject
- **接 OpenTelemetry**：`tracer.start_as_current_span("chat_endpoint")` 自动丢去 Datadog
- **K8s manifests**：Deployment + Service + HPA + ConfigMap
