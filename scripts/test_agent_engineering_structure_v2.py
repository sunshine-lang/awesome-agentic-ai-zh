"""Reader-facing contract for structures, engineering work, and chapter order."""

from __future__ import annotations

import re
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[1]
DIAGRAM_PROMPT = ROOT / "resources/diagrams/locale-variant-prompts.md"
LOCALES = {
    "zh-TW": {
        "stage4": ROOT / "stages/04-agent-frameworks.md",
        "stage7": ROOT / "stages/07-multi-agent-production.md",
        "readme": ROOT / "README.md",
        "stage4_title": "# Stage 4 — Workflow Graph 與 Agent 框架",
        "stage7_title": "# Stage 7 — Agent Production Engineering：Harness、Loop 與 Graph",
        "umbrella": "**Agent Production Engineering（Agent 上線工程）**",
        "structure_header": "會跑的東西",
        "work_header": "設計它的工作",
        "stage4_bridge": "Stage 4 先教 **Workflow Graph** 和實作它的 **Agent Framework**；Stage 7 再把同一張圖做成可觀測、可復原的 production orchestration",
        "readme_route": "Stage 4 先看懂 **Workflow Graph**，再用 framework 把它做出來",
        "term_status": "**Loop Engineering** 是 IBM 明確標為 emerging practice 的新興稱呼",
    },
    "en": {
        "stage4": ROOT / "stages/04-agent-frameworks.en.md",
        "stage7": ROOT / "stages/07-multi-agent-production.en.md",
        "readme": ROOT / "README.en.md",
        "stage4_title": "# Stage 4 — Workflow Graphs & Agent Frameworks",
        "stage7_title": "# Stage 7 — Agent Production Engineering: Harness, Loops, and Graphs",
        "umbrella": "**Agent Production Engineering**",
        "structure_header": "What runs",
        "work_header": "Work that designs it",
        "stage4_bridge": "Stage 4 introduces the **Workflow Graph** and the **Agent Frameworks** that can implement it. Stage 7 makes that same map observable and recoverable as production orchestration",
        "readme_route": "Stage 4 first explains the **Workflow Graph**, then uses a framework to build it",
        "term_status": "IBM explicitly describes **Loop Engineering** as an emerging practice",
    },
    "zh-Hans": {
        "stage4": ROOT / "stages/04-agent-frameworks.zh-Hans.md",
        "stage7": ROOT / "stages/07-multi-agent-production.zh-Hans.md",
        "readme": ROOT / "README.zh-Hans.md",
        "stage4_title": "# Stage 4 — Workflow Graph 与 Agent 框架",
        "stage7_title": "# Stage 7 — Agent Production Engineering：Harness、Loop 与 Graph",
        "umbrella": "**Agent Production Engineering（Agent 上线工程）**",
        "structure_header": "会运行的东西",
        "work_header": "设计它的工作",
        "stage4_bridge": "Stage 4 先教 **Workflow Graph** 和实现它的 **Agent Framework**；Stage 7 再把同一张图做成可观测、可恢复的 production orchestration",
        "readme_route": "Stage 4 先看懂 **Workflow Graph**，再用 framework 把它做出来",
        "term_status": "**Loop Engineering** 是 IBM 明确标为 emerging practice 的新兴称呼",
    },
}

def without_closed_details(text: str) -> str:
    return re.sub(
        r"<details(?![^>]*\bopen\b)[^>]*>.*?</details>",
        "",
        text,
        flags=re.DOTALL | re.IGNORECASE,
    )


@pytest.mark.parametrize("locale,config", LOCALES.items())
def test_chapter_titles_put_the_concept_before_the_tool_and_production_details(
    locale: str, config: dict[str, object]
) -> None:
    stage4 = Path(config["stage4"]).read_text(encoding="utf-8")
    stage7 = Path(config["stage7"]).read_text(encoding="utf-8")
    assert stage4.startswith(str(config["stage4_title"]))
    assert stage7.startswith(str(config["stage7_title"]))
    assert str(config["umbrella"]) in without_closed_details(stage7)
    assert str(config["term_status"]) in without_closed_details(stage7)
    assert "taking shape in 2026" not in stage7
    assert "2026 年正在形成" not in stage7


@pytest.mark.parametrize("locale,config", LOCALES.items())
def test_five_control_questions_separate_the_running_structure_from_engineering_work(
    locale: str, config: dict[str, object]
) -> None:
    stage7 = without_closed_details(
        Path(config["stage7"]).read_text(encoding="utf-8")
    )
    assert str(config["structure_header"]) in stage7
    assert str(config["work_header"]) in stage7
    lines = stage7.splitlines()
    header_index = next(
        index
        for index, line in enumerate(lines)
        if str(config["structure_header"]) in line
    )
    assert lines[header_index].count("|") == 7
    assert lines[header_index + 1].count("|") == 7
    for structure, engineering in (
        ("Prompt", "Prompt Engineering"),
        ("Context", "Context Engineering"),
        ("Agent Harness", "Harness Engineering"),
        ("Agent Loop", "Loop Engineering"),
        ("Workflow Graph", "Production orchestration"),
    ):
        assert re.search(
            rf"\|[^\n]*\*\*{re.escape(structure)}\*\*[^\n]*\*\*{re.escape(engineering)}\*\*[^\n]*\|",
            stage7,
        ), (locale, structure, engineering)
    assert str(config["stage4_bridge"]) in stage7


@pytest.mark.parametrize("locale,config", LOCALES.items())
def test_stage4_teaches_workflow_graph_before_presenting_framework_as_the_toolbox(
    locale: str, config: dict[str, object]
) -> None:
    stage4 = without_closed_details(
        Path(config["stage4"]).read_text(encoding="utf-8")
    )
    graph_pos = stage4.index("**Workflow")
    framework_pos = stage4.index("**Framework")
    assert graph_pos < framework_pos, locale


@pytest.mark.parametrize("locale,config", LOCALES.items())
def test_readme_names_the_graph_before_the_framework_toolbox(
    locale: str, config: dict[str, object]
) -> None:
    readme = Path(config["readme"]).read_text(encoding="utf-8")
    assert str(config["readme_route"]) in readme, locale


def test_diagram_regeneration_contract_keeps_responsibilities_overlapping() -> None:
    prompt = DIAGRAM_PROMPT.read_text(encoding="utf-8")
    for marker in (
        "Prompt 與 Context 都進入 Harness",
        "上半部只畫一次 Agent run",
        "Loop Engineering 另外明寫 `Goal → Action → Observation → Adjustment`",
        "不得和 Harness 內的一次 Agent Loop 混成同一尺度",
        "Workflow Graph／Production Orchestration",
        "圖上以「不是五層」直接阻止嚴格層級誤讀",
        "Harness 包住 Agent Loop",
        "不得畫成 Harness 被 Loop 淘汰",
    ):
        assert marker in prompt
