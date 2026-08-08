# Schema Evolution：坏 schema 改到好（worked example）

> [繁體中文](./schema-evolution.md) | **简体中文** | [English](./schema-evolution.en.md)


> 同一个工具（温度转换）、4 个改进步骤。对应 SKILL.md Step 2(d)、补 [`resources/schema-design-cheatsheet.zh-Hans.md`](../../../../resources/schema-design-cheatsheet.zh-Hans.md) 缺的 procedural 走法。

## Iteration 0：原始坏 schema

```python
{
    "name": "convert",
    "description": "Convert a value.",
    "parameters": {
        "type": "object",
        "properties": {
            "value": {"type": "string"},
            "unit": {"type": "string"}
        }
    }
}
```

### 观察行为（用 qwen2.5:3b 跑）

```python
# user: "Convert 32 Celsius to Fahrenheit"
# LLM 行为（多次测试平均）：
# - 40% 挑到 convert、args = {"value": "32 Celsius", "unit": ""}        ← 类型错
# - 30% 挑到 convert、args = {"value": "32", "unit": "C"}                ← unit 不一致
# - 20% 挑到别的 tool（process_data 等）                                  ← 边界不清
# - 10% 完全没调用 tool、纯文字回答                                       ← description 太笼统
```

**正确率 ≈ 0%**。Claude haiku 大概 60-70% 能猜对（但仍不稳定）。

## Iteration 1：修 description

```python
# ❌ 之前
"description": "Convert a value."

# ✅ 之后（明确「何时用」）
"description": "Use this when the user asks to convert temperatures between Fahrenheit and Celsius."
```

### 新行为

- LLM 正确 trigger tool 机率：60%（从 ~30% 提升、但 args 仍错）
- 仍然挑错 unit 格式

**这一步搞定“LLM 愿不愿意调用”、但 args 还没固定。**

## Iteration 2：修 parameter type

```python
# ❌ 之前
"value": {"type": "string"}

# ✅ 之后
"value": {"type": "number", "description": "Temperature value to convert"}
```

### 新行为

- `value` 改传 `32`（number）而非 `"32"` / `"32 Celsius"`
- 仍偶尔漏传 `unit`、或传 `"C"` 而非 `"celsius"`

**类型固定、但字段完整性与 enum 还没处理。**

## Iteration 3：加 `required`

```python
"parameters": {
    "type": "object",
    "properties": {
        "value": {"type": "number", "description": "Temperature value to convert"},
        "unit": {"type": "string"}
    },
    "required": ["value", "unit"]   # ✅ NEW
}
```

### 新行为

- LLM 不再漏传 `unit`
- 仍偶尔传 `"C"` / `"Celsius"` / `"celsius"`（大小写 / 缩写不一致）

**必填字段固定、但模糊边界还没收敛。**

## Iteration 4：加 `enum`

```python
"unit": {
    "type": "string",
    "enum": ["celsius", "fahrenheit"],   # ✅ NEW
    "description": "Unit of the input value"
}
```

### 最终 schema

```python
{
    "name": "convert_temperature",   # ✅ 也改具体 name
    "description": "Use this when the user asks to convert temperatures between Fahrenheit and Celsius.",
    "parameters": {
        "type": "object",
        "properties": {
            "value": {"type": "number", "description": "Temperature value to convert"},
            "unit": {
                "type": "string",
                "enum": ["celsius", "fahrenheit"],
                "description": "Unit of the input value"
            }
        },
        "required": ["value", "unit"]
    }
}
```

### 行为

- qwen2.5:3b 正确率 95%+
- Claude haiku 99%+

## 4 个改进的 cost vs benefit

| Iteration | 改了什么 | 程序码变动量 | 正确率提升（qwen） |
|---|---|---|---|
| 1 | description | 1 line | 0% → 60% |
| 2 | type: number | 1 line | 60% → 75% |
| 3 | required | 1 line | 75% → 85% |
| 4 | enum | 1 line | 85% → 95%+ |

**4 行程序码、把正确率从 ~0% 推到 95%+**。这就是 schema 设计的 ROI。

## 为什么这在小 model 上**更重要**

```
正确率（同一份 query × 1000 次）：
              BAD schema   GOOD schema   diff
Claude haiku  60%          99%           +39%
qwen2.5:3b    0%           95%           +95%
gemma4:e4b    0%           80%           +80%
```

**结论**：写好 schema 的功夫**省下换大 model 的 $$**。Production 想用便宜 model？schema 必须能上线跑。

## 看完整对照范例

→ [`../../stage-3/06-schema-design/`](../../../stage-3/06-schema-design/)：含 `starter_bad.py` + `starter_good.py` + 4 lang README 对照可跑版本。
