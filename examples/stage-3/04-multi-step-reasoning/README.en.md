<div align="right">
  <a href="./README.md">繁體中文</a> | <a href="./README.zh-Hans.md">简体中文</a> | <strong>English</strong>
</div>

# Exercise 4: Multi-Step Reasoning

Corresponds to [Stage 3 — Tool Use & Agent Intro](../../../stages/03-tool-use-and-hello-agent.en.md) Exercise 4.
> 🎓 **How to use this**: `starter.py` is the **complete solution**, not a TODO skeleton. The active approach works better — `mv starter.py starter_reference.py`, read the signatures but not the bodies, write your own `starter.py` from scratch, then run `python test.py` to check it; if you are stuck for 20 minutes, go back and compare against the reference. Full methodology in [`docs/HOW_TO_USE.md`](../../../docs/HOW_TO_USE.md).

> 📚 **Want the chapter-length version?** The starter in this folder is a 70-150 line illustrative build focused on `the core pattern + two SDK paths` — it is not in-depth teaching material. Recommended for depth:
> - [`datawhalechina/hello-agents`](https://github.com/datawhalechina/hello-agents) ⭐ the most complete Chinese-language course out there — chapter-based, covering 16 production capabilities. **this exercise maps to hello-agents' planning / multi-step workflow chapter**
> - [Anthropic — Building Effective Agents](https://www.anthropic.com/engineering/building-effective-agents) (when to break a task into steps, and when not to)
> - Full references in [Stage 3 Curated Projects](../../../stages/03-tool-use-and-hello-agent.en.md#-curated-projects)


## Why this matters

Extends the ReAct loop from Exercise 3 into a **3-5 step task**: look up Taipei population → look up NY population → divide → convert to percentage. The LLM plans the next step; the tools reliably execute small actions. Together they look like an agent that can complete a workflow.

It's also a great place to feel **model scale vs multi-step stability**. Same loop, claude-haiku usually finishes in 4 steps; qwen2.5:3b may skip a step (e.g., forget to convert to percentage) or stop too early.

## How to run — two paths

### Path A (default, free, local)

```bash
pip install -r requirements.txt
ollama pull qwen2.5:3b
ollama serve
python starter.py
```

Budget: **$0**. A 4-5 round loop takes ~30-120s on CPU.

### Path B (Anthropic, cloud-quality comparison)

```bash
pip install -r requirements.txt
export ANTHROPIC_API_KEY=sk-ant-...
python starter_anthropic.py
```

Budget: ~**$0.005** per run (claude-haiku-4-5, 5 rounds of accumulating messages).

Expected output (Path A, local, ideal 4-step path):

```
❓ Question: Find Taipei population divided by New York population, then express it as a percentage.
------------------------------------------------------------
[step 0] tool: lookup_population({'city': 'Taipei'}) → 2602000
[step 1] tool: lookup_population({'city': 'New York'}) → 8336000
[step 2] tool: divide({'a': 2602000, 'b': 8336000}) → 0.3122...
[step 3] tool: to_percentage({'ratio': 0.3122}) → 31.22
------------------------------------------------------------
✅ Final answer: Taipei is about 31.22% of New York's population.
   Took 5 rounds.
✅ Exercise 4 passed — multi-step ReAct loop ran locally on qwen2.5:3b, $0/run
```

## Validate the logic without API credits (mock-based)

```bash
python test.py            # validates Path A (Ollama) starter.py logic
python test_anthropic.py  # validates Path B (Anthropic) starter_anthropic.py logic
```

Both test suites use `unittest.mock`, no real API call, $0/run.

## Conceptual reminders

The core of multi-step tasks isn't "the model is good at math" — it's breaking a complex task into reliable small steps:

- **Tools should be narrow and stable**: `divide(a, b)` does one thing; even `b=0` doesn't crash, it returns 0
- **The LLM plans**: decides which tool to call next and when to stop
- **`max_iter=8` is a mandatory safety net**: prevents the model from looping forever without finishing
- **`messages` grows each round**: assistant response + tool_result are appended so the LLM can see history

## What to watch on each path

| Observation | Anthropic Claude haiku | Ollama qwen2.5:3b |
|---|---|---|
| Probability of completing 4 steps | High | Medium (may skip "to_percentage") |
| Step ordering | Stable | Can swap order |
| End-turn detection | Reliable `end_turn` | May add a redundant tool call before stopping |
| Cost per run | $0.005 | $0 |

This is precisely the teaching point of Exercise 4 — **same ReAct loop, different model, which step breaks first**. When picking a production model, multi-step stability is as important as cost.

## Want smarter answers?

Default is `claude-haiku-4-5` (cheapest). Try Sonnet:

```bash
MODEL=claude-sonnet-5 python starter_anthropic.py
```

Or on the Ollama path, swap to a larger model:

```bash
MODEL=qwen2.5:7b python starter.py    # 4.7 GB, more stable
MODEL=mistral-nemo:12b python starter.py  # 7.1 GB, closer to cloud
```

## Extensions

- **Add more tools** — append one entry each to `TOOLS_SPEC` + `TOOL_IMPL`
- **Add retry / error handling** — see [`../05-error-handling/`](../05-error-handling/) for tool failure patterns
- **Schema design** — see [`../06-schema-design/`](../06-schema-design/) for a bad vs good schema A/B
