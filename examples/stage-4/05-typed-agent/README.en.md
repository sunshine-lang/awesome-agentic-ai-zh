<div align="right">
  <a href="./README.md">繁體中文</a> | <a href="./README.zh-Hans.md">简体中文</a> | <strong>English</strong>
</div>

# Exercise 5: Type-Safe Agent (Pydantic AI structured output)

Pairs with [Stage 4 — Agent Frameworks](../../../stages/04-agent-frameworks.en.md) Exercise 5.
> 🎓 **How to use this**: `starter.py` is the **complete solution**, not a TODO skeleton. The active approach works better — `mv starter.py starter_reference.py`, read the signatures but not the bodies, write your own `starter.py` from scratch, then run `python test.py` to check it; if you are stuck for 20 minutes, go back and compare against the reference. Full methodology in [`docs/HOW_TO_USE.md`](../../../docs/HOW_TO_USE.md).

> 📚 **Want the chapter-length version?** The starter in this folder is an illustrative build focused on the core pattern plus two SDK paths — it is not in-depth teaching material. Recommended for depth:
> - [`datawhalechina/hello-agents`](https://github.com/datawhalechina/hello-agents) ⭐ the most complete Chinese-language course out there — chapter by chapter, plus 16 production capabilities. **This exercise maps to hello-agents' structured output / type-safe chapter**
> - [Pydantic AI official docs](https://ai.pydantic.dev/) + [Instructor library](https://github.com/instructor-ai/instructor) (another route to typed output)
> - Full references in [Stage 4 Curated Projects](../../../stages/04-agent-frameworks.en.md#-curated-projects)


## Task

Agent answers questions and is **forced** to return `AnswerWithConfidence`:

```python
class AnswerWithConfidence(BaseModel):
    answer: str
    confidence: float = Field(ge=0.0, le=1.0)  # runtime check
    sources: list[str]
```

Pydantic AI lifts schema validation from the prompt layer (Stage 3 Exercise 6) **to the type layer** — if the LLM violates the schema, the framework auto-retries. Production teams use this to fight hallucination.

## How to run — two paths

### Path A (default, free, local)

```bash
pip install -r requirements.txt
ollama pull qwen2.5:3b
ollama serve
python starter.py
```

Budget: **$0**. But qwen2.5:3b may retry several times to satisfy the schema, raising total token usage.

### Path B (Anthropic, cloud-quality)

```bash
pip install -r requirements.txt
export ANTHROPIC_API_KEY=sk-ant-...
python starter_anthropic.py
```

Budget: ~**$0.001** per run (claude-haiku-4-5, usually one shot, no retry).

## Validate the logic

```bash
python test.py             # Pydantic schema validation + agent structure
python test_anthropic.py   # Path B import check
```

`test.py` directly verifies `AnswerWithConfidence` raises `ValidationError` on invalid data (confidence > 1.0, wrong type, sources not a list) — no LLM calls, pure type-layer testing.

## Why type-safe agents matter

```
Stage 3 Exercise 6: schema = JSON Schema in the prompt
    LLM sees it, but what it returns is up to the LLM (may violate)

Stage 4 Exercise 5: schema = Pydantic model in code
    LLM violates → framework auto-raises → retry / fix
    Final output is guaranteed to conform (runtime guarantee)
```

For production:

| Need | Prompt-only schema | Pydantic AI |
|---|---|---|
| LLM drops a field | Your downstream code needs try/except | Auto-retry until conformant |
| Wrong type (confidence="high") | Downstream crash | Pydantic ValidationError, retry |
| Out of bound (confidence=1.5) | Downstream gets bad data | Reject, retry |
| LLM hallucinates extra fields | Silently accepted | Default ignore (configurable to strict) |

**Bottom line**: production agents must use type-safe output. Stage 3 Exercise 6 teaches schema design; Stage 4 Exercise 5 teaches turning that schema into a runtime contract.

## Core Pydantic AI concepts

### Agent + output_type

```python
agent = Agent(
    model=...,
    output_type=AnswerWithConfidence,   # ← force LLM into this shape
    system_prompt="..."
)
result = agent.run_sync(question)
answer: AnswerWithConfidence = result.output   # validated object
```

**Key**: behind the scenes, the framework converts the Pydantic schema into structured-output instructions for the LLM, validates the response, and retries on failure.

### Field constraints

```python
confidence: float = Field(ge=0.0, le=1.0, description="...")
```

`ge` / `le` are Pydantic's numeric bounds. If the LLM returns 1.5, Pydantic raises ValidationError → retry.

### Auto-retry

```python
Agent(..., retries=3)  # default 1, configurable
```

When Pydantic AI sees a ValidationError, it appends the error message back into the prompt and asks the LLM to retry.

## What to watch on each path

| Observation | Anthropic Claude haiku | Ollama qwen2.5:3b |
|---|---|---|
| One-shot schema correct | 90%+ | 50-70% |
| Average retries | 0-1 | 1-3 |
| Confidence bound respected | Stable | Occasional 1.5 / negative (rejected, retry) |
| Sources is a list | Stable | Occasional string (rejected) |
| Total token cost | Low (few retries) | High (multiple retries) |

**Counterintuitive**: Path B (Claude) can actually have **lower total token cost** than Path A (qwen) — retries add up. Looking at the full bill, production teams pick the larger model.

## Common pitfalls

- **`output_type` too complex**: deeply nested models are hard for the LLM to produce in one shot. Aim for flat, ≤5 top-level fields
- **Missing `description`**: `Field(...)` without `description=` leaves the LLM guessing what the field is for
- **`retries=0`**: failure raises immediately, no chance to fix. Empirically `retries=1-3` works well
- **Small model + deep nesting**: qwen2.5:3b may retry many times and still fail. Upgrade or flatten

## Want smarter answers?

```bash
MODEL=claude-sonnet-5 python starter_anthropic.py    # highest one-shot rate
MODEL=qwen2.5:7b python starter.py                      # larger local model
```

## Extensions

- **Add tools**: Pydantic AI agents can have tools + structured output simultaneously via `@agent.tool`
- **Stream typed output**: `agent.run_stream(...)` validates as it streams
- **Cross-model comparison**: same schema across Claude / GPT / Gemini / local — see who's most stable
- **Production wiring**: Pydantic AI integrates with FastAPI; output doubles as your API response model
