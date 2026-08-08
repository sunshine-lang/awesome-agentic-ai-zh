<div align="right">
  <a href="./README.md">繁體中文</a> | <strong>简体中文</strong> | <a href="./README.en.md">English</a>
</div>

# tool-calling-tutor — Claude Code skill

> Skill 用途：当你卡在 tool calling（LLM 不调用、args 错、ReAct loop 跑不停、schema 不知道怎么写），自动跳出来帮你 4-symptom 诊断 + 5-step 修法走查。

对应 [Stage 3 — Tool Use & Agent 入门](../../../stages/03-tool-use-and-hello-agent.zh-Hans.md)，同时是 [Stage 5 — Claude Code Ecosystem](../../../stages/05-claude-code-ecosystem.zh-Hans.md) 5.3 的**自带 skill 范例**。

## 为什么这个 skill 存在

Tool calling 是整个 curriculum 最陡的学习曲线——schema 设计、SDK response shape、ReAct loop 三个 mental model 叠在一起。Stage 3 doc 已经把概念讲清楚，但**遇到“我这份就是不会跑”的时候、需要互动式 debug**。

这个 skill 补的就是这块缺：

| 已有资源 | 不足 | 这个 skill 补的 |
|---|---|---|
| `stages/03-tool-use-and-hello-agent.zh-Hans.md` | 讲 6 个练习、不互动 | 互动式 triage：你卡哪个 symptom？ |
| `resources/schema-design-cheatsheet.zh-Hans.md` | 5 条规则 + 5 anti-pattern、prescriptive | 走步骤版：bad → good schema 怎么 4 步改 |
| `resources/glossary.zh-Hans.md` 2 | 1 行定义 | 不重复定义、引用为主 |
| `examples/stage-3/02-06/` | 完整可跑 starter | Skill 指过去当 fork template |

## 双重用途

1. **学习者用**：安装后当 personal debug 助手。当你 prompt Claude Code“为什么 LLM 不调用我的 tool”、skill 自动载入、走 4-symptom 诊断。
2. **Stage 5 5.3 meta-example**：学 SKILL.md 怎么写的时候，直接看这份。包含完整 frontmatter（含 trigger phrases + Do NOT use for）、`references/` 设计、`evals/evals.json` 范例。

## 怎么安装（30 秒）

### Option A：user 级（所有 project 共用）

```bash
mkdir -p ~/.claude/skills/tool-calling-tutor
cp SKILL.md ~/.claude/skills/tool-calling-tutor/
cp -r references evals ~/.claude/skills/tool-calling-tutor/
```

简体中文用户：`cp translations/SKILL.zh-Hans.md ~/.claude/skills/tool-calling-tutor/SKILL.md`（canonical 是 zh-TW）。
繁体中文：直接用 `SKILL.md`。
English：`cp translations/SKILL.en.md ~/.claude/skills/tool-calling-tutor/SKILL.md`

### Option B：project 级（只在这个 repo 触发）

```bash
mkdir -p .claude/skills/tool-calling-tutor
cp SKILL.md references/ evals/ .claude/skills/tool-calling-tutor/
```

### 验证安装

重启 Claude Code、然后 prompt：

```
为什么 LLM 不调用我的 tool？
```

预期：Claude 自动载入 skill、先问你“是 (a)/(b)/(c)/(d) 哪个 symptom”、然后 branch 到对应 reference。

## 包含什么

```
tool-calling-tutor/
├── SKILL.md # 主 skill 档（zh-TW canonical）
├── README.md / .en.md / .zh-Hans.md # 你正在看的这份
├── references/
│ ├── debug-flowchart.md # 4-symptom 诊断流程
│ ├── schema-evolution.md # bad → good schema 4-step worked example
│ └── sdk-diff.md # Anthropic vs OpenAI-compat 并排对照
│ （以上每份都有 .en.md / .zh-Hans.md 翻译）
├── translations/
│ ├── SKILL.en.md # SKILL.md 英文版（给英语用户装）
│ └── SKILL.zh-Hans.md # SKILL.md 简体版
└── evals/
    └── evals.json # 5 个 test cases（promptfoo / 手动皆可）
```

## 跑 evals（选择性）

```bash
# 不装 promptfoo 也可以、直接眼看 evals/evals.json 的 input 拿去问 Claude、对照 expected_behavior
cat evals/evals.json
```

如果要 batch 跑、装 [promptfoo](https://github.com/promptfoo/promptfoo)：

```bash
npm install -g promptfoo
promptfoo eval -c evals/evals.json
```

## 跟其他资源的关系

```
        ┌─────────────────────────────────┐
        │ Stage 3 doc + 练习 1-6 inline │
        │ (学 tool calling 概念) │
        └────────────────┬─────────────────┘
                         │
                         ▼
        ┌─────────────────────────────────┐
        │ examples/stage-3/02-06/ │
        │ (完整可跑 starter + test) │
        └────────────────┬─────────────────┘
                         │ fork template
                         ▼
        ┌─────────────────────────────────┐
        │ 你的 tool-calling agent │
        │ ❓ 卡住了 │
        └────────────────┬─────────────────┘
                         │ 载入
                         ▼
        ┌─────────────────────────────────┐
        │ tool-calling-tutor skill (这个) │
        │ → 4-symptom triage │
        │ → references/ deep dive │
        │ → 路由到 cookbook / Stage 4/7 │
        └─────────────────────────────────┘
```

## 不处理什么

| 情境 | 路 |
|---|---|
| LangChain / LangGraph / CrewAI / Pydantic AI | Stage 4 |
| 写 MCP server / client | `resources/cookbook.zh-Hans.md` 2 |
| Production observability / cost tracking | Stage 7 |
| 一般 prompt engineering | Stage 2 |

## 延伸

- **改 trigger phrases**：在 SKILL.md frontmatter `description` 加你自己常用的触发句
- **加你的 case 到 references/**：debug-flowchart 里开新 Section、把你碰到的 weird case 记下来
- **fork 成你的版本**：这个 skill 设计就是 Stage 5 5.3 的 meta-example、欢迎 fork

## License

跟 repo 一致（MIT）。Skill body 改写、fork、商用都 OK。
