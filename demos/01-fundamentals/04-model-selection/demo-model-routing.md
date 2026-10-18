# Route Tasks to the Cheapest Model That Still Works

Model choice is a routing decision, and the only way to settle it is to measure. You run the same work on Haiku, Sonnet, and Opus with `/usage` and `/context` open, and weigh cost against output quality.

---

Work in `demos/01-fundamentals/04-model-selection/model-routing-api`; no solution folder ships, so your measured results table is `model-routing-api/MODEL-NOTES.md`.

## Step 1: Repeat the Task One Tier Up

A price comparison is only meaningful when the task is held constant. Run a mechanical, fully specified edit on the fast tier, then run `/usage` and record this run as row 1 of `MODEL-NOTES.md` (task, model, compiled, follow-up correction, session cost):

```text
/model haiku

@Controllers/TodosController.cs @Models/PaginatedResponse.cs

Add page and pageSize query parameters to the list action and return
PaginatedResponse<Todo>, matching the field names in the model file exactly.
Change nothing else in the file.
```

Then run the same class of edit one tier up:

```text
/model sonnet

@Controllers/UsersController.cs @Models/PaginatedResponse.cs

Add page and pageSize query parameters to the list action and return
PaginatedResponse<User>, matching the field names in the model file exactly.
Change nothing else in the file.
```

Then run `/usage` and add this run as the second row of `MODEL-NOTES.md`.

Expected Outcome: a second row in `MODEL-NOTES.md` and a compiled `UsersController.cs`. In most runs the two outputs are equivalent on a task this mechanical, which is the finding: the cheap tier was sufficient and the extra spend bought nothing.

## Step 2: Give the Top Tier Work That Justifies It

Opus earns its cost on decision work, where several answers are defensible and the wrong one is expensive to unwind. Hand it a cross-cutting change and compare the shape of the response, then have it implement the option it recommended and add the run as the third row of `MODEL-NOTES.md`.

```text
/model opus

@Program.cs @Controllers/TodosController.cs @Controllers/UsersController.cs

Both controllers now paginate with duplicated parameter handling. Propose three
different ways to remove that duplication in this codebase, with the trade-offs
of each, and say which one you would pick and why.

Do not implement anything yet.
```

Expected Outcome: genuinely different designs (a shared base controller, a binding model, a filter or middleware), with at least one of its own options rejected for a concrete reason. This is the observable difference from Step 1: the answer contains a defended decision.

## Step 3: Cut the Bill Without Changing the Model

Tier selection is one lever and context size is the other. Measure how much of your spend is the model and how much is what you are sending it every turn.

```text
/context

Break down what is filling my context window right now: instructions, files I
attached, and conversation history. Which part is largest, and which parts
would survive a /compact?

Then tell me which of these gives the bigger saving on my next ten turns:
dropping one tier, or halving what I send.
```

Then run `/compact` and `/context` again, and ask what changed in tokens and what the compaction dropped.

Expected Outcome: a visibly smaller context reading after compaction and an honest statement of what was dropped. If the largest slice is conversation history, `/compact` is the lever; if it is attached files, narrower `@`-mentions are.
