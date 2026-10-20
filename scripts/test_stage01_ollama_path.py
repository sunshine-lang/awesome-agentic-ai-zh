from __future__ import annotations

import contextlib
import io
import re
import sys
import types
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch


ROOT = Path(__file__).resolve().parents[1]
PAGES = {
    "zh-TW": ROOT / "stages" / "01-llm-basics.md",
    "en": ROOT / "stages" / "01-llm-basics.en.md",
    "zh-Hans": ROOT / "stages" / "01-llm-basics.zh-Hans.md",
}


def ollama_example(page: str, exercise: int) -> str:
    filename = f"practice_{exercise}.py"
    for details in re.finditer(r"<details\b[^>]*>([\s\S]*?)</details\s*>", page, re.I):
        body = details.group(1)
        summary = re.search(r"<summary\b[^>]*>([\s\S]*?)</summary\s*>", body, re.I)
        if not summary or filename not in summary.group(1):
            continue
        fence = "`" * 3
        code = re.search(re.escape(fence) + r"python\s*\r?\n([\s\S]*?)" + re.escape(fence), body)
        if code:
            return code.group(1)
    raise AssertionError(f"Path A code block for {filename} was not found")


def response(finish_reason: str = "stop", content: str = "A cat is resting.") -> SimpleNamespace:
    return SimpleNamespace(
        choices=[
            SimpleNamespace(
                finish_reason=finish_reason,
                message=SimpleNamespace(content=content),
            )
        ],
        usage=SimpleNamespace(completion_tokens=18, prompt_tokens=5),
    )


class FakeCompletions:
    def __init__(self, responses=()):
        self.responses = list(responses)
        self.calls: list[dict] = []
        self.chat = SimpleNamespace(completions=self)

    def create(self, **kwargs):
        self.calls.append(kwargs)
        if self.responses:
            return self.responses.pop(0)
        return response()


def execute_example(source: str, responses=()):
    api = FakeCompletions(responses)
    openai = types.ModuleType("openai")
    init_calls = []

    def fake_openai(**kwargs):
        init_calls.append(kwargs)
        return api

    openai.OpenAI = fake_openai
    error = None
    namespace = {}
    with patch.dict(sys.modules, {"openai": openai}):
        with contextlib.redirect_stdout(io.StringIO()):
            try:
                exec(compile(source, "<documented Path A example>", "exec"), namespace)
            except Exception as exc:  # Return the exact failure for assertions below.
                error = exc
    return error, api, namespace, init_calls


class Stage01OllamaPathTests(unittest.TestCase):
    def test_all_locale_examples_disable_thinking_and_accept_complete_answers(self):
        for locale, path in PAGES.items():
            page = path.read_text(encoding="utf-8")
            for exercise, max_tokens, expected_calls in ((1, 100, 1), (2, 80, 20)):
                with self.subTest(locale=locale, exercise=exercise):
                    source = ollama_example(page, exercise)
                    error, api, _namespace, init_calls = execute_example(source)
                    self.assertIsNone(error)
                    self.assertEqual(len(api.calls), expected_calls)
                    self.assertTrue(all(call["reasoning_effort"] == "none" for call in api.calls))
                    self.assertTrue(all(call["model"] == "gemma4:e4b" for call in api.calls))
                    self.assertTrue(all(call["max_tokens"] == max_tokens for call in api.calls))
                    self.assertEqual(init_calls[0]["base_url"], "http://localhost:11434/v1")

            self.assertIn("gemma4:e4b", page)
            self.assertIn("0.34.2", page)
            self.assertIn('finish_reason="length"', page)
            self.assertIn('reasoning_effort="none"', page)
            self.assertIn('finish_reason="stop"', page)
            self.assertRegex(page, r"(?i)(older|舊版|旧版)")
            self.assertRegex(page, r"(?i)(compatib|相容|兼容)")
            self.assertRegex(page, r"(?i)(paid API quota|付費 API 額度|付费 API 额度)")

    def test_truncated_empty_and_whitespace_outputs_fail_before_token_counting(self):
        bad_responses = (
            response("length", ""),
            response("length", "partial text"),
            response("stop", "   "),
        )
        for locale, path in PAGES.items():
            page = path.read_text(encoding="utf-8")
            for exercise in (1, 2):
                source = ollama_example(page, exercise)
                for bad in bad_responses:
                    with self.subTest(locale=locale, exercise=exercise, finish=bad.choices[0].finish_reason,
                                      content=bad.choices[0].message.content):
                        error, api, namespace, _init_calls = execute_example(source, [bad])
                        self.assertIsInstance(error, AssertionError)
                        self.assertIn("finish_reason", str(error))
                        self.assertEqual(len(api.calls), 1)
                        if exercise == 2:
                            self.assertEqual(namespace.get("output_tokens"), [])


if __name__ == "__main__":
    unittest.main()
