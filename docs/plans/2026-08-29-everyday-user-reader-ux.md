# 日常使用者路線漸進式重整 Implementation Plan

**Goal:** 讓沒有寫程式經驗的讀者，先安全完成一個日常 AI 任務，再分清聊天介面、App／Connector、CLI Agent 與 Local LLM Runtime；不再把它們誤認成同一條升級階梯。

**Architecture:** 保留三語檔名與主要舊錨點，移除線性 Tier 階梯，改成「按工作選四扇門」。繁中先定稿，英語與簡中只做語意鏡像。必要閱讀、精選工具及 15 筆資源表直接可見；帳號／資料／費用、CLI／本地進階步驟、替代方案／排錯預設收合。

**Stack boundary:** 在 `codex/everyday-user-reader-ux-stack` 工作，base 固定為知識工作者 PR #179 的 head `2d6500d6`。只開 stacked PR；未經使用者明確同意，不合併、不 retarget、不清 branch／worktree。

## 一、已確認的問題

1. 三語頁面目前都是 `0` 個 `<details>`，第一次打開就看到完整工具牆。
2. `Tier 0 → Desktop → CLI → Local LLM` 把四種不同身分誤寫成同一條升級路線。
3. 必修閱讀在大量工具之後才出現；繁中／簡中有三筆，英文只有兩筆。
4. `runoob.com` 是一般首頁，不是 ChatGPT 官方教學；舊 OpenAI／Anthropic prompt URL 已重新導向開發者文件。
5. 頁面保存 `103k+`、`115k+`、`138k+` 等 GitHub stars，以及半小時、半天、1–2 天等易失真估算。
6. `Perplexity 每個答案都有引用`、`Claude 比較不瞎掰`、`ChatGPT 生態最廣`、`Claude Code 最容易上手` 都是沒有足夠證據的比較結論。
7. `Claude Desktop 是 MCP 入口` 已過度簡化：Anthropic 現行把 remote connectors 與本機 desktop extensions 分開，支援 surface 也不同。
8. Ollama 與 LM Studio 都能使用雲端功能；只寫「本地 = 資料一定不出機器」不正確。
9. 第一個隱私示例使用醫療／法律／財務筆記，會把高風險任務放在初學者入口。
10. CLI Agent 的 permission、diff、preview、sandbox 與人工批准沒有在第一個相關動作前說清楚。

## 二、讀者可見主線

不展開任何選單時，依序看到：

1. `📌 這條路幫你做什麼`：不寫 code 也能開始；AI 先產生草稿，人最後檢查。
2. `🎯 四個學習目標`：寫清楚要求、分清四種入口、保護資料、查證輸出。
3. `🧩 九個核心詞`：**Prompt**、**Source**、**Private Data**、**Hallucination**、**Human Review**、**App／Connector**、**CLI Agent**、**Local LLM／Runtime**、**Approval Gate**。
4. `🛠 第一個練習`：直接複製一個 prompt，整理虛構訊息；輸出 `Draft | Facts copied | Needs confirmation`，不得猜測、不得傳送。
5. `🚪 按工作選四扇門`：聊天介面、App／Connector、CLI Agent、本地模型執行環境。
6. `📚 必修閱讀`：六個官方入口，先學 prompt、資料與 permission。
7. `⭐ 精選 Projects 與學習資源`：15 筆可見、五星編輯評分、真正 HTML `rowspan`。
8. `✅ 完成條件與下一站`：能說出四種入口的差別，知道何時要人工確認，再選 Stage 2、Track A 或知識工作者路線。

## 三、三個預設收合區

1. `帳號、資料、權限與費用`：方案／地區／workspace 可用性、資料政策、連接外部服務前要看的 permission。
2. `CLI Agent 與本地模型進階步驟`：preview／dry-run、限定資料夾、diff、approval；Ollama local-only 與 LM Studio offline 邊界。
3. `更多流程、替代方案與疑難排解`：語言練習、週記、批次檔案、常見錯誤；不把醫療／法律／投資決策當新手模板。

全部使用 `<details markdown="1">`，不得有 `open`。必要安全警告不得只存在於收合區。

## 四、四扇門的固定定義

| 入口 | 五歲也懂的說法 | 正確邊界 |
|---|---|---|
| **Chat surface** | 打開一個對話框，請它先幫你寫草稿 | 適合單次詢問；仍要查來源，不能假設回答正確 |
| **App／Connector** | 幫聊天工具開一扇通往其他服務的門 | 能讀或操作什麼取決於產品、方案、地區、workspace 與原服務權限；寫入動作先確認 |
| **CLI Agent** | 在終端機裡工作的助手 | 可能讀寫檔案、執行命令；先限定資料夾、看 preview／diff、再人工批准 |
| **Local LLM／Runtime** | 模型在自己的電腦裡跑 | Runtime 不是聊天 App，也不是 CLI Agent；啟用 cloud model、web search 或 cloud API 後，相關資料仍會離開裝置 |

固定句：**這四扇門不是等級。需要哪一扇才開哪一扇。**

## 五、第一個可複製練習

輸入使用虛構訊息，例如：

```text
來源訊息：
「小安說星期五前會把海報草稿交給小美。活動日期是 9 月 12 日。訊息沒有寫交付時間。」

請幫我寫一段簡短提醒。只能使用來源訊息裡的事實，不要猜。
請輸出：
1. Draft
2. Facts copied
3. Needs confirmation

不要替我傳送訊息。
```

完成檢查：人要逐項對照 Source；沒有時間就放進 `Needs confirmation`，不能自行補上。

## 六、必修閱讀（直接可見）

1. OpenAI — Prompt engineering best practices for ChatGPT
   `https://help.openai.com/en/articles/10032626-how-do-i-prompt-chatgpt-effectively`
2. Anthropic — Get started with Claude
   `https://support.claude.com/en/articles/8114491-get-started-with-claude`
3. OpenAI — Apps in ChatGPT
   `https://help.openai.com/en/articles/11487775-connectors-in`
4. Anthropic — When to use desktop and web connectors
   `https://support.claude.com/en/articles/11725091-when-to-use-desktop-and-web-connectors`
5. Google — Gemini Apps Privacy Hub
   `https://support.google.com/gemini/answer/13594961?hl=en`
6. Ollama FAQ
   `https://docs.ollama.com/faq`

## 七、15 筆可見資源表

固定 rowgroups：`4／4／4／2／1`。

### 聊天介面（4）

1. `https://claude.ai` ⭐⭐⭐⭐⭐
2. `https://chatgpt.com` ⭐⭐⭐⭐⭐
3. `https://gemini.google.com` ⭐⭐⭐⭐
4. `https://perplexity.ai` ⭐⭐⭐⭐

### 官方入門與安全指南（4）

5. `https://help.openai.com/en/articles/10032626-how-do-i-prompt-chatgpt-effectively` ⭐⭐⭐⭐⭐
6. `https://support.claude.com/en/articles/8114491-get-started-with-claude` ⭐⭐⭐⭐⭐
7. `https://help.openai.com/en/articles/11487775-connectors-in` ⭐⭐⭐⭐⭐
8. `https://support.google.com/gemini/answer/13594961?hl=en` ⭐⭐⭐⭐⭐

### CLI Agent（4）

9. `https://github.com/anthropics/claude-code` ⭐⭐⭐⭐⭐
10. `https://github.com/openai/codex` ⭐⭐⭐⭐⭐
11. `https://github.com/anomalyco/opencode` ⭐⭐⭐⭐⭐
12. `https://github.com/google-gemini/gemini-cli` ⭐⭐⭐⭐

### Local LLM Runtime（2）

13. `https://github.com/ollama/ollama` ⭐⭐⭐⭐⭐
14. `https://lmstudio.ai/` ⭐⭐⭐⭐

### Prompt 素材（1）

15. `https://github.com/f/prompts.chat` ⭐⭐⭐⭐

每列固定欄位：`分類｜入口／專案｜它是什麼｜適合做什麼｜狀態／授權｜先知道的限制｜編輯評分`。分類以每個 `<tbody>` 第一列真正 `scope="rowgroup" rowspan="N"` 合併，不重複、不留空格。

## 八、官方事實包（2026-08-29 UTC）

- OpenAI 已將 ChatGPT connectors 改稱 Apps；功能、方案、地區、workspace 與管理員設定會影響可用性。來源：Apps in ChatGPT。
- Anthropic 的 remote connectors 適合雲端服務；desktop extensions 適合本機 app／檔案，支援 surface 不同。來源：Anthropic connector guide。
- Google Connected Apps 可能涉及 email、files、events、location 與敏感資料；使用前要看 activity、review 與第三方政策。來源：Gemini Privacy Hub。
- Ollama 本機 run 不會被 Ollama 看見，但 cloud models 與 web search 是雲端功能；需要純 local 時使用官方 local-only 設定。來源：Ollama FAQ／Cloud docs。
- LM Studio 已下載的 local model、chat、文件與 local server 可以 offline；model search、download、update、cloud models 與 web search 仍需要網路或雲端處理。來源：LM Studio offline／privacy docs。
- Gemini CLI 的修改工具會要求批准並顯示 command／diff；sandbox 降低風險但不消除風險。來源：Gemini CLI tools／sandbox docs。
- OpenCode 可以對 edit、bash、external directory 設 ask／allow／deny；provider 要透過 API key、OAuth 或環境設定連接，不能簡化成「self-host 就能免費使用任何模型」。來源：OpenCode agents／providers docs。

## 九、禁止重新出現的說法

- GitHub stars 數字與固定安裝／學習時間。
- `90% 的場景`、`免付費`、`最容易上手`、`最大生態`、`較不瞎掰`、`每個答案都有引用`。
- `Claude Desktop 是 MCP 的入口` 或 `Desktop App 是 Web App 的升級版`。
- `本地模型一定離線／一定不送雲`。
- `81+ MCP server` 等固定 catalog 數量。
- 把醫療、法律或投資判斷當成新手的第一個工作流。
- `runoob.com` 與已重新導向的舊 prompt-engineering URL。

## 十、深連結與三語契約

保留下列語意入口的 compatibility anchors，放在最接近的新 heading 旁：使用情境、起步選層、精選 Projects、必修閱讀、可建立流程、層級建議、社群備註；英語與簡中使用各自既有 slug。三語保持相同 URL、順序、評分、狀態、授權、安全限制、三個 details 與 `2026-08-29` freshness marker。

## 十一、測試與執行順序

1. 先在 `scripts/test_role_paths.py` 與 `scripts/reader-ux-pages.yml` 寫會失敗的 everyday-user contract。
2. 只改繁中 canonical，跑 targeted test、reader-UX、anchors。
3. 繁中定形後更新英語與簡中，逐欄做語意鏡像。
4. 更新 `branches/DESIGN.md`、`docs/TESTING_PLAN.md` 與 `CHANGELOG.md`。
5. 依序執行：`git diff --check`、reader UX、strict anchors、slug parity、mirror、locale links、Hans、image locale、duplicate repos、strict freshness、targeted pytest、full `scripts` pytest、docs tree、三語 MkDocs build。
6. 逐檔 stage，凍結 staged path count 與 `git write-tree` fingerprint。
7. 對最終 staged diff 執行一次獨立 `code-reviewer`；任何 byte 改變使 ACK 失效。
8. Commit：`content(everyday): make the safe starting path clear`。
9. Push 並開 stacked PR；等所有 checks 綠燈，保持未合併供使用者檢查。

## 十二、驗收標準

- 不展開 details 也能完成第一題並選對入口。
- 讀者能用一句話分清 Chat surface、App／Connector、CLI Agent、Local LLM Runtime。
- 九個核心詞在第一題前粗體定義，沒有因精簡而消失。
- 必修閱讀、精選 Projects、15 筆資源與五星評分全部直接可見。
- 資源表為 `4／4／4／2／1` 五組真正合併欄位。
- 三語恰有三個預設關閉 details，URL／數字／權限／安全說法一致。
- 沒有 stars、固定時間、舊 catalog 數量、無來源排名、過度隱私承諾或高風險新手流程。
- Stacked PR clean、checks 綠燈、獨立 reviewer ACK，且未自行合併。
