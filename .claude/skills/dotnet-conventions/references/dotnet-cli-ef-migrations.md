# dotnet CLI: EF Core migrations, and where they are banned

## EF Core Migrations

| Command | Description |
|---|---|
| `dotnet ef migrations add <Name>` | Scaffold a new migration |
| `dotnet ef database update` | Apply pending migrations to the database |
| `dotnet ef migrations remove` | Remove the last unapplied migration |

Prefix with `--project <path>` when running from the solution root:

```bash
dotnet ef migrations add AddIndexTable --project src/my-api
dotnet ef database update --project src/my-api
```

Apply against a Release build/output (`--configuration Release`) rather than the `bin/Debug` output a
running API holds locked.

**Some projects prohibit `dotnet ef` outright.** Where schema and data changes ship as hand-written
SQL delta scripts (typically a blue/green topology with a `db/<project>/deltas/` folder), none of
`migrations add`, `migrations script`, `migrations remove`, `database update` or `dbcontext scaffold`
may be run, in any project, for any reason: not even once to extract DDL or to baseline a
database-first schema. Check the repo's `CLAUDE.md` and its own skill before running any of them, and
see [`sql-delta-scripts`](sql-delta-scripts.md).

Back to the index: [dotnet-cli](dotnet-cli.md)
