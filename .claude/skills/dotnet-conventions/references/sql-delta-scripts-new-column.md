# Adding a column and using it in the same script

## Adding a column and using it in the same script

SQL Server compiles a whole batch before executing any of it, and deferred name resolution does not
cover a column added earlier in that same batch. So an `ALTER TABLE ... ADD [NewCol]` followed by
anything that names `NewCol` fails to compile, and the script dies on `Msg 207, Invalid column name`
before a single statement runs. This bites the backfill, any `CHECK` constraint over the new column,
any index on it, and any verification `SELECT` that has not been pushed past the final `GO`.

`GO` is not the way out: it ends the explicit transaction the delta is wrapped in. Route every
statement that names the new column through `EXEC sp_executesql`, which compiles at execution time:

```sql
BEGIN TRANSACTION;

IF COL_LENGTH(N'MyTable', N'ApprovalState') IS NULL
BEGIN
    ALTER TABLE [MyTable]
        ADD [ApprovalState] nvarchar(20) NOT NULL
            CONSTRAINT [DF_MyTable_ApprovalState] DEFAULT N'Pending';

    EXEC sp_executesql N'
        UPDATE [MyTable] SET [ApprovalState] = N''Approved'';';
END;

IF NOT EXISTS (SELECT 1 FROM sys.check_constraints WHERE [name] = N'CK_MyTable_ApprovalState')
BEGIN
    EXEC sp_executesql N'
        ALTER TABLE [MyTable]
            ADD CONSTRAINT [CK_MyTable_ApprovalState]
                CHECK ([ApprovalState] IN (N''Pending'', N''Approved'', N''Rejected''));';
END;

COMMIT TRANSACTION;
GO
```

Putting the backfill inside the column-creation branch is deliberate beyond the compile problem: it
runs on the first application only, so a re-run cannot undo a state a person has since changed.

A backfill that marks existing rows as already-approved, already-migrated or already-whatever is how
a new gate is introduced without anything disappearing from a live system. State that in the script's
header comment, because it is the sentence a later reader needs and the one the diff does not carry.

Back to the index: [sql-delta-scripts](sql-delta-scripts.md)
