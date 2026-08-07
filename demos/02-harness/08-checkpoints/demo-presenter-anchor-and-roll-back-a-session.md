---
presents: demo-anchor-and-roll-back-a-session.md
budget: 6 min
beats: 6
---

# Present: Anchor a Checkpoint and Roll Back a Runaway Refactor

A green suite anchored, a refactor let loose on it, then a rewind to the anchor in front of the room. A room walks away knowing what a restore covers, why the menu beats asking Claude to undo its own work, and which two commands prove it landed.

------

## Beats

### Beat 1: the boundary is narrower than everyone assumes (1 min)

**Open:** [Step 2: Learn What a Checkpoint Actually Covers](demo-anchor-and-roll-back-a-session.md#step-2-learn-what-a-checkpoint-actually-covers) · the four questions in the Research prompt · [`readme.md`](readme.md#how-checkpoints-work)
**Say:** A restore is drawn around one channel: changes made through Claude's own file editing tools. Everything else that moved while you worked sits outside it.

```text
1. When is a checkpoint created?
2. How do I open the rewind menu, by keystroke and by command?
3. Which of these are covered by a restore: edits made with Claude's file editing tools, files
   changed by a bash command Claude ran, files I edited by hand in my editor, database rows,
   git history?
4. What are the restore options in the menu and how do they differ?

Answer from the docs, not from memory, and quote the exact command name.
```

**Result:** the answer became the closing section of [`checkpoint-drill-solution/rollback-playbook.md`](checkpoint-drill-solution/rollback-playbook.md), the one file the drill adds

```markdown
A restore reverts only the files Claude edited through its file editing tools in this session. Files changed by a bash command Claude ran, your own manual editor changes, database rows, and git history are all outside the boundary.
```

**Gotcha:** "Answer from the docs, not from memory" is in the prompt for a reason: if Claude offers an `/undo` command, that is not in the current documentation.

### Beat 2: the rewind menu is driven by you, not by Claude (1 min)

**Open:** [Step 4: Rewind to the Anchor](demo-anchor-and-roll-back-a-session.md#step-4-rewind-to-the-anchor) · the Recipe keystroke sequence · [`readme.md`](readme.md#noticing-a-checkpoint-and-rolling-back)
**Say:** Recovery here is a mechanic you operate, which is why this part of the drill has no prompt to paste. Interrupting a run and undoing what it wrote are two independent decisions.

```text
1. Press `Esc` twice with an empty prompt input, or type `/rewind`.
2. In the menu, select the prompt from Step 1 (the baseline and anchor turn).
3. Choose **Restore code** to revert the files while keeping the conversation.
```

**Result:** the State Note in [`checkpoint-drill-solution/readme.md`](checkpoint-drill-solution/readme.md) records what the run did

```text
The rollback restored the original `roundCents` implementation, and the suite is back at 15 passing.
```

**Gotcha:** what appears in the menu is your own prompt list and is session-dependent, so verify with a command instead of by reading the screen.

### Beat 3: a stored snapshot is byte-identical, a model-written revert is a reconstruction (1 min)

**Open:** [Step 4: Rewind to the Anchor](demo-anchor-and-roll-back-a-session.md#step-4-rewind-to-the-anchor) · the Research prompt comparing recovery routes · [`checkpoint-drill/src`](checkpoint-drill/src) · the four files the refactor rewrote
**Say:** One route replays bytes stored at the time; the other asks a model to write the old code again from what it can still see. The second degrades exactly when it is needed most.

```text
I want to discard the refactor you just made and get back to the state before my refactor prompt.

Compare two recovery routes for me: asking you to revert the edits by writing the old code back,
versus using the rewind menu to restore the code. Which one guarantees byte-identical files, and
which one can drift? Answer in four sentences.
```

**Result:** an absence, so there is nothing to open: four files were rewritten and restored, and the entire starter-to-solution difference is this

```text
Only in checkpoint-drill-solution: .gitignore
Only in checkpoint-drill-solution: package-lock.json
Files checkpoint-drill/readme.md and checkpoint-drill-solution/readme.md differ
Only in checkpoint-drill-solution: rollback-playbook.md
```

**Gotcha:** `src/` and `test/` do not appear in that listing at all, and if anyone calls the two routes equivalent, ask what happens once the session has been compacted.

### Beat 4: the honest part, the refactor may well stay green (1 min)

**Open:** [`checkpoint-drill/src/money.js`](checkpoint-drill/src/money.js) · `roundCents` and `multiply` · [`checkpoint-drill/test/money.test.js`](checkpoint-drill/test/money.test.js)
**Say:** A green suite says the assertions someone once thought to write still hold, which is far weaker than the change being correct. The risk this drill answers is an unreviewed multi-file diff, not a broken build.

```javascript
export function roundCents(amount) {
  return Math.round((amount + Number.EPSILON) * 100) / 100;
}

export function multiply(amount, factor) {
  return roundCents(amount * factor);
}
```

**Result:** the recorded run went red, and nothing of it survives: [`checkpoint-drill-solution/src/money.js`](checkpoint-drill-solution/src/money.js) is byte-identical to the starter's

```text
the rounding strategy was swapped from half-up to truncation, which turned 4 of the 15 tests red across `test/money.test.js` and `test/pricing.test.js`
```

**Gotcha:** a textbook half-even implementation would instead keep all 15 green, because `roundCents(2.375)` rounds `237.5` to the even `238` and still yields `2.38`.

### Beat 5: two independent checks, because each one misses what the other catches (1 min)

**Open:** [Step 5: Prove the Rollback with the Suite and the Diff](demo-anchor-and-roll-back-a-session.md#step-5-prove-the-rollback-with-the-suite-and-the-diff) · the verification Recipe · [`checkpoint-drill/readme.md`](checkpoint-drill/readme.md) · its closing line
**Say:** Behaviour and file state are genuinely independent: a suite can pass with a stray file left behind, and a clean tree says nothing about behaviour. Neither alone supports "the folder is back where it started".

```text
Verify the rollback of demos/02-harness/08-checkpoints/checkpoint-drill:

1. Run npm test in that folder and report pass and fail counts and the exit code.
2. Run git status --short for that folder only and report every line.
3. Print the first 10 lines of src/money.js.

Then state in one sentence whether the folder is back at the baseline, and if not, name exactly
which file still differs.
```

**Result:** [`checkpoint-drill-solution/readme.md`](checkpoint-drill-solution/readme.md) turned the starter's closing instruction into a number the check can be graded against

```diff
-The suite must be green before you start the drill. Follow [../demo-anchor-and-roll-back-a-session.md](../demo-anchor-and-roll-back-a-session.md).
+Expected: `pass 15`, `fail 0`, exit code 0.
```

**Gotcha:** `npm install` here drops a `package-lock.json` into a folder that must stay pristine, which is what the starter's Setup warns about and what step 2 reports.

### Beat 6: the decision rule is the thing worth taking home (1 min)

**Open:** [`readme.md`](readme.md#when-to-request-an-explicit-checkpoint) · [`checkpoint-drill-solution`](checkpoint-drill-solution)
**Say:** The point is knowing which of two tools a piece of work needs before starting it. The question that separates them is whether the work has to survive something: a restart, another machine, a review.

```markdown
| Situation | Anchor | Commit | Why |
|-----------|--------|--------|-----|
| A risky refactor I might abandon in the next ten minutes | Yes | No | Pure checkpoint case: the work never has to outlive the session, and `/rewind` restores byte-identical files. |
| A working feature I want to keep across a machine restart | No | Yes | Checkpoints are session state and expire with the session, so only a commit carries the work forward. |
| A migration script that writes to a database | Yes | Yes | The checkpoint covers the script file, but nothing rolls back the rows, so the commit is the only durable record of what ran. |
| A change made partly by Claude and partly by me editing files by hand | No | Yes | Manual edits are outside the checkpoint boundary, so a restore would leave a half-reverted tree. |
```

**Result:** that table opens [`checkpoint-drill-solution/rollback-playbook.md`](checkpoint-drill-solution/rollback-playbook.md), which exists only in the solution folder

**Gotcha:** the database row is the sharpest case: the checkpoint restores the migration script and leaves the rows it wrote exactly where they are.

## If the room asks

| Question | Answer |
|---|---|
| Is a checkpoint a git commit? | No, it is session-local undo for files Claude edited with its own tools, it expires with the session, and a restore never touches git history. |
| How far back can I go? | The session keeps the 100 most recent checkpoints, so any earlier prompt in the timeline is reachable, not only the last turn. |
| Why anchor explicitly if checkpoints are automatic? | To get a point you can recognise in the menu: the anchor turn states the file list and the test result. |
