# Review one API with three reviewers at once

A single reviewer drifts toward one class of problem and reports it well, so the review you get is a report on the reviewer. Here three teammates take one lens each, argue where their findings collide, and the lead merges what survives into a single ranked file.

------

Work in `catalog-service-cs/`; the finished result is beside it in [`catalog-service-cs-solution/`](catalog-service-cs-solution), holding the team's `review-findings.md`.

## Step 1: Split the Work by Lens, Not by File

All three reviewers need `FoodController.cs`, so a concern-based split is the only one that produces disjoint findings. Agent teams must be enabled first, with `"CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS": "1"` under `env` in `~/.claude/settings.json`.

```text
Spawn three agent team teammates, not sub-agents, named security, performance
and tests.
- security: Controllers/, Common/AppConfig.cs, Common/AppBuilder.cs,
  appsettings.json and Program.cs. Authentication, input validation, secret
  handling, and anything an anonymous caller can reach.
- performance: Infrastructure/FoodDBContext.cs and the query paths in
  Controllers/FoodController.cs. Query shape, tracking, allocation per request.
- tests: the whole project. What coverage exists, and what a first test file
  would have to cover to catch the other two lenses' findings.
Every finding carries a severity, a file and a line, verified against the file.
Have them message each other by name wherever two lenses touch the same code
path, and record what they disagreed on. Do not change any source file.
```

Three rows appear in the agent panel and a team of four in `~/.claude/teams/session-XXXXXXXX/config.json`. Leave the session in the foreground and press Ctrl+T to toggle the shared task list; the lead reports each teammate as it lands, without polling. Teammates finish when their own work is done, which separates a team from three sequential sub-agent calls.

## Step 2: Redirect One Reviewer Without Restarting Anything

A lens is a guess you made before seeing the code, so correcting one reviewer mid-run without touching the other two is what makes the guess cheap. Select `performance` in the agent panel with the up and down arrows, press Enter to open its transcript, and send it:

```text
Also cover the write path, not just the reads. Report what a PUT actually emits
against the database and what happens when the id does not exist, with the same
units you used for the read path.
```

The teammate continues from where it was, and the extra work lands as its own rows in the final table:

```text
| 23 | medium | performance | Controllers/FoodController.cs | 41 | Attach plus
Entry(item).State = Modified flags every property dirty, emitting a full-row
UPDATE, and a PUT for a missing ID affects 0 rows and surfaces as a
DbUpdateConcurrencyException 500 instead of a 404. |
```

The other two teammates keep working while this one is redirected. While you are viewing a teammate, plain text goes to that teammate but built-in slash commands still run in the lead's session.

## Step 3: Make the Disagreements Explicit

Two reviewers filing the same line is the interesting case, and averaging their severities destroys the information. The deliverable is one ordering, because the only question a reader has is what to fix first.

```text
Before writing anything: for every line two lenses both filed, have the two
teammates message each other and settle whether it is one defect or two. Record
each disagreement with both positions, which one was accepted, and why. If a
teammate concedes, say so and say what convinced it.
Wait for all teammates to finish, then write review-findings.md in this folder:
- One table of every finding: number, severity, lens, file, line, one sentence.
- Ranked by severity, then by blast radius.
- A contested section with each disagreement, both positions, and which was
  accepted.
- Do not include a finding no reviewer actually reported.
```

[`review-findings.md`](catalog-service-cs-solution/review-findings.md) ranks every finding and keeps each disagreement unaveraged in its contested section, including one reviewer withdrawing a claim about what can be tested:

```text
Assertability of the missing UseHttpsRedirection at Program.cs:56
  Accepted: tests' position. security conceded outright, having reasoned about a
            deployed request rather than an in-process one.
```
