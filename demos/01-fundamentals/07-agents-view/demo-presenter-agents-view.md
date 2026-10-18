---
presents: demo-agents-view.md
budget: 4 min
beats: 3
---

# Present: Dispatch and Triage a Fleet of Background Sessions

Three beats dispatch three background sessions, triage the board they land on, and review each branch without checking it out. The room walks away knowing how to clear a board without attaching.

------

**Shell:** beats quote Bash; in PowerShell the Beat 1 path variable is `$S = "demos/01-fundamentals/07-agents-view/agents-sandbox"`. A bare `S=...` assignment is a PowerShell parse error, and the demo guide carries both fences in full. No solution folder ships: the output lives on three branches and in the per-session worktrees, never in the checkout.

## Beats

### Beat 1: Dispatch is three commands, and each prompt must end in a commit (1 min)

**Open:** [Step 1: Dispatch the Fleet](demo-agents-view.md#step-1-dispatch-the-fleet) · [`agents-sandbox/src/`](agents-sandbox/src)
**Say:** A dispatch prompt is the entire brief a session will ever get, so it carries the scope and the finish line together. Work left uncommitted inside an isolated worktree survives only by luck.

```bash
S=demos/01-fundamentals/07-agents-view/agents-sandbox
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

### Beat 2: Triage from the board, and answer Needs input first (2 min)

**Open:** [`readme.md`](readme.md#read-the-board) · [Step 2: Triage the Board Without Attaching](demo-agents-view.md#step-2-triage-the-board-without-attaching)
**Say:** Supervising several sessions turns the question from what to type next into which row deserves attention. A blocked session burns wall-clock time doing nothing while the others finish.

```bash
claude agents --json
```

**Result:** nothing lands in the checkout while the board fills, and `git status --short` at the repository root prints nothing

```json
[
  {
    "id": "7c5dcf5d",
    "kind": "background",
    "name": "jsdoc-greet",
    "state": "working"
  }
]
```

**Gotcha:** `Space` peeks at a row and answers it without losing your place; a session stuck on Needs input is usually a permission prompt.

### Beat 3: Review three branches without checking one out (1 min)

**Open:** [Step 3: Review Three Branches Without Checking Any Out](demo-agents-view.md#step-3-review-three-branches-without-checking-any-out) · [`agents-sandbox/src/parse.js`](agents-sandbox/src/parse.js) · `parseDuration`, the unguarded `match`
**Say:** The diff here is the test of Beat 1's independence claim, so what matters is that no two branches touch one file. Reading a whole file out of a branch with `git show` is [06: Git Worktrees](../06-git-worktrees/demo-worktrees-intro.md#step-3-review-a-branch-without-checking-it-out) Step 3.

```bash
git branch --list "worktree-*"
git diff --stat master..worktree-validate-parse
```

**Result:** three branches with one commit each, `worktree-jsdoc-greet`, `worktree-validate-parse` and `worktree-test-format`, none of them touching a file another one touched

```text
 agents-sandbox/src/
   format.js
   greet.js
   parse.js
+  format.test.js   on worktree-test-format only
```

**Gotcha:** read the `parse.js` diff most closely: it is the only chore of the three that is a judgement call.

## If the room asks

| Question | Answer |
|---|---|
| What happens to a session if I close the terminal? | Nothing, a separate per-user supervisor owns background sessions; they survive the terminal and machine sleep, but not a shutdown. |
| Why is my session idle and gone an hour later? | Unpinned idle sessions stop after roughly an hour; `Ctrl+T` pins one so it stays running. |
| Can I turn the isolation off? | Yes, with `worktree.bgIsolation`; Claude also skips the worktree when the directory is not a git repository. |
