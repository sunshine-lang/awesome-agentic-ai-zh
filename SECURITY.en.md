# Security Policy

> [繁體中文](./SECURITY.md) | [简体中文](./SECURITY.zh-Hans.md) | **English**

This repo is a **curated learning roadmap** (mainly Markdown learning materials plus a small amount of example code), not a software product that gets deployed. Even so, several categories of security issues are still worth reporting, especially because this material teaches readers to **actually run agents / MCP / tool-use**.

## Supported Scope

This project uses **rolling maintenance**: the supported scope is the latest state of the `main` branch. Versioned tags (`vYYYY.MM.DD[-N]`, used for citation via [`CITATION.cff`](CITATION.cff)) are **content snapshots** and are not patched retroactively - reported issues are fixed on `main`, and no fix release is cut for an older tag.

## What Counts as a Security Issue

Please report the following:

- **Hijacked / malicious third-party links** — a repo link in the catalog points to a phishing site or malicious package, or the project has been taken over maliciously
- **Supply-chain risks in example code** — code in `examples/`, `walkthroughs/`, or `scripts/` leads readers toward unsafe dependencies, patterns that leak keys, or injectable commands
- **Leaked secrets in learning materials** — real API keys / tokens / credentials were accidentally pasted into the docs
- **Command-injection-style instructional content** — a piece of instruction leads readers to run something dangerous on their own machines (for example, executing an agent on untrusted input without sandboxing)

**Not in scope** for this repo's security policy: vulnerabilities in third-party projects **themselves**. Please report those directly to the upstream project maintainers, and you may also open an issue to remind us to label or remove that entry.

## How to Report

**Please do not post exploitable details in a public issue.**

1. **Preferred**: Use GitHub's **private vulnerability reporting** (the repo's **Security** tab → **Report a vulnerability**). Only maintainers can see it.
2. If that feature is unavailable: please DM **@WenyuChiou** on GitHub with the impact and the affected files / links, and we will continue privately. **Do not open a public issue** — even without exploit details, a public title and labels would expose that there is an unpatched issue.

When reporting, please include as much as possible: affected files / links, a description of the issue, the possible impact, and (if any) suggested fixes.

## Response Timeline

This is a community-maintained educational project with no SLA, but we will handle reports as quickly as possible. In general:

- **Acknowledgement**: within 7 days
- **Initial assessment**: within 14 days
- **Fix or annotation**: depends on severity; malicious links will be prioritized

Thank you for helping make this material safer for all learners.
