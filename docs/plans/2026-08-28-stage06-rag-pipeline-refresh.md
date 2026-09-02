# Stage 06 RAG Pipeline 圖與內容更新計畫

> 狀態：已從獲使用者接受的本地 commit 移植到 `codex/stage06-rag-pipeline-release`，基底為最新 `origin/main@4eec2570`。原分支保留作回溯；本分支只建立 Draft PR，未經使用者同意不合併或清理。

## 目標

這次只處理 Stage 06 的 RAG 流水線，不重寫整章。讀者應該能用一句話說出：

> RAG 先整理資料；問題來時，再找證據、整理證據、帶著來源回答。

同時避免三個常見誤會：

1. RAG 不等於 vector database；BM25、SQL、網站搜尋與 hybrid search 都能提供 retrieval。
2. query rewrite、contextualization、fusion 與 reranking 是可選強化，不是每條 pipeline 都必須打開。
3. 生成答案不是最後一步；來源、拒答、retrieval quality 與 answer quality 都需要檢查。

## 已確認的現況

- `rag-memory-map.{png,en.png,zh-Hans.png}` 是目前可見的總覽圖，已清楚區分 RAG ingestion、RAG query 與 Memory，保留不動。
- `rag-pipeline-overview.{png,en.png,zh-Hans.png}` 是 1920×1080 的舊平面箭頭圖，目前沒有任何 Stage 正文引用。
- `resources/diagrams/locale-variant-prompts.md` 已記錄這組舊圖「未達 house style」，線條 icon、層次與配色不足。
- Stage 06 的「RAG 基礎流水線」已在預設關閉的 `<details>` 中，正適合承載完整圖；重要主線與第一個練習不會因此被藏起來。
- 現行正文已正確說明 retriever 不必使用 vector database，也已保留 GraphRAG、Contextual Retrieval、Hybrid Search、Reranking、query transformations、RAPTOR、DSPy 與 evaluation 等必要概念。

## 2026-08-30 官方事實包

來源優先使用官方文件、canonical repository 與原始論文：

- [LangChain Retrieval](https://docs.langchain.com/oss/python/deepagents/retrieval)：現行教學把常見形狀分成 2-step RAG、Agentic RAG 與 Hybrid RAG；不把所有 RAG 畫成同一條固定 pipeline。
- [LangGraph Agentic RAG](https://docs.langchain.com/oss/python/langgraph/agentic-rag)：agent 可以決定是否 retrieval、評分文件、改寫問題，再生成答案。
- [OpenAI Retrieval](https://developers.openai.com/api/docs/guides/retrieval)：vector store semantic search 是一種 retrieval 方案，可單獨使用或把結果交給模型生成。
- [Qdrant Hybrid Queries](https://qdrant.tech/documentation/search/hybrid-queries/)：dense／sparse 候選可用 RRF／DBSF 等方法融合，也可做多階段查詢；是否增加 reranking 要用自己的 evaluation set 判斷。
- [Weaviate Hybrid Search](https://docs.weaviate.io/weaviate/concepts/search/hybrid-search)：vector search 與 BM25 平行取候選後再融合；reranking 是後續第二階段。
- [Anthropic Contextual Retrieval](https://www.anthropic.com/engineering/contextual-retrieval)：contextual embeddings、contextual BM25 與 reranking 的數字只適用其資料與測試設定，不外推成通用保證。
- [Microsoft GraphRAG](https://github.com/microsoft/graphrag)：MIT 研究參考實作，目前官方 README 標為 largely maintenance mode；保留研究價值，但不能描述為快速演進的一般產品。
- [Ragas metrics](https://docs.ragas.io/en/stable/concepts/metrics/available_metrics/) 與 [vibrantlabsai/ragas](https://github.com/vibrantlabsai/ragas)：用可重跑 dataset／metric 檢查 retrieval 與 answer；metric 仍需人工校準。

查證規則：staging 前重新開啟上述官方頁面；若狀態或 canonical URL 改變，三語正文、freshness config、測試與 CHANGELOG 一起更新，舊 review fingerprint 作廢。

## 新圖的資訊架構

三語圖維持同一個 16:9 bright house style，但不把兩條路硬塞成一條直線。

### 上路：先整理資料（Index lane）

`來源文件 → 解析／清理 → Chunk + metadata →〔可選：補背景〕→ 建立索引 → 可搜尋的資料庫`

- 「建立索引」分成語意索引與關鍵字／結構化索引的視覺提示。
- `Embedding` 是語意索引的一種方法，不畫成所有資料來源都必須經過的唯一入口。
- `Contextualization` 使用虛線或「可選」標籤。

### 下路：問題來了（Query lane）

`使用者問題 →〔可選：改寫／過濾〕→ 多路找候選 →〔可選：融合／Rerank〕→ Evidence Pack → 有來源的答案`

- 多路候選明示 semantic、keyword／BM25、SQL／web 等例子。
- query rewrite、fusion 與 reranking 都標成 optional。
- Evidence Pack 先於 LLM answer，提醒讀者「模型看到的是整理過的證據」。

### 右側／底部：檢查迴圈

`引用來源 → 找不到就說不知道 → 評估 retrieval 與 answer → 記錄結果`

- 用回饋環或 checklist 表現，不畫成每次請求都必然同步跑完的單一路徑。
- 不放固定 chunk size、top-k、模型、價格、排名、GitHub stars 或 benchmark 數字。
- 圖中只使用短標籤；完整定義仍由正文與表格負責。

## 三語文案

### 繁體中文

- 標題：`RAG 有兩條路：先整理資料，再帶著證據回答`
- Lane 1：`先整理資料`；`來源`、`解析／清理`、`Chunk + metadata`、`可選：補背景`、`建立索引`、`可搜尋的資料庫`
- Lane 2：`問題來了`；`問題`、`可選：改寫／過濾`、`多路找候選`、`可選：融合／重新排序`、`證據包`、`有來源的答案`
- Footer：`找不到證據就說不知道 · 檢查 Retrieval 與 Answer · 記錄結果`

### English

- Title: `RAG has two lanes: prepare data, then answer with evidence`
- Lane 1: `Prepare data`; `Sources`, `Parse / clean`, `Chunks + metadata`, `Optional: add context`, `Build indexes`, `Searchable stores`
- Lane 2: `A question arrives`; `Question`, `Optional: rewrite / filter`, `Retrieve candidates`, `Optional: fuse / rerank`, `Evidence pack`, `Answer with citations`
- Footer: `Say “I don't know” without evidence · Evaluate retrieval and answers · Log results`

### 简体中文

- 标题：`RAG 有两条路：先整理数据，再带着证据回答`
- Lane 1：`先整理数据`；`来源`、`解析／清理`、`Chunk + metadata`、`可选：补背景`、`建立索引`、`可搜索的数据仓库`
- Lane 2：`问题来了`；`问题`、`可选：改写／过滤`、`多路找候选`、`可选：融合／重新排序`、`证据包`、`有来源的答案`
- Footer：`找不到证据就说不知道 · 检查 Retrieval 与 Answer · 记录结果`

## 檔案與實作順序

1. 新增 `scripts/test_stage06_rag_pipeline.py`，先鎖定三語引用、圖檔尺寸／不同 hash、兩條 lane、可選步驟、非 vector-only retrieval、來源 URL 與 GraphRAG maintenance caveat。
2. 用 Codex 內建 Image 2.0 重畫：
   - `resources/diagrams/rag-pipeline-overview.png`
   - `resources/diagrams/rag-pipeline-overview.en.png`
   - `resources/diagrams/rag-pipeline-overview.zh-Hans.png`
3. 將各語系圖片放進各自「RAG 基礎流水線」的關閉 `<details>`，位置在兩條路的白話說明後、表格前。
4. 小幅更新三語正文：
   - 把流水線表拆成 ingestion 與 query／answer 兩組，不重複圖上的所有文字。
   - 明示 2-step RAG 是初學基線，Agentic RAG 是「模型決定何時找資料」的進階形狀；Hybrid RAG 是兩者混合，不等於 hybrid search。
   - 更新 Qdrant／Weaviate canonical docs URL。
   - 保留所有現有重要詞、練習、anchors、rowspan 資源評分與 details 狀態。
5. 更新：
   - `scripts/freshness-models.yml`
   - `resources/diagrams/locale-variant-prompts.md`
   - `stages/DESIGN.md`
   - `docs/TESTING_PLAN.md`
   - `CHANGELOG.md`
6. 重新建立 repository freshness snapshot，只有新增／更換 repository URL 時才修改 snapshot。

## 驗收條件

- 不展開選單時，Stage 06 主線字數與目前 ratchet 不增加。
- 展開基礎流水線後，五歲程度的讀者能指出「先整理資料」與「問題來了」兩條路。
- 三張圖各自使用正確語言、相同節點、相同箭頭語意，且三個 binary hash 不同。
- 圖與正文都不暗示 vector database 是唯一 retriever。
- optional 步驟不會被畫成 mandatory。
- `Hybrid RAG` 與 `Hybrid Search` 有清楚區分。
- GraphRAG maintenance mode、Contextual Retrieval scoped result、Ragas canonical owner 與 Qdrant／Weaviate URL 保持正確。
- 舊 anchors、三語 URL 順序、資源五星評分與 `rowspan` 不退化。

## Gate 與提交邊界

依序執行：

1. targeted Stage 06 RAG tests；
2. `git diff --check`；
3. full `python -m pytest scripts -q`；
4. template、strict anchors、anchor slug parity、mirror parity、locale links、Hans／localization、image locale、duplicate repos、freshness、repository snapshot；
5. `python scripts/build-docs-tree.py`；
6. `python -m mkdocs build`；
7. 精確 stage 檔案並記錄 fingerprint；
8. 對穩定 staged diff 執行一次獨立 `code-reviewer`；任何修改都要重跑相關 gate 與 review；
9. 建立單一 follow-up commit，push 並開 Draft PR；不合併、不清理分支。

本分支以獨立 Draft PR 提供檢查；未取得使用者明確批准前，不合併，也不清理分支或 worktree。
