"""
Stage 1 練習 4：Cross-Provider 比較 — starter.py

同一個 prompt 同時送給 Claude / GPT / Gemini、印對照表。
缺哪家 key 就 skip 哪家、不 crash。

跑法：
    pip install -r requirements.txt
    export ANTHROPIC_API_KEY=...   # 至少設一個
    export OPENAI_API_KEY=...      # （可選）
    export GOOGLE_API_KEY=...      # （可選）
    python starter.py

驗證：
    python test.py  （用 mock、不打 API）
"""

from __future__ import annotations

import os
import sys
import time
from dataclasses import dataclass

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")


PROMPT = "用 1-2 句話解釋 AGI 跟 narrow AI 的差別。"


@dataclass
class Reply:
    provider: str
    model: str
    text: str
    in_tokens: int
    out_tokens: int
    latency_ms: int


def call_claude(prompt: str) -> Reply | None:
    if not os.environ.get("ANTHROPIC_API_KEY"):
        return None
    import anthropic

    client = anthropic.Anthropic()
    t0 = time.time()
    msg = client.messages.create(
        model="claude-haiku-4-5",
        max_tokens=200,
        messages=[{"role": "user", "content": prompt}],
    )
    return Reply(
        provider="Anthropic",
        model="claude-haiku-4-5",
        text=msg.content[0].text,
        in_tokens=msg.usage.input_tokens,
        out_tokens=msg.usage.output_tokens,
        latency_ms=int((time.time() - t0) * 1000),
    )


def call_openai(prompt: str) -> Reply | None:
    if not os.environ.get("OPENAI_API_KEY"):
        return None
    from openai import OpenAI

    client = OpenAI()
    t0 = time.time()
    r = client.chat.completions.create(
        model="gpt-5-mini",
        max_tokens=200,
        messages=[{"role": "user", "content": prompt}],
    )
    return Reply(
        provider="OpenAI",
        model="gpt-5-mini",
        text=r.choices[0].message.content or "",
        in_tokens=r.usage.prompt_tokens,
        out_tokens=r.usage.completion_tokens,
        latency_ms=int((time.time() - t0) * 1000),
    )


def call_gemini(prompt: str) -> Reply | None:
    if not os.environ.get("GOOGLE_API_KEY"):
        return None
    from google import genai

    client = genai.Client()
    t0 = time.time()
    r = client.models.generate_content(
        model="gemini-3.5-flash",
        contents=prompt,
    )
    usage = getattr(r, "usage_metadata", None)
    return Reply(
        provider="Google",
        model="gemini-3.5-flash",
        text=r.text,
        in_tokens=getattr(usage, "prompt_token_count", 0) or 0,
        out_tokens=getattr(usage, "candidates_token_count", 0) or 0,
        latency_ms=int((time.time() - t0) * 1000),
    )


def compare(prompt: str) -> list[Reply]:
    replies = []
    for fn in (call_claude, call_openai, call_gemini):
        r = fn(prompt)
        if r is None:
            print(f"⚠ skip {fn.__name__}（沒有對應 API key）")
        else:
            replies.append(r)
    return replies


if __name__ == "__main__":
    print(f"prompt: {PROMPT}\n" + "=" * 60)
    replies = compare(PROMPT)

    for r in replies:
        print(f"\n[{r.provider} / {r.model}]  latency={r.latency_ms}ms  in={r.in_tokens} out={r.out_tokens}")
        print(r.text)

    # === 自我驗證 ===
    assert len(replies) >= 1, "至少要有一家 provider 回應（請設一個 API key）"
    for r in replies:
        assert len(r.text) > 5, f"{r.provider} 回應太短"
        assert r.in_tokens > 0, f"{r.provider} 沒 input token"
    print(f"\n✅ 練習 4 通過 — 收到 {len(replies)} 家 provider 回應、可比較風格 / 長度 / 成本")
