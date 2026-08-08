<div align="right">
  <a href="./README.md">繁體中文</a> | <a href="./README.zh-Hans.md">简体中文</a> | <strong>English</strong>
</div>

# Exercise 3: Chunking Comparison (fixed / paragraph / heading-aware)

Pairs with [Stage 6 — Memory & RAG](../../../stages/06-memory-rag.en.md) Exercise 3.
> 🎓 **How to use this**: `starter.py` is the **complete solution**, not a TODO skeleton. The active approach works better — `mv starter.py starter_reference.py`, read the signatures but not the bodies, write your own `starter.py` from scratch, then run `python test.py` to check it; if you are stuck for 20 minutes, go back and compare against the reference. Full methodology in [`docs/HOW_TO_USE.md`](../../../docs/HOW_TO_USE.md).

> 📚 **Want the chapter-length version?** The starter in this folder is an illustrative build focused on the core pattern plus two SDK paths — it is not in-depth teaching material. Recommended for depth:
> - [`datawhalechina/hello-agents`](https://github.com/datawhalechina/hello-agents) ⭐ The most complete chapter-based course in Chinese — 16 production capabilities. **This exercise maps to hello-agents' RAG chunking chapter**
> - [LangChain RecursiveCharacterTextSplitter docs](https://python.langchain.com/docs/how_to/recursive_text_splitter/) + [LlamaIndex SemanticSplitter](https://docs.llamaindex.ai/en/stable/api_reference/node_parsers/semantic_splitter/)
> - Full references in [Stage 6 Curated Projects](../../../stages/06-memory-rag.en.md#-featured-projects-templates--specs--example-collections)

## Task

Same document → 3 chunking strategies → 5 queries → see which yields the best retrieval.

| Strategy | How | Good for |
|---|---|---|
| **fixed-length** | N chars per chunk + overlap | Plain text (logs, chat history) |
| **paragraph** | Split on double newline | Prose / articles |
| **heading-aware** | Split on `# / ##` | Structured docs (README, wiki, specs) |

## How to run

```bash
pip install -r requirements.txt
python starter.py   # first run downloads embedding model
```

Budget: **$0** (fully local).

```bash
python test.py             # 4 tests for chunking logic
python test_anthropic.py   # Path B concept demo
```

## Strategy comparison

### Fixed-length

```python
def chunk_fixed(text, chunk_size=200, overlap=40):
    # 200 chars per chunk, 40-char overlap
    # Simple but splits sentences
```

Pros: 1-line implementation, works on any text. Cons: breaks sentences mid-flow.

### Paragraph-based

```python
def chunk_paragraphs(text):
    return text.split("\n\n")
```

Pros: preserves semantic units. Cons: paragraphs vary in length (10 chars vs 500 chars), throws off embeddings.

### Heading-aware

```python
def chunk_headings(text):
    return re.split(r"\n(?=#{1,3} )", text)
```

Pros: each chunk includes its heading (extra retrieval signal), structure preserved. Cons: requires markdown / structured docs — won't work on plain text or PDFs without headings.

## Observations

For query "How much does the MRT cost?":

- **fixed-length** may cut "EasyCard is the universal payment. A single ride..." across chunks (MRT cost detached from context)
- **paragraph** retrieves the full Transit paragraph including NT$20-65
- **heading-aware** retrieves the entire `## Transit` section — embedding for "MRT cost" lands closer to the heading

For "What food can I try?":

- **fixed-length** hits a chunk containing Food info but with bad boundaries
- **paragraph** hits one of the Food paragraphs
- **heading-aware** returns the whole `## Food` section — Shilin / dan bing / coffee info in one shot

**Punchline**: **chunking strategy caps RAG quality** — content the retriever misses, no LLM can answer.

## Production considerations

- **Chunk size**: empirically 200-1000 chars (depends on embedding model's token limit; MiniLM is 512)
- **Overlap**: 10-20% on fixed-length to avoid splitting sentences
- **Reranker**: retrieve top-20, rerank with a cross-encoder, keep top-5 — big precision boost
- **Metadata**: tag each chunk `{"section": "Transit"}` for filter queries
- **Hybrid hierarchy**: split by heading first, then sub-split each section by fixed-length

## Common pitfalls

- **Chunks too large**: embedding averages out details, retrieval misses precise paragraphs
- **Chunks too small**: insufficient context, LLM can't form holistic answers — need more top-k
- **Testing on toy queries**: production queries are different. **Always validate chunking with real queries**
- **PDF chunking with markdown logic**: PDFs have columns / footnotes / tables — use `pdfplumber` or `unstructured`
- **CJK text byte-sliced mid-character**: UTF-8 byte slice breaks multi-byte chars. Use character-level slicing

## Smarter chunking options

- **`LangChain RecursiveCharacterTextSplitter`**: tries `\n\n`, then `\n`, then `.`, then char — auto-fallback
- **`LlamaIndex SemanticSplitter`**: uses embeddings to find semantic boundaries (most accurate, slowest)
- **`unstructured`**: full pipeline for PDF / DOCX / HTML

## Extensions

- **Grid-search chunk_size**: across 5 queries, find the size with highest mean similarity
- **Metadata filter**: tag chunks by section, query "only in Food section"
- **Plug into Exercise 4**: feed retrieval results to an LLM for full RAG
