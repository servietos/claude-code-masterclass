# Anchor a Checkpoint and Roll Back a Runaway Refactor

Checkpoints let you rewind a session to a known state after Claude takes a change further than you wanted. You anchor a green pricing module, let an over-reaching cross-cutting refactor run until the suite goes red, then rewind to the anchor and prove the rollback landed with the tests and a diff. You finish knowing exactly what a restore covers, what it leaves untouched, and when to reach for it instead of git.

---

## Setup

Open Claude Code with the starter folder in scope. The project is plain ESM with `node:test` and zero npm dependencies, so there is nothing to install: running `npm install` here would only drop a `package-lock.json` into a folder that must stay pristine, and Step 5 verifies exactly that it is clean.

```bash
cd demos/01-fundamentals/06-git-worktrees/checkpoint-drill
npm test
```

Keep this terminal next to Claude Code for the whole drill: every step is verified by re-running `npm test` there.

---

## Step 1: Establish the Green Baseline and Anchor It

**Overview:** A rollback is only meaningful if you can prove where you landed. The green suite is that proof, so the first move is to confirm 15 passing tests and then anchor the session state with an explicit prompt before anything is touched.

**Research / Planning / Discussion:**

```text
Read demos/01-fundamentals/06-git-worktrees/checkpoint-drill/ and describe the module in your own words:
which file owns which responsibility, which files import which, and which single file every
other layer ultimately depends on.

Then tell me: if someone changed the rounding strategy in one place, which test files would
you expect to go red, and why?

Do not modify anything yet.
```

**Finding:** Claude should name `src/money.js` as the shared dependency that `discount.js`, `tax.js`, and `pricing.js` all import, and predict that a rounding change surfaces in `test/money.test.js` and `test/pricing.test.js` because those assert exact cent values. If it only mentions the money tests, push back and ask it to trace the import chain into `priceOrder`.

**Recipe:**

```text
Run npm test in demos/01-fundamentals/06-git-worktrees/checkpoint-drill and report the pass and fail
counts and the exit code.

Then anchor this state: I want to be able to return to exactly this point later. Confirm in one
sentence what the current state is (file list plus test result) so I can recognise it in the
rewind menu.

Do not change any file.
```

**Expected Outcome:** The terminal reports a fully green suite, and Claude's turn is now a labelled point in the session you can find again.

```text
> checkpoint-drill@1.0.0 test
> node --test

✔ findProduct returns a product with a unit price (0.7232ms)
✔ findProduct returns null for an unknown sku (0.0935ms)
✔ listSkus returns every catalog key (0.0756ms)
✔ roundCents rounds to two decimals (0.4132ms)
✔ multiply rounds the product (0.0788ms)
✔ sum adds a list of amounts (0.0649ms)
✔ formatEur prints two decimals and a currency suffix (0.0577ms)
✔ priceOrder prices a single line without a discount (0.9281ms)
✔ priceOrder applies per-line volume discounts (0.1012ms)
✔ priceOrder totals net plus tax (0.0738ms)
✔ renderInvoice prints one row per line plus the totals block (0.1724ms)
✔ discountRate picks the highest matching tier (0.4089ms)
✔ discountFor applies the tier to the line total (0.0898ms)
✔ taxRate falls back to zero for unknown countries (0.4794ms)
✔ taxFor applies the country rate to the net amount (0.0704ms)
ℹ tests 15
ℹ suites 0
ℹ pass 15
ℹ fail 0
ℹ cancelled 0
ℹ skipped 0
ℹ todo 0
ℹ duration_ms 93.5355
```

---

## Step 2: Learn What a Checkpoint Actually Covers

**Overview:** Most rollback disasters come from assuming a checkpoint covers more than it does. Before relying on it, pin down the boundary: which changes are tracked, which are invisible, and how the mechanic is invoked.

**Research / Planning / Discussion:**

```text
Look up the current Claude Code checkpointing documentation at
https://code.claude.com/docs/en/checkpointing and answer precisely:

1. When is a checkpoint created?
2. How do I open the rewind menu, by keystroke and by command?
3. Which of these are covered by a restore: edits made with Claude's file editing tools, files
   changed by a bash command Claude ran, files I edited by hand in my editor, database rows,
   git history?
4. What are the restore options in the menu and how do they differ?

Answer from the docs, not from memory, and quote the exact command name.
```

**Finding:** Claude should report that a checkpoint is captured before each user prompt, that the menu opens with `/rewind` or by pressing `Esc` twice on an empty prompt input, and that only edits made through Claude's file editing tools are tracked. Files touched by bash commands, your own manual edits, database state, and git history are all outside the boundary. If Claude mentions an `/undo` command, push back: it is not in the current docs.

**Recipe:**

```text
Write a five-row markdown table titled "Checkpoint coverage" with columns Change and Covered.
Rows: Claude Edit/Write tool changes, files changed by a bash command Claude ran, my own manual
editor changes, database rows, git commits and branches.

Below the table add two sentences: one on how checkpoints differ from a git commit, one on when
it is worth anchoring explicitly instead of relying on the automatic per-prompt checkpoint.

Do not modify any project file.
```

**Expected Outcome:** A coverage table where only the first row is covered, plus a stated distinction between session-level local undo (checkpoints) and permanent history (git).

---

## Step 3: Trigger the Runaway Refactor

**Overview:** This is the deliberate mistake. You ask for a cross-cutting change that touches every layer at once, which is exactly the shape of change that is painful to unwind by hand and cheap to unwind with a checkpoint.

**Research / Planning / Discussion:**

```text
I am considering changing the rounding strategy of the pricing module from half-up rounding to
banker's rounding (round half to even), applied everywhere: money.js, and every call site in
discount.js, tax.js and pricing.js.

Before writing code, tell me how many files this touches, how many existing test assertions it
would invalidate, and whether you would do it as one change or in stages.
```

**Finding:** Claude should count at least four source files and flag that the cent-level assertions in `test/money.test.js` and `test/pricing.test.js` encode half-up behaviour, so a single sweeping change breaks the suite. Treat a confident "this is safe, no tests will change" as a warning sign and ask which exact assertion values it expects after the change.

**Recipe:**

```text
Change the rounding strategy of demos/01-fundamentals/06-git-worktrees/checkpoint-drill from half-up to
banker's rounding (round half to even). Apply it consistently: replace the implementation in
src/money.js and thread an explicit rounding-mode parameter through src/discount.js, src/tax.js
and src/pricing.js so every call site names the mode it wants.

Do not update the tests. Do not run the tests. Edit the source files only, then list every file
you changed.
```

**Expected Outcome:** Claude reports a multi-file diff across `src/`, and `npm test` in your terminal either stays green or reports failures depending on how the change was implemented. This step is model-dependent: Claude may thread the parameter differently, break a different set of tests, or produce a diff that still passes. Any multi-file diff is enough to continue, since the point of the drill is the rollback, not the failure count.

A textbook half-even implementation actually keeps this suite green, because `roundCents(2.375)` rounds `237.5` to the even `238` and still yields `2.38`:

```text
ℹ tests 15
ℹ suites 0
ℹ pass 15
ℹ fail 0
ℹ cancelled 0
ℹ skipped 0
ℹ todo 0
ℹ duration_ms 100.0494
```

The suite goes red when Claude drops the tie handling and truncates instead, which is a common mis-implementation of the request. That run looks like this (passing lines elided):

```text
✖ roundCents rounds to two decimals (0.8072ms)
✖ multiply rounds the product (0.1328ms)
✖ priceOrder applies per-line volume discounts (0.7817ms)
✖ priceOrder totals net plus tax (0.199ms)
...
ℹ tests 15
ℹ suites 0
ℹ pass 11
ℹ fail 4
ℹ cancelled 0
ℹ skipped 0
ℹ todo 0
ℹ duration_ms 101.6725

✖ failing tests:

test at test\money.test.js:5:1
✖ roundCents rounds to two decimals (0.8072ms)
  AssertionError [ERR_ASSERTION]: Expected values to be strictly equal:

  2.37 !== 2.38
```

Either way you now have a multi-file diff across `src/` that you did not review, which is the state the rollback undoes.

---

## Step 4: Rewind to the Anchor

**Overview:** Now you recover. Instead of asking Claude to undo its own work (which is another set of edits that can go wrong), you use the session mechanic and restore the files from the snapshot taken before the refactor prompt.

**Research / Planning / Discussion:**

```text
I want to discard the refactor you just made and get back to the state before my refactor prompt.

Compare two recovery routes for me: asking you to revert the edits by writing the old code back,
versus using the rewind menu to restore the code. Which one guarantees byte-identical files, and
which one can drift? Answer in four sentences.

Do not change anything yet.
```

**Finding:** Claude should say the rewind restore replays a stored snapshot and is therefore byte-identical, while a model-written revert reconstructs code from context and can drift, especially across four files. If it claims both are equivalent, ask it what happens when the session context has been compacted since the edit.

**Recipe:** This step has no prompt. The rewind menu is driven by you, not by Claude, so the recipe is a keystroke sequence rather than something you paste into the input:

1. Press `Esc` twice with an empty prompt input, or type `/rewind`.
2. In the menu, select the prompt from Step 1 (the baseline and anchor turn).
3. Choose **Restore code** to revert the files while keeping the conversation.

If Claude is still mid-run when you spot the problem, press `Esc` once first to interrupt it, then open the menu. The outcome here is session-dependent: what you see is the rewind list of your own prompts, and after the restore the conversation reports which files were reverted. There is no fixed text to match, so verify with a command instead of by reading the screen.

**Expected Outcome:** The rewind menu lists your session prompts, the restore reports reverted files, and the `src/` files are back to their pre-refactor content. Verification comes in the next step.

---

## Step 5: Prove the Rollback with the Suite and the Diff

**Overview:** A restore you did not verify is a hope, not a recovery. Two independent checks close the loop: the test suite is green again, and git reports no modifications in the drill folder.

**Research / Planning / Discussion:**

```text
I just restored the code from a checkpoint. Propose two independent checks that would prove the
files are back at the exact baseline state, and explain what each check would fail to catch on
its own. Do not run anything yet.
```

**Finding:** Claude should propose re-running the suite (catches behavioural regressions but not stray untracked files) and inspecting `git status` or `git diff` for the drill folder (catches leftover or new files but not behaviour). If it proposes only the tests, ask it what would happen if the refactor had also added a new file.

**Recipe:**

```text
Verify the rollback of demos/01-fundamentals/06-git-worktrees/checkpoint-drill:

1. Run npm test in that folder and report pass and fail counts and the exit code.
2. Run git status --short for that folder only and report every line.
3. Print the first 10 lines of src/money.js.

Then state in one sentence whether the folder is back at the baseline, and if not, name exactly
which file still differs.
```

**Expected Outcome:** The suite is green again with the same counts as Step 1, and `git status --short` prints nothing for the drill folder:

```text
...
ℹ tests 15
ℹ suites 0
ℹ pass 15
ℹ fail 0
ℹ cancelled 0
ℹ skipped 0
ℹ todo 0
ℹ duration_ms 93.5355
```

---

## Step 6: Decide When to Anchor and When to Commit

**Overview:** The drill only pays off if you know which tool to reach for next time. Checkpoints are session-local undo, git is permanent history, and the two fail in different ways.

**Research / Planning / Discussion:**

```text
Based on this drill, work out a decision rule for me.

For each situation, say whether a checkpoint anchor is enough, whether a git commit is required,
or whether both are: a risky refactor I might abandon in the next ten minutes; a working feature
I want to keep across a machine restart; a migration script that writes to a database; a change
made partly by you and partly by me editing files by hand; work I want a colleague to review.

One line per situation, with the reason.
```

**Finding:** Claude should require a git commit for anything crossing a session boundary or a review, treat the abandonable refactor as the pure checkpoint case, and flag both the database migration and the mixed manual edits as outside the checkpoint boundary. If it treats checkpoints as a git substitute anywhere, send it back to the coverage table from Step 2.

**Recipe:**

```text
Write demos/01-fundamentals/06-git-worktrees/checkpoint-drill/rollback-playbook.md with:

- An H1 title that is a verb-action phrase
- A short intro of at most three sentences
- A "Decision Rule" table with columns Situation, Anchor, Commit, Why, covering the five
  situations above
- A "Before You Start Anything Risky" section with three copy-paste prompts that anchor state
- A closing note naming what checkpoints never cover

No em dashes. Every code fence declares a language.
```

**Expected Outcome:** A `rollback-playbook.md` in the drill folder containing a five-row decision table and three anchor prompts. Since you created it after the restore, it is the only entry `git status --short` reports for that folder.


---

The completed reference for this drill lives in [checkpoint-drill-solution/](checkpoint-drill-solution/readme.md).
