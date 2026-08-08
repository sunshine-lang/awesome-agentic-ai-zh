<div align="right">
  <a href="./README.md">繁體中文</a> | <strong>简体中文</strong> | <a href="./README.en.md">English</a>
</div>

# 练习 1：同一个 agent、两个 framework（LangGraph + CrewAI）

对应 [Stage 4 — Agent Frameworks](../../../stages/04-agent-frameworks.zh-Hans.md) 练习 1。
> 🎓 **学习模式**：这份 `starter.py` 是**完整解答**、不是 TODO skeleton。建议用**主动模式**——`mv starter.py starter_reference.py`、看 signature 不看 body、自己重写一份 `starter.py`、跑 `python test.py` 验证；卡 20 分钟再回去对照 reference。完整方法论看 [`docs/HOW_TO_USE.md`](../../../docs/HOW_TO_USE.md)。

> 📚 **想要 chapter-length 深入版？** 本 folder 的 starter 是 illustrative 版、聚焦核心 pattern + 两条 SDK path，不是进阶深度教材。深度教材推荐：
> - [`datawhalechina/hello-agents`](https://github.com/datawhalechina/hello-agents) ⭐ 中文圈最完整、章节式 + 16 种 production 能力。**本练习对应 hello-agents 的 framework 对照 / orchestration 章节**
> - [LangGraph official tutorial](https://langchain-ai.github.io/langgraph/tutorials/) + [CrewAI 官方 docs](https://docs.crewai.com/)
> - 完整 references 见 [Stage 4 精选 Projects](../../../stages/04-agent-frameworks.zh-Hans.md#-精选-projects)


## 任务

最简单的 search + summarize agent：

- 给一个 query（譬如“summarize Taipei”）
- Agent 用 `search` tool 拿 knowledge base 数据
- LLM 把 search result 摘成 1-2 句

用 **LangGraph** 跟 **CrewAI** 各做一次、比较风格差异。

## 怎么跑 — 两条路径 + 两个 framework

### Path A（默认、本机免费）

```bash
pip install -r requirements.txt
ollama pull qwen2.5:3b
ollama serve

python starter.py         # LangGraph + Ollama
python starter_crewai.py  # CrewAI + Ollama（对照）
```

预算：**$0**。

### Path B（Anthropic、想看 cloud 高质量）

```bash
pip install -r requirements.txt
export ANTHROPIC_API_KEY=sk-ant-...
python starter_anthropic.py   # LangGraph + Claude
```

预算：每次 ≈ **$0.001**（claude-haiku-4-5）。

## 不花钱验证程序逻辑（mock-based）

```bash
python test.py             # LangGraph + mock LLM
python test_anthropic.py   # starter_anthropic 可载入 + ChatAnthropic 可构造
python test_crewai.py      # CrewAI tool 逻辑 + 模块可载入
```

## 两个 framework 的并排比较

| 维度 | LangGraph | CrewAI |
|---|---|---|
| 核心抽象 | `StateGraph` + node + edge | `Agent` + `Task` + `Crew` |
| 思考方式 | “状态怎么流动” | “角色怎么分工” |
| Loop 控制 | 显式 conditional edge | 隐藏在 `Crew.kickoff()` 里 |
| 程序码行数（这题） | ~50 行 | ~25 行 |
| Debug 路径 | 看 graph state、可 time-travel | 看 verbose log、不容易 step |
| 适合场景 | 复杂分支、production、需要 audit | 多 agent 雏形、role-based 任务 |
| 学习曲线 | 中-高 | 低 |

### LangGraph 风格（精简）

```python
g = StateGraph(State)
g.add_node("agent", agent_node)
g.add_node("tools", tool_node)
g.add_conditional_edges("agent", should_continue, {"tools": "tools", END: END})
g.add_edge("tools", "agent")
```

“我要显式地告诉系统：状态长这样、节点互相连这样、条件分支看 `should_continue`。”

### CrewAI 风格（精简）

```python
researcher = Agent(role="Researcher", goal="...", tools=[search], llm=MODEL)
task = Task(description=query, expected_output="...", agent=researcher)
crew = Crew(agents=[researcher], tasks=[task])
crew.kickoff()
```

“我要描述：这个角色是谁、要完成什么任务、有什么工具。框架自己决定怎么跑。”

## 观察重点

1. **抽象代价**：CrewAI 隐藏的多、写得少；要 debug 时 stack 比较深
2. **小 model 友善度**：LangGraph 对 qwen2.5:3b 较稳；CrewAI 可能让小 model 多绕几步（因为 prompt 比较复杂）
3. **可控性**：LangGraph 你能看到每个 state 变化；CrewAI 偏向“结果导向”
4. **何时选哪个**：production 级 / 需要 audit → LangGraph。多 agent 雏形 / role-based → CrewAI

## 常见坑

- **LangGraph `bind_tools`**：要 `llm.bind_tools([search])` 才会把 tool schema 给 LLM。没 bind 模型就不知道 tool 存在
- **CrewAI LLM 设定**：要靠 LiteLLM 格式（譬如 `"ollama/qwen2.5:3b"`、不是 `"qwen2.5:3b"`）。错一个字 framework 不会 raise、会直接连到 OpenAI 预设
- **CrewAI 结果类型**：`crew.kickoff()` 回 `CrewOutput` 对象、`str(result)` 拿文字。直接 `print(result)` 有可能拿到 repr

## 想看更聪明的答案？

```bash
MODEL=claude-sonnet-5 python starter_anthropic.py    # 更稳
MODEL=qwen2.5:7b python starter.py                      # 大本机 model
```

## 延伸

- **改成 streaming**：LangGraph `graph.stream(...)` 边跑边看 state、CrewAI `crew.kickoff(stream=True)`
- **加 checkpointing**：LangGraph 加 `MemorySaver` 就能 time-travel debug
- **加 human-in-the-loop**：练习 3 会做
