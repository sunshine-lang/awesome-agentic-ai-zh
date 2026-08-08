<div align="right">
  <a href="./README.md">繁體中文</a> | <strong>简体中文</strong> | <a href="./README.en.md">English</a>
</div>

# 练习 5：型别安全 agent（Pydantic AI structured output）

对应 [Stage 4 — Agent Frameworks](../../../stages/04-agent-frameworks.zh-Hans.md) 练习 5。
> 🎓 **学习模式**：这份 `starter.py` 是**完整解答**、不是 TODO skeleton。建议用**主动模式**——`mv starter.py starter_reference.py`、看 signature 不看 body、自己重写一份 `starter.py`、跑 `python test.py` 验证；卡 20 分钟再回去对照 reference。完整方法论看 [`docs/HOW_TO_USE.md`](../../../docs/HOW_TO_USE.md)。

> 📚 **想要 chapter-length 深入版？** 本 folder 的 starter 是 illustrative 版、聚焦核心 pattern + 两条 SDK path，不是进阶深度教材。深度教材推荐：
> - [`datawhalechina/hello-agents`](https://github.com/datawhalechina/hello-agents) ⭐ 中文圈最完整、章节式 + 16 种 production 能力。**本练习对应 hello-agents 的 structured output / type-safe 章节**
> - [Pydantic AI 官方 docs](https://ai.pydantic.dev/) + [Instructor library](https://github.com/instructor-ai/instructor)（另一条 typed-output 路线）
> - 完整 references 见 [Stage 4 精选 Projects](../../../stages/04-agent-frameworks.zh-Hans.md#-精选-projects)


## 任务

Agent 回问题、**强制** return `AnswerWithConfidence`：

```python
class AnswerWithConfidence(BaseModel):
    answer: str
    confidence: float = Field(ge=0.0, le=1.0)  # runtime 验证 0-1
    sources: list[str]
```

Pydantic AI 把 schema validation 从 prompt 层（Stage 3 练习 6）**提升到 type 层**——LLM 不照 schema、framework 自动 retry。Production team 用这个防 hallucinate。

## 怎么跑 — 两条路径

### Path A（默认、本机免费）

```bash
pip install -r requirements.txt
ollama pull qwen2.5:3b
ollama serve
python starter.py
```

预算：**$0**。但 qwen2.5:3b 可能 retry 多次才产对 schema、总 token 较高。

### Path B（Anthropic、想看 cloud 高质量）

```bash
pip install -r requirements.txt
export ANTHROPIC_API_KEY=sk-ant-...
python starter_anthropic.py
```

预算：每次 ≈ **$0.001**（claude-haiku-4-5、通常一次过、无 retry）。

## 不花钱验证程序逻辑

```bash
python test.py             # Pydantic schema 验证 + agent 结构
python test_anthropic.py   # Path B 载入检查
```

`test.py` 直接验 `AnswerWithConfidence` 对非法数据（confidence > 1.0、type 不对、sources 不是 list）的 ValidationError——不需要打 LLM、纯 type 层测试。

## 为什么 type-safe agent 重要

```
Stage 3 练习 6：schema = JSON Schema in prompt
    LLM 看到、但回什么是 LLM 决定（可能违反）

Stage 4 练习 5：schema = Pydantic model in code
    LLM 违反 → framework 自动 raise → retry / 修
    最终 output 一定 conform（runtime 保证）
```

对 production：

| 需求 | 纯 prompt schema | Pydantic AI |
|---|---|---|
| LLM 偶尔少字段 | 你的下游 code 要 try/except | 自动 retry 直到符合 |
| 类型错（confidence="high"） | 下游 crash | Pydantic ValidationError、retry |
| 边界错（confidence=1.5） | 下游用错误值 | 拒绝、retry |
| LLM hallucinate 多余字段 | 接收 silently | 预设 ignore（可调 strict） |

**结论**：production agent 必用 type-safe output。Stage 3 练习 6 教 schema 设计、Stage 4 练习 5 教把 schema 变成 runtime contract。

## Pydantic AI 核心观念

### Agent + output_type

```python
agent = Agent(
    model=...,
    output_type=AnswerWithConfidence,   # ← 强制 LLM 回这个 shape
    system_prompt="..."
)
result = agent.run_sync(question)
answer: AnswerWithConfidence = result.output   # 已验证的物件
```

**重点**：framework 在背后把 Pydantic schema 转成 LLM 的 structured output instruction、执行 validation、failure 时 retry。

### Field constraints

```python
confidence: float = Field(ge=0.0, le=1.0, description="...")
```

`ge` / `le` 是 Pydantic 的 numeric bound。LLM 回 `1.5` 会被 ValidationError 挡下、retry。

### 自动 retry

```python
Agent(..., retries=3)  # default 1，可调
```

Pydantic AI 看到 ValidationError、会把错误讯息塞回 prompt、要求 LLM 重产。

## 两个 path 观察重点

| 观察项 | Anthropic Claude haiku | Ollama qwen2.5:3b |
|---|---|---|
| 一次产对 schema | 90%+ | 50-70% |
| 平均 retry 次数 | 0-1 | 1-3 |
| confidence 边界遵守 | 稳 | 偶尔 1.5 / 负值（会被 reject + retry） |
| sources 是 list | 稳 | 偶尔 string、被 reject |
| 总 token 成本 | 低（少 retry） | 高（多 retry） |

**反直觉结论**：Path B（Claude）的实际 token cost **可能比 Path A（qwen）低**——retry 成本累计起来。Production team 算总帐会选大 model。

## 常见坑

- **`output_type` 太复杂**：nested model 深、LLM 难一次写对。production 建议扁平化、≤5 个 top-level 字段
- **缺 `description`**：`Field(...)` 没写 `description=`、LLM 看不到字段用途、易误填
- **`retries=0`**：失败就 raise、不给 LLM 修的机会。经验值 `retries=1-3`
- **小 model + 深 nested**：qwen2.5:3b 可能 retry 多次仍不对。换大 model 或扁平 schema

## 想看更聪明的答案？

```bash
MODEL=claude-sonnet-5 python starter_anthropic.py    # 一次过机率最高
MODEL=qwen2.5:7b python starter.py                      # 较大本机 model
```

## 延伸

- **加 tools**：Pydantic AI agent 可以同时有 tools + structured output、`@agent.tool` 装饰函数
- **stream typed output**：`agent.run_stream(...)` 边跑边验
- **跨 model 比较**：同一个 schema 跑 Claude / GPT / Gemini / 本机 model、看谁最稳
- **接 production**：Pydantic AI 跟 FastAPI 整合很好、output 直接当 API response model
