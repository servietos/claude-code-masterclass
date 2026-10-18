# wt-demo

Sandbox for the git worktrees demo. It runs in place: this course repository is already a git repository, which is the only prerequisite a worktree has, so every command in the guide runs from the repository root.

The demo leaves worktree directories under `.claude/worktrees/`, which is gitignored, and `worktree-*` branches in this repository. Remove both by hand when you finish: `git worktree remove` for each directory and `git branch -D` for each branch.
