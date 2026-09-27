# Proving this still holds

## Proving this still holds

Run the script a second time against the slot you applied it to first. Every `RowsFound` must equal
the `RowsExpected` beside it and must not have moved from the first run. Where the project still has
migrations in the tree, `SELECT COUNT(*) FROM __EFMigrationsHistory WHERE MigrationId = N'<the
migration id>'` must return 1, not 2. If the counts move or the history row duplicates, the script is
not idempotent and the guards described above are missing or misplaced.

Prove the prohibition itself the same way, from the repository root:

```bash
grep -rn "Database\.Migrate\|EnsureCreated\|EntityFrameworkCore\.Design\|IDesignTimeDbContextFactory"   --include="*.cs" --include="*.csproj" src/ | grep -v "/obj/\|/bin/"
find src -type d -name Migrations | grep -v "/obj/\|/bin/"
```

Both must return nothing. A project that prohibits migrations but still carries the Design package or
a design-time factory is one `dotnet ef` away from a violation, and the artifact reads to the next
session as permission.

Back to the index: [sql-delta-scripts](sql-delta-scripts.md)
