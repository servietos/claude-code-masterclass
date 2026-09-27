# EF Core: context registration and query patterns

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

## Query Patterns

| Pattern | Code |
|---|---|
| Read all (no tracking) | `await db.Items.AsNoTracking().ToListAsync()` |
| Read by primary key | `await db.Items.FindAsync(id)` |
| Filtered read | `await db.Items.AsNoTracking().Where(i => i.Name == name).ToListAsync()` |
| Add and save | `db.Items.Add(entity); await db.SaveChangesAsync()` |
| Remove and save | `db.Items.Remove(entity); await db.SaveChangesAsync()` |

Always use `AsNoTracking()` for read-only queries to reduce memory overhead and avoid unintended change tracking.

Back to the index: [dotnet-efcore](dotnet-efcore.md)
