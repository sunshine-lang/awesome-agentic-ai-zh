<div align="right">
  <a href="./README.md">繁體中文</a> | <a href="./README.zh-Hans.md">简体中文</a> | <strong>English</strong>
</div>

# Exercise 3: ReAct from Scratch (no framework)

Corresponds to [Stage 3 — Tool Use & Agent Intro](../../../stages/03-tool-use-and-hello-agent.en.md) Exercise 3.
> 🎓 **How to use this**: `starter.py` is the **complete solution**, not a TODO skeleton. The active approach works better — `mv starter.py starter_reference.py`, read the signatures but not the bodies, write your own `starter.py` from scratch, then run `python test.py` to check it; if you are stuck for 20 minutes, go back and compare against the reference. Full methodology in [`docs/HOW_TO_USE.md`](../../../docs/HOW_TO_USE.md).

> 📚 **Want the chapter-length version?** The starter in this folder is a 70-150 line illustrative build focused on `the core pattern + two SDK paths` — it is not in-depth teaching material. Recommended for depth:
> - [`datawhalechina/hello-agents`](https://github.com/datawhalechina/hello-agents) ⭐ the most complete Chinese-language course out there — chapter-based, covering 16 production capabilities. **this exercise maps to hello-agents' ReAct chapter (paired with the [`learn_version` branch](https://github.com/jjyaoao/HelloAgents/tree/learn_version))**
> - [The original ReAct paper](https://arxiv.org/abs/2210.03629) (Yao et al. 2022, Section 3) + [pguso/ai-agents-from-scratch](https://github.com/pguso/ai-agents-from-scratch) (from-scratch implementation on a local LLM)
> - Full references in [Stage 3 Curated Projects](../../../stages/03-tool-use-and-hello-agent.en.md#-curated-projects)


## Why write it from scratch

ReAct (Reasoning + Acting) is the foundational pattern of modern agents:

```
while not done:
    thought     = LLM reads current context and verbalizes the next step
    action      = LLM calls a tool
    observation = tool result, fed back to the LLM
```

LangGraph / CrewAI hide this loop from you. **Writing it once yourself** is what teaches you:

- Why the `messages` array keeps growing
- How `tool_use_id` pairs with `tool_result`
- Why `stop_reason` is `tool_use` vs `end_turn`
- Why `max_iter` is a mandatory safety net

All of that is covered in 70 lines of Python.

## How to run — two paths

### Path A (default, free, local)

```bash
pip install -r requirements.txt
ollama pull qwen2.5:3b
ollama serve
python starter.py
```

Budget: **$0**. A 4-6 round ReAct loop on local qwen2.5:3b takes ~30-120s (CPU slower, GPU faster).

### Path B (Anthropic, cloud-quality comparison)

```bash
pip install -r requirements.txt
export ANTHROPIC_API_KEY=sk-ant-...
python starter_anthropic.py
```

Budget: ~**$0.001** per run (claude-haiku-4-5). 5-15x faster than local, with steadier answer quality.

Expected output (Path A, local):

```
❓ Question: Divide 'Taipei population' by 'NYC population', 4 decimal places.
------------------------------------------------------------
[step 0] thought: Let me look up Taipei's population...
           tool: lookup_fact({'query': '台北人口'}) → 2602000
[step 1] thought: Now NYC's...
           tool: lookup_fact({'query': '紐約人口'}) → 8336000
[step 2] thought: Compute the ratio...
           tool: calculator({'expression': '2602000 / 8336000'}) → 0.3121...
[step 3] thought: The answer is 0.3122.
------------------------------------------------------------
✅ Final answer: Taipei / NYC ≈ 0.3122
   Took 4 rounds.
✅ Exercise 3 passed — the ReAct loop chained lookup_fact and calculator on its own.
```

## Validate the logic without spending API credits

```bash
python test.py            # validates Path A (Ollama) starter.py logic
python test_anthropic.py  # validates Path B (Anthropic) starter_anthropic.py logic
```

Both test suites use `unittest.mock`, no real API call, $0/run. Path A uses the OpenAI-compat response shape; Path B uses Anthropic content blocks.

`test.py` uses `unittest.mock.MagicMock` to replace the Anthropic client and feed canned responses, validating your loop logic. Expected:

```
✅ test_calculator_basic
✅ test_calculator_rejects_eval_injection
✅ test_lookup_fact
✅ test_react_loop_single_tool_call
✅ test_react_loop_multi_step
✅ test_react_loop_respects_max_iter

🎉 All tests passed — your ReAct loop logic is correct.
```

## Program structure walkthrough

| Section | Lines | What it does |
|---|---|---|
| `tool_calculator` | ~30-40 | Safe calculator (whitelist filter, avoids `eval` injection) |
| `tool_lookup_fact` | ~42-50 | Fake fact lookup (teaching-only, avoids external API dep) |
| `TOOLS_SPEC` | ~52-75 | Tool schema that the LLM sees |
| `TOOL_IMPL` | ~77-80 | name → callable dispatch table |
| `react_loop` | ~85-130 | Main loop, with max_iter safety, `messages` accumulation, tool_result wiring |

## Common pitfalls

1. **Forgetting to append the assistant response to messages** — next round the LLM can't see what it just said, leading to infinite loops
2. **Not passing `tool_use_id` with tool_result** — the LLM can't pair results to calls
3. **`while True` without `max_iter`** — if a tool returns garbage the LLM may call it forever; safety net is mandatory
4. **Unfiltered eval** — `eval(user_input)` in calculator = RCE; use a whitelist or `ast.literal_eval`

## Want smarter answers?

Default model is `claude-haiku-4-5` (cheapest). Switch to Sonnet:

```bash
MODEL=claude-sonnet-5 python starter.py
```

Or change `MODEL = ...` in `starter.py`.

## Extensions

- **Add more tools** — append one entry each to `TOOLS_SPEC` + `TOOL_IMPL`
- **Add streaming** — swap `client.messages.create(...)` for `with client.messages.stream(...) as s:`, print as it goes
- **Add prompt cache** — pass `cache_control={"type":"ephemeral"}` on `system=` or `tools=` to save 90% on repeat calls
- **Plug into [LangGraph](https://langchain-ai.github.io/langgraph/) or [Pydantic AI](https://ai.pydantic.dev/)** to see how frameworks hide these 70 lines
