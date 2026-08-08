<div align="right">
  <strong>繁體中文</strong> | <a href="./README.zh-Hans.md">简体中文</a> | <a href="./README.en.md">English</a>
</div>

# 練習 4：CodeAct vs JSON tool（Smolagents）

對應 [Stage 4 — Agent Frameworks](../../../stages/04-agent-frameworks.md) 練習 4。
> 🎓 **學習模式**：這份 `starter.py` 是**完整解答**、不是 TODO skeleton。建議用**主動模式**——`mv starter.py starter_reference.py`、看 signature 不看 body、自己重寫一份 `starter.py`、跑 `python test.py` 驗證；卡 20 分鐘再回去對照 reference。完整方法論看 [`docs/HOW_TO_USE.md`](../../../docs/HOW_TO_USE.md)。

> 📚 **想要 chapter-length 深入版？** 本 folder 的 starter 是 illustrative 版、聚焦核心 pattern + 兩條 SDK path，不是進階深度教材。深度教材推薦：
> - [`datawhalechina/hello-agents`](https://github.com/datawhalechina/hello-agents) ⭐ 中文圈最完整、章節式 + 16 種 production 能力。**本練習對應 hello-agents 的 CodeAct vs JSON tool 章節**
> - [Smolagents 官方 cookbook](https://github.com/huggingface/smolagents/tree/main/examples) + [QuantaLogic/quantalogic](https://github.com/quantalogic/quantalogic)（另一個 CodeAct framework）
> - 完整 references 見 [Stage 4 精選 Projects](../../../stages/04-agent-frameworks.md#-精選-projects)


## 兩種 agent action 路線對照

| 路線 | 怎麼 act | 範例 framework |
|---|---|---|
| **JSON tool** | LLM 回 `{"name": "tool_x", "arguments": {...}}` | OpenAI function calling、LangGraph、CrewAI |
| **CodeAct** | LLM 寫 Python code、直接執行 | HuggingFace Smolagents |

**這題用 CodeAct 解同題（人口比例）、跟練習 1 / 3 的 JSON tool 路線對照**。

## 怎麼跑 — 兩條路徑

### Path A（默認、本機免費）

```bash
pip install -r requirements.txt
ollama pull qwen2.5:3b
ollama serve
python starter.py
```

預算：**$0**。CodeAct 對小 model 比較吃力——qwen2.5:3b 可能會產 syntax error、agent 自己迭代修。

### Path B（Anthropic、想看 cloud 高品質）

```bash
pip install -r requirements.txt
export ANTHROPIC_API_KEY=sk-ant-...
python starter_anthropic.py
```

預算：每次 ≈ **$0.005-0.02**（CodeAct 通常多步、claude-haiku-4-5）。Claude 寫 Python code 比 qwen2.5:3b 穩很多。

## 不花錢驗證程式邏輯

```bash
python test.py # tool function + agent 結構
python test_anthropic.py # Path B 可載入檢查
```

## CodeAct 是怎麼運作的

LLM 不回 JSON、而是**回 Python code block**：

```
（user）Find Taipei population, divide by NYC, give ratio.

（LLM 回應）
```python
pop_taipei = lookup_fact(query="Taipei population") # 2602000
pop_nyc = lookup_fact(query="New York population") # 8336000
ratio = calculator(expression=f"{pop_taipei}/{pop_nyc}") # 0.3122
print(ratio)
```

（Smolagents 執行這段 code、把 print 結果接回去給 LLM 繼續）
```

Framework 提供 sandboxed Python interpreter、agent 在裡面 import tool、寫 code、看 print 結果繼續。

## CodeAct vs JSON tool 對照

| 維度 | JSON tool | CodeAct |
|---|---|---|
| LLM 輸出形式 | 結構化 JSON | Python 程式碼 |
| 變數綁定 | LLM 要自己記得 / 重複呼叫 | 自然有 variable（`pop_taipei = ...`） |
| 多步運算 | 每步一次 LLM call | 一次寫好幾行 code |
| 一輪 token 數 | 較少 | 較多（code 較長） |
| 對小 model | 較友善（穩定的 JSON） | 較吃力（要產正確 Python） |
| Debug 友善 | tool call 看得清楚 | 看 code execution log |
| 安全考量 | tool args validated | Sandboxed Python（注意 eval/exec 限制） |
| 哪些題目擅長 | 單步、邊界明確 | 多步運算、需要中間 variable |

**HuggingFace 的觀點**：CodeAct 更貼近「人類怎麼解問題」——你也是用變數記中間結果、不是每步都重新查。

## 兩個 path 觀察重點

| 觀察項 | Anthropic Claude haiku | Ollama qwen2.5:3b |
|---|---|---|
| 產正確 Python syntax | 穩 | 偶爾 syntax error、會自己迭代修 |
| 變數命名 / 重用 | 自然 | 容易重複呼叫 tool 而非用 variable |
| 多步 ratio 算對 | 高機率 | 中機率 |
| 步數 | 1-2 步 | 3-5 步（迭代修錯） |
| 成本 | $0.005-0.02 | $0 |

**punchline**：CodeAct 是 **model 質量敏感** pattern——LLM 要會寫能在 production 跑的 Python。**小 model 在 JSON tool 路線比 CodeAct 路線優**（Stage 3 練習 6 也驗證過這點）。

## 常見坑

- **`@tool` 函式 docstring 是 prompt 的一部分**：Smolagents 把 docstring 當 tool description 給 LLM 看。**docstring 沒寫好、LLM 不知道何時用這 tool**
- **CodeAct sandbox**：Smolagents 預設禁 `import os`、`open` 等危險操作。要放行特定 module、設 `additional_authorized_imports=[...]`
- **`max_steps` 不夠**：CodeAct 跑多步、`max_steps=4` 可能不夠。但太大又會無限迴圈。經驗值 4-8
- **小 model 寫的 code 有 syntax error**：Smolagents 會把 error 接回去讓 LLM 修、但會浪費 token。Production 用大 model 比較划算

## 想看更聰明的答案？

```bash
MODEL=anthropic/claude-sonnet-5 python starter_anthropic.py # 最穩
MODEL=qwen2.5:7b python starter.py # 較大本機 model
```

## 延伸

- **加更多 tools**：`@tool` 裝飾函式即自動 wrap、Smolagents 自動拿 docstring 當 description
- **改 ToolCallingAgent**：Smolagents 也有非 CodeAct 的 `ToolCallingAgent`、用 JSON tool 路線。對照看
- **接 Hugging Face Hub**：`HfApiModel` 直接打 HF inference（不必本機 ollama）
- **看 [Anthropic Building Effective Agents](https://www.anthropic.com/engineering/building-effective-agents)**：Anthropic 的觀點是兩條路線都合理、看任務
