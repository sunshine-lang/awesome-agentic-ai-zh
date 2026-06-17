from stage2_fewshot2 import llm_call

TEST_CASES = [
    {
        "question": "商店先将商品涨价20%，随后打八折。最终价格相对原价变化多少？",
        # "answer": "降低4%",
    },
    {
        "question": "5台机器5分钟生产5个零件。100台机器生产100个零件需要几分钟？",
        # "answer": "5分钟",
    },
    {
        "question": (
            "盒子里有红、蓝、绿球各若干。红球比蓝球多2个，"
            "绿球是蓝球的2倍，总共17个。蓝球有多少个？"
        ),
        # "answer": "5个",
    },
]

# 比较三种解题方式：
# A：只输出答案
# B：一步一步思考并输出答案（Chain of Thought）
# C：先检查题目条件是否一致，再计算；只输出结论和关键依据
# 
# 注意：第三题数据有问题：蓝球=x, 红球=x+2, 绿球=2x, 总数=4x+2=17, x=3.75
# 它没有整数解，优秀模型应指出题目条件不一致，而不是硬猜答案

# 三种系统提示词
SYSTEM_PROMPTS = {
    "A": "你是一个数学问题解决者。请直接给出最终答案，不要解释。",
    "B": "你是一个数学问题解决者。请一步一步思考并详细解释你的解题过程，最后给出答案。",
    "C": "你是一个严谨的数学问题解决者。请先检查题目条件是否一致（如是否存在矛盾、是否有解等），然后再进行计算。只输出结论和关键依据。如果题目条件不一致，请明确指出。"
}

# 循环处理每个测试用例
for i, case in enumerate(TEST_CASES, 1):
    print(f"="*60)
    print(f"问题 {i}：{case['question']}")
    print()
    
    # 使用三种方式分别解答
    for mode, system_prompt in SYSTEM_PROMPTS.items():
        response = llm_call(
            system_prompt,
            case["question"],
            temperature=0,
            max_tokens=500,
        )
        print(f"方式{mode}：")
        print(response)
        print()
    print()
