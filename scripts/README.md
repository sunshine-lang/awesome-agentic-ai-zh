# scripts/

維護用的工具腳本 + distribution build。

## `check-links.py` — 檢查連結是否失效

掃描所有 markdown 檔案中的 URL，回報 4xx / 5xx / timeout。

```bash
# 一次性檢查全部
python scripts/check-links.py

# 只查 GitHub repos（最容易 404 的）
python scripts/check-links.py --fast

# 只印失敗，不印 OK
python scripts/check-links.py --quiet
```

退出 code：失敗時 = 1，全部 OK = 0。可以接 CI。

依賴：`pip install requests`

## `refresh-stars.py` — 比對 markdown 內標註的 stars 跟實際

```bash
# 列出所有差距 ≥ 10% 的 entry
python scripts/refresh-stars.py

# 設定門檻（譬如 ≥ 20%）
python scripts/refresh-stars.py --threshold 20

# CI 模式（差距超過門檻就退 code 1）
python scripts/refresh-stars.py --check
```

依賴：`pip install requests` + `gh` CLI（`gh auth login`）

## 建議的維護節奏

- **每月**：跑一次 `check-links.py --fast` 看 GitHub repo 連結有沒有 404
- **星數刷新**：`weekly-catalog-refresh` CI 每週自動跑 `refresh-stars.py`（手動補跑可看大幅成長 / 衰退的 repo）
- **每半年**：跑一次完整 `check-links.py`（包含非 GitHub 連結）

可以接到 GitHub Actions 自動跑（見未來 Phase 6 的 CI 設定）。

---

## `build-pdf.sh` — 編譯成單一 PDF

```bash
bash scripts/build-pdf.sh                  # zh-TW 版（預設）
LANG_VARIANT=en bash scripts/build-pdf.sh  # 英文版
```

輸出：`dist/awesome-agentic-ai-zh.pdf`（或 `.en.pdf`）

依賴：

- `pandoc` (>= 3.0)
- `xelatex`（TeX Live with CJK support）
- **CJK 字型**：`Noto Sans CJK TC`（zh-TW + en 共用——en 版也需要，因為章節標題仍含中文）
- **西文字型**：`DejaVu Sans`

### 安裝指令

**macOS**：
```bash
brew install pandoc
brew install --cask mactex-no-gui          # TeX Live + xelatex
brew install --cask font-noto-sans-cjk-tc  # CJK 字型
brew install --cask font-dejavu            # 西文字型
```

**Linux (Debian / Ubuntu)**：
```bash
sudo apt install pandoc texlive-xetex texlive-lang-chinese \
                 fonts-noto-cjk fonts-dejavu
```

**Windows**：
```powershell
choco install pandoc miktex
# 然後手動裝字型：
# Noto Sans CJK TC: https://fonts.google.com/noto/specimen/Noto+Sans+TC
# DejaVu Sans: https://dejavu-fonts.github.io/
```

### 換字型

如果上面的字型沒有，可以改用系統內建的：

```bash
# macOS（已內建 PingFang）
CJK_FONT="PingFang TC" bash scripts/build-pdf.sh
# Windows（已內建 Microsoft JhengHei）
CJK_FONT="Microsoft JhengHei" bash scripts/build-pdf.sh
```

兩個字型 env var 都支援：`CJK_FONT` 跟 `MAIN_FONT`。

**Mermaid 圖**：目前 build-pdf.sh 會把 ` ```mermaid` 退化成普通 code block。要 render 圖需要另外裝 `pandoc-mermaid` filter（複雜度高，預設跳過）。

## `build-mdbook.sh` — 建可瀏覽的網站版

```bash
bash scripts/build-mdbook.sh           # 建到 book/dist/
bash scripts/build-mdbook.sh --serve   # 建好後本機開 server (port 3000)
```

依賴：

- Rust + cargo（[rustup.rs](https://rustup.rs)）
- `cargo install mdbook mdbook-mermaid`
- 第一次跑前：`mdbook-mermaid install .`（會生成 `mermaid.min.js`、`mermaid-init.js`，工作流需要）

**自動部署**：
推 main branch 時，[`.github/workflows/docs.yml`](../.github/workflows/docs.yml) 會自動 build mkdocs 站（`/` 首頁）+ mdBook（`/book/`）並 deploy 到 GitHub Pages。單一 workflow 擁有 Pages（兩個 workflow 各自 deploy 會互搶同一個 root，故已合併、刪除舊的 `deploy-book.yml`）。
要啟用，去 Settings → Pages → Source: GitHub Actions。

## 整體 Phase 5 deploy 流程

1. 推 main → `docs.yml` 自動 build mkdocs（`/` 首頁）+ mdBook（`/book/`）並 deploy 到 `https://wenyuchiou.github.io/awesome-agentic-ai-zh/`
2. PDF：手動跑 `bash scripts/build-pdf.sh`，把 `dist/*.pdf` 上傳到 GitHub Release（或自動化 release workflow，TBD）
