---
presents: demo-model-routing.md
budget: 5 min
beats: 5
---

# Present: Route Tasks to the Cheapest Model That Still Works

Five beats run the same tasks across three model tiers and turn the measurements into a rule anyone can apply. The room walks away with a routing rule stated as a signal rather than a difficulty adjective, and with the knowledge that context size is the larger half of the bill.

------

**No solution folder ships.** `MODEL-NOTES.md` is the only new file in `model-routing-api/`; everything else is an edit the demo's Cleanup reverts.

## Beats

### Beat 1: Route on a signal, not on a difficulty adjective (1 min)

**Open:** [`model-routing-api/Program.cs`](model-routing-api/Program.cs) · [`model-routing-api/Controllers/`](model-routing-api/Controllers/)
**Say:** Model choice is a routing decision, and routing needs its categories fixed before any measurement. A category a colleague cannot apply to an unseen task collects anecdotes instead.

```text
Read Program.cs and both files under Controllers/.

List eight realistic tasks someone would actually do in this codebase, from a
one-line rename up to a cross-cutting refactor. For each one, say which model
tier you would route it to (Haiku, Sonnet, or Opus) and what specifically about
the task drives that choice.

Name the signal, not the vibe: number of files touched, whether the change needs
a decision or just a transformation, and whether being wrong is cheap or expensive.
```

**Result:** nothing on disk; the Recipe collapses the eight tasks into a five-row table in chat, which the next three beats test.

**Gotcha:** any justification that reduces to "this task is complex" goes back with the question of which named signal is actually present.

### Beat 2: Hold the prompt constant or the comparison proves nothing (1 min)

**Open:** [`model-routing-api/Controllers/TodosController.cs`](model-routing-api/Controllers/TodosController.cs) · [`model-routing-api/Controllers/UsersController.cs`](model-routing-api/Controllers/UsersController.cs) · [`model-routing-api/Models/PaginatedResponse.cs`](model-routing-api/Models/PaginatedResponse.cs)
**Say:** Almost every claim that one model beats another comes from two runs that differed in more than the model. Deciding what to hold constant is part of the experiment, not preparation for it.

```text
/model haiku

@Controllers/TodosController.cs @Models/PaginatedResponse.cs

Add page and pageSize query parameters to the list action and return
PaginatedResponse<Todo>, matching the field names in the model file exactly.

...

/model sonnet

@Controllers/UsersController.cs @Models/PaginatedResponse.cs
```

**Result:** rows 1 and 2 of `MODEL-NOTES.md`, created by this step in [`model-routing-api/`](model-routing-api/), plus two controllers whose fields must match `Page` and `Size` in the starter's record, not the prompt's `pageSize`.

**Gotcha:** on a task this fully specified the outputs usually match, which is the finding rather than a disappointment.

### Beat 3: The top tier earns it on decisions, not on edits (1 min)

**Open:** [Step 4: Give the Top Tier Work That Justifies It](demo-model-routing.md#step-4-give-the-top-tier-work-that-justifies-it) · [`model-routing-api/Program.cs`](model-routing-api/Program.cs)
**Say:** A fully specified edit has one right answer, so the strongest model has nothing to be strong about. The tiers separate on work with several defensible answers and an expensive wrong one.

```text
/model opus

@Program.cs @Controllers/TodosController.cs @Controllers/UsersController.cs

Both controllers now paginate with duplicated parameter handling. Propose three
different ways to remove that duplication in this codebase, with the trade-offs
of each, and say which one you would pick and why.

Do not implement anything yet.
```

**Result:** no file changes; the prompt ends "Do not implement anything yet", and the Step 4 Recipe adds row 3 of `MODEL-NOTES.md`.

**Gotcha:** a strong response rejects one of its own three options for a concrete reason, and that rejection is what the top tier is being paid for.

### Beat 4: Tier is the smaller lever (1 min)

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

**Result:** no file changes; the artifact is the second `/context` reading, which the Step 5 Recipe asks for in tokens after a `/compact`.

**Gotcha:** the answer has to name the largest slice on the screen: history makes `/compact` the lever, attached files make narrower `@`-mentions it.

### Beat 5: A policy no measurement could falsify is not a policy (1 min)

**Open:** [Step 6: Encode the Policy Where It Will Be Read](demo-model-routing.md#step-6-encode-the-policy-where-it-will-be-read) · [`model-routing-api/`](model-routing-api/)
**Say:** A routing rule that lives in someone's head gets skipped under deadline. What makes it a policy rather than an opinion is a row the measurements changed.

```text
Add a "## Model routing" section to CLAUDE.md with:

- The revised routing table, one line per task pattern.
- A default: start on the cheapest tier that has ever succeeded at this pattern
  and escalate only after a failed attempt, never in anticipation.
- A rule: before a multi-file refactor, run /context and compact if history is
  the largest slice.

Keep every line checkable. Then show me the section you wrote.
```

**Result:** a fourth section in [`model-routing-api/CLAUDE.md`](model-routing-api/CLAUDE.md), where the starter ships three (Architecture, Conventions, Build and Run)

```diff
 ## Conventions
 
 Return `ProblemDetails` for every error, using the `Problem()` helper in controllers. Use 4xx for client errors and 5xx for server errors. Every list endpoint returns `PaginatedResponse<T>`.
+
+## Model routing
+
+- A default: start on the cheapest tier that has ever succeeded at this pattern
+  and escalate only after a failed attempt, never in anticipation.
```

**Gotcha:** note the word revised: if nothing in the table changed, ask which measurement would have changed it.

## If the room asks

| Question | Answer |
|---|---|
| The starter's `CLAUDE.md` already requires `PaginatedResponse<T>`. Does that give Haiku the answer? | It gives the target, not the edit; watch whether each tier matches the record's real field names (`Page`, `Size`) instead of inventing `pageSize`. |
| Does switching tiers three times cost anything by itself? | Yes, each `/model` switch rebuilds the whole cached prefix, so pick the tier at the top of a session. |
| Is fast mode a cheaper Opus? | No, it runs Opus with faster output and is priced above standard Opus usage. |
| What do I do when I hit the plan limit? | `/usage` shows where you stand and `/usage-credits` opens the billing surface; it needs a claude.ai login, so an API-key session cannot use it. |
| How many rows should the routing table have? | Five at most; a longer table is a lookup of this demo rather than a policy. |
