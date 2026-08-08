# Stage 0 — 基礎準備（Foundations）

> **繁體中文** | [简体中文](./00-foundations.zh-Hans.md) | [English](./00-foundations.en.md)

⏱ **時間估算**：1-2 週（約 5-15 小時，已具備可跳過）

> 💡 **看不懂某個詞**？翻 [`resources/glossary.md`](../resources/glossary.md) 查 30 秒再回來。Stage 0 還不會碰太多 jargon，但接下來幾 stage 會。
> 🗺️ **想先看 agent 的全景地圖**（為什麼有的 agent 在 terminal、有的在 Telegram、有的在 Jetson 板子）？→ [`resources/agent-paradigms.md`](../resources/agent-paradigms.md)（5 種 agent 型態，10 min 讀完）

> 📋 **本章組成**：跳過條件檢查 → 環境設定步驟 → 進入 Stage 1（foundation stage，無「學習目標 / 進入條件」框架）  
> 🔑 **關鍵名詞**：見 [`resources/glossary.md`](../resources/glossary.md)（每 stage 用到的術語都收在那裡）

## 何時可以跳過這個階段

如果你能：

- 寫一個會呼叫公開 API 並解析 JSON 回應的 Python 函式
- 用 git 做 clone、commit、push，並處理基本的 merge 衝突
- 在自己的作業系統上使用命令列（cd、ls、mkdir、執行 script）
- 看懂 YAML / JSON 檔案

→ **直接跳到 [Stage 1](01-llm-basics.md)**。

如果做不到，就把這個階段走完。不要跳——後面每個階段都會預設你已經會這些。

## 📌 學習目標

- 寫 Python：函式、類別、async/await 基本用法
- 用 git：clone、branch、commit、push、基本衝突處理
- 用 REST API：發 GET/POST、解析 JSON、處理 auth header
- 讀寫 YAML 跟 JSON

## 🛠 動手練習

- **練習：Python** — 寫一個 Python script 呼叫 https://api.github.com/users/torvalds 並印出 follower 數量
- **練習：git** — clone 任何一個公開 repo，做一次 commit，push 到自己的 fork
- **練習：CLI** — 用命令列建幾個資料夾跟檔案（macOS / Linux：`mkdir project && cd project && mkdir src tests docs`；Windows PowerShell：`New-Item -ItemType Directory -Path project,project\src,project\tests,project\docs`）、執行 Python script、把輸出存到檔案
- **練習：YAML** — 用 Python 讀一個 `.yaml` 設定檔，改一個值，再寫回去
- **練習：API auth** — 去 [github.com/settings/tokens](https://github.com/settings/tokens) 產生一個 personal access token（給最少權限：`read:user`），呼叫 `https://api.github.com/user` 需 auth 的 endpoint，看 401（無 token）vs 200（帶 token）的差別。注意：production agent 一定會用到 API auth，所以這一題要做

## 🎯 精選資源（不是完整 Project，只是學習素材）

按 5 個 prereq 主題分類、18 個資源一張表搞定。**挑入口看「適合誰」、想深入點連結看 repo / 網站**。

| 主題 | 資源 | 適合誰 | 為什麼推薦 / 備註 |
|---|---|---|---|
| **Python** | [Python Crash Course](https://github.com/ehmatthes/pcc_3e) | 從零學 Python | 書 + 練習；書付費、練習免費 |
| | [Real Python](https://realpython.com/) | 已會基礎、想深入單一主題 | 高品質免費文章、Google 搜尋常出現 |
| | [Corey Schafer YouTube](https://www.youtube.com/c/Coreyms) | 喜歡英文影片學習者 | 從基礎到進階、講解清楚 |
| | [Boot.dev](https://www.boot.dev/) | 想要互動式練習 | 部分免費、付費含完整 backend 路線 |
| | [runoob.com Python 教學](https://www.runoob.com/python3/python3-tutorial.html) | 中文讀者快速查語法 | 中文 Python 入門參考 |
| **Git** | [Pro Git book](https://git-scm.com/book/en/v2) | 想徹底搞懂 Git | 免費完整參考書、官方推薦 |
| | [Atlassian Git Tutorials](https://www.atlassian.com/git/tutorials) | 想學 workflow（branch / merge / rebase）| 以 workflow 為主、視覺化好 |
| | [Oh Shit, Git!?!](https://ohshitgit.com/) | 出包時急救 | 「我搞砸了 X、怎麼救」cheat sheet |
| | [git-flight-rules](https://github.com/k88hudson/git-flight-rules) | 想要更深的急救手冊 | 高人氣 cheat sheet、覆蓋場景更廣 |
| **CLI / Shell** | [The Art of Command Line](https://github.com/jlevy/the-art-of-command-line) | 想系統性學命令列 | ★ 160k+、多語言版、新手到進階都涵蓋 |
| | [Learn Shell](https://www.learnshell.org/) | 喜歡互動式練習 | 互動式 Bash 教學、瀏覽器內跑 |
| | [explainshell.com](https://explainshell.com/) | debug shell 指令 | 把任何 shell 指令拆解講解（debug 救星）|
| **REST API** | [MDN — HTTP](https://developer.mozilla.org/en-US/docs/Web/HTTP) | 想搞懂 HTTP 協定 | Mozilla 維護的 web 平台參考文件 |
| | [Postman Learning Center](https://learning.postman.com/) | 用 GUI 探索 API | API 探索工具、視覺化好 |
| | [HTTPie](https://github.com/httpie/cli) | 偏好 CLI、`curl` 太醜 | 比 `curl` 友善的命令列 HTTP client |
| **YAML / JSON** | [YAML 官網](https://yaml.org/) | 需要查語法規格 | YAML 規格文件 |
| | [JSON crash course](https://www.json.org/json-en.html) | 第一次接觸 JSON | 官方快速指南 |
| | [jq](https://github.com/jqlang/jq) | 命令列處理 JSON | agent 工作中常用、處理 API response 必備 |

## 為什麼有這個階段

大多數「AI agent」教學都預設你已經會這些。如果你還沒，就會在奇怪的地方卡關（tool 需要 async、設定檔是 YAML、SDK 安裝要用 git）。在這裡花一週的投資，可以省下後面 10 週以上的挫折。

---

> ✅ **走完 Stage 0 了？** 接下來 [**Stage 1 — LLM 基礎**](01-llm-basics.md) 會用 5-8 小時帶你做完第一次 LLM API 呼叫、認識 token / context window / temperature，以及用 per-token 計價估算實際任務成本。**繼續往下走 →**
