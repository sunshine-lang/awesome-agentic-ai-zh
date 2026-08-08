<div align="right">
  <strong>繁體中文</strong> | <a href="./README.zh-Hans.md">简体中文</a> | <a href="./README.en.md">English</a>
</div>

# 練習 4：完整 RAG 流水線

對應 [Stage 6 — Memory & RAG](../../../stages/06-memory-rag.md) 練習 4。
> 🎓 **學習模式**：這份 `starter.py` 是**完整解答**、不是 TODO skeleton。建議用**主動模式**——`mv starter.py starter_reference.py`、看 signature 不看 body、自己重寫一份 `starter.py`、跑 `python test.py` 驗證；卡 20 分鐘再回去對照 reference。完整方法論看 [`docs/HOW_TO_USE.md`](../../../docs/HOW_TO_USE.md)。

> 📚 **想要 chapter-length 深入版？** 本 folder 的 starter 是 illustrative 版、聚焦核心 pattern + 兩條 SDK path，不是進階深度教材。深度教材推薦：
> - [`datawhalechina/hello-agents`](https://github.com/datawhalechina/hello-agents) ⭐ 中文圈最完整、章節式 + 16 種 production 能力。**本練習對應 hello-agents 的 完整 RAG 流水線章節**
> - [LlamaIndex RAG tutorial](https://docs.llamaindex.ai/en/stable/understanding/rag/) + [LangChain RAG cookbook](https://python.langchain.com/docs/tutorials/rag/)
> - 完整 references 見 [Stage 6 精選 Projects](../../../stages/06-memory-rag.md#-精選-projects範本--spec--範例-collection)


## 任務

把練習 1-3 串起來：

```
doc → chunk_doc → embed → ChromaDB → top_k retrieve → LLM 生答案
```

範例 KB 是公司 onboarding 文件、4 個 section（vacation / remote / expenses / tech stack）。

## 怎麼跑 — 兩條路徑

### Path A（默認、本機免費）

```bash
pip install -r requirements.txt
ollama pull qwen2.5:3b
ollama serve
python starter.py
```

預算：**$0**。

### Path B（Anthropic、想看 cloud 答案質量）

```bash
pip install -r requirements.txt
export ANTHROPIC_API_KEY=sk-ant-...
python starter_anthropic.py
```

預算：每次 ≈ **$0.001**。

## 不花錢驗證程式邏輯

```bash
python test.py # 5 個 test、mock LLM 驗整條 pipeline
python test_anthropic.py # Anthropic mock
```

`test.py` 用 mock LLM 跑整個 RAG pipeline（chunking → retrieval → generation）、確認 prompt 真的帶上 context、確認 generate 拿到 retrieval 結果。

## RAG 4 個步驟

```python
def rag(query, doc):
    collection = build_kb(doc) # 1. chunk + embed + index（一次性）
    contexts = retrieve(collection, q) # 2. top-k 語意搜
    answer = generate(q, contexts) # 3. LLM 看 context 回答
    return {"contexts": contexts, "answer": answer}
```

每一步都有獨立 trade-off：

| 步驟 | 主要 knob | 影響 |
|---|---|---|
| chunk | size / overlap / strategy | retrieval 上限 |
| embed | model 大小 / multilingual | retrieval 精度 |
| retrieve | top_k / metadata filter / reranker | recall vs precision |
| generate | prompt 寫法 / model / temperature | 答案質量 |

## Generate prompt 經典 pattern

```python
prompt = f"""Answer the user's question based ONLY on the context below.
If the context doesn't contain the answer, say "I don't have that information".

Context:
{context_text}

Question: {query}

Answer:"""
```

**3 個關鍵 instruction**：

1. `based ONLY on context` — 防 hallucinate
2. `if doesn't contain → say so` — 給 LLM 退路、不強答
3. Context + Question 順序固定 — 模型訓練偏好這個 layout

## 兩個 path 觀察重點

| 觀察項 | Anthropic Claude haiku | Ollama qwen2.5:3b |
|---|---|---|
| 答案 grounding | 穩（緊扣 context） | 偶爾發散、用知識補答 |
| "I don't have that info" 機率 | 高（守規則） | 低（強答） |
| 答案 fluency | 高 | 中 |
| 多 context 整合 | 好 | 偶爾只看第一個 |
| 速度 | 1-3 秒 | 5-15 秒（CPU） |
| 成本 | $0.001 | $0 |

**production 觀察**：RAG 質量 = retrieval quality × generation quality。**retrieval 漏 = LLM 無中生有；retrieval 對但 LLM 弱 = 答案不準**。Stage 7 production 通常 retrieval 走本機 / 中模型、generation 用 Claude / GPT。

## 常見坑

- **prompt 沒講「only based on context」**：LLM 會自由發揮、用訓練資料補答、不可控
- **`top_k` 設太大**：context 太長、LLM 注意力分散、可能答錯
- **`top_k` 設太小**：context 漏關鍵段、LLM 無法答
- **prompt 把 context 放後面**：LLM 較重視 prompt 開頭、context 應該在 question 之前
- **沒驗證「答錯就 say I don't know」**：production 加 5-10 個「答不出來該說 unknown」的 eval case

## 想看實際在 production 跑的 RAG？

- **Persistent ChromaDB**：`chromadb.PersistentClient(path=...)` 不重新 index
- **Reranker**：retrieve top-20、cross-encoder rerank、留 top-3
- **Citation**：prompt 改成「cite which context section you used」、LLM 標 [chunk_0]
- **Streaming**：`client.chat.completions.create(stream=True)` 邊跑邊印
- **接 LangGraph**：把 retrieve → generate 變 graph node、加 fallback path

## 延伸

- **加 query rewriting**：先讓 LLM 把 user query 改寫成更適合 retrieval 的版本（HyDE pattern）
- **Multi-hop RAG**：第一輪 retrieve 拿到部分答案、用部分答案再 retrieve 補完整
- **接練習 5 long-term memory**：對話 history 也丟進 vector store、跨輪對話記住事情
