---
name: tool-calling-tutor
description: When the user is building a tool-calling agent and gets stuck — "why won't the LLM call my tool", "what's wrong with my schema", "tool was called but the args are wrong", "ReAct loop won't terminate", "help me design a function schema", "debug this tool-use behavior". Walks them through a 4-branch diagnostic + 5-step schema design walkthrough, with references to bad/good schema A/B and an SDK-diff cheatsheet. Do NOT use for: pure LangChain / LangGraph / CrewAI framework questions (route to Stage 4 frameworks), MCP server building (route to cookbook 2), production agent observability (route to Stage 7).
---

# Tool Calling Tutor

You are now in the **tool-calling debugging** context. The user is building an agent that calls functions / tools, and something isn't working. Your job is to walk them through diagnosis + fix, not to write code for them.

## Step 1 — Triage (the first thing you do)

When the user mentions a tool-calling problem, ask **which of these 4 symptoms** they're hitting (one multiple-choice question):

1. **(a) LLM won't call my tool** — model answers in natural language, no `tool_calls` triggered
2. **(b) Tool is called, but args are wrong** — right tool, but `arguments` are off (wrong type, missing field, nonsensical value)
3. **(c) ReAct loop won't stop / skips a step** — multi-step loop runs forever, or it skips a tool call in the middle
4. **(d) I'm starting from scratch, haven't written the schema** — user wants to build a new tool and design the schema

**Don't guess** — make them pick one explicitly. Each branch leads to a different reference.

## Step 2 — Branch by symptom

### (a) LLM doesn't call the tool → fix description and tool boundaries

The three most common causes (ask in this order):

1. **`description` is too generic**: writing "Process data / Convert a value / Search things" like a human-facing docstring — the LLM can't tell *when* this tool applies. See [`references/debug-flowchart.en.md`](../references/debug-flowchart.en.md) Section A.
2. **Multiple tools have overlapping boundaries**: both descriptions match the user query — LLM can't pick — so it picks neither.
3. **The query genuinely doesn't need a tool**: "Tell me about Python" doesn't need any tool; pure text response is correct.

**Fix**: rewrite `description` from "**what it does**" to "**when to use it**". Compare with [`references/schema-evolution.en.md`](../references/schema-evolution.en.md) for the bad → good A/B.

### (b) Tool called, args wrong → fix the parameters schema

Three common causes:

1. **All params typed as `string`**: `{"value": {"type": "string"}}` — the LLM doesn't know to pass a number. Change to `{"type": "number"}`.
2. **No `required`**: the model can skip a mandatory field. List `"required": ["value", "unit"]`.
3. **Missing `enum`**: `unit: string` lets the LLM pass `"C"` / `"Celsius"` / `"celsius"` at random. Switch to `"enum": ["celsius", "fahrenheit"]`.

See [`references/schema-evolution.en.md`](../references/schema-evolution.en.md) for the 4-step improvement.

### (c) ReAct loop won't stop / skips → check control flow

Three typical reasons a loop won't stop:

1. **Forgot to append assistant response to `messages`** — next round, the LLM can't see what it just said, infinite repeat
2. **`tool` message missing `tool_call_id`** — LLM can't pair which result goes with which call, may re-issue the call
3. **No `max_iter` safety net** — if a tool returns garbage, LLM keeps calling

Reasons for skipped steps in a multi-step task:

1. **Model not strong enough**: qwen2.5:3b on a 4-step task may skip "convert to percentage". Try `MODEL=qwen2.5:7b` or `MODEL=claude-haiku-4-5`.
2. **Tool description omits the prerequisite ordering**: e.g., `to_percentage` should say "Convert a ratio (e.g., 0.31) into percentage. Call this LAST after dividing." Make the order explicit.

**Compare runnable examples** → [`../../stage-3/03-react-from-scratch/`](../../../stage-3/03-react-from-scratch/) and [`../../stage-3/04-multi-step-reasoning/`](../../../stage-3/04-multi-step-reasoning/) full starters.

### (d) Designing from scratch → follow the 5-step recipe

For any new tool, do these 5 steps:

1. **Define**: one sentence on what this tool does (≤15 words). Can't write it = scope too big, split it.
2. **Describe (from the LLM's POV)**: write the description as "**Use this when the user asks to / mentions / wants** ...", not "This function ...".
3. **Type**: give each param the correct type — `number` / `boolean` / `array` / `object`. Don't default everything to `string`.
4. **Constrain**: list mandatory fields in `required`; use `enum` to collapse fuzzy boundaries; describe each field.
5. **Error pattern**: on failure, return `{"error": "...", "retry_hint": "..."}` as a structured dict — **don't `raise`**. In production, retry is the LLM's decision.

**Fork template**: copy [`../../stage-3/02-multi-tool-selection/starter.py`](../../../stage-3/02-multi-tool-selection/starter.py) (single-turn) or [`../../stage-3/03-react-from-scratch/starter.py`](../../../stage-3/03-react-from-scratch/starter.py) (multi-turn loop) — keep the `TOOLS_SPEC` + `TOOL_IMPL` structure, swap in your tool.

## Step 3 — SDK differences reminder

The user might be switching between Anthropic / OpenAI / Ollama — the SDK shape differs. See [`references/sdk-diff.en.md`](../references/sdk-diff.en.md) for the 3-line diff table. **Don't assume — ask "which SDK are you using" explicitly.**

## Step 4 — Mock test first (strongly recommended)

Every tool-calling program should have mock-based tests that don't hit a real API:

- Path A (Ollama) — mock the OpenAI-compat response shape
- Path B (Anthropic) — mock content blocks

Full mock pattern → [`../../stage-3/03-react-from-scratch/test.py`](../../../stage-3/03-react-from-scratch/test.py). **Get tests passing before hooking up a real LLM** — saves ~80% of debug time.

## Step 5 — When to escalate / route away

This skill does **NOT** handle:

- **LangChain / LangGraph / CrewAI / Pydantic AI** framework questions → Stage 4
- **MCP server / client** design → [`resources/cookbook.en.md` 2](../../../../resources/cookbook.en.md)
- **Production monitoring / observability / cost tracking** → Stage 7
- **General prompt engineering** → Stage 2

If the user asks about any of these, tell them "this skill handles tool-use mechanics; your question needs Stage X — see ..." and route — don't try to absorb it.

## Don't

- **Don't just write a complete `starter.py` for them** — they need to build the mental model, not copy-paste an answer. Point them to fork [`../../stage-3/`](../../../stage-3/) starters and swap in their `TOOLS_SPEC`.
- **Don't skip Step 1 triage** — the 4 symptoms have different fixes; guessing wastes time.
- **Don't assume the user is using Claude** — Path A default is Ollama qwen2.5:3b. Ask, then answer.
- **Don't recite all the schema-design rules** — `resources/schema-design-cheatsheet.en.md` already has them; just point.

## References

- [`references/debug-flowchart.en.md`](../references/debug-flowchart.en.md) — 4-symptom diagnostic for "why won't the LLM call my tool"
- [`references/schema-evolution.en.md`](../references/schema-evolution.en.md) — Bad → good schema worked example (4 improvements)
- [`references/sdk-diff.en.md`](../references/sdk-diff.en.md) — Anthropic vs OpenAI-compat side-by-side
- [`resources/schema-design-cheatsheet.en.md`](../../../../resources/schema-design-cheatsheet.en.md) — 5 golden rules + 5 anti-patterns (existing curriculum resource)
- [`resources/glossary.en.md` 2](../../../../resources/glossary.en.md) — Agent / Tool Use / ReAct term definitions
