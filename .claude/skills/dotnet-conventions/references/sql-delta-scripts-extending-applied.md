# Extending a delta that has already been applied

## Extending a delta that has already been applied

The default is a new file: a script that ran is history, and editing it makes the tree disagree with
every database that already took it. The one exception is a migration whose later phase belongs to the
same change as its earlier one (an id column that turns out to need a sibling id turned too), where two
files would leave a half-migrated schema representable. Extend the original only under one condition:

**Each phase carries its own guard, on its own target's real type, so a re-run skips exactly what is
already applied.** Not one guard at the top of the file. A run against a database that took phase 1
prints `Already applied: ... skipping the list id migration.` and proceeds into phase 2, while a fresh
database runs both. That is what makes the extended file honest for the dev box, the test database and
every slot at once.

```sql
IF EXISTS (SELECT 1 FROM sys.columns c
           INNER JOIN sys.types t ON t.user_type_id = c.user_type_id
           WHERE c.object_id = OBJECT_ID(N'dbo.SecretLists') AND c.name = N'ListId'
             AND t.name = N'uniqueidentifier')
BEGIN
    PRINT 'Already applied: dbo.SecretLists.ListId is a uniqueidentifier. Skipping the list id migration.';
    SET NOEXEC ON;
END
GO
```

**Wrap every statement that names a transient column in `sp_executesql`.** A batch is parsed as a whole
before any of it runs, so a statement referencing a column that a *skipped* phase would have created
fails at compile time even though it would never execute. Deferred name resolution covers a missing
table, never a missing column. The string form is what lets one file be correct on both a fresh database
and one mid-migration.

Prove it the way the phases claim: drop and rebuild the test database from the full apply order, and run
the extended file a second time against the already-migrated dev database. Both must be clean, and the
closing `SELECT` must show the same row counts and zero orphans it showed the first time.

Back to the index: [sql-delta-scripts](sql-delta-scripts.md)
