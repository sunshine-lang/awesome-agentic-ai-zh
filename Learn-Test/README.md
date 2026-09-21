# Learn-Test

**繁體中文** | [简体中文](README.zh-Hans.md) | [English](README.en.md)

本目錄包含 Stage 0-2 的本地練習腳本，用於記錄 Python API 基礎、LLM API 調用、Prompt Engineering 和簡單評測實驗。

這些腳本默認調用本地 OpenAI-compatible oMLX 服務。模型配置集中放在 `.env.template`，並由 `config.py` 統一讀取。

## 環境配置

1. 複製模板文件：

```bash
cp .env.template .env
```

2. 如果你的 oMLX 服務地址、API key 或模型名不同，修改 `.env`：

```env
OMLX_BASE_URL=http://127.0.0.1:8429/v1
OMLX_API_KEY=010209
OMLX_MODEL=Qwen3.5-9B-MLX-4bit
```

3. 運行 Stage 1 或 Stage 2 腳本前，先啓動 oMLX。

4. 建議從本目錄運行腳本：

```bash
cd Learn-Test
python stage1_hello.py
```

## 文件說明

| 文件 | 作用 |
|---|---|
| `.env.template` | 本地 oMLX 配置模板。複製爲 `.env` 後可按機器環境修改。 |
| `config.py` | 讀取 `.env.template` 和 `.env`，並暴露 `BASE_URL`、`API_KEY`、`MODEL`。 |
| `stage0.py` | Stage 0 練習：調用 GitHub REST API、解析 JSON、處理請求錯誤。 |
| `stage1_hello.py` | Stage 1 練習：完成一次基礎 LLM 調用，並查看響應元數據。 |
| `stage1_context.py` | Stage 1 練習：演示 API 多輪上下文需要顯式傳入歷史消息。 |
| `stage1_retry.py` | Stage 1 練習：封裝 LLM 調用，包含 prompt 校驗、usage 日誌和連接錯誤重試。 |
| `stage2_prompt.py` | Stage 2 練習：針對 7 天學習計劃任務迭代 V1-V5 prompt。 |
| `stage2_fewshot.py` | Stage 2 練習：比較 system prompt，並驗證 JSON 輸出。 |
| `stage2_fewshot2.py` | Stage 2 練習：運行 few-shot 情緒分類評測。 |
| `stage2_cot.py` | Stage 2 練習：比較直接回答、詳細推理和先檢查條件的 prompt。 |
| `prompt_eval.py` | Stage 2 總驗收：評估 V1-V5 prompt 輸出，並打印 Markdown 表格。 |

## 建議運行順序

按下面順序運行：

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

`stage0.py` 會訪問 GitHub 公共 API。如果設置了 `GITHUB_TOKEN`，腳本會把它作爲認證 header 發送：

```bash
export GITHUB_TOKEN=...
```

## 配置規則

練習腳本中不要硬編碼本地模型配置。統一使用：

```python
from config import API_KEY, BASE_URL, MODEL
```

配置來源順序：

1. `.env.template`：隨練習文件提交的默認配置。
2. `.env`：本機私有覆蓋配置。
3. 已存在的 shell 環境變量；如果 `.env` 存在，會覆蓋同名變量。

## 注意事項

- `config.py` 有意保持輕量，不依賴 `python-dotenv`。
- Stage 1 和 Stage 2 腳本假設本地服務兼容 OpenAI API。
- 即使設置 `temperature=0`，不同模型或推理後端仍可能產生輕微輸出差異。
