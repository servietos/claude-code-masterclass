---
presents: demo-worktrees-intro.md
budget: 4 min
beats: 4
---

# Present: Run Two Claude Sessions Without Them Colliding

Four beats build two working trees over one history, dispatch sessions into them, and review a branch without checking it out. The room walks away knowing that two directories over one history is the whole mechanism.

------

**No solution folder ships, and that is the proof:** three sessions edit the same folder while `git status --short` prints nothing. Every beat quotes plain `git` and `claude`, identical in Bash and PowerShell.

## Beats

### Beat 1: Claude Code creates the worktree and locks it (1 min)

**Open:** [`readme.md`](readme.md#how-claude-code-uses-worktrees) · [Step 1: Run two sessions in parallel and prove they cannot collide](demo-worktrees-intro.md#step-1-run-two-sessions-in-parallel-and-prove-they-cannot-collide)
**Say:** The everyday form is a flag, with the path, the branch name and the starting commit all decided for you. A tree a live session is using is marked, and the mark is what stops a cleanup sweep from deleting it.

```bash
claude --worktree feature-auth
```

**Result:** a second worktree at `.claude/worktrees/feature-auth/` on `worktree-feature-auth`, marked `locked` for as long as the session is alive so a cleanup sweep cannot delete work in progress

```text
<repo>                                 f0f9e35 [v2]
<repo>/.claude/worktrees/feature-auth  08386d3 [worktree-feature-auth] locked
```

**Gotcha:** you never run `git worktree add`: the flag creates `.claude/worktrees/<name>/` on a `worktree-<name>` branch off the default branch, and starts the session there.

### Beat 2: One file, two contents, at the same moment (1 min)

**Open:** [`worktree-sandbox/app.js`](worktree-sandbox/app.js) · the `greet` template literal · [Step 1: Run two sessions in parallel and prove they cannot collide](demo-worktrees-intro.md#step-1-run-two-sessions-in-parallel-and-prove-they-cannot-collide)
**Say:** Two sessions hold different contents for the same path at the same instant, neither aware of the other. That is not a merge, not a stash and not a race git will resolve later.

```text
In demos/01-fundamentals/06-git-worktrees/worktree-sandbox/, edit app.js so the greeting template ends with an exclamation mark. Do not commit.
```

**Result:** one path, two contents; the right side lives only under `.claude/worktrees/hotfix-greet/`, and `git status --short` in the checkout prints nothing

```diff
 export function greet(name) {
-  return `Hello, ${name}`
+  return `Hello, ${name}!`
 }
```

**Gotcha:** the left side is your checkout, the right side is the `hotfix-greet` worktree, both live.

### Beat 3: A background session isolates itself without being asked (1 min)

**Open:** [Step 2: Send a task to the background and watch it isolate itself](demo-worktrees-intro.md#step-2-send-a-task-to-the-background-and-watch-it-isolate-itself) · [`worktree-sandbox/`](worktree-sandbox)
**Say:** Work nobody is watching cannot be allowed into the checkout you are still typing in, so the session moves itself first and edits second. It takes its branch name from the task, not from you.

```bash
claude --bg "In demos/01-fundamentals/06-git-worktrees/worktree-sandbox/, create NOTES.md with three bullet points about git worktrees. Commit it with the message 'docs: add NOTES.md'."
```

**Result:** the session named its own worktree `notes-md` and committed there, while `git status` in the checkout stayed empty

```text
1e87867 docs: add NOTES.md
4e88f4c chore: update models and presentation materials
```

**Gotcha:** supervising the session is [07: Agents View](../07-agents-view/readme.md); here the only claim is that the commit exists and the checkout did not move.

### Beat 4: Review a branch you never check out (1 min)

**Open:** [Step 3: Review a branch without checking it out](demo-worktrees-intro.md#step-3-review-a-branch-without-checking-it-out) · [`worktree-sandbox/`](worktree-sandbox)
**Say:** Reading a branch you are not standing on is ordinary git and needs nothing Claude Code adds. It matters most for a file that did not exist before, since a diff of a new file is the entire file.

```bash
git diff --stat master..worktree-notes-md
git show worktree-notes-md:demos/01-fundamentals/06-git-worktrees/worktree-sandbox/NOTES.md
```

**Result:** a seven-line `NOTES.md` that exists on `worktree-notes-md` alone, read from a checkout standing on master

```text
 demos/01-fundamentals/06-git-worktrees/worktree-sandbox/NOTES.md | 7 +++++++
 1 file changed, 7 insertions(+)
```

**Gotcha:** `git show <branch>:<path>` prints a whole file straight out of a branch checked out somewhere else.

## If the room asks

| Question | Answer |
|---|---|
| Who cleans up the worktrees I forget? | A periodic sweep removes the ones Claude created past `cleanupPeriodDays`, skipping any holding changes or unpushed commits, and never touching yours. |
| How do I show they are really separate? | `git worktree list` in Step 1 prints three entries, the two worktrees both branched from `master` at `08386d3` and both `locked`. |
