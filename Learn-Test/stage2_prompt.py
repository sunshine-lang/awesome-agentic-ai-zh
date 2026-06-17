from openai import OpenAI
import re

from config import API_KEY, BASE_URL, MODEL

openai = OpenAI(
    base_url=BASE_URL,
    api_key=API_KEY,
)

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

第1天：主题
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


response = openai.chat.completions.create(
    model=MODEL,
    messages=[
        {"role": "user", "content": PROMPT_V5}
    ],
    temperature=0,
    max_tokens=2000,
    extra_body={
        "chat_template_kwargs": {
            "enable_thinking": False
        }
    },
)
# PROMPT_V2 格式验证
# answer = response.choices[0].message.content
# print(answer)
# print("字符数：", len(answer))
# print("输出 tokens：", response.usage.completion_tokens)
# print("结束原因：", response.choices[0].finish_reason)

# PROMPT_V3 / PROMPT_V4 / PROMPT_V5 格式验证
answer = response.choices[0].message.content

assert response.choices[0].finish_reason == "stop", response.choices[0].finish_reason
assert len(answer) <= 800, f"字符数超限：{len(answer)}"

for day in range(1, 8):
    assert re.search(rf"第\s*{day}\s*天", answer), (
        f"缺少第{day}天，实际输出：\n{answer}"
    )

learning_count = len(re.findall(r"学习\s*[（(]\s*20\s*分钟\s*[）)]", answer))
coding_count = len(re.findall(r"编码\s*[（(]\s*55\s*分钟\s*[）)]", answer))
review_count = len(re.findall(r"复盘\s*[（(]\s*15\s*分钟\s*[）)]", answer))

assert learning_count == 7, f"学习字段数量不等于7：{learning_count}\n实际输出：\n{answer}"
assert coding_count == 7, f"编码字段数量不等于7：{coding_count}\n实际输出：\n{answer}"
assert review_count == 7, f"复盘字段数量不等于7：{review_count}\n实际输出：\n{answer}"

for banned in ["文档", "课程", "书籍", "官网", "教程"]:
    assert banned not in answer, f"出现外部资料词：{banned}"

print("V5格式验证通过")
print(answer)
print("字符数：", len(answer))
print("输出 tokens：", response.usage.completion_tokens)
print("结束原因：", response.choices[0].finish_reason)
