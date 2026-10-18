# Recover From a Runaway Edit and Run Two Sessions in Parallel

Claude can change a dozen files in one turn, and by the time you read the diff the wrong design is already everywhere. A second problem shows up when you want two jobs done at once: two sessions editing one checkout overwrite each other. You will rewind an over-reaching refactor and prove the recovery with a green test run and a clean `git status`, then run two sessions in separate git worktrees that edit the same file, review both branches, merge them and remove them.

What you practice here: anchor a known-good state, undo a whole turn with `/rewind`, learn what a checkpoint cannot undo, and give each session its own worktree and branch so parallel work meets only at a merge you control.

Duration: about 80 minutes.

Teaching for this lab lives in [Rewind with Checkpoints and Run Parallel Agents with Git Worktrees](../../../demos/01-fundamentals/06-git-worktrees/readme.md); the rollback walk-through is [Anchor a Checkpoint and Roll Back a Runaway Refactor](../../../demos/01-fundamentals/06-git-worktrees/demo-anchor-and-roll-back-a-session.md) and the parallel sessions are shown in [Run Two Claude Sessions Without Them Colliding](../../../demos/01-fundamentals/06-git-worktrees/demo-worktrees-intro.md).

Each step contains:

- **Goal**: what you are building
- **Prompt**: paste this into Claude Code
- **Expected result**: what the outcome looks like

You write no new files of your own. The deliverable is the state of the starter repository at the end: a `main` branch carrying both parallel features, a green suite, a clean `git status`, one worktree and no leftover branches.

## Where to Open Claude Code

The starter is a small Node module that prices an order and renders a plain-text receipt, with 10 passing `node:test` tests and no dependencies. Open Claude Code inside the starter folder. Run this from the repo root.

```bash
cd labs/01-fundamentals/05-checkpoints-and-worktrees/starter && claude
```

```powershell
cd labs/01-fundamentals/05-checkpoints-and-worktrees/starter; claude
```

Skip `npm install`; the starter has nothing to install. Accept the trust dialog on the first start. This first terminal is your main session and stays open for the whole lab. Step 7 opens two more terminals, and each of them starts in the same folder.

---

## Step 1: Turn the Starter Into Its Own Repository

**Goal:** Give the lab a git history of its own, so branches and merges happen here and leave the course repository alone.

A worktree is a second checkout of one repository, so it needs commits to branch from. The starter folder sits inside the course repository, and a repository of its own keeps every branch and merge in this lab separate from it. Approve each command when Claude asks.

**Prompt:**

```text
Run these commands one at a time and show me each output:
git init -b main
git add .
git commit -m "Baseline receipt shop"
npm test
git status --short
```

**Expected result:** `git init` reports an empty repository, the commit lists 11 files, `npm test` ends with `pass 10` and `fail 0`, and `git status --short` prints nothing. If the commit fails with an author identity error, run `git config user.name "Your Name"` and `git config user.email "you@example.com"` in the starter folder and repeat the prompt. This clean, green state is the point the rest of the lab returns to.

---

## Step 2: Anchor the Green State

**Goal:** Create a labelled point in the session you can find again in the rewind menu.

Claude Code snapshots the files it edits before every prompt you send. A turn that changes nothing still creates a restore point, so a plain prompt that describes the state is enough to anchor it.

**Prompt:**

```text
Run npm test and report the pass and fail counts. Then anchor this state: I want to be able to return to exactly this point later. Say in one sentence what the current state is (the list of files in src and test, plus the test result) so I can recognise it in the rewind menu. Do not change any file.
```

Open the rewind menu and look, then leave it without choosing anything:

```text
/rewind
```

Press `Esc` to close the menu.

**Expected result:** Claude reports `pass 10` and `fail 0` and describes the files in one sentence. The `/rewind` menu lists your prompts from this session, newest at the bottom, and the prompt above is one of them. Closing the menu with `Esc` changes nothing.

---

## Step 3: Let a Refactor Run Too Far

**Goal:** Produce the damage you will undo: a multi-file change you did not review, with a failing suite.

This prompt is deliberately over-reaching. It touches every layer at once, forbids Claude from updating the tests, and asks for no verification, which is how a runaway turn looks in real work.

**Prompt:**

```text
Change how money is stored in this project from euros with two decimals to integer cents. Apply it everywhere: the item prices in src/items.js, lineTotal and orderTotal in src/totals.js, the order lines in src/order.js and the formatting in src/receipt.js. Do not update the tests and do not run them. Edit the source files only, then list every file you changed.
```

Then check the result:

```text
Run exactly: npm test
```

**Expected result:** Claude lists the four source files, and `npm test` now ends with a failing count above zero, for example `pass 3` and `fail 7`, because `findItem("mug")` returns a price of `800` while the tests still expect `8`. Your working tree holds changes you never asked to keep. You decide here that the approach is wrong, which is the moment `/rewind` exists for.

---

## Step 4: Make a Change a Checkpoint Cannot See

**Goal:** Learn the boundary of the rewind by creating a file through a shell command.

A checkpoint tracks the files Claude edits with its own file tools. Output redirected by a shell command is invisible to it. Write the damage report to a file the shell way and see how git shows both kinds of change.

**Prompt:**

```text
Run exactly: git diff --stat > CHANGES.txt
```

```text
Run exactly: git status --short
```

**Expected result:** `git status --short` prints four lines starting with ` M` for the files in `src/` and one line `?? CHANGES.txt`. The `src/` files are edits made through Claude's file tools; `CHANGES.txt` came from a shell redirect. Keep both in mind for the next step.

---

## Step 5: Rewind and Prove the Recovery

**Goal:** Restore the code to the anchor and show with two independent checks that you landed there.

A restore replays a stored snapshot, so the files come back byte for byte. A model-written revert rebuilds code from memory and can drift. You drive the menu yourself, so this step is a keystroke sequence followed by a verification prompt.

1. Press `Esc` twice on an empty prompt, or type `/rewind`.
2. Select the prompt from Step 2, the one that starts with `Run npm test and report the pass and fail counts`.
3. Choose **Restore code** so the conversation stays intact.

Then verify the result with the suite and with git:

**Prompt:**

```text
Verify the rollback. Run exactly: npm test
Then run exactly: git status --short
Then run exactly: git diff --stat
Report every output line.
```

**Expected result:** `npm test` is green again with `pass 10` and `fail 0`. `git diff --stat` prints nothing, so no tracked file differs from the baseline commit. `git status --short` prints one line, `?? CHANGES.txt`: the rewind restored everything Claude edited and left the shell-created file in place. Remove it and confirm a fully clean tree.

```text
Run exactly: rm CHANGES.txt
```

```text
Run exactly: git status --short
```

The second command now prints nothing, which together with the green suite is your receipt for the recovery.

---

## Step 6: Prepare the Repository for Worktrees

**Goal:** Keep worktree directories out of `git status` before you create any.

Claude Code places each worktree under `.claude/worktrees/<name>/` inside the repository. Without an ignore line, every worktree appears as untracked noise in the main checkout and in the clean-status checks that follow. The ignore line is a commit, so every worktree you create later inherits it.

**Prompt:**

```text
Add the line .claude/worktrees/ to .gitignore, then run exactly: git add .gitignore
Then run exactly: git commit -m "Ignore worktree folders"
Then run exactly: git worktree list
```

**Expected result:** the commit lists one changed file and `git worktree list` prints one line, the starter folder on branch `[main]`. `git status --short` is still empty.

---

## Step 7: Run Two Sessions on the Same File

**Goal:** Edit `src/receipt.js` in two sessions at the same time and see that neither one disturbs the other.

Open two new terminals, both in the starter folder. Pass `--worktree` with a name and Claude Code creates `.claude/worktrees/<name>/` on a new branch called `worktree-<name>`, then starts the session there. Both tasks change the total line of the receipt on purpose, so the merge in Step 9 has something to resolve.

Terminal 2:

```bash
cd labs/01-fundamentals/05-checkpoints-and-worktrees/starter && claude --worktree add-currency
```

```powershell
cd labs/01-fundamentals/05-checkpoints-and-worktrees/starter; claude --worktree add-currency
```

Terminal 3:

```bash
cd labs/01-fundamentals/05-checkpoints-and-worktrees/starter && claude --worktree add-footer
```

```powershell
cd labs/01-fundamentals/05-checkpoints-and-worktrees/starter; claude --worktree add-footer
```

Send each session its own prompt, and send them close together so both are running at once. Terminal 2:

**Prompt:**

```text
In src/receipt.js, append " EUR" to the amount in every row and to the amount on the total line. Run npm test, then commit with the message "feat: print EUR on every amount".
```

Terminal 3:

```text
In src/receipt.js, change the label on the total line from "Total" to "TOTAL DUE" and add a final line "Thank you for your order" after it. Run npm test, then commit with the message "feat: add total label and footer".
```

Back in terminal 1, the main session, check that your checkout never moved:

```text
Run exactly: git status --short
Then run exactly: git worktree list
Then run exactly: git branch
```

**Expected result:** each worktree session reports a green suite and a commit. In terminal 1, `git status --short` prints nothing and `src/receipt.js` still holds the original receipt. `git worktree list` shows three lines: the starter folder on `[main]`, `.claude/worktrees/add-currency` on `[worktree-add-currency]` and `.claude/worktrees/add-footer` on `[worktree-add-footer]`, with the two worktree lines marked `locked` while their sessions are alive. `git branch` lists `main` and both `worktree-` branches.

---

## Step 8: Review Both Branches Without Checking Them Out

**Goal:** Read each session's work from where you stand and find the line where the two collide.

Reviewing a branch is ordinary git: `git diff` between two branches and `git show <branch>:<path>` work from your checkout, even while the branch is checked out in another worktree.

**Prompt:**

```text
Run exactly: git diff main..worktree-add-currency
Then run exactly: git diff main..worktree-add-footer
Then answer in three sentences: what does each branch change in src/receipt.js, which line of that file do both branches change, and what will git do when I merge the second one?
```

**Expected result:** the first diff shows the row line and the `const total` line gaining ` EUR`. The second diff shows the `const total` line renamed to `TOTAL DUE` and a footer added to the returned array. Claude names the `const total` line as the shared one and predicts a merge conflict in `src/receipt.js` on the second merge. If Claude predicts no conflict, ask it to compare the two versions of that single line.

---

## Step 9: Merge Both Branches and Resolve the Conflict

**Goal:** Land both features on `main` with a green suite.

The first merge applies cleanly because `main` has not moved since the branches were created. The second one stops on the line both sessions changed, and the conflict is yours to resolve with both intentions kept.

**Prompt:**

```text
Run exactly: git merge worktree-add-currency
Then run exactly: git merge worktree-add-footer
Report the output of both.
```

**Expected result:** the first merge fast-forwards and the second prints `CONFLICT (content): Merge conflict in src/receipt.js` followed by `Automatic merge failed; fix conflicts and then commit the result.` `git status --short` shows `UU src/receipt.js`. Now resolve it.

```text
Open src/receipt.js and resolve the merge conflict so the file keeps both changes: the label TOTAL DUE, the EUR suffix on the amount, and the footer line "Thank you for your order". Remove every conflict marker. Then run npm test, run exactly: git add src/receipt.js and commit with the message "Merge parallel receipt features".
```

Prove the result:

```text
Run exactly: grep -c "<<<<<<<" src/receipt.js
Then run exactly: cat src/receipt.js
Then run exactly: git log --oneline --graph
```

**Expected result:** `grep -c` prints `0`. `src/receipt.js` shows the `EUR` suffix in the row template, a total line built as `TOTAL DUE` plus the amount plus ` EUR`, and `Thank you for your order` as the last element of the returned array. `git log --oneline --graph` shows a merge commit with both feature commits beneath it. The `npm test` run from the resolution prompt ended with `pass 10` and `fail 0`.

---

## Step 10: Remove the Worktrees and the Branches

**Goal:** Leave one worktree and one branch, and prove it.

A worktree that a live session uses is locked, so close the two sessions first. Removing a worktree leaves its branch behind, so a full cleanup is two commands per session. Branch deletion with `-d` succeeds only for merged branches, which doubles as a check that nothing was lost.

In terminals 2 and 3, type:

```text
/exit
```

If Claude Code asks whether to keep or remove the worktree on exit, either answer is fine. Then, in terminal 1:

**Prompt:**

```text
Run exactly: git worktree list
Then, for each worktree under .claude/worktrees that is still listed, run exactly: git worktree remove <path>
Then run exactly: git branch -d worktree-add-currency worktree-add-footer
```

Finish with the full check:

```text
Run exactly: git worktree list
Then run exactly: git branch
Then run exactly: git status --short
Then run exactly: npm test
```

**Expected result:** `git worktree list` prints one line, the starter folder on `[main]`. `git branch` prints only `* main`. `git status --short` prints nothing and `npm test` ends with `pass 10` and `fail 0`. If `git worktree remove` reports that the worktree is locked, the session in that terminal is still open; exit it and repeat. If it refuses because of modified files, a session left uncommitted work behind: review it with `git -C <path> status`, because `--force` discards it.

---

## Troubleshooting

| Symptom | Cause | Fix |
|---|---|---|
| `CHANGES.txt` is still there after the rewind | A shell redirect is outside what checkpoints track | Remove it with `rm CHANGES.txt`, as Step 5 does |
| `claude --worktree` reports it is not in a git repository | Step 1 was skipped, or the terminal is outside the starter folder | Run `git rev-parse --show-toplevel` in the starter folder and expect a path ending in `starter` |
| The second merge succeeds without a conflict | One session edited a different part of the file than the prompt named | Check `git diff main..worktree-add-footer` for the `const total` line; when only one session changed it, the merge is already clean and the resolution prompt can be skipped |
| `git branch -d` says a branch is not fully merged | A session committed after you merged | Run `git log main..worktree-add-footer`, merge again, then delete |
| `git worktree remove` names a lock | The session in that worktree is still alive | Type `/exit` in that terminal and repeat |
| `git worktree remove` still names a lock after the session ended | The session stopped without releasing its lock, so the lock file stays behind | Read the pid in `.git/worktrees/<name>/locked`; when no process has that pid, run `git worktree unlock <path>`, then repeat the removal |
| `npm test` fails after the merge | The resolution dropped part of one change | Ask Claude to compare `src/receipt.js` with both branch versions and restore the missing part |
