# Response Options and Custom JSON

## Health check options

```csharp
app.MapHealthChecks("/health", new HealthCheckOptions
{
    Predicate = check => check.Tags.Contains("sample"),   // filter which checks run
    ResultStatusCodes =
    {
        [HealthStatus.Healthy] = StatusCodes.Status200OK,
        [HealthStatus.Degraded] = StatusCodes.Status200OK,
        [HealthStatus.Unhealthy] = StatusCodes.Status503ServiceUnavailable
    },
    AllowCachingResponses = false   // default: sets Cache-Control/Expires/Pragma to prevent caching
});
```

## Custom JSON response

By default `/health` returns a plain `Healthy`/`Unhealthy`/`Degraded` string. For a richer response
(useful if a dashboard consumes it directly):

```csharp
app.MapHealthChecks("/health", new HealthCheckOptions
{
    ResponseWriter = async (context, report) =>
    {
        context.Response.ContentType = "application/json";
        var payload = new
        {
            status = report.Status.ToString(),
            checks = report.Entries.Select(e => new
            {
                name = e.Key,
                status = e.Value.Status.ToString(),
                description = e.Value.Description,
                duration = e.Value.Duration
            })
        };
        await context.Response.WriteAsync(JsonSerializer.Serialize(payload));
    }
});
```

Back to the index: [dotnet-health-checks](dotnet-health-checks.md)
