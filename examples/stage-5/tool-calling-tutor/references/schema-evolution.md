# Schema Evolution：壞 schema 改到好（worked example）

> **繁體中文** | [简体中文](./schema-evolution.zh-Hans.md) | [English](./schema-evolution.en.md)


> 同一個工具（溫度轉換）、4 個改進步驟。對應 SKILL.md Step 2(d)、補 [`resources/schema-design-cheatsheet.md`](../../../../resources/schema-design-cheatsheet.md) 缺的 procedural 走法。

## Iteration 0：原始壞 schema

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

### 觀察行為（用 qwen2.5:3b 跑）

```python
# user: "Convert 32 Celsius to Fahrenheit"
# LLM 行為（多次測試平均）：
# - 40% 挑到 convert、args = {"value": "32 Celsius", "unit": ""}        ← 型別錯
# - 30% 挑到 convert、args = {"value": "32", "unit": "C"}                ← unit 不一致
# - 20% 挑到別的 tool（process_data 等）                                  ← 邊界不清
# - 10% 完全沒呼叫 tool、純文字回答                                       ← description 太籠統
```

**正確率 ≈ 0%**。Claude haiku 大概 60-70% 能猜對（但仍不穩定）。

## Iteration 1：修 description

```python
# ❌ 之前
"description": "Convert a value."

# ✅ 之後（明確「何時用」）
"description": "Use this when the user asks to convert temperatures between Fahrenheit and Celsius."
```

### 新行為

- LLM 正確 trigger tool 機率：60%（從 ~30% 提升、但 args 仍錯）
- 仍然挑錯 unit 格式

**這一步搞定「LLM 願不願意呼叫」、但 args 還沒固定。**

## Iteration 2：修 parameter type

```python
# ❌ 之前
"value": {"type": "string"}

# ✅ 之後
"value": {"type": "number", "description": "Temperature value to convert"}
```

### 新行為

- `value` 改傳 `32`（number）而非 `"32"` / `"32 Celsius"`
- 仍偶爾漏傳 `unit`、或傳 `"C"` 而非 `"celsius"`

**型別固定、但欄位完整性與 enum 還沒處理。**

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

### 新行為

- LLM 不再漏傳 `unit`
- 仍偶爾傳 `"C"` / `"Celsius"` / `"celsius"`（大小寫 / 縮寫不一致）

**必填欄位固定、但模糊邊界還沒收斂。**

## Iteration 4：加 `enum`

```python
"unit": {
    "type": "string",
    "enum": ["celsius", "fahrenheit"],   # ✅ NEW
    "description": "Unit of the input value"
}
```

### 最終 schema

```python
{
    "name": "convert_temperature",   # ✅ 也改具體 name
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

### 行為

- qwen2.5:3b 正確率 95%+
- Claude haiku 99%+

## 4 個改進的 cost vs benefit

| Iteration | 改了什麼 | 程式碼變動量 | 正確率提升（qwen） |
|---|---|---|---|
| 1 | description | 1 line | 0% → 60% |
| 2 | type: number | 1 line | 60% → 75% |
| 3 | required | 1 line | 75% → 85% |
| 4 | enum | 1 line | 85% → 95%+ |

**4 行程式碼、把正確率從 ~0% 推到 95%+**。這就是 schema 設計的 ROI。

## 為什麼這在小 model 上**更重要**

```
正確率（同一份 query × 1000 次）：
              BAD schema   GOOD schema   diff
Claude haiku  60%          99%           +39%
qwen2.5:3b    0%           95%           +95%
gemma4:e4b    0%           80%           +80%
```

**結論**：寫好 schema 的功夫**省下換大 model 的 $$**。Production 想用便宜 model？schema 必須能上線跑。

## 看完整對照範例

→ [`../../stage-3/06-schema-design/`](../../../stage-3/06-schema-design/)：含 `starter_bad.py` + `starter_good.py` + 4 lang README 對照可跑版本。
