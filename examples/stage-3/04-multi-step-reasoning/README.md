<div align="right">
  <strong>繁體中文</strong> | <a href="./README.zh-Hans.md">简体中文</a> | <a href="./README.en.md">English</a>
</div>

# 練習 4：多步驟推理任務

對應 [Stage 3 — Tool Use & Agent 入門](../../../stages/03-tool-use-and-hello-agent.md) 練習 4。
> 🎓 **學習模式**：這份 `starter.py` 是**完整解答**、不是 TODO skeleton。建議用**主動模式**——`mv starter.py starter_reference.py`、看 signature 不看 body、自己重寫一份 `starter.py`、跑 `python test.py` 驗證；卡 20 分鐘再回去對照 reference。完整方法論看 [`docs/HOW_TO_USE.md`](../../../docs/HOW_TO_USE.md)。

> 📚 **想要 chapter-length 深入版？** 本 folder 的 starter 是 70-150 行 illustrative 版、聚焦 `核心 pattern + 兩條 SDK path`，不是進階深度教材。深度教材推薦：
> - [`datawhalechina/hello-agents`](https://github.com/datawhalechina/hello-agents) ⭐ 中文圈最完整、章節式 + 16 種 production 能力。**本練習對應 hello-agents 的 planning / multi-step workflow 章節**
> - [Anthropic — Building Effective Agents](https://www.anthropic.com/engineering/building-effective-agents)（什麼時候該拆步驟、什麼時候不要）
> - 完整 references 見 [Stage 3 精選 Projects](../../../stages/03-tool-use-and-hello-agent.md#-精選-projects)


## 為什麼這題重要

把練習 3 的 ReAct loop 延伸成 **3-5 步任務**：查台北人口 → 查紐約人口 → 相除 → 轉百分比。LLM 負責規劃下一步、工具負責可靠地執行小動作；兩者合起來才像能完成 workflow 的 agent。

這題也是觀察「**model 規模 vs 多步推理穩定度**」的好實驗。同樣 loop、claude-haiku 通常 4 步走完；qwen2.5:3b 可能中間漏一步（譬如忘了轉百分比），或停太早。

## 怎麼跑 — 兩條路徑

### Path A（默認、本機免費）

```bash
pip install -r requirements.txt
ollama pull qwen2.5:3b
ollama serve
python starter.py
```

預算：**$0**。多步 loop ≈ 30-120 秒（CPU、4-5 輪累積）。

### Path B（Anthropic、想看 cloud 高品質）

```bash
pip install -r requirements.txt
export ANTHROPIC_API_KEY=sk-ant-...
python starter_anthropic.py
```

預算：每次 ≈ **$0.005**（claude-haiku-4-5、5 輪 messages 累積、每輪 prompt 漸長）。

預期看到（Path A、本機，理想 4 步走完）：

```
❓ 問題：Find Taipei population divided by New York population, then express it as a percentage.
------------------------------------------------------------
[step 0] tool: lookup_population({'city': 'Taipei'}) → 2602000
[step 1] tool: lookup_population({'city': 'New York'}) → 8336000
[step 2] tool: divide({'a': 2602000, 'b': 8336000}) → 0.3122...
[step 3] tool: to_percentage({'ratio': 0.3122}) → 31.22
------------------------------------------------------------
✅ 最終答案：Taipei is about 31.22% of New York's population.
   共 5 輪
✅ 練習 4 通過 — 你已用本機 qwen2.5:3b 跑通多步 ReAct loop、$0/run
```

## 不花錢驗證程式邏輯（mock-based）

```bash
python test.py # 驗 Path A (Ollama) starter.py 邏輯
python test_anthropic.py # 驗 Path B (Anthropic) starter_anthropic.py 邏輯
```

兩條 test 都用 `unittest.mock`、不打真 API、$0/run。Path A 用 OpenAI-compat response shape、Path B 用 Anthropic content blocks。

## 觀念提醒

多步任務的核心不是「模型很會算」、而是把複雜任務拆成可靠的小步：

- **工具要窄而穩**：`divide(a, b)` 只做一件事、`b=0` 也不 crash 而是回 0
- **LLM 負責規劃**：決定下一步要呼叫哪個工具、何時停
- **`max_iter=8` 是必要安全網**：避免模型一直要求工具而沒收尾
- **每輪 messages 一直長**：assistant response + tool_result 都接回去、LLM 才看得到歷史

## 兩個 path 觀察重點

| 觀察項 | Anthropic Claude haiku | Ollama qwen2.5:3b |
|---|---|---|
| 走完 4 步機率 | 高 | 中（可能漏「轉百分比」） |
| 中間步驟順序 | 穩定 | 可能跳序 |
| 收尾判斷 | 穩定 `end_turn` | 可能多跑一輪冗餘 tool call |
| 單次成本 | $0.005 | $0 |

這恰好是 Stage 3 練習 4 的教學重點——**同樣 ReAct loop、不同 model、在哪一步開始崩**。Production 選 model 時、多步穩定度是 cost 之外的關鍵考量。

## 想看更聰明的答案？

預設用 `claude-haiku-4-5`（最便宜）。改成 sonnet：

```bash
MODEL=claude-sonnet-5 python starter_anthropic.py
```

或 Ollama path 換更大 model：

```bash
MODEL=qwen2.5:7b python starter.py # 4.7 GB、更穩
MODEL=mistral-nemo:12b python starter.py # 7.1 GB、更接近 cloud
```

## 延伸

- **加更多 tool**：在 `TOOLS_SPEC` + `TOOL_IMPL` 補一個 entry 即可
- **加 retry / error handling**：看 [`../05-error-handling/`](../05-error-handling/) 怎麼處理 tool 失敗
- **schema 設計**：看 [`../06-schema-design/`](../06-schema-design/) 比較 bad / good schema
