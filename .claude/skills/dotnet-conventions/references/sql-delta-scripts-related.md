# Related references

## Related

- `~/.claude/skills/sql-server/references/portable-multi-env-migration.md`: the environment-agnostic
  scripting technique in depth, including generator-side injective-mapping asserts for scripts whose
  seed rows come from a data file.
- `~/.claude/skills/sql-server/references/sqlcmd-safe-execution.md`: sqlcmd invocation on Windows,
  UTF-8 fidelity, and COMMIT-to-ROLLBACK dry runs. Two traps bite this kind of script specifically:
  `-b` is load-bearing, because without it a `THROW` in an early batch does not stop the run and
  execution falls through into the DDL, and `-i` needs a backslash path on Windows while piping the
  file on stdin runs and prints nothing.
- [`dotnet-efcore`](dotnet-efcore.md): model and `IEntityTypeConfiguration` conventions, which still
  apply unchanged. Only the migration workflow is replaced.

Back to the index: [sql-delta-scripts](sql-delta-scripts.md)
