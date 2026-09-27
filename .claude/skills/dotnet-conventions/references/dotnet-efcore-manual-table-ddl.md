# EF Core: hand-creating a table a migration owns

### Hand-creating a table an EF migration owns

Sometimes one environment's database needs a table before that environment's API image ships — for
example a blue/green pair where the candidate slot has the migration applied and the live slot does
not yet. If you create the table with raw DDL, you **must write the `__EFMigrationsHistory` row in the
same transaction**:

```sql
IF NOT EXISTS (SELECT 1 FROM dbo.__EFMigrationsHistory WHERE MigrationId = '<stamp>_<Name>')
    INSERT INTO dbo.__EFMigrationsHistory (MigrationId, ProductVersion)
    VALUES ('<stamp>_<Name>', '<version copied from the database that already has it>');
```

Without that row, the next `Database.Migrate()` re-runs `CreateTable` against a table that already
exists and **the application fails to start**. Rules:

- Transcribe the DDL from the migration's `Up()` verbatim: identity seed, column types *and* lengths,
  PK name, FK name, cascade behaviour, index name. A table that differs from what EF would have built
  is a silent model/schema mismatch later.
- Copy `ProductVersion` from the database that already has the migration; do not invent it.
- Guard the script with `IF DB_NAME() <> '<target>' RAISERROR(...)` so it cannot hit the wrong database.
- Verify parity afterwards by diffing `sys.columns` / `sys.indexes` / `sys.foreign_keys` between the two
  databases, not by reading the script back.

An extra history row is harmless for an older image whose assembly does not contain that migration —
EF only compares history against the migrations present in the assembly. For the sqlcmd mechanics
(dry runs, guards, structure diffing) see the `sql-server` skill, `sqlcmd-safe-execution` reference.

Back to the index: [dotnet-efcore](dotnet-efcore.md)
