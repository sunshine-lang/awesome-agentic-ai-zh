<div align="right">
  <a href="./README.md">繁體中文</a> | <strong>简体中文</strong> | <a href="./README.en.md">English</a>
</div>

# 练习 3：Chunking 对照（fixed / paragraph / heading-aware）

对应 [Stage 6 — Memory & RAG](../../../stages/06-memory-rag.zh-Hans.md) 练习 3。
> 🎓 **学习模式**：这份 `starter.py` 是**完整解答**、不是 TODO skeleton。建议用**主动模式**——`mv starter.py starter_reference.py`、看 signature 不看 body、自己重写一份 `starter.py`、跑 `python test.py` 验证；卡 20 分钟再回去对照 reference。完整方法论看 [`docs/HOW_TO_USE.md`](../../../docs/HOW_TO_USE.md)。

> 📚 **想要 chapter-length 深入版？** 本 folder 的 starter 是 illustrative 版、聚焦核心 pattern + 两条 SDK path，不是进阶深度教材。深度教材推荐：
> - [`datawhalechina/hello-agents`](https://github.com/datawhalechina/hello-agents) ⭐ 中文圈最完整、章节式 + 16 种 production 能力。**本练习对应 hello-agents 的 RAG chunking 章节**
> - [LangChain RecursiveCharacterTextSplitter docs](https://python.langchain.com/docs/how_to/recursive_text_splitter/) + [LlamaIndex SemanticSplitter](https://docs.llamaindex.ai/en/stable/api_reference/node_parsers/semantic_splitter/)
> - 完整 references 见 [Stage 6 精选 Projects](../../../stages/06-memory-rag.zh-Hans.md#-精选-projects模板--规范--示例合集)

## 任务

同一份文档 → 3 种切法、跑 5 个 query、看哪种切法 retrieval 最准。

| 策略 | 怎么切 | 适合 |
|---|---|---|
| **fixed-length** | 每 N 字一段、有 overlap | 纯文字（log / chat history） |
| **paragraph** | 双 newline 为界 | 散文 / 文章 |
| **heading-aware** | 看 `# / ##` 切 | structured doc（README / wiki / spec） |

## 怎么跑

```bash
pip install -r requirements.txt
python starter.py   # 第一次自动下载 embedding model
```

预算：**$0**（纯本机）。

```bash
python test.py             # 4 个 test、验 chunking 逻辑
python test_anthropic.py   # Path B concept demo
```

## 3 种策略对照

### Fixed-length

```python
def chunk_fixed(text, chunk_size=200, overlap=40):
    # 每 200 字一块、40 字重叠
```

**优点**：实作 1 行、适用所有文字；**缺点**：切到一半句子、语意被打断

### Paragraph-based

```python
def chunk_paragraphs(text):
    return text.split("\n\n")
```

**优点**：保语意完整；**缺点**：段落长度不一（10 字 vs 500 字、embedding 不准）

### Heading-aware

```python
def chunk_headings(text):
    return re.split(r"\n(?=#{1,3} )", text)
```

**优点**：每个 chunk 含 heading、structure 清楚；**缺点**：要 markdown / structured doc

## 观察重点

对 query“How much does the MRT cost?”：

- **fixed-length**：可能切到“...EasyCard is the universal payment. A single ride...”（MRT cost 跟前后 chunk 切开了）
- **paragraph**：抓到完整 Transit 段、含 NT$20-65
- **heading-aware**：抓到完整 ## Transit section、含 heading“Transit”（embedding 对“MRT cost”的相似度更高）

对 query“What food can I try?”：

- **fixed-length**：抓到含 Food section 的 chunk、但可能 boundary 不对
- **paragraph**：抓到 Food 内某个段落
- **heading-aware**：抓到 `## Food` 整段、含 Shilin / dan bing / coffee 信息一次到位

**punchline**：**chunking 策略决定 RAG 上限**——retrieval 抓不到的内容、再强的 LLM 也答不出。

## Production 额外考量

- **Chunk size**：经验 200-1000 字（取决于 embedding model 的 token limit）
- **Overlap**：fixed-length 用 10-20% overlap、避免句子被切坏
- **Reranker**：捞 top-20、丢 cross-encoder rerank 留 top-5、精度大跃进
- **Metadata**：每个 chunk 加 `{"section": "Transit"}` 等 metadata、query 时可 filter
- **混合策略**：先 heading 切大块、每块内再 fixed-length 切小块（两层 hierarchy）

## 常见坑

- **Chunk 太大**：embedding 平均掉细节、retrieval 抓不到精准段落
- **Chunk 太小**：context 不足、LLM 看不到 holistic 答案
- **没测过真实 query**：开发时用 toy query 验、production query 完全不同
- **PDF chunking 直接套 markdown 逻辑**：PDF 有 column / footnote / table、要用 `pdfplumber` 或 `unstructured`
- **CJK 文本切到一半字符**：UTF-8 byte slice 会切坏 multi-byte char

## 想看更聪明的 chunking？

- **`LangChain RecursiveCharacterTextSplitter`**：自动 fallback
- **`LlamaIndex SemanticSplitter`**：用 embedding 找语意断点切
- **`unstructured`**：对 PDF / DOCX / HTML 全套处理

## 延伸

- **改变 chunk_size 跑 grid search**：对 5 个 query、看哪个 size 平均 sim 最高
- **加 metadata filter**：每个 chunk 标 section、query 时可指定“只在 Food section 搜”
- **接练习 4 完整 RAG**：选好 chunking 策略后、丢给 LLM 生答案
