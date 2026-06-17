from openai import OpenAI

from config import API_KEY, BASE_URL, MODEL

# 检查模型列表
# curl --noproxy "*" "$OMLX_BASE_URL/models" \
#   -H "Authorization: Bearer $OMLX_API_KEY"

PROMPT = """
任务：面向零基础学生解释大语言模型。

格式：
1. 恰好三个编号要点；
2. 一个生活类比；
3. 结尾提醒回答可能出错；
4. 不超过300字，不使用表格。

禁止：
- 不得声称模型读过所有书；
- 不得声称模型真正理解或一定正确；
- 不得把模型描述成知识数据库。
"""

client = OpenAI(
    base_url=BASE_URL,
    api_key=API_KEY,
)

messages = [
    {
        "role": "user",
        "content": PROMPT
    }
]

response = client.chat.completions.create(
    model=MODEL,
    messages=messages,
    max_tokens=500,
    temperature=1.2,
    extra_body={
        "chat_template_kwargs": {
            "enable_thinking": False
        }
    },
)

print(response.choices[0].message.content)
print(response.model)
print(response.usage)
print(response.choices[0].finish_reason)

# 循环调用 AI 模型，比较不同的温度
# for temperature in [0.0, 0.7, 1.2]:
#     print(f"\n===== temperature={temperature} =====")

#     for run in range(1, 4):
#         response = client.chat.completions.create(
#             model=MODEL,
#             messages=messages,
#             temperature=temperature,
#             max_tokens=500,
#             extra_body={
#                 "chat_template_kwargs": {
#                     "enable_thinking": False
#                 }
#             },
#         )

#         print(f"\n--- 第 {run} 次 ---")
#         print(response.choices[0].message.content)
#         print(response.usage)
