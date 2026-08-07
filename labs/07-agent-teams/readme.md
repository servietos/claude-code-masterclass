# Labs - Module 07: Agent Teams

| Lab | Topic | Title | Track | Level | Time | Description |
|-----|-------|-------|-------|-------|------|-------------|
| 01 | Review Team | [Spawn a review team and steer it](lab-01-spawn-a-review-team.md) | Core | Intermediate | 30m | Enable agent teams, spawn three named reviewers on one unreviewed service, watch them claim tasks off the shared list, redirect one by messaging it directly, and gate the single fix behind plan approval. |

**Core** is the one lab that teaches this module's central capability; run it if you run nothing else. **Optional** labs go deeper, cover a second tool, or need an account you may not have. **Level** rates the lab itself: Beginner needs no prior Claude Code experience, Intermediate assumes you have configured a harness before, Advanced assumes you are comfortable with hooks, subagents, or headless scripting.

Core path: 30m. All labs: 30m.

Agent teams are experimental and need Claude Code 2.1.178 or newer, and three teammates bill roughly three times a single-session review of the same code. Check `claude --version` before the clock starts.

The lab starter is `01-review/notes-api-py`, and your finished counterpart is the `notes-api-py-solution/` copy you make in Step 0. The starter stays pristine (no generated files, no findings); the review file the team writes and the one approved fix land in the solution folder, while the agent-teams flag goes into your global harness at `~/.claude/settings.json`.
