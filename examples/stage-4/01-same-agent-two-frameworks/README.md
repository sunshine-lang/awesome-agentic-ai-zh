<div align="right">
  <strong>繁體中文</strong> | <a href="./README.zh-Hans.md">简体中文</a> | <a href="./README.en.md">English</a>
</div>

# 練習 1：同一個 agent、兩個 framework（LangGraph + CrewAI）

對應 [Stage 4 — Agent Frameworks](../../../stages/04-agent-frameworks.md) 練習 1。
> 🎓 **學習模式**：這份 `starter.py` 是**完整解答**、不是 TODO skeleton。建議用**主動模式**——`mv starter.py starter_reference.py`、看 signature 不看 body、自己重寫一份 `starter.py`、跑 `python test.py` 驗證；卡 20 分鐘再回去對照 reference。完整方法論看 [`docs/HOW_TO_USE.md`](../../../docs/HOW_TO_USE.md)。

> 📚 **想要 chapter-length 深入版？** 本 folder 的 starter 是 illustrative 版、聚焦核心 pattern + 兩條 SDK path，不是進階深度教材。深度教材推薦：
> - [`datawhalechina/hello-agents`](https://github.com/datawhalechina/hello-agents) ⭐ 中文圈最完整、章節式 + 16 種 production 能力。**本練習對應 hello-agents 的 framework 對照 / orchestration 章節**
> - [LangGraph official tutorial](https://langchain-ai.github.io/langgraph/tutorials/) + [CrewAI 官方 docs](https://docs.crewai.com/)
> - 完整 references 見 [Stage 4 精選 Projects](../../../stages/04-agent-frameworks.md#-精選-projects)


## 任務

最簡單的 search + summarize agent：

- 給一個 query（譬如「summarize Taipei」）
- Agent 用 `search` tool 拿 knowledge base 資料
- LLM 把 search result 摘成 1-2 句

用 **LangGraph** 跟 **CrewAI** 各做一次、比較風格差異。

## 怎麼跑 — 兩條路徑 + 兩個 framework

### Path A（默認、本機免費）

```bash
pip install -r requirements.txt
ollama pull qwen2.5:3b
ollama serve

python starter.py # LangGraph + Ollama
python starter_crewai.py # CrewAI + Ollama（對照）
```

預算：**$0**。

### Path B（Anthropic、想看 cloud 高品質）

```bash
pip install -r requirements.txt
export ANTHROPIC_API_KEY=sk-ant-...
python starter_anthropic.py # LangGraph + Claude
```

預算：每次 ≈ **$0.001**（claude-haiku-4-5）。

## 不花錢驗證程式邏輯（mock-based）

```bash
python test.py # LangGraph + mock LLM
python test_anthropic.py # starter_anthropic 可載入 + ChatAnthropic 可建構
python test_crewai.py # CrewAI tool 邏輯 + 模組可載入
```

## 兩個 framework 的並排比較

| 維度 | LangGraph | CrewAI |
|---|---|---|
| 核心抽象 | `StateGraph` + node + edge | `Agent` + `Task` + `Crew` |
| 思考方式 | 「狀態怎麼流動」 | 「角色怎麼分工」 |
| Loop 控制 | 顯式 conditional edge | 隱藏在 `Crew.kickoff()` 裡 |
| 程式碼行數（這題） | ~50 行 | ~25 行 |
| Debug 路徑 | 看 graph state、可 time-travel | 看 verbose log、不容易 step |
| 適合場景 | 複雜分支、production、需要 audit | 多 agent 雛形、role-based 任務 |
| 學習曲線 | 中-高 | 低 |

### LangGraph 風格（精簡）

```python
g = StateGraph(State)
g.add_node("agent", agent_node)
g.add_node("tools", tool_node)
g.add_conditional_edges("agent", should_continue, {"tools": "tools", END: END})
g.add_edge("tools", "agent")
```

「我要顯式地告訴系統：狀態長這樣、節點互相連這樣、條件分支看 `should_continue`。」

### CrewAI 風格（精簡）

```python
researcher = Agent(role="Researcher", goal="...", tools=[search], llm=MODEL)
task = Task(description=query, expected_output="...", agent=researcher)
crew = Crew(agents=[researcher], tasks=[task])
crew.kickoff()
```

「我要描述：這個角色是誰、要完成什麼任務、有什麼工具。框架自己決定怎麼跑。」

## 觀察重點

1. **抽象代價**：CrewAI 隱藏的多、寫得少；要 debug 時 stack 比較深
2. **小 model 友善度**：LangGraph 對 qwen2.5:3b 較穩；CrewAI 可能讓小 model 多繞幾步（因為 prompt 比較複雜）
3. **可控性**：LangGraph 你能看到每個 state 變化；CrewAI 偏向「結果導向」
4. **何時選哪個**：production 級 / 需要 audit → LangGraph。多 agent 雛形 / role-based → CrewAI

## 常見坑

- **LangGraph `bind_tools`**：要 `llm.bind_tools([search])` 才會把 tool schema 給 LLM。沒 bind 模型就不知道 tool 存在
- **CrewAI LLM 設定**：要靠 LiteLLM 格式（譬如 `"ollama/qwen2.5:3b"`、不是 `"qwen2.5:3b"`）。錯一個字 framework 不會 raise、會直接連到 OpenAI 預設
- **CrewAI 結果型別**：`crew.kickoff()` 回 `CrewOutput` 物件、`str(result)` 拿文字。直接 `print(result)` 有可能拿到 repr

## 想看更聰明的答案？

```bash
MODEL=claude-sonnet-5 python starter_anthropic.py # 更穩
MODEL=qwen2.5:7b python starter.py # 大本機 model
```

## 延伸

- **改成 streaming**：LangGraph `graph.stream(...)` 邊跑邊看 state、CrewAI `crew.kickoff(stream=True)`
- **加 checkpointing**：LangGraph 加 `MemorySaver` 就能 time-travel debug
- **加 human-in-the-loop**：練習 3 會做
