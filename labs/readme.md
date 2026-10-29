# Labs

Hands-on exercises that accompany the masterclass modules. Module numbering follows `demos/`, and each module folder contains its own `readme.md` index with one or more sub-labs.

| Module                                                                | Labs            | Core        | Full    | Level        | Focus                                                                                                                                                         |
| --------------------------------------------------------------------- | --------------- | ----------- | ------- | ------------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| [01: Fundamentals](01-fundamentals/readme.md)                         | 7 sub-labs      | 1h 10m      | 7h 10m  | Beginner     | Install Claude Code, build a first prompt-driven REST API, route models and keep the cache warm, lock down a secrets file with permission rules, rewind a runaway edit, supervise background sessions, publish an artifact |
| [02: Configure the Harness](02-harness/readme.md)                     | 4 sub-labs      | 1h 15m      | 3h 55m  | Intermediate | Install a community React skill, configure the harness to fix a broken React app, apply five prompting techniques, build a mod test-first                                                          |
| [03: Creating & Managing Skills](03-skills/readme.md)                 | 5 sub-labs      | 1h 15m      | 5h 5m   | Intermediate | Build a composite `invoice-docx` skill, serve the same renderer as an HTTP document endpoint, install a catalog DOCX skill, fork a skill into a subagent, then test and package a skill |
| [04: MCP](04-mcp/readme.md)                                           | 6 sub-labs      | 1h          | 6h 35m  | Intermediate | Modernize Angular with the Angular MCP, build an event-registration MCP server, build PDF and map MCP Apps, extract a Python MCP server into a reusable skill, publish a connector-backed artifact that reads live data |
| [05: Agentic CLI & Headless Execution](06-automate-cli/readme.md)              | 3 sub-labs      | 1h          | 3h 45m  | Intermediate | Headless mode and worktrees, hooks plus GitHub Actions plus agent-CLI comparison, always-on patterns and fleet                                                |
| [06: Subagents and Agent Teams](05-subagents-agent-teams/readme.md)   | 6 sub-labs      | 1h 20m      | 6h 20m  | Intermediate | Build a docs agent and a scoped unit-testing agent, orchestrate both as an agentic team, spawn and steer a review team, converge a review loop, then debate a root cause with a team |
| [07: Optimizing, Securing & Observing the Harness](07-optimize-observability/readme.md) | 4 sub-labs      | 1h 45m      | 3h 45m  | Intermediate | Caveman compression, skill evolution via deterministic experiments, hardening a newsletter agent with quarantine, hooks, scoped tools, and a budget cap, then a prompt audit for dated instructions |
| [08: Bundling & Distributing Plugins](08-distribution/readme.md)      | 3 sub-labs      | 1h          | 3h      | Intermediate | Build a plugin from a `.claude/` configuration, audit any plugin you install for security, then publish it through a team catalog pinned to a tag and a commit sha |
| [09: Agentic DevOps](09-agentic-devops/readme.md)                     | 4 sub-labs      | 1h 30m      | 4h 45m  | Advanced     | Ship a containerized React app to an Ubuntu box over SSH behind a Caddy edge, ship the same app and a Hugo blog over simpler pipelines, then fix Web Vitals and SEO findings on the deployed app |
| [10: Claude Agent SDK & Managed Agents](10-sdk-managed-agents/readme.md) | 5 sub-labs      | 1h          | 5h 25m  | Intermediate | Embed Claude in a TypeScript program, orchestrate parallel SDK reviewer agents, build a cloud-hosted triage agent behind a human approval gate, coordinate several Agents with outcomes and memory, then extend an Agent with an MCP server and a skill |
| [11: Planning & Spec-Driven Development](11-planning/readme.md)       | 3 sub-labs      | 1h 15m      | 3h 20m  | Beginner     | Optional. Plan Mode end-to-end, the same workflow with Spec Kit and BMAD-METHOD, then a parallel-subagent harvest of a brownfield project's current state |
| **Total**                                                             | **50 sub-labs** | **13h 30m** | **53h 5m** |              | One lab per module on the core path, everything on the full path                                                                                              |

## Course Totals

Labs are half the clock. These are the two routes with the module teaching time from [demos](../demos/readme.md) added, excluding breaks.

| Route                                    | Teaching | Labs | Overall     | Days at 8h |
| ---------------------------------------- | -------- | ---- | ----------- | ---------- |
| **Core path**, one lab per module        | 22h 05m  | 14h  | **36h 05m** | **4.5**    |
| **Full path**, every lab in every module | 22h 05m  | 53h 5m | **75h 10m** | **9.4**    |

The core path is the recommended route for a taught class. It is 4.5 days of pure delivery at eight hours, which in practice runs as roughly six days at six hours, since a full eight-hour day of teaching and labs is not a rate a room sustains. The full path adds every optional lab: 9.4 eight-hour days, or almost five more delivery days on top of the core route.

Its labs figure reads 14h here and 13h 30m in the table above, and both are right for the question they answer. The table sums the Core column literally, which counts Module 01's 30m setup lab. A taught class hands that out as pre-work and instead schedules Module 10's Managed Agents triage lab, which the module marks Optional, so the delivered figure lands 30 minutes higher.

## How to Read Core, Full and Level

Each module marks exactly one lab as **Core** in its own index, except Module 05, which marks one for sub-agents and one for agent teams, and Module 07, which marks one for optimizing the harness and one for hardening it; every other lab is **Optional**. Optional never means lesser: it means the module's central point already landed in the Core lab, and the rest go deeper, cover a second tool, or need an account you may not have.

**Level** rates the lab, not the module topic: Beginner needs no prior Claude Code experience, Intermediate assumes you have configured a harness before, Advanced assumes you are comfortable with hooks, subagents, or headless scripting. The module-level rating above is the level of its Core lab.

Timings are calibrated against the one lab that budgets itself, Module 07 Lab 03, which allots 45 minutes across five prompt-driven steps, and against the install and build times measured while verifying these labs. Model-driven steps are the largest variable: a step that lands first time takes a few minutes, and the same step takes three times that when you push back on the first answer, which the guides frequently ask you to do.

Four modules carry prerequisites that sit outside the time above, because they depend on accounts, keys, or downloads rather than on you:

| Module | What it needs before the clock starts                                                                                                                              |
| ------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| 05     | A GitHub account with `gh` authenticated, plus optional OpenAI Codex and Aider installs for the comparison                                                         |
| 09     | Docker running locally for every lab, no cloud or GitHub account needed. Labs 02 and 03 deploy to the box Lab 01 builds, and every build runs inside a container, so no local Node or Hugo install either |
| 10     | A funded Claude Console account and an `ANTHROPIC_API_KEY` in `labs/10-sdk-managed-agents/.env`. Every `query()` call and every Managed Agents Session in the labs is billed to it |
| 11     | `uv` for the Spec Kit CLI in Lab 02, which installs `specify-cli` 1.2.1 into your user profile, and Node 18 or later for the BMAD-METHOD installer |

Add 15 to 30 minutes to Modules 02, 04, 06 and 09 on a cold machine: they install Angular, .NET or React dependency trees, and a first `npm install` on the Angular app is the slowest single wait in the course.

## Where to Open Claude Code

The harness is project-scoped. `CLAUDE.md`, `.claude/settings.json` hooks, `.claude/agents/`, `.claude/skills/`, `.claude/commands/` and `.mcp.json` are all read from the directory you launched `claude` in, not from wherever the file happens to sit. Opening the session in the wrong folder is the most common reason a lab appears to do nothing: the hook never fires, the skill is never discovered, and nothing reports an error.

Two kinds of lab follow from that, and all 50 lab guides carry a "Where to Open Claude Code" section saying which one they are:

- 47 guides build their own harness inside their own project folder (`tasks-app/`, `cli-utils/`, `notes-cli/`, `harden-newsletter/`, `notes-toolkit/` and the rest). `cd` into that folder and start `claude` there, so the harness you just wrote is the one that loads.
- 3 guides consume the harness this repository already ships and open at the repo root: Module 01 Lab 01 (install and verify the CLI), Module 04 Lab 03 (the PDF MCP App, which configures Claude Desktop), and Module 05 Lab 03 (the agentic team driving the committed `dotnet-expert` and `angular-expert`). Those three read the repository's `.claude/` and never write to it.

No lab writes into this repository's `.claude/` directory. Module 02 is the sharpest illustration of the rule rather than an exception to it: each of its labs opens inside its own starter under `labs/02-harness/`, and every skill, hook, command and `.mcp.json` entry they create lands there.

Whenever a lab edits `.claude/settings.json` or adds a hook, restart the session with `/exit` then `claude` before testing it. Hook configuration is read at startup, so an unrestarted session keeps running the old policy.

Each runnable project folder is the starter and stays pristine: no `node_modules`, no lockfile, no build output. Its finished counterpart lives beside it as `<starter>-solution/`, which is where installs, runs and lockfiles belong. Guides walk you through the starter and name the solution once as the completed reference.
