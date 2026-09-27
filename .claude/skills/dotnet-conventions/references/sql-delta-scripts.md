# SQL delta scripts instead of EF migrations

Hand-written SQL deltas as the schema workflow: rule, anatomy, seed rows, apply order, proofs.

**A subagent authors the script and never runs it.** Applying to a live database is a main-thread action.

| You want to... | Read |
| --- | --- |
| Know if this repo ships deltas not EF migrations, and why | [rule](sql-delta-scripts-rule.md) |
| Place and name a new delta file and its generator | [layout](sql-delta-scripts-layout.md) |
| Get CREATE TABLE without `dotnet ef`, even to bootstrap | [no-ef-tooling](sql-delta-scripts-no-ef-tooling.md) |
| Write one now: its five parts, and which databases `DB_NAME()` names | [anatomy](sql-delta-scripts-anatomy.md) |
| Stop a boot crash from `Migrations/` and `__EFMigrationsHistory` | [ef-history-coexistence](sql-delta-scripts-ef-history-coexistence.md) |
| Add or change seed rows in a table a generator owns | [seed-rows](sql-delta-scripts-seed-rows.md) |
| Fix `Msg 207, Invalid column name` for a just-added column | [new-column](sql-delta-scripts-new-column.md) |
| Edit a delta that already ran, with per-phase guards | [extending-applied](sql-delta-scripts-extending-applied.md) |
| Apply and deploy per slot, and the `sqlcmd` invocation | [apply-order](sql-delta-scripts-apply-order.md) |
| Prove idempotence and that the prohibition still holds | [verify](sql-delta-scripts-verify.md) |
| Find multi-env scripting, sqlcmd traps, EF model conventions | [related](sql-delta-scripts-related.md) |
