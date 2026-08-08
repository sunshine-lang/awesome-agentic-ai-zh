# Stage 0 — 基础准备（Foundations）

> [繁體中文](./00-foundations.md) | **简体中文** | [English](./00-foundations.en.md)

⏱ **时间估算**：1-2 周（约 5-15 小时，已具备可跳过）

> 💡 **看不懂某个词**？翻 [`resources/glossary.zh-Hans.md`](../resources/glossary.zh-Hans.md) 查 30 秒再回来。Stage 0 还不会碰太多 jargon，但接下来几 stage 会。
> 🗺️ **想先看 agent 的全景地图**（为什么有的 agent 在 terminal、有的在 Telegram、有的在 Jetson 板子）？→ [`resources/agent-paradigms.zh-Hans.md`](../resources/agent-paradigms.zh-Hans.md)（5 种 agent 型态，10 min 读完）

> 📋 **本章组成**：跳过条件检查 → 环境设置步骤 → 进入 Stage 1（foundation stage，无“学习目标 / 进入条件”框架）  
> 🔑 **关键名词**：见 [`resources/glossary.zh-Hans.md`](../resources/glossary.zh-Hans.md)（每个 stage 用到的术语都收在那里）

## 何时可以跳过这个阶段

如果你能：

- 写一个会调用公开 API 并解析 JSON 响应的 Python 函数
- 用 git 做 clone、commit、push，并处理基本的 merge 冲突
- 在自己的操作系统上使用命令行（cd、ls、mkdir、执行 script）
- 看懂 YAML / JSON 文件

→ **直接跳到 [Stage 1](01-llm-basics.zh-Hans.md)**。

如果做不到，就把这个阶段走完。不要跳——后面每个阶段都会预设你已经会这些。

## 📌 学习目标

- 写 Python：函数、类、async/await 基本用法
- 用 git：clone、branch、commit、push、基本冲突处理
- 用 REST API：发 GET/POST、解析 JSON、处理 auth header
- 读写 YAML 跟 JSON

## 🛠 动手练习

- **练习：Python** — 写一个 Python script 调用 https://api.github.com/users/torvalds 并打印 follower 数量
- **练习：git** — clone 任何一个公开 repo，做一次 commit，push 到自己的 fork
- **练习：CLI** — 用命令行建几个文件夹跟文件（macOS / Linux：`mkdir project && cd project && mkdir src tests docs`；Windows PowerShell：`New-Item -ItemType Directory -Path project,project\src,project	ests,project\docs`）、执行 Python script、把输出存到文件
- **练习：YAML** — 用 Python 读一个 `.yaml` 配置文件，改一个值，再写回去
- **练习：API auth** — 去 [github.com/settings/tokens](https://github.com/settings/tokens) 产生一个 personal access token（给最少权限：`read:user`），调用 `https://api.github.com/user` 需 auth 的 endpoint，看 401（无 token）vs 200（带 token）的差别。注意：production agent 一定会用到 API auth，所以这一题要做

## 🎯 精选资源（不是完整 Project，只是学习素材）

按 5 个 prereq 主题分类、18 个资源一张表搞定。**挑入口看“适合谁”、想深入点链接看 repo / 网站**。

| 主题 | 资源 | 适合谁 | 为什么推荐 / 备注 |
|---|---|---|---|
| **Python** | [Python Crash Course](https://github.com/ehmatthes/pcc_3e) | 从零学 Python | 书 + 练习；书要付费、练习免费 |
| | [Real Python tutorials](https://realpython.com/) | 已会基础、想深入单一主题 | 高质量免费文章、Google 搜索常出现 |
| | [Corey Schafer YouTube](https://www.youtube.com/c/Coreyms) | 喜欢英文视频学习者 | 视频教学，从基础到进阶、讲解清楚 |
| | [Boot.dev](https://www.boot.dev/) | 想要互动式练习 | 互动式 Python 课程；部分免费、付费含完整 backend 路线 |
| | [runoob.com Python 教程](https://www.runoob.com/python3/python3-tutorial.html) | 中文读者快速查语法 | 中文 Python 入门参考 |
| **Git** | [Pro Git book](https://git-scm.com/book/en/v2) | 想彻底搞懂 Git | 免费完整参考书、官方推荐 |
| | [Atlassian Git Tutorials](https://www.atlassian.com/git/tutorials) | 想学 workflow（branch / merge / rebase） | 以 workflow 为主、视觉化好 |
| | [Oh Shit, Git!?!](https://ohshitgit.com/) | 搞砸时急救 | “我搞砸了 X，怎么救？”cheat sheet |
| | [git-flight-rules](https://github.com/k88hudson/git-flight-rules) | 想要更深的急救手册 | 高人气 cheat sheet、覆盖场景更广 |
| **CLI / Shell** | [The Art of Command Line](https://github.com/jlevy/the-art-of-command-line) | 想系统性学命令行 | ★ 160k+、多语言版、新手到进阶都涵盖 |
| | [Learn Shell](https://www.learnshell.org/) | 喜欢互动式练习 | 互动式 Bash 教学、浏览器内跑 |
| | [explainshell.com](https://explainshell.com/) | debug shell 指令 | 把任何 shell 指令拆解讲解（debug 救星） |
| **REST API** | [MDN — HTTP](https://developer.mozilla.org/en-US/docs/Web/HTTP) | 想搞懂 HTTP 协议 | Mozilla 维护的 web 平台参考文档 |
| | [Postman Learning Center](https://learning.postman.com/) | 用 GUI 探索 API | API 探索工具、视觉化好 |
| | [HTTPie](https://github.com/httpie/cli) | 偏好 CLI、`curl` 太丑 | 比 `curl` 友善的命令行 HTTP client |
| **YAML / JSON** | [YAML 官网](https://yaml.org/) | 需要查语法规格 | YAML 规格文件 |
| | [JSON crash course](https://www.json.org/json-en.html) | 第一次接触 JSON | 官方快速指南 |
| | [jq](https://github.com/jqlang/jq) | 命令行处理 JSON | agent 工作中常用、处理 API response 必备 |

## 为什么有这个阶段

大多数“AI agent”教学都预设你已经会这些。如果你还没，就会在奇怪的地方卡关（tool 需要 async、配置文件是 YAML、SDK 安装要用 git）。在这里花一周的投资，可以省下后面 10 周以上的挫折。

---

> ✅ **走完 Stage 0 了？** 接下来 [**Stage 1 — LLM 基础**](01-llm-basics.zh-Hans.md) 会用 5-8 小时带你做完第一次 LLM API 调用、认识 token / context window / temperature，以及用 per-token 计价估算实际任务成本。**继续往下走 →**
