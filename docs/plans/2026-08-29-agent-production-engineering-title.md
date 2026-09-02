# Stage 7 Agent Production Engineering 章名與順序計畫

## 目的

讓讀者分清三件事：**Agent Framework** 是工具箱、**Workflow Graph** 是工作地圖、**Production orchestration** 是把整條路做成可觀測、可復原系統的上線工作；**Graph Engineering** 只保留為新興替代稱呼。同時讓 Stage 7 的章名涵蓋 Harness、Loop、Graph、Multi-Agent、Eval、Observability 與 Guardrail。

## 決定

- Stage 3 保留「工具使用與第一個 Agent Loop」。
- Stage 4 使用「Workflow Graphs & Agent Frameworks」，先教工作地圖，再教實作它的工具箱；不直接改叫 Graph Engineering。
- Stage 7 使用上位名稱：
  - zh-TW：`Stage 7 — Agent Production Engineering：Harness、Loop 與 Graph`
  - en：`Stage 7 — Agent Production Engineering: Harness, Loops, and Graphs`
  - zh-Hans：`Stage 7 — Agent Production Engineering：Harness、Loop 与 Graph`
- `Prompt → Context → Harness → Loop → Graph` 保留為五個控制問題，不再描述成嚴格五層；Harness 可以包含 Agent Loop，Workflow Graph 可以連接 Harness、固定程式、Loop 與人工核准。
- 課程維持「先做出來、再看見結構、最後做穩」：Stage 2 Prompt／Context 初識 → Stage 3 Agent Loop → Stage 4 Framework／Workflow Graph → Stage 5 Harness 實例 → Stage 6 Context 深化 → Stage 7 Production 整合。

## 圖像決定

後續依 IBM、Anthropic、OpenAI Agents SDK 與 Microsoft Agent Framework 的一手定義重查後，原五層圖仍會讓人誤讀成 Harness、Loop、Graph 是嚴格階層或替換世代，因此由 `agent-engineering-control-questions.{png,en.png,zh-Hans.png}` 取代：

- Prompt 與 Context 是進入 Harness 的兩種輸入設計。
- Harness 畫成處理模型、工具、state、log、結果與下一步決定的工作台；權限、sandbox、錯誤與其他 production 細節留在緊接的正文檢查表，避免圖過密。
- Agent Loop 畫在 Harness 內，表示一次 run 的模型／工具／證據迴圈；Loop Engineering 另放在整個長任務尺度，表示 Goal／Action／Observation／Adjustment、預算與停止條件。兩者不能混成同一個框。
- Workflow Graph 畫成連接 Harness run、驗證、返回路線、人工核准與完成狀態的 production route。
- 圖以 Harness 包住 Agent Loop 與上下兩個尺度呈現責任重疊；標題明寫「不是五層」，不暗示五代產品或章節順序。
- 使用 Image 2.0 產生三語 PNG，尺寸與主頁 README 圖同為 `1672×941`。繁中先定稿，英語與簡中以同一母版在地化；逐張以原尺寸人工核對字詞、箭頭、icon、格線與留白。

## 修改邊界

- 更新 Stage 7 三語 H1、五層段落自稱、README／index／PROGRESS／ROADMAP／MkDocs／mdBook、Stage 6 出口、Stage 7 examples 返回名稱、DESIGN、TESTING_PLAN、CHANGELOG 與 regression。
- 保留 Stage 7 的九個核心詞、五份必修閱讀、20 筆五星資源、五題練習、六個預設關閉選單及所有既有 anchor。
- 不改 Stage 檔名、Stage 編號、模型事實、價格或範例程式。因官方定義重查發生在 `2026-08-29`，Stage 7.5 三語 freshness 日期同步更新；六張會誤導責任邊界的舊 PNG 由三張同構 Image 2.0 PNG 取代。
- PR 開出後保持未合併；未經使用者明確同意，不 merge、retarget、刪 branch／worktree 或 prune。

## 驗收

- 三語完整 H1 與所有直接路由一致，compact 首頁卡仍保留附近的 Multi-Agent／production 說明。
- repo 非歷史 Markdown 不再出現舊 Stage 7 完整章名。
- 控制問題圖與正文一致，且不暗示 Harness、Loop、Graph 是互斥產品或替換世代；箭頭不穿字、不壓 icon、不越過無關卡片，同層元素依共同格線對齊。
- strict anchors、anchor slug parity、mirror parity、locale links、Hans、image locale、freshness、reader UX、全量 scripts tests 與三語 MkDocs build 通過。
- 最終 staged diff 經獨立 `code-reviewer` APPROVE；任何 byte 修改都讓舊 ACK 失效。
