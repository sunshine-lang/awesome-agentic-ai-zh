# 知識工作者路徑漸進式重整計畫

**目標：** 讓沒有開發背景的知識工作者先完成一個安全、可核對的小任務，再理解何時用聊天服務、App／Connector、MCP Server 或工作流自動化；不再把四者混成同一種工具。

**基準：** 以 `codex/researcher-reader-ux-stack` 的 commit `59c9afe8be54ee73d5f5dddbf372f629cddcf0d0` 為底，使用 `codex/knowledge-worker-reader-ux-stack`。本層不合併、不 retarget、不清理前序 branch／worktree。

## 已確認的內容判斷（2026-08-29 UTC）

1. ChatGPT 已在 2025-12-17 把 Connectors 改稱 Apps；App 可搜尋、同步或執行動作，但功能仍受方案、地區、管理員與來源系統權限控制。
2. Claude 把 Skills、Connectors 與 Plugins 放入同一目錄，但三者不是同義詞；Connector 仍要經過驗證與組織設定。
3. Google Workspace 與 Microsoft 365 的 connected app／connector 都不會繞過使用者原有權限，管理員仍可限制或停用。
4. 官方 MCP Registry 仍是 Preview；它驗證 namespace 與 metadata，不替 server 程式碼做完整安全審查。
5. Flowise repo 已封存，不再放進現行推薦清單。n8n 使用 Sustainable Use License；Dify 與 LobeHub 都有額外商用條件，不能誤寫成普通 Apache／MIT。

## 讀者不展開選單時看到的順序

1. `📌` 這條路解決什麼。
2. `🎯` 四個學習目標。
3. `🧩` 九個粗體核心詞：Source、Action Item、Knowledge Base、Private Data、Human Review、App／Connector、MCP Server、Workflow Automation、Approval Gate。
4. `🛠` 使用虛構會議紀錄的第一個練習；輸出 Decision、Action Item、Owner、Due date、Source sentence、Needs confirmation，資料不足時不可猜。
5. `📚` 三個入口：一次性聊天、組織核准的 App／Connector、重複性工作流。
6. `📖` 六份官方必讀。
7. `⭐` 15 筆精選服務、repo 與官方目錄，固定 `4／4／2／3／2` 五組，真正 `rowspan`、五星編輯評分、狀態、授權／服務型態與限制。
8. `✅` 完成檢查與下一站。

## 預設收合

- 帳號、方案、資料與成本檢查。
- Email、會議、weekly report、產品經理與知識庫的進階流程。
- 替代方案與排錯。

所有 `<details markdown="1">` 預設關閉。必讀、精選資源、安全警告與第一個練習不得收合。

## 資源表固定形狀

| 分組 | 數量 | 收錄 |
|---|---:|---|
| AI 工作空間與組織內 App | 4 | ChatGPT Apps、Claude directory、Gemini Connected Apps、Microsoft 365 Copilot connectors |
| 工作流自動化 | 4 | n8n、Make、Power Automate、Zapier |
| 視覺化 AI builder | 2 | Langflow、Dify |
| 知識工作空間 | 3 | Khoj、LobeHub、AnythingLLM |
| Skill 與協定入口 | 2 | obra/superpowers、官方 MCP Registry |

不保存 GitHub stars、整合數量、固定安裝時間或「最強／首選」結論。自架不等於所有資料都留在本機；真正資料流還要看模型供應商、connector、telemetry 與部署設定。

## 驗證與發布

1. 先新增 reader-UX 與 role-path 失敗測試，再重寫繁中。
2. 繁中定義與事實穩定後，同步英語與簡中；三語 URL、順序、評分、狀態、授權、限制與日期完全一致。
3. 保留舊 heading 的 compatibility anchors，並讓 anchor 落在語意相符的新位置。
4. 執行 role tests、reader-UX、strict anchors、mirror parity、locale links、freshness、完整 `python -m pytest scripts -q`、docs tree 與 MkDocs build。
5. 穩定 staged diff 經獨立 reviewer，任何修改都使 ack 失效。
6. 逐檔 stage、commit、push，建立 base 為 `codex/researcher-reader-ux-stack` 的 stacked PR；等待使用者明確同意前不合併。
