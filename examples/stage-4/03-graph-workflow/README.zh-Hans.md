<div align="right">
  <a href="./README.md">繁體中文</a> | <strong>简体中文</strong> | <a href="./README.en.md">English</a>
</div>

# 练习 3：图式 workflow（LangGraph 条件分支 + HITL）

对应 [Stage 4 — Agent Frameworks](../../../stages/04-agent-frameworks.zh-Hans.md) 练习 3。
> 🎓 **学习模式**：这份 `starter.py` 是**完整解答**、不是 TODO skeleton。建议用**主动模式**——`mv starter.py starter_reference.py`、看 signature 不看 body、自己重写一份 `starter.py`、跑 `python test.py` 验证；卡 20 分钟再回去对照 reference。完整方法论看 [`docs/HOW_TO_USE.md`](../../../docs/HOW_TO_USE.md)。

> 📚 **想要 chapter-length 深入版？** 本 folder 的 starter 是 illustrative 版、聚焦核心 pattern + 两条 SDK path，不是进阶深度教材。深度教材推荐：
> - [`datawhalechina/hello-agents`](https://github.com/datawhalechina/hello-agents) ⭐ 中文圈最完整、章节式 + 16 种 production 能力。**本练习对应 hello-agents 的 graph workflow + HITL 章节**
> - [LangGraph HITL tutorial](https://langchain-ai.github.io/langgraph/tutorials/human-in-the-loop/) + [LangGraph time-travel docs](https://langchain-ai.github.io/langgraph/concepts/time-travel/)
> - 完整 references 见 [Stage 4 精选 Projects](../../../stages/04-agent-frameworks.zh-Hans.md#-精选-projects)


## 任务

`classify → [search?] → respond → [HITL] → final`

- **`classify_node`**：看 query 决定 `needs_search`
- **条件分支**：`needs_search=True` 走 `search` node、否则直接 `respond`
- **HITL checkpoint**：`respond_node` 后 interrupt、等人类在 state 改 `approved`
- **`final_node`**：`approved=True` → PUBLISHED、否则 REJECTED

这题 **LangGraph 最拿手**：graph state + checkpointing + interrupt_before 是 LangGraph 招牌组合。CrewAI 对 HITL 支援较弱。

## 怎么跑

```bash
pip install -r requirements.txt
python starter.py
```

预算：**$0**。这份 demo 的节点都是 deterministic 逻辑、不打 LLM；要实接 Claude / Ollama 在 `respond_node` 改成 `llm.invoke(...)` 即可。

```bash
python test.py             # 6 个 test，验 routing + HITL 逻辑
python test_anthropic.py   # Path B concept demo
```

## LangGraph 图结构（精简）

```python
g = StateGraph(State)
g.add_node("classify", classify_node)
g.add_node("search", search_node)
g.add_node("respond", respond_node)
g.add_node("final", final_node)

g.add_edge(START, "classify")
g.add_conditional_edges("classify", should_search, {"search": "search", "respond": "respond"})
g.add_edge("search", "respond")
g.add_edge("respond", "final")
g.add_edge("final", END)

graph = g.compile(checkpointer=InMemorySaver(), interrupt_before=["final"])
```

## HITL 怎么运作

```python
# 第一段：跑到 final 之前自动停（因为 interrupt_before=["final"]）
state_before = graph.invoke({"query": ...}, config={"configurable": {"thread_id": "demo"}})
# 此时可以印 state_before["draft"]、问人类「要 publish 吗？」

# 人类决定：把 approved 写进 state
graph.update_state(config, {"approved": True})

# 第二段：继续从 final 跑（None 表示「不给新 input、用 checkpoint」）
state_after = graph.invoke(None, config=config)
```

**关键**：`interrupt_before=["final"]` 告诉 graph“跑到 final 之前停”。Production 把它接到 webhook / Slack / 前端 button、等用户按 approve 才继续。

## 为什么这个 pattern 重要

| 情境 | 不用 HITL | 用 HITL |
|---|---|---|
| Agent 发 email | 直接送出（风险） | 显示草稿、人类按 approve |
| Agent 改 production 设定 | 直接套用 | dry-run 后等核准 |
| Agent 做退款 | 自动退 | 超过 $X 等审核 |

**Production agent 凡是有 side effect 的、都该加 HITL**。LangGraph `interrupt_before` 就是为这个设计。

## 两个 path 观察重点

本练习节点都是 deterministic 逻辑、不打 LLM、所以 Path A / Path B 跑出来一致。**重点是学图结构本身**。要实接 LLM：

```python
# 在 respond_node 改：
from langchain_openai import ChatOpenAI  # Path A
# from langchain_anthropic import ChatAnthropic  # Path B
llm = ChatOpenAI(base_url="http://localhost:11434/v1", api_key="ollama", model="qwen2.5:3b")
draft = llm.invoke(state["query"]).content
return {"draft": draft}
```

## 常见坑

- **`checkpointer` 没设**：`graph.compile(interrupt_before=[...])` 没带 checkpointer 会 raise。必须有 checkpointer 才能 pause/resume
- **`thread_id` 不一致**：第一段 invoke + update_state + 第二段 invoke 必须用同一个 `config={"configurable": {"thread_id": "..."}}`、否则 checkpoint 找不到
- **`interrupt_before` vs `interrupt_after`**：before = 进这个 node 前停、after = 跑完这个 node 停。**HITL 通常用 before**（让人类看完整 state 再决定）
- **conditional_edges 函数要回 string**：`should_search` return value 必须是 `add_conditional_edges` 第三个参数 dict 的 key、不能 return literal value 直接当 node name

## 想看更聪明的答案？

把 `respond_node` 接 LLM、用真的 model 写 draft（不再用 template）。Production setup 还会把 checkpointer 换成 SQLite / Redis（`SqliteSaver` / `RedisSaver`）做持久化。

## 延伸

- **加 retry**：在 `search_node` 失败时 retry、用 LangGraph 的 `error` edge
- **加多个 HITL**：`interrupt_before=["draft", "publish"]` 两个地方都暂停
- **time-travel debug**：`graph.get_state_history(config)` 拿到所有 checkpoint、可以回到任一步 fork 新 thread
- **加 streaming**：`for state in graph.stream(...)` 边跑边看 state
