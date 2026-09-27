# EF Core: seeding and migration prohibitions

## Hard Rules — Seeding and Migrations

**NEVER add seed data unless explicitly requested by the user.**
Seeding is only valid at initial project setup. Do not add `HasData()` calls, seed methods, or any startup data insertion on your own initiative. Do not add `EnsureMigratedAsync()` or `db.Database.MigrateAsync()` to `Program.cs`.

**NEVER use migrations to insert data.**
Migrations are strictly for schema changes (DDL: tables, columns, indexes, constraints). Do not embed `INSERT`, `UPDATE`, or any DML inside migration `Up()`/`Down()` methods. Data belongs in dedicated seed scripts, delta scripts or import tools — never in migrations and never in application startup.

## When the project prohibits migrations altogether

Some projects ship every schema and data change as a hand-written SQL delta script instead (see
[`sql-delta-scripts`](sql-delta-scripts.md)). Where that rule is in force it is absolute: never
scaffold, generate, script or apply an EF Core migration, and do not reintroduce a `Migrations/`
folder, a `Microsoft.EntityFrameworkCore.Design` package reference, an
`IDesignTimeDbContextFactory<T>`, or a `Database.Migrate()` / `EnsureCreated()` call, including "just
once" to extract DDL or to baseline a database-first schema. Deltas live under the repository's delta
folder, which belongs at the REPOSITORY ROOT and not inside the .NET project (typically
`db/<service>/deltas/`, named `YYYY-MM-DD-<change>.sql`; a Python generator beside a `.csproj` is the
smell that says the tree is in the wrong place).

To get `CREATE TABLE` statements for tables that do not exist yet in such a project, write them by
hand from the `IEntityTypeConfiguration<T>` classes, or script an existing database with SMO or
sqlpackage. Never `dotnet ef`. Everything else in this file (model configuration, context
registration, query patterns, splitting a model across services) still applies unchanged; only the
migration workflow is replaced.

Back to the index: [dotnet-efcore](dotnet-efcore.md)
