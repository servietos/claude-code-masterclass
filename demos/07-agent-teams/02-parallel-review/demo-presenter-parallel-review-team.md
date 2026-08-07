---
presents: demo-parallel-review-team.md
budget: 5 min
beats: 5
---

# Present: Review one API with three reviewers at once

A single reviewer gives you a report on the reviewer, not on the code. Five beats: the split that has to be by concern rather than by file, three teammates landing independently, redirecting one mid-run, the disagreement that survives instead of being averaged away, and the one ranked file at the end.

------

## Beats

### Beat 1: Split by lens, because the files cannot be split (1 min)

**Open:** [`Controllers/FoodController.cs`](catalog-service-cs/Controllers/FoodController.cs) · [Step 1: Split the Work by Lens, Not by File](demo-parallel-review-team.md#step-1-split-the-work-by-lens-not-by-file)
**Say:** All three reviewers need this one file, so a file-based split is impossible here. Security, performance and coverage own different questions about the same lines, which is what makes their findings disjoint.

```text
Spawn three agent team teammates, not sub-agents, named security, performance
and tests.
Every finding carries a severity, a file and a line, verified against the file.
Have them message each other by name wherever two lenses touch the same code
path, and record what they disagreed on.
```

**Result:** a team of four, the lead plus one teammate per lens

```text
session-279effd6
  team-lead   | team-lead       | in-process
  security    | general-purpose | in-process
  performance | general-purpose | in-process
  tests       | general-purpose | in-process
```

**Gotcha:** the flag lives in the global harness at `~/.claude/settings.json`; without it the same prompt quietly gives you sub-agents that cannot compare notes.

### Beat 2: They land when they are done, not in lockstep (1 min)

**Open:** [Step 2: Watch Them Land Independently](demo-parallel-review-team.md#step-2-watch-them-land-independently)
**Say:** Nobody is polling. A teammate finishing notifies the lead on its own, and the lead keeps a running picture of who is still out.

**Result:** the lead's own commentary as the reports arrive

```text
Three teammates running: security, perf, tests. Waiting on their reports.
Teammate @perf finished
Message from perf (ctrl+o to expand)
perf reported. Waiting on security and tests.
```

**Gotcha:** Ctrl+T toggles the shared task list; a task stuck pending while everyone is idle means an unresolved dependency, not a crash.

### Beat 3: Correct one reviewer without restarting the run (1 min)

**Open:** [Step 3: Redirect One Reviewer Without Restarting Anything](demo-parallel-review-team.md#step-3-redirect-one-reviewer-without-restarting-anything)
**Say:** A lens is a guess made before anyone saw the code. Arrow to the teammate, Enter, and type: it continues from where it was, and the other two never notice.

```text
Also cover the write path, not just the reads. Report what a PUT actually emits
against the database and what happens when the id does not exist.
```

**Result:** the extra scope lands as its own row in the final table

```text
| 23 | medium | performance | Controllers/FoodController.cs | 41 | Attach plus
Entry(item).State = Modified flags every property dirty, emitting a full-row
UPDATE ... |
```

**Gotcha:** while viewing a teammate, plain text goes to it but slash commands still run in the lead, so `/model` typed there changes the lead.

### Beat 4: The disagreement is the deliverable (1 min)

**Open:** [Step 4: Make the Disagreements Explicit](demo-parallel-review-team.md#step-4-make-the-disagreements-explicit)
**Say:** Two reviewers on one line is the interesting case, and averaging their severities throws the information away. Ask for the argument, not the merged number.

**Result:** a concession, and a disagreement kept unresolved on purpose

```text
Assertability of the missing UseHttpsRedirection at Program.cs:56
  Accepted: tests' position. security conceded outright, having reasoned about a
  deployed request rather than an in-process one.

Severity of the 204-instead-of-404 on GetById
  Accepted: both, unaveraged. The disclosure vector stays low and the coverage
  gap stays high.
```

**Gotcha:** this beat is the whole reason to pay for a team. Sub-agents never see each other's findings, so nothing can be conceded and nothing can be contested.

### Beat 5: One ranked file, and what they refused to do (1 min)

**Open:** [`review-findings.md`](catalog-service-cs-solution/review-findings.md) · [Step 6: Note What the Team Refused to Do](demo-parallel-review-team.md#step-6-note-what-the-team-refused-to-do)
**Say:** Forty-one findings, ranked, each tied to a line. The three criticals compound into one chain, and the reviewers were explicit about where they stopped short of proof.

**Result:** the chain, and the line they drew

```text
auth is off by default, so an unauthenticated GET /config returns a live SQL
admin credential over plain HTTP, and the wildcard CORS policy lets any origin
fetch it.

All three declined to run the DELETE because it would mutate the checked-in
food.db in a working tree another session may be using.
```

**Gotcha:** check one finding live before trusting forty. Open `FoodController.cs` line 51 and show `var item = GetById(id);` with no `await`.

## If the room asks

| Question | Answer |
|---|---|
| Why not one reviewer with a longer prompt? | It produces a report on the reviewer. One agent gravitates to one class of issue and the other two lenses come back thin, which is visible the moment you compare a single-session review with this table. |
| What does it cost? | Roughly four context windows instead of one. For a pre-ship review of code you are about to deploy that is cheap; for a routine diff it is not. |
| Could they have fixed what they found? | Not in parallel on these files. Split so no two teammates own the same file, or spawn one fix teammate and require plan approval before it edits. |
| Is 41 findings not too many? | The ranking is the answer to that: the top four are what you act on, and the rest is a backlog with lines attached. |
| Why did they not run the DELETE? | It would mutate the checked-in `food.db`. They measured the compiled DLL timestamp instead, which shows the defect ships past the compiler warning. |
