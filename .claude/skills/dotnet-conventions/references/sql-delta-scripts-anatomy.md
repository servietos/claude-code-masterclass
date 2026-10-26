# What every script contains

## What every script contains

1. **A `DB_NAME()` guard, first statement.** `THROW` unless the current database is one this change is
   meant for. A delta applied to the wrong database is the failure this prevents, and it costs two
   lines.
2. **DDL guarded by existence checks.** `IF OBJECT_ID(N'dbo.T') IS NULL CREATE TABLE ...`,
   `IF COL_LENGTH('dbo.T','C') IS NULL ALTER TABLE ...`, indexes behind a `sys.indexes` check. The
   script will be re-run: dev, then each slot, then again after a fix. A filtered index
   (`CREATE INDEX ... WHERE`), an index on a computed column or an indexed view also needs
   `SET QUOTED_IDENTIFIER ON;` in its own batch right after the guard: `sqlcmd -i` connects with it
   OFF, and the create fails with `Msg 1934 ... incorrect settings: 'QUOTED_IDENTIFIER'`.
3. **No surrogate key the script did not create.** Identity and GUID keys differ per database, so a
   literal id targets a different row on the next slot, or nothing. Resolve existing rows by natural
   key at runtime; for rows the script inserts, capture the generated key with `OUTPUT INSERTED ...
   INTO #Map` and join through that map for the dependent tables.
4. **`THROW` on any unresolved lookup**, selecting the offending rows first so the fix is obvious. A
   half-applied change that inserted NULLs is worse than a script that stopped.
5. **Count verification as the closing statements**, one `SELECT` per table with the expected number
   beside the found one. Exit code 0 means the batch parsed, not that the data is right.
6. **A `Reversal:` header line declaring how to get back.** Idempotence is forward-only: a guarded
   script is safe to re-run, which says nothing about undoing what it already did. Every delta states
   its class in a header comment, `-- Reversal: <class>`, one of:
   - `reversible` — guarded DDL/inserts only, undone by a paired forward delta that reverses the
     change (drop what was added, restore what was renamed). The default for additive changes.
   - `reverse-script-required` — ships with a sibling `<name>.reverse.sql`, guarded and verified the
     same way as the forward script.
   - `restore-only` — the script destroys data (`DROP TABLE`, `TRUNCATE TABLE`, `DROP COLUMN`, an
     unguarded `DELETE FROM`) with no scripted way back. The only recovery is a pre-apply copy: the
     per-slot safety backup taken immediately before the delta runs, or the previous night's backup.
     A `restore-only` delta must not be applied to a slot whose pre-apply copy is missing.

   This classifies a delta; it does not retroactively rewrite one that has already been applied to a
   slot; changing the transaction structure of an applied script makes the file on disk stop
   describing what actually ran.
7. **An `AppliedDelta` stamp as the last statement inside the same transaction as the change**, for a
   repo that keeps its own `dbo.AppliedDelta` ledger table (`FileName`, `AppliedAtUtc`, `AppliedBy`):
   `INSERT INTO [dbo].[AppliedDelta] ([FileName], [AppliedAtUtc], [AppliedBy]) SELECT N'<this file's
   name>', SYSUTCDATETIME(), SYSTEM_USER WHERE NOT EXISTS (SELECT 1 FROM [dbo].[AppliedDelta] WHERE
   [FileName] = N'<this file's name>')`. This makes "which deltas has this database actually seen"
   answerable from the database itself instead of only from a hand-maintained readme table, and it
   is idempotent for the same reason every other guarded statement here is: a second run inserts
   nothing because the row already exists.

## Every environment, including the one with no site

Count the databases before writing the guard. A repo usually has more than the environments it
deploys: the integration-test database the xUnit suite connects to is a real target with no site in
front of it, and it is the one that gets forgotten. A delta can apply cleanly to every deployed slot
and still leave the whole test suite failing on `Invalid column name`, which reads as broken code
rather than as a missing apply.

Find them by reading the connection strings, not by listing the environments: the test factory's
constant, `appsettings*.json`, and the deploy env files. Then name all of them in the `DB_NAME()`
guard, and apply to the test database first: it is the cheapest place for the script to be wrong.

A deployed slot's database name comes from the env file on the box itself (`/opt/<stack>/env/*.env`),
never from a repo template or a compose default: the media-creator green slot runs `media-creator`
while every delta guarded on the compose name `media-creator-db`, so each one would `THROW` there.

Back to the index: [sql-delta-scripts](sql-delta-scripts.md)
