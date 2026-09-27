# EF Core: migration commands and database-first baselining

## Migrations

See `dotnet-cli` for the full command reference. Typical workflow:

```bash
dotnet ef migrations add <Name> --project src/my-api
dotnet ef database update --project src/my-api
```

A running app locks its build output exe, so `dotnet build` / `dotnet ef` can fail with
`MSB3027`/`MSB3021` while it is up. When that app is the user's own `dotnet watch run` session, the
lock is not yours to break. It is also not yours to work around by force: the lock covers
`bin/Debug/<tfm>` only, so `-c Release` or `-o <scratch>` builds past it without disturbing anything
(see [`dotnet-cli`](dotnet-cli.md)). Never `taskkill` a watch process you did not start just to get a
green build.

### Adding migrations to a database-first schema (baseline trick)

When a context maps a **pre-existing, database-first** schema (the DB already exists, was never `ef migrations`-managed, and has no `__EFMigrationsHistory` table), you cannot just `migrations add MyChange` — EF diffs against an *empty* model snapshot and emits `CreateTable` for **every** existing table, which would fail against the live DB. To add only the new tables:

1. **`migrations add InitialBaseline`** first — this captures the entire current model in the snapshot/`Designer`. Then **manually empty its `Up()` and `Down()` bodies** (make it a no-op). It exists only to give the next migration a correct diff baseline; applying it just writes a history row.
2. **`migrations add AddMyTables`** next — now diffed against the baseline snapshot, so it contains `CreateTable` for **only** the genuinely new entities.
3. **`database update`** applies InitialBaseline as a no-op history row, then `AddMyTables`' real DDL.

Never remove, reorder, or hand-edit `InitialBaseline` afterward — every future migration must come *after* it. Verify the migration by generating migrations against a throwaway copy of the source tree if the live API/DB must not be disturbed (`ef` builds the project and needs the DLL unlocked).

Back to the index: [dotnet-efcore](dotnet-efcore.md)
