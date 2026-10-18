# Labs - Module 01: Fundamentals

| Lab | Topic | Title | Track | Level | Time | Description |
|-----|-------|-------|-------|-------|------|-------------|
| 01 | Setup | [Install and Set Up Claude Code](01-setup-claude/readme.md) | Required | Beginner | 30m | Install Claude Code CLI, authenticate, and explore it through the VS Code extension. |
| 02 | First App | [Build a Task Tracking REST API](02-hello-claude/readme.md) | Core | Beginner | 40m | Build a Python REST API for task management using Claude Code. Every step is prompt-driven: you provide the prompt, Claude does the work. |
| 03 | Model Selection | [Route Models and Keep the Cache Warm](03-route-models-and-cache/readme.md) | Optional | Beginner | 1h 10m | Run the same three tasks on Haiku, Sonnet and Opus, measure each with `/usage` and `/context`, and write a `CLAUDE.md` routing policy plus cache notes from the numbers. |
| 04 | Permissions | [Lock Down a Secrets File With Permission Rules](04-permission-settings/readme.md) | Optional | Beginner | 1h 5m | Write allow, ask and deny rules in `.claude/settings.json` plus a git-ignored `settings.local.json`, and prove each rule by attempting the blocked path. |
| 05 | Checkpoints and Worktrees | [Recover From a Runaway Edit and Run Two Sessions in Parallel](05-checkpoints-and-worktrees/readme.md) | Optional | Beginner | 1h 20m | Rewind an over-reaching refactor with `/rewind` and prove it with a green suite and a clean `git status`, then run two sessions in separate worktrees on the same file, review, merge and remove their branches. |
| 06 | Agents View | [Supervise Three Background Sessions and Merge Only the Branches That Pass Review](06-agents-view/readme.md) | Optional | Beginner | 1h 15m | Dispatch three chores with `--bg`, triage them by state in the Agents View, answer a stalled session from the peek panel, and merge only the branches that pass a written review gate. |
| 07 | Artifacts | [Publish a CI Failure Page and Revise It Through Versions](07-publish-an-artifact/readme.md) | Optional | Beginner | 1h 10m | Publish a CSV as a private claude.ai page, revise the same URL through versions from a fresh session, restyle it from design tokens in `CLAUDE.md`, and check the fallback when the `Artifact` tool is denied. |

**Core** is the one lab that teaches this module's central capability; run it if you run nothing else. **Optional** labs go deeper, cover a second tool, or need an account you may not have. **Required** is a prerequisite; nothing else in the course works until Claude Code is installed and authenticated. **Level** rates the lab itself: Beginner needs no prior Claude Code experience, Intermediate assumes you have configured a harness before, Advanced assumes you are comfortable with hooks, subagents, or headless scripting.

Core path: 1h 10m. All labs: 7h 10m.
