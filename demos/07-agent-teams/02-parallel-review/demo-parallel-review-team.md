# Review one API with three reviewers at once

A single reviewer drifts toward one class of problem and reports it well, so the review you get is a report on the reviewer rather than on the code. Here three teammates take one lens each, argue where their findings collide, and the lead merges what survives into a single ranked file. What you hold at the end is a `review-findings.md` for `catalog-service-cs` with every finding tied to a file and a line, and a contested section recording what the reviewers disagreed on.

------

## Running the Starter API

Run these commands from the repository root:

```bash
cd demos/07-agent-teams/02-parallel-review/catalog-service-cs
dotnet restore
dotnet run
```

The launch profile binds `http://localhost:5000` and answers `GET /food` with five catalog items. Stop it with Ctrl+C before starting the team, then start Claude Code in the same folder:

```bash
cd demos/07-agent-teams/02-parallel-review/catalog-service-cs
claude
```

Agent teams must be enabled in your global harness at `~/.claude/settings.json` before this demo does anything a sub-agent could not:

```json
{
  "env": {
    "CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS": "1"
  }
}
```

---

## Step 1: Split the Work by Lens, Not by File

**Overview:** The split decides whether you get three reviews or one review three times. All three reviewers need `FoodController.cs`, so a file-based split is impossible and a concern-based split is the only one that produces disjoint findings.

**Research:**

```text
Read Controllers/, Common/AppConfig.cs, Infrastructure/FoodDBContext.cs,
appsettings.json and Program.cs in this folder.

Propose three review lenses that between them cover this API, and for each one
name the files and functions that lens owns. Then name every place two lenses
would land on the same line, and say how you would tell a duplicate from two
separate defects that happen to share a line.
```

**Finding:** you want security, performance and test coverage, with the overlap acknowledged rather than engineered away. The right answer to the last question is that two lenses filing the same line are separate defects when the fixes differ, and a good response names `FoodController.cs` line 51 as the obvious collision. Push back on any lens described as general code quality: a reviewer responsible for everything reports the same things as the others.

**Recipe:**

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

**Expected Outcome:** three rows in the agent panel, and a team of four in `~/.claude/teams/session-XXXXXXXX/config.json`:

```text
session-279effd6
  team-lead   | team-lead       | in-process
  security    | general-purpose | in-process
  performance | general-purpose | in-process
  tests       | general-purpose | in-process
```

---

## Step 2: Watch Them Land Independently

**Overview:** Teammates finish when their own work is done, not in lockstep, and the lead is told without asking. Seeing that on screen is what separates a team from three sequential sub-agent calls.

**Recipe:**

Leave the session in the foreground. Press Ctrl+T to toggle the shared task list.

**Expected Outcome:** the lead reports each teammate as it lands, and teammate messages arrive without it polling:

```text
Three teammates running: security, perf, tests. Waiting on their reports.
Teammate @perf finished
Message from perf (ctrl+o to expand)
perf reported. Waiting on security and tests.
Teammate @security finished
Waiting on tests.
```

---

## Step 3: Redirect One Reviewer Without Restarting Anything

**Overview:** A lens is a guess you made before seeing the code, so the ability to correct one reviewer mid-run without touching the other two is what makes the guess cheap.

**Recipe:**

Select `performance` in the agent panel with the up and down arrows, press Enter to open its transcript, and send it:

```text
Also cover the write path, not just the reads. Report what a PUT actually emits
against the database and what happens when the id does not exist, with the same
units you used for the read path.
```

**Expected Outcome:** the teammate continues from where it was rather than starting over, and the extra work lands as its own rows in the final table:

```text
| 23 | medium | performance | Controllers/FoodController.cs | 41 | Attach plus
Entry(item).State = Modified flags every property dirty, emitting a full-row
UPDATE, and a PUT for a missing ID affects 0 rows and surfaces as a
DbUpdateConcurrencyException 500 instead of a 404. |
```

While you are viewing a teammate, plain text goes to that teammate but built-in slash commands still run in the lead's session.

---

## Step 4: Make the Disagreements Explicit

**Overview:** Two reviewers filing the same line is the interesting case, and averaging their severities destroys the information. Asking for the disagreement rather than a merged number is what keeps it.

**Recipe:**

```text
Before writing anything: for every line two lenses both filed, have the two
teammates message each other and settle whether it is one defect or two. Record
each disagreement with both positions, which one was accepted, and why. If a
teammate concedes, say so and say what convinced it.
```

**Expected Outcome:** real concessions, including one reviewer withdrawing a claim about what can be tested:

```text
Assertability of the missing UseHttpsRedirection at Program.cs:56
  security: no HTTP test can catch it, launchSettings binds http with sslPort 0.
  tests:    WebApplicationFactory exercises the pipeline in-process, so
            "assert 200 and not 307" is a valid test.
  Accepted: tests' position. security conceded outright, having reasoned about a
            deployed request rather than an in-process one.
```

and one that stays unresolved on purpose, because the two lenses were looking at different objects:

```text
Severity of the 204-instead-of-404 on GetById
  Accepted: both, unaveraged. The disclosure vector stays low and the coverage
  gap stays high. Averaging them would have lost the fact that the missing
  assertion is the larger problem.
```

---

## Step 5: Merge Into One Ranked File

**Overview:** Three reports appended is not a review. The deliverable is one ordering, because the only question a reader has is what to fix first.

**Recipe:**

```text
Wait for all teammates to finish, then write review-findings.md in this folder:

- One table of every finding: number, severity, lens, file, line, one sentence.
- Ranked by severity, then by blast radius.
- A contested section with each disagreement, both positions, and which was
  accepted.
- Do not include a finding no reviewer actually reported.
```

**Expected Outcome:** [`review-findings.md`](catalog-service-cs-solution/review-findings.md) opens on the three criticals that compound:

```text
| 1 | critical | security | appsettings.json | 26 | Live Azure SQL admin
credentials sit in plaintext ... |
| 2 | critical | security | Controllers/ConfigController.cs | 25 | cfg.Get<AppConfig>()
binds the whole configuration root and line 26 serves it anonymously ... |
| 4 | critical | performance | Controllers/FoodController.cs | 51 | var item =
GetById(id); is never awaited, so the guard on line 52 is always true ... |
```

and states the chain in one sentence:

```text
The three criticals in ConfigController and appsettings.json compound into one
chain: auth is off by default, so an unauthenticated GET /config returns a live
SQL admin credential over plain HTTP, and the wildcard CORS policy lets any
origin fetch it.
```

Check one before you believe any of them. `Controllers/FoodController.cs` line 51 reads `var item = GetById(id);` with no `await`, so the null guard below it tests a `Task` and never fails.

---

## Step 6: Note What the Team Refused to Do

**Overview:** A review team that runs the code it is reviewing can destroy the thing under review. Reading how the reviewers handled that is worth more than the finding itself.

**Recipe:**

```text
Did any teammate execute the DELETE endpoint to confirm the un-awaited call
fails at runtime? If not, say what you measured instead and why.
```

**Expected Outcome:** the reviewers separate what they read from what they inferred, and say why they stopped:

```text
Row 4 is filed on what was read in the source, not on an observed exception.
All three declined to run the DELETE because it would mutate the checked-in
food.db in a working tree another session may be using. What was measured
instead: bin/Debug/net10.0/catalog-service.dll postdates FoodController.cs, so
the defect compiles clean and ships past CS4014.
```

The finished result is beside the starter in [`catalog-service-cs-solution/`](catalog-service-cs-solution/), holding the team's `review-findings.md`.
