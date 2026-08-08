<div align="right">
  <a href="./README.md">繁體中文</a> | <strong>简体中文</strong> | <a href="./README.en.md">English</a>
</div>

# 练习 1：Embeddings + nearest neighbors

对应 [Stage 6 — Memory & RAG](../../../stages/06-memory-rag.zh-Hans.md) 练习 1。
> 🎓 **学习模式**：这份 `starter.py` 是**完整解答**、不是 TODO skeleton。建议用**主动模式**——`mv starter.py starter_reference.py`、看 signature 不看 body、自己重写一份 `starter.py`、跑 `python test.py` 验证；卡 20 分钟再回去对照 reference。完整方法论看 [`docs/HOW_TO_USE.md`](../../../docs/HOW_TO_USE.md)。

> 📚 **想要 chapter-length 深入版？** 本 folder 的 starter 是 illustrative 版、聚焦核心 pattern + 两条 SDK path，不是进阶深度教材。深度教材推荐：
> - [`datawhalechina/hello-agents`](https://github.com/datawhalechina/hello-agents) ⭐ 中文圈最完整、章节式 + 16 种 production 能力。**本练习对应 hello-agents 的 embedding 章节**
> - [sentence-transformers official docs](https://www.sbert.net/) + [MTEB leaderboard](https://huggingface.co/spaces/mteb/leaderboard)（embedding model 评分排行）
> - 完整 references 见 [Stage 6 精选 Projects](../../../stages/06-memory-rag.zh-Hans.md#-精选-projects模板--规范--示例合集)

## 任务

把 100 个句子做 embedding、给一个 query、找出 top-k 最相近的句子。观察 cosine similarity 排序意义。

## 怎么跑 — 两条路径

### Path A（默认、本机免费）

```bash
pip install -r requirements.txt
python starter.py   # 第一次自动下载 model (~80 MB)
```

预算：**$0**。`sentence-transformers/all-MiniLM-L6-v2` 模型在 CPU 跑、约 100 句 < 1 秒。

### Path B（cloud embedding，对照、极便宜）

```bash
pip install -r requirements.txt
export OPENAI_API_KEY=sk-...
python starter_anthropic.py
```

预算：每次 ≈ **$0.00002**（text-embedding-3-small、100 句）。

> 💡 **Anthropic 没提供 embedding API**——官方推荐 [Voyage AI](https://www.voyageai.com/)。这份用 OpenAI 示范（最常见），改 Voyage 只需换 client。

## 不花钱验证程序逻辑

```bash
python test.py             # mock SentenceTransformer、不下载 model
python test_anthropic.py   # mock OpenAI client、验 normalize 逻辑
```

## 核心观念

```python
# 1. Encode → vector
sent_vecs = model.encode(sentences, normalize_embeddings=True)  # 100 × 384 vec
q_vec = model.encode([query], normalize_embeddings=True)[0]      # 384 vec

# 2. Cosine similarity = dot product (因为 normalized)
sims = sent_vecs @ q_vec        # 100 个 similarity score

# 3. Top-k
top_idx = np.argsort(-sims)[:top_k]
```

**为什么 normalize**：normalized vector 的 dot product 直接等于 cosine similarity（范围 [-1, 1]）、不用每次重算 norm。是 vector DB 通用技巧。

## 本机 vs cloud embedding 对照

| 维度 | sentence-transformers (本机) | OpenAI text-embedding-3-small (cloud) |
|---|---|---|
| 维度 | 384 | 1536 |
| 速度（100 句、CPU） | < 1 秒 | 1-2 秒（含网络） |
| 成本 | $0 | $0.00002 / 100 sentences |
| Multilingual | OK（多语版见 `paraphrase-multilingual-MiniLM-L12-v2`） | 强 |
| Long context（>512 token） | 截断 | 强 |
| 一致性（同 input 同 output） | 100% | 99%（API 偶尔微扰） |

**结论**：个人 / 小数据 / 本机实验、用 sentence-transformers 完全够。大量 multilingual / 长文档 / SaaS、用 cloud。

## 常见坑

- **没 normalize**：cosine similarity ≠ dot product、要 `sim = dot(a,b) / (|a||b|)` 自己算
- **Mixed precision**：sentence-transformers 预设 fp32、若用 fp16 量化（省记忆体）相似度会差 1-2%
- **不同模型 vector 不能比**：MiniLM 跟 OpenAI 是两个语意空间、不要把 cosine sim 直接比
- **太短 query**：1-2 字 query embedding 不稳、结果可能跳很远。query 至少要句子

## 想看更好的 embedding？

```bash
# 本机更大 model（精度更好、速度较慢）
# 把 starter.py 的 MODEL_NAME 改成：
#   "sentence-transformers/all-mpnet-base-v2"           # 768 维、accuracy↑
#   "sentence-transformers/paraphrase-multilingual-..." # 多语

# Cloud 高精度
EMBED_MODEL=text-embedding-3-large python starter_anthropic.py   # 3072 维、$$
```

## 延伸

- **改成 BM25 + embedding hybrid**：keyword 跟 semantic 各取优、production 常用
- **加 reranker**：top-k 拿来丢 cross-encoder（`cross-encoder/ms-marco-MiniLM-L-6-v2`）做 reranking、精度大跃进
- **接练习 2 vector DB**：放到 Chroma 里能跑万笔规模、不必每次重 embedding
