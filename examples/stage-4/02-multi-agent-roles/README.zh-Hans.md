<div align="right">
  <a href="./README.md">繁體中文</a> | <strong>简体中文</strong> | <a href="./README.en.md">English</a>
</div>

# 练习 2：多 agent 角色分配（CrewAI）

对应 [Stage 4 — Agent Frameworks](../../../stages/04-agent-frameworks.zh-Hans.md) 练习 2。
> 🎓 **学习模式**：这份 `starter.py` 是**完整解答**、不是 TODO skeleton。建议用**主动模式**——`mv starter.py starter_reference.py`、看 signature 不看 body、自己重写一份 `starter.py`、跑 `python test.py` 验证；卡 20 分钟再回去对照 reference。完整方法论看 [`docs/HOW_TO_USE.md`](../../../docs/HOW_TO_USE.md)。

> 📚 **想要 chapter-length 深入版？** 本 folder 的 starter 是 illustrative 版、聚焦核心 pattern + 两条 SDK path，不是进阶深度教材。深度教材推荐：
> - [`datawhalechina/hello-agents`](https://github.com/datawhalechina/hello-agents) ⭐ 中文圈最完整、章节式 + 16 种 production 能力。**本练习对应 hello-agents 的 multi-agent roles / Crew 章节**
> - [CrewAI Examples repo](https://github.com/crewAIInc/crewAI-examples)（官方 sequential / hierarchical 范本；⚠️ 已归档 2026-04、仍可当参考）
> - 完整 references 见 [Stage 4 精选 Projects](../../../stages/04-agent-frameworks.zh-Hans.md#-精选-projects)


## 任务

3 个 agent 各自负责一段、合作完成一篇 blog intro：

```
Researcher → Writer → Critic
  (找资料)    (写稿)    (审稿、PASS/ISSUES)
```

这种“role-based pipeline”**CrewAI 最拿手**——你描述角色 / 目标 / 任务，框架自己 orchestrate。

## 怎么跑 — 两条路径

### Path A（默认、本机免费）

```bash
pip install -r requirements.txt
ollama pull qwen2.5:3b
ollama serve
python starter.py
```

预算：**$0**。3 agent sequential ≈ 30-90 秒（CPU、qwen2.5:3b）。

### Path B（Anthropic、想看 cloud 高质量）

```bash
pip install -r requirements.txt
export ANTHROPIC_API_KEY=sk-ant-...
python starter_anthropic.py
```

预算：每次 ≈ **$0.005-0.01**（3 agent × 短输出、claude-haiku-4-5）。

## 不花钱验证程序逻辑

```bash
python test.py             # tool 逻辑 + crew structure
python test_anthropic.py   # starter_anthropic 载入
```

CrewAI 整个 `kickoff()` 太黑盒、纯 mock 困难。这份 test 只验结构（3 agent + 3 task + sequential process + context dependencies）跟 tool 逻辑。实测请跑 starter.py。

## CrewAI multi-agent 核心观念

### Agent

```python
researcher = Agent(
    role="Researcher",
    goal="...",          # 一句话讲「成功」长什么样
    backstory="...",     # 提供 persona context、影响 prompt
    tools=[search],
    llm=MODEL,
)
```

**重点**：`role` 跟 `goal` 影响 prompt 质量很大。不要写“Agent”、要写“Researcher who finds factual data”。

### Task

```python
research_task = Task(
    description="Search for X and report findings.",
    expected_output="A 1-2 sentence factual entry.",
    agent=researcher,
)
```

**重点**：`expected_output` 是给 LLM 看的“合格范本”、写越具体越好（譬如“A 2-sentence intro paragraph”比“Some text”好 10 倍）。

### Context dependency

```python
write_task = Task(..., context=[research_task])   # writer 看 researcher 结果
critic_task = Task(..., context=[research_task, write_task])  # critic 同时看两个
```

**重点**：`context` 是 CrewAI 的 dataflow 机制。`critic_task.context=[a, b]` 表示 critic 看到 a, b 两个 task 的 output。

### Sequential vs Hierarchical Process

```python
Crew(..., process=Process.sequential)    # 线性走完
Crew(..., process=Process.hierarchical)  # 多个 manager+worker、需设 manager_llm
```

这题用 sequential（最简单、最 deterministic）。Hierarchical 是 ManagementAgent 派任务给其他 agent、适合更复杂场景。

## 两个 path 观察重点

| 观察项 | Anthropic Claude haiku | Ollama qwen2.5:3b |
|---|---|---|
| Researcher 直接调用 tool | 稳 | 偶尔跳过 tool、自己编答案 |
| Writer 引用 Researcher 结果 | 稳 | 可能凭印象写、偏离 search result |
| Critic 抓 hallucination | 较敏锐 | 较松、可能 PASS 过头 |
| 速度 | 10-30 秒 | 30-90 秒 |
| 成本 | $0.005-0.01 | $0 |

**教学 punchline**：multi-agent 对 model 质量比 single-agent 敏感——每个 agent 都可能漏一步、错误会累积到 critic 那边。Production 多 agent 系统几乎必用大 model（或细调过的小 model）。

## 常见坑

- **`expected_output` 太笼统**：写“Some output”LLM 完全没指引、随便给。写“A 2-sentence blog intro paragraph in active voice”效果差 10 倍
- **`context` 漏设**：Writer 没设 `context=[research_task]`、就拿不到 researcher 结果、会凭空写
- **小 model + 3 agent**：qwen2.5:3b 跑 3-agent crew 可能 1 分钟+。换 `qwen2.5:7b` 或 Claude
- **`allow_delegation=True` 慎用**：开启后 agent 可以叫其他 agent 帮忙、容易 loop。雏形阶段建议 `False`

## 想看更聪明的答案？

```bash
MODEL=anthropic/claude-sonnet-5 python starter_anthropic.py  # 高品质
MODEL=ollama/qwen2.5:7b python starter.py                       # 较大本机 model
```

## 延伸

- **加 manager**：`process=Process.hierarchical` + `manager_llm=...`、让 manager agent 动态分配
- **加 memory**：CrewAI 有 `memory=True`、让 agent 跨 task 记住 context
- **改成 streaming**：`crew.kickoff_for_each(...)` 或 `crew.kickoff_async(...)`
- **加 human-in-the-loop**：练习 3 用 LangGraph 做、CrewAI 对 HITL 较弱
