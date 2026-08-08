<div align="right">
  <strong>繁體中文</strong> | <a href="./README.zh-Hans.md">简体中文</a> | <a href="./README.en.md">English</a>
</div>

# 練習 6：Function Schema 設計（bad vs good）

對應 [Stage 3 — Tool Use & Agent 入門](../../../stages/03-tool-use-and-hello-agent.md) 練習 6。
> 🎓 **學習模式**：這份 `starter.py` 是**完整解答**、不是 TODO skeleton。建議用**主動模式**——`mv starter.py starter_reference.py`、看 signature 不看 body、自己重寫一份 `starter.py`、跑 `python test.py` 驗證；卡 20 分鐘再回去對照 reference。完整方法論看 [`docs/HOW_TO_USE.md`](../../../docs/HOW_TO_USE.md)。

> 📚 **想要 chapter-length 深入版？** 本 folder 的 starter 是 70-150 行 illustrative 版、聚焦 `核心 pattern + 兩條 SDK path`，不是進階深度教材。深度教材推薦：
> - [`datawhalechina/hello-agents`](https://github.com/datawhalechina/hello-agents) ⭐ 中文圈最完整、章節式 + 16 種 production 能力。**本練習對應 hello-agents 的 [Extra08 — 如何寫出好的 Skill](https://github.com/datawhalechina/hello-agents/blob/main/Extra-Chapter/Extra08-如何写出好的Skill.md)**
> - [OpenAI Function Calling guide](https://platform.openai.com/docs/guides/function-calling) + [schema 設計 cheatsheet](../../../resources/schema-design-cheatsheet.md)
> - 完整 references 見 [Stage 3 精選 Projects](../../../stages/03-tool-use-and-hello-agent.md#-精選-projects)


## 為什麼這題重要

Schema 是 **prompt 的一部分**、而且是模型做工具選擇時**最依賴**的 prompt。這題用 `starter_bad` 與 `starter_good` 對照同一題：「把攝氏 32 度換成華氏」。

- **Bad schema**：description 太短、參數都 string、沒 required、沒 enum → LLM 容易把溫度轉換丟給 `process_data`
- **Good schema**：用途明確、`value: number`、`unit: enum["celsius", "fahrenheit"]`、required 都列好 → 穩定選到 `convert_temperature`

寫 schema 不要只想「人看得懂」、要想「模型能不能用它排除錯誤工具」。

## 怎麼跑 — 兩條路徑

### Path A（默認、本機免費、4 個 starter）

```bash
pip install -r requirements.txt
ollama pull qwen2.5:3b
ollama serve

python starter_bad.py # 觀察壞 schema 怎麼讓 qwen 挑錯
python starter_good.py # 觀察好 schema 怎麼讓 qwen 挑對
```

預算：**$0**。

### Path B（Anthropic、想看 cloud 高品質）

```bash
pip install -r requirements.txt
export ANTHROPIC_API_KEY=sk-ant-...

python starter_bad_anthropic.py
python starter_good_anthropic.py
```

預算：每次 ≈ **$0.0005**（claude-haiku-4-5、單輪 call）。

## 不花錢驗證程式邏輯（mock-based）

```bash
python test.py # 驗 Path A (Ollama) starter_bad + starter_good
python test_anthropic.py # 驗 Path B (Anthropic) starter_*_anthropic
```

兩條 test 都用 `unittest.mock`、不打真 API、$0/run。每組 test 都直接檢查 schema 結構（good 有 `required` + `enum`、bad 沒有），不只是看 LLM 怎麼選。

## Bad vs Good schema 對照

| 設計面向 | Bad | Good |
|---|---|---|
| Description | "Process data." | "Use only to summarize structured JSON table rows. Do not use for temperature conversion." |
| 參數型別 | 全部 `string` | `number` / `array` / 對應實際型別 |
| Required | 無 | `["value", "unit"]` |
| Enum 收斂 | 無 | `["celsius", "fahrenheit"]` |
| 失敗回傳 | 簡單字串 | 結構化 dict + retry_hint |

## 兩個 path 的觀察重點（教學重點）

**小 model 對 schema 質量的敏感度比大 model 高**——這題在 Ollama 上**反而更有教學意義**：

| 觀察項 | Anthropic Claude haiku | Ollama qwen2.5:3b |
|---|---|---|
| Bad schema 仍能猜對 | 中-高機率 | 低機率（幾乎必錯） |
| Good schema 選對 | 穩定 | 穩定 |
| 差距 | 小 | 大 |

換句話說：**寫 schema 的功夫、在小 model 上能省下換大 model 的成本**。Production 想用便宜 model（qwen / mistral）？schema 必須寫到能上線跑的程度。

## 延伸閱讀

更多 schema 設計規則對照 [`resources/schema-design-cheatsheet.md`](../../../resources/schema-design-cheatsheet.md)：清楚用途、正確型別、必填欄位、enum 收斂、結構化錯誤回傳。

## 延伸

- **故意改壞 good schema**：把一個 enum 拿掉、看 qwen 是否就開始挑錯
- **加第三個工具**：寫一個跟 `convert_temperature` 用途相近但邊界模糊的 tool、看 LLM 怎麼挑
- **接 [`../05-error-handling/`](../05-error-handling/) 的 structured error pattern**：結合 schema 設計 + 錯誤處理、production 級
