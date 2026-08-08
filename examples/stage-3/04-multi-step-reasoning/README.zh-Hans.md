<div align="right">
  <a href="./README.md">繁體中文</a> | <strong>简体中文</strong> | <a href="./README.en.md">English</a>
</div>

# 练习 4：多步骤推理任务

对应 [Stage 3 — Tool Use & Agent 入门](../../../stages/03-tool-use-and-hello-agent.zh-Hans.md) 练习 4。
> 🎓 **学习模式**：这份 `starter.py` 是**完整解答**、不是 TODO skeleton。建议用**主动模式**——`mv starter.py starter_reference.py`、看 signature 不看 body、自己重写一份 `starter.py`、跑 `python test.py` 验证；卡 20 分钟再回去对照 reference。完整方法论看 [`docs/HOW_TO_USE.md`](../../../docs/HOW_TO_USE.md)。

> 📚 **想要 chapter-length 深入版？** 本 folder 的 starter 是 70-150 行 illustrative 版、聚焦 `核心 pattern + 两条 SDK path`，不是进阶深度教材。深度教材推荐：
> - [`datawhalechina/hello-agents`](https://github.com/datawhalechina/hello-agents) ⭐ 中文圈最完整、章节式 + 16 种 production 能力。**本练习对应 hello-agents 的 planning / multi-step workflow 章节**
> - [Anthropic — Building Effective Agents](https://www.anthropic.com/engineering/building-effective-agents)（什么时候该拆步骤、什么时候不要）
> - 完整 references 见 [Stage 3 精选 Projects](../../../stages/03-tool-use-and-hello-agent.zh-Hans.md#-精选-projects)


## 为什么这题重要

把练习 3 的 ReAct loop 延伸成 **3-5 步任务**：查台北人口 → 查纽约人口 → 相除 → 转百分比。LLM 负责规划下一步、工具负责可靠地执行小动作；两者合起来才像能完成 workflow 的 agent。

这题也是观察“**model 规模 vs 多步推理稳定度**”的好实验。同样 loop、claude-haiku 通常 4 步走完；qwen2.5:3b 可能中间漏一步（譬如忘了转百分比），或停太早。

## 怎么跑 — 两条路径

### Path A（默认、本机免费）

```bash
pip install -r requirements.txt
ollama pull qwen2.5:3b
ollama serve
python starter.py
```

预算：**$0**。多步 loop ≈ 30-120 秒（CPU、4-5 轮累积）。

### Path B（Anthropic、想看 cloud 高质量）

```bash
pip install -r requirements.txt
export ANTHROPIC_API_KEY=sk-ant-...
python starter_anthropic.py
```

预算：每次 ≈ **$0.005**（claude-haiku-4-5、5 轮 messages 累积、每轮 prompt 渐长）。

预期看到（Path A、本机，理想 4 步走完）：

```
❓ 问题：Find Taipei population divided by New York population, then express it as a percentage.
------------------------------------------------------------
[step 0] tool: lookup_population({'city': 'Taipei'}) → 2602000
[step 1] tool: lookup_population({'city': 'New York'}) → 8336000
[step 2] tool: divide({'a': 2602000, 'b': 8336000}) → 0.3122...
[step 3] tool: to_percentage({'ratio': 0.3122}) → 31.22
------------------------------------------------------------
✅ 最终答案：Taipei is about 31.22% of New York's population.
   共 5 轮
✅ 练习 4 通过 — 你已用本机 qwen2.5:3b 跑通多步 ReAct loop、$0/run
```

## 不花钱验证程序逻辑（mock-based）

```bash
python test.py            # 验 Path A (Ollama) starter.py 逻辑
python test_anthropic.py  # 验 Path B (Anthropic) starter_anthropic.py 逻辑
```

两条 test 都用 `unittest.mock`、不打真 API、$0/run。

## 观念提醒

多步任务的核心不是“模型很会算”、而是把复杂任务拆成可靠的小步：

- **工具要窄而稳**：`divide(a, b)` 只做一件事、`b=0` 也不 crash 而是回 0
- **LLM 负责规划**：决定下一步要调用哪个工具、何时停
- **`max_iter=8` 是必要安全网**：避免模型一直要求工具而没收尾
- **每轮 messages 一直长**：assistant response + tool_result 都接回去、LLM 才看得到历史

## 两个 path 观察重点

| 观察项 | Anthropic Claude haiku | Ollama qwen2.5:3b |
|---|---|---|
| 走完 4 步机率 | 高 | 中（可能漏“转百分比”） |
| 中间步骤顺序 | 稳定 | 可能跳序 |
| 收尾判断 | 稳定 `end_turn` | 可能多跑一轮冗余 tool call |
| 单次成本 | $0.005 | $0 |

这恰好是 Stage 3 练习 4 的教学重点——**同样 ReAct loop、不同 model、在哪一步开始崩**。Production 选 model 时、多步稳定度是 cost 之外的关键考量。

## 想看更聪明的答案？

预设用 `claude-haiku-4-5`（最便宜）。改成 sonnet：

```bash
MODEL=claude-sonnet-5 python starter_anthropic.py
```

或 Ollama path 换更大 model：

```bash
MODEL=qwen2.5:7b python starter.py    # 4.7 GB、更稳
MODEL=mistral-nemo:12b python starter.py  # 7.1 GB、更接近 cloud
```

## 延伸

- **加更多 tool**：在 `TOOLS_SPEC` + `TOOL_IMPL` 补一个 entry 即可
- **加 retry / error handling**：看 [`../05-error-handling/`](../05-error-handling/) 怎么处理 tool 失败
- **schema 设计**：看 [`../06-schema-design/`](../06-schema-design/) 比较 bad / good schema
