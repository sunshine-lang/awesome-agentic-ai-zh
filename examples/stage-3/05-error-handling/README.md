<div align="right">
  <strong>繁體中文</strong> | <a href="./README.zh-Hans.md">简体中文</a> | <a href="./README.en.md">English</a>
</div>

# 練習 5：Tool 錯誤處理

對應 [Stage 3 — Tool Use & Agent 入門](../../../stages/03-tool-use-and-hello-agent.md) 練習 5。
> 🎓 **學習模式**：這份 `starter.py` 是**完整解答**、不是 TODO skeleton。建議用**主動模式**——`mv starter.py starter_reference.py`、看 signature 不看 body、自己重寫一份 `starter.py`、跑 `python test.py` 驗證；卡 20 分鐘再回去對照 reference。完整方法論看 [`docs/HOW_TO_USE.md`](../../../docs/HOW_TO_USE.md)。

> 📚 **想要 chapter-length 深入版？** 本 folder 的 starter 是 70-150 行 illustrative 版、聚焦 `核心 pattern + 兩條 SDK path`，不是進階深度教材。深度教材推薦：
> - [`datawhalechina/hello-agents`](https://github.com/datawhalechina/hello-agents) ⭐ 中文圈最完整、章節式 + 16 種 production 能力。**本練習對應 hello-agents 的 Extra Chapter 錯誤處理 / circuit breaker**
> - [規則 5 結構化錯誤回傳](../../../resources/schema-design-cheatsheet.md)（本 repo 既有 cheatsheet）
> - 完整 references 見 [Stage 3 精選 Projects](../../../stages/03-tool-use-and-hello-agent.md#-精選-projects)


## 為什麼這題重要

真實 agent 很少只走成功路徑：API 會 timeout、第三方服務暫時不可用、user 傳壞參數。這題故意讓 `fetch_weather(city)` 第一次回**結構化 error**（`{"error": "network timeout", "retry_hint": "try again in 1s"}`）、第二次才成功；觀察 ReAct loop 怎麼把 error observation 交回 LLM、讓模型自己決定 retry / 改 query / 放棄。

核心觀念：**tool error 是資料、不是 exception**。回傳結構化 dict、不要 raise。

## 怎麼跑 — 兩條路徑

### Path A（默認、本機免費）

```bash
pip install -r requirements.txt
ollama pull qwen2.5:3b
ollama serve
python starter.py
```

預算：**$0**。3 輪 loop ≈ 10-60 秒。

### Path B（Anthropic、想看 cloud 高品質）

```bash
pip install -r requirements.txt
export ANTHROPIC_API_KEY=sk-ant-...
python starter_anthropic.py
```

預算：每次 ≈ **$0.003**（claude-haiku-4-5、3 輪 messages 累積）。

預期看到（Path A、本機，理想 retry 走法）：

```
❓ 問題：Will it rain in Taipei today?（using Ollama qwen2.5:3b）
------------------------------------------------------------
[step 0] tool: fetch_weather({'city': 'Taipei'}) → {'error': 'network timeout', 'retry_hint': 'try again in 1s'}
[step 1] tool: fetch_weather({'city': 'Taipei'}) → {'city': 'Taipei', 'forecast': 'rain', 'temperature_c': 24}
------------------------------------------------------------
✅ 最終答案：It will rain in Taipei today (24°C).
✅ 練習 5 通過 — tool error 是 data 不是 exception、$0/run
```

## 不花錢驗證程式邏輯（mock-based）

```bash
python test.py # 驗 Path A (Ollama) starter.py 邏輯
python test_anthropic.py # 驗 Path B (Anthropic) starter_anthropic.py 邏輯
```

兩條 test 都用 `unittest.mock`、不打真 API、$0/run。

## 設計提醒

錯誤也應該是結構化資料，讓 LLM 有 context 做決策：

| Bad | Good |
|---|---|
| `raise Exception("failed")` | `return {"error": "network timeout", "retry_hint": "try again in 1s"}` |
| `return "failed"` | `return {"error": "...", "category": "transient", "retry_hint": "..."}` |
| 無限 retry | `max_iter` safety + 業務層 retry quota |

只回傳 `"failed"` 讓模型不知道下一步；加入 `retry_hint`、錯誤類型與可恢復建議，模型才有足夠 context 做決策。retry 次數也要有限制，否則 agent 會在壞掉的工具前面無限打轉。

## 兩個 path 觀察重點

**附加觀察**：小 model（qwen2.5:3b）對 `retry_hint` 的 follow-up 可能不如 Claude 精細——可能會直接放棄、或無視 hint 重複同一個錯。**這恰好是教學點**：production 寫好 retry pattern 後，不同 model 對結構化 error 的「閱讀力」差距，是選 model 的考量之一（Stage 7 production tier 會再回來討論）。

| 觀察項 | Anthropic Claude haiku | Ollama qwen2.5:3b |
|---|---|---|
| 看到 retry_hint 就 retry | 高機率 | 中機率（可能直接放棄） |
| 連續失敗後 graceful end | 穩定 | 可能再 retry 第 3 次 |
| 錯誤類型分流（transient vs permanent） | 較細緻 | 較粗略 |

## 想看更聰明的答案？

預設用 `claude-haiku-4-5`（最便宜）。改成 sonnet：

```bash
MODEL=claude-sonnet-5 python starter_anthropic.py
```

或 Ollama path 換更大 model：

```bash
MODEL=qwen2.5:7b python starter.py
```

## 延伸

- **加 retry quota**：在 loop 加 `error_count`、超過 N 次就放棄
- **加 circuit breaker**：連續失敗、暫時 stop call（避免 wave-after-wave 打死下游）
- **錯誤分類**：transient（429 / connection）vs permanent（401 / 400）、不同處理
- **Production 級**：看 [`../../stage-1/05-error-handling/`](../../stage-1/05-error-handling/) 的 API-level retry wrapper（exponential backoff + jitter）
