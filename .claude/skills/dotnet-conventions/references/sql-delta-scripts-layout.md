# Where the scripts live

## Where the scripts live

Database artifacts belong in `db/` at the REPOSITORY ROOT, one directory per service, never inside
the .NET project directory:

```
db/<service>/
  readme.md                            the rule and the apply order
  deltas/YYYY-MM-DD-<change-name>.sql  one file per change, named by the date it was authored
  generate-<change-name>.py            optional, when the seed rows come from a data file
```

A delta whose rows come from a JSON or spreadsheet source gets its generator committed beside it, so
the script is regenerated when the source changes rather than hand-patched. That generator is
typically Python, which is the concrete reason the tree sits outside the project: a `.csproj`
directory with a `.py` file and a `__pycache__` in it is wrong on sight, and it was removed from one
repo for exactly that.


## `create-schema.sql` is a second target, not a historical file

Where the repo also ships a `db/<service>/create-schema.sql` that builds the database from empty, a
delta is only half a change: the same guarded DDL goes into `create-schema.sql` in the same commit.
The reason is not tidiness. A test project whose scratch fixture bootstraps from
`create-schema.sql` + `load-data.sql` (never from `deltas/`) sees a database missing every table the
deltas added, so the new tables' integration tests cannot run and, worse, a PREVIOUS session's
un-backported delta leaves a block of failures that the next session reads as "pre-existing, not
mine" and steps around. That is how `secrets-mcp` reached 29 failing tests: one delta added
Apps/Settings and never touched `create-schema.sql`.

Seed rows are the delta's alone; only the DDL is mirrored. Check for the file before writing the
delta, and if you find the fixture already broken by an earlier delta, say so rather than adding a
second layer of it.

Back to the index: [sql-delta-scripts](sql-delta-scripts.md)
