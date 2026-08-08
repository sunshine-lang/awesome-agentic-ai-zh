# How to use this curriculum — 主動 vs 被動學習

> 給每個動手練習 folder 的 meta-instruction。如果你跳過這一頁、會把這套教材當 reference book 讀完、學到大概 60%。讀完這一頁、用對方法、學到 100%。

## 真實問題

每個練習 folder（譬如 `examples/stage-3/03-react-from-scratch/`）裡都有一個 **`starter.py`**——它**長得像 starter、其實是完整解答**。

如果你：

```bash
git clone ... && cd examples/stage-3/03-react-from-scratch
cat starter.py             # 看完整解答
python starter.py          # 跑通
python test.py             # 全 pass
```

你會以為「學會了」、其實**沒寫過一行 code**。

這是這份教材的最大設計缺陷。下面講怎麼繞過它。

## 兩種學習模式

### 🟢 主動模式（推薦、學到 100%）

**步驟**：

```bash
cd examples/stage-3/03-react-from-scratch/

# 1. 讀 README、了解這題在做什麼、預期 input / output
cat README.md

# 2. 把 starter.py 改名（藏起來、等下對照用）
mv starter.py starter_reference.py

# 3. 看 starter_reference.py 的「imports + function signatures」、不看 function body
head -50 starter_reference.py

# 4. 自己寫一個新的 starter.py、function body 自己想
$EDITOR starter.py

# 5. 跑 test.py、看自己寫的能不能 pass
python test.py

# 6. 卡住超過 20 分鐘？才打開 starter_reference.py 對照
diff starter.py starter_reference.py

# 7. 寫完一輪後、看 README 的 punchline + common pitfalls、跟你的 trial 對照
```

**重點**：

- **看 signature、不看 body**。imports / TOOLS_SPEC / function names + arg types 可以看；裡面怎麼實作要自己想。
- **卡 20 分鐘是健康的**。卡 1 小時也健康。卡 3 小時就回去看 reference、然後**默寫一遍**。
- **test 通過 ≠ 學會**。test 通過代表 logic 對；學會代表你**講得出**為什麼這 13 行 ReAct loop 必要、為什麼 `tool_call_id` 要配對、為什麼要 `max_iter`。

### 🟡 被動模式（reference book、學到 60%）

**步驟**：

```bash
cd examples/stage-3/03-react-from-scratch/
cat README.md
cat starter.py        # 讀完整解答、理解每一行
python test.py        # 確認跑得起來
```

**何時用**：

- 你**之前寫過 ReAct loop**、現在只是想看本 curriculum 是怎麼寫的、做 cross-reference
- 你在**找 pitfall reference**（譬如 production 出 bug、想看 curriculum 提過沒）
- 你是**講課老師**、要快速看完整套教材然後挑題目給學生

被動模式適合**已經會了**的人複習、不適合**沒寫過**的人入門。

## 為什麼這份教材的 starter.py 是完整解答（不是 TODO skeleton）

短答：**v1 階段、為了快速 ship 完整可跑版本**。

長答：完整 starter.py 有 3 個好處（給維護者）：

1. **test 直接 pass**——確認 framework 整合沒漏東西
2. **不會 outdated**——隨 framework 升級可以馬上 fix（不必同步維護 template）
3. **新手 onboard 快**——把 repo clone 下來就能跑、降低裝環境 friction

但對學習者來講有 1 個大缺點：**容易被誤用成抄答案**。所以這份 HOW_TO_USE 文件存在、提醒你**自己改名、自己重寫**。

**v2 規劃**（未開始）：把 starter.py 分裂成 `starter_template.py`（TODO skeleton）+ `starter_reference.py`（完整解答）、test 預設打 template、學生 fill in、卡住才看 reference。這需要重做 ~20 個 folder、預計 v2 在 [`docs/TESTING_PLAN.md`](TESTING_PLAN.md) 之後排期。

## 每個 stage 怎麼用這份教材

| Stage | 主動模式時間預算 | 被動模式時間預算 |
|---|---|---|
| Stage 3（tool use + ReAct） | 5-8 hr（每練習 1-1.5 hr） | 1-2 hr（讀過去） |
| Stage 4（agent frameworks） | 8-12 hr（每練習 2 hr） | 2-3 hr |
| Stage 6（RAG + memory） | 8-12 hr | 2-3 hr |
| Stage 7（production） | 10-15 hr | 3-4 hr |

**主動模式時間是被動的 4-5 倍**——這就是「卡住 + 修通」的時間成本、也是真學會的成本。如果你只有 1 週時間、選 1-2 個你覺得最重要的練習走**主動模式**、其他**被動模式**過。

## 我自己（curriculum 作者）跑驗證踩到的 bug

跑 verification（2026-05-13）發現我寫的 starter / test **本身有 6 個 bug**：

1. **operator precedence** in test (`and` 比 `or` 緊)
2. **ChromaDB collection name length** (Chroma 1.0 break、'kb' 太短)
3. **EphemeralClient state leak** 跨 test fixture
4. **i18n key mismatch**（test 用中文 query、starter db 用英文 key）
5. **Smolagents `@tool` 要求 Google-style docstring `Args:`** 區塊
6. **Python 3.14 + tiktoken/regex 無 wheel**（CrewAI 在 3.14 裝不起來）

**這對你的意義**：當你做主動模式、卡住時，**有可能不是你錯、是教材有 bug**。提 issue 上來、我會修。Bug 修在 commit [50c3bf8](https://github.com/WenyuChiou/awesome-agentic-ai-zh/commit/50c3bf8)。

## 練習 checkpoint（每練習做完問自己這 3 題）

不要光看 starter.py 過去、問自己：

1. **「為什麼」**：這份 code 為什麼這樣寫、不那樣寫？（譬如 ReAct loop 為什麼必須把 assistant response 接回 messages？沒接會怎樣？）
2. **「拿掉 X 會怎樣」**：拿掉 `max_iter`、拿掉 `tool_call_id`、拿掉 `cache_control`，runtime 會出什麼問題？
3. **「production 怎麼改」**：這份 demo code 上 production 還缺什麼？（提示：observability / eval / retry / auth 通常都缺）

回答得出來 = 真學會了。回答不出來 = 只是讀過。

## 進入條件：每個 Stage 開始前自我檢查

不要直接從 Stage 4 開始——除非 Stage 3 的 6 個練習你**每個都用主動模式寫過 1 次**。

- **Stage 4** 前：必須能不查文件寫出 13 行 ReAct loop（Stage 3 練習 3）
- **Stage 6** 前：必須能講出為什麼 schema 要寫 enum + required（Stage 3 練習 6）
- **Stage 7** 前：必須會用 mock 寫 LLM unit test（Stage 3 練習 5 + 任何 Stage 4）

沒過 checkpoint 直接跳級、後面會卡住、回頭重做更慢。

## 如果你卡住

順序：

1. **再讀一次 README 的 pitfall + punchline** — 80% 的卡住來自漏看某個關鍵設計
2. **打開 `examples/stage-5/tool-calling-tutor/` skill**（裝進 Claude Code）— tool calling 相關的卡住、4-symptom triage 帶你診斷
3. **看 `starter_reference.py`**（你改名藏起來的那個）— 對照你寫的差別、找出哪裡邏輯漏
4. **看 GitHub issue** 有沒有人問過
5. **開 issue** — 帶上你的 code + 你看到的錯誤、我會回

絕對不要：抄 `starter_reference.py` 就走。沒寫過 = 沒學會。

---

## 給維護者：v2 path

v2 把 starter.py 拆成 template + reference 的計畫：

- 每個 folder 多 2 個檔案：`starter_template.py`（TODO skeleton）+ `starter_reference.py`（answer）
- `test.py` 預設打 `starter_template.py`、有 env var 切到 reference 對照
- README 多 1 段 "Learning mode" 解釋
- 約 20 個 folder × 3 file changes = 60 個檔案

如果有人想接 v2、歡迎 PR。對應 issue / branch 等決定後開出來。
