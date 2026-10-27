# Demos

Great software no longer has to cost a fortune or consume every hour of your day. With Claude Code, you get an engineering partner that plans, builds, tests, and ships alongside you at a fraction of the time and cost. This isn't about prompting an AI. It's about designing systems that multiply what you can deliver.

Welcome to the new standard.

Agentic software engineering is a discipline shift, and once you experience it, there's no going back. Instead of spending days on tasks that take agents minutes, you orchestrate workflows that reduce cost, eliminate repetition, and scale your output without scaling your team. The developers who master this don't just move faster. They do more with less, and they do it consistently.

Across 11 hands-on modules, you'll go from Claude Code fundamentals to production-grade multi-agent pipelines. You'll design composable skills, build MCP tools that connect agents to real systems, extend and customize the harness with mods, architect parallel sub-agent workflows, and harden everything for real-world conditions. Every module is built around genuine engineering decisions, because the goal was never to write more code. It was always to build software that matters.

The class also covers everything required to pass the [Claude Certified Architect: Foundations certification](https://anthropic-partners.skilljar.com/claude-certified-architect-foundations-certification). Every exam area, from the CLAUDE.md constitution and the permission model through skills, MCP, sub-agents and security, is taught in a module and practiced in its lab. Work through the 11 modules and you are prepared for the exam without any separate study track. Still we want to point out that this is not a dedicated exam prep class.

## Module 1: Claude Code Fundamentals

- Introduction to Claude Code
- Setup & Installation
- Editors: Terminal, Desktop App, VS Code
- Model Selection Strategy
- Prompt caching, cost and token awareness
- Permission Model: Tools, Bash, Network
- Checkpoints & Session Safety
- Git worktrees: isolated checkouts
- Agents view: background sessions
- Artifacts: results as shareable pages

## Module 2: Claude Code Configure Harness

- Settings Hierarchy: Global, Project
- CLAUDE.md and path-scoped rules
- @-mentioning files
- Slash Commands
- MCP Servers & Tools
- Skill folders and their sources
- Sub-agents under `.claude/agents/`
- Hooks: PreToolUse, PostToolUse, Stop
- Mods: extend and customize the harness
- Auto-memory: MEMORY.md index, four typed files

## Module 3: Creating & Managing Skills

- Skills vs. slash commands
- Invocation model, anatomy, body structure
- Authoring manually or from conversation
- Front matter fields
- Allowed-tools and disallowed-tools fields
- Composite skills: scripts, references, assets
- Cross-skill references and delegation patterns
- Dynamic context injection: command preprocessing (optional)
- Forked execution: agent and background (optional)
- Testing: triggers and measurement
- Distribution: portable folder and skills API
- Repo facts: rules file contract

## Module 4: Consuming & Designing MCP Tools

- MCP architecture: servers, clients, transports
- Session lifecycle and exposed capabilities
- Remote auth: tokens, keys, OAuth
- Building a server in C#
- Inspection with the MCP Inspector (optional)
- MCP Apps: interfaces inside the host
- Artifact connectors calling MCP live (optional)
- Tool design: granularity, descriptions, resources
- Error and deferred-loading contract
- MCP Tasks: long-running tool calls

## Module 5: Automate Claude Code from the Command Line

- Agent harness: tools, knowledge, action interfaces
- CLI, terminal, and headless mode
- Headless mode: print, JSON, exit codes
- Least-privilege tool scoping
- CI gates: sentinels and exit codes
- GitHub Actions: scripting agentic workflows
- Parallel worktree lanes and task-queue orchestration
- PreToolUse policy gates across lanes
- Always-on goal patterns with turn limits
- Harness interop with Copilot CLI (optional)

## Module 6: Scale task execution with sub-agents and agent teams

- Single-agent limits (optional)
- Frontmatter: name, model, tools, permission mode
- Per-agent tool restrictions (optional)
- Backend agent: .NET and Learn MCP
- Frontend agent: Angular and DevTools MCPs
- QA agent: Playwright, no implementation authority
- Evaluating performance with test cases
- Orchestration: prompt delegation, loops, workflow graphs
- Context isolation between parallel agents
- Where a team beats sub-agents
- Lead, teammates, shared task list, mailbox
- Enabling teams and session state
- Spawning teammates: names and models (optional)
- Display modes and steering keys (optional)
- Task states, dependencies, and self-claiming (optional)
- Messaging between lead and teammates (optional)
- Competing hypotheses in a team (optional)
- Plan approval and lifecycle hooks (optional)
- Team sizing, conflicts, and cost (optional)

## Module 7: Optimize, Secure and Observe the Agentic Harness

- /doctor prompt-audit: dated instructions
- Caveman Compression: shorter CLAUDE.md
- Plugin Eval: graded skill experiments
- Prompt Injection: quarantine, MCP responses
- Hook Guardrails: PreToolUse hard stops
- OpenTelemetry: tracing, cost, failure diagnosis

## Module 8: Bundle and Distribute Your Config as a Plugin

- Plugins vs. standalone configuration: namespacing
- Plugin anatomy: manifest, skills, hooks, MCP
- Bundling skills, hooks, MCP configs
- LSP servers and background monitors
- Default agent activation via plugin settings
- Local testing: plugin directory and reload
- Converting `.claude/` configs into plugins
- Publishing to official and team marketplaces
- Plugins by Anthropic
- Plugins and repo rules: `.claude/rules/`

## Module 9: Agentic DevOps & Automation

- The deployment sub-agent: allowlists, prove-it contract
- Bootstrapping and hardening Ubuntu over SSH
- Docker Compose behind a Caddy edge
- DNS before the first ACME attempt
- Core Web Vitals and SEO loops

## Module 10: Build and host agents with the Agent SDK and Managed Agents

- Agent SDK: query() and sessions
- Agent SDK: parallel agents, orchestrator
- Managed Agents: Agent, Environment, Session
- Managed Agents: files, SSE stream
- Managed Agents: vaults, versions, policies
- Managed Agents: MCP servers, skills
- Human-in-the-Loop: approval gates
- Multiagent: outcomes, memory stores

## Module 11: Planning & Spec-Driven Development (Optional)

- Brownfield analysis: harvesting the current state
- Plan Mode: mechanics and activation
- Stepwise context: questions and constraints
- Spec iteration via feedback loops
- Authoring specs and technical plans
- Decomposing tasks into sub-agent packages
- Defining and validating done criteria
- Why spec-driven development
- GitHub Spec Kit pipeline
- Spec-driven feature, end to end

## Schedule

| Day | Clock          | Length | Deliverable                                                                                                        | Description                                                                                                                                                                                                                                                               |
| --- | -------------- | ------ | ------------------------------------------------------------------------------------------------------------------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 1   | 09:00 to 10:00 | 1h 00m | [Claude Code Fundamentals](01-fundamentals/readme.md)                                                              | Setup and editors, model selection, prompt caching and cost, permissions, checkpoints, git worktrees, agents view, artifacts (8 topics, 4 demos, 3 optional)                                                                                                                          |
| 1   | 10:00 to 10:10 | 10m    | Break                                                                                                              |                                                                                                                                                                                                                                                                           |
| 1   | 10:10 to 10:55 | 45m    | [Lab: Build a Task Tracking REST API](../labs/01-fundamentals/02-hello-claude/readme.md)                           | Build a Python REST API for task management entirely through prompts, one step at a time. Every step gives you the prompt to paste and the result to expect.                                                                                                              |
| 1   | 10:55 to 11:45 | 50m    | [Claude Code Configure Harness](02-harness/readme.md)                                                              | Harness elements and settings hierarchy, CLAUDE.md constitution and path-scoped rules, slash commands, hooks and mods, memory (5 topics, 4 demos, 2 optional)                                                                                                                                               |
| 1   | 11:45 to 12:45 | 1h 00m | Lunch                                                                                                              |                                                                                                                                                                                                                                                                           |
| 1   | 12:45 to 14:10 | 1h 25m | [Lab: Configure the Harness on a Broken React App](../labs/02-harness/lab-02-fix-the-react-food-shop.md)           | Configure the harness piece by piece (CLAUDE.md, MCP servers, a PostToolUse hook, a slash command, a skill, checkpoints) on a broken React app. The app is the use case; the harness is the lesson.                                                                       |
| 1   | 14:10 to 14:55 | 45m    | [Creating & Managing Skills](03-skills/readme.md)                                                                  | Skills versus slash commands, installing skills, authoring and frontmatter, composite skills, dynamic context and forked execution, testing, packaging, and repo facts for global skills (5 topics, 4 demos)                                                                                             |
| 1   | 14:55 to 15:05 | 10m    | Break                                                                                                              |                                                                                                                                                                                                                                                                           |
| 1   | 15:05 to 16:25 | 1h 20m | [Lab: Package Invoice Generation Into a Skill](../labs/03-skills/lab-01-invoice-docx-skill.md)                     | Turn a one-off document script into a composite skill with frontmatter, a reference file, a rendering script, restricted tools and a value injected at load time. It answers "invoice Nordwind for two days of training" with a real Word document.                       |
| 2   | 09:00 to 09:30 | 30m    | [Consuming & Designing MCP Tools](04-mcp/readme.md)                                                                | MCP architecture and transports, developer servers, building a server in C#, MCP apps, artifact connectors, tool design, MCP tasks (6 topics, 4 demos)                                                                                                                    |
| 2   | 09:30 to 10:35 | 1h 05m | [Lab: Build the EventTrack Registration MCP Server](../labs/04-mcp/lab-02-eventtrack-mcp-server.md)                | Build a headless Python MCP server that manages events, attendee registrations and per-event capacity, then drive the full registration workflow from Claude Code.                                                                                                        |
| 2   | 10:35 to 10:45 | 10m    | Break                                                                                                              |                                                                                                                                                                                                                                                                           |
| 2   | 10:45 to 11:30 | 45m    | [Automate Claude Code from the Command Line](05-cli/readme.md)                                                     | Headless mode and tool scoping, CI gates, worktree lanes with policy hooks and parallel orchestration, always-on goal patterns, harness interop with Copilot CLI (5 topics, 5 demos, 2 optional)                                                                                                                        |
| 2   | 11:30 to 12:35 | 1h 05m | [Lab: Headless Claude Code and parallel git worktrees](../labs/05-cli/lab-01-headless-and-worktrees.md)            | Run `claude -p` one-shot prompts, wrap them in a script with meaningful exit codes, and run independent changes in parallel across git worktrees. Background tasks and on-demand skill injection close it out.                                                            |
| 2   | 12:35 to 13:35 | 1h 00m | Lunch                                                                                                              |                                                                                                                                                                                                                                                                           |
| 2   | 13:35 to 14:20 | 45m    | [Sub-Agents](06-subagents-agent-teams/readme.md)                                                                   | Frontmatter and scoping, backend, frontend and QA domain agents, evaluating agent performance, orchestration and workflow graphs (4 topics, 3 demos, 2 optional)                                                                                                                      |
| 2   | 14:20 to 15:15 | 55m    | [Lab: Build a specialized documentation agent](../labs/06-subagents-agent-teams/lab-01-specialized-agents.md)      | Reason through the design of a documentation sub-agent in conversation first, then implement it with brand-voice enforcement built in.                                                                                                                                    |
| 2   | 15:15 to 15:25 | 10m    | Break                                                                                                              |                                                                                                                                                                                                                                                                           |
| 2   | 15:25 to 16:20 | 55m    | [Agent Teams](06-subagents-agent-teams/readme.md)                                                                  | Lead, teammates, shared task list and mailbox, spawning and steering a team, debate and quality gates (3 topics, 1 demo, 1 optional)                                                                                                                                                 |
| 2   | 16:20 to 16:50 | 30m    | [Lab: Spawn a review team and steer it](../labs/06-subagents-agent-teams/lab-04-spawn-a-review-team.md)            | Enable agent teams, spawn three named reviewers on one codebase, watch them claim tasks off the shared list, redirect one by messaging it directly, and gate the single fix behind plan approval.                                                                         |
| 3   | 09:00 to 09:25 | 25m    | [Optimize the Agentic Harness](07-optimize-observability/readme.md)                                                | Prompt audit, caveman compression, the autoresearch loop (3 topics, 2 demos, 1 optional)                                                                                                                                                                                              |
| 3   | 09:25 to 10:30 | 1h 05m | [Lab: Compress a Bloated Harness with Caveman Mode](../labs/07-optimize-observability/lab-01-caveman-compress.md)  | Compress a bloated `CLAUDE.md` with a caveman rewrite, verify it still binds the model the same way the original did, then codify the rewrite prompt as a reusable skill.                                                                                                 |
| 3   | 10:30 to 10:40 | 10m    | Break                                                                                                              |                                                                                                                                                                                                                                                                           |
| 3   | 10:40 to 11:05 | 25m    | [Secure and Observe the Agentic Harness](07-optimize-observability/readme.md)                                      | Prompt injection and MCP tool poisoning, hook guardrails and least privilege, tracing and failure diagnosis (3 topics, 2 demos)                                                                                                                                           |
| 3   | 11:05 to 11:55 | 50m    | [Lab: Harden a Newsletter Drafting Agent](../labs/07-optimize-observability/lab-03-harden-newsletter.md)           | Wire four security layers onto a working newsletter agent: quarantine the untrusted read, block destructive commands with a hook, scope what each agent can reach, and cap a runaway with a budget.                                                                       |
| 3   | 11:55 to 12:55 | 1h 00m | Lunch                                                                                                              |                                                                                                                                                                                                                                                                           |
| 3   | 12:55 to 13:20 | 25m    | [Bundle and Distribute Your Config as a Plugin](08-distribution/readme.md)                                         | Why plugins, plugin anatomy, converting a `.claude/` config into a plugin, marketplaces (4 topics, 1 demo)                                                                                                                                                                |
| 3   | 13:20 to 14:25 | 1h 05m | [Lab: Build a Plugin From a `.claude/` Configuration](../labs/08-distribution/lab-01-build-a-plugin.md)            | Convert a working `.claude/` configuration (skills, hooks, slash commands, an MCP server) into a self-contained plugin, then test it locally with `--plugin-dir` and `/reload-plugins`.                                                                                   |
| 3   | 14:25 to 14:35 | 10m    | Break                                                                                                              |                                                                                                                                                                                                                                                                           |
| 3   | 14:35 to 15:10 | 35m    | [Agentic DevOps & Automation](09-agentic-devops/readme.md)                                                         | The deployment agent and its prove-it contract, bootstrapping and hardening Ubuntu over SSH, Compose behind a Caddy edge with TLS, Web Vitals and agentic SEO (3 topics, 4 demos)                                                                                         |
| 3   | 15:10 to 16:50 | 1h 40m | [Lab: Deploy a Containerized React App over SSH](../labs/09-agentic-devops/lab-01-deploy-to-an-ubuntu-box.md)      | Take a containerized React app onto an Ubuntu host you operate yourself: prove SSH access, harden the box, ship the image without a registry, front it with Caddy and TLS. The redeploy loop then goes to a deployment sub-agent whose claims you check against the host. |
| 4   | 09:00 to 09:40 | 40m    | [Claude Agent SDK](10-sdk-managed-agents/readme.md)                                                                | Where the SDK sits against the CLI, the Messages API and Managed Agents, the API surface and output control, parallel agents with session isolation (2 topics, 2 demos)                                                                                                   |
| 4   | 09:40 to 11:15 | 1h 35m | [Lab: Embed Claude in a TypeScript Program](../labs/10-sdk-managed-agents/lab-01-embed-claude.md)                  | Spawn Claude from inside your own TypeScript program with the Agent SDK: one-shot calls, streaming, session resume, custom tools, typed output schemas, and a CI script.                                                                                                  |
| 4   | 11:15 to 11:25 | 10m    | Break                                                                                                              |                                                                                                                                                                                                                                                                           |
| 4   | 11:25 to 12:00 | 35m    | [Claude Managed Agents](10-sdk-managed-agents/readme.md)                                                           | Agent, Environment and Session resources, SSE streaming and file mounts, production features, MCP servers and skills, human-in-the-loop gates, multiagent with outcomes and memory (6 topics, 2 demos, 4 optional)                                                                    |
| 4   | 12:00 to 13:00 | 1h 00m | Lunch                                                                                                              |                                                                                                                                                                                                                                                                           |
| 4   | 13:00 to 14:35 | 1h 35m | [Lab: Managed Agent for Codebase Triage](../labs/10-sdk-managed-agents/lab-03-managed-agent-codebase-triage.md)    | Build a cloud Managed Agent that fixes three planted bugs in a small Python repo, with its own Environment and a human approval gate before any commit lands.                                                                                                             |
| 4   | 14:35 to 14:45 | 10m    | Break                                                                                                              |                                                                                                                                                                                                                                                                           |
| 4   | 14:45 to 15:15 | 30m    | Optional: [Planning & Spec-Driven Development](11-planning/readme.md)                                              | Brownfield analysis, Plan Mode and the constraint ratchet, statefiles and work-package decomposition, the Spec Kit pipeline, a sample feature from brief to tasks (5 topics, 4 demos, 2 optional)                                                                                     |
| 4   | 15:15 to 16:30 | 1h 15m | Optional: [Lab: Drive a Feature Spec-First with Plan Mode](../labs/11-planning/lab-01-spec-driven-from-scratch.md) | Take a notes CLI feature through Plan Mode end to end: clarification, constraint iteration, extended thinking on one hard design decision, a `STATE.md` handoff and sub-agent decomposition.                                                                              |
| 4   | 16:30 to 16:40 | 10m    | Feedback and Questions                                                                                             | Wrap-up, open questions, where to take the harness next                                                                                                                                                                                                                   |
