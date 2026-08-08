# Stage 7 — 多 Agent 系统与稳定运作（Multi-Agent & Production）

> [繁體中文](./07-multi-agent-production.md) | **简体中文** | [English](./07-multi-agent-production.en.md)

⏱ **时间估算**：2-4 周（约 15-30 小时）

> 💡 用语密度高（multi-agent / handoff / eval / observability / guardrails⋯）→ 翻 [`resources/glossary.zh-Hans.md` 4 + 6](../resources/glossary.zh-Hans.md#4-multi-agent)。

> 📋 **本章组成**：〔Multi-Agent · Production 化 是什么（先定位）+ 三层工程分工 + 何时用 multi-agent〕→ 学习目标 → 进入条件 → 必修阅读 → Harness Engineering（**8 个核心元件含 Cost/Latency**）→ 动手练习（含练习 6 Cost Optimization）→ **Agent Benchmark Landscape：怎么看，不要只看排行榜** → 常用工具推荐 → 精选 Projects → 自我检查
> 🔑 **关键名词**：见 [`resources/glossary.zh-Hans.md` 4 + 6](../resources/glossary.zh-Hans.md#4-multi-agent)（multi-agent / orchestration / handoff / eval / observability / harness（模型外围的执行与控制层））

最后一个阶段。你正从“我会做 agent”走向“我能让 agent **真的给人稳定用**——多个 agent 协作、有 eval、有 observability、能部署到可用环境”。**“Production 化” ≠ enterprise scale**——只要 agent 能稳定产出 + 能让别人使用，就算进入这 stage 范围。

## 🎯 Multi-Agent · Production 化 是什么（先定位）

**本 stage = 多 agent 怎么协作 + 把 agent 从 prototype 推到能稳定给人用的程度**。三句话厘清范围：

- **不是只学 framework**——Stage 4 已教 framework 怎么挑
- **不一定要 enterprise scale**——只要 agent 能让别人用，就算 Production 化
- **核心是 harness engineering**——8 个核心元件 + eval + observability + cost / latency 控制

**跟前后 stage 的分工**：

- **Stage 4** = 单 agent framework 怎么挑、ReAct / Plan-Execute 等 pattern
- **本 stage** = **多 agent 协作** + **harness engineering**（执行系统工程）+ **部署到可用环境 / observability / eval**

### 三层工程分工：Prompt → Context → Harness

工程分工可以分成三层，对应 stack 的不同位置（不是 call 一次 vs 多次的差别）：

| 层级 | 概念 | 核心问题 | 关注单位 | 对应 stage |
|---|---|---|---|---|
| 1 | **Prompt Engineering** | 这一次要怎么问？ | **单次 LLM call** | [Stage 2](02-prompt-engineering.zh-Hans.md) |
| 2 | **Context Engineering** | 这次该给模型哪些信息？ | **多次互动中的上下文** | [Stage 6](06-memory-rag.zh-Hans.md) |
| **3** | **Harness Engineering**<br>（**本 stage**） | 整个流程怎么跑起来？ | **可执行的 LLM workflow / system** | **本 stage** |

> 🔁 **下一层：Loop Engineering（循环工程）**：prompt → context → harness 之后，2026 浮现的第四层是“**设计 agent 的迭代循环本身**”——目标、可用工具、context 管理、**终止条件**、错误处理，让 agent 跑数百步、跨 session 仍可靠。Claude Code 的 `/goal`（给一个可验证的完成条件、agent 自己 loop 到达成）就是这个方向；[Stage 5.6 Dynamic Workflows](05-claude-code-ecosystem.zh-Hans.md) 则是 agent 自己写出 loop 脚本。谱系：ReAct（2022）→ AutoGPT（2023）→ /goal（2026）。

**白话差异**：

- **Prompt** = 设计一个好的问法，让模型这次回答准
- **Context** = 动态决定要放入哪些背景、记忆、文件、工具结果，让模型知道当前情境
- **Harness** = 把 prompt、context、tools、state、流程控制、错误处理串成一套真的能跑的系统

**本 stage 三个核心问题**：

1. **Multi-agent 协作** — debate / planner-executor / peer review / handoff / supervisor-worker pattern
2. **Harness Engineering** — agent loop / tool registry（agent 可调用工具的清单 + 接口定义）/ context manager / safety / retry / telemetry / eval / cost（8 个核心元件、下面详述）
3. **Production 化** — eval harness / observability / cost & latency 优化 / 部署到可用环境

**跟 Stage 5 的分工**（避免混淆）：

| 跟谁比 | 那边讲什么 | 本 stage 讲什么 |
|---|---|---|
| **Stage 5.5 Subagents** | Claude Code 原生 subagent 机制（markdown-based、不写程序）| 通用 multi-agent framework（autogen / crewAI / langgraph、跨 vendor）|
| **Stage 5.7 Claude Code source** | Claude Code source 解剖（reference implementation case study）| Harness engineering 通则（不绑特定 vendor）|

### ⚠ 但你真的需要 multi-agent 吗？

**Multi-agent 不是 default，而是任务真的需要时才上的设计**。多数场景应先尝试 simple workflow 或 single agent；**只有在任务天然可分解、需要平行探索、单一 context 不够、或需要明确角色分工时，multi-agent 才值得引入**。硬上会付 **3-10× token、debug 困难、context fragmentation（context 被切散在多个 agent、彼此看不到全貌）严重**。

> 📌 **决策框架的 canonical 在 Stage 4**：完整的 Anthropic / Cognition 立场对照 + 4 个"该上 multi-agent"信号 + 每个信号对应的 pattern，见 [Stage 4 §什么时候真的需要 multi-agent](04-agent-frameworks.zh-Hans.md#什么时候真的需要-multi-agent不要硬上)（设计阶段决策）。本节只做 production 前的最后回头检查——**4 个信号一个都不在？** → single agent + 好 prompt + tool use 就够，别硬上 multi-agent。**本 stage 的 harness engineering 部分（8 个元件 / eval / observability）即使你最后用 single agent 也都会用到**——所以即使你决定不走 multi-agent，本 stage 仍是必修。

## 📌 学习目标

- 设计 multi-agent orchestration 模式（debate、planner-executor、peer review）
- 为 agent 架一套 evaluation harness
- 加上 observability（tracing、logging、cost tracking）
- 用 Anthropic SDK / OpenAI SDK 做 production deploy（进阶功能：streaming、prompt caching、batching）
- 把 agent deploy 到 production（Docker、serverless、monitoring）

## 🚪 进入条件

你应该已经：

- 完成 Stage 4（用过至少一个 agent framework 跑 multi-agent demo）
- 完成 Stage 5（懂 MCP / Skills / Plugins / Subagents 各自角色，并用 5.7 解剖过 harness 内部）
- 完成 Stage 6（会基本 RAG，能讲出 memory pattern 差异）
- 对 Docker / git / CI 基础熟悉（production deploy 会用到）

没到的话 → 补完前面几个 stage。本 stage 是“组合所有前面学到的东西 → 跑 production”，缺一块都会卡。

## 📚 必修阅读

1. [**Anthropic — Building Effective Agents**](https://www.anthropic.com/engineering/building-effective-agents) — 用 production 的角度再读一次
2. [**Anthropic — Prompt Caching**](https://www.anthropic.com/news/prompt-caching) — 90% 成本下降的技巧
3. [**Anthropic — Message Batches API**](https://docs.anthropic.com/en/docs/build-with-claude/batch-processing) — 异步 batch job
4. [**anthropics/courses — Prompt Evaluations**](https://github.com/anthropics/courses) ⭐⭐⭐⭐⭐ ★ 22k+ — Anthropic 官方 5 course umbrella、**module 4“Prompt Evaluations”对应本 stage eval / observability 部分**。Jupyter notebook、教怎么系统化评估 prompt 跟 agent 行为。
5. **任一 eval framework 的文件** — promptfoo 或 LangSmith 或 weave
6. [**ai-boost/awesome-harness-engineering**](https://github.com/ai-boost/awesome-harness-engineering)（★ 3.4k+）— agent harness 的工具 / pattern / eval / memory / MCP / observability 全集合
7. [**ZhangHanDong/harness-engineering-from-cc-to-ai-coding**](https://github.com/ZhangHanDong/harness-engineering-from-cc-to-ai-coding)（★ 1.5k+）— 从 Claude Code 源码学 harness 设计（中文）

## 🏗 Harness Engineering — production agent runtime 的工程设计 ⭐ 本 stage 核心概念

### 定位：模型外围的执行与控制层

要把 LLM 变成可用的 agent，通常会碰到三层工程问题。这三层对应的是不同工程位置，不是单纯用“一次 call”或“多次 call”来区分。

> 💡 **Simon Willison 2025**：“coding agent = LLM + harness”；harness = 所有**不是 model 本身**的代码。
>
> 💡 **OpenAI 2026 也使用 "Harness Engineering" 这个说法**（见 [OpenAI Harness Engineering article](https://openai.com/index/harness-engineering)、2026-02 发布）。

| 层级 | 工程的对象 | 在哪学 |
|---|---|---|
| **1. Prompt Engineering** | 送进 LLM 的**字符串**（system prompt / few-shot / 格式） | [Stage 2](02-prompt-engineering.zh-Hans.md) |
| **2. Context Engineering** | 窗口里装的**信息**（RAG / memory / tool defs / history 组装） | [Stage 6](06-memory-rag.zh-Hans.md) |
| **3. Harness Engineering**<br>（**本节**） | 模型**外围的执行与控制层**（loop / retry / sandbox / observability / 部署） | 本 stage |

**怎么分辨自己在做哪一层？问**：

1. 我改的是**字符串本身**吗？→ Prompt engineering
2. 我改的是**塞进窗口的信息**吗？→ Context engineering
3. 我改的是**调用模型的外围程序**吗？→ Harness engineering

→ 三层**正交**：1 次 call 的 RAG app 也在做 context engineering（重点是怎么组窗口）；50 次 call 但没做 retrieval 的 chatbot，仍然只是在做 prompt engineering。

### Harness 的 8 个核心元件

**Harness Engineering（Agent 执行系统设计）= 把 LLM、tools、memory、state、workflow control、错误处理、eval、observability 与 deployment 串成一套可执行、可观测、可维护的 agent 系统。**

→ 所有**不属于 model weights、也不只是 prompt string 本身**的工程元件都算 harness 范围。一个可部署的 agent runtime 包含这 8 个核心元件（前 6 个是 runtime 内建、第 7 个 eval 是外挂工具、第 8 个 cost / latency 是跨层议题）：

| 元件 | 做什么 | 对应本 stage 练习 |
|---|---|---|
| **Agent loop** | “LLM → tool → result → LLM”循环、稳定处理多轮 | 练习 1 multi-agent 辩论 |
| **Tool registry** | 动态 tool dispatch、permission gate、sandboxing | （在每个 framework / SDK 都有）|
| **Context manager** | message history 管理、context window 控制、auto-compact | Stage 6 + 本 stage 练习 4 SDK |
| **Safety layer** | permission prompts、sandboxed exec、destructive op 拦截 | （Claude Code 内建、SDK 可自定义）|
| **Retry / recovery** | tool fail 怎么处理（exception vs LLM 自己看 error 反思） | 练习 4 SDK 进阶 |
| **Telemetry / Observability** | metrics、logging、token counting、trace export | **练习 3 Observability** |
| **Eval harness** | regression test、quality gate、A/B test | **练习 2 Eval** |
| **Cost / Latency optimization** ⭐ 2024-2026 必修 | prompt caching、model routing、thinking budget、batching、semantic cache | **练习 6 Cost optimization**（新加）|

**Framework vs Harness 关键差别**：

- **Framework**（[Stage 4](04-agent-frameworks.zh-Hans.md)）规范 **API** — 你调用的接口长什么样
- **Harness**（本节）规范 **runtime** — 怎么跑、怎么 recovery、怎么观测

### 反馈循环：agent 进步靠的是反馈，不是更完美的提示

上面 8 个元件是 harness 的“骨架”。但让骨架真正运作的，是一件更基础的事：**agent 变强，靠的是“把反馈送回循环”，不是把开头那段提示写得更完美。**

打个比方：一个学生不会因为作业题目写得更漂亮就变强，他变强是因为在对的时机收到反馈——交草稿、写到一半被老师提醒、完成后被批改、下次重做。agent 也一样，而反馈可以在四个时机进来：

| 时机 | 白话 | 工程上长什么样 |
|---|---|---|
| **1. 工具返回值** | 工具吐回来的那段话，本身就是写给 agent 看的反馈 | 把错误信息、提示、下一步建议“写清楚”，别只丢一个 stack trace |
| **2. 执行中插话** | 在 agent 两次思考之间塞一句话调整方向 | 中途注入消息（steering），不用等它整轮跑完才修正 |
| **3. 单轮结束的验收** | 一轮做完，由“另一个人”对着目标检查 | 用独立的验收者（evaluator）比对目标，而不是让 agent 自己打分 |
| **4. 外层 loop** | 对着同一个目标反复叫 agent，直到完成 | 目标导向的重跑（像 OpenAI Codex 的 `/goal`、或 cron 定时重跑）|

**为什么第 3 个（独立验收）特别重要**：Anthropic 自己的实验发现，叫 agent 检查自己的成品，它几乎都会“自我称赞”——就算质量明显普通。所以他们把“做东西的 agent”和“验收的 agent”拆开：一个负责做，一个用工具（像 Playwright）实际去点、去测，再把 bug 回报回去。把外部验收者“调得更挑剔”，比让同一个 agent“对自己更严格”容易得多。

> 📚 实际案例：Anthropic [Harness design for long-running apps](https://www.anthropic.com/engineering/harness-design-long-running-apps)（2026-03）用 planner → generator → evaluator 三段，让 agent 连续跑好几小时做出一个完整的音乐制作 app，每轮都靠 evaluator 反馈修正。

### 参考实现

想看实际在 production 跑的 harness 长什么样？两个 reference：

- **Claude Code 整个 runtime** — 是 reference harness 实现。**读 source 练习见 [Stage 5.7](05-claude-code-ecosystem.zh-Hans.md#57--claude-code-source-解剖reference-harness-implementation-track-b-必看)**（clone `claude-agent-sdk-python` 解剖 main loop + 上表前 6 个 runtime 元件位置；第 7 个 Eval harness 是外挂、第 8 个 Cost / Latency 是 cross-cutting、见下方深入段）
- **`anthropics/claude-agent-sdk-python`** source — 上面练习用的具体 repo

→ 本 stage 剩下的 6 个练习（multi-agent / eval / observability / SDK / deploy / cost）每个都是 harness 的一个面向。学完整 stage = 拼出完整的 harness engineering mental model。

### 第 8 个核心元件深入 — Cost / Latency Optimization（2024-2026 Production 化必修）

Production agent 跑久了，**cost / latency 两条线会吃掉你大半预算与用户体验**。2024-2026 前沿模型都把这当 first-class API feature——**会用 = 省 50-90% cost / latency**。

| 技巧 | 怎么省 | 2026 状态 |
|---|---|---|
| **Prompt caching** | 重复 prefix（system prompt、long context）一次计费、后续 cache hit 折扣 ~90% | Anthropic / OpenAI / Gemini 全支持、自动或手动标记 |
| **Model routing / cascade** | 简单 query → 小 model、难 query → frontier model | [RouteLLM](https://github.com/lm-sys/RouteLLM) / [OpenRouter](https://openrouter.ai/) production 内建 |
| **Thinking budget** | reasoning model 可控 thinking token 上限、trade latency / quality | Claude / Gemini API 参数、o-series 默认高 |
| **Speculative decoding** | 小 model 预测 N token、大 model 一次验证、单 model 速度 ×2-3 | vLLM / TGI 内建、推理层自动 |
| **Batching** | 多 query 并行处理、GPU 利用率高 | vLLM、production inference layer |
| **Semantic caching** | 相似 query 共享回答（不只 exact match）| [GPTCache](https://github.com/zilliztech/GPTCache) / Helicone 内建 |

**Track A 怎么用**（用 CLI agent 的人）：

- 在 Claude Code / Cursor 设置 prompt caching，daily session 省 50-90% cost
- 用 [RouteLLM](https://github.com/lm-sys/RouteLLM) / [OpenRouter](https://openrouter.ai/) 动态切换 model（简单问题用 Haiku / Flash，困难问题用 Opus / Pro）
- Claude API 用 `thinking_budget` 参数控 reasoning model 的 token 上限

**Track B 怎么 build**（自己写 agent 的人）：

- 自架 cascade router，把 query embedding → classifier → model 对应起来
- 在 agent loop 内监控 token cost，超 budget 自动降级
- 在部署到可用环境时整合 semantic cache 层
- [Helicone](https://github.com/Helicone/helicone) / [langfuse](https://github.com/langfuse/langfuse) 等 observability 平台都已内建这些能力，不用自己写

## 🛠 动手练习（基础 illustrative 练习）

### 练习 1：Multi-Agent 辩论
两个 agent 辩论一个题目（例如“该用 Python 还是 Rust 写 backend”），第三个 agent 当裁判。观察辩论收敛或分歧的 pattern。

### 练习 2：Eval
替你前面的 agent 写一份 eval，跑 N 次量成功率。把“我用眼睛看一下”的习惯换掉。

### 练习 3：Observability
把 LangSmith、Helicone、或 weave 接上一个 agent，看完整 trace。理解“没 observability 的 agent debug = 黑盒”。

### 练习 4：SDK 进阶
在同一次调用里用 streaming + prompt caching + tool use。看成本怎么降下来。

### 练习 5：Deploy
把一个 agent 包进 Docker，deploy 到云端（任何 provider 都行）。学会把 prototype 变成可以给别人跑的东西。

### 练习 6：Cost Optimization（新加）⭐
量你前面任一个练习 agent 的 token cost、加上 prompt caching、再量一次。观察 cache hit rate 跟 cost 下降的对应关系。**Bonus**：接 [RouteLLM](https://github.com/lm-sys/RouteLLM) 或 [OpenRouter](https://openrouter.ai/)、做 cascade routing（简单 query → Haiku / 难 query → Opus），量平均 cost。

## 📊 Agent Benchmark Landscape：怎么看，不要只看排行榜 + ⚠ Reward-Hacking 警告

挑 model / build agent 之前，你会想看 benchmark 数字——但 **2026-04 UC Berkeley 发现 8 个主流 agent benchmark 全部可被 reward-hack 到 ~100%**。下面是 2026 leaderboard 现况 + 怎么看不被骗。

### 主流 Agent Benchmark 2026-05 SOTA

| Benchmark | 领域 | 2026-05 SOTA | 领先 Model |
|---|---|---|---|
| [**SWE-bench Verified**](https://www.swebench.com/) | 软工 / code agent | **88.6%** | Claude Opus 4.8 |
| [**Terminal-Bench**](https://github.com/laude-institute/terminal-bench) | terminal 任务 | 领先 | Claude Opus 4.8 |
| **GAIA** | general assistant | **74.6%** | Claude Sonnet 4.5（Princeton HAL）|
| [**WebArena**](https://github.com/web-arena-x/webarena) | web 导航 | **68.7%** | （领先 model 未公布）|
| [**ClawBench**](https://github.com/TIGER-AI-Lab/ClawBench) | 真实网站上的 browser agent 任务 | **44.6%**（lenient）/**24.6%**（strict） | Claude Opus 4.7（V2 Hermes leaderboard history、2026-08 快照：58/130 通过）；283 个任务、144 个真实网站、Apache-2.0、[论文](https://arxiv.org/abs/2604.08523)；V2 两阶段 rubric 比 V1 更严格 |
| [**OSWorld**](https://github.com/xlang-ai/OSWorld) | OS-level 桌面控制 | v1 **76.26%**（接近饱和）| OpenAI CUA 38%；[OSWorld 2.0](https://osworld-v2.xlang.ai/)（2026-06、long-horizon）已取代 v1、真实长任务 SOTA 仅 ~20%（Opus 4.8 20.6%），见 Stage 8 |
| [**τ-bench**](https://github.com/sierra-research/tau-bench) | tool use 多轮对话 | （较难 hack）| Anthropic / OpenAI 领先 |
| **RE-bench** | research engineering | （较难 hack、接近人类 baseline）| Frontier model |

> **⚠ 上表是 Opus 4.8 世代的数字**：这些都是当时实测并归属到该 model 的结果，故原样保留。Claude Opus 5（`claude-opus-5`）已于 2026-07-24 发布、Anthropic 官方宣称有所提升，但那些宣称目前还没有第三方独立复现，因此本表刻意不拿它们来更新。

> **Mythos-class 层级（Claude Fable 5 — 2026-06-09 发布）**：[**Claude Fable 5**](https://www.anthropic.com/news/claude-fable-5-mythos-5)（`claude-fable-5`，Mythos-class、定位在 Opus 之上）是对外开放的最高能力 Claude 层级，与姊妹版 Claude Mythos 5（`claude-mythos-5`，部分安全措施放宽、限定核准客户）同日发布。曾于 2026-06-12 因美国出口管制指令暂停，[2026-07-01 全球恢复](https://www.anthropic.com/news/redeploying-fable-5)（Mythos 5 仅对核准的美国组织恢复）。上表数字维持原本归属的 model；Fable 5 官方 benchmark 数字始终未公布，故未列入。**Fable 5 是最高阶的 Claude 层级；Opus-class 旗舰现为 Claude Opus 5（Opus 4.8 仍可使用，官方文档已归入 legacy）。**

→ 详细排行 + 即时更新：[Agent Benchmark Leaderboard 2026](https://benchmarkingagents.com/agent-benchmarks/)、[Rapid Claw AI Agent Framework Scorecard 2026](https://rapidclaw.dev/blog/ai-agent-benchmarks-2026)

### ⚠ Berkeley 2026-04 Reward-Hacking 警告

[**UC Berkeley RDI 2026-04-12 报告**](https://rdi.berkeley.edu/blog/trustworthy-benchmarks-cont/)：用 automated scanning agent 系统性 audit **8 个主流 benchmark**（SWE-bench / WebArena / OSWorld / GAIA / Terminal-Bench / FieldWorkArena / CAR-bench 等）、**每个都能 reward-hack 到接近 100%、agent 一个 task 都不用真正解**。

意思：leaderboard 上“Claude 87.6% / GPT 85.0%”这种数字、可能其中 X% 是 hack 出来的、不是真的解 task。

### 怎么看 benchmark 不被骗

| 看数字方式 | 推荐 |
|---|---|
| 只看 leaderboard top | ❌ 上面 8 个都被证实可 hack |
| 看 task-level success rate breakdown | ✅ 多数 hack 集中少数 task |
| 跑你自己的 hold-out test set | ✅✅ 最可靠、production agent 必做 |
| 看 trajectory / log 是否真的解 task | ✅ 区分 reward hacking vs genuine solve |
| 看多个 benchmark + 自己 use case | ✅ 不依赖单一指标 |

**哪些 benchmark 较难 hack（2026-05）**：

- **τ-bench** — 多轮对话 + tool use、reward function 较密集
- **RE-bench** — research engineering 真实任务
- **你自己的 production eval set** ⭐ 永远是最可靠的

> 💡 **production agent 的 eval 纪律**：
> - 不要把外部 benchmark 数字当 ground truth、它告诉你“上限”不是“真实表现”
> - 你自己的 eval set（内部 hold-out test）才是上线决策的依据
> - 每次 model upgrade → 跑内部 eval set 验证、不只看厂商公布的 benchmark 提升
> - 接 [langfuse](https://github.com/langfuse/langfuse) / [promptfoo](https://github.com/promptfoo/promptfoo) 把 eval 自动化、每次 deploy 都跑

> 📊 **observability 认一个可携标准 + 两个评估观念**：(1) **OpenTelemetry GenAI 惯例**（`gen_ai.*` semantic conventions）——langfuse / Arize Phoenix / Helicone 都吐 OTel-兼容 span，认这层才不被单一工具绑死；OTel-native 的 [Arize Phoenix](https://github.com/Arize-ai/phoenix)（★ 10k+）可看。(2) **pass^k**（同一题连对 k 次的概率 = 可靠度，不是只看过一次）+ [τ²-bench](https://github.com/sierra-research/tau2-bench)。(3) 多 agent 失败有现成词汇：**MAST**（[arXiv 2503.13657](https://arxiv.org/abs/2503.13657)、14 种失败模式分 3 类）。

## 🎯 常用 Multi-Agent / Production 工具推荐（按用途分类）

不知道从哪挑工具？下面是 2025-2026 业界常用搭配——**挑入口看“场景”、想深入点链接看 repo**：

| 场景 | 推荐工具 | 为什么 |
|---|---|---|
| **第一次写 multi-agent**（最快上手）| [crewAI](https://github.com/crewAIInc/crewAI) | role-based、几行 code 跑起来、production pattern 直接 |
| **想要 group debate / brainstorm pattern** | [AutoGen](https://github.com/microsoft/autogen) | GroupChat 自由辩论、Microsoft 出品 |
| **production 要 audit trail / checkpoint / human-in-loop** | [LangGraph](https://github.com/langchain-ai/langgraph) | state machine、控制最完整 |
| **eval 标准化**（CI / regression 必装）| [promptfoo](https://github.com/promptfoo/promptfoo) ⭐ | YAML config、跨模型比较、★ 23k+ |
| **eval + observability 同平台** | [langfuse](https://github.com/langfuse/langfuse) ⭐ | OSS、tracing + eval + prompt mgmt、★ 31k+ |
| **不改程序、快速 instrumentation** | [Helicone](https://github.com/Helicone/helicone) | proxy 中介、不绑 framework |
| **全 stack 在 LangChain** | [LangSmith](https://www.langchain.com/langsmith)（商业）| LangChain 官方 observability |
| **打造 Claude agent**（programmatic）| [claude-agent-sdk-python](https://github.com/anthropics/claude-agent-sdk-python) ⭐ | Anthropic 官方 agent SDK、跟 Claude Code 同 runtime |
| **Deploy agent 成 API service** | [BentoML](https://github.com/bentoml/BentoML) | 最完整、Docker + serving |
| **自架开源 LLM**（取代付费 API）| [vLLM](https://github.com/vllm-project/vllm) | 高吞吐量、★ 87k+ |
| **Fine-tune 开源 LLM** | [LLaMA-Factory](https://github.com/hiyouga/LLaMA-Factory) | 100+ 模型统一 SFT/DPO/PPO/GRPO、Web UI 零 code、中文社群最广、★ 73k+ |

**建议入手顺序**：

1. 第一个 multi-agent：**crewAI**（role-based、最简单）
2. 加 eval：**promptfoo**（YAML、CI 整合）
3. 加 observability：**langfuse**（OSS、完整）
4. Production 升级：换 **LangGraph**（control 强）+ **BentoML**（deploy）
5. 进阶：自架 LLM 接 **vLLM**、fine-tune 用 **LLaMA-Factory**

## 🎯 精选 Projects（范本 / SDK / 工具 collection）

按用途分类、27 个项目一张表搞定。**挑入口看“适合谁”、想深入点链接看 repo**。

| 分类 | Project | ⭐ | 适合谁 | 为什么推荐 / 备注 |
|---|---|---|---|---|
| **Multi-Agent Orchestration** | [microsoft/autogen](https://github.com/microsoft/autogen) | ⭐⭐⭐⭐⭐ | 想要 GroupChat 自由 debate pattern | Stage 4 介绍过、production 场景再回头看 multi-agent 辩论 / brainstorming 模式 |
| | [crewAIInc/crewAI](https://github.com/crewAIInc/crewAI) | ⭐⭐⭐⭐⭐ | 想要 role-based 流水线 | 角色式 multi-agent（research → writer → reviewer），最简单 production pattern |
| | [langchain-ai/langgraph](https://github.com/langchain-ai/langgraph) | ⭐⭐⭐⭐⭐ | 需要 audit trail / checkpoint / human-in-the-loop | state machine 路线、production 控制最强 |
| **Eval Frameworks** | [promptfoo](https://github.com/promptfoo/promptfoo) ⭐ | ⭐⭐⭐⭐⭐ | 把 eval 流程标准化、CI 整合 | YAML config、跨模型比较。★ 23k+、MIT |
| | [lm-evaluation-harness](https://github.com/EleutherAI/lm-evaluation-harness) | ⭐⭐⭐⭐ | 学术 benchmark 主张（MMLU / HellaSwag / GSM8K）| 学术等级。★ 13k+、MIT |
| | [openai/evals](https://github.com/openai/evals) | ⭐⭐⭐⭐ | OpenAI 专属 eval / 想回馈上游 | ★ 19k+ |
| **Observability** | [langfuse](https://github.com/langfuse/langfuse) ⭐ | ⭐⭐⭐⭐⭐ | 自架 production observability | OSS LangSmith 替代、traces + sessions + evals + prompt mgmt。★ 31k+、MIT |
| | [LangSmith](https://www.langchain.com/langsmith)（商业）| ⭐⭐⭐⭐ | 全 stack 在 LangChain / LangGraph 上 | LangChain 官方、只有 hosted 版 |
| | [Helicone](https://github.com/Helicone/helicone) | ⭐⭐⭐⭐ | 不想改程序、快速上 instrumentation | proxy 中介、顺便拿到 logging + caching。★ 6k+、Apache 2.0 |
| | [weave (W&B)](https://github.com/wandb/weave) | ⭐⭐⭐⭐ | 团队已在用 W&B 做 ML 实验追踪 | W&B tracing + eval、跟 wandb 整合 |
| | [comet-ml/opik](https://github.com/comet-ml/opik) | ⭐⭐⭐⭐ | eval + observability 同一个开源平台 | 追踪 LLM / agent 做了什么、追踪实验、跑质量检查（eval）。★ 21k+、Apache 2.0 |
| | [pydantic/logfire](https://github.com/pydantic/logfire) | ⭐⭐⭐⭐ | 用 OpenTelemetry 标准追踪 agent / LLM 调用 | 看清楚并 debug 你的 agent / LLM 调用做了什么；Pydantic 团队出品、建在 OpenTelemetry 标准上。★ 4.4k+、MIT |
| **Safety / Guardrails** | [NVIDIA-NeMo/Guardrails](https://github.com/NVIDIA-NeMo/Guardrails) | ⭐⭐⭐⭐ | 想在 agent 的输入 / 输出加上安全规则 | 包在 LLM app 外的安全规则——让它不离题、挡 jailbreak、过滤不当输出。★ 6.6k+、Apache 2.0 |
| **Anthropic SDK 进阶** | [anthropic-sdk-python](https://github.com/anthropics/anthropic-sdk-python) | ⭐⭐⭐⭐⭐ | 直接基于 Claude API 做应用 | 官方 Python SDK：streaming / async / tool use / prompt caching / batches / files |
| | [anthropic-sdk-typescript](https://github.com/anthropics/anthropic-sdk-typescript) | ⭐⭐⭐⭐ | TypeScript / Node / web app | Python SDK 的 TS 版 |
| | [claude-agent-sdk-python](https://github.com/anthropics/claude-agent-sdk-python) ⭐ | ⭐⭐⭐⭐⭐ | 打造 Claude-based agent 而非只 API | 内建 tool use loop / file access / sandbox / subagent 编排；跟 Claude Code 同 runtime、想看内部运作直接读 source。★ 7.6k+、MIT |
| | [claude-agent-sdk-typescript](https://github.com/anthropics/claude-agent-sdk-typescript) | ⭐⭐⭐⭐ | Node / web app 环境 Claude agent | Claude Agent SDK TS 版。★ 1.6k+ |
| | [Anthropic Cookbook（进阶）](https://github.com/anthropics/anthropic-cookbook) | ⭐⭐⭐⭐ | 想看官方进阶 SDK pattern | 特别是 `prompt_caching.ipynb` / `tool_use/` / `multimodal/` 三个 notebook |
| **Structured Output** | [BoundaryML/baml](https://github.com/BoundaryML/baml) | ⭐⭐⭐⭐ | 想稳定拿到任何模型输出的可靠 JSON | 一个专用小语言、帮你从 LLM 稳定取得经过检查的 JSON；支持 Claude / OpenAI / 本地模型、7 种编程语言。★ 8.8k+、Apache 2.0 |
| **Deployment** | [BentoML](https://github.com/bentoml/BentoML) | ⭐⭐⭐⭐ | 把 agent 包成 production API service | Docker + serving framework。★ 8.8k+、Apache 2.0 |
| | [LangServe](https://github.com/langchain-ai/langserve) | ⭐⭐⭐（⚠️ 已封存）| LangChain agent 快速 deploy | 底层 FastAPI；⚠️ **repo 已封存 2026-05**、新部署改用 LangGraph Platform |
| | [vLLM](https://github.com/vllm-project/vllm) | ⭐⭐⭐⭐ | 自架开源 LLM 取代付费 API | 高吞吐量 LLM serving、Llama / Qwen 等。★ 87k+、Apache 2.0 |
| **中文 deploy / fine-tune** | [datawhalechina/self-llm](https://github.com/datawhalechina/self-llm) | ⭐⭐⭐⭐ | 中文团队要自架开源 LLM | training-to-deployment 完整中文指南、Qwen / Llama / GLM / 多模态。★ 31k+、Apache 2.0 |
| | [hiyouga/LLaMA-Factory](https://github.com/hiyouga/LLaMA-Factory) | ⭐⭐⭐⭐⭐ | 要 fine-tune 开源 LLM（不只 prompt eng）| 100+ 模型统一 SFT/DPO/PPO/GRPO、Web UI 零 code、中文社群最广。★ 73k+、Apache 2.0 |
| **Multi-Agent 案例研究** | [geekan/MetaGPT](https://github.com/geekan/MetaGPT) | ⭐⭐⭐⭐⭐ | 想看角色分工 + artifact 交接 pattern | SOP-based PM / Architect / Engineer multi-agent team、PRD → 设计 → code 一路产出。★ 67k+、MIT |
| | [OpenBMB/ChatDev](https://github.com/OpenBMB/ChatDev) | ⭐⭐⭐⭐ | 想看 agent debate / peer-review pattern | 对话式软件开发、agents 在 design / code / test 互相辩论。★ 33k+、Apache 2.0、有 zh README |
| | [princeton-nlp/SWE-agent](https://github.com/princeton-nlp/SWE-agent) | ⭐⭐⭐⭐ | 理解为什么 tool 设计 > prompt tuning | Agent-Computer Interface (ACI) 设计思路、Princeton paper-backed、SWE-Bench 领先方法。★ 19k+、MIT |

> 🌳 **Claude 原生 subagent 机制**（不用 framework 也能 multi-agent）见 [Stage 5.5](05-claude-code-ecosystem.zh-Hans.md#55--subagentsclaude-code-原生-multi-agent-机制-2025-新功能)。本 stage 重 framework / production；Stage 5.5 重 markdown-based subagent 编排。

## ✅ Stage 7 之后的自我检查

你能不能：

- [ ] 设计一个 multi-agent 系统，协作协定讲得清楚
- [ ] 在 CI 跑自动 eval pipeline
- [ ] 把 observability（tracing）接到 production agent
- [ ] 在真实 workload 上量测 prompt caching 前后的成本差异
- [ ] 把 agent deploy 到云端（任何 provider）

如果都可以 → 先进 [**Stage 7.5 — 进阶 Agentic 概念地图**](07.5-advanced-agentic-concepts.zh-Hans.md)（1 周、不写 code、建立 frontier 概念地图、定位业界还在讨论哪些进阶概念），再进 [**Stage 8 — Agent Interfaces**](08-agent-interfaces.zh-Hans.md)（**两 track 共用 hub**）学 agent 怎么跟非 API 世界互动（Computer Use / Browser Use / Sandbox）。或挑一个[特化分支](../README.zh-Hans.md#-学习地图两条学习路径)、或回头来贡献这份 repo。

## 💡 接下来

你已经有基础能力了。接下来 6-12 个月应该专注在：

1. **挑一个 production 系统** 从 prototype 推到 production
2. **回馈上游**（LangGraph、AutoGen、MCP servers、Anthropic cookbook）
3. **读论文**——agent 研究进展很快
4. **做出看得到的东西**——开源一个真的工具，不要再写教学了
