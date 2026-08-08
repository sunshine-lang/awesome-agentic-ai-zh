# Function Schema 设计 Cheatsheet

> [繁體中文](./schema-design-cheatsheet.md) | **简体中文** | [English](./schema-design-cheatsheet.en.md)

> [Stage 3 — Tool Use & Agent 入门](../stages/03-tool-use-and-hello-agent.zh-Hans.md) 的补充参考。写 tool / function schema 时的 5 条黄金规则 + 5 个 anti-pattern。

LLM 怎么用你的 tool **80% 取决于 schema 写得好不好**——schema 模糊，再强的模型也会选错、传错。

---

## 5 条黄金规则

### 规则 1：description 是写给 LLM 看的，不是 docstring

LLM 只看 `description` 决定要不要叫这个 tool、什么时候叫。所以要：

- ✅ 写**情境**（when）跟**做什么**（what）：`"当用户问特定城市的天气时调用"`
- ❌ 不要写实作细节：`"使用 OpenWeather API v2.5 取得 JSON"`

对照：

```python
# 坏
"description": "Get weather data."

# 好
"description": "Get current weather for a specified city. Use this when the user asks about the current weather, temperature, humidity, or 'is it raining' for any specific location. Do NOT use for forecasts (use get_forecast instead) or historical data."
```

### 规则 2：参数用对 type，模糊处用 enum 收敛

LLM 对 `type: string` 自由度高、容易乱传。能用窄型别就用：

| 模糊 | 收敛 |
|---|---|
| `unit: string`（摄氏？华氏？kelvin？） | `unit: enum["celsius", "fahrenheit"]` |
| `priority: string`（low/中/HIGH？） | `priority: enum["low", "medium", "high"]` |
| `count: string`（"五个"？） | `count: integer` |
| `enabled: string`（"true" / "True"） | `enabled: boolean` |
| `tags: string`（"a,b,c"？JSON？） | `tags: array of string` |

### 规则 3：required vs optional 分清楚

- `required` 列**真的必要的**参数（少了 this tool 就跑不起来）
- 有默认值的放 `default`，不要列 required
- LLM 看到 required 多会“**自己编参数**”，所以 required 越少越好

```python
# 坏：把 timezone 列 required，LLM 会乱编「Asia/Taipei」即便用户没提到
"required": ["city", "timezone"]

# 好
"required": ["city"]
"properties": {
    "timezone": {"type": "string", "default": "UTC", "description": "..."}
}
```

### 规则 4：tool name + parameter name 要自说明

LLM 看到 `do_thing(x, y, z)` 跟看到 `get_weather(city, unit)` 用法完全不同。

- ✅ `get_user_profile(user_id)`
- ❌ `fetch(id)` 或 `process_data(input)`

动词开头，说清楚是 query / mutation / action。

### 规则 5：error 回传要让 LLM 可以恢复

LLM 看到错误信息后决定要 retry / 换工具 / 放弃。错误信息要结构化：

```json
{
    "error": "City not found",
    "code": "INVALID_CITY",
    "retry_hint": "Check spelling, or try a major city nearby"
}
```

而不是只回 `"Error 500"`——LLM 拿这个没招。

---

## 5 个常见 Anti-Pattern

### Anti-1：“万能工具”（God Tool）

```python
# 坏：一个 tool 做所有事
def do_database_op(operation: str, table: str, data: str) -> str:
    """Do anything with the database."""
```

LLM 会把错的 operation 配上对的 table 然后烂掉。**拆成 `query_users` / `create_order` / `update_inventory`** 等具体 tool，LLM 选择正确率大幅提升。

### Anti-2：description 是 docstring

```python
# 坏
"description": "GET /api/v2/weather endpoint. Returns JSON. See API docs."

# 好
"description": "Get current weather for a city. Returns temperature in C/F, humidity, and conditions."
```

LLM 不是程序，它要的是 **“这个 tool 什么时候有用”**。

### Anti-3：所有东西都是 string

```python
# 坏
{"properties": {
    "count": {"type": "string"},     # LLM 可能传 "five"
    "active": {"type": "string"},    # LLM 可能传 "yes"
    "list": {"type": "string"}       # LLM 可能传 "[a, b, c]" 或 "a, b, c"
}}

# 好
{"properties": {
    "count": {"type": "integer", "minimum": 1, "maximum": 100},
    "active": {"type": "boolean"},
    "list": {"type": "array", "items": {"type": "string"}}
}}
```

### Anti-4：没写范例

LLM 对 description **加上 example 比没加准确很多**。

```python
"description": "Search products by query string. Examples: 'laptop under $1000', 'red shoes size 10'. Do NOT use for product ID lookup (use get_product_by_id)."
```

### Anti-5：沉默的失败

Tool 失败只回 `null` 或 `{}`，LLM 以为成功，继续用空数据推论。**永远回**：

- 成功 → `{"success": true, "data": {...}}`
- 失败 → `{"success": false, "error": "...", "retry_hint": "..."}`

LLM 看到 `success: false` 就知道要处理错误，不会把空数据当答案编造。

---

## Schema 演进的小建议

- 加参数要 backward-compatible：新参数设 `default` 而不是 required
- 改参数含义 → 开新 tool（`get_weather_v2`），旧的标 deprecated 一段时间再下
- description 改了要重新测——LLM 行为对 description 敏感，连标点都会影响
- 上 production 前用 [promptfoo](https://github.com/promptfoo/promptfoo) eval 一下“LLM 在 5-10 个典型 query 是否选对 tool”

---

## 延伸阅读

- [Anthropic — Tool Use Guide](https://docs.anthropic.com/en/docs/agents-and-tools/tool-use/overview) — 官方 schema 规格
- [OpenAI — Function Calling](https://platform.openai.com/docs/guides/function-calling) — OpenAI 的 schema 规格（跟 Anthropic 略有差异）
- [Stage 3 — Tool Use & Agent 入门](../stages/03-tool-use-and-hello-agent.zh-Hans.md) — 主要动手练习
- [Stage 5.2 — MCP 基础](../stages/05-claude-code-ecosystem.zh-Hans.md#52--mcpmodel-context-protocol-基础) — MCP server 的 tool schema（跟 function calling schema 结构几乎相同）
