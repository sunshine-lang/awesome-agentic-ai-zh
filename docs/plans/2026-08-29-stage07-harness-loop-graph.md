# Stage 7 Harness → Loop → Graph 教學順序計畫

## 要解決的問題

目前五層圖已列出 Prompt、Context、Harness、Loop、Graph，但章名只突出 Loop／Graph，容易讓初學者以為 Loop 是新版 Harness，或以為 Stage 4 的 Agent Framework 就等於 Graph Engineering。

## 讀者第一遍要看懂的順序

1. **Agent Production Engineering** 是本章上位名稱；它不是跨供應商的正式標準名稱。
2. **Harness** 管一次執行：工具、權限、sandbox、錯誤、狀態與紀錄。
3. **Loop Engineering** 管反覆工作：目標、動作、觀察、驗證、記憶、預算、停止與人工升級。
4. **Graph Engineering** 管完整路線：節點、分支、平行、回程、checkpoint 與人工核准。
5. Harness、Loop、Graph 可能由同一套程式實作；這是責任邊界，不是假裝它們永遠是三個產品。

## 本層修改

- Stage 7 三語章名改為 `Agent Production Engineering：Harness、Loop 與 Graph`，並同步直接寫出完整章名的導覽與返回連結。
- 保留現有九個核心詞、五份必修閱讀、Harness 八元件、五題練習、20 筆精選資源與五星評分。
- 新增可見的 Harness／Loop／Graph 邊界表，以及一張三語同構亮色圖。
- 新增三種 loop 的白話區分：程式迴圈、單次執行內的 Agent Loop、Loop Engineering。
- 明說模型變強可能淘汰某個 workaround，但不會自動淘汰權限、安全、log、eval 或 recovery 邊界。
- 更新 DESIGN、圖稿重產 prompt、reader UX 與內容／路由 regression。

## 官方查證基準

- IBM Loop Engineering：`Goal → Action → Observation → Adjustment`，並要求可驗證停止條件、成本與人工監督。
- OpenAI Harness Engineering：環境、工具、可讀文件、機械式規則與 feedback loop 讓 Agent 能可靠工作。
- Anthropic Managed Agents：session、harness、sandbox 可分開替換；harness 會呼叫模型並路由工具。
- Anthropic Harness Design：模型能力提升後，某些補丁可逐項移除；安全與品質邊界仍要靠 eval 驗證。

統一查核日期為 `2026-08-29`。只引用官方工程文章來支持可用性與工程定位；新興詞彙不冒充所有供應商共同標準。

## 圖稿不變量

- 左到右只畫 `Harness → Loop → Graph`，不畫成版本升級或互相淘汰。
- Harness 卡片必須包含「一次執行」；Loop 必須包含「反覆驗證」；Graph 必須包含「完整路線」。
- Loop 包住 Harness 的一次執行；Graph 安排一個或多個 Loop／節點與人工核准。
- 不放模型名、版本、價格、benchmark、GitHub stars 或「官方／非官方」badge。
- 三語各自生成本地化圖檔，不在圖片中混用繁中、簡中與英文。

## 發布邊界

本層疊在 Cookbook PR #186 上，獨立 commit／PR，未經使用者明確同意不合併、不刪 branch、不清理 worktree。Stage 7.5 的 Model–Harness Fit 圖另開下一層 PR。
