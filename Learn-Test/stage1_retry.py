from openai import OpenAI, APIConnectionError   
import time

from config import API_KEY, BASE_URL, MODEL

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
def call_with_retry(model=MODEL, messages=messages, max_tokens=500, max_retries=3):
    """
    调用 AI 模型，支持重试。
    
    参数：
        model: 模型名称
        messages: 消息列表
        max_tokens: 最大 token 数
        max_retries: 最大重试次数（默认3次）
    
    返回：
        成功时返回响应，超过重试次数后抛出异常
    """
    for attempt in range(1, max_retries + 1):
        try:
            print(f"第 {attempt} 次尝试...")
            if attempt < 3:
                raise ConnectionError("模拟网络暂时中断")
            response = client.chat.completions.create(
                model=model,
                messages=messages,
                max_tokens=max_tokens,
                extra_body={
                    "chat_template_kwargs": {
                        "enable_thinking": False
                    }
                },
            )
            print(f"第 {attempt} 次尝试成功！")
            return response
        except ConnectionError as e:
            print(f"第 {attempt} 次尝试失败: {e}")
            # 如果不是最后一次尝试，等待后重试
            if attempt < max_retries:
                wait_time = attempt  # 等待时间依次为 1, 2 秒
                print(f"等待 {wait_time} 秒后重试...")
                time.sleep(wait_time)
            else:
                # 超过最大重试次数，抛出异常
                raise Exception(f"已尝试 {max_retries} 次，均失败") from e

def ask_llm(prompt, model=MODEL, temperature=0.3, max_tokens=500, max_retries=3):
    """
    调用 oMLX；默认关闭 thinking；对连接错误最多重试三次；返回回答文本；同时打印 token 用量、耗时和结束原因；空 prompt 时抛出 ValueError；不在函数中硬编码具体问题。
    """
    if not prompt or not prompt.strip():
        raise ValueError("prompt 不能为空")

    messages = [{"role": "user", "content": prompt}]
    start_time = time.time()

    for attempt in range(1, max_retries + 1):
        try:
            print(f"第 {attempt} 次尝试...")
            response = client.chat.completions.create(
                model=model,
                messages=messages,
                max_tokens=max_tokens,
                temperature=temperature,
                extra_body={
                    "chat_template_kwargs": {
                        "enable_thinking": False
                    }
                },
            )
            elapsed = time.time() - start_time
            print(f"第 {attempt} 次尝试成功！")
            print(f"token 用量: {response.usage.total_tokens}")
            print(f"输入 token 数: {response.usage.prompt_tokens}")
            print(f"输出 token 数: {response.usage.completion_tokens}")
            print(f"耗时: {elapsed:.2f} 秒")
            print(f"结束原因: {response.choices[0].finish_reason}")
            return response.choices[0].message.content
        except APIConnectionError as e:
            print(f"第 {attempt} 次尝试失败: {e}")
            # 如果不是最后一次尝试，等待后重试
            if attempt < max_retries:
                wait_time = attempt  # 等待时间依次为 1, 2 秒
                print(f"等待 {wait_time} 秒后重试...")
                time.sleep(wait_time)
            else:
                # 超过最大重试次数，抛出异常
                raise Exception(f"已尝试 {max_retries} 次，均失败") from e

if __name__ == "__main__":
    ask_llm("用一句话介绍Python")
    try:
        ask_llm("   ")
    except ValueError as error:
        print(f"验证通过：{error}")
