from openai import OpenAI
import json

from config import API_KEY, BASE_URL, MODEL

client = OpenAI(
    base_url=BASE_URL,
    api_key=API_KEY,
)

def llm_call(system_prompt, message, temperature=0.3):
    response = client.chat.completions.create(
    model=MODEL,
    messages=[
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": message}
    ],
    max_tokens=500,
    temperature=temperature,
    extra_body={
        "chat_template_kwargs": {
            "enable_thinking": False
        }
    },
    )
    return response.choices[0].message.content

promptC = """ 你是一个只输出合法JSON的API。
规则：
1. 禁止输出Markdown代码围栏或解释文字；
2. 顶层必须包含 success 和 data；
3. success 必须是布尔值；
4. data 必须包含 topic、summary、limitations；
5. limitations 必须是字符串数组；
6. 不允许出现其他字段。"""

print("dataA: "+llm_call("你是严谨的大学教授。", "解释什么是大语言模型。"))
print("dataB: "+llm_call("你是面向6岁儿童的科普老师。", "解释什么是大语言模型。"))

# 调用 LLM 生成 JSON 格式的输出（使用 promptC 要求只输出合法 JSON）
try:
    # 调用 llm_call，传入要求输出 JSON 的系统提示词
    C_output = llm_call(promptC, "解释什么是大语言模型。")
    
    # 尝试将输出解析为 JSON
    data = json.loads(C_output)
    print(data)
    
    # JSON Schema 验证：验证顶层结构
    # 1. 顶层必须只包含 success 和 data 两个字段
    assert set(data.keys()) == {"success", "data"}
    # 2. success 字段必须是布尔值
    assert isinstance(data["success"], bool)
    
    # 获取 data 字段内容
    result = data["data"]
    
    # 3. data 必须只包含 topic、summary、limitations 三个字段
    assert set(result.keys()) == {"topic", "summary", "limitations"}
    # 4. topic 必须是字符串类型
    assert isinstance(result["topic"], str)
    # 5. summary 必须是字符串类型
    assert isinstance(result["summary"], str)
    # 6. limitations 必须是列表类型
    assert isinstance(result["limitations"], list)
    # 7. limitations 列表中的每个元素必须是字符串
    assert all(isinstance(item, str) for item in result["limitations"])
    # 8. success 必须为 True
    assert data["success"]
    
    # 验证通过后输出提示信息
    print("JSON Schema 验证通过")
    print("JSON 验证通过")
    print(data["data"]["topic"])  # 输出主题

# 捕获 JSON 解析错误（当 LLM 输出的不是合法 JSON 时）
except json.JSONDecodeError as error:
    print(f"JSON 验证失败：{error}")

# 捕获键缺失错误（当 JSON 结构缺少必要字段时）
except KeyError as error:
    print(f"缺少字段：{error}")
