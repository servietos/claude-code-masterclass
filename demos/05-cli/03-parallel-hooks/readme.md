# Enforce Policy Hooks Across Parallel Worktrees

Two safety mechanisms make unmonitored agent runs reliable at scale: physical directory isolation and harness-level policy enforcement. Git worktrees give each agent its own working directory while sharing a single repository history, which prevents agents running in parallel from overwriting each other's changes. A PreToolUse hook blocks any tool call that matches a policy rule regardless of what the prompt says, and because it lives in the checkout it covers every lane the orchestrator opens.

## Git Worktrees as Agent Lanes

A Git worktree is a separate checkout of the same repository. Each worktree has its own branch, its own working tree, and its own uncommitted state. Two agents running in separate worktrees cannot conflict at the file level because they are operating on different physical paths. When both finish, their branches are independent and can be merged in whatever order the orchestration script requires.

The `git worktree add <path> -b <branch>` command creates a new directory at `<path>` checked out on a new branch `<branch>`. From that point, any `git` command run inside `<path>` operates on that branch only, and the original repository directory continues on its own branch unaffected.

A worktree is not a clone. Both the original directory and the worktree share the same `.git` directory and the same object database, so creating one is fast: no network, no copy. The two checkouts stay connected, with refs, tags, and remote tracking branches visible from either directory. The constraint is that the same branch cannot be checked out in two worktrees simultaneously, which is what makes one branch per lane the natural unit.

The practical workflow is: create a worktree per agent lane, launch Claude in each worktree with `cd worktree-path && claude -p "..."`, wait for all background processes to finish, then merge or cherry-pick the resulting branches.

## Committing Inside a Worktree

Commits made inside a worktree are commits on the worktree's branch. Running `git add` and `git commit` inside the worktree directory advances that branch's HEAD exactly as it would in the original repository directory. The commit is immediately visible from the original directory via `git log --all`. No synchronization step is needed because both directories share the same object store.

When an agent runs inside a worktree with `Bash(git:*)` allowed, it can commit its own work without touching any other branch. This is the isolation guarantee that makes parallel agent runs safe: agent A commits on `feat/a`, agent B commits on `feat/b`, and neither can reach the other's branch through normal Git operations.

## Policy Gates Are a Property of the Checkout

A `PreToolUse` hook is registered in `.claude/settings.json` and anchored with `$CLAUDE_PROJECT_DIR`, both of which are tracked files, so every worktree checks the gate out again and loads it. A prompt instruction travels with one session; a hook travels with the repository.

## Helpful Claude Code CLI Commands

| Command | Usage |
|---|---|
| `claude -p "prompt" --settings .claude/settings.json` | Run an agent under an explicit settings file so the `PreToolUse` policy gate is loaded. |
| `claude -p "prompt" --allowed-tools "Read,Edit,Bash(git:*),Bash(npm:*)"` | Run an agent inside a worktree with git and npm access for committing results. |
| `claude -p "prompt" --max-turns 10 &` | Launch each worktree lane in the background, then `wait` for all of them to finish. |

## Key Topics Covered in This Module

- [Claude Code hooks](https://code.claude.com/docs/en/hooks): PreToolUse registration and how `$CLAUDE_PROJECT_DIR` resolves per checkout
- [Git worktrees](https://git-scm.com/docs/git-worktree): `add`, `list`, `remove`, and `prune` subcommands with all relevant flags
- [git merge](https://git-scm.com/docs/git-merge): `--no-ff` flag and merge commit anatomy for automated integration workflows
