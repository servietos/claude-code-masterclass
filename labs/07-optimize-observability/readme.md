# Labs - Module 07: Optimizing, Securing & Observing the Harness

| Lab | Topic | Title | Track | Level | Time | Description |
|-----|-------|-------|-------|-------|------|-------------|
| 01 | Compression | [Compress a Bloated Harness with Caveman Mode](lab-01-caveman-compress.md) | Core | Intermediate | 1h | Compress a bloated CLAUDE.md by instructing Claude to rewrite it "as a caveman": terse, no articles, no hedging. Measure the token drop with tiktoken, verify behaviour is preserved, then codify the prompt as a reusable skill. |
| 02 | Metrics | [Evolve a Skill with Deterministic Experiments](lab-02-evolve-via-metrics.md) | Optional | Advanced | 1h 15m | Write an eval case and graders for a release-notes plugin, run it with `claude plugin eval`, then run two propose-evaluate-revert cycles to improve it. |
| 03 | Agent Hardening | [Harden a Newsletter Drafting Agent](lab-03-harden-newsletter.md) | Core | Advanced | 45m | Wire four security layers onto a working agent: quarantine the untrusted read behind a sub-agent contract, block destructive commands with a `PreToolUse` hook, scope each agent with tool lists and a `Read(./.env)` deny rule, and cap a runaway with a session-keyed budget hook. |
| 04 | Prompt Audit | [Audit a Harness for Dated Instructions](lab-04-audit-dated-instructions.md) | Optional | Intermediate | 45m | Run `/doctor prompt-audit` over a harness seeded with pressure language, a missing script, a renamed file and a test-framework contradiction, verify two High rows from the shell, audit one skill with `/claude-api prompt-audit`, apply the diff and re-audit until nothing reaches it. |

**Core** labs teach this module's central capabilities, one for optimizing the harness and one for hardening it; run them if you run nothing else. **Optional** labs go deeper, cover a second tool, or need an account you may not have. **Level** rates the lab itself: Beginner needs no prior Claude Code experience, Intermediate assumes you have configured a harness before, Advanced assumes you are comfortable with hooks, subagents, or headless scripting.

Core path: 1h 45m. All labs: 3h 45m.

Lab 01 is Core because the compression technique is immediately reusable on any project and the lab is self-contained.

Each lab has its own project inside this module's topic folders and ships a completed reference beside it. All three starters are already in the repo, so no lab scaffolds anything.

| Lab | You work in | Completed reference |
|---|---|---|
| 01 | [`01-compression/caveman-lab/`](01-compression/caveman-lab/readme.md) | [`01-compression/caveman-lab-solution/`](01-compression/caveman-lab-solution/readme.md) |
| 02 | [`02-evolution/release-notes-lab/`](02-evolution/release-notes-lab/readme.md) | [`02-evolution/release-notes-lab-solution/`](02-evolution/release-notes-lab-solution/readme.md) |
| 03 | [`harden-newsletter/`](harden-newsletter/readme.md) | [`harden-newsletter-solution/`](harden-newsletter-solution/readme.md) |
| 04 | [`audit-dated-instructions/`](audit-dated-instructions/) | none: the lab's deliverables are the files you write |

Lab 01's `caveman-lab` belongs to this module and is already checked in at `labs/07-optimize-observability/01-compression/caveman-lab/`, so change into it and run `npm install` rather than creating anything.

An agent that reads a file you did not write, holds a token you cannot rotate, and loops until the budget runs out is three separate incidents waiting on the same afternoon. Lab 03 wires the four layers from the module demos onto one working agent, in the order they fail: quarantine the untrusted read behind a sub-agent with a strict output contract ([Map the Agent Threat Model](../../demos/07-optimize-observability/04-threat-model/readme.md)), block destructive commands with a `PreToolUse` hook and scope what each agent can reach with tool lists and deny rules ([Apply Guardrails and Least Privilege](../../demos/07-optimize-observability/05-guardrails/readme.md)), and cap a runaway with a session-scoped budget hook ([Trace Agents and Diagnose Failures](../../demos/07-optimize-observability/06-observability/readme.md)).

Two of those layers look convincing and enforce nothing when you get the details wrong, so the lab makes you check both against the docs before you write them: a hook that returns the wrong decision shape blocks the command but throws away the reason, and a frontmatter key the harness does not recognise is decoration, not a control.

Lab 03's starter stays pristine (no `.claude/` folder, no hooks, no logs, no counter file); copy `.env.example` to `.env` there and build the wiring yourself, then use the solution folder as the completed reference when you want to compare a hook script or a settings block against a version that has been driven with real `PreToolUse` payloads.

Tooling the labs assume on `PATH`: Node and npm (Lab 01), Python 3.10 or newer with `tiktoken` installed in a per-lab virtual environment (Lab 01), Claude Code 2.1.269 or later for `claude plugin eval` (Lab 02), PowerShell 7 as `pwsh` (Lab 03, since both hooks are `.ps1` and the settings entries spawn them directly). Lab 03 was written and driven against pwsh 7.6.3 and Claude Code 2.1.219.
