# Diagnosing a Failing Suite

## Diagnosing a Failing Suite

### Get the actual error first

`dotnet test -v q` prints only the `[FAIL]` test names, and `-v n` buries the detail. Neither shows you
the assertion message. Use the console logger explicitly:

```bash
dotnet test <project> --nologo --logger "console;verbosity=detailed"
```

Package-audit and analyzer warnings (`NU1903`, `EF1002`) can flood the output to the point that the
failures scroll away. Filter them, then pull the failure blocks:

```bash
dotnet test <project> --nologo --logger "console;verbosity=detailed" 2>&1 \
  | grep -v "NU1903\|EF1002" | grep -B2 -A 14 "Error Message"
```

### Establish which side is wrong before editing either

A failing test means the test and the production code disagree. It does **not** say which one is right.
Decide per failure, and state the verdict:

| Symptom | Likely wrong side | How to confirm |
|---|---|---|
| Test asserts a field/table the code no longer writes | **Test** — a migration moved the data and the tests were not swept | Find the migration; check whether producers and consumers both moved |
| A sibling test on the adjacent path passes | **Test fixture** — the mock/stub for this path is broken, not the service | Read the fixture's branching, not just the service |
| FK / constraint violation on an in-memory DB | **Production** — a write persists a row referencing something that does not exist | Check whether the caller guards it; an unreachable path is still a defect |
| Library throws on a degenerate input the test deliberately passes | **Production** — the builder does not handle the empty/zero case | Read the library's precondition in the stack trace |

**Never weaken an assertion to reach green.** Relaxing `NotBeNull()`, widening a matcher, or deleting a
case converts a real signal into a silent one. Change an assertion only after establishing that it
encodes an expectation the system deliberately abandoned, and say so explicitly when reporting.

### A permanently-red suite has stopped reporting

Failures that are known, tolerated, and labelled "pre-existing" stop being read. A genuine new regression
in the same area lands in the same red block and is invisible. Treat a standing red count as a defect in
its own right, not as background noise: the cost is not the red rows, it is every future regression they
will hide.

### Delegating a "make the tests pass" task

The cheap path to green is weakening assertions, and an agent optimizing for a passing suite will find it.
Any delegation prompt for test failures must carry:

- Do not weaken an assertion unless you establish that the assertion, not the production code, encodes
  the wrong expectation, and say so explicitly in your report.
- Group the failures by root cause before editing; N failures in one area are frequently not one bug.
- Report per group which side was wrong (test or production) and why.

Back to the index: [dotnet-testing](dotnet-testing.md)
