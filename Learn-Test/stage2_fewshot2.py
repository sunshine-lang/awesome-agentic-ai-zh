import json
from openai import OpenAI

from config import API_KEY, BASE_URL, MODEL

client = OpenAI(
    base_url=BASE_URL,
    api_key=API_KEY,
)


TEST_CASES = [
    # 明确正面
    ("物流很快，包装完整，商品质量也很好。", "正面"),
    ("用了一个月依然很稳定，完全超出预期。", "正面"),

    # 明确负面
    ("收到时屏幕已经碎了，客服也不处理。", "负面"),
    ("质量非常差，用了两天就坏了。", "负面"),

    # 明确中立
    ("商品已经收到，颜色是黑色的。", "中立"),
    ("功能和商品页面描述基本一致。", "中立"),

    # 混合评价
    ("质量不错，但是价格有点贵。", "中立"),
    ("外观很好看，可惜续航时间太短。", "中立"),
    ("物流很慢，不过商品本身还不错。", "中立"),

    # 反讽或含蓄表达
    ("真耐用，刚拆开包装按钮就掉了。", "负面"),
    ("客服回复得真快，三天了还没有消息。", "负面"),
    ("这个价格能买到这种质量，也算长见识了。", "负面"),
]

EXAMPLES = [
    ("体验很好，值得推荐。", "正面"),
    ("到货时已经损坏，完全无法使用。", "负面"),
    ("商品已经收到，型号为B20。", "中立"),
    ("包装不错，但物流有点慢。", "中立"),
    ("价格偏贵，不过质量还可以。", "中立"),
    ("说好的秒回，结果两天没人理。", "负面"),
]

def llm_call(system_prompt, message, temperature, max_tokens):
    response = client.chat.completions.create(
    model=MODEL,
    messages=[
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": message}
    ],
    max_tokens=max_tokens,
    temperature=temperature,
    extra_body={
        "chat_template_kwargs": {
            "enable_thinking": False
        }
    },
    )
    return response.choices[0].message.content


def classify(text, examples=EXAMPLES):
    prompt = """
        任务：判断用户评价的情绪。

        标签定义：
        - 正面：整体表达满意、认可或推荐
        - 负面：整体表达不满、批评或失望
        - 中立：没有明显态度，或正负评价基本平衡

        只允许输出：正面、负面、中立

        分类规则：
        - 同时包含明确优点和缺点，且没有明显总体倾向：中立
        - 转折词“但是、不过、可惜”后的内容可能更能体现最终态度
        - 反讽应按真实含义分类，不按表面褒义词分类

        - 仅陈述商品符合描述、已经收到、颜色型号等事实：中立
        
        - 同时出现优缺点：
          - 明确表示总体满意：正面
          - 明确表示总体不满：负面
          - 没有总体结论：中立
        - 不根据转折词机械判断，优先看总体态度
        """

    if examples:
        prompt += "\n示例：\n"
        for example_text, label in examples:
            prompt += f"{example_text} → {label}\n"

    prompt += f"\n待分类评价：{text}\n标签："

    return llm_call(
        prompt,
        text,
        temperature=0,
        max_tokens=10,
    ).strip()


if __name__ == "__main__":
    correct = 0

    for text, expected in TEST_CASES:
        predicted = classify(text)
        passed = predicted == expected
        correct += passed
        print(
            f"评价：{text}\n"
            f"预期：{expected}｜预测：{predicted}｜"
            f"{'通过' if passed else '失败'}\n"
        )

    accuracy = correct / len(TEST_CASES)
    print(f"准确率：{correct}/{len(TEST_CASES)} = {accuracy:.1%}")
