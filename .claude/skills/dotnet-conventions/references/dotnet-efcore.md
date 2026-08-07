# EF Core Patterns

Reference for EF Core 10 usage: configuration, context registration, migrations, and query patterns.

## Hard Rules — Seeding and Migrations

**NEVER add seed data unless explicitly requested by the user.**
Seeding is only valid at initial project setup. Do not add `HasData()` calls, seed methods, or any startup data insertion on your own initiative. Do not add `EnsureMigratedAsync()` or `db.Database.MigrateAsync()` to `Program.cs`.

**NEVER use migrations to insert data.**
Migrations are strictly for schema changes (DDL: tables, columns, indexes, constraints). Do not embed `INSERT`, `UPDATE`, or any DML inside migration `Up()`/`Down()` methods. Data belongs in dedicated seed scripts or import tools — not migrations.

## Entity Configuration

Use `IEntityTypeConfiguration<T>` for all model configuration. Never place data annotations on domain model classes.

```csharp
public class ItemConfiguration : IEntityTypeConfiguration<Item>
{
    public void Configure(EntityTypeBuilder<Item> builder)
    {
        builder.HasKey(i => i.Id);
        builder.Property(i => i.Name).IsRequired().HasMaxLength(200);
    }
}
```

Apply in `OnModelCreating`:

```csharp
protected override void OnModelCreating(ModelBuilder modelBuilder)
{
    modelBuilder.ApplyConfigurationsFromAssembly(typeof(AppDbContext).Assembly);
}
```

## Context Registration

```csharp
builder.Services.AddDbContext<AppDbContext>(options =>
    options.UseSqlServer(builder.Configuration.GetConnectionString("App")));
```

Connection string in `appsettings.json`:

```json
"ConnectionStrings": {
  "App": "Server=localhost;Database=mydb;Trusted_Connection=True;"
}
```

## Migrations

See `dotnet-cli` for the full command reference. Typical workflow:

```bash
dotnet ef migrations add <Name> --project src/my-api
dotnet ef database update --project src/my-api
```

### Adding migrations to a database-first schema (baseline trick)

When a context maps a **pre-existing, database-first** schema (the DB already exists, was never `ef migrations`-managed, and has no `__EFMigrationsHistory` table), you cannot just `migrations add MyChange` — EF diffs against an *empty* model snapshot and emits `CreateTable` for **every** existing table, which would fail against the live DB. To add only the new tables:

1. **`migrations add InitialBaseline`** first — this captures the entire current model in the snapshot/`Designer`. Then **manually empty its `Up()` and `Down()` bodies** (make it a no-op). It exists only to give the next migration a correct diff baseline; applying it just writes a history row.
2. **`migrations add AddMyTables`** next — now diffed against the baseline snapshot, so it contains `CreateTable` for **only** the genuinely new entities.
3. **`database update`** applies InitialBaseline as a no-op history row, then `AddMyTables`' real DDL.

Never remove, reorder, or hand-edit `InitialBaseline` afterward — every future migration must come *after* it. Verify the migration by generating migrations against a throwaway copy of the source tree if the live API/DB must not be disturbed (`ef` builds the project and needs the DLL unlocked).

## Query Patterns

| Pattern | Code |
|---|---|
| Read all (no tracking) | `await db.Items.AsNoTracking().ToListAsync()` |
| Read by primary key | `await db.Items.FindAsync(id)` |
| Filtered read | `await db.Items.AsNoTracking().Where(i => i.Name == name).ToListAsync()` |
| Add and save | `db.Items.Add(entity); await db.SaveChangesAsync()` |
| Remove and save | `db.Items.Remove(entity); await db.SaveChangesAsync()` |

Always use `AsNoTracking()` for read-only queries to reduce memory overhead and avoid unintended change tracking.
