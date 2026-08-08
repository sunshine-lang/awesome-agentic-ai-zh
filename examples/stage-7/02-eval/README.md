<div align="right">
  <strong>繁體中文</strong> | <a href="./README.zh-Hans.md">简体中文</a> | <a href="./README.en.md">English</a>
</div>

# 練習 2：Eval Pipeline（"pytest for LLMs"）

對應 [Stage 7 — Multi-Agent & Production](../../../stages/07-multi-agent-production.md) 練習 2。
> 🎓 **學習模式**：這份 `starter.py` 是**完整解答**、不是 TODO skeleton。建議用**主動模式**——`mv starter.py starter_reference.py`、看 signature 不看 body、自己重寫一份 `starter.py`、跑 `python test.py` 驗證；卡 20 分鐘再回去對照 reference。完整方法論看 [`docs/HOW_TO_USE.md`](../../../docs/HOW_TO_USE.md)。

> 📚 **想要 chapter-length 深入版？** 本 folder 的 starter 是 illustrative 版、聚焦核心 pattern + 兩條 SDK path，不是進階深度教材。深度教材推薦：
> - [`datawhalechina/hello-agents`](https://github.com/datawhalechina/hello-agents) ⭐ 中文圈最完整、章節式 + 16 種 production 能力。**本練習對應 hello-agents 的 eval / regression testing 章節**
> - [promptfoo](https://github.com/promptfoo/promptfoo) + [Anthropic Workbench Evals](https://console.anthropic.com/workbench/evals)（官方 eval UI）
> - 完整 references 見 [Stage 7 精選 Projects](../../../stages/07-multi-agent-production.md#-精選-projects範本--sdk--工具-collection)


## 任務

為 production agent 寫 5 個 eval case、跑 baseline、追 regression。**Production 沒 eval = 沒 confidence ship**。

5 個 case 涵蓋：
1-2. **Math**（deterministic 答案）
3-4. **Geography**（factual recall）

5. **Grounding test**（fake word「flrgglemerk」、agent 應該說 "don't know"、不該 hallucinate）

兩種 evaluator：

| 方式 | 何時用 | 成本 |
|---|---|---|
| **string match** | 答案有 deterministic substring（數字、專有名詞） | $0、極快 |
| **LLM-as-judge** | 開放式答案（recommendation / explanation） | 多 1 個 LLM call |

## 怎麼跑

### Path A（默認、本機免費）

```bash
pip install -r requirements.txt
ollama pull qwen2.5:3b
ollama serve
python starter.py
```

### Path B（Anthropic）

```bash
pip install -r requirements.txt
export ANTHROPIC_API_KEY=sk-ant-...
python starter_anthropic.py
```

預算：5 cases × 1 call ≈ **$0.003**（Claude haiku）。

## 不花錢驗證程式邏輯

```bash
python test.py # 7 個 test：evaluator + run_eval aggregation
python test_anthropic.py # Anthropic agent mock
```

## Eval 的 production 價值

```
Without eval：
   PR merge → 上 prod → user 抱怨 → 你才知道 LLM 行為變了

With eval：
   PR → run eval → pass_rate 從 95% 掉到 70% → block merge
   → 找出哪些 case regression → 改 prompt / model / retry → recover
```

**Eval pin baseline**：第一次跑、記住 pass_rate（譬如 80%）；每次 ship 前確認沒掉。

## 經典 eval 結構

```python
eval_cases = [
    {"id": ..., "input": ..., "expected_substring": ..., "instruction": ...},
    ...
]

def run_eval(cases, agent_fn, eval_fn):
    results = [...]
    return {"pass_count": ..., "pass_rate": ...}
```

**3 個關鍵**：

1. **`id` 必要**：方便定位是哪一題 regress
2. **`expected_substring` 而非 full match**：LLM 答案有 variability、用 substring 才穩
3. **Eval function 跟 agent 分離**：可以換不同 evaluator 對同一份 cases

## LLM-as-judge 何時用

| 情境 | 用 substring | 用 LLM-as-judge |
|---|---|---|
| 「2+2=?」答案 | ✅ "4" | overkill |
| 「summarize this article」 | ❌ 沒固定 substring | ✅ |
| 「is the tone professional?」 | ❌ | ✅ |
| 「count tokens used」 | ✅ 用 regex | overkill |

**Production 經驗**：80% case 用 substring + heuristic、20% 用 LLM-as-judge（cost / latency 較高）。

## Production-ready tools

- **[promptfoo](https://github.com/promptfoo/promptfoo)**：YAML config + CLI runner + diff report
- **[Anthropic Workbench eval](https://console.anthropic.com/workbench/evals)**：官方 eval UI、prompts as code
- **[LangSmith](https://smith.langchain.com/)**：LangChain ecosystem 的 eval + observability 一條龍
- **[Weights & Biases Weave](https://wandb.ai/site/weave)**：generic LLM eval framework
- **[Braintrust](https://www.braintrust.dev/)**：跨 model / version A/B、上線部署用的 dashboards

## 兩個 path 觀察重點

| 觀察項 | Anthropic Claude | Ollama qwen2.5:3b |
|---|---|---|
| math case pass rate | ~100% | ~80% |
| geo case pass rate | ~100% | ~70-90% |
| grounding test (flrgglemerk) | 守規則說 don't know | 偶爾編答案 |
| 整體 pass_rate | 95-100% | 70-85% |

**結論**：production 應該針對「自家 use case」建 50-200 case 的 eval set、看自家任務上的 pass rate、決定該用哪個 model。

## 常見坑

- **Eval set 太小（< 10 cases）**：noise 高、看不出 regression
- **Eval set 太靠近 training data**：model 死背、實際 user query 表現完全不同
- **沒 grounding test**：production agent hallucination 是最致命的 bug、必須有「答不出來該說 unknown」case
- **`expected_substring` 太嚴**：寫「The capital is Tokyo, Japan.」當 expected、LLM 寫「Tokyo」會 fail。應該只匹配關鍵字
- **LLM-as-judge bias**：用同一個 model 既當 agent 又當 judge、容易 self-preferenced。Production 用不同 model 當 judge

## 延伸

- **加 regression 追蹤**：每次 ship 把 `{"date": ..., "pass_rate": ...}` 存進 sqlite、畫趨勢圖
- **CI 整合**：GitHub Actions 自動跑 eval、`pass_rate < 90%` 就 block merge
- **A/B model 對照**：同一份 eval、跑 qwen vs Claude vs GPT、看誰準
- **接觀察 (練習 3)**：eval failure 串到 observability、自動 alert
