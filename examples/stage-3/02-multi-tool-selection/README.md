<div align="right">
  <strong>繁體中文</strong> | <a href="./README.zh-Hans.md">简体中文</a> | <a href="./README.en.md">English</a>
</div>

# 練習 2：多工具選擇

對應 [Stage 3 — Tool Use & Agent 入門](../../../stages/03-tool-use-and-hello-agent.md) 練習 2。
> 🎓 **學習模式**：這份 `starter.py` 是**完整解答**、不是 TODO skeleton。建議用**主動模式**——`mv starter.py starter_reference.py`、看 signature 不看 body、自己重寫一份 `starter.py`、跑 `python test.py` 驗證；卡 20 分鐘再回去對照 reference。完整方法論看 [`docs/HOW_TO_USE.md`](../../../docs/HOW_TO_USE.md)。

> 📚 **想要 chapter-length 深入版？** 本 folder 的 starter 是 70-150 行 illustrative 版、聚焦 `核心 pattern + 兩條 SDK path`，不是進階深度教材。深度教材推薦：
> - [`datawhalechina/hello-agents`](https://github.com/datawhalechina/hello-agents) ⭐ 中文圈最完整、章節式 + 16 種 production 能力。**本練習對應 hello-agents 的 tool-calling / multi-tool dispatch 章節**
> - [Anthropic Tool Use Cookbook](https://github.com/anthropics/claude-cookbooks/tree/main/tool_use)（單工具→多工具→parallel 完整 notebook）
> - 完整 references 見 [Stage 3 精選 Projects](../../../stages/03-tool-use-and-hello-agent.md#-精選-projects)


## 為什麼這題重要

這個練習讓 LLM 在同一輪面對三個工具：`web_search`、`calculator`、`calendar_lookup`。重點不是工具本身強不強，而是觀察 schema 的 `name` / `description` / `parameters` 如何決定模型挑哪一個。寫清楚 schema、是 Stage 3 最值得花時間的子題。

## 怎麼跑 — 兩條路徑

### Path A（默認、本機免費）

```bash
pip install -r requirements.txt
ollama pull qwen2.5:3b
ollama serve
python starter.py
```

預算：**$0**。qwen2.5:3b 單輪 tool call ≈ 1-5 秒（CPU 慢、GPU 快）。

### Path B（Anthropic、想看 cloud 高品質）

```bash
pip install -r requirements.txt
export ANTHROPIC_API_KEY=sk-ant-...
python starter_anthropic.py
```

預算：每次 ≈ **$0.0005**（claude-haiku-4-5）。

預期看到（Path A、本機）：

```
❓ 問題：What is (19 * 42) - 8? Use the best available tool.（using Ollama qwen2.5:3b）
   tool: calculator
   tool_input: {'expression': '(19 * 42) - 8'}
   observation: 790
✅ 練習 2 通過 — 你已用本機 qwen2.5:3b 跑通 multi-tool selection、$0/run
```

## 不花錢驗證程式邏輯（mock-based）

```bash
python test.py # 驗 Path A (Ollama) starter.py 邏輯
python test_anthropic.py # 驗 Path B (Anthropic) starter_anthropic.py 邏輯
```

兩條 test 都用 `unittest.mock`、不打真 API、$0/run。Path A 用 OpenAI-compat response shape、Path B 用 Anthropic content blocks。

## 兩條 path 的 SDK 差異

三個關鍵差異（其他完全一樣）：

| 部分 | Anthropic（Path B） | OpenAI-compat / Ollama（Path A） |
|---|---|---|
| Schema 包法 | `tools=[{name, description, input_schema}, ...]` | `tools=[{"type": "function", "function": {name, description, parameters}}, ...]` |
| 抓 tool call | `resp.content[i].type == "tool_use"` | `resp.choices[0].message.tool_calls[i]` |
| input 格式 | `call.input` 是 dict（自動 parse） | `call.function.arguments` 是 JSON string、要 `json.loads(...)` |

Tool selection **邏輯本身**跨 backend——schema 寫好、qwen2.5:3b 也會挑對 tool。這題很適合拿來對照 Claude vs qwen2.5「在哪幾題會挑錯」，是觀察小 model 邊界的好實驗。

## 容易踩坑

多工具選擇最常見的錯誤是 description 寫得太像「一般說明文件」，而不是「給模型做決策的判斷規則」：

- `calendar_lookup` 描述只說「行事曆」就會跟 `web_search` 邊界模糊；明寫「查特定日期事件」才好
- `web_search` 適合「外部 / 近期 / 不確定資訊」、`calculator` 只處理算式；邊界寫越清楚、模型越少誤判
- 小 model（qwen2.5:3b）對 description 質量比 Claude **更敏感**——同一份 schema、Claude 可能還能猜對、qwen 直接挑錯

## 想看更聰明的答案？

預設用 `claude-haiku-4-5`（最便宜）。改成 sonnet：

```bash
MODEL=claude-sonnet-5 python starter_anthropic.py
```

或在 Ollama path 換 `qwen2.5:7b`（更大、更穩、但慢）：

```bash
MODEL=qwen2.5:7b python starter.py
```

## 延伸

- **加更多 tool**：在 `TOOLS_SPEC` + `TOOL_IMPL` 補一個 entry 即可
- **改成多輪 ReAct**：把單輪 call 包進 while loop，看 [`../03-react-from-scratch/`](../03-react-from-scratch/)
- **schema 細節**：看 [`../06-schema-design/`](../06-schema-design/) 比較 bad / good schema 對選擇正確率的影響
