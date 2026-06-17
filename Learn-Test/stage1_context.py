from openai import OpenAI

from config import API_KEY, BASE_URL, MODEL

client = OpenAI(
    base_url=BASE_URL,
    api_key=API_KEY,
)

messages = [
    {"role": "user", "content": "用100字解释大语言模型，并提醒它可能出错。"}
]

first = client.chat.completions.create(
    model=MODEL,
    messages=messages,
    temperature=0,
    extra_body={"chat_template_kwargs": {"enable_thinking": False}},
)

answer = first.choices[0].message.content
messages.append({"role": "assistant", "content": answer})
messages.append({"role": "user", "content": "把刚才的解释缩短到50字以内。"})

second = client.chat.completions.create(
    model=MODEL,
    messages=messages,
    temperature=0,
    extra_body={"chat_template_kwargs": {"enable_thinking": False}},
)

print(second.choices[0].message.content)
print(second.usage)

print("第一轮：", first.usage)
print("第二轮：", second.usage)
