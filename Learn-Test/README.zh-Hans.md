# Learn-Test

[繁體中文](README.md) | **简体中文** | [English](README.en.md)

本目录包含 Stage 0-2 的本地练习脚本，用于记录 Python API 基础、LLM API 调用、Prompt Engineering 和简单评测实验。

这些脚本默认调用本地 OpenAI-compatible oMLX 服务。模型配置集中放在 `.env.template`，并由 `config.py` 统一读取。

## 环境配置

1. 复制模板文件：

```bash
cp .env.template .env
```

2. 如果你的 oMLX 服务地址、API key 或模型名不同，修改 `.env`：

```env
OMLX_BASE_URL=http://127.0.0.1:8429/v1
OMLX_API_KEY=010209
OMLX_MODEL=Qwen3.5-9B-MLX-4bit
```

3. 运行 Stage 1 或 Stage 2 脚本前，先启动 oMLX。

4. 建议从本目录运行脚本：

```bash
cd Learn-Test
python stage1_hello.py
```

## 文件说明

| 文件 | 作用 |
|---|---|
| `.env.template` | 本地 oMLX 配置模板。复制为 `.env` 后可按机器环境修改。 |
| `config.py` | 读取 `.env.template` 和 `.env`，并暴露 `BASE_URL`、`API_KEY`、`MODEL`。 |
| `stage0.py` | Stage 0 练习：调用 GitHub REST API、解析 JSON、处理请求错误。 |
| `stage1_hello.py` | Stage 1 练习：完成一次基础 LLM 调用，并查看响应元数据。 |
| `stage1_context.py` | Stage 1 练习：演示 API 多轮上下文需要显式传入历史消息。 |
| `stage1_retry.py` | Stage 1 练习：封装 LLM 调用，包含 prompt 校验、usage 日志和连接错误重试。 |
| `stage2_prompt.py` | Stage 2 练习：针对 7 天学习计划任务迭代 V1-V5 prompt。 |
| `stage2_fewshot.py` | Stage 2 练习：比较 system prompt，并验证 JSON 输出。 |
| `stage2_fewshot2.py` | Stage 2 练习：运行 few-shot 情绪分类评测。 |
| `stage2_cot.py` | Stage 2 练习：比较直接回答、详细推理和先检查条件的 prompt。 |
| `prompt_eval.py` | Stage 2 总验收：评估 V1-V5 prompt 输出，并打印 Markdown 表格。 |

## 建议运行顺序

按下面顺序运行：

```bash
python stage0.py
python stage1_hello.py
python stage1_context.py
python stage1_retry.py
python stage2_fewshot.py
python stage2_fewshot2.py
python stage2_cot.py
python stage2_prompt.py
python prompt_eval.py
```

`stage0.py` 会访问 GitHub 公共 API。如果设置了 `GITHUB_TOKEN`，脚本会把它作为认证 header 发送：

```bash
export GITHUB_TOKEN=...
```

## 配置规则

练习脚本中不要硬编码本地模型配置。统一使用：

```python
from config import API_KEY, BASE_URL, MODEL
```

配置来源顺序：

1. `.env.template`：随练习文件提交的默认配置。
2. `.env`：本机私有覆盖配置。
3. 已存在的 shell 环境变量；如果 `.env` 存在，会覆盖同名变量。

## 注意事项

- `config.py` 有意保持轻量，不依赖 `python-dotenv`。
- Stage 1 和 Stage 2 脚本假设本地服务兼容 OpenAI API。
- 即使设置 `temperature=0`，不同模型或推理后端仍可能产生轻微输出差异。
