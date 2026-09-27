# EF Core: condensing a migration chain

### Condensing many migrations into one

Squashing an accumulated migration chain back to a single file is safe **only if the consolidated
migration inherits the id of a migration the deployed databases have already applied** — normally the
first one. Regenerating with a fresh timestamp instead makes every existing database treat it as
pending, so the next `Database.Migrate()` runs `CreateTable` for every table against a populated
schema and the application fails to start.

```bash
# 0. back up the folder, and stop the app (it locks the output exe)
cp -r src/my-api/Migrations <scratch>/migrations-backup
taskkill //F //IM my-api.exe

# 1. clear the folder — migration files AND the model snapshot
rm -f src/my-api/Migrations/*.cs

# 2. regenerate the whole model as one migration (gets a new timestamp)
dotnet ef migrations add InitialBaseline --project src/my-api

# 3. retag it with the id the live databases already have
cd src/my-api/Migrations
mv <new>_InitialBaseline.cs          <old>_InitialBaseline.cs
mv <new>_InitialBaseline.Designer.cs <old>_InitialBaseline.Designer.cs
sed -i 's/\[Migration("<new>_InitialBaseline")\]/[Migration("<old>_InitialBaseline")]/' <old>_InitialBaseline.Designer.cs
```

Then verify, in this order, and do not trust the change until all three pass:

| Check | Expected |
| --- | --- |
| `dotnet ef migrations list` | one entry, **not** marked `(Pending)` |
| `dotnet ef migrations has-pending-model-changes` | "No changes have been made to the model since the last migration." |
| Application startup log | `No migrations were applied. The database is already up to date.` |

Notes that matter:

- **Leave the orphaned history rows alone.** Deployed databases keep a `__EFMigrationsHistory` row per
  squashed migration. EF computes pending as (migrations in the assembly) minus (rows in history), so
  rows with no matching migration are ignored. Deleting them is a write against a live database and
  needs the user's say-so; it buys tidiness, nothing else.
- **A hard-coded baseline id in startup code must still resolve.** If an initializer stamps a constant
  `BaselineMigrationId` onto out-of-band databases, reusing that same id is what keeps it valid.
  Reusing a *different* id silently breaks the stamp.
- **Classify each migration before dropping it.** Schema DDL and `HasData` seeds are regenerated from
  the model. Hand-written DML in `migrationBuilder.Sql()` / `InsertData` is genuinely lost, which is
  fine only when it repairs rows a new database will not have. Grep the regenerated migration for the
  `InsertData` calls you expect.
- This is the one sanctioned exception to "never hand-edit `InitialBaseline`" above: the id is
  preserved precisely so the ordering guarantee still holds.

Back to the index: [dotnet-efcore](dotnet-efcore.md)
