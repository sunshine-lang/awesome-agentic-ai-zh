# Stage 0 — Foundations

> [繁體中文](./00-foundations.md) | [简体中文](./00-foundations.zh-Hans.md) | **English**


⏱ **Time estimate**: 1-2 weeks (~5-15 hours, can skip if you have these)

> 💡 **Don't recognize a term?** Check [`resources/glossary.en.md`](../resources/glossary.en.md) for a 30-second definition. Stage 0 doesn't lean on much jargon, but the next stages do.
> 🗺️ **Want the big picture of the agent landscape first** (why some agents live in a terminal, some in Telegram, some on a Jetson board)? → [`resources/agent-paradigms.en.md`](../resources/agent-paradigms.en.md) (5 agent paradigms, ~10 min read)

> 📋 **Structure of this chapter**: skip-check → environment setup steps → on to Stage 1 (a foundation stage, so it has no "learning goals / prerequisites" frame)  
> 🔑 **Key terms**: see [`resources/glossary.en.md`](../resources/glossary.en.md) (every term each stage uses is collected there)

## When to skip this stage

If you can:

- Write a Python function that calls a public API and parses JSON response
- Use git to clone, commit, push, and resolve a basic merge
- Use the command line on your OS (cd, ls, mkdir, run a script)
- Read a YAML / JSON file without confusion

→ **Skip directly to [Stage 1](01-llm-basics.en.md)**.

If you can't, work through this stage. Don't skip — every later stage assumes these.

## 📌 Learning Goals

- Write Python: functions, classes, async/await basics
- Use git: clone, branch, commit, push, basic conflict resolution
- Use REST APIs: send GET/POST, parse JSON, handle auth headers
- Read & write YAML and JSON

## 🛠 Hands-on Exercises

- **Exercise: Python** — write a Python script that calls https://api.github.com/users/torvalds and prints follower count
- **Exercise: git** — clone any public repo, make a commit, push to your fork
- **Exercise: CLI** — make a small directory tree with the command line (macOS / Linux: `mkdir project && cd project && mkdir src tests docs`; Windows PowerShell: `New-Item -ItemType Directory -Path project,project\src,project\tests,project\docs`), run a Python script, redirect output to a file
- **Exercise: YAML** — read a `.yaml` config file in Python, modify a value, write it back
- **Exercise: API auth** — at [github.com/settings/tokens](https://github.com/settings/tokens) generate a personal access token (minimal scope: `read:user`), call the auth-required `https://api.github.com/user` endpoint, observe 401 (no token) vs 200 (with token). Note: real production agents always use API auth — do this exercise

## 🎯 Curated Resources (not full projects, just learning material)

Five prereq topics, 18 resources, one table. **Pick your entry point from "Who it's for", then follow the link to the repo / site when you want to go deeper.**

| Topic | Resource | Who it's for | Why recommended / Notes |
|---|---|---|---|
| **Python** | [Python Crash Course](https://github.com/ehmatthes/pcc_3e) | Learning Python from scratch | Book + exercises; the book is paid, the exercises are free |
| | [Real Python tutorials](https://realpython.com/) | Know the basics, want to go deep on one topic | High-quality free articles; they turn up in Google searches all the time |
| | [Corey Schafer YouTube](https://www.youtube.com/c/Coreyms) | Learners who like English video | Beginner to advanced, very clear delivery |
| | [Boot.dev](https://www.boot.dev/) | Want interactive practice | Partially free; the paid tier includes a full backend track |
| | [runoob.com Python tutorial](https://www.runoob.com/python3/python3-tutorial.html) | Chinese readers looking up syntax fast | Chinese-language Python intro reference |
| **Git** | [Pro Git book](https://git-scm.com/book/en/v2) | Want to understand Git properly | Free, full-length reference; the official recommendation |
| | [Atlassian Git Tutorials](https://www.atlassian.com/git/tutorials) | Want to learn workflows (branch / merge / rebase) | Workflow-focused, good visuals |
| | [Oh Shit, Git!?!](https://ohshitgit.com/) | First aid when things go wrong | "I screwed up X, how do I undo?" cheat sheet |
| | [git-flight-rules](https://github.com/k88hudson/git-flight-rules) | Want a deeper recovery manual | Popular cheat sheet, covers more scenarios |
| **CLI / Shell** | [The Art of Command Line](https://github.com/jlevy/the-art-of-command-line) | Want to learn the command line systematically | ★ 160k+, multi-language, covers beginner to advanced |
| | [Learn Shell](https://www.learnshell.org/) | Like interactive practice | Interactive Bash tutorial, runs in the browser |
| | [explainshell.com](https://explainshell.com/) | Debugging shell commands | Breaks down any shell command (debug life-saver) |
| **REST API** | [MDN — HTTP](https://developer.mozilla.org/en-US/docs/Web/HTTP) | Want to understand the HTTP protocol | Mozilla's web platform reference docs |
| | [Postman Learning Center](https://learning.postman.com/) | Exploring APIs through a GUI | API exploration tool, good visuals |
| | [HTTPie](https://github.com/httpie/cli) | Prefer the CLI, find `curl` ugly | Friendlier-than-`curl` command-line HTTP client |
| **YAML / JSON** | [YAML official site](https://yaml.org/) | Need to look up the syntax spec | The YAML spec document |
| | [JSON crash course](https://www.json.org/json-en.html) | First time meeting JSON | Official quick guide |
| | [jq](https://github.com/jqlang/jq) | Processing JSON on the command line | Heavy use in agent work; essential for handling API responses |

## Why this stage exists

Most "AI agent" tutorials assume you already have these. If you don't, you'll get blocked at random places (tools requires async; configs are YAML; SDK setup needs git). One week investing here saves 10+ weeks of frustration later.

---

> ✅ **Done with Stage 0?** Next, [**Stage 1 — LLM Fundamentals**](01-llm-basics.en.md) takes 5-8 hours to walk you through your first LLM API call, the meaning of token / context window / temperature, and how to estimate real task cost via per-token pricing. **Keep going →**
