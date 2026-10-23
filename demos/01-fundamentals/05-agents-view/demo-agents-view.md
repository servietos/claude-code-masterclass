# Dispatch and Triage a Fleet of Background Sessions

The agents view is a board for supervising many background sessions at once. You dispatch three independent chores, triage the board, unblock the session that stalls, and review each branch without checking it out.

---

Run every command from the repository root; the sessions work in `demos/01-fundamentals/05-agents-view/agents-sandbox/`, and each result lands on its own `worktree-<name>` branch.

## Step 1: Dispatch the Fleet

A background session returns your terminal immediately and keeps working in its own worktree. Run `claude` once in the sandbox and accept the workspace trust dialog, then dispatch the three chores from the repository root in Bash or PowerShell:

```bash
S=demos/01-fundamentals/05-agents-view/agents-sandbox
claude --bg --name "jsdoc-greet" "Add JSDoc comments to every export in $S/src/greet.js. Commit with the message 'docs: document greet exports'."
claude --bg --name "validate-parse" "Add input validation to parseDuration in $S/src/parse.js so malformed input throws a clear Error. Commit with the message 'fix: validate parseDuration input'."
claude --bg --name "test-format" "Create $S/src/format.test.js with tests covering formatBytes. Commit with the message 'test: cover formatBytes'."
```

```powershell
$S = "demos/01-fundamentals/05-agents-view/agents-sandbox"
claude --bg --name "jsdoc-greet" "Add JSDoc comments to every export in $S/src/greet.js. Commit with the message 'docs: document greet exports'."
claude --bg --name "validate-parse" "Add input validation to parseDuration in $S/src/parse.js so malformed input throws a clear Error. Commit with the message 'fix: validate parseDuration input'."
claude --bg --name "test-format" "Create $S/src/format.test.js with tests covering formatBytes. Commit with the message 'test: cover formatBytes'."
```

Each command returns straight away with a short ID and a reminder card of the commands you might want later:

```text
backgrounded · 7c5dcf5d
  claude agents             list sessions
  claude attach 7c5dcf5d    open in this terminal
  claude logs 7c5dcf5d      show recent output
  claude stop 7c5dcf5d      stop this session
```

Run `git status --short` at the repository root and confirm it prints nothing: none of the three sessions has touched a file in your checkout, and `.claude/worktrees/` is gitignored.

## Step 2: Triage the Board Without Attaching

The board earns its keep when you stop opening sessions to find out what they are doing. Open it with `claude agents` and work it from the keyboard, without attaching to anything:

1. Press `Space` on the top row to open the peek panel and read the session's latest output.
2. Press `↓` and `↑` to peek the neighbouring sessions.
3. If a session sits in Needs input, answer it from the peek panel: type a reply and press `Enter`, or press the number key matching a choice it offered.
4. Press `Ctrl+S` to regroup by directory, then `Ctrl+S` again to return to grouping by state.
5. Press `Esc` to close the panel.

Expected Outcome: all three sessions reach Ready for review or Completed without you attaching to any of them. A session that stalls in Needs input is almost always a permission prompt, and answering it from the peek panel is the whole skill this step teaches. For a scriptable view of the same state, `claude agents --json` returns:

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

## Step 3: Review Three Branches Without Checking Any Out

Each session committed to its own branch, so reviewing them means reading three diffs from where you are standing, with your checkout still on master.

```bash
git branch --list "worktree-*"
git diff --stat master..worktree-validate-parse
```

Expected Outcome: three branches listed, each carrying exactly one commit, and a diff that touches exactly one file. Read the validation change closely: it is the one chore of the three whose implementation is a judgement call, and the one most likely to have solved a slightly different problem than you asked for.

Repeat the `git diff --stat` against the other two branches; if any of them touches a file another branch also touched, the chores were never independent, which is worth knowing before merge time. Reading a whole file straight out of a branch with `git show` is [04: Git Worktrees](../04-git-worktrees/demo-worktrees-intro.md#step-3-review-a-branch-without-checking-it-out) Step 3, and works here unchanged.
