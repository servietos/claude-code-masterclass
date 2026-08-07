---
presents: demo-agents-view.md
budget: 4 min
beats: 5
---

# Present: Dispatch and Triage a Fleet of Background Sessions

Five beats dispatch three background sessions, triage the board they land on, and clear it without losing work. The room walks away knowing what makes work safe to split, how to clear a board without attaching, and which delete path destroys uncommitted work.

------

**Shell:** beats quote Bash; in PowerShell the Beat 2 path variable is `$S = "demos/01-fundamentals/09-agents-view/agents-sandbox"`. A bare `S=...` assignment is a PowerShell parse error, and the demo guide carries both fences in full. No solution folder ships: the output lives on three branches and in the per-session worktrees, never in the checkout.

## Beats

### Beat 1: Independence is about blast radius, not about file names (1 min)

**Open:** [`agents-sandbox/src/parse.js`](agents-sandbox/src/parse.js) · [`agents-sandbox/src/format.js`](agents-sandbox/src/format.js)
**Say:** Fanning out only pays when the work is genuinely separable, and separability is about what a change affects, not where it is written. Collisions surface at merge time, the most expensive place to find them.

```text
Read every file under src/ in this repository.

I want to run several Claude sessions in parallel on this codebase. Tell me
which chores here are genuinely independent and which would collide, and say
what "collide" means concretely in each case: same file, same function, or a
shared contract one change would break for the other.

Then tell me which chores are not worth a separate session at all. Do not
change any files yet.
```

**Result:** nothing changes on disk; the plan comes back as Beat 2's three commands, one file each and each ending in a commit.

**Gotcha:** push back on any answer that only counts files: a `parse.js` validation change can break the contract `format.js` relies on.

### Beat 2: Dispatch is three commands, and each prompt must end in a commit (1 min)

**Open:** [Step 2: Dispatch the Fleet](demo-agents-view.md#step-2-dispatch-the-fleet) · [`agents-sandbox/src/`](agents-sandbox/src/)
**Say:** A dispatch prompt is the entire brief a session will ever get, so it carries the scope and the finish line together. Work left uncommitted inside an isolated worktree survives only by luck.

```bash
S=demos/01-fundamentals/09-agents-view/agents-sandbox
claude --bg --name "jsdoc-greet" "Add JSDoc comments to every export in $S/src/greet.js. Commit with the message 'docs: document greet exports'."
claude --bg --name "validate-parse" "Add input validation to parseDuration in $S/src/parse.js so malformed input throws a clear Error. Commit with the message 'fix: validate parseDuration input'."
claude --bg --name "test-format" "Create $S/src/format.test.js with tests covering formatBytes. Commit with the message 'test: cover formatBytes'."
```

**Result:** three short IDs within a second or two, each with a reminder card, and `src/format.test.js` written by the third session on `worktree-test-format` only

```text
backgrounded · 7c5dcf5d
  claude agents             list sessions
  claude attach 7c5dcf5d    open in this terminal
  claude logs 7c5dcf5d      show recent output
  claude stop 7c5dcf5d      stop this session
```

**Gotcha:** each command names exactly one file, and each carries `--name`, because the default label is the whole prompt.

### Beat 3: Triage from the board, and answer Needs input first (1 min)

**Open:** [`readme.md`](readme.md#read-the-board) · [Step 3: Triage the Board Without Attaching](demo-agents-view.md#step-3-triage-the-board-without-attaching)
**Say:** Supervising several sessions turns the question from what to type next into which row deserves attention. A blocked session burns wall-clock time doing nothing while the others finish.

```bash
claude agents --json
```

**Result:** nothing lands in the checkout while the board fills, and `git status --short` at the repository root prints nothing

```json
{
  "id": "7c5dcf5d",
  "kind": "background",
  "name": "jsdoc-greet",
  "status": "busy",
  "state": "working"
}
```

**Gotcha:** `Space` peeks at a row and answers it without losing your place; a session stuck on Needs input is usually a permission prompt.

### Beat 4: Review three branches without checking one out (0.5 min)

**Open:** [Step 4: Review Three Branches Without Checking Any Out](demo-agents-view.md#step-4-review-three-branches-without-checking-any-out) · [`agents-sandbox/src/parse.js`](agents-sandbox/src/parse.js) · `parseDuration`, the unguarded `match`
**Say:** The diff here is the test of Beat 1's independence claim, so what matters is that no two branches touch one file. Reading a whole file out of a branch with `git show` is [08: Git Worktrees](../08-git-worktrees/demo-worktrees-intro.md#step-5-review-a-branch-without-checking-it-out) Step 5.

```bash
git branch --list "worktree-*"
git diff --stat master..worktree-validate-parse
```

**Result:** three branches with one commit each, `worktree-jsdoc-greet`, `worktree-validate-parse` and `worktree-test-format`, none of them touching a file another one touched

```diff
 agents-sandbox/src/
   format.js
   greet.js
   parse.js
+  format.test.js   on worktree-test-format only
```

**Gotcha:** read the `parse.js` diff most closely: it is the only chore of the three that is a judgement call.

### Beat 5: Two ways to delete, one of which loses work (0.5 min)

**Open:** [Step 5: Clear the Board Without Losing Work](demo-agents-view.md#step-5-clear-the-board-without-losing-work) · [`readme.md`](readme.md#how-file-edits-stay-isolated)
**Say:** Clearing the board is a destructive operation wearing the clothes of a tidy-up, and the two obvious ways do not behave the same. Which one you reach for decides whether uncommitted work in the worktree survives.

```bash
claude stop <id>
claude rm <id>
```

**Result:** an empty board; the worktrees and branches that outlive it go with the git cleanup in [08: Git Worktrees](../08-git-worktrees/demo-worktrees-intro.md#step-6-clean-up-and-the-two-errors-that-block-it) Step 6.

**Gotcha:** `Ctrl+X` twice removes the session's worktree along with any uncommitted changes in it, while `claude rm` refuses in exactly that situation.

## If the room asks

| Question | Answer |
|---|---|
| What happens to a session if I close the terminal? | Nothing, a separate per-user supervisor owns background sessions; they survive the terminal and machine sleep, but not a shutdown. |
| Why is my session idle and gone an hour later? | Unpinned idle sessions stop after roughly an hour; `Ctrl+T` pins one so it stays running. |
| Is fanning out cheap? | Ten parallel sessions cost roughly ten times the quota of one, arriving as mid-afternoon rate limiting rather than an error at dispatch. |
| Can I turn the isolation off? | Yes, with `worktree.bgIsolation`; Claude also skips the worktree when the directory is not a git repository. |
