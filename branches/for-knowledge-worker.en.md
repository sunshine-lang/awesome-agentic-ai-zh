# Extension Path: For Knowledge Workers

> [繁體中文](./for-knowledge-worker.md) | [简体中文](./for-knowledge-worker.zh-Hans.md) | **English**

<!-- freshness: canonical=branches/for-knowledge-worker.md; verified_on=2026-08-29; scope=apps,connectors,mcp,workflow-automation,permissions,project-status; max_age_days=90 -->

> [← Back to the main route](../README.en.md) · Continue after **Track A A3** or **Track B Stage 7**. No development background is required: start with one-off tasks and connect tools only when work repeats.

<a id="use-cases-office-scenarios--how-ai-helps"></a>
## 📌 What this path helps you do
Turn scattered meeting notes, email, documents, and tasks into work that is clear, findable, and owned. AI can organize a first draft; sources, permissions, and final decisions remain human responsibilities.

Common work includes sorting email, turning meetings into Action Items, drafting weekly reports, organizing product requirements, summarizing research, and maintaining a **Knowledge Base**.

## 🎯 Learning goals
1. Find decisions, owners, deadlines, and evidence in the original text without letting AI fill gaps.
2. Distinguish one-off chat, **App／Connector**, **MCP Server**, and **Workflow Automation**.
3. Check data and permissions before tools read or modify company systems.
4. Keep email, data changes, and task creation behind an **Approval Gate**.

## 🧩 Nine core terms
- **Source**: the original email, transcript, document, or data row; answers must point back to it.
- **Action Item**: a task with what, who, and when.
- **Knowledge Base**: reusable information stored where people and tools can find it.
- **Private Data**: company, customer, employee, or personal data; do not give it to a new tool without policy and permission.
- **Human Review**: compare with the Source, check content, tone, recipients, and omissions before use.
- **App／Connector**: a bridge from an AI service to Gmail, Drive, Slack, and similar sources. ChatGPT renamed Connectors to Apps; other services may still use Connector.
- **MCP Server**: a service exposing data or tools to compatible clients through MCP; it is not a ChatGPT App or automatic approval.
- **Workflow Automation**: a fixed sequence of actions triggered by an event.
- **Approval Gate**: a pause for human confirmation before sending, posting, editing, or deleting.

**Do not conflate them: App／Connector is a service bridge; MCP Server is a protocol endpoint; Workflow Automation repeats triggers, conditions, and actions.** One product may include more than one of them, but the names are not interchangeable.

## 🛠 First exercise: turn meeting notes into a checkable action table
Use fictional data only; do not include **Private Data**. Copy this prompt into an AI chat tool:
```text
You are a meeting-notes assistant. Use only the note below; do not invent names or dates.
Output a Markdown table with fixed columns:
Decision | Action Item | Owner | Due date | Source sentence | Needs confirmation
Rules:
1. Copy a short Source sentence in every row.
2. If Owner or Due date is unclear, write “unknown” and mark Needs confirmation “yes”.
3. Do not send, post, or write to any system; produce a draft only.
4. End with a Human Review checklist: source, owner, deadline, sensitive data, recipients.
Fictional meeting note: “The team decided to publish the help page Friday. Lin will organize FAQs, but no deadline is recorded. The support lead must confirm the reply template by September 3. Whether to email all customers will be decided after the meeting.”
```
Compare every Source sentence. If AI invents Lin’s deadline or the email decision, reject the draft: this is **Human Review**.

<a id="tier-recommendations"></a>
## 📚 Choose an entry point
| Need | Start with | Upgrade when |
|---|---|---|
| Occasionally organize approved text | **One-off chat** | The same task repeats |
| Search company Gmail, Drive, Slack, or Microsoft 365 | Approved **App／Connector** | Existing bridges cannot do it and an administrator approves a custom connection |
| Run the same steps for each new email/form | **Workflow Automation** | Test data works and you can add an Approval Gate |

Do not install MCP just because you see it. Ask whether an in-service App／Connector is safe enough; use [Stage 5.2 — MCP](../stages/05-claude-code-ecosystem.en.md#52--mcp-model-context-protocol--foundation) only for custom tools or reuse across clients.

<a id="reading"></a>
## 📖 Required reading
1. [OpenAI — Apps in ChatGPT](https://help.openai.com/en/articles/11487775-connectors-in): capabilities, plans, regions, and admin limits.
2. [Anthropic — Skills, Connectors and Plugins directory](https://support.claude.com/en/articles/14328846-browse-skills-connectors-and-plugins-in-one-directory): distinguish the three and do not treat installation as approval.
3. [Google — Gemini Connected Apps](https://support.google.com/gemini/answer/14959807?co=GENIE.Platform%3DDesktop&hl=en): admin, account, and source limits.
4. [Microsoft — Understand Copilot connectors](https://support.microsoft.com/en-us/microsoft-365-copilot/understand-copilot-connectors): connectors should see only content the user already may access.
5. [Model Context Protocol — Registry](https://modelcontextprotocol.io/registry/about): Preview metadata is not code security review.
6. [Zapier — workflow quick start](https://help.zapier.com/hc/en-us/articles/22234847450893-Zap-workflows-quick-start-guide): triggers, actions, testing, and publishing.

<a id="curated-projects"></a>
## ⭐ Curated tools, projects, and official entry points
Stars are this project’s teaching-fit ratings, not GitHub stars. Ask an administrator before using a cloud service; self-hosted tools still need updates, backups, permissions, and data-flow checks.

<small>Data verified: 2026-08-29 UTC</small>

<a id="workflow-tools"></a><strong>Workflow tools:</strong> use for repeated work; keep the first version at draft or Approval Gate.<br>
<a id="knowledge-worker-skills"></a><strong>Knowledge-worker Skills:</strong> reusable methods do not grant company-system access.<br>
<a id="knowledge-management--personal-ai"></a><strong>Knowledge management / personal AI:</strong> self-hosting does not guarantee local data; check provider and Connector settings.<br>
<a id="mcp-servers-useful-for-knowledge-workers"></a><strong>MCP Server:</strong> inspect source, code, permissions, credentials, and actions before use.

<table><thead><tr><th scope="col">Type</th><th scope="col">Tool / entry point</th><th scope="col">Good for</th><th scope="col">Status / license</th><th scope="col">Know first</th><th scope="col">Rating</th></tr></thead>
<tbody><tr><th scope="rowgroup" rowspan="4">AI workspaces and organization Apps</th><td><a href="https://help.openai.com/en/articles/11487775-connectors-in">ChatGPT Apps</a></td><td>Search sources or run allowed actions</td><td>Commercial; commercial cloud service</td><td>Plan, region, and admin dependent; retain human confirmation</td><td>⭐⭐⭐⭐⭐</td></tr><tr><td><a href="https://support.claude.com/en/articles/14328846-browse-skills-connectors-and-plugins-in-one-directory">Claude directory</a></td><td>Find Skills, Connectors, and Plugins</td><td>Commercial; commercial cloud service</td><td>Different purposes; administrator approval first</td><td>⭐⭐⭐⭐⭐</td></tr><tr><td><a href="https://support.google.com/gemini/answer/14959807?co=GENIE.Platform%3DDesktop&hl=en">Gemini Connected Apps</a></td><td>Use Gmail, Drive, Calendar sources</td><td>Commercial; commercial cloud service</td><td>Account/admin dependent; check answers against sources</td><td>⭐⭐⭐⭐⭐</td></tr><tr><td><a href="https://support.microsoft.com/en-us/microsoft-365-copilot/understand-copilot-connectors">Microsoft 365 Copilot connectors</a></td><td>Search Microsoft 365 and approved external content</td><td>Commercial; commercial cloud service</td><td>Original permissions still apply; administrator setup required</td><td>⭐⭐⭐⭐⭐</td></tr></tbody>
<tbody><tr><th scope="rowgroup" rowspan="4">Workflow automation</th><td><a href="https://github.com/n8n-io/n8n">n8n</a></td><td>Connect services and AI steps</td><td>Active; Sustainable Use License</td><td>Not MIT; you own self-hosting security, updates, backups, credentials</td><td>⭐⭐⭐⭐⭐</td></tr><tr><td><a href="https://academy.make.com/courses/FoundationC01?pc=workflow">Make</a></td><td>Visual cloud scenarios</td><td>Commercial; commercial cloud service</td><td>Test data, runs, retries, and cost need monitoring</td><td>⭐⭐⭐⭐</td></tr><tr><td><a href="https://learn.microsoft.com/en-us/training/powerplatform/power-automate">Power Automate</a></td><td>Microsoft trigger/action flows</td><td>Commercial; commercial cloud service</td><td>Plans, Connectors, and data policy are administrator-controlled</td><td>⭐⭐⭐⭐</td></tr><tr><td><a href="https://help.zapier.com/hc/en-us/articles/22234847450893-Zap-workflows-quick-start-guide">Zapier</a></td><td>Repeated cloud-App workflows</td><td>Commercial; commercial cloud service</td><td>Test step by step; writing to the trigger can create an infinite loop</td><td>⭐⭐⭐⭐</td></tr></tbody>
<tbody><tr><th scope="rowgroup" rowspan="2">Visual AI builders</th><td><a href="https://github.com/langflow-ai/langflow">Langflow</a></td><td>Draw AI, data, and tool flows as nodes</td><td>Active; MIT</td><td>Demo success is not production security; add auth, secrets, monitoring</td><td>⭐⭐⭐⭐</td></tr><tr><td><a href="https://github.com/langgenius/dify">Dify</a></td><td>Build AI workflows, knowledge bases, and apps</td><td>Active; modified Apache-2.0</td><td>Multi-tenant and branding cases have commercial conditions</td><td>⭐⭐⭐⭐</td></tr></tbody>
<tbody><tr><th scope="rowgroup" rowspan="3">Knowledge workspaces</th><td><a href="https://github.com/khoj-ai/khoj">Khoj</a></td><td>Self-hosted personal knowledge assistant</td><td>Active; AGPL-3.0</td><td>Check AGPL and data configuration; manage model and backups</td><td>⭐⭐⭐⭐</td></tr><tr><td><a href="https://github.com/lobehub/lobehub">LobeHub</a></td><td>Chat, knowledge bases, and team workspace</td><td>Active; LobeHub Community License</td><td>Check commercial terms before distributing a derivative work</td><td>⭐⭐⭐⭐⭐</td></tr><tr><td><a href="https://github.com/Mintplex-Labs/anything-llm">AnythingLLM</a></td><td>Self-hosted document Q&A, workspace, and agent</td><td>Active; MIT</td><td>Outbound data depends on model provider, embedder, and Connector</td><td>⭐⭐⭐⭐⭐</td></tr></tbody>
<tbody><tr><th scope="rowgroup" rowspan="2">Skills and protocol entry points</th><td><a href="https://github.com/obra/superpowers">obra/superpowers</a></td><td>Reusable brainstorming, planning, and checking Skills</td><td>Active; MIT</td><td>Not an organization Approval Gate; adapt its rules</td><td>⭐⭐⭐⭐</td></tr><tr><td><a href="https://modelcontextprotocol.io/registry/about">Official MCP Registry</a></td><td>Standardized metadata for public MCP Servers</td><td>Preview; official metadata service</td><td>Namespace validation is not a security review or endorsement</td><td>⭐⭐⭐⭐</td></tr></tbody></table>

<a id="workflows-you-can-build-by-frequency"></a>
<details markdown="1"><summary>🧪 Expand: advanced office workflows and product-manager use</summary>
| Work | Safe first version | Automate later |
|---|---|---|
| Email triage | De-identified test messages; draft classifications/replies | Admin-approved inbox; Approval Gate before sending |
| Meetings → Action Items | Transcript to Source-sentence table | Host confirms Owner and Due date before task write |
| Weekly report | Human-provided approved metrics | Preserve source links and pre-send review |
| Product requirements | Fictional feedback → problem, evidence, hypothesis, next step | Restrict project, fields, and actions before ticket connection |
| Knowledge Base | Classify a few documents | Back up and sample-check before batch retagging |
</details>
<details markdown="1"><summary>🔐 Expand: account, data, permission, and cost checks</summary>
- Ask whether the organization approves the tool, account, region, and data use.
- Grant minimum permissions; approve reading and writing separately.
- Keep secrets in credential stores or environment variables, never prompts, documents, or screenshots.
- Test with fictional/de-identified data and retain an Approval Gate for high-risk actions.
- Check plans, runs, models, and storage; set budget alerts. When finished, stop workflows, revoke connections, and delete test data.
</details>
<details markdown="1"><summary>🧯 Expand: alternatives and troubleshooting</summary>
- Missing data: confirm direct Source access, then account, dates, sync, and admin settings.
- Duplicate tasks: check whether an action retriggers itself; add unique IDs or deduplication.
- Invented Owner/Due date: require Source sentence and Needs confirmation.
- Unsure about MCP: use an in-service App／Connector first.
- Self-hosting is heavy: use an approved cloud service; it is not a privacy shortcut.
</details>

## ✅ Completion check and next stop
- [ ] I can turn fictional notes into a Decision／Action Item table and check each Source sentence.
- [ ] I do not conflate App／Connector, MCP Server, and Workflow Automation.
- [ ] I check policy and permission for Private Data; external actions have an Approval Gate.
- [ ] I chose one entry point instead of installing everything.

Next: custom connections via [Stage 5.2 — MCP](../stages/05-claude-code-ecosystem.en.md#52--mcp-model-context-protocol--foundation); long-running workflows via [Stage 7](../stages/07-multi-agent-production.en.md); code via the [Developer path](./for-developer.en.md).
