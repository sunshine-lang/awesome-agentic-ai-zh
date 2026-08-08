<div align="right">
  <a href="./README.md">繁體中文</a> | <strong>简体中文</strong> | <a href="./README.en.md">English</a>
</div>

# 练习 2：多工具选择

对应 [Stage 3 — Tool Use & Agent 入门](../../../stages/03-tool-use-and-hello-agent.zh-Hans.md) 练习 2。
> 🎓 **学习模式**：这份 `starter.py` 是**完整解答**、不是 TODO skeleton。建议用**主动模式**——`mv starter.py starter_reference.py`、看 signature 不看 body、自己重写一份 `starter.py`、跑 `python test.py` 验证；卡 20 分钟再回去对照 reference。完整方法论看 [`docs/HOW_TO_USE.md`](../../../docs/HOW_TO_USE.md)。

> 📚 **想要 chapter-length 深入版？** 本 folder 的 starter 是 70-150 行 illustrative 版、聚焦 `核心 pattern + 两条 SDK path`，不是进阶深度教材。深度教材推荐：
> - [`datawhalechina/hello-agents`](https://github.com/datawhalechina/hello-agents) ⭐ 中文圈最完整、章节式 + 16 种 production 能力。**本练习对应 hello-agents 的 tool-calling / multi-tool dispatch 章节**
> - [Anthropic Tool Use Cookbook](https://github.com/anthropics/claude-cookbooks/tree/main/tool_use)（单工具→多工具→parallel 完整 notebook）
> - 完整 references 见 [Stage 3 精选 Projects](../../../stages/03-tool-use-and-hello-agent.zh-Hans.md#-精选-projects)


## 为什么这题重要

这个练习让 LLM 在同一轮面对三个工具：`web_search`、`calculator`、`calendar_lookup`。重点不是工具本身强不强，而是观察 schema 的 `name` / `description` / `parameters` 如何决定模型挑哪一个。把 schema 写清楚，是 Stage 3 最值得花时间的子题。

## 怎么跑 — 两条路径

### Path A（默认、本机免费）

```bash
pip install -r requirements.txt
ollama pull qwen2.5:3b
ollama serve
python starter.py
```

预算：**$0**。qwen2.5:3b 单轮 tool call ≈ 1-5 秒（CPU 慢、GPU 快）。

### Path B（Anthropic、想看 cloud 高质量）

```bash
pip install -r requirements.txt
export ANTHROPIC_API_KEY=sk-ant-...
python starter_anthropic.py
```

预算：每次 ≈ **$0.0005**（claude-haiku-4-5）。

预期看到（Path A、本机）：

```
❓ 问题：What is (19 * 42) - 8? Use the best available tool.（using Ollama qwen2.5:3b）
   tool: calculator
   tool_input: {'expression': '(19 * 42) - 8'}
   observation: 790
✅ 练习 2 通过 — 你已用本机 qwen2.5:3b 跑通 multi-tool selection、$0/run
```

## 不花钱验证程序逻辑（mock-based）

```bash
python test.py            # 验 Path A (Ollama) starter.py 逻辑
python test_anthropic.py  # 验 Path B (Anthropic) starter_anthropic.py 逻辑
```

两条 test 都用 `unittest.mock`、不打真 API、$0/run。Path A 用 OpenAI-compat response shape、Path B 用 Anthropic content blocks。

## 两条 path 的 SDK 差异

三个关键差异（其他完全一样）：

| 部分 | Anthropic（Path B） | OpenAI-compat / Ollama（Path A） |
|---|---|---|
| Schema 包法 | `tools=[{name, description, input_schema}, ...]` | `tools=[{"type": "function", "function": {name, description, parameters}}, ...]` |
| 抓 tool call | `resp.content[i].type == "tool_use"` | `resp.choices[0].message.tool_calls[i]` |
| input 格式 | `call.input` 是 dict（自动 parse） | `call.function.arguments` 是 JSON string、要 `json.loads(...)` |

Tool selection **逻辑本身**跨 backend——schema 写好、qwen2.5:3b 也会挑对 tool。这题很适合拿来对照 Claude vs qwen2.5“在哪几题会挑错”，是观察小 model 边界的好实验。

## 容易踩坑

多工具选择最常见的错误是 description 写得太像“一般说明文档”，而不是“给模型做决策的判断规则”：

- `calendar_lookup` 描述只说“行事历”就会跟 `web_search` 边界模糊；明写“查特定日期事件”才好
- `web_search` 适合“外部 / 近期 / 不确定信息”、`calculator` 只处理算式；边界写越清楚、模型越少误判
- 小 model（qwen2.5:3b）对 description 质量比 Claude **更敏感**——同一份 schema、Claude 可能还能猜对、qwen 直接挑错

## 想看更聪明的答案？

预设用 `claude-haiku-4-5`（最便宜）。改成 sonnet：

```bash
MODEL=claude-sonnet-5 python starter_anthropic.py
```

或在 Ollama path 换 `qwen2.5:7b`（更大、更稳、但慢）：

```bash
MODEL=qwen2.5:7b python starter.py
```

## 延伸

- **加更多 tool**：在 `TOOLS_SPEC` + `TOOL_IMPL` 补一个 entry 即可
- **改成多轮 ReAct**：把单轮 call 包进 while loop，看 [`../03-react-from-scratch/`](../03-react-from-scratch/)
- **schema 细节**：看 [`../06-schema-design/`](../06-schema-design/) 比较 bad / good schema 对选择正确率的影响
