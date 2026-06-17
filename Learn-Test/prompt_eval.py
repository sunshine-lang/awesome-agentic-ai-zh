from dataclasses import dataclass
import re

from openai import OpenAI

from config import API_KEY, BASE_URL, MODEL


PROMPT_V1 = """
请为Python入门者制定一个7天学习计划，
目标是能够调用REST API并处理JSON。
"""

PROMPT_V2 = """
为 Python 入门者制定一个 7 天学习计划。
目标：能够使用 requests 调用 REST API，并解析 JSON。

要求：
1. 每天总计90分钟；
2. 每天必须包含：
   - 概念学习：20分钟
   - 编码练习：55分钟
   - 复盘检查：15分钟
3. 第7天完成一个综合项目；
4. 每项任务必须具体、可执行；
5. 不推荐课程、书籍或其他学习资源；
6. 总字数不超过800个中文字符；
7. 直接从“第1天”开始，不写前言、总结、表格或完整代码。
"""

PROMPT_V3 = """
为 Python 入门者制定一个7天学习计划。
目标：能够使用 requests 调用 REST API，并解析 JSON。

严格要求：
1. 完整输出第1天至第7天；
2. 每天必须严格使用以下四行格式：

第N天：主题
学习（20分钟）：具体内容
编码（55分钟）：具体任务
复盘（15分钟）：检查标准

3. 第7天完成一个综合项目；
4. 每项任务必须具体、可执行；
5. 每天不超过100个中文字符；
6. 全文不超过800个字符；
7. 不写前言、总结、表格、完整代码或外部资源；
8. 不得省略或修改时间数字。
"""

PROMPT_V4 = """
为已会基础 Python 的入门者制定一个7天学习计划。
目标：能够使用 requests 调用 REST API，并解析 JSON。

严格要求：
1. 完整输出第1天至第7天；
2. 每天必须严格使用以下四行格式：
天标题必须严格写作“第1天”“第2天”直到“第7天”，数字前后不得有空格。

第N天：主题
学习（20分钟）：具体内容
编码（55分钟）：具体任务
复盘（15分钟）：检查标准

3. 第7天完成综合项目：GitHub 用户信息查询工具；
4. 每天任务必须围绕 JSON、HTTP、requests、错误处理逐步递进；
5. 每天不超过100个中文字符；
6. 全文不超过800个字符；
7. 不写前言、总结、表格、完整代码或外部资源；
8. 不得省略或修改时间数字。
"""

PROMPT_V5 = """
为已会基础 Python 的入门者制定一个7天学习计划。
目标：能够使用 requests 调用 GitHub REST API，并解析 JSON。

严格要求：
1. 完整输出第1天至第7天；
2. 每天必须严格使用以下四行格式：
3. 禁止出现“文档”“课程”“书籍”“官网”“教程”等外部资料词。

第N天：主题
学习（20分钟）：具体概念
编码（55分钟）：当天必须产出的脚本或函数
复盘（15分钟）：可执行验收标准

3. 第7天综合项目必须是：GitHub 用户信息查询工具；
4. 每天任务必须围绕 HTTP、JSON、requests、认证、错误处理逐步递进；
5. 不依赖外部课程、书籍或文档；
6. 每天不超过100个中文字符；
7. 全文不超过800个字符；
8. 不写前言、总结、表格、完整代码；
9. 不得省略或修改时间数字。
"""


@dataclass
class EvalResult:
    version: str
    finish_reason: str
    chars: int
    completion_tokens: int
    passed: bool
    failure_reason: str
    answer: str


def call_model(client, prompt):
    return client.chat.completions.create(
        model=MODEL,
        messages=[{"role": "user", "content": prompt}],
        temperature=0,
        max_tokens=2000,
        extra_body={"chat_template_kwargs": {"enable_thinking": False}},
    )


def count_time_field(answer, label, minutes):
    pattern = rf"{label}\s*[（(]\s*{minutes}\s*分钟\s*[）)]"
    return len(re.findall(pattern, answer))


def validate_basic(answer):
    problems = []
    if not re.search(r"第\s*7\s*天", answer):
        problems.append("未完整输出到第7天")
    if "综合项目" not in answer:
        problems.append("第7天综合项目不明确")
    if len(answer) > 800:
        problems.append(f"字符数超过800：{len(answer)}")
    return problems


def validate_strict_format(answer, check_banned_words=False):
    problems = []

    if len(answer) > 800:
        problems.append(f"字符数超过800：{len(answer)}")

    for day in range(1, 8):
        if not re.search(rf"第\s*{day}\s*天", answer):
            problems.append(f"缺少第{day}天")

    learning_count = count_time_field(answer, "学习", 20)
    coding_count = count_time_field(answer, "编码", 55)
    review_count = count_time_field(answer, "复盘", 15)

    if learning_count != 7:
        problems.append(f"学习字段数量不等于7：{learning_count}")
    if coding_count != 7:
        problems.append(f"编码字段数量不等于7：{coding_count}")
    if review_count != 7:
        problems.append(f"复盘字段数量不等于7：{review_count}")

    if check_banned_words:
        for banned in ["文档", "课程", "书籍", "官网", "教程"]:
            if banned in answer:
                problems.append(f"出现外部资料词：{banned}")

    return problems


def validate_answer(version, answer, finish_reason):
    problems = []

    if finish_reason != "stop":
        problems.append(f"finish_reason不是stop：{finish_reason}")

    if version in {"V1", "V2"}:
        problems.extend(validate_basic(answer))
    elif version in {"V3", "V4"}:
        problems.extend(validate_strict_format(answer))
    elif version == "V5":
        problems.extend(validate_strict_format(answer, check_banned_words=True))

    return problems


def evaluate_prompt(client, version, prompt):
    response = call_model(client, prompt)
    answer = response.choices[0].message.content
    finish_reason = response.choices[0].finish_reason
    problems = validate_answer(version, answer, finish_reason)

    return EvalResult(
        version=version,
        finish_reason=finish_reason,
        chars=len(answer),
        completion_tokens=response.usage.completion_tokens,
        passed=not problems,
        failure_reason="；".join(problems) if problems else "-",
        answer=answer,
    )


def print_markdown_table(results):
    print("| 版本 | finish_reason | 字符数 | 输出tokens | 是否通过 | 主要失败原因 |")
    print("|---|---|---:|---:|---|---|")
    for result in results:
        print(
            f"| {result.version} | {result.finish_reason} | {result.chars} | "
            f"{result.completion_tokens} | {'是' if result.passed else '否'} | "
            f"{result.failure_reason} |"
        )


def main():
    client = OpenAI(base_url=BASE_URL, api_key=API_KEY)
    prompts = [
        ("V1", PROMPT_V1),
        ("V2", PROMPT_V2),
        ("V3", PROMPT_V3),
        ("V4", PROMPT_V4),
        ("V5", PROMPT_V5),
    ]

    results = []
    for version, prompt in prompts:
        print(f"正在评估 {version}...")
        results.append(evaluate_prompt(client, version, prompt))

    print()
    print_markdown_table(results)

    print("\n--- V5 输出 ---")
    print(results[-1].answer)


if __name__ == "__main__":
    main()
