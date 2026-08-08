<div align="right">
  <strong>繁體中文</strong> | <a href="./README.zh-Hans.md">简体中文</a> | <a href="./README.en.md">English</a>
</div>

# 練習 4：SDK 進階（streaming + prompt caching）

對應 [Stage 7 — Multi-Agent & Production](../../../stages/07-multi-agent-production.md) 練習 4。
> 🎓 **學習模式**：這份 `starter.py` 是**完整解答**、不是 TODO skeleton。建議用**主動模式**——`mv starter.py starter_reference.py`、看 signature 不看 body、自己重寫一份 `starter.py`、跑 `python test.py` 驗證；卡 20 分鐘再回去對照 reference。完整方法論看 [`docs/HOW_TO_USE.md`](../../../docs/HOW_TO_USE.md)。

> 📚 **想要 chapter-length 深入版？** 本 folder 的 starter 是 illustrative 版、聚焦核心 pattern + 兩條 SDK path，不是進階深度教材。深度教材推薦：
> - [`datawhalechina/hello-agents`](https://github.com/datawhalechina/hello-agents) ⭐ 中文圈最完整、章節式 + 16 種 production 能力。**本練習對應 hello-agents 的 進階 SDK feature 章節**
> - [Anthropic Prompt Caching docs](https://docs.anthropic.com/en/docs/build-with-claude/prompt-caching) + [Anthropic Batch API](https://docs.anthropic.com/en/docs/build-with-claude/batch-processing)
> - 完整 references 見 [Stage 7 精選 Projects](../../../stages/07-multi-agent-production.md#-精選-projects範本--sdk--工具-collection)


## Production 兩個必備 SDK feature

1. **Streaming** — 邊產 token 邊送 UI、user 0.3-1 秒就看到第一個字（不必等完整答案）
2. **Prompt caching**（Anthropic-only）— 重複 long system prompt / tools / context 省 90% cost

## 怎麼跑

### Path A（默認、本機免費、streaming demo）

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

預算：streaming demo + caching demo ≈ **$0.005**（2 call + cached ~2000 token）。

## 不花錢驗證程式邏輯

```bash
python test.py # 3 個 test、mock OpenAI streaming
python test_anthropic.py # mock Anthropic streaming + cache_control
```

## Streaming 怎麼用

### OpenAI / Ollama

```python
stream = client.chat.completions.create(
    model=..., messages=[...],
    stream=True, # ← key
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

**UX 觀察**：non-streaming 5 秒才看到答案 / streaming 0.5 秒看到第一個字。**user perception 差很大**。

## Prompt Caching 怎麼用（Anthropic-only）

```python
resp = client.messages.create(
    model="claude-haiku-4-5",
    system=[
        {
            "type": "text",
            "text": "[2000-token reference material...]",
            "cache_control": {"type": "ephemeral"}, # ← key
        }
    ],
    messages=[{"role": "user", "content": "..."}]
)
```

第一次寫入：`cache_creation_input_tokens=2000`（25% premium）
之後 5 分鐘內：`cache_read_input_tokens=2000`（10% cost = 90% off）

**何時用**：

- Long system prompt 重複 call（聊天機器人）
- Tool schema 重複（multi-tool agent）
- Document context 重複問（RAG with same doc）

**不用的時候**：

- 每次 prompt 都不同
- 5 分鐘內 call 次數 < 1（cache 過期）

## Production 算盤

對 1000 req/min 的 agent、prompt 含 5000 token system prompt：

| 模式 | Input cost / req | 月 cost（30 天） |
|---|---|---|
| 無 caching | 5000 × $1/M = $0.005 | $216,000 |
| 有 caching | 500 × $1/M = $0.0005 | $21,600 |

**省 90%**——這就是為什麼 production agent 一律用 caching。

## 兩個 path 觀察重點

| 觀察項 | Anthropic Claude | Ollama qwen2.5:3b |
|---|---|---|
| Streaming | ✅ smooth | ✅ smooth |
| First token latency | 0.3-0.8s | 0.5-2s (CPU) |
| Prompt caching | ✅ 90% off | ❌ 無此 API |
| 適合 production 用法 | 全套 caching + streaming | 主要為 dev / 本機 demo |

## 常見坑

### Streaming
- **忘記 `flush=True`**：buffered output、user 還是要等
- **沒處理 None delta**：開頭 / 結尾 chunk 可能 `delta.content is None`、要 skip
- **錯誤處理**：streaming 中途斷線、要 catch + restart
- **Token counting**：streaming response 不一定有 `usage`、要自己 tokenize 或 sum chunks

### Prompt caching
- **`cache_control` 放錯位置**：要在「想 cache 的那段」、不是整個 system。可同時 cache system + tools + 前面幾條 messages
- **Cache key 含 model name**：換 model（haiku → sonnet）cache 失效
- **5 分鐘 TTL**：低 QPS 場景 cache 經常過期、白付 25% premium 沒省到
- **Minimum 1024 tokens**：太短的 content cache 不會生效

## 延伸

- **Streaming + tool use**：tool_use block 也能 stream、用 `event_type` 判斷
- **Anthropic Batch API**：非即時任務丟 batch、省 50% cost、24 小時內回（適合 eval、bulk processing）
- **Files API**：100MB+ 文件直接 upload、cache_control 一起用
- **OpenAI Responses API**：OpenAI 也有 prompt caching（不同 API、自動 cache）、條件不同
- **接 observability（練習 3）**：cache_read_input_tokens 記到 telemetry、追 cache hit rate
