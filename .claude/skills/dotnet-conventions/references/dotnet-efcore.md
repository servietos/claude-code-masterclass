# EF Core Patterns

Reference for EF Core 10 usage: configuration, context registration, migrations, and query patterns.

**NEVER add seed data unless explicitly requested by the user.**
**NEVER use migrations to insert data.**

| You want to... | Read |
| --- | --- |
| Adding seed data, or a project where every schema change ships as a hand-written SQL delta and dotnet ef is banned. | [bans](dotnet-efcore-seeding-and-migration-bans.md) |
| Configuring an entity (keys, lengths, a one-to-one whose PK is the FK) and where OnModelCreating applies them. | [entity-config](dotnet-efcore-entity-configuration.md) |
| Registering AppDbContext with a connection string, or a read, add or remove query with AsNoTracking(). Also: aggregating a header/detail schema by month, quarter or year, when a monthly total is wrong, a row is missing from a period, or two reports over the same data disagree. Also: moving an in-memory aggregate into SQL with a byte-identical response (decimal scale 0 vs 0.00, latest row per group, tie order). Also: a write that must be rejected when a derived value (a recomputed time, a total) breaks a rule: validate on an in-memory preview before saving, never save then delete. Also: a Guid id compared as a string never matches because `ToString()` ran in SQL and came back uppercase. | [context-queries](dotnet-efcore-context-and-queries.md) |
| dotnet ef migrations add: commands, an MSB3027/MSB3021 lock from a running app, or CreateTable emitted for every existing table. | [migrations](dotnet-efcore-migrations-workflow.md) |
| Squashing a migration chain into one file without every deployed database treating it as pending and failing startup. | [squash](dotnet-efcore-migrations-squash.md) |
| One environment needs a table before its API image ships (blue/green): raw DDL plus the __EFMigrationsHistory row. | [manual-ddl](dotnet-efcore-manual-table-ddl.md) |
| Turning one entity model into two or three services: the boundary, cross-area foreign keys, guarding the partition. | [model-split](dotnet-efcore-model-split.md) |
