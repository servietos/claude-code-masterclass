# Labs - Module 09: Security, Hardening & Observability

| Lab | Topic | Title | Track | Level | Time | Description |
|-----|-------|-------|-------|-------|------|-------------|
| 01 | Agent Hardening | [Harden a Newsletter Drafting Agent](lab-01-harden-newsletter.md) | Core | Advanced | 45m | Wire four security layers onto a working agent: quarantine the untrusted read behind a sub-agent contract, block destructive commands with a `PreToolUse` hook, scope each agent with tool lists and a `Read(./.env)` deny rule, and cap a runaway with a session-keyed budget hook. |

**Core** is the one lab that teaches this module's central capability; run it if you run nothing else. **Optional** labs go deeper, cover a second tool, or need an account you may not have. **Level** rates the lab itself: Beginner needs no prior Claude Code experience, Intermediate assumes you have configured a harness before, Advanced assumes you are comfortable with hooks, subagents, or headless scripting.

Core path: 45m. All labs: 45m.

An agent that reads a file you did not write, holds a token you cannot rotate, and loops until the budget runs out is three separate incidents waiting on the same afternoon. This lab wires the four layers from the module demos onto one working agent, in the order they fail: quarantine the untrusted read behind a sub-agent with a strict output contract ([Map the Agent Threat Model](../../demos/09-observability/01-threat-model/readme.md)), block destructive commands with a `PreToolUse` hook ([Apply Guardrails and Least Privilege](../../demos/09-observability/02-guardrails/readme.md)), scope what each agent can reach with tool lists and deny rules ([Secure Secrets and Credentials](../../demos/09-observability/03-secrets/readme.md)), and cap a runaway with a session-scoped budget hook ([Trace Agents and Diagnose Failures](../../demos/09-observability/04-observability/readme.md)).

Two of those layers look convincing and enforce nothing when you get the details wrong, so the lab makes you check both against the docs before you write them: a hook that returns the wrong decision shape blocks the command but throws away the reason, and a frontmatter key the harness does not recognise is decoration, not a control.

The lab has a starter you work in, [`harden-newsletter/`](harden-newsletter/readme.md), and a finished counterpart beside it named [`harden-newsletter-solution/`](harden-newsletter-solution/readme.md). The starter stays pristine (no `.claude/` folder, no hooks, no logs, no counter file); copy `.env.example` to `.env` there and build the wiring yourself, then use the solution folder as the completed reference when you want to compare a hook script or a settings block against a version that has been driven with real `PreToolUse` payloads.

Prerequisites: PowerShell 7 on `PATH` as `pwsh`, since both hooks are `.ps1` and the settings entries spawn them directly. The lab was written and driven against pwsh 7.6.3 and Claude Code 2.1.219. Time budget is 45 minutes.
