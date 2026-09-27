# Dependency Probes and Custom Checks

## Dependency checks (DB, downstream services)

A "the process is up" check is weaker than "the process can actually do its job":

```csharp
builder.Services.AddHealthChecks()
    .AddSqlServer(
        connectionString: builder.Configuration.GetConnectionString("DefaultConnection")!,
        name: "sql-server",
        tags: ["ready"])
    .AddUrlGroup(new Uri("https://api.example.com/ping"), name: "downstream-api", tags: ["ready"]);
```

`AddSqlServer` comes from the community `AspNetCore.HealthChecks.SqlServer` package (not
Microsoft-maintained) and runs `SELECT 1` — keep the probe query trivial; don't run anything that
could add load to the database.

For EF Core, prefer the first-party `Microsoft.Extensions.Diagnostics.HealthChecks.EntityFrameworkCore`
package instead — it calls `DbContext.CanConnectAsync()`:

```csharp
builder.Services.AddDbContext<AppDbContext>(options =>
    options.UseSqlServer(builder.Configuration.GetConnectionString("DefaultConnection")));

builder.Services.AddHealthChecks()
    .AddDbContextCheck<AppDbContext>(tags: ["ready"]);
```

`AspNetCore.HealthChecks.*` community packages exist for Postgres, MySQL, Redis, RabbitMQ, and
most common dependencies.

## Custom checks

```csharp
public class QueueDepthHealthCheck : IHealthCheck
{
    public Task<HealthCheckResult> CheckHealthAsync(
        HealthCheckContext context, CancellationToken ct = default)
    {
        var depth = GetQueueDepth();
        return Task.FromResult(depth < 10_000
            ? HealthCheckResult.Healthy($"Queue depth: {depth}")
            : HealthCheckResult.Degraded($"Queue depth high: {depth}"));
    }
}

builder.Services.AddHealthChecks()
    .AddCheck<QueueDepthHealthCheck>("queue-depth", tags: ["ready"]);
```

`CheckHealthAsync` returns `Healthy`, `Degraded`, or `Unhealthy`. A check can also consume DI —
inject config or options into the `IHealthCheck` implementation's constructor when the probe needs
more than what a static delegate can capture.

Back to the index: [dotnet-health-checks](dotnet-health-checks.md)
