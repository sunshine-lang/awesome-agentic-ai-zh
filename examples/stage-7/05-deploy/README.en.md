<div align="right">
  <a href="./README.md">繁體中文</a> | <a href="./README.zh-Hans.md">简体中文</a> | <strong>English</strong>
</div>

# Exercise 5: Deploy (FastAPI + Docker)

Pairs with [Stage 7 — Multi-Agent & Production](../../../stages/07-multi-agent-production.en.md) Exercise 5.
> 🎓 **How to use this**: `starter.py` is the **complete solution**, not a TODO skeleton. The active approach works better — `mv starter.py starter_reference.py`, read the signatures but not the bodies, write your own `starter.py` from scratch, then run `python test.py` to check it; if you are stuck for 20 minutes, go back and compare against the reference. Full methodology in [`docs/HOW_TO_USE.md`](../../../docs/HOW_TO_USE.md).

> 📚 **Want the chapter-length version?** The starter in this folder is an illustrative build focused on the core pattern plus two SDK paths — it is not in-depth teaching material. Recommended for depth:
> - [`datawhalechina/hello-agents`](https://github.com/datawhalechina/hello-agents) ⭐ the most complete Chinese-language resource — chapter-by-chapter, covering 16 production capabilities. **This exercise maps to hello-agents' production deploy / harness chapter**
> - [FastAPI official tutorial](https://fastapi.tiangolo.com/tutorial/) + [awesome-harness-engineering](https://github.com/ai-boost/awesome-harness-engineering) (a full collection of harness patterns)
> - Full references in [Stage 7 Curated Projects](../../../stages/07-multi-agent-production.en.md#-featured-projects-templates--sdks--tool-collections)

## Task

Package the agent as a production-style HTTP API:

- FastAPI app with `/health` + `/chat` endpoints
- Structured logging with `request_id`
- Proper HTTP status codes (200 / 422 / 429 / 503 / 500)
- Pydantic schema validation (FastAPI free)
- Dockerfile (covers both Ollama and Anthropic deploys)

## How to run

### Local Ollama

```bash
pip install -r requirements.txt
ollama pull qwen2.5:3b
ollama serve

uvicorn starter:app --reload --port 8000

# In another shell:
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

# Ollama path (host must run ollama)
docker run -p 8000:8000 \
  -e OLLAMA_API_BASE=http://host.docker.internal:11434/v1 \
  agent-api

# Anthropic path
docker run -p 8000:8000 \
  -e APP_MODULE=starter_anthropic:app \
  -e ANTHROPIC_API_KEY=$ANTHROPIC_API_KEY \
  agent-api
```

## Validate without starting the server

```bash
python test.py             # 5 tests via fastapi.TestClient
python test_anthropic.py   # 3 tests (incl. 429 rate limit)
```

`fastapi.TestClient` uses in-process ASGI — no real port, no Docker.

## Production essentials

| Element | Why | In this starter |
|---|---|---|
| `/health` endpoint | K8s liveness/readiness probes | ✅ |
| `request_id` per call | Trace / debug | ✅ uuid4 |
| Structured logging | ELK / Datadog / Loki parseable | ✅ JSON-like format |
| Pydantic schema validation | Malformed JSON → 422 automatically | ✅ FastAPI built-in |
| Specific exception → HTTP status | 503 ≠ 500 — client knows whether to retry | ✅ APIConnectionError → 503 |
| Token tracking in response | Cost / token usage transparency | ✅ Path B includes input/output tokens |

## Status codes

| Situation | HTTP code | Client should |
|---|---|---|
| LLM answered | 200 | Use answer |
| Missing `message` field | 422 | Fix request, don't retry |
| Anthropic rate limit (429) | 429 | Exponential backoff retry |
| LLM service disconnected | 503 | Retry (transient) |
| Other unexpected | 500 | Log + alert, don't auto-retry |

## Deploy targets

| Target | Good for | Watch out |
|---|---|---|
| **Local uvicorn** | Dev | 1 worker, not for prod |
| **Docker + uvicorn** | Small prod | Add `--workers N`, put nginx in front |
| **K8s** | Scalable prod | Use `/health` for liveness/readiness |
| **AWS Lambda + API Gateway** | Sporadic traffic | Slow cold starts, fits light agents |
| **Cloud Run / Fargate** | Mid-scale prod | Scale-to-zero, simple |
| **Anthropic Computer Use / Skills** | Very specific use cases | See Stage 5 |

## Common pitfalls

- **No health check**: load balancer can't detect dead instances
- **Heavy `/health`**: calling the LLM to verify = wasted cost + slow startup gets you killed
- **Missing `request_id`**: traces scattered across logs, can't correlate
- **All errors → 500**: client can't distinguish transient (retry) vs permanent. Use specific codes
- **Synchronous LLM call in `def`**: FastAPI blocks the event loop. Use `async def` + `await client.messages.create(...)` or a thread pool
- **No rate limiting**: attackers or buggy clients explode your LLM bill. Add `slowapi` / nginx rate limit
- **Hard-coded secrets**: API key in code = git leak. Use env vars + secret manager

## Connecting back to earlier exercises

- **Exercise 3 observability**: add `TraceContext` to endpoint, log latency / tokens / errors per request
- **Exercise 2 eval**: post-deploy CI eval, `pass_rate < 90%` triggers rollback
- **Exercise 4 caching**: cache_control on the system prompt — 90% cost cut immediately
- **Stage 6 RAG**: endpoint wires up vector DB + memory store

## Extensions

- **Streaming endpoint**: `@app.post("/chat/stream")` with `StreamingResponse` + SSE format
- **Auth**: FastAPI `Depends(verify_token)` + JWT / API key
- **Cost limit**: per-user / per-day token cap, reject above limit
- **OpenTelemetry**: `tracer.start_as_current_span("chat_endpoint")` ships traces to Datadog
- **K8s manifests**: Deployment + Service + HPA + ConfigMap
