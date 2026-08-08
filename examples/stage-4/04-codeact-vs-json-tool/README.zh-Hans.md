<div align="right">
  <a href="./README.md">繁體中文</a> | <strong>简体中文</strong> | <a href="./README.en.md">English</a>
</div>

# 练习 4：CodeAct vs JSON tool（Smolagents）

对应 [Stage 4 — Agent Frameworks](../../../stages/04-agent-frameworks.zh-Hans.md) 练习 4。
> 🎓 **学习模式**：这份 `starter.py` 是**完整解答**、不是 TODO skeleton。建议用**主动模式**——`mv starter.py starter_reference.py`、看 signature 不看 body、自己重写一份 `starter.py`、跑 `python test.py` 验证；卡 20 分钟再回去对照 reference。完整方法论看 [`docs/HOW_TO_USE.md`](../../../docs/HOW_TO_USE.md)。

> 📚 **想要 chapter-length 深入版？** 本 folder 的 starter 是 illustrative 版、聚焦核心 pattern + 两条 SDK path，不是进阶深度教材。深度教材推荐：
> - [`datawhalechina/hello-agents`](https://github.com/datawhalechina/hello-agents) ⭐ 中文圈最完整、章节式 + 16 种 production 能力。**本练习对应 hello-agents 的 CodeAct vs JSON tool 章节**
> - [Smolagents 官方 cookbook](https://github.com/huggingface/smolagents/tree/main/examples) + [QuantaLogic/quantalogic](https://github.com/quantalogic/quantalogic)（另一个 CodeAct framework）
> - 完整 references 见 [Stage 4 精选 Projects](../../../stages/04-agent-frameworks.zh-Hans.md#-精选-projects)


## 两种 agent action 路线对照

| 路线 | 怎么 act | 范例 framework |
|---|---|---|
| **JSON tool** | LLM 回 `{"name": "tool_x", "arguments": {...}}` | OpenAI function calling、LangGraph、CrewAI |
| **CodeAct** | LLM 写 Python code、直接执行 | HuggingFace Smolagents |

**这题用 CodeAct 解同题（人口比例）、跟练习 1 / 3 的 JSON tool 路线对照**。

## 怎么跑 — 两条路径

### Path A（默认、本机免费）

```bash
pip install -r requirements.txt
ollama pull qwen2.5:3b
ollama serve
python starter.py
```

预算：**$0**。CodeAct 对小 model 比较吃力——qwen2.5:3b 可能会产 syntax error、agent 自己迭代修。

### Path B（Anthropic、想看 cloud 高质量）

```bash
pip install -r requirements.txt
export ANTHROPIC_API_KEY=sk-ant-...
python starter_anthropic.py
```

预算：每次 ≈ **$0.005-0.02**（CodeAct 通常多步、claude-haiku-4-5）。Claude 写 Python code 比 qwen2.5:3b 稳很多。

## 不花钱验证程序逻辑

```bash
python test.py             # tool function + agent 结构
python test_anthropic.py   # Path B 可载入检查
```

## CodeAct 是怎么运作的

LLM 不回 JSON、而是**回 Python code block**：

```
（user）Find Taipei population, divide by NYC, give ratio.

（LLM 回应）
```python
pop_taipei = lookup_fact(query="Taipei population")  # 2602000
pop_nyc = lookup_fact(query="New York population")   # 8336000
ratio = calculator(expression=f"{pop_taipei}/{pop_nyc}")  # 0.3122
print(ratio)
```

（Smolagents 执行这段 code、把 print 结果接回去给 LLM 继续）
```

Framework 提供 sandboxed Python interpreter、agent 在里面 import tool、写 code、看 print 结果继续。

## CodeAct vs JSON tool 对照

| 维度 | JSON tool | CodeAct |
|---|---|---|
| LLM 输出形式 | 结构化 JSON | Python 程序码 |
| 变数绑定 | LLM 要自己记得 / 重复调用 | 自然有 variable（`pop_taipei = ...`） |
| 多步运算 | 每步一次 LLM call | 一次写好几行 code |
| 一轮 token 数 | 较少 | 较多（code 较长） |
| 对小 model | 较友善（稳定的 JSON） | 较吃力（要产正确 Python） |
| Debug 友善 | tool call 看得清楚 | 看 code execution log |
| 安全考量 | tool args validated | Sandboxed Python（注意 eval/exec 限制） |
| 哪些题目擅长 | 单步、边界明确 | 多步运算、需要中间 variable |

**HuggingFace 的观点**：CodeAct 更贴近“人类怎么解问题”——你也是用变数记中间结果、不是每步都重新查。

## 两个 path 观察重点

| 观察项 | Anthropic Claude haiku | Ollama qwen2.5:3b |
|---|---|---|
| 产正确 Python syntax | 稳 | 偶尔 syntax error、会自己迭代修 |
| 变数命名 / 重用 | 自然 | 容易重复调用 tool 而非用 variable |
| 多步 ratio 算对 | 高机率 | 中机率 |
| 步数 | 1-2 步 | 3-5 步（迭代修错） |
| 成本 | $0.005-0.02 | $0 |

**punchline**：CodeAct 是 **model 质量敏感** pattern——LLM 要会写能在 production 跑的 Python。**小 model 在 JSON tool 路线比 CodeAct 路线优**（Stage 3 练习 6 也验证过这点）。

## 常见坑

- **`@tool` 函数 docstring 是 prompt 的一部分**：Smolagents 把 docstring 当 tool description 给 LLM 看。**docstring 没写好、LLM 不知道何时用这 tool**
- **CodeAct sandbox**：Smolagents 预设禁 `import os`、`open` 等危险操作。要放行特定 module、设 `additional_authorized_imports=[...]`
- **`max_steps` 不够**：CodeAct 跑多步、`max_steps=4` 可能不够。但太大又会无限循环。经验值 4-8
- **小 model 写的 code 有 syntax error**：Smolagents 会把 error 接回去让 LLM 修、但会浪费 token。Production 用大 model 比较划算

## 想看更聪明的答案？

```bash
MODEL=anthropic/claude-sonnet-5 python starter_anthropic.py  # 最稳
MODEL=qwen2.5:7b python starter.py                              # 较大本机 model
```

## 延伸

- **加更多 tools**：`@tool` 装饰函数即自动 wrap、Smolagents 自动拿 docstring 当 description
- **改 ToolCallingAgent**：Smolagents 也有非 CodeAct 的 `ToolCallingAgent`、用 JSON tool 路线。对照看
- **接 Hugging Face Hub**：`HfApiModel` 直接打 HF inference（不必本机 ollama）
- **看 [Anthropic Building Effective Agents](https://www.anthropic.com/engineering/building-effective-agents)**：Anthropic 的观点是两条路线都合理、看任务
