# Outreach: Datawhale (datawhalechina)

> ⚠️ **Send content is now canonical in [`_send-day-packages.md`](_send-day-packages.md)** (package E — current numbers: 8 stages / 240+ resources). This file is kept for positioning rationale; do not paste its older issue/stats blocks directly.

> **Status**: not contacted · **Channel**: GitHub issue + (later) WeChat group
> **Primary lang**: zh-Hans
> **Last updated**: 2026-05-09
> **Decision-maker**: Datawhale 開源教學團隊 (open-source curriculum team)

**Why this target**: Datawhale 是中國大陸最有影響力的 AI 教學社群之一；他們的 [`hello-agents`](https://github.com/datawhalechina/hello-agents) (★ 60k+) 在中文 agentic AI 圈子幾乎人人在用。我們的 Stage 5 cookbook 已經 cite 他們的 Extra05 / Extra08——cross-link 對雙方都加分。

**Pitch angle (我們對他們)**: 我們的 7 階段三語學習地圖把 Hello-Agents 放在 Stage 5 / 6 的位置——讀完我們前 4 階段的 LLM 基礎、prompt、context engineering 之後再進 Hello-Agents 會吸收得更好。我們等於是他們的「pre-flight」入口。

**Their counter-value (他們對我們)**: ★45k 的影響力；如果他們在 Hello-Agents README / docs 提我們一句「想看更完整的學習路線可以參考...」，能帶可觀流量。

---

## Variant 1 — Social post (Weibo / Threads / X，~280 字)

> 「想用 Hello-Agents 但不確定該從哪裡入手？」
>
> awesome-agentic-ai-zh 把 agentic AI 切成 7 階段（Stage 0 基礎 → Stage 7 production），每階段都標註預估時程跟入門條件。Stage 5/6 直接接到 @datawhalechina 的 Hello-Agents Extra05/08。
>
> 三語（zh-TW / zh-Hans / en）· 145+ curated projects · MIT
> 👉 https://github.com/WenyuChiou/awesome-agentic-ai-zh

## Variant 2 — GitHub issue (200-300 字)

**Title**: Cross-link suggestion: structured learning path that points readers to Hello-Agents

```
Hi Datawhale 團隊！

我在維護 [awesome-agentic-ai-zh](https://github.com/WenyuChiou/awesome-agentic-ai-zh)
——一份中文 agentic AI 的 7 階段三語學習地圖（zh-TW canonical / zh-Hans / en，145+
curated projects，MIT），第一週累積 ★525、3,185 unique visitors、1,099 clones。

我們的 Stage 5 cookbook 已經把 Hello-Agents 的 Extra05（記憶 + RAG 概覽）跟 Extra08
（多代理）放進 reading list（[cookbook.md](https://github.com/WenyuChiou/awesome-agentic-ai-zh/blob/main/resources/cookbook.md)），
作為走完前 4 階段 LLM 基礎之後的延伸閱讀。

**想 propose 一個雙向 cross-link**：

1. 我們這邊已經 link 你們了（無條件，已經 ship）
2. 如果你們覺得合適——能不能在 Hello-Agents 的 README 或 docs 裡加一句「想看更
   完整的 agentic AI 學習路線，可以參考 awesome-agentic-ai-zh」？
3. 或是 reverse PR：我們在 §11 中文圈專用 加 Hello-Agents 的正式 entry（你們
   review）？

我們這邊的讀者主要從 Stage 4 之後想進 framework 跟 multi-agent，Hello-Agents
正好是下一階段最強的中文教材。如果不合適也完全 OK，謝謝你們把 Hello-Agents
做出來——它本身就是中文社群的公共財。

— Wenyu (PhD candidate · Lehigh CEE，個人 maintainer)
```

## Variant 3 — Email / WeChat DM (150 字)

```
Hi Datawhale 團隊好，

我是 awesome-agentic-ai-zh 的維護者 Wenyu。這份 repo 是中文 agentic AI 的 7 階段
三語學習地圖（145+ projects，三語齊全），上線一週 ★525。

我們 Stage 5 cookbook 已經把 Hello-Agents 的 Extra05/08 放進延伸閱讀清單。想跟你們
聊聊有沒有可能 reciprocal cross-link 的可能——細節在我剛開的 [GitHub issue]
（連結）。

謝謝你們把 Hello-Agents 做出來，這幾年中文 agentic AI 學習的公共財都是你們扛的，
真的很感激。

— Wenyu
```

---

## Notes

- **不要 promise**「我們會幫你們宣傳」之類的——只 offer 已經 ship 的 cross-link
- 如果他們同意 reverse PR 加 Hello-Agents 到 §11，記得用 `gh api` 確認 ★ 後加
- WeChat 是 Datawhale 主要互動 channel，但 GitHub issue 比較 maintainable + 可追蹤
- 如果一週沒回——OK，他們團隊很忙、不要 ping
