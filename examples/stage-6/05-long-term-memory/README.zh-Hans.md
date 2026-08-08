<div align="right">
  <a href="./README.md">繁體中文</a> | <strong>简体中文</strong> | <a href="./README.en.md">English</a>
</div>

# 练习 5：Long-term Memory（跨轮对话记得事情）

对应 [Stage 6 — Memory & RAG](../../../stages/06-memory-rag.zh-Hans.md) 练习 5。
> 🎓 **学习模式**：这份 `starter.py` 是**完整解答**、不是 TODO skeleton。建议用**主动模式**——`mv starter.py starter_reference.py`、看 signature 不看 body、自己重写一份 `starter.py`、跑 `python test.py` 验证；卡 20 分钟再回去对照 reference。完整方法论看 [`docs/HOW_TO_USE.md`](../../../docs/HOW_TO_USE.md)。

> 📚 **想要 chapter-length 深入版？** 本 folder 的 starter 是 illustrative 版、聚焦核心 pattern + 两条 SDK path，不是进阶深度教材。深度教材推荐：
> - [`datawhalechina/hello-agents`](https://github.com/datawhalechina/hello-agents) ⭐ 中文圈最完整、章节式 + 16 种 production 能力。**本练习对应 hello-agents 的 long-term memory 章节**
> - [mem0](https://github.com/mem0ai/mem0)（auto fact extraction + forgetting）+ [Letta / MemGPT](https://github.com/letta-ai/letta)（两级 memory pattern）
> - 完整 references 见 [Stage 6 精选 Projects](../../../stages/06-memory-rag.zh-Hans.md#-精选-projects模板--规范--示例合集)

## 任务

Agent 跨多轮对话记得 user 说过的事情。实作方式：

```
Turn 1: user: "I live in Taipei and prefer Python."
        → maybe_remember_fact() 抓到「I + ...」格式、存进 vector store
Turn 2: user: "What's 2+2?"        → recall 拿不到 relevant memory、纯算术
Turn 3: user: "Recommend a language for me."
        → recall 拿到「prefer Python」、塞进 system prompt → LLM 知道推荐 Python
```

这是 **RAG 的另一面**——retrieve 对象从外部文档变成“对话历史”。

## 怎么跑

### Path A（默认、本机免费）

```bash
pip install -r requirements.txt
ollama pull qwen2.5:3b
ollama serve
python starter.py
```

预算：**$0**。

### Path B（Anthropic）

```bash
pip install -r requirements.txt
export ANTHROPIC_API_KEY=sk-ant-...
python starter_anthropic.py
```

预算：每次 ≈ **$0.001**。

## 不花钱验证程序逻辑

```bash
python test.py             # 5 个 test、mock LLM
python test_anthropic.py   # Anthropic mock
```

## MemoryStore + chat 流程

```python
class MemoryStore:
    def remember(self, fact: str) -> str:   # add to vector store
    def recall(self, query: str) -> list:    # top-k semantic search

def chat(user_msg, memory):
    memories = memory.recall(user_msg, top_k=3)   # 1. 捞相关 memory
    system = f"Relevant memories: {memories}"      # 2. 塞进 system prompt
    return llm.invoke(system + user_msg)           # 3. LLM 看 memory 回答
```

**核心**：memory 不是当“context window history”存（会爆），而是当“semantic search index”存——LLM 只看到相关的几条。

## 跟普通 chat history 的差别

| 维度 | Chat history (in-context) | Vector memory store |
|---|---|---|
| 存放位置 | messages array | ChromaDB |
| 容量 | context window 限制（200k-2M token） | 不限（millions of facts） |
| 跨 session | ❌ session 结束就没 | ✅ persistent |
| 捞出方式 | 所有 history 都进 prompt（吃 token） | top-k semantic search（精准） |
| 适合 | 短对话、单 session | 长 user 关系、多 session、persona |

**Production 用法**：两个都用——recent N 轮当 in-context、超过 N 轮 + 跨 session 用 vector memory。

## 什么是“memory-worthy fact”

这份用 heuristic：user 说“I + verb...”就存。Production 通常更复杂：

1. **Explicit trigger**：user 说“remember that...”
2. **Profile facts**：location / language / role / preferences
3. **Past decisions**：上次 agent 怎么处理某情境
4. **Negative feedback**：“don't suggest X”要存
5. **LLM-extracted**：每轮结束、用 LLM 自己抓 facts（mem0 / Letta / MemGPT 都这么做）

## 两个 path 观察重点

| 观察项 | Anthropic Claude haiku | Ollama qwen2.5:3b |
|---|---|---|
| 把 memory 融进回答 | 自然（cite memory） | 偶尔 ignore memory、用通用答案 |
| “无相关 memory”时不强用 | 守规则 | 较松 |
| 多 memory 整合 | 好 | 中 |

## 常见坑

- **每轮都 add to memory**：vector store 会爆。要有“fact extraction”过滤、只存值得记的
- **没 dedup**：用户多轮重复讲“I live in Taipei”、会存 5 条一样的。要加 dedup 逻辑（similarity > 0.95 视为重复）
- **Forget / update 机制缺失**：用户搬家了“I now live in Tokyo”、旧 memory“Taipei”要怎么处理？production 要支持“supersede”概念
- **没 context size 控制**：recall top-k 太大、context 爆，LLM 也分心
- **隐私 / GDPR**：用户要求删除个人信息、要有 `forget(user_id)` API

## Production-ready 工具

- **[mem0](https://github.com/mem0ai/mem0)**：full memory pipeline、auto-fact-extraction、forgetting、user-scoped namespace
- **[Letta (formerly MemGPT)](https://github.com/letta-ai/letta)**：两级 memory（working memory + archival storage）
- **CrewAI memory**：framework 内建 short / long term memory
- **LangGraph checkpointer + persistent storage**：自带 thread-level memory

## 延伸

- **加 dedup**：`if similarity(new, existing) > 0.95: skip`
- **加 LLM-based fact extraction**：每轮结束用小 LLM 抓 facts、不靠 heuristic
- **加 user_id scoping**：MemoryStore 加 `user_id` filter、不同 user 互不污染
- **接 [mem0](https://github.com/mem0ai/mem0)**：production 不要自己写 memory pipeline、用成熟 lib
