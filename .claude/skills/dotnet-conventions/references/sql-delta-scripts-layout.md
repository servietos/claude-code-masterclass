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

Back to the index: [sql-delta-scripts](sql-delta-scripts.md)
