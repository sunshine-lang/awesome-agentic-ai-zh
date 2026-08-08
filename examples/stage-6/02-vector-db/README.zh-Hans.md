<div align="right">
  <a href="./README.md">繁體中文</a> | <strong>简体中文</strong> | <a href="./README.en.md">English</a>
</div>

# 练习 2：Vector DB（ChromaDB）+ semantic vs keyword

对应 [Stage 6 — Memory & RAG](../../../stages/06-memory-rag.zh-Hans.md) 练习 2。
> 🎓 **学习模式**：这份 `starter.py` 是**完整解答**、不是 TODO skeleton。建议用**主动模式**——`mv starter.py starter_reference.py`、看 signature 不看 body、自己重写一份 `starter.py`、跑 `python test.py` 验证；卡 20 分钟再回去对照 reference。完整方法论看 [`docs/HOW_TO_USE.md`](../../../docs/HOW_TO_USE.md)。

> 📚 **想要 chapter-length 深入版？** 本 folder 的 starter 是 illustrative 版、聚焦核心 pattern + 两条 SDK path，不是进阶深度教材。深度教材推荐：
> - [`datawhalechina/hello-agents`](https://github.com/datawhalechina/hello-agents) ⭐ 中文圈最完整、章节式 + 16 种 production 能力。**本练习对应 hello-agents 的 vector store 章节**
> - [ChromaDB official tutorial](https://docs.trychroma.com/) + [Qdrant / Weaviate / Pinecone 对照](https://github.com/zilliztech/VectorDBBench)（production scale benchmark）
> - 完整 references 见 [Stage 6 精选 Projects](../../../stages/06-memory-rag.zh-Hans.md#-精选-projects模板--规范--示例合集)

## 任务

把 8 个 doc 存进 Chroma、用同一个 query 比较 semantic（vector）跟 keyword（substring）两种 retrieval。

## 怎么跑

```bash
pip install -r requirements.txt
python starter.py   # 第一次自动下载 embedding model
```

预算：**$0**。Chroma in-memory mode、跑完就 release。

```bash
python test.py             # 5 个 test、验 index/query/ranking
python test_anthropic.py   # Path B concept demo（同 starter）
```

## Vector DB 为什么 vs 为什么不

| 情境 | List comprehension + cosine | ChromaDB |
|---|---|---|
| < 100 doc | ✅ 简单够用 | overkill |
| 100-10K doc | 慢（每次 query 都 re-embed all） | ✅ 持久 + index |
| 10K+ doc | 不行 | ✅（或考虑 production 用的 Qdrant / Weaviate） |
| Persistence | ❌ 每次重 embed | ✅ SQLite 后端 |
| Filter / metadata | 自己写 | ✅ where clause |
| Hybrid search | 自己写 | ✅ 有 BM25 + vector |

**经验法则**：练习用 in-memory（`EphemeralClient`）、production 用 `PersistentClient(path=...)`。

## Semantic vs Keyword 对照

```
Query: "where to drink good coffee in Asian cities"

📝 Keyword (substring) → 漏 doc 3
    因为 query 没有「coffee」精确字串

🔍 Semantic (vector) → 抓到 doc 3
    "Coffee shops in Taipei often serve pour-over..."
    语意对齐、不靠字面
```

| 维度 | Keyword search | Semantic search (vector) |
|---|---|---|
| 同义词 | 漏（"car" 跟 "auto" 不同） | 抓得到 |
| 换字面 | 漏 | 抓得到 |
| 拼字错 | 漏 | 抓得到（小错） |
| 精确专有名词 | 强 | 偶尔混淆 |
| 否定（NOT） | 简单 | 困难（embedding 不擅长） |
| 速度 | 快 | 中（要 embed query） |
| Production 用法 | BM25 + vector **hybrid** | 同左 |

**Production 结论**：两条路都要、**hybrid search** 是 best practice。Chroma 0.4+ 内建 BM25 + vector hybrid。

## Chroma 核心 API

```python
client = chromadb.EphemeralClient()    # in-memory；PersistentClient(path=...) 用磁盘
embed_fn = embedding_functions.SentenceTransformerEmbeddingFunction(model_name="...")
collection = client.get_or_create_collection(name="demo", embedding_function=embed_fn)

collection.add(ids=[...], documents=[...], metadatas=[{"category": "..."}, ...])
collection.query(query_texts=[query], n_results=3, where={"category": "tech"})
collection.upsert(...)
collection.delete(ids=[...])
```

## 常见坑

- **重复 id `.add()`**：Chroma raise；用 `.upsert()` 或先检查 `.get()["ids"]`
- **每次 query 重 build collection**：别这样！`PersistentClient` 持久化、只 index 一次
- **`n_results` 太大**：Chroma 没返回 reranker、k 太大就会吃到 noise。经验值 3-10
- **Filter 用错**：`where={"category": "tech"}` 是 metadata filter、`where_document={"$contains": "..."}` 是 doc 内容 filter
- **embedding function 一致性**：index 时用 model A、query 时用 model B、retrieval 会错。Chroma 把 embedding_function 绑在 collection 上避免

## 想看实际在 production 跑的选择？

```bash
collection = build_collection(path="./chroma_db")   # 持久化
# 或 cloud embedding：
embed_fn = embedding_functions.OpenAIEmbeddingFunction(api_key=..., model_name="text-embedding-3-small")
```

## 延伸

- **加 metadata filter**：`collection.query(query_texts=[q], where={"category": "food"})`
- **Hybrid search**：BM25 + vector
- **Swap to Qdrant / Weaviate**：production scale
- **接练习 4**：完整 RAG pipeline 用同一个 collection
