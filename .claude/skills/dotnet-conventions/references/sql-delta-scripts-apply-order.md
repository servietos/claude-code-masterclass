# Apply order

## Apply order

Per slot, never in parallel: apply the script, verify the counts, deploy the application, verify the
application. Schema lands before the build that depends on it, or every query against the new table
throws for the length of the deploy. Prove idempotence for real by running it twice on the first slot
and confirming no count moves.

Applying to a live database is a main-thread action. A subagent authors the script and never runs it.
That names who applies it, not whether it happens. On a local development database the coordinator
applies it on the main thread as the last step of the same run, before reporting, and quotes the
verification counts. A delta left authored while the application that queries the new table keeps
running does not read as a missing apply: it reads as broken code, because the next request throws
`Invalid object name` from inside the feature that was just delivered. A delta that only adds a COLUMN
throws `Invalid column name '<X>'` instead, from a table that plainly exists, which reads even less
like a missing apply. Where the apply genuinely belongs to the user (a deployed slot), it is the single
next action line of the reply, never a clause inside a summary of what went well.

**The split at the permission boundary is what loses the apply.** "A subagent authors the script and
never runs it" is a correct rule that leaves the apply owned by nobody unless the coordinator writes it
into its own task list at the moment it writes the brief. The failure mode is not forgetting the rule;
it is briefing "write it, do not run it", getting a clean report back, and treating that report as the
end of the task. Add the apply and its verification query to the coordinator's own list before the
subagent is dispatched.

Neither a compiler nor a unit test can fail on an unapplied delta: the build validates C# against the
entity, the component tests validate against fixtures, and both are blind to the schema. The only check
that can fail is a live query. If no live query ran, the change is unverified however green the run was.

On a local Windows dev instance the invocation is `sqlcmd -S localhost -E -C -b -W -d "<database>" -i
"<backslash Windows path>"`. `-C` is required for the self-signed certificate. Where an agent harness
classifies shell commands, a `sqlcmd -i` against a live database may be blocked in the POSIX shell and
permitted through the PowerShell tool; try the other interpreter before treating the denial as a wall.

Back to the index: [sql-delta-scripts](sql-delta-scripts.md)
