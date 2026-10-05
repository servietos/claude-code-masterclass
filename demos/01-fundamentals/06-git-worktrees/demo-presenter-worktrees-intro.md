---
presents: demo-worktrees-intro.md
budget: 5.5 min
beats: 6
---

# Present: Run Two Claude Sessions Without Them Colliding

Six beats build two working trees over one history, dispatch sessions into them, and clean up afterwards. The room walks away knowing that two directories over one history is the whole mechanism, and that every refusal `git worktree remove` prints is protecting work.

------

**No solution folder ships, and that is the proof:** three sessions edit the same folder while `git status --short` prints nothing. Every beat quotes plain `git` and `claude`, identical in Bash and PowerShell.

## Beats

### Beat 1: Two working trees, one history (1 min)

**Open:** [`readme.md`](readme.md#manual-vs-automatic-worktrees) · [Step 1: Watch git create a second working tree](demo-worktrees-intro.md#step-1-watch-git-create-a-second-working-tree)
**Say:** A worktree gives a second directory its own files while both read and write one history, branches and remotes. Everything else in this topic follows from that single arrangement.

```bash
git worktree add .claude/worktrees/scratch -b scratch
git worktree list
```

**Result:** `.claude/worktrees/scratch/`, created by this step: one repository, two entries, two independent sets of files on disk

```text
<repo>                            4e88f4c [master]
<repo>/.claude/worktrees/scratch  4e88f4c [scratch]
```

**Gotcha:** removing a worktree leaves its branch behind, which is why a full cleanup is always two commands.

### Beat 2: Claude Code creates the worktree and locks it (1 min)

**Open:** [`readme.md`](readme.md#how-claude-code-uses-worktrees) · [Step 2: Start a Claude session in its own worktree](demo-worktrees-intro.md#step-2-start-a-claude-session-in-its-own-worktree)
**Say:** The everyday form is a flag, with the path, the branch name and the starting commit all decided for you. A tree a live session is using is marked, which is a safety property rather than a status label.

```bash
claude --worktree feature-auth
```

**Result:** a second worktree at `.claude/worktrees/feature-auth/` on `worktree-feature-auth`, marked `locked` for as long as the session is alive so a cleanup sweep cannot delete work in progress

```text
<repo>                                 4e88f4c [master]
<repo>/.claude/worktrees/feature-auth  4e88f4c [worktree-feature-auth] locked
```

**Gotcha:** you never run `git worktree add`: the flag creates `.claude/worktrees/<name>/` on a `worktree-<name>` branch off the default branch, and starts the session there.

### Beat 3: One file, two contents, at the same moment (1 min)

**Open:** [`worktree-sandbox/app.js`](worktree-sandbox/app.js) · the `greet` template literal · [Step 3: Run two sessions in parallel and prove they cannot collide](demo-worktrees-intro.md#step-3-run-two-sessions-in-parallel-and-prove-they-cannot-collide)
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

### Beat 4: A background session isolates itself without being asked (0.5 min)

**Open:** [Step 4: Send a task to the background and watch it isolate itself](demo-worktrees-intro.md#step-4-send-a-task-to-the-background-and-watch-it-isolate-itself) · [`worktree-sandbox/`](worktree-sandbox/)
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

### Beat 5: Review a branch you never check out (1 min)

**Open:** [Step 5: Review a branch without checking it out](demo-worktrees-intro.md#step-5-review-a-branch-without-checking-it-out) · [`worktree-sandbox/`](worktree-sandbox/)
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

### Beat 6: Removal refuses twice, and both refusals are the safety net (1 min)

**Open:** [Step 6: Clean up, and the two errors that block it](demo-worktrees-intro.md#step-6-clean-up-and-the-two-errors-that-block-it) · [`readme.md`](readme.md#cleaning-up)
**Say:** A command refuses, a force flag is offered in the message, and it gets used without anyone reading which refusal it just overrode. Two different conditions block a removal, and only one is about a running process.

```bash
git worktree remove .claude/worktrees/hotfix-greet
git worktree remove .claude/worktrees/feature-auth
```

**Result:** two refusals from two different places, in the order the demo triggers them

```text
fatal: cannot remove a locked working tree, lock reason: claude session hotfix-greet (pid 55268 start 639206594865118980)
use 'remove -f -f' to override or unlock first

...

fatal: '.claude/worktrees/feature-auth' contains modified or untracked files, use --force to delete it
```

**Gotcha:** the first is Claude Code protecting a running session, cleared with `git worktree unlock`; the second is git refusing to discard the untracked `auth.js`.

## If the room asks

| Question | Answer |
|---|---|
| Does a worktree double my disk usage? | No, the `.git` in a worktree is a one-line file pointing at the shared object store, so only the checked-out files are duplicated. |
| My app will not start in the worktree. Why? | Gitignored files such as `.env` are absent from a fresh checkout; list them in a `.worktreeinclude` at the repository root and Claude Code copies them in. |
| Who cleans up the worktrees I forget? | A periodic sweep removes the ones Claude created past `cleanupPeriodDays`, skipping any holding changes or unpushed commits, and never touching yours. |
| How do I show they are really separate? | `git worktree list` in Step 3 prints three entries at commit `4e88f4c`, two of them `locked`, and Step 6 deletes all three branches so nothing is merged. |
