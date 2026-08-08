<div align="right">
  <a href="./README.md">繁體中文</a> | <strong>简体中文</strong> | <a href="./README.en.md">English</a>
</div>

# 练习 6：Function Schema 设计（bad vs good）

对应 [Stage 3 — Tool Use & Agent 入门](../../../stages/03-tool-use-and-hello-agent.zh-Hans.md) 练习 6。
> 🎓 **学习模式**：这份 `starter.py` 是**完整解答**、不是 TODO skeleton。建议用**主动模式**——`mv starter.py starter_reference.py`、看 signature 不看 body、自己重写一份 `starter.py`、跑 `python test.py` 验证；卡 20 分钟再回去对照 reference。完整方法论看 [`docs/HOW_TO_USE.md`](../../../docs/HOW_TO_USE.md)。

> 📚 **想要 chapter-length 深入版？** 本 folder 的 starter 是 70-150 行 illustrative 版、聚焦 `核心 pattern + 两条 SDK path`，不是进阶深度教材。深度教材推荐：
> - [`datawhalechina/hello-agents`](https://github.com/datawhalechina/hello-agents) ⭐ 中文圈最完整、章节式 + 16 种 production 能力。**本练习对应 hello-agents 的 [Extra08 — 如何写出好的 Skill](https://github.com/datawhalechina/hello-agents/blob/main/Extra-Chapter/Extra08-如何写出好的Skill.md)**
> - [OpenAI Function Calling guide](https://platform.openai.com/docs/guides/function-calling) + [schema 设计 cheatsheet](../../../resources/schema-design-cheatsheet.zh-Hans.md)
> - 完整 references 见 [Stage 3 精选 Projects](../../../stages/03-tool-use-and-hello-agent.zh-Hans.md#-精选-projects)


## 为什么这题重要

Schema 是 **prompt 的一部分**、而且是模型做工具选择时**最依赖**的 prompt。这题用 `starter_bad` 与 `starter_good` 对照同一题：“把摄氏 32 度换成华氏”。

- **Bad schema**：description 太短、参数都 string、没 required、没 enum → LLM 容易把温度转换丢给 `process_data`
- **Good schema**：用途明确、`value: number`、`unit: enum["celsius", "fahrenheit"]`、required 都列好 → 稳定选到 `convert_temperature`

写 schema 不要只想“人看得懂”、要想“模型能不能用它排除错误工具”。

## 怎么跑 — 两条路径

### Path A（默认、本机免费、4 个 starter）

```bash
pip install -r requirements.txt
ollama pull qwen2.5:3b
ollama serve

python starter_bad.py    # 观察坏 schema 怎么让 qwen 挑错
python starter_good.py   # 观察好 schema 怎么让 qwen 挑对
```

预算：**$0**。

### Path B（Anthropic、想看 cloud 高质量）

```bash
pip install -r requirements.txt
export ANTHROPIC_API_KEY=sk-ant-...

python starter_bad_anthropic.py
python starter_good_anthropic.py
```

预算：每次 ≈ **$0.0005**（claude-haiku-4-5、单轮 call）。

## 不花钱验证程序逻辑（mock-based）

```bash
python test.py            # 验 Path A (Ollama) starter_bad + starter_good
python test_anthropic.py  # 验 Path B (Anthropic) starter_*_anthropic
```

两条 test 都用 `unittest.mock`、不打真 API、$0/run。每组 test 都直接检查 schema 结构（good 有 `required` + `enum`、bad 没有），不只是看 LLM 怎么选。

## Bad vs Good schema 对照

| 设计面向 | Bad | Good |
|---|---|---|
| Description | "Process data." | "Use only to summarize structured JSON table rows. Do not use for temperature conversion." |
| 参数类型 | 全部 `string` | `number` / `array` / 对应实际类型 |
| Required | 无 | `["value", "unit"]` |
| Enum 收敛 | 无 | `["celsius", "fahrenheit"]` |
| 失败回传 | 简单字符串 | 结构化 dict + retry_hint |

## 两个 path 的观察重点（教学重点）

**小 model 对 schema 质量的敏感度比大 model 高**——这题在 Ollama 上**反而更有教学意义**：

| 观察项 | Anthropic Claude haiku | Ollama qwen2.5:3b |
|---|---|---|
| Bad schema 仍能猜对 | 中-高机率 | 低机率（几乎必错） |
| Good schema 选对 | 稳定 | 稳定 |
| 差距 | 小 | 大 |

换句话说：**写 schema 的功夫、在小 model 上能省下换大 model 的成本**。Production 想用便宜 model（qwen / mistral）？schema 必须写到能上线跑的程度。

## 延伸阅读

更多 schema 设计规则对照 [`resources/schema-design-cheatsheet.zh-Hans.md`](../../../resources/schema-design-cheatsheet.zh-Hans.md)：清楚用途、正确类型、必填字段、enum 收敛、结构化错误回传。

## 延伸

- **故意改坏 good schema**：把一个 enum 拿掉、看 qwen 是否就开始挑错
- **加第三个工具**：写一个跟 `convert_temperature` 用途相近但边界模糊的 tool、看 LLM 怎么挑
- **接 [`../05-error-handling/`](../05-error-handling/) 的 structured error pattern**：结合 schema 设计 + 错误处理、production 级
