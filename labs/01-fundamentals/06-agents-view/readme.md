# Supervise Three Background Sessions and Merge Only the Branches That Pass Review

Three chores that touch different files do not need three terminals you babysit one after another. You will dispatch them with `--bg`, read the Agents View board to see which session needs you, answer a stalled session from the peek panel without attaching, and review each branch against a written gate. Only the branches that pass the gate get merged.

What you practice here: dispatch background sessions with names, triage by state, answer in place, review a branch from your own checkout, and clean up the worktrees and branches a fleet leaves behind.

Duration: about 75 minutes.

Teaching for this lab lives in [Supervise Background Sessions with the Agents View](../../../demos/01-fundamentals/05-agents-view/readme.md); the board walk-through is [Dispatch and Triage a Fleet of Background Sessions](../../../demos/01-fundamentals/05-agents-view/demo-agents-view.md). The worktree isolation behind each session is covered in [Rewind with Checkpoints and Run Parallel Agents with Git Worktrees](../../../demos/01-fundamentals/04-git-worktrees/readme.md). This lab needs Claude Code v2.1.139 or later.

Each step contains:

- **Goal**: what you are building
- **Prompt**: paste this into Claude Code or the shell
- **Expected result**: what the outcome looks like

You write no new files of your own. The deliverable is the state of the starter repository at the end: a `main` branch carrying two of the three chores, one chore rejected, a green suite, a clean `git status` and no leftover worktrees or branches.

## Where to Open Claude Code

The starter is a small Node module with two source files, 7 passing `node:test` tests and no dependencies. A `.claude/settings.json` already allows `npm test`, `git add`, `git commit`, `git status` and `git diff`, so background sessions do not stall on routine commands. Run this from the repository root.

```bash
cd labs/01-fundamentals/06-agents-view/starter && claude
```

```powershell
cd labs/01-fundamentals/06-agents-view/starter; claude
```

Skip `npm install`; the starter has nothing to install. Accept the trust dialog on the first start: background sessions started later in this folder rely on it. The dialog opens with `No, exit` highlighted, so press `↓` once to reach `Yes, I trust this folder`, then `Enter`. Pressing `Enter` on its own exits Claude Code, and `claude --bg` then stops with `Workspace not trusted`.

---

## Step 1: Turn the Starter Into Its Own Repository

**Goal:** Give the lab a git history of its own, so the three session branches and the merges happen here and leave the course repository alone.

Every background session moves into a git worktree before it edits a file, and a worktree needs commits to branch from. The starter folder sits inside the course repository, so a repository of its own keeps this lab separate. Approve each command when Claude asks.

**Prompt:**

```text
Run these commands one at a time and show me each output:
git init -b main
git add .
git commit -m "Baseline toolbox"
npm test
git status --short
```

Then leave the session:

```text
/exit
```

**Expected result:** `git init` reports an empty repository, the commit lists 8 files, `npm test` ends with `pass 7` and `fail 0`, and `git status --short` prints nothing. If the commit fails with an author identity error, run `git config user.name "Your Name"` and `git config user.email "you@example.com"` in the starter folder and repeat the prompt. The rest of the lab runs from a plain shell in this folder.

---

## Step 2: Dispatch the Three Chores

**Goal:** Start three independent sessions that run without holding your terminal.

`--bg` starts a session and returns at once. `--name` replaces the default label, which is the prompt itself, with a short name you can scan in a list. The three chores touch different files by design: documentation in `src/text.js`, a behaviour change in `src/duration.js`, and a new file `src/csv.js`. Two of them are built to need you:

- The CSV chore tells the session to ask you a question before it writes anything, so it will stall in Needs input.
- The duration chore asks for a change that the existing test `parseDuration reads a bare number as seconds` forbids, and it forbids editing tests. That branch cannot pass review, and you will find out why in Step 6.

Run the three commands in a shell opened in the starter folder.

**Prompt:**

```bash
claude --bg --name "jsdoc-text" "Add a JSDoc comment to every export in src/text.js, describing parameters and return value. Edit only src/text.js. Run npm test, then commit with the message 'docs: document text exports'."
claude --bg --name "unit-required" "In src/duration.js make parseDuration throw an Error for any string that has no unit suffix, so '90' is rejected and '90s' is accepted. Edit only src/duration.js and do not touch the tests. Run npm test, then commit with the message 'fix: require a unit in parseDuration'."
claude --bg --name "csv-export" "Before you write any file, ask me whether the CSV delimiter should be a comma or a semicolon, and wait for my answer. Then create src/csv.js exporting toCsv(rows), which turns an array of objects with the same keys into a header line plus one line per row, and create test/csv.test.js covering it. Run npm test, then commit with the message 'feat: add toCsv'."
```

```powershell
claude --bg --name "jsdoc-text" "Add a JSDoc comment to every export in src/text.js, describing parameters and return value. Edit only src/text.js. Run npm test, then commit with the message 'docs: document text exports'."
claude --bg --name "unit-required" "In src/duration.js make parseDuration throw an Error for any string that has no unit suffix, so '90' is rejected and '90s' is accepted. Edit only src/duration.js and do not touch the tests. Run npm test, then commit with the message 'fix: require a unit in parseDuration'."
claude --bg --name "csv-export" "Before you write any file, ask me whether the CSV delimiter should be a comma or a semicolon, and wait for my answer. Then create src/csv.js exporting toCsv(rows), which turns an array of objects with the same keys into a header line plus one line per row, and create test/csv.test.js covering it. Run npm test, then commit with the message 'feat: add toCsv'."
```

Then confirm your checkout is untouched:

```bash
git status --short
```

**Expected result:** each command returns immediately with `backgrounded` and a short ID, followed by the four lines `claude agents`, `claude attach <id>`, `claude logs <id>` and `claude stop <id>`. `git status --short` prints nothing: the sessions work in `.claude/worktrees/`, which `.gitignore` excludes, and your checkout on `main` has not moved. Each session names its own worktree and branch, so their names can differ from the `--name` labels; Step 6 shows the names to use.

---

## Step 3: Read the Board

**Goal:** Find the session that needs you without opening any session.

The board groups sessions by state and puts the group that needs you at the top. Reading the group is faster than reading output, and it is the habit this lab trains.

**Prompt:**

```bash
claude agents
```

Then work the board from the keyboard:

1. Find the row named `csv-export` and note which group it sits in.
2. Type this in the dispatch input to filter the list, then clear the input again:

```text
s:blocked
```

3. Press `Ctrl+S` to regroup by directory, then `Ctrl+S` again to return to grouping by state.

**Expected result:** three rows named `jsdoc-text`, `unit-required` and `csv-export`. `csv-export` reaches Needs input within a minute or two, because it asked its question and is waiting. The filter `s:blocked` leaves only the sessions waiting on you, which is `csv-export` and possibly `unit-required`. The other rows are in Working or Ready for review.

If every row is already in Ready for review, the CSV session ignored the instruction to ask first; note that and continue, because Step 8 then verifies the delimiter it chose.

---

## Step 4: Answer the Stalled Session in Place

**Goal:** Unblock `csv-export` from the board with a typed reply, without attaching.

Attaching opens the whole session and takes you away from the board. The peek panel shows the latest output and accepts a reply, so you can unblock a session and stay where you are.

1. Select the `csv-export` row and press `Space` to open the peek panel.
2. Read the question it asked.
3. Type this reply and press `Enter`:

```text
Use a semicolon.
```

4. Press `Esc` to close the panel. If the session offered numbered choices, pressing the number of the semicolon choice is an equivalent answer.

If `unit-required` is also in Needs input, peek at it and answer with:

```text
Follow the instruction exactly. Do not edit any test.
```

**Expected result:** after your reply the `csv-export` row leaves Needs input and moves to Working. You never pressed `→` or `Enter` on a row, so no session was attached, and `←` was never needed to detach.

---

## Step 5: Peek at Every Finished Session

**Goal:** Learn what each session did from its output panel before you read any diff.

Wait until no row sits in Working. Move through the list with `↓` and `↑`, pressing `Space` on each row to read its summary.

**Expected result:** all three sessions are in Ready for review or Completed. `jsdoc-text` reports a committed JSDoc change and a green suite. `csv-export` reports its new files, a green suite and the commit `feat: add toCsv`. `unit-required` reports the commit `fix: require a unit in parseDuration` and a failing suite, with a failing count of 1 for the bare-number test, because the change contradicts a test it was not allowed to edit.

A session that quietly edited the test file anyway is handled by the review gate in the next step.

---

## Step 6: Review Each Branch Against the Gate

**Goal:** Decide per branch whether it merges, using a gate written down before you read the code.

A branch passes review when both of these hold:

- Its diff touches only the files its chore named.
- `npm test` is green in its worktree.

Each session commits to its own `worktree-` branch, and its checkout lives under `.claude/worktrees/<folder>/`. The session chooses `<folder>`, so read the names from `git branch --list` and `git worktree list` first. Match each folder to its chore with `git diff --stat main..worktree-<folder>`: the JSDoc chore touches `src/text.js`, the unit chore touches `src/duration.js`, and the CSV chore adds `src/csv.js`. The commands below use the placeholders `<jsdoc>`, `<unit>` and `<csv>` for those three folder names. You review from `main` without checking anything out.

**Prompt:**

```bash
git branch --list "worktree-*"
git diff --stat main..worktree-<jsdoc>
git diff --stat main..worktree-<unit>
git diff --stat main..worktree-<csv>
npm test --prefix .claude/worktrees/<jsdoc>
npm test --prefix .claude/worktrees/<unit>
npm test --prefix .claude/worktrees/<csv>
```

**Expected result:** `git branch --list` lists the three `worktree-` branches. The diffs show one file for the JSDoc branch (`src/text.js`), one for the unit branch (`src/duration.js`) and two for the CSV branch (`src/csv.js` and `test/csv.test.js`). The three test runs end as follows:

| Branch | Diff scope | Suite | Verdict |
|---|---|---|---|
| `worktree-<jsdoc>` | `src/text.js` only | `pass 7`, `fail 0` | Merge |
| `worktree-<csv>` | `src/csv.js` and `test/csv.test.js` | green, with the new CSV tests counted | Merge |
| `worktree-<unit>` | `src/duration.js` only | `fail 1` | Reject |

If `unit-required` touched `test/duration.test.js` to make the suite green, it fails the scope half of the gate and is rejected for that reason. If `.claude/worktrees/<folder>` does not exist for a branch, run `git worktree list` and use the path it prints.

---

## Step 7: Merge Only the Branches That Passed

**Goal:** Land the two passing chores on `main` and leave the rejected one unmerged.

The JSDoc branch merges as a fast-forward because `main` has not moved. The CSV branch then merges as a true merge, because `main` now holds the JSDoc commit. The two touch different files, so no conflict appears. `--no-edit` accepts the default merge message.

**Prompt:**

```bash
git merge worktree-<jsdoc>
git merge --no-edit worktree-<csv>
npm test
git log --oneline --graph
```

**Expected result:** the first merge prints `Fast-forward` and lists `src/text.js`. The second prints `Merge made by the 'ort' strategy` and lists `src/csv.js` and `test/csv.test.js`. `npm test` ends with `fail 0` and a test count above 7. `git log --oneline --graph` shows the baseline commit, `docs: document text exports`, `feat: add toCsv` and a merge commit, and no `fix: require a unit in parseDuration`.

---

## Step 8: Prove the Answer You Gave Reached the Code

**Goal:** Check that your reply in the peek panel shaped the merged result.

The reply you typed in Step 4 was the only decision you made inside a session. The delimiter in the merged file is the receipt for it.

**Prompt:**

```bash
grep -n '";"' src/csv.js
git log --oneline -- src/duration.js
```

```powershell
Select-String -Path src/csv.js -Pattern '";"'
git log --oneline -- src/duration.js
```

**Expected result:** the first command prints at least one line of `src/csv.js` that contains `";"`, such as the delimiter definition `const DELIMITER = ";";`; if your session used single quotes, search for the semicolon character instead. The second command prints only the baseline commit, because the rejected change to `src/duration.js` is not merged and the file still accepts a bare number.

---

## Step 9: Clean Up the Fleet

**Goal:** Stop the sessions, remove their worktrees and branches, and leave `main` as the only branch.

Stopping a session leaves its worktree in place. Removing a worktree leaves its branch behind. Branch deletion with `-d` succeeds only for merged branches, which doubles as a check that nothing you merged is lost, and `-D` is the deliberate discard for the rejected one.

**Prompt:**

```bash
claude agents --json
```

Stop each session with the ID that listing printed:

```bash
claude stop <id>
```

Then remove the worktrees and branches:

```bash
git worktree list
git worktree remove .claude/worktrees/<jsdoc>
git worktree remove .claude/worktrees/<csv>
git worktree remove --force .claude/worktrees/<unit>
git branch -d worktree-<jsdoc> worktree-<csv>
git branch -D worktree-<unit>
```

Finish with the full check:

```bash
git worktree list
git branch
git status --short
npm test
```

**Expected result:** `git worktree list` prints one line, the starter folder on `[main]`. `git branch` prints only `* main`. `git status --short` prints nothing and `npm test` is green. `--force` is needed for `unit-required` only when its worktree still holds uncommitted changes; you are discarding that branch on purpose, so it is the right flag there and nowhere else.

If `claude agents` still lists the three rows after `claude stop`, press `Ctrl+X` on each row once to stop it; a second press deletes the session record.

---

## Troubleshooting

| Symptom | Cause | Fix |
|---|---|---|
| A session sits in Needs input on a `git` or `npm` command | The command is outside the allow list in `.claude/settings.json` | Peek at it, read the command, and approve it from the panel |
| `claude --bg` reports it cannot start the session | Claude Code is older than v2.1.139 or the background feature is disabled | Run `claude --version`, and check that `disableAgentView` is not `true` in your settings |
| No `worktree-` branches exist after Step 2 | The sessions started before Step 1 finished, so the folder had no commits, or the folder is not a git repository | Run `git log --oneline` in the starter folder and expect `Baseline toolbox` |
| A branch is named differently from the `--name` label | The session chooses its own worktree and branch name, and `--name` does not set it | Run `git branch --list "worktree-*"` and use the names it prints |
| `git worktree remove` says the working tree is locked | The session in that worktree is still alive, or it stopped and left its lock behind | Stop it with `claude stop <id>` and repeat; if the lock stays, run `git worktree unlock .claude/worktrees/<folder>` and repeat |
| `git branch -d` says a branch is not fully merged | The branch was never merged, or a session committed after the merge | Run `git log main..<branch>`; merge again, or use `-D` for a branch you rejected |
| `npm test --prefix` finds no tests | The path to the worktree is wrong | Copy the path from `git worktree list` |
