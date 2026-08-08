<div align="right">
  <a href="./README.md">繁體中文</a> | <strong>简体中文</strong> | <a href="./README.en.md">English</a>
</div>

# 练习 4：完整 RAG 流水线

对应 [Stage 6 — Memory & RAG](../../../stages/06-memory-rag.zh-Hans.md) 练习 4。
> 🎓 **学习模式**：这份 `starter.py` 是**完整解答**、不是 TODO skeleton。建议用**主动模式**——`mv starter.py starter_reference.py`、看 signature 不看 body、自己重写一份 `starter.py`、跑 `python test.py` 验证；卡 20 分钟再回去对照 reference。完整方法论看 [`docs/HOW_TO_USE.md`](../../../docs/HOW_TO_USE.md)。

> 📚 **想要 chapter-length 深入版？** 本 folder 的 starter 是 illustrative 版、聚焦核心 pattern + 两条 SDK path，不是进阶深度教材。深度教材推荐：
> - [`datawhalechina/hello-agents`](https://github.com/datawhalechina/hello-agents) ⭐ 中文圈最完整、章节式 + 16 种 production 能力。**本练习对应 hello-agents 的完整 RAG 流水线章节**
> - [LlamaIndex RAG tutorial](https://docs.llamaindex.ai/en/stable/understanding/rag/) + [LangChain RAG cookbook](https://python.langchain.com/docs/tutorials/rag/)
> - 完整 references 见 [Stage 6 精选 Projects](../../../stages/06-memory-rag.zh-Hans.md#-精选-projects模板--规范--示例合集)

## 任务

把练习 1-3 串起来：

```
doc → chunk_doc → embed → ChromaDB → top_k retrieve → LLM 生答案
```

范例 KB 是公司 onboarding 文档、4 个 section（vacation / remote / expenses / tech stack）。

## 怎么跑 — 两条路径

### Path A（默认、本机免费）

```bash
pip install -r requirements.txt
ollama pull qwen2.5:3b
ollama serve
python starter.py
```

预算：**$0**。

### Path B（Anthropic、想看 cloud 答案质量）

```bash
pip install -r requirements.txt
export ANTHROPIC_API_KEY=sk-ant-...
python starter_anthropic.py
```

预算：每次 ≈ **$0.001**。

## 不花钱验证程序逻辑

```bash
python test.py             # 5 个 test、mock LLM 验整条 pipeline
python test_anthropic.py   # Anthropic mock
```

## RAG 4 个步骤

```python
def rag(query, doc):
    collection = build_kb(doc)           # 1. chunk + embed + index（一次性）
    contexts = retrieve(collection, q)    # 2. top-k 语意搜
    answer = generate(q, contexts)        # 3. LLM 看 context 回答
    return {"contexts": contexts, "answer": answer}
```

每一步都有独立 trade-off：

| 步骤 | 主要 knob | 影响 |
|---|---|---|
| chunk | size / overlap / strategy | retrieval 上限 |
| embed | model 大小 / multilingual | retrieval 精度 |
| retrieve | top_k / metadata filter / reranker | recall vs precision |
| generate | prompt 写法 / model / temperature | 答案质量 |

## Generate prompt 经典 pattern

```python
prompt = f"""Answer the user's question based ONLY on the context below.
If the context doesn't contain the answer, say "I don't have that information".

Context:
{context_text}

Question: {query}

Answer:"""
```

**3 个关键 instruction**：

1. `based ONLY on context` — 防 hallucinate
2. `if doesn't contain → say so` — 给 LLM 退路、不强答
3. Context + Question 顺序固定 — 模型训练偏好这个 layout

## 两个 path 观察重点

| 观察项 | Anthropic Claude haiku | Ollama qwen2.5:3b |
|---|---|---|
| 答案 grounding | 稳（紧扣 context） | 偶尔发散、用知识补答 |
| "I don't have that info" 机率 | 高（守规则） | 低（强答） |
| 答案 fluency | 高 | 中 |
| 多 context 整合 | 好 | 偶尔只看第一个 |
| 速度 | 1-3 秒 | 5-15 秒（CPU） |
| 成本 | $0.001 | $0 |

**production 观察**：RAG 质量 = retrieval quality × generation quality。**retrieval 漏 = LLM 无中生有；retrieval 对但 LLM 弱 = 答案不准**。Stage 7 production 通常 retrieval 走本机 / 中模型、generation 用 Claude / GPT。

## 常见坑

- **prompt 没讲“only based on context”**：LLM 会自由发挥、用训练数据补答、不可控
- **`top_k` 设太大**：context 太长、LLM 注意力分散、可能答错
- **`top_k` 设太小**：context 漏关键段、LLM 无法答
- **prompt 把 context 放后面**：LLM 较重视 prompt 开头、context 应该在 question 之前
- **没验证“答错就 say I don't know”**：production 加 5-10 个“答不出来该说 unknown”的 eval case

## 想看实际在 production 跑的 RAG？

- **Persistent ChromaDB**：`chromadb.PersistentClient(path=...)` 不重新 index
- **Reranker**：retrieve top-20、cross-encoder rerank、留 top-3
- **Citation**：prompt 改成“cite which context section you used”、LLM 标 [chunk_0]
- **Streaming**：`client.chat.completions.create(stream=True)` 边跑边印
- **接 LangGraph**：把 retrieve → generate 变 graph node、加 fallback path

## 延伸

- **加 query rewriting**：先让 LLM 把 user query 改写成更适合 retrieval 的版本（HyDE pattern）
- **Multi-hop RAG**：第一轮 retrieve 拿到部分答案、用部分答案再 retrieve 补完整
- **接练习 5 long-term memory**：对话 history 也丢进 vector store、跨轮对话记住事情
