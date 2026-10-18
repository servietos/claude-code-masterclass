# Capture a Planning Session in STATE.md

A statefile is dictated section by section: you name the headings and Claude fills only content that `plan.md` and your constraints actually support. You write `STATE.md` in the HR MCP server starter with Goal, Decisions, Status, Next Action, Done Criteria and Open Questions, then close the one question Claude could not answer from its sources.

------

Run this in the [hr-mcp-server/](hr-mcp-server) starter after [demo-plan-vacancies.md](demo-plan-vacancies.md), whose corrected `plan.md` is the input; the finished statefile is in [hr-mcp-server-solution/STATE.md](hr-mcp-server-solution/STATE.md).

## Dictate the Statefile Sections

Fix the structure yourself and leave Claude only the content `plan.md` and the constraints support:

```text
Write STATE.md in this folder with exactly these sections:

## Goal
Add vacancies to the HR MCP server.

## Decisions
[every decision plan.md and the constraints below lock in: the vacancy fields, the four tool names, storage through EmployeeDbContext with no new packages, how the Vacancies table reaches an existing hr-data.db, the ranking rule for match_candidates]

## Status
- [ ] vacancy schema
- [ ] vacancy service
- [ ] vacancy tools
- [ ] smoke verification

## Next Action
vacancy schema

## Done Criteria
- npx @modelcontextprotocol/inspector --cli --config inspector.config.json --server hr-mcp --method tools/list lists add_vacancy, list_vacancies, close_vacancy and match_candidates beside the 5 employee tools
- the same CLI with --method tools/call --tool-name list_employees still returns the 8 seeded employees
- match_candidates for a vacancy requiring "Menu Planning, Food Safety" returns Carlos Gomez first

## Open Questions
[anything plan.md and the constraints leave undecided; leave it empty if nothing is]

Use plan.md and these constraints as the source of truth. Do not invent new decisions.

Constraints (non-negotiable):
  1. A vacancy has a title, required skills, required languages and a status of open or filled.
  2. Four new MCP tools: add_vacancy, list_vacancies, close_vacancy, match_candidates.
  3. Store vacancies in the existing SQLite database through EmployeeDbContext. No new NuGet packages.
  4. Existing employee rows in hr-data.db must survive. No destructive migration.
  5. match_candidates returns employees ranked by how many required skills they have.
```

The headings come back literally, in the dictated order, and Goal, Status, Next Action and Done Criteria are copied word for word. Decisions is the section to read: in the recorded run every bullet traced to `plan.md` or a constraint, including the `CREATE TABLE IF NOT EXISTS Vacancies` the existing `hr-data.db` depends on.

Open Questions came back with six items; the first, the tie order, is one neither source settles:

```markdown
## Open Questions
- Where the `CREATE TABLE IF NOT EXISTS` runs in `Data/EmployeeDbInitializer.cs`. The initializer returns early when the employee table is not empty, so the statement has to run before that return for an existing seeded database to receive the table. plan.md does not place it.
- Tie-breaking when two employees hold the same number of required skills. Neither plan.md nor the constraints order them.
- The output shape of `match_candidates`. `EmployeeCollection` holds only the employees, so the matched count is not returned unless a new type is added. plan.md does not decide this.
- Whether the readme smoke test is updated for the vacancy tools (plan.md task 6 asks, and flags it as a documentation decision).
- Title maximum length. plan.md says a max length applies but gives no value.
- Whether the seeded employees hold the skills "Menu Planning" and "Food Safety". The ledger records no seed skill values, so the Carlos Gomez done criterion cannot be checked from it.
```

## Close the Open Question

An open question in the statefile is a decision the executing session would otherwise make for you. Close it with one constraint line:

```text
Close the open question in STATE.md: employees with the same match count keep the order list_employees already returns. Move that into Decisions, leave Open Questions empty, and change nothing else.
```

The recorded run moved the tie answer into Decisions and emptied all of Open Questions, the five other items included:

```diff
+- Ties in `match_candidates`: employees with the same match count keep the order that `list_employees` returns.
...
-- Tie-breaking when two employees hold the same number of required skills. Neither plan.md nor the constraints order them.
...
```

Read the result before moving on: every Decisions bullet must trace to `plan.md` or a constraint, and Open Questions must be empty.
