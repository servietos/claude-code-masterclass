# Reconciling a delta with EF migrations already in the tree

## Reconciling a delta with EF migrations already in the tree

This section applies only while a `Migrations/` folder and a `Database.Migrate()` call still exist.
Once they are deleted, a delta owns the schema outright and must NOT write to
`__EFMigrationsHistory`; any surviving copy of that table is read-only history of what was applied
before the rule, and a new script guards on the object it touches instead.

This is the part that is easy to miss and fails loudly at the worst moment. A project that adopts the
rule mid-life still has old migrations on disk and often still calls `ctx.Database.Migrate()` at
startup. If a delta creates tables that a migration also describes, EF finds that `MigrationId`
absent from `__EFMigrationsHistory`, tries to `CREATE TABLE` again, and the application crashes on
boot against a table the script already made.

So a delta that replaces a migration ends by marking that migration applied:

```sql
DECLARE @ProductVersion nvarchar(32) =
    (SELECT TOP 1 h.[ProductVersion] FROM [__EFMigrationsHistory] h ORDER BY h.[MigrationId] DESC);
INSERT INTO [__EFMigrationsHistory] ([MigrationId], [ProductVersion])
SELECT N'<the migration id>', @ProductVersion
WHERE NOT EXISTS (SELECT 1 FROM [__EFMigrationsHistory] h WHERE h.[MigrationId] = N'<the migration id>');
```

Read `ProductVersion` from the table at runtime rather than hardcoding it. The value is also written
into every `*.Designer.cs` and into the model snapshot, so those files tell you what it should be,
but a row you read is evidence and a designer file is inference. Confirm against a real row before
applying anywhere.

Guard the whole script with a second check that `__EFMigrationsHistory` exists at all: its absence
means the target is not the database you think it is.

Back to the index: [sql-delta-scripts](sql-delta-scripts.md)
