<div align="right">
  <a href="./README.md">繁體中文</a> | <strong>简体中文</strong> | <a href="./README.en.md">English</a>
</div>

# 练习 5：Tool 错误处理

对应 [Stage 3 — Tool Use & Agent 入门](../../../stages/03-tool-use-and-hello-agent.zh-Hans.md) 练习 5。
> 🎓 **学习模式**：这份 `starter.py` 是**完整解答**、不是 TODO skeleton。建议用**主动模式**——`mv starter.py starter_reference.py`、看 signature 不看 body、自己重写一份 `starter.py`、跑 `python test.py` 验证；卡 20 分钟再回去对照 reference。完整方法论看 [`docs/HOW_TO_USE.md`](../../../docs/HOW_TO_USE.md)。

> 📚 **想要 chapter-length 深入版？** 本 folder 的 starter 是 70-150 行 illustrative 版、聚焦 `核心 pattern + 两条 SDK path`，不是进阶深度教材。深度教材推荐：
> - [`datawhalechina/hello-agents`](https://github.com/datawhalechina/hello-agents) ⭐ 中文圈最完整、章节式 + 16 种 production 能力。**本练习对应 hello-agents 的 Extra Chapter 错误处理 / circuit breaker**
> - [规则 5 结构化错误回传](../../../resources/schema-design-cheatsheet.zh-Hans.md)（本 repo 既有的 cheatsheet）
> - 完整 references 见 [Stage 3 精选 Projects](../../../stages/03-tool-use-and-hello-agent.zh-Hans.md#-精选-projects)


## 为什么这题重要

真实 agent 很少只走成功路径：API 会 timeout、第三方服务暂时不可用、user 传坏参数。这题故意让 `fetch_weather(city)` 第一次回**结构化 error**（`{"error": "network timeout", "retry_hint": "try again in 1s"}`）、第二次才成功；观察 ReAct loop 怎么把 error observation 交回 LLM、让模型自己决定 retry / 改 query / 放弃。

核心观念：**tool error 是数据、不是 exception**。回传结构化 dict、不要 raise。

## 怎么跑 — 两条路径

### Path A（默认、本机免费）

```bash
pip install -r requirements.txt
ollama pull qwen2.5:3b
ollama serve
python starter.py
```

预算：**$0**。3 轮 loop ≈ 10-60 秒。

### Path B（Anthropic、想看 cloud 高质量）

```bash
pip install -r requirements.txt
export ANTHROPIC_API_KEY=sk-ant-...
python starter_anthropic.py
```

预算：每次 ≈ **$0.003**（claude-haiku-4-5、3 轮 messages 累积）。

预期看到（Path A、本机，理想 retry 走法）：

```
❓ 问题：Will it rain in Taipei today?（using Ollama qwen2.5:3b）
------------------------------------------------------------
[step 0] tool: fetch_weather({'city': 'Taipei'}) → {'error': 'network timeout', 'retry_hint': 'try again in 1s'}
[step 1] tool: fetch_weather({'city': 'Taipei'}) → {'city': 'Taipei', 'forecast': 'rain', 'temperature_c': 24}
------------------------------------------------------------
✅ 最终答案：It will rain in Taipei today (24°C).
✅ 练习 5 通过 — tool error 是 data 不是 exception、$0/run
```

## 不花钱验证程序逻辑（mock-based）

```bash
python test.py            # 验 Path A (Ollama) starter.py 逻辑
python test_anthropic.py  # 验 Path B (Anthropic) starter_anthropic.py 逻辑
```

两条 test 都用 `unittest.mock`、不打真 API、$0/run。

## 设计提醒

错误也应该是结构化数据，让 LLM 有 context 做决策：

| Bad | Good |
|---|---|
| `raise Exception("failed")` | `return {"error": "network timeout", "retry_hint": "try again in 1s"}` |
| `return "failed"` | `return {"error": "...", "category": "transient", "retry_hint": "..."}` |
| 无限 retry | `max_iter` safety + 业务层 retry quota |

只回传 `"failed"` 让模型不知道下一步；加入 `retry_hint`、错误类型与可恢复建议，模型才有足够 context 做决策。retry 次数也要有限制，否则 agent 会在坏掉的工具前面无限打转。

## 两个 path 观察重点

**附加观察**：小 model（qwen2.5:3b）对 `retry_hint` 的 follow-up 可能不如 Claude 精细——可能会直接放弃、或无视 hint 重复同一个错。**这恰好是教学点**：production 写好 retry pattern 后，不同 model 对结构化 error 的“阅读力”差距，是选 model 的考量之一（Stage 7 production tier 会再回来讨论）。

| 观察项 | Anthropic Claude haiku | Ollama qwen2.5:3b |
|---|---|---|
| 看到 retry_hint 就 retry | 高机率 | 中机率（可能直接放弃） |
| 连续失败后 graceful end | 稳定 | 可能再 retry 第 3 次 |
| 错误类型分流（transient vs permanent） | 较细致 | 较粗略 |

## 想看更聪明的答案？

预设用 `claude-haiku-4-5`（最便宜）。改成 sonnet：

```bash
MODEL=claude-sonnet-5 python starter_anthropic.py
```

或 Ollama path 换更大 model：

```bash
MODEL=qwen2.5:7b python starter.py
```

## 延伸

- **加 retry quota**：在 loop 加 `error_count`、超过 N 次就放弃
- **加 circuit breaker**：连续失败、暂时 stop call（避免 wave-after-wave 打死下游）
- **错误类型分类**：transient（429 / connection）vs permanent（401 / 400）、不同处理
- **Production 级**：看 [`../../stage-1/05-error-handling/`](../../stage-1/05-error-handling/) 的 API-level retry wrapper（exponential backoff + jitter）
