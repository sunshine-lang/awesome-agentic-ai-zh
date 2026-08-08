<div align="right">
  <a href="./README.md">繁體中文</a> | <a href="./README.zh-Hans.md">简体中文</a> | <strong>English</strong>
</div>

# Exercise 4: CodeAct vs JSON tool (Smolagents)

Pairs with [Stage 4 — Agent Frameworks](../../../stages/04-agent-frameworks.en.md) Exercise 4.
> 🎓 **How to use this**: `starter.py` is the **complete solution**, not a TODO skeleton. The active approach works better — `mv starter.py starter_reference.py`, read the signatures but not the bodies, write your own `starter.py` from scratch, then run `python test.py` to check it; if you are stuck for 20 minutes, go back and compare against the reference. Full methodology in [`docs/HOW_TO_USE.md`](../../../docs/HOW_TO_USE.md).

> 📚 **Want the chapter-length version?** The starter in this folder is an illustrative build focused on the core pattern plus two SDK paths — it is not in-depth teaching material. Recommended for depth:
> - [`datawhalechina/hello-agents`](https://github.com/datawhalechina/hello-agents) ⭐ the most complete Chinese-language course out there — chapter by chapter, plus 16 production capabilities. **This exercise maps to hello-agents' CodeAct vs JSON tool chapter**
> - [Smolagents official cookbook](https://github.com/huggingface/smolagents/tree/main/examples) + [QuantaLogic/quantalogic](https://github.com/quantalogic/quantalogic) (another CodeAct framework)
> - Full references in [Stage 4 Curated Projects](../../../stages/04-agent-frameworks.en.md#-curated-projects)


## Two agent-action paradigms

| Path | How the agent acts | Example frameworks |
|---|---|---|
| **JSON tool** | LLM returns `{"name": "tool_x", "arguments": {...}}` | OpenAI function calling, LangGraph, CrewAI |
| **CodeAct** | LLM writes Python code, framework executes it | HuggingFace Smolagents |

**This exercise solves the same task (population ratio) using CodeAct** — compare with the JSON-tool implementations in Exercises 1 / 3.

## How to run — two paths

### Path A (default, free, local)

```bash
pip install -r requirements.txt
ollama pull qwen2.5:3b
ollama serve
python starter.py
```

Budget: **$0**. CodeAct is hard on small models — qwen2.5:3b sometimes produces syntax errors and iterates to fix.

### Path B (Anthropic, cloud-quality)

```bash
pip install -r requirements.txt
export ANTHROPIC_API_KEY=sk-ant-...
python starter_anthropic.py
```

Budget: ~**$0.005-0.02** per run (CodeAct typically multi-step, claude-haiku-4-5). Claude writes correct Python far more reliably than qwen2.5:3b.

## Validate the logic

```bash
python test.py             # tool function + agent structure
python test_anthropic.py   # Path B import check
```

## How CodeAct works

The LLM doesn't return JSON — it returns a **Python code block**:

```
(user) Find Taipei population, divide by NYC, give ratio.

(LLM response)
```python
pop_taipei = lookup_fact(query="Taipei population")  # 2602000
pop_nyc = lookup_fact(query="New York population")   # 8336000
ratio = calculator(expression=f"{pop_taipei}/{pop_nyc}")  # 0.3122
print(ratio)
```

(Smolagents runs the code in a sandbox and feeds the print output back to the LLM)
```

The framework provides a sandboxed Python interpreter; the agent imports tools, writes code, sees stdout, continues.

## CodeAct vs JSON tool

| Dimension | JSON tool | CodeAct |
|---|---|---|
| LLM output form | Structured JSON | Python code |
| Variable binding | LLM must remember / call again | Native variables (`pop_taipei = ...`) |
| Multi-step compute | One call per step | Multiple steps in one code block |
| Tokens per round | Fewer | More (code is longer) |
| Small-model friendliness | Better (stable JSON) | Worse (must produce valid Python) |
| Debug | Inspect tool calls | Inspect code execution log |
| Safety | Tool args validated | Sandboxed Python (watch eval/exec limits) |
| Best for | Single-step, clear boundaries | Multi-step computation, intermediate variables |

**HuggingFace's stance**: CodeAct is closer to how humans solve problems — use a variable for intermediate results, don't re-fetch each step.

## What to watch on each path

| Observation | Anthropic Claude haiku | Ollama qwen2.5:3b |
|---|---|---|
| Valid Python syntax | Stable | Occasional syntax errors, iterates to fix |
| Variable naming / reuse | Natural | Tends to re-call tools instead of using vars |
| Correct multi-step ratio | High | Medium |
| Total steps | 1-2 | 3-5 (iterating fixes) |
| Cost | $0.005-0.02 | $0 |

**Punchline**: CodeAct is **model-quality-sensitive** — the LLM has to write Python that's solid enough for production. **Small models favor JSON-tool over CodeAct** (Exercise 6 of Stage 3 confirms a similar pattern at the schema layer).

## Common pitfalls

- **`@tool` function docstring is part of the prompt**: Smolagents passes the docstring to the LLM as the tool description. **Bad docstring = LLM doesn't know when to use it.**
- **CodeAct sandbox**: by default Smolagents bans `import os`, `open`, etc. To allow specific modules, set `additional_authorized_imports=[...]`
- **`max_steps` too low**: CodeAct iterates; `max_steps=4` may not be enough. But too high = infinite loops. 4-8 is the empirical range
- **Small models produce syntax errors**: Smolagents feeds the error back to the LLM, but you waste tokens. Production wants a larger model

## Want smarter answers?

```bash
MODEL=anthropic/claude-sonnet-5 python starter_anthropic.py  # most stable
MODEL=qwen2.5:7b python starter.py                              # larger local model
```

## Extensions

- **More tools**: just `@tool`-decorate; Smolagents auto-extracts docstring as description
- **Try `ToolCallingAgent`**: Smolagents also offers JSON-tool-style agents. Compare side-by-side
- **Hugging Face Hub**: `HfApiModel` for HF inference (no need for local Ollama)
- **Read [Anthropic — Building Effective Agents](https://www.anthropic.com/engineering/building-effective-agents)**: Anthropic argues both paradigms are valid; pick by task
