# Demos

Great software no longer has to cost a fortune or consume every hour of your day. With Claude Code, you get an engineering partner that plans, builds, tests, and ships alongside you at a fraction of the time and cost. This isn't about prompting an AI. It's about designing systems that multiply what you can deliver.

Welcome to the new standard.

Agentic software engineering is a discipline shift, and once you experience it, there's no going back. Instead of spending days on tasks that take agents minutes, you orchestrate workflows that reduce cost, eliminate repetition, and scale your output without scaling your team. The developers who master this don't just move faster. They do more with less, and they do it consistently.

Across 14 hands-on modules, you'll go from Claude Code fundamentals to production-grade multi-agent pipelines. You'll design composable skills, build MCP tools that connect agents to real systems, extend and customize the harness with mods, architect parallel sub-agent workflows, and harden everything for real-world conditions. Every module is built around genuine engineering decisions, because the goal was never to write more code. It was always to build software that matters.

The class also covers everything required to pass the [Claude Certified Architect: Foundations certification](https://anthropic-partners.skilljar.com/claude-certified-architect-foundations-certification). Every exam area, from the CLAUDE.md constitution and the permission model through skills, MCP, sub-agents and security, is taught in a module and practiced in its lab. Work through the 14 modules and you are prepared for the exam without any separate study track. Still we want to point out that this is not a dedicated exam prep class.

## Module 1: Claude Code Fundamentals

- Introduction to Claude Code
- Setup & Installation
- Editors: Console, Desktop App, VS Code
- Model Selection Strategy
- Prompt caching, cost and token awareness
- Permission Model: Tools, Bash, Network
- Checkpoints & Session Safety
- Git worktrees: isolated checkouts
- Agents view: background sessions
- Artifacts: results as shareable pages

## Module 2: Claude Code Configure Harness

- Settings Hierarchy: Global, Project, Session
- CLAUDE.md constitution
- @-mentioning files and URLs
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
- Allowed-tools restrictions and metadata conventions
- Composite skills: scripts, references, assets
- Cross-skill references and delegation patterns
- Dynamic context injection: command preprocessing
- Forked execution: agent and background
- Testing: Trigger, correctness, performance
- Distribution: portable folder, skills API, hosting

## Module 4: Consuming & Designing MCP Tools

- MCP architecture: servers, clients, transports
- Session lifecycle and exposed capabilities
- Remote auth: tokens, keys, OAuth
- Building a server in C#
- Inspection with the MCP Inspector
- MCP Apps: interfaces inside the host
- Artifact connectors calling MCP live
- Tool design: granularity, descriptions, resources
- Error and deferred-loading contract

## Module 5: Agentic CLI & Headless Execution

- Agent harness: tools, knowledge, action interfaces
- CLI, terminal, and headless mode
- Headless mode: print, JSON, exit codes
- Least-privilege tool scoping
- CI gates: sentinels and exit codes
- GitHub Actions: scripting agentic workflows
- Parallel worktree lanes and task-queue orchestration
- PreToolUse policy gates across lanes
- Always-on goal patterns with turn limits

## Module 6: Sub-Agents

- Where single-agent sequential hits a ceiling
- Frontmatter: name, model, tools, permission mode
- Restricting tools and permissions per agent
- Backend agent: .NET and Learn MCP
- Frontend agent: Angular and DevTools MCPs
- QA agent: Playwright, no implementation authority
- Evaluating performance with test cases
- Orchestration: prompt delegation, loops, workflow graphs
- Context isolation between parallel agents

## Module 7: Agent Teams

- Where a team beats sub-agents
- Lead, teammates, shared task list, mailbox
- Enabling teams and session state
- Spawning teammates: names and models
- Display modes, agent panel, steering keys
- Task states, dependencies, file-locked claiming
- Messaging between lead and teammates
- Competing hypotheses: teammates disproving each other
- Plan approval and lifecycle hooks
- Team sizing, conflicts, and cost

## Module 8: Optimizing the Agentic Harness & Continuous Learning

- Skills and agents as living artifacts
- Autoresearch loop: propose, evaluate, revert
- Deterministic experiments for skill quality
- Caveman skill: 60-75% output compression
- Compressing CLAUDE.md with caveman-mode
- Memory architectures: statefile and graph
- Updating harness from observed behavior
- Metrics: determinism, output structure, abort rate

## Module 9: Security, Hardening & Observability

- Prompt injection: tool results and files
- Tool poisoning: validating MCP responses
- Untrusted content isolation in agent context
- Guardrails: hard stops and scope constraints
- Least privilege scoping per sub-agent
- Secrets: preventing cross-agent credential leakage
- Tracing tool chains and cost attribution
- Diagnosing stuck, runaway, hallucinating agents
- Artifact governance: toggles, retention, audit events

## Module 10: Bundling & Distributing Plugins

- Plugins vs. standalone configuration: namespacing
- Plugin anatomy: manifest, skills, hooks, MCP
- Bundling skills, hooks, MCP configs
- LSP servers and background monitors
- Default agent activation via plugin settings
- Local testing: plugin directory and reload
- Converting `.claude/` configs into plugins
- Publishing to official and team marketplaces
- Plugins by Anthropic

## Module 11: Agentic DevOps & Deployment

- The deployment sub-agent: allowlists, prove-it contract
- Bootstrapping and hardening Ubuntu over SSH
- Docker Compose behind a Caddy edge
- DNS before the first ACME attempt
- Core Web Vitals and SEO loops

## Module 12: Claude Managed Agents

- Cloud containers with network and files
- Steering agents mid-execution via SSE
- OAuth vaults and token refresh
- Callable-agent patterns with isolated threads
- Session lifecycle: idle, running, termination
- Human-in-the-loop approval gates
- Managed Agents vs. Messages API
- Versioning agents as deployable units

## Module 13: Claude Code SDK

- Spawning Claude Code via the SDK
- Sessions, context, streaming responses
- Custom tools as in-process MCP servers
- Typed output with Zod
- Parallel agents: session isolation, orchestrator pattern
- Output control: tool choice and batches

## Module 14: Planning & Spec-Driven Development (Optional)

- Plan Mode: mechanics and activation
- Stepwise context: questions and constraints
- Spec iteration via feedback loops
- Extended Thinking: steering reasoning chains
- Thinking budget vs. token cost
- Authoring specs and technical plans
- Decomposing tasks into sub-agent packages
- Defining and validating done criteria
- Spec Kit and BMAD-METHOD compared

### Day 1

| Clock          | Length | Deliverable                                                                                              | Description                                                                                                                                                                                                                                        |
| -------------- | ------ | -------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 09:00 to 10:20 | 1h 20m | [Claude Code Fundamentals](01-fundamentals/readme.md)                                                    | Setup and editors, model selection, prompt caching and cost, permissions, checkpoints, git worktrees, agents view, artifacts (8 topics, 7 demos)                                                                                                                 |
| 10:20 to 10:30 | 10m    | Break                                                                                                    |                                                                                                                                                                                                                                                    |
| 10:30 to 11:15 | 45m    | [Lab: Build a Task Tracking REST API](../labs/01-fundamentals/02-hello-claude/readme.md)                 | Build a Python REST API for task management entirely through prompts, one step at a time. Every step gives you the prompt to paste and the result to expect.                                                                                        |
| 11:15 to 12:20 | 1h 05m | [Claude Code Configure Harness](02-harness/readme.md)                                                    | Settings hierarchy, CLAUDE.md constitution, slash commands, MCP servers, skills, sub-agents, hooks and mods, memory (7 topics, 8 demos)                                                                                                                                              |
| 12:20 to 13:20 | 1h 00m | Lunch                                                                                                    |                                                                                                                                                                                                                                                    |
| 13:20 to 14:45 | 1h 25m | [Lab: Configure the Harness on a Broken React App](../labs/02-harness/lab-02-fix-the-react-food-shop.md) | Configure the harness piece by piece (CLAUDE.md, MCP servers, a PostToolUse hook, a slash command, a skill, checkpoints) on a broken React app. The app is the use case; the harness is the lesson.                                                 |
| 14:45 to 15:30 | 45m    | [Creating & Managing Skills](03-skills/readme.md)                                                        | Skills versus slash commands, authoring and frontmatter, composite skills, dynamic context and forked execution, testing and packaging (5 topics, 3 demos)                                                                                          |
| 15:30 to 15:40 | 10m    | Break                                                                                                    |                                                                                                                                                                                                                                                    |
| 15:40 to 17:00 | 1h 20m | [Lab: Package Invoice Generation Into a Skill](../labs/03-skills/lab-01-invoice-docx-skill.md)           | Turn a one-off document script into a composite skill with frontmatter, a reference file, a rendering script, restricted tools and a value injected at load time. It answers "invoice Nordwind for two days of training" with a real Word document. |

### Day 2

| Clock          | Length | Deliverable                                                                                             | Description                                                                                                                                                                                                   |
| -------------- | ------ | ------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 09:00 to 09:30 | 30m    | [Consuming & Designing MCP Tools](04-mcp/readme.md)                                                     | MCP architecture and transports, building a server in C#, MCP apps, artifact connectors, tool design (5 topics, 3 demos)                                                                                      |
| 09:30 to 10:35 | 1h 05m | [Lab: Build the EventTrack Registration MCP Server](../labs/04-mcp/lab-02-eventtrack-mcp-server.md)     | Build a headless Python MCP server that manages events, attendee registrations and per-event capacity, then drive the full registration workflow from Claude Code.                                            |
| 10:35 to 10:45 | 10m    | Break                                                                                                   |                                                                                                                                                                                                               |
| 10:45 to 11:30 | 45m    | [Agentic CLI & Headless Execution](05-cli/readme.md)                                                    | Headless mode and tool scoping, CI gates, worktree lanes with policy hooks and parallel orchestration, always-on goal patterns (4 topics, 5 demos)                                                            |
| 11:30 to 12:35 | 1h 05m | [Lab: Headless Claude Code and parallel git worktrees](../labs/05-cli/lab-01-headless-and-worktrees.md) | Run `claude -p` one-shot prompts, wrap them in a script with meaningful exit codes, and run independent changes in parallel across git worktrees. Background tasks and on-demand skill injection close it out. |
| 12:35 to 13:35 | 1h 00m | Lunch                                                                                                   |                                                                                                                                                                                                               |
| 13:35 to 14:25 | 50m    | [Sub-Agents](06-subagents/readme.md)                                                                    | Frontmatter and scoping, backend, frontend and QA domain agents, evaluating agent performance, orchestration and workflow graphs (6 topics, 5 demos)                                                          |
| 14:25 to 15:20 | 55m    | [Lab: Build a specialized documentation agent](../labs/06-subagents/lab-01-specialized-agents.md)       | Reason through the design of a documentation sub-agent in conversation first, then implement it with brand-voice enforcement built in.                                                                        |
| 15:20 to 15:30 | 10m    | Break                                                                                                   |                                                                                                                                                                                                               |
| 15:30 to 16:30 | 1h 00m | [Agent Teams](07-agent-teams/readme.md)                                                                 | Lead, teammates, shared task list and mailbox, spawning and steering a team, debate and quality gates (3 topics, 2 demos)                                                                                     |
| 16:30 to 17:00 | 30m    | [Lab: Spawn a review team and steer it](../labs/07-agent-teams/lab-01-spawn-a-review-team.md)           | Enable agent teams, spawn three named reviewers on one codebase, watch them claim tasks off the shared list, redirect one by messaging it directly, and gate the single fix behind plan approval.             |

### Day 3

| Clock          | Length | Deliverable                                                                                                   | Description                                                                                                                                                                                                                                                             |
| -------------- | ------ | ------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 09:00 to 09:30 | 30m    | [Optimizing the Agentic Harness & Continuous Learning](08-optimize/readme.md)                                 | Harness artifacts as living code, caveman compression, the autoresearch loop, memory architectures (4 topics, 3 demos)                                                                                                                                                  |
| 09:30 to 10:35 | 1h 05m | [Lab: Compress a Bloated Harness with Caveman Mode](../labs/08-optimize/lab-01-caveman-compress.md)           | Compress a bloated `CLAUDE.md` with a caveman rewrite, verify it still binds the model the same way the original did, then codify the rewrite prompt as a reusable skill.                                                                                                |
| 10:35 to 10:45 | 10m    | Break                                                                                                         |                                                                                                                                                                                                                                                                         |
| 10:45 to 11:10 | 25m    | [Security, Hardening & Observability](09-observability/readme.md)                                             | Prompt injection and the threat model, hook guardrails, secrets and least privilege, tracing and cost attribution (4 topics, 2 demos)                                                                                                                                    |
| 11:10 to 12:00 | 50m    | [Lab: Harden a Newsletter Drafting Agent](../labs/09-observability/lab-01-harden-newsletter.md)               | Wire four security layers onto a working newsletter agent: quarantine the untrusted read, block destructive commands with a hook, scope what each agent can reach, and cap a runaway with a budget.                                                                      |
| 12:00 to 13:00 | 1h 00m | Lunch                                                                                                         |                                                                                                                                                                                                                                                                         |
| 13:00 to 13:25 | 25m    | [Bundling & Distributing Plugins](10-distribution/readme.md)                                                  | Why plugins, plugin anatomy, converting a `.claude/` config into a plugin, marketplaces (4 topics, 1 demo)                                                                                                                                                               |
| 13:25 to 14:30 | 1h 05m | [Lab: Build a Plugin From a `.claude/` Configuration](../labs/10-distribution/lab-01-build-a-plugin.md)       | Convert a working `.claude/` configuration (skills, hooks, slash commands, an MCP server) into a self-contained plugin, then test it locally with `--plugin-dir` and `/reload-plugins`.                                                                                  |
| 14:30 to 14:40 | 10m    | Break                                                                                                         |                                                                                                                                                                                                                                                                         |
| 14:40 to 15:20 | 40m    | [Agentic DevOps & Deployment](11-agentic-devops/readme.md)                                                    | The deployment agent and its prove-it contract, bootstrapping and hardening Ubuntu over SSH, Compose behind a Caddy edge with TLS, Web Vitals and agentic SEO (3 topics, 4 demos)                                                                                       |
| 15:20 to 17:00 | 1h 40m | [Lab: Deploy a Containerized React App over SSH](../labs/11-agentic-devops/lab-01-deploy-to-an-ubuntu-box.md) | Take a containerized React app onto an Ubuntu host you operate yourself: prove SSH access, harden the box, ship the image without a registry, front it with Caddy and TLS. The redeploy loop then goes to a deployment sub-agent whose claims you check against the host. |

### Day 4

| Clock          | Length | Deliverable                                                                                                        | Description                                                                                                                                                                                 |
| -------------- | ------ | ------------------------------------------------------------------------------------------------------------------ | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 09:00 to 09:50 | 50m    | [Claude Managed Agents](12-managed-agents/readme.md)                                                               | Agent, Environment and Session resources, SSE streaming and file mounts, versioning, human-in-the-loop gates (4 topics, 4 demos)                                                            |
| 09:50 to 11:25 | 1h 35m | [Lab: Managed Agent for Codebase Triage](../labs/12-managed-agents/lab-01-managed-agent-codebase-triage.md)         | Build a cloud Managed Agent that fixes three planted bugs in a small Python repo, with its own Environment and a human approval gate before any commit lands.                               |
| 11:25 to 11:35 | 10m    | Break                                                                                                              |                                                                                                                                                                                             |
| 11:35 to 12:15 | 40m    | [Claude Code SDK](13-claude-sdk/readme.md)                                                                         | Where the SDK sits against the CLI and the Messages API, the API surface, parallel agents with session isolation, output control (4 topics, 2 demos)                                        |
| 12:15 to 13:15 | 1h 00m | Lunch                                                                                                              |                                                                                                                                                                                             |
| 13:15 to 14:50 | 1h 35m | [Lab: Embed Claude in a TypeScript Program](../labs/13-claude-sdk/lab-01-embed-claude.md)                           | Spawn Claude from inside your own TypeScript program with the Agent SDK: one-shot calls, streaming, session resume, custom tools, typed output schemas, and a CI script.                    |
| 14:50 to 15:00 | 10m    | Break                                                                                                              |                                                                                                                                                                                             |
| 15:00 to 15:35 | 35m    | Optional: [Planning & Spec-Driven Development](14-planning/readme.md)                                              | Plan Mode and the constraint ratchet, extended thinking, statefiles and work-package decomposition, Spec Kit and BMAD (3 topics, 6 demos)                                                   |
| 15:35 to 16:50 | 1h 15m | Optional: [Lab: Drive a Feature Spec-First with Plan Mode](../labs/14-planning/lab-01-spec-driven-from-scratch.md) | Take a notes CLI feature through Plan Mode end to end: clarification, constraint iteration, extended thinking on one hard design decision, a `STATE.md` handoff and sub-agent decomposition. |
| 16:50 to 17:00 | 10m    | Feedback and Questions                                                                                             | Wrap-up, open questions, where to take the harness next                                                                                                                                     |
