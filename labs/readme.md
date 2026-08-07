# Labs

Hands-on exercises that accompany the masterclass modules. Module numbering follows `demos/`, and each module folder contains its own `readme.md` index with one or more sub-labs.

| Module                                                                | Labs            | Core        | Full    | Level        | Focus                                                                                                                                                         |
| --------------------------------------------------------------------- | --------------- | ----------- | ------- | ------------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| [01: Fundamentals](01-fundamentals/readme.md)                         | 3 sub-labs      | 1h 10m      | 2h      | Beginner     | Install Claude Code, build a first prompt-driven REST API, apply five prompting techniques and install a plugin                                               |
| [02: Configure the Harness](02-harness/readme.md)                     | 2 sub-labs      | 1h 15m      | 1h 45m  | Intermediate | Install a community React skill, then configure the harness piece by piece to fix a broken React app                                                          |
| [03: Creating & Managing Skills](03-skills/readme.md)                 | 2 sub-labs      | 1h 15m      | 2h      | Intermediate | Build a composite `invoice-docx` skill with references, a script and injected context, then serve the same renderer as an HTTP document endpoint              |
| [04: MCP](04-mcp/readme.md)                                           | 5 sub-labs      | 1h          | 5h 15m  | Intermediate | Modernize Angular with the Angular MCP, build an event-registration MCP server, build PDF and map MCP Apps, extract a Python MCP server into a reusable skill |
| [05: Agentic CLI & Headless Execution](05-cli/readme.md)              | 3 sub-labs      | 1h          | 3h 45m  | Intermediate | Headless mode and worktrees, hooks plus GitHub Actions plus agent-CLI comparison, always-on patterns and fleet                                                |
| [06: Subagents](06-subagents/readme.md)                               | 3 sub-labs      | 50m         | 3h      | Intermediate | Build a docs agent and a scoped unit-testing agent, then orchestrate both as an agentic team                                                                  |
| [07: Agent Teams](07-agent-teams/readme.md)                           | 1 sub-lab       | 30m         | 30m     | Intermediate | Spawn a three-teammate review team, steer it through the shared task list and direct messages, and gate the one fix behind plan approval                      |
| [08: Optimizing the Agentic Harness](08-optimize/readme.md)           | 3 sub-labs      | 1h          | 3h 15m  | Intermediate | Caveman compression, skill evolution via deterministic experiments, memory architectures                                                                      |
| [09: Security, Hardening & Observability](09-observability/readme.md) | 1 sub-lab       | 45m         | 45m     | Advanced     | Harden a newsletter agent with quarantine, hooks, scoped secrets, and a budget cap                                                                            |
| [10: Bundling & Distributing Plugins](10-distribution/readme.md)      | 2 sub-labs      | 1h          | 1h 45m  | Intermediate | Build a plugin from a `.claude/` configuration, then audit any plugin you install for security                                                                |
| [11: Agentic DevOps](11-agentic-devops/readme.md)                     | 3 sub-labs      | 1h 30m      | 3h 30m  | Advanced     | Ship a containerized React app to an Ubuntu box over SSH behind a Caddy edge, then ship the same app and a Hugo blog to the same box over simpler pipelines   |
| [12: Managed Agents](12-managed-agents/readme.md)                     | 1 sub-lab       | none        | 1h      | Advanced     | Build a cloud-hosted triage agent that fixes planted bugs behind a human approval gate                                                                        |
| [13: Claude Agent SDK](13-claude-sdk/readme.md)                       | 2 sub-labs      | 1h          | 2h      | Intermediate | Embed Claude in a TypeScript program, then orchestrate parallel SDK reviewer agents with session isolation                                                    |
| [14: Planning & Spec-Driven Development](14-planning/readme.md)       | 2 sub-labs      | 1h 15m      | 2h 30m  | Beginner     | Optional. Plan Mode end-to-end, then the same workflow with Spec Kit and BMAD-METHOD                                                                          |
| **Total**                                                             | **33 sub-labs** | **13h 30m** | **33h** |              | One lab per module on the core path, everything on the full path                                                                                              |

## Course Totals

Labs are half the clock. These are the two routes with the module teaching time from [demos](../demos/readme.md) added, excluding breaks.

| Route                                    | Teaching | Labs | Overall     | Days at 8h |
| ---------------------------------------- | -------- | ---- | ----------- | ---------- |
| **Core path**, one lab per module        | 22h 05m  | 14h  | **36h 05m** | **4.5**    |
| **Full path**, every lab in every module | 22h 05m  | 33h  | **55h 05m** | **6.9**    |

The core path is the recommended route for a taught class. It is 4.5 days of pure delivery at eight hours, which in practice runs as roughly six days at six hours, since a full eight-hour day of teaching and labs is not a rate a room sustains. The full path adds every optional lab: 6.9 eight-hour days, or another three delivery days on top of the core route.

Its labs figure reads 14h here and 13h 30m in the table above, and both are right for the question they answer. The table sums the Core column literally, which counts Module 01's 30m setup lab. A taught class hands that out as pre-work and instead schedules Module 12's lab, the one module whose Core cell reads none, so the delivered figure lands 30 minutes higher.

## How to Read Core, Full and Level

Each module marks exactly one lab as **Core** in its own index; every other lab is **Optional**. Optional never means lesser: it means the module's central point already landed in the Core lab, and the rest go deeper, cover a second tool, or need an account you may not have. Module 12 is the one module with no Core lab, because its only lab is gated behind beta access to Managed Agents.

**Level** rates the lab, not the module topic: Beginner needs no prior Claude Code experience, Intermediate assumes you have configured a harness before, Advanced assumes you are comfortable with hooks, subagents, or headless scripting. The module-level rating above is the level of its Core lab.

Timings are calibrated against the one lab that budgets itself, Module 09, which allots 45 minutes across five prompt-driven steps, and against the install and build times measured while verifying these labs. Model-driven steps are the largest variable: a step that lands first time takes a few minutes, and the same step takes three times that when you push back on the first answer, which the guides frequently ask you to do.

Four modules carry prerequisites that sit outside the time above, because they depend on accounts, keys, or downloads rather than on you:

| Module | What it needs before the clock starts                                                                                                                              |
| ------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| 05     | A GitHub account with `gh` authenticated, plus optional OpenAI Codex and Aider installs for the comparison                                                         |
| 11     | Docker running locally for Lab 01, no cloud account needed. Labs 02 and 03 need a GitHub account with Pages enabled, and Lab 03 also needs a Hugo Extended install |
| 12     | Beta access to Managed Agents and an `ANTHROPIC_API_KEY`. Without access this lab is a read-through, not a build                                                   |
| 13     | An `ANTHROPIC_API_KEY`. Every SDK call in these two labs is billed to it                                                                                           |

Add 15 to 30 minutes to Modules 02, 04, 06 and 11 on a cold machine: they install Angular, .NET or React dependency trees, and a first `npm install` on the Angular app is the slowest single wait in the course.

## Where to Open Claude Code

The harness is project-scoped. `CLAUDE.md`, `.claude/settings.json` hooks, `.claude/agents/`, `.claude/skills/`, `.claude/commands/` and `.mcp.json` are all read from the directory you launched `claude` in, not from wherever the file happens to sit. Opening the session in the wrong folder is the most common reason a lab appears to do nothing: the hook never fires, the skill is never discovered, and nothing reports an error.

Two kinds of lab follow from that, and all 33 lab guides carry a "Where to Open Claude Code" section saying which one they are:

- 30 guides build their own harness inside their own project folder (`tasks-app/`, `cli-utils/`, `notes-cli/`, `harden-newsletter/`, `notes-toolkit-source/` and the rest). `cd` into that folder and start `claude` there, so the harness you just wrote is the one that loads.
- 3 guides consume the harness this repository already ships and open at the repo root: Module 01 Lab 01 (install and verify the CLI), Module 04 Lab 03 (the PDF MCP App, which configures Claude Desktop), and Module 06 Lab 03 (the agentic team driving the committed `dotnet-expert` and `angular-expert`). Those three read the repository's `.claude/` and never write to it.

No lab writes into this repository's `.claude/` directory. Module 02 is the sharpest illustration of the rule rather than an exception to it: each of its labs opens inside its own starter under `labs/02-harness/`, and every skill, hook, command and `.mcp.json` entry they create lands there.

Whenever a lab edits `.claude/settings.json` or adds a hook, restart the session with `/exit` then `claude` before testing it. Hook configuration is read at startup, so an unrestarted session keeps running the old policy.

Each runnable project folder is the starter and stays pristine: no `node_modules`, no lockfile, no build output. Its finished counterpart lives beside it as `<starter>-solution/`, which is where installs, runs and lockfiles belong. Guides walk you through the starter and name the solution once as the completed reference.
