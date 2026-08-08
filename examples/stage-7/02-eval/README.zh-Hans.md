<div align="right">
  <a href="./README.md">繁體中文</a> | <strong>简体中文</strong> | <a href="./README.en.md">English</a>
</div>

# 练习 2：Eval Pipeline（"pytest for LLMs"）

对应 [Stage 7 — Multi-Agent & Production](../../../stages/07-multi-agent-production.zh-Hans.md) 练习 2。
> 🎓 **学习模式**：这份 `starter.py` 是**完整解答**、不是 TODO skeleton。建议用**主动模式**——`mv starter.py starter_reference.py`、看 signature 不看 body、自己重写一份 `starter.py`、跑 `python test.py` 验证；卡 20 分钟再回去对照 reference。完整方法论看 [`docs/HOW_TO_USE.md`](../../../docs/HOW_TO_USE.md)。

> 📚 **想要 chapter-length 深入版？** 本 folder 的 starter 是 illustrative 版、聚焦核心 pattern + 两条 SDK path，不是进阶深度教材。深度教材推荐：
> - [`datawhalechina/hello-agents`](https://github.com/datawhalechina/hello-agents) ⭐ 中文圈最完整、章节式 + 16 种 production 能力。**本练习对应 hello-agents 的 eval / regression testing 章节**
> - [promptfoo](https://github.com/promptfoo/promptfoo) + [Anthropic Workbench Evals](https://console.anthropic.com/workbench/evals)（官方 eval UI）
> - 完整 references 见 [Stage 7 精选 Projects](../../../stages/07-multi-agent-production.zh-Hans.md#-精选-projects范本--sdk--工具-collection)

## 任务

为 production agent 写 5 个 eval case、跑 baseline、追 regression。**Production 没 eval = 没 confidence ship**。

5 个 case 涵盖：
1-2. **Math**（deterministic 答案）
3-4. **Geography**（factual recall）

5. **Grounding test**（fake word“flrgglemerk”、agent 应该说 "don't know"、不该 hallucinate）

两种 evaluator：

| 方式 | 何时用 | 成本 |
|---|---|---|
| **string match** | 答案有 deterministic substring（数字、专有名词） | $0、极快 |
| **LLM-as-judge** | 开放式答案（recommendation / explanation） | 多 1 个 LLM call |

## 怎么跑

### Path A（默认、本机免费）

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

预算：5 cases × 1 call ≈ **$0.003**（Claude haiku）。

## 不花钱验证程序逻辑

```bash
python test.py             # 7 个 test：evaluator + run_eval aggregation
python test_anthropic.py   # Anthropic agent mock
```

## Eval 的 production 价值

```
Without eval：
   PR merge → 上 prod → user 抱怨 → 你才知道 LLM 行为变了

With eval：
   PR → run eval → pass_rate 从 95% 掉到 70% → block merge
   → 找出哪些 case regression → 改 prompt / model / retry → recover
```

**Eval pin baseline**：第一次跑、记住 pass_rate（譬如 80%）；每次 ship 前确认没掉。

## 经典 eval 结构

```python
eval_cases = [
    {"id": ..., "input": ..., "expected_substring": ..., "instruction": ...},
    ...
]

def run_eval(cases, agent_fn, eval_fn):
    results = [...]
    return {"pass_count": ..., "pass_rate": ...}
```

**3 个关键**：

1. **`id` 必要**：方便定位是哪一题 regress
2. **`expected_substring` 而非 full match**：LLM 答案有 variability、用 substring 才稳
3. **Eval function 跟 agent 分离**：可以换不同 evaluator 对同一份 cases

## LLM-as-judge 何时用

| 情境 | 用 substring | 用 LLM-as-judge |
|---|---|---|
| “2+2=?”答案 | ✅ "4" | overkill |
| “summarize this article” | ❌ 没固定 substring | ✅ |
| “is the tone professional?” | ❌ | ✅ |
| “count tokens used” | ✅ 用 regex | overkill |

**Production 经验**：80% case 用 substring + heuristic、20% 用 LLM-as-judge（cost / latency 较高）。

## Production-ready tools

- **[promptfoo](https://github.com/promptfoo/promptfoo)**：YAML config + CLI runner + diff report
- **[Anthropic Workbench eval](https://console.anthropic.com/workbench/evals)**：官方 eval UI、prompts as code
- **[LangSmith](https://smith.langchain.com/)**：LangChain ecosystem 的 eval + observability 一条龙
- **[Weights & Biases Weave](https://wandb.ai/site/weave)**：generic LLM eval framework
- **[Braintrust](https://www.braintrust.dev/)**：跨 model / version A/B、上线部署用的 dashboards

## 两个 path 观察重点

| 观察项 | Anthropic Claude | Ollama qwen2.5:3b |
|---|---|---|
| math case pass rate | ~100% | ~80% |
| geo case pass rate | ~100% | ~70-90% |
| grounding test (flrgglemerk) | 守规则说 don't know | 偶尔编答案 |
| 整体 pass_rate | 95-100% | 70-85% |

**结论**：production 应该针对“自家 use case”建 50-200 case 的 eval set、看自家任务上的 pass rate、决定该用哪个 model。

## 常见坑

- **Eval set 太小（< 10 cases）**：noise 高、看不出 regression
- **Eval set 太靠近 training data**：model 死背、实际 user query 表现完全不同
- **没 grounding test**：production agent hallucination 是最致命的 bug、必须有“答不出来该说 unknown”case
- **`expected_substring` 太严**：写“The capital is Tokyo, Japan.”当 expected、LLM 写“Tokyo”会 fail。应该只匹配关键字
- **LLM-as-judge bias**：用同一个 model 既当 agent 又当 judge、容易 self-preferenced。Production 用不同 model 当 judge

## 延伸

- **加 regression 追踪**：每次 ship 把 `{"date": ..., "pass_rate": ...}` 存进 sqlite、画趋势图
- **CI 整合**：GitHub Actions 自动跑 eval、`pass_rate < 90%` 就 block merge
- **A/B model 对照**：同一份 eval、跑 qwen vs Claude vs GPT、看谁准
- **接观察 (练习 3)**：eval failure 串到 observability、自动 alert
