# Route Tasks to the Cheapest Model That Still Works

Model choice is a routing decision rather than a preference, and the only way to settle it is to measure. You classify a C# Web API's realistic tasks into tiers, run the same work on Haiku, Sonnet, and Opus with `/usage` and `/context` open, and weigh cost against output quality. You finish with a measurements table and a routing policy encoded in CLAUDE.md.

---

## Demo Files

Work directly in the starter. It is a small ASP.NET Core API carrying tasks at three genuinely different difficulty levels, and it sits in this topic folder:

```bash
cd demos/01-fundamentals/06-model-selection/model-routing-api
claude
```

| File | What it represents |
|------|--------------------|
| `Controllers/TodosController.cs` | A small, mechanical target: the kind of edit a fast model should handle |
| `Controllers/UsersController.cs` | The second controller, used to check consistency across a repeated task |
| `Models/PaginatedResponse.cs` | The response envelope every task in this demo must match |
| `Program.cs` | Service registration, the file a cross-cutting refactor has to reason about |
| `MODEL-NOTES.md` | Created in Step 2; your measured results table |

---

## Step 1: Classify the Work Before Choosing a Tier

Overview: Model choice is a routing decision, and routing needs categories. Before running anything, get an explicit split of this project's realistic tasks into tiers, so the runs that follow are testing a hypothesis instead of collecting anecdotes.

Research / Planning / Discussion:

```text
Read Program.cs and both files under Controllers/.

List eight realistic tasks someone would actually do in this codebase, from a
one-line rename up to a cross-cutting refactor. For each one, say which model
tier you would route it to (Haiku, Sonnet, or Opus) and what specifically about
the task drives that choice.

Name the signal, not the vibe: number of files touched, whether the change needs
a decision or just a transformation, and whether being wrong is cheap or expensive.
```

Finding: A useful answer separates transformation work (mechanical, verifiable, low blast radius) from decision work (trade-offs, multiple valid answers, expensive to redo). Push back on any justification that reduces to "this task is complex": ask which of the named signals is actually present.

Recipe:

```text
Turn your task list into a routing table with three columns: task pattern,
model tier, and the signal that decides it.

Collapse the eight tasks into at most five general patterns, so the table is a
policy I can apply to work you have not seen yet, not a lookup of these
specific tasks. Output it in chat only.
```

Expected Outcome: A five-row routing table in the response where every row names a decision signal, not a difficulty adjective. This is the hypothesis the next three steps test.

---

## Step 2: Baseline a Mechanical Task on the Fast Tier

Overview: The cheapest tier is the correct default until it demonstrably fails. Start with a mechanical, fully specified edit and measure it, so every later run has a number to be compared against.

Research / Planning / Discussion:

```text
Run /model and tell me which model is active right now, and what /usage and
/context each report.

Explain what each number actually counts, and which of them will move when I
switch models versus when I change my prompt. Do not change any settings yet.
```

Finding: Read the response against the numbers on your own screen and reject any figure that is not visible in your session output. The point of this step is learning which panel to read, so if the explanation is vague about what `/context` counts, ask again naming the exact line you see.

Recipe:

```text
/model haiku

@Controllers/TodosController.cs @Models/PaginatedResponse.cs

Add page and pageSize query parameters to the list action and return
PaginatedResponse<Todo>, matching the field names in the model file exactly.
Change nothing else in the file.
```

Then measure the run and record it:

```text
/usage

Create MODEL-NOTES.md with a table: task, model, whether the result compiled,
whether it needed a follow-up correction, and the session cost after this run.
Fill in the first row from what we just did. Leave the remaining rows empty.
```

Expected Outcome: A modified `Controllers/TodosController.cs` that compiles under `dotnet build`, plus a `MODEL-NOTES.md` with one filled row. Note whether you had to correct the output at all, because that follow-up turn is part of the true cost of the cheap tier.

---

## Step 3: Repeat the Task One Tier Up

Overview: A price comparison is only meaningful when the task is held constant. Run the same class of edit on the middle tier and record it in the same table, so the difference you observe is attributable to the model and not to a different prompt.

Research / Planning / Discussion:

```text
I am about to run the same kind of edit on UsersController with a stronger model.

What would make this comparison invalid? Name every variable I need to hold
constant between the two runs, and tell me which differences in the output
would be real evidence of a tier difference rather than ordinary variation.
```

Finding: Expect the answer to flag the obvious confounds: a differently worded prompt, an already-warm conversation carrying the earlier answer, and a file that is not actually equivalent. Treat any claim that the stronger model is simply better without an observable difference as something to test rather than accept.

Recipe:

```text
/model sonnet

@Controllers/UsersController.cs @Models/PaginatedResponse.cs

Add page and pageSize query parameters to the list action and return
PaginatedResponse<User>, matching the field names in the model file exactly.
Change nothing else in the file.

Then run /usage and add this run as the second row of MODEL-NOTES.md.
```

Expected Outcome: A second row in `MODEL-NOTES.md` and a compiled `UsersController.cs`. In most runs the two outputs are equivalent on a task this mechanical, which is the finding: the cheap tier was sufficient and the extra spend bought nothing.

---

## Step 4: Give the Top Tier Work That Justifies It

Overview: Opus earns its cost on decision work, where several answers are defensible and the wrong one is expensive to unwind. Hand it a cross-cutting change and compare the shape of the response, not just whether it compiles.

Research / Planning / Discussion:

```text
/model opus

@Program.cs @Controllers/TodosController.cs @Controllers/UsersController.cs

Both controllers now paginate with duplicated parameter handling. Propose three
different ways to remove that duplication in this codebase, with the trade-offs
of each, and say which one you would pick and why.

Do not implement anything yet.
```

Finding: A strong response offers genuinely different designs (a shared base controller, a binding model, a filter or middleware) and rejects at least one of its own options for a concrete reason. This is the observable difference from Step 3: the answer contains a defended decision, not just a transformation.

Recipe:

```text
Implement the option you recommended.

Keep both controllers compiling, do not change the JSON shape either endpoint
returns, and show me the diff for every file before you write it.

Then run /usage and add this run as the third row of MODEL-NOTES.md, including
which tier you would route this task to knowing what it actually took.
```

Expected Outcome: A refactor spanning at least two files that still builds with `dotnet build`, and a third row in `MODEL-NOTES.md`. Compare the three cost figures: the gap tells you what decision work costs relative to transformation work in this codebase.

---

## Step 5: Cut the Bill Without Changing the Model

Overview: Tier selection is one lever and context size is the other. Before committing to a policy, measure how much of your spend is the model and how much is what you are sending it every turn.

Research / Planning / Discussion:

```text
/context

Break down what is filling my context window right now: instructions, files I
attached, and conversation history. Which part is largest, and which parts
would survive a /compact?

Then tell me which of these gives the bigger saving on my next ten turns:
dropping one tier, or halving what I send.
```

Finding: Look for an answer that ties the recommendation to the actual numbers on your screen rather than a general claim that context is expensive. If the largest slice is conversation history, `/compact` is the lever; if it is attached files, narrower `@`-mentions are.

Recipe:

```text
/compact

Then run /context again and tell me what changed, in tokens, and what
information was lost in the compaction that I might still need.
```

Expected Outcome: A visibly smaller context reading after compaction and an honest statement of what was dropped. You have now seen both levers move independently, which is what makes the policy in the next step specific.

---

## Step 6: Encode the Policy Where It Will Be Read

Overview: A routing decision you have to remember is a routing decision you will forget under deadline. Write the measured result into CLAUDE.md so it applies automatically on every future session in this repository.

Research / Planning / Discussion:

```text
Read MODEL-NOTES.md.

Compare what actually happened in those three runs against the routing table you
proposed in Step 1. Which of your original predictions did the measurements
support, and which did they contradict?

Rewrite only the rows the evidence changed.
```

Finding: The valuable output here is a revised row, not a confirmation. If nothing in the table changed, ask which measurement would have changed it, because a policy no observation could falsify is not a policy.

Recipe:

```text
Add a "## Model routing" section to CLAUDE.md with:

- The revised routing table, one line per task pattern.
- A default: start on the cheapest tier that has ever succeeded at this pattern
  and escalate only after a failed attempt, never in anticipation.
- A rule: before a multi-file refactor, run /context and compact if history is
  the largest slice.

Keep every line checkable. Then show me the section you wrote.
```

Expected Outcome: A `## Model routing` section in `CLAUDE.md` grounded in your own measurements, plus `MODEL-NOTES.md` as the evidence behind it. Start a fresh session, ask for a one-line rename, and Claude proposes the cheap tier without being prompted.

---

## Summary

You predicted a routing policy, tested it on three real tasks at three tiers, and let the measurements correct the prediction. You saw where a stronger model changes nothing (a fully specified mechanical edit) and where it changes the kind of answer you get (a design with defended trade-offs), and you separated model cost from context cost with `/context` and `/compact`.

Continue with [Configure the Permission Model](../07-permissions/demo-permission-settings.md), which puts the same kind of rule into a machine-readable settings file.

