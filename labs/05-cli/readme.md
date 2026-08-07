# Labs - Module 05: Agentic CLI and Headless Execution

| Lab | Topic | Title | Track | Level | Time | Description |
|-----|-------|-------|-------|-------|------|-------------|
| 01 | Headless | [Drive Claude Code headlessly and run parallel work in git worktrees](lab-01-headless-and-worktrees.md) | Core | Intermediate | 1h | Drive Claude in headless mode (`claude -p`), wire it into bash scripts with meaningful exit codes, run parallel work across git worktrees, and inject skills on demand. |
| 02 | CI + Comparison | [Gate tools with PreToolUse hooks and review pull requests in CI](lab-02-hooks-actions-and-cli-comparison.md) | Optional | Advanced | 1h 30m | Build a PreToolUse hook as a policy gate, run Claude on PRs from a GitHub Actions workflow, then run the same task through OpenAI Codex CLI and Aider to compare the agent-CLI landscape. |
| 03 | Always-On + Fleet | [Keep agents working while you are away from the keyboard](lab-03-always-on-and-fleet.md) | Optional | Advanced | 1h 15m | Persistent sessions, an OS scheduler (cron or Task Scheduler), the Ralph Wiggum loop technique, GitHub Actions on a schedule, and a parallel-worktree fleet pattern using `xargs -P`. |

**Core** is the one lab that teaches this module's central capability; run it if you run nothing else. **Optional** labs go deeper, cover a second tool, or need an account you may not have. **Level** rates the lab itself: Beginner needs no prior Claude Code experience, Intermediate assumes you have configured a harness before, Advanced assumes you are comfortable with hooks, subagents, or headless scripting.

Core path: 1h. All labs: 3h 45m.

Lab 01 is Core because it is the module's foundation and runs entirely locally. Labs 02 and 03 need a GitHub account, and Lab 03's cron and fleet steps are Unix-first, so on Windows they need git-bash or WSL.

Labs 01 to 03 build `cli-utils` as its own git repository outside the course checkout, and the finished counterparts are checked in beside each topic as `01-headless/cli-utils-solution/` and `02-cicd/hooks-solution/`. The starter you scaffold stays pristine (no dependencies, no build output); install, run and generate only inside your own working copy or the solution folders, and use the solutions as the completed reference when you want to compare.
