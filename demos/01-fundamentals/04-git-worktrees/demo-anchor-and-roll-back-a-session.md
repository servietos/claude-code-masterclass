# Anchor a Checkpoint and Roll Back a Runaway Refactor

Checkpoints let you rewind a session to a known state after Claude takes a change further than you wanted. You anchor a green pricing module, let an over-reaching cross-cutting refactor run until the suite goes red, then rewind to the anchor and prove the rollback landed with the tests and a diff.

---

Work in `demos/01-fundamentals/04-git-worktrees/checkpoint-drill` with a terminal beside Claude Code for `npm test` (skip `npm install`, the folder must stay clean); the finished state sits in [checkpoint-drill-solution/](checkpoint-drill-solution/readme.md).

## Step 1: Establish the Green Baseline and Anchor It

A rollback is only meaningful if you can prove where you landed. Confirm the green suite, then anchor the session state with an explicit prompt before anything is touched.

```text
Run npm test in demos/01-fundamentals/04-git-worktrees/checkpoint-drill and report the pass and fail
counts and the exit code.

Then anchor this state: I want to be able to return to exactly this point later. Confirm in one
sentence what the current state is (file list plus test result) so I can recognise it in the
rewind menu.

Do not change any file.
```

Expected Outcome: the terminal reports a fully green suite, and Claude's turn is now a labelled point in the session you can find again.

```text
ℹ pass 15
ℹ fail 0
```

## Step 2: Trigger the Runaway Refactor

This is the deliberate mistake: a cross-cutting change that touches every layer at once, which is painful to unwind by hand and cheap to unwind with a checkpoint.

```text
Change the rounding strategy of demos/01-fundamentals/04-git-worktrees/checkpoint-drill from half-up to
banker's rounding (round half to even). Apply it consistently: replace the implementation in
src/money.js and thread an explicit rounding-mode parameter through src/discount.js, src/tax.js
and src/pricing.js so every call site names the mode it wants.

Do not update the tests. Do not run the tests. Edit the source files only, then list every file
you changed.
```

The outcome is model-dependent: a textbook half-even implementation keeps this suite green, and it goes red when Claude drops the tie handling and truncates. Either way you now have a multi-file diff across `src/` that you did not review, which is the state the rollback undoes. A truncating run reports:

```text
ℹ tests 15
ℹ suites 0
ℹ pass 11
ℹ fail 4
```

## Step 3: Rewind to the Anchor

The rewind restore replays a stored snapshot and is therefore byte-identical, while a model-written revert reconstructs code from context and can drift. The menu is driven by you, so this part is a keystroke sequence:

1. Press `Esc` twice with an empty prompt input, or type `/rewind`.
2. In the menu, select the prompt from Step 1 (the baseline and anchor turn).
3. Choose **Restore code** to revert the files while keeping the conversation.

Then verify with two independent checks, the suite and git:

```text
Verify the rollback of demos/01-fundamentals/04-git-worktrees/checkpoint-drill:

1. Run npm test in that folder and report pass and fail counts and the exit code.
2. Run git status --short for that folder only and report every line.
3. Print the first 10 lines of src/money.js.

Then state in one sentence whether the folder is back at the baseline, and if not, name exactly
which file still differs.
```

Expected Outcome: the suite is green again with the same counts as Step 1, and `git status --short` prints nothing for the drill folder.
