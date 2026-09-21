# Learn-Test

[繁體中文](README.md) | [简体中文](README.zh-Hans.md) | **English**

This directory contains local practice scripts for Stage 0-2 of the agentic AI learning path.

The scripts use a local OpenAI-compatible oMLX endpoint for LLM calls. Configuration is centralized in `.env.template` and loaded through `config.py`.

## Setup

1. Copy the template file:

```bash
cp .env.template .env
```

2. Edit `.env` if your local oMLX server uses a different URL, API key, or model:

```env
OMLX_BASE_URL=http://127.0.0.1:8429/v1
OMLX_API_KEY=010209
OMLX_MODEL=Qwen3.5-9B-MLX-4bit
```

3. Start oMLX before running Stage 1 or Stage 2 scripts.

4. Run scripts from this directory:

```bash
cd Learn-Test
python stage1_hello.py
```

## Files

| File | Purpose |
|---|---|
| `.env.template` | Template for local oMLX configuration. Copy to `.env` for local overrides. |
| `config.py` | Loads `.env.template`, then `.env`, and exposes `BASE_URL`, `API_KEY`, and `MODEL`. |
| `stage0.py` | Stage 0 practice: call the GitHub REST API, parse JSON, and handle request errors. |
| `stage1_hello.py` | Stage 1 practice: make a basic local LLM call and inspect response metadata. |
| `stage1_context.py` | Stage 1 practice: demonstrate explicit multi-turn context in API calls. |
| `stage1_retry.py` | Stage 1 practice: wrap LLM calls with prompt validation, usage logging, and connection retry handling. |
| `stage2_prompt.py` | Stage 2 practice: iterate V1-V5 prompts for a 7-day learning-plan generation task. |
| `stage2_fewshot.py` | Stage 2 practice: compare system prompts and validate JSON output. |
| `stage2_fewshot2.py` | Stage 2 practice: run a few-shot sentiment classification evaluation. |
| `stage2_cot.py` | Stage 2 practice: compare direct answers, verbose reasoning, and condition-checking prompts. |
| `prompt_eval.py` | Stage 2 final check: evaluate V1-V5 prompt outputs and print a Markdown summary table. |

## Suggested Run Order

Run the scripts in this order:

```bash
python stage0.py
python stage1_hello.py
python stage1_context.py
python stage1_retry.py
python stage2_fewshot.py
python stage2_fewshot2.py
python stage2_cot.py
python stage2_prompt.py
python prompt_eval.py
```

`stage0.py` uses the public GitHub API. If you set `GITHUB_TOKEN`, it will be sent as an auth header:

```bash
export GITHUB_TOKEN=...
```

## Configuration Rules

Do not hard-code local model settings in practice scripts. Use:

```python
from config import API_KEY, BASE_URL, MODEL
```

The intended source of these values is:

1. `.env.template` for defaults committed with the exercise files.
2. `.env` for local machine-specific overrides.
3. Existing shell environment variables, unless `.env` overrides them.

## Notes

- `config.py` is intentionally minimal and does not require `python-dotenv`.
- Stage 1 and Stage 2 scripts assume an OpenAI-compatible local endpoint.
- Some outputs may vary slightly even with `temperature=0`, depending on model and serving backend behavior.
