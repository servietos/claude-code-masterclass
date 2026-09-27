# Never reach for dotnet ef, including to bootstrap

## Never reach for `dotnet ef`, including to bootstrap

When a project prohibits migrations, the prohibition covers **generating** them, not only committing
them. `dotnet ef migrations script` to extract the DDL "one last time" before deleting the folder is
still using the banned tool, and it was done in this repository and rejected.

To get `CREATE TABLE` statements for tables that do not exist yet, write them from the
`IEntityTypeConfiguration<T>` classes by hand, or script an existing database with SMO or sqlpackage.

Two traps the model sets that only surface at `CREATE TABLE`, both hit in a real run:

- **A raw check constraint is emitted verbatim**, so any reserved word inside it must be bracketed:
  `t.HasCheckConstraint("CK_X_Trigger", "[Trigger] IS NULL OR [Trigger] IN (...)")`. Unbracketed, the
  script dies with `Incorrect syntax near the keyword 'Trigger'`, and the model builds fine until then.
- **A table mapped `ExcludeFromMigrations` is a read-only mirror of another service's table, and the
  foreign key onto it is real.** Two services that mirror each other cannot both be created first, so
  the create order is its own artifact: one own-tables script per service, then a separate
  cross-service constraints script guarded on the referenced table existing. Those mirrors are also a
  co-location constraint: services whose schemas reference each other share ONE database, whatever
  their names suggest. Grep `ExcludeFromMigrations` and cross-schema `principalSchema` before deciding
  how many databases a stack has.

Back to the index: [sql-delta-scripts](sql-delta-scripts.md)
