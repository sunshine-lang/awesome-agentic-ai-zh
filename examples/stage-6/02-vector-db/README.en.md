<div align="right">
  <a href="./README.md">繁體中文</a> | <a href="./README.zh-Hans.md">简体中文</a> | <strong>English</strong>
</div>

# Exercise 2: Vector DB (ChromaDB) + semantic vs keyword

Pairs with [Stage 6 — Memory & RAG](../../../stages/06-memory-rag.en.md) Exercise 2.
> 🎓 **How to use this**: `starter.py` is the **complete solution**, not a TODO skeleton. The active approach works better — `mv starter.py starter_reference.py`, read the signatures but not the bodies, write your own `starter.py` from scratch, then run `python test.py` to check it; if you are stuck for 20 minutes, go back and compare against the reference. Full methodology in [`docs/HOW_TO_USE.md`](../../../docs/HOW_TO_USE.md).

> 📚 **Want the chapter-length version?** The starter in this folder is an illustrative build focused on the core pattern plus two SDK paths — it is not in-depth teaching material. Recommended for depth:
> - [`datawhalechina/hello-agents`](https://github.com/datawhalechina/hello-agents) ⭐ The most complete chapter-based course in Chinese — 16 production capabilities. **This exercise maps to hello-agents' vector store chapter**
> - [ChromaDB official tutorial](https://docs.trychroma.com/) + [Qdrant / Weaviate / Pinecone comparison](https://github.com/zilliztech/VectorDBBench) (production-scale benchmark)
> - Full references in [Stage 6 Curated Projects](../../../stages/06-memory-rag.en.md#-featured-projects-templates--specs--example-collections)

## Task

Index 8 docs into Chroma; compare semantic (vector) vs keyword (substring) retrieval on the same query.

## How to run

```bash
pip install -r requirements.txt
python starter.py   # auto-downloads embedding model on first run
```

Budget: **$0**. In-memory mode; released after process exits.

```bash
python test.py             # 5 tests for index/query/ranking
python test_anthropic.py   # Path B concept demo (same as starter)
```

## When to use a vector DB

| Scenario | List + cosine | ChromaDB |
|---|---|---|
| < 100 docs | ✅ enough | overkill |
| 100-10K docs | Slow (re-embed each query) | ✅ persistent + indexed |
| 10K+ docs | No | ✅ (consider Qdrant / Weaviate at huge scale) |
| Persistence | Re-embed | ✅ SQLite backend |
| Filter / metadata | DIY | ✅ where clause |
| Hybrid search | DIY | ✅ built-in BM25 + vector |

**Rule of thumb**: experimentation = `EphemeralClient`; production = `PersistentClient(path=...)`.

## Semantic vs keyword

```
Query: "where to drink good coffee in Asian cities"

📝 Keyword (substring) → misses doc 3
    Query doesn't have the exact word "coffee"

🔍 Semantic (vector) → hits doc 3
    "Coffee shops in Taipei often serve pour-over..."
    Semantic alignment, not literal match
```

| Dimension | Keyword | Semantic |
|---|---|---|
| Synonyms ("car" vs "auto") | Miss | Catch |
| Rephrasings | Miss | Catch |
| Typos | Miss | Catch (small) |
| Exact proper nouns | Strong | Occasionally confused |
| Negation (NOT) | Easy | Hard (embeddings don't grok negation) |
| Speed | Fast | Medium (need to embed the query) |
| Production | BM25 + vector **hybrid** | Same |

**Production takeaway**: use both — hybrid search is best practice. Chroma 0.4+ has BM25 + vector built in.

## Chroma API

```python
client = chromadb.EphemeralClient()    # in-memory; PersistentClient(path=...) for disk
embed_fn = embedding_functions.SentenceTransformerEmbeddingFunction(model_name="...")
collection = client.get_or_create_collection(name="demo", embedding_function=embed_fn)

collection.add(ids=[...], documents=[...], metadatas=[{"category": "..."}, ...])
collection.query(query_texts=[query], n_results=3, where={"category": "tech"})
collection.upsert(...)
collection.delete(ids=[...])
```

## Common pitfalls

- **Duplicate ids in `.add()`**: raises. Use `.upsert()` or check `.get()["ids"]` first
- **Rebuilding the collection each query**: don't! `PersistentClient` indexes once
- **`n_results` too high**: no reranker — large k pulls in noise. 3-10 typically
- **Filter confusion**: `where={"category": "tech"}` is metadata; `where_document={"$contains": "..."}` is content
- **Inconsistent embedding function**: indexing with model A and querying with model B breaks retrieval. Chroma binds embedding_function to the collection to prevent this

## Production-ready alternatives

```bash
# Persistent
collection = build_collection(path="./chroma_db")

# Cloud embeddings (higher quality)
embed_fn = embedding_functions.OpenAIEmbeddingFunction(api_key=..., model_name="text-embedding-3-small")
```

## Extensions

- **Metadata filter**: `collection.query(query_texts=[q], where={"category": "food"})`
- **Hybrid search**: BM25 + vector via Chroma 0.4+ or external `rank_bm25`
- **Swap to Qdrant / Weaviate** at production scale
- **Plug into Exercise 4**: full RAG pipeline reuses this collection
