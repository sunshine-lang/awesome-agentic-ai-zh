# Channel Partners — Outreach Tracking

> Single source of truth for **awesome-agentic-ai-zh** channel-partner outreach.
> Per-target pitch templates live in `.github/outreach/<slug>.md`.
> Maintainer: @WenyuChiou (个人 maintainer; rule: 1-2 sends/day max).

---

## Status enum

| Status | Meaning |
|---|---|
| `not contacted` | Pitch drafted in `outreach/<slug>.md`, nothing sent yet |
| `contacted` | Outbound sent (issue/PR/email) — awaiting response |
| `replied-positive` | Partner replied; discussion in progress; no commit yet |
| `replied-negative` | Partner declined or asked to redirect |
| `merged-or-listed` | Cross-link landed (PR merged / featured / listed) |
| `ghosted` | No reply in ≥ 2 weeks; one ping sent then dropped |
| `cooldown` | Don't contact for ≥ 30 days (over-asked, restructuring, etc.) |

## Outreach matrix

| # | Target | Channel | Status | Date contacted | Outcome | Date confirmed | Notes |
|---|---|---|---|---|---|---|---|
| 1 | [Datawhale](outreach/datawhale.md) | GitHub issue | not contacted | — | — | — | Already cite Hello-Agents Extra05/08 in our cookbook |
| 2 | [liyupi/ai-guide](outreach/liyupi.md) | GitHub PR | not contacted | — | — | — | ★13k mainland resource hub |
| 3 | [HuggingFace 中文社群](outreach/huggingface-zh.md) | HF community/discuss | not contacted | — | — | — | English ecosystem hub w/ growing zh segment |
| 4 | [LangChain (kyrolabs/awesome-langchain)](outreach/langchain-ai.md) | GitHub PR | not contacted | — | — | — | Stage 4 covers LangChain; §11 lists Langchain-Chatchat |
| 5 | [hesreallyhim/awesome-claude-code](outreach/awesome-claude-code.md) | GitHub **issue** | not contacted | — | — | — | ⚠️ Reorg STILL incomplete (verified 2026-05-21: README TOC is a placeholder; resources now live in `THE_RESOURCES_TABLE.csv` + a submission template). Keep parked — do not spend a send here yet |
| 6 | [punkpeye/awesome-mcp-servers](outreach/awesome-mcp-servers.md) | GitHub PR | contacted | 2026-05-09 | — | — | [PR #6135](https://github.com/punkpeye/awesome-mcp-servers/pull/6135). 2026-05-10: addressed bot name-check ([6f711ec](https://github.com/WenyuChiou/awesome-mcp-servers/commit/6f711ec3)) + replied to glama/emoji bot warnings ([comment](https://github.com/punkpeye/awesome-mcp-servers/pull/6135#issuecomment-4416517075)). Awaiting punkpeye human review. |
| 7 | [Zhipu BigModel community](outreach/zhipu.md) | dev community / 知乎 | not contacted | — | — | — | Inviting them to PR a Zhipu agent entry to §11 |
| 8 | [Moonshot Kimi](outreach/moonshot.md) | dev community / 知乎 | not contacted | — | — | — | Inviting them to PR a Kimi agent entry to §11 |
| 9 | [travisvn/awesome-claude-skills](https://github.com/travisvn/awesome-claude-skills) | GitHub PR | contacted | 2026-05-21 | — | — | [PR #754](https://github.com/travisvn/awesome-claude-skills/pull/754) opened 2026-05-21 — entry in `### Written Tutorials`, framed around Stage 5 (Claude Code ecosystem). Fit is moderate (Claude-Skills-specific list); awaiting maintainer review |
| 10 | [WangRongsheng/awesome-LLM-resources](https://github.com/WangRongsheng/awesome-LLM-resources) | GitHub PR | contacted | 2026-05-21 | — | — | [PR #121](https://github.com/WangRongsheng/awesome-LLM-resources/pull/121) opened 2026-05-21 — entry added to `## 课程 Course` (beside mlabonne/llm-course). Maintainer active; awaiting review |
| 11 | [AiHubCN/Awesome-Chinese-LLM](https://github.com/AiHubCN/Awesome-Chinese-LLM) | GitHub PR | not contacted | — | — | — | ★22k, pushed today, no license (yellow flag). Long TOC — need to browse README before deciding section. Lower priority due to license uncertainty |

## Sequencing rule

**Pace: 1-2 outbound sends per day.** Reasoning:

- Replies need to be handled. If we batch-send all 8 in one day, we can't respond
  to early-positive replies before they cool.

- Multiple open conversations dilute attention; one-at-a-time keeps quality.
- If 5 replies land in week 1, that's a good problem; if 0 land, we don't burn
  all our cards before learning what's not working.

Suggested first-week order (low-risk → high-risk, **revised 2026-05-09**
after upstream-target audit caught the awesome-claude-code reorg):

1. **Day 1**: [#6 punkpeye/awesome-mcp-servers PR](outreach/awesome-mcp-servers.md)
   — has `## Tutorials` section, ★86k repo, reciprocal cite already exists.
   Lowest-risk concrete-action target.

2. **Day 2**: [#5 awesome-claude-code **issue**](outreach/awesome-claude-code.md)
   — repo mid-reorg, no PR-able sections; open an issue parking the proposal
   for when their new TOC lands.

3. **Day 3**: [#1 Datawhale](outreach/datawhale.md) — most strategic for zh-Hans
   reach (we cite Hello-Agents Extra05/08).

4. **Day 4**: [#2 liyupi](outreach/liyupi.md) — high reach if accepted (★13k
   resource hub).

5. **Day 5**: [#4 LangChain (kyrolabs/awesome-langchain)](outreach/langchain-ai.md).
6. **Day 6**: pause — review responses to date.
7. **Day 7+**: [#3 HuggingFace](outreach/huggingface-zh.md), then
   [#7 Zhipu](outreach/zhipu.md), [#8 Moonshot](outreach/moonshot.md) only
   after digesting earlier feedback.

8. **Day 8+ (added 2026-05-10 retroactively)**: targets 9-11 (`travisvn/awesome-claude-skills`,
   `WangRongsheng/awesome-LLM-resources`, `AiHubCN/Awesome-Chinese-LLM`) — discovered they were
   on `.github/launch-checklist.md` from day 1 but missing from this outreach matrix. Pitch
   files not yet drafted; use awesome-mcp-servers template as base when ready. Prioritize
   travisvn (cleanest fit, explicit Tutorials section).

## Update protocol

- Always update this matrix when contacted / received reply / closed.
- Use `git commit -m "outreach: status update for <target> (<status>)"` so the
  log is greppable.

- Dates: ISO format `YYYY-MM-DD`.
- Notes: 1-2 lines max — full context lives in the per-target `outreach/<slug>.md`.

## What NOT to do

- ❌ Bulk-send same template to all 8 in one day — looks like spam
- ❌ Lead with star count (★525) — small to ★1k+ partners; lead with scope
- ❌ Promise things we won't ship (e.g., "we'll add X if you cross-link")
- ❌ Ping after one reply — give 5+ business days
- ❌ Pitch via Discord DM unless explicitly invited (follow each project's
  preferred contact channel; Discord DM cold = annoying)

- ❌ Edit pitch templates without recording the change in the file's git history

## Success indicators

Order by signal strength (top = stronger):

1. **Cross-link landed** in their canonical README / docs / awesome-list
2. **Public mention** (their tweet / post / blog cites us)
3. **Reciprocal listing** in their tutorials/learning section
4. **Soft acknowledgment** — they replied positively but no concrete action

If by **2026-06-01** no signal #1-3 has landed across all 8: pause outreach,
audit the pitch tone (likely too founder-y, not enough technical specifics).


---

## English-audience launch (added 2026-05-17)

Rationale: 14-day traffic is ~100% Chinese-social (Threads #1 external
referrer); zero English dev-channel inbound (no HN / Reddit / lobste.rs
/ newsletter). English content is 99.6% native (0.4% CJK measured) but
was under-promoted. Pre-req DONE this round: README positioning reframed
(trilingual / English fully maintained) + GitHub description/topics
de-zh-gated (commit b4bb862). Drafts ready — maintainer posts manually.

| # | Target | Channel | Status | Draft | Notes |
|---|---|---|---|---|---|
| E1 | Hacker News | Show HN (one shot) | not contacted | [hacker-news.md](outreach/hacker-news.md) | Highest single-spike; weekday AM US-Eastern; author first-comment pre-empts "why a list"/"MT slop" |
| E2 | r/AI_Agents | Reddit self-post | not contacted | [reddit.md](outreach/reddit.md) | Primary sub; exact audience |
| E3 | r/LocalLLaMA | Reddit self-post | not contacted | [reddit.md](outreach/reddit.md) | Local-LLM-angle variant |
| E4 | r/ClaudeAI | Reddit self-post | not contacted | [reddit.md](outreach/reddit.md) | Ecosystem-depth variant |
| E5 | r/learnmachinelearning | Reddit self-post | not contacted | [reddit.md](outreach/reddit.md) | Resource-framing variant |
| E6 | TLDR AI / Ben's Bites / Latent Space / LWiAI | Newsletter tip | not contacted | [newsletters-en.md](outreach/newsletters-en.md) | Submit AFTER a HN/Reddit signal to reference |
| E7 | kyrolabs/awesome-agents · Shubhamsaboo/awesome-llm-apps | GitHub PR | not contacted | [awesome-lists-en.md](outreach/awesome-lists-en.md) | Passive; PR desc MUST state "trilingual/EN-maintained" or `-zh` gets mis-filed. (e2b-dev/awesome-ai-agents dropped 2026-05-21 — ~15-month-stale, see awesome-lists-en.md Don'ts) |

### English sequencing rule

1. **First**: README positioning + GitHub metadata (✅ done b4bb862) —
   without it every English referral bounces on "this is Chinese-only".

2. Then **one** of E1/E2 (HN or r/AI_Agents) — not both same day; gauge response.
3. E3–E5 spaced 1 sub/day, each tailored (identical body = spam-flag).
4. E6 newsletters only AFTER an E1–E5 signal exists ("already trending").
5. E7 awesome-list PRs anytime (passive, low-risk), excluding the two
   already tracked above (punkpeye #6, travisvn #9).

Same "What NOT to do" rules as the zh matrix apply: no star-count lead,
no overclaim, no upvote/star asks, reply to comments for ~24h, never
mass-paste identical text.
