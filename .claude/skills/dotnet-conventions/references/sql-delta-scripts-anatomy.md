# What every script contains

## What every script contains

1. **A `DB_NAME()` guard, first statement.** `THROW` unless the current database is one this change is
   meant for. A delta applied to the wrong database is the failure this prevents, and it costs two
   lines.
2. **DDL guarded by existence checks.** `IF OBJECT_ID(N'dbo.T') IS NULL CREATE TABLE ...`,
   `IF COL_LENGTH('dbo.T','C') IS NULL ALTER TABLE ...`, indexes behind a `sys.indexes` check. The
   script will be re-run: dev, then each slot, then again after a fix.
3. **No surrogate key the script did not create.** Identity and GUID keys differ per database, so a
   literal id targets a different row on the next slot, or nothing. Resolve existing rows by natural
   key at runtime; for rows the script inserts, capture the generated key with `OUTPUT INSERTED ...
   INTO #Map` and join through that map for the dependent tables.
4. **`THROW` on any unresolved lookup**, selecting the offending rows first so the fix is obvious. A
   half-applied change that inserted NULLs is worse than a script that stopped.
5. **Count verification as the closing statements**, one `SELECT` per table with the expected number
   beside the found one. Exit code 0 means the batch parsed, not that the data is right.

## Every environment, including the one with no site

Count the databases before writing the guard. A repo usually has more than the environments it
deploys: the integration-test database the xUnit suite connects to is a real target with no site in
front of it, and it is the one that gets forgotten. A delta can apply cleanly to every deployed slot
and still leave the whole test suite failing on `Invalid column name`, which reads as broken code
rather than as a missing apply.

Find them by reading the connection strings, not by listing the environments: the test factory's
constant, `appsettings*.json`, and the deploy env files. Then name all of them in the `DB_NAME()`
guard, and apply to the test database first: it is the cheapest place for the script to be wrong.

Back to the index: [sql-delta-scripts](sql-delta-scripts.md)
