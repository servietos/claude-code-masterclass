# The rule: hand-written deltas instead of EF migrations

Some projects deliberately do not change a database with EF Core migrations. Every schema and data
change ships as a hand-written SQL delta script, authored once and applied identically to each slot.
Where that rule is in force, `dotnet ef migrations add` and `dotnet ef database update` are not part
of the workflow, and a model change means you write the script.

Check the repo before assuming either way: the presence of a `db/deltas/` folder, or a rule in the
project's `CLAUDE.md` or agent definition, decides it. When the rule is in force, the project's own
skill states where the scripts live and what they are named.

The reason is usually a blue/green topology. Two databases behind two slots, with a
`Database.Migrate()` call at container start, applies schema on whichever slot happens to boot first,
at a moment nobody chose. A script is an artifact you can read, dry run, apply in a chosen order, and
verify by counts.

Back to the index: [sql-delta-scripts](sql-delta-scripts.md)
