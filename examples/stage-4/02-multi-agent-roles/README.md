<div align="right">
  <strong>繁體中文</strong> | <a href="./README.zh-Hans.md">简体中文</a> | <a href="./README.en.md">English</a>
</div>

# 練習 2：多 agent 角色分配（CrewAI）

對應 [Stage 4 — Agent Frameworks](../../../stages/04-agent-frameworks.md) 練習 2。
> 🎓 **學習模式**：這份 `starter.py` 是**完整解答**、不是 TODO skeleton。建議用**主動模式**——`mv starter.py starter_reference.py`、看 signature 不看 body、自己重寫一份 `starter.py`、跑 `python test.py` 驗證；卡 20 分鐘再回去對照 reference。完整方法論看 [`docs/HOW_TO_USE.md`](../../../docs/HOW_TO_USE.md)。

> 📚 **想要 chapter-length 深入版？** 本 folder 的 starter 是 illustrative 版、聚焦核心 pattern + 兩條 SDK path，不是進階深度教材。深度教材推薦：
> - [`datawhalechina/hello-agents`](https://github.com/datawhalechina/hello-agents) ⭐ 中文圈最完整、章節式 + 16 種 production 能力。**本練習對應 hello-agents 的 multi-agent roles / Crew 章節**
> - [CrewAI Examples repo](https://github.com/crewAIInc/crewAI-examples)（官方 sequential / hierarchical 範本；⚠️ 已封存 2026-04、仍可當參考）
> - 完整 references 見 [Stage 4 精選 Projects](../../../stages/04-agent-frameworks.md#-精選-projects)


## 任務

3 個 agent 各自負責一段、合作完成一篇 blog intro：

```
Researcher → Writer → Critic
  (找資料) (寫稿) (審稿、PASS/ISSUES)
```

這種「role-based pipeline」**CrewAI 最拿手**——你描述角色 / 目標 / 任務，框架自己 orchestrate。

## 怎麼跑 — 兩條路徑

### Path A（默認、本機免費）

```bash
pip install -r requirements.txt
ollama pull qwen2.5:3b
ollama serve
python starter.py
```

預算：**$0**。3 agent sequential ≈ 30-90 秒（CPU、qwen2.5:3b）。

### Path B（Anthropic、想看 cloud 高品質）

```bash
pip install -r requirements.txt
export ANTHROPIC_API_KEY=sk-ant-...
python starter_anthropic.py
```

預算：每次 ≈ **$0.005-0.01**（3 agent × 短輸出、claude-haiku-4-5）。

## 不花錢驗證程式邏輯

```bash
python test.py # tool 邏輯 + crew structure
python test_anthropic.py # starter_anthropic 載入
```

CrewAI 整個 `kickoff()` 太黑盒、純 mock 困難。這份 test 只驗結構（3 agent + 3 task + sequential process + context dependencies）跟 tool 邏輯。實測請跑 starter.py。

## CrewAI multi-agent 核心觀念

### Agent

```python
researcher = Agent(
    role="Researcher",
    goal="...", # 一句話講「成功」長什麼樣
    backstory="...", # 提供 persona context、影響 prompt
    tools=[search],
    llm=MODEL,
)
```

**重點**：`role` 跟 `goal` 影響 prompt 質量很大。不要寫「Agent」、要寫「Researcher who finds factual data」。

### Task

```python
research_task = Task(
    description="Search for X and report findings.",
    expected_output="A 1-2 sentence factual entry.",
    agent=researcher,
)
```

**重點**：`expected_output` 是給 LLM 看的「合格範本」、寫越具體越好（譬如「A 2-sentence intro paragraph」比「Some text」好 10 倍）。

### Context dependency

```python
write_task = Task(..., context=[research_task]) # writer 看 researcher 結果
critic_task = Task(..., context=[research_task, write_task]) # critic 同時看兩個
```

**重點**：`context` 是 CrewAI 的 dataflow 機制。`critic_task.context=[a, b]` 表示 critic 看到 a, b 兩個 task 的 output。

### Sequential vs Hierarchical Process

```python
Crew(..., process=Process.sequential) # 線性走完
Crew(..., process=Process.hierarchical) # 多個 manager+worker、需設 manager_llm
```

這題用 sequential（最簡單、最 deterministic）。Hierarchical 是 ManagementAgent 派任務給其他 agent、適合更複雜場景。

## 兩個 path 觀察重點

| 觀察項 | Anthropic Claude haiku | Ollama qwen2.5:3b |
|---|---|---|
| Researcher 直接呼叫 tool | 穩 | 偶爾跳過 tool、自己編答案 |
| Writer 引用 Researcher 結果 | 穩 | 可能憑印象寫、偏離 search result |
| Critic 抓 hallucination | 較敏銳 | 較鬆、可能 PASS 過頭 |
| 速度 | 10-30 秒 | 30-90 秒 |
| 成本 | $0.005-0.01 | $0 |

**教學 punchline**：multi-agent 對 model 質量比 single-agent 敏感——每個 agent 都可能漏一步、錯誤會累積到 critic 那邊。Production 多 agent 系統幾乎必用大 model（或細調過的小 model）。

## 常見坑

- **`expected_output` 太籠統**：寫「Some output」LLM 完全沒指引、隨便給。寫「A 2-sentence blog intro paragraph in active voice」效果差 10 倍
- **`context` 漏設**：Writer 沒設 `context=[research_task]`、就拿不到 researcher 結果、會憑空寫
- **小 model + 3 agent**：qwen2.5:3b 跑 3-agent crew 可能 1 分鐘+。換 `qwen2.5:7b` 或 Claude
- **`allow_delegation=True` 慎用**：開啟後 agent 可以叫其他 agent 幫忙、容易 loop。雛形階段建議 `False`

## 想看更聰明的答案？

```bash
MODEL=anthropic/claude-sonnet-5 python starter_anthropic.py # 高品質
MODEL=ollama/qwen2.5:7b python starter.py # 較大本機 model
```

## 延伸

- **加 manager**：`process=Process.hierarchical` + `manager_llm=...`、讓 manager agent 動態分配
- **加 memory**：CrewAI 有 `memory=True`、讓 agent 跨 task 記住 context
- **改成 streaming**：`crew.kickoff_for_each(...)` 或 `crew.kickoff_async(...)`
- **加 human-in-the-loop**：練習 3 用 LangGraph 做、CrewAI 對 HITL 較弱
