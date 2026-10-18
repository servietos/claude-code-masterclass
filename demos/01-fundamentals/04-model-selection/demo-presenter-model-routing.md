---
presents: demo-model-routing.md
budget: 4 min
beats: 3
---

# Present: Route Tasks to the Cheapest Model That Still Works

Three beats run the same tasks across three model tiers and weigh the tier against context size. The room walks away knowing the top tier earns its cost on decisions, and that context size is the larger half of the bill.

------

**No solution folder ships.** `MODEL-NOTES.md` is the only new file in `model-routing-api/`; the controller edits are changes to revert from git before the next run.

## Beats

### Beat 1: Hold the prompt constant or the comparison proves nothing (2 min)

**Open:** [`model-routing-api/Controllers/TodosController.cs`](model-routing-api/Controllers/TodosController.cs) · [`model-routing-api/Controllers/UsersController.cs`](model-routing-api/Controllers/UsersController.cs) · [`model-routing-api/Models/PaginatedResponse.cs`](model-routing-api/Models/PaginatedResponse.cs)
**Say:** Almost every claim that one model beats another comes from two runs that differed in more than the model. Deciding what to hold constant is part of the experiment itself.

```text
/model haiku

@Controllers/TodosController.cs @Models/PaginatedResponse.cs

Add page and pageSize query parameters to the list action and return
PaginatedResponse<Todo>, matching the field names in the model file exactly.

...

/model sonnet

@Controllers/UsersController.cs @Models/PaginatedResponse.cs
```

**Result:** rows 1 and 2 of `MODEL-NOTES.md`, created by this step in [`model-routing-api/`](model-routing-api), plus two controllers whose list actions take `page` and `pageSize` and return `PaginatedResponse<Todo>` and `PaginatedResponse<User>`.

**Gotcha:** on a task this fully specified the outputs usually match, and that match is the finding.

### Beat 2: The top tier earns its cost on decisions (1 min)

**Open:** [Step 2: Give the Top Tier Work That Justifies It](demo-model-routing.md#step-2-give-the-top-tier-work-that-justifies-it) · [`model-routing-api/Program.cs`](model-routing-api/Program.cs)
**Say:** A fully specified edit has one right answer, so the strongest model has nothing to be strong about. The tiers separate on work with several defensible answers and an expensive wrong one.

```text
/model opus

@Program.cs @Controllers/TodosController.cs @Controllers/UsersController.cs

Both controllers now paginate with duplicated parameter handling. Propose three
different ways to remove that duplication in this codebase, with the trade-offs
of each, and say which one you would pick and why.

Do not implement anything yet.
```

**Result:** no file changes; the prompt ends "Do not implement anything yet", and Step 2 adds row 3 of `MODEL-NOTES.md`.

**Gotcha:** a strong response rejects one of its own three options for a concrete reason, and that rejection is what the top tier is being paid for.

### Beat 3: Tier is the smaller lever (1 min)

**Open:** [`readme.md`](readme.md#the-other-half-of-the-bill)
**Say:** The whole conversation is sent again on every turn, so what you send compounds in a way the tier never does. Context is the larger half of the bill and the half nobody inspects.

```text
/context

Break down what is filling my context window right now: instructions, files I
attached, and conversation history. Which part is largest, and which parts
would survive a /compact?

Then tell me which of these gives the bigger saving on my next ten turns:
dropping one tier, or halving what I send.
```

**Result:** no file changes; the artifact is the second `/context` reading, which Step 3 asks for in tokens after a `/compact`.

**Gotcha:** the answer has to name the largest slice on the screen: history makes `/compact` the lever, attached files make narrower `@`-mentions it.

## If the room asks

| Question | Answer |
|---|---|
| The starter's `CLAUDE.md` already requires `PaginatedResponse<T>`. Does that give Haiku the answer? | It gives the target, and the edit is still the model's to write; watch whether each tier builds the record with its real fields (`Page`, `Size`) and invents no names. |
| Does switching tiers three times cost anything by itself? | Yes, each `/model` switch rebuilds the whole cached prefix, so pick the tier at the top of a session. |
| Is fast mode a cheaper Opus? | No, it runs Opus with faster output and is priced above standard Opus usage. |
