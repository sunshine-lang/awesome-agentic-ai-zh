<div align="right">
  <a href="./README.md">繁體中文</a> | <strong>简体中文</strong> | <a href="./README.en.md">English</a>
</div>

# 练习 4：SDK 进阶（streaming + prompt caching）

对应 [Stage 7 — Multi-Agent & Production](../../../stages/07-multi-agent-production.zh-Hans.md) 练习 4。
> 🎓 **学习模式**：这份 `starter.py` 是**完整解答**、不是 TODO skeleton。建议用**主动模式**——`mv starter.py starter_reference.py`、看 signature 不看 body、自己重写一份 `starter.py`、跑 `python test.py` 验证；卡 20 分钟再回去对照 reference。完整方法论看 [`docs/HOW_TO_USE.md`](../../../docs/HOW_TO_USE.md)。

> 📚 **想要 chapter-length 深入版？** 本 folder 的 starter 是 illustrative 版、聚焦核心 pattern + 两条 SDK path，不是进阶深度教材。深度教材推荐：
> - [`datawhalechina/hello-agents`](https://github.com/datawhalechina/hello-agents) ⭐ 中文圈最完整、章节式 + 16 种 production 能力。**本练习对应 hello-agents 的进阶 SDK feature 章节**
> - [Anthropic Prompt Caching docs](https://docs.anthropic.com/en/docs/build-with-claude/prompt-caching) + [Anthropic Batch API](https://docs.anthropic.com/en/docs/build-with-claude/batch-processing)
> - 完整 references 见 [Stage 7 精选 Projects](../../../stages/07-multi-agent-production.zh-Hans.md#-精选-projects范本--sdk--工具-collection)

## Production 两个必备 SDK feature

1. **Streaming** — 边产 token 边送 UI、user 0.3-1 秒就看到第一个字（不必等完整答案）
2. **Prompt caching**（Anthropic-only）— 重复 long system prompt / tools / context 省 90% cost

## 怎么跑

### Path A（默认、本机免费、streaming demo）

```bash
pip install -r requirements.txt
ollama pull qwen2.5:3b
ollama serve
python starter.py
```

### Path B（Anthropic、streaming + caching）

```bash
pip install -r requirements.txt
export ANTHROPIC_API_KEY=sk-ant-...
python starter_anthropic.py
```

预算：streaming demo + caching demo ≈ **$0.005**（2 call + cached ~2000 token）。

## 不花钱验证程序逻辑

```bash
python test.py             # 3 个 test、mock OpenAI streaming
python test_anthropic.py   # mock Anthropic streaming + cache_control
```

## Streaming 怎么用

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

**UX 观察**：non-streaming 5 秒才看到答案 / streaming 0.5 秒看到第一个字。**user perception 差很大**。

## Prompt Caching 怎么用（Anthropic-only）

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

第一次写入：`cache_creation_input_tokens=2000`（25% premium）
之后 5 分钟内：`cache_read_input_tokens=2000`（10% cost = 90% off）

**何时用**：

- Long system prompt 重复 call（聊天机器人）
- Tool schema 重复（multi-tool agent）
- Document context 重复问（RAG with same doc）

**不用的时候**：

- 每次 prompt 都不同
- 5 分钟内 call 次数 < 1（cache 过期）

## Production 算盘

对 1000 req/min 的 agent、prompt 含 5000 token system prompt：

| 模式 | Input cost / req | 月 cost（30 天） |
|---|---|---|
| 无 caching | 5000 × $1/M = $0.005 | $216,000 |
| 有 caching | 500 × $1/M = $0.0005 | $21,600 |

**省 90%**——这就是为什么 production agent 一律用 caching。

## 两个 path 观察重点

| 观察项 | Anthropic Claude | Ollama qwen2.5:3b |
|---|---|---|
| Streaming | ✅ smooth | ✅ smooth |
| First token latency | 0.3-0.8s | 0.5-2s (CPU) |
| Prompt caching | ✅ 90% off | ❌ 无此 API |
| 适合 production 用法 | 全套 caching + streaming | 主要为 dev / 本机 demo |

## 常见坑

### Streaming
- **忘记 `flush=True`**：buffered output、user 还是要等
- **没处理 None delta**：开头 / 结尾 chunk 可能 `delta.content is None`、要 skip
- **错误处理**：streaming 中途断线、要 catch + restart
- **Token counting**：streaming response 不一定有 `usage`、要自己 tokenize 或 sum chunks

### Prompt caching
- **`cache_control` 放错位置**：要在“想 cache 的那段”、不是整个 system。可同时 cache system + tools + 前面几条 messages
- **Cache key 含 model name**：换 model（haiku → sonnet）cache 失效
- **5 分钟 TTL**：低 QPS 场景 cache 经常过期、白付 25% premium 没省到
- **Minimum 1024 tokens**：太短的 content cache 不会生效

## 延伸

- **Streaming + tool use**：tool_use block 也能 stream、用 `event_type` 判断
- **Anthropic Batch API**：非实时任务丢 batch、省 50% cost、24 小时内回（适合 eval、bulk processing）
- **Files API**：100MB+ 文件直接 upload、cache_control 一起用
- **OpenAI Responses API**：OpenAI 也有 prompt caching（不同 API、自动 cache）、条件不同
- **接 observability（练习 3）**：cache_read_input_tokens 记到 telemetry、追 cache hit rate
