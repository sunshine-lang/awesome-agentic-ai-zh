<div align="right">
  <strong>繁體中文</strong> | <a href="./README.zh-Hans.md">简体中文</a> | <a href="./README.en.md">English</a>
</div>

# 練習 5：型別安全 agent（Pydantic AI structured output）

對應 [Stage 4 — Agent Frameworks](../../../stages/04-agent-frameworks.md) 練習 5。
> 🎓 **學習模式**：這份 `starter.py` 是**完整解答**、不是 TODO skeleton。建議用**主動模式**——`mv starter.py starter_reference.py`、看 signature 不看 body、自己重寫一份 `starter.py`、跑 `python test.py` 驗證；卡 20 分鐘再回去對照 reference。完整方法論看 [`docs/HOW_TO_USE.md`](../../../docs/HOW_TO_USE.md)。

> 📚 **想要 chapter-length 深入版？** 本 folder 的 starter 是 illustrative 版、聚焦核心 pattern + 兩條 SDK path，不是進階深度教材。深度教材推薦：
> - [`datawhalechina/hello-agents`](https://github.com/datawhalechina/hello-agents) ⭐ 中文圈最完整、章節式 + 16 種 production 能力。**本練習對應 hello-agents 的 structured output / type-safe 章節**
> - [Pydantic AI 官方 docs](https://ai.pydantic.dev/) + [Instructor library](https://github.com/instructor-ai/instructor)（另一條 typed-output 路線）
> - 完整 references 見 [Stage 4 精選 Projects](../../../stages/04-agent-frameworks.md#-精選-projects)


## 任務

Agent 回問題、**強制** return `AnswerWithConfidence`：

```python
class AnswerWithConfidence(BaseModel):
    answer: str
    confidence: float = Field(ge=0.0, le=1.0) # runtime 驗證 0-1
    sources: list[str]
```

Pydantic AI 把 schema validation 從 prompt 層（Stage 3 練習 6）**提升到 type 層**——LLM 不照 schema、framework 自動 retry。Production team 用這個防 hallucinate。

## 怎麼跑 — 兩條路徑

### Path A（默認、本機免費）

```bash
pip install -r requirements.txt
ollama pull qwen2.5:3b
ollama serve
python starter.py
```

預算：**$0**。但 qwen2.5:3b 可能 retry 多次才產對 schema、總 token 較高。

### Path B（Anthropic、想看 cloud 高品質）

```bash
pip install -r requirements.txt
export ANTHROPIC_API_KEY=sk-ant-...
python starter_anthropic.py
```

預算：每次 ≈ **$0.001**（claude-haiku-4-5、通常一次過、無 retry）。

## 不花錢驗證程式邏輯

```bash
python test.py # Pydantic schema 驗證 + agent 結構
python test_anthropic.py # Path B 載入檢查
```

`test.py` 直接驗 `AnswerWithConfidence` 對非法資料（confidence > 1.0、type 不對、sources 不是 list）的 ValidationError——不需要打 LLM、純 type 層測試。

## 為什麼 type-safe agent 重要

```
Stage 3 練習 6：schema = JSON Schema in prompt
    LLM 看到、但回什麼是 LLM 決定（可能違反）

Stage 4 練習 5：schema = Pydantic model in code
    LLM 違反 → framework 自動 raise → retry / 修
    最終 output 一定 conform（runtime 保證）
```

對 production：

| 需求 | 純 prompt schema | Pydantic AI |
|---|---|---|
| LLM 偶爾少欄位 | 你的下游 code 要 try/except | 自動 retry 直到符合 |
| 型別錯（confidence="high"） | 下游 crash | Pydantic ValidationError、retry |
| 邊界錯（confidence=1.5） | 下游用錯誤值 | 拒絕、retry |
| LLM hallucinate 多餘欄位 | 接收 silently | 預設 ignore（可調 strict） |

**結論**：production agent 必用 type-safe output。Stage 3 練習 6 教 schema 設計、Stage 4 練習 5 教把 schema 變成 runtime contract。

## Pydantic AI 核心觀念

### Agent + output_type

```python
agent = Agent(
    model=...,
    output_type=AnswerWithConfidence, # ← 強制 LLM 回這個 shape
    system_prompt="..."
)
result = agent.run_sync(question)
answer: AnswerWithConfidence = result.output # 已驗證的物件
```

**重點**：framework 在背後把 Pydantic schema 轉成 LLM 的 structured output instruction、執行 validation、failure 時 retry。

### Field constraints

```python
confidence: float = Field(ge=0.0, le=1.0, description="...")
```

`ge` / `le` 是 Pydantic 的 numeric bound。LLM 回 `1.5` 會被 ValidationError 擋下、retry。

### 自動 retry

```python
Agent(..., retries=3) # default 1，可調
```

Pydantic AI 看到 ValidationError、會把錯誤訊息塞回 prompt、要求 LLM 重產。

## 兩個 path 觀察重點

| 觀察項 | Anthropic Claude haiku | Ollama qwen2.5:3b |
|---|---|---|
| 一次產對 schema | 90%+ | 50-70% |
| 平均 retry 次數 | 0-1 | 1-3 |
| confidence 邊界遵守 | 穩 | 偶爾 1.5 / 負值（會被 reject + retry） |
| sources 是 list | 穩 | 偶爾 string、被 reject |
| 總 token 成本 | 低（少 retry） | 高（多 retry） |

**反直覺結論**：Path B（Claude）的實際 token cost **可能比 Path A（qwen）低**——retry 成本累計起來。Production team 算總帳會選大 model。

## 常見坑

- **`output_type` 太複雜**：nested model 深、LLM 難一次寫對。production 建議扁平化、≤5 個 top-level 欄位
- **缺 `description`**：`Field(...)` 沒寫 `description=`、LLM 看不到欄位用途、易誤填
- **`retries=0`**：失敗就 raise、不給 LLM 修的機會。經驗值 `retries=1-3`
- **小 model + 深 nested**：qwen2.5:3b 可能 retry 多次仍不對。換大 model 或扁平 schema

## 想看更聰明的答案？

```bash
MODEL=claude-sonnet-5 python starter_anthropic.py # 一次過機率最高
MODEL=qwen2.5:7b python starter.py # 較大本機 model
```

## 延伸

- **加 tools**：Pydantic AI agent 可以同時有 tools + structured output、`@agent.tool` 裝飾函式
- **stream typed output**：`agent.run_stream(...)` 邊跑邊驗
- **跨 model 比較**：同一個 schema 跑 Claude / GPT / Gemini / 本機 model、看誰最穩
- **接 production**：Pydantic AI 跟 FastAPI 整合很好、output 直接當 API response model
