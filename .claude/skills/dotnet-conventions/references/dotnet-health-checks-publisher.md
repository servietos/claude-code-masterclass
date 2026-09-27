# Push-Based Publishing

## Push-based publishing (`IHealthCheckPublisher`)

For monitoring systems that expect the app to push status rather than being polled, register an
`IHealthCheckPublisher` — the health check system runs it on a timer and calls `PublishAsync` with
the aggregated report:

```csharp
public class SampleHealthCheckPublisher : IHealthCheckPublisher
{
    public Task PublishAsync(HealthReport report, CancellationToken cancellationToken)
    {
        // push report.Status / report.Entries to an external monitoring system
        return Task.CompletedTask;
    }
}

builder.Services.Configure<HealthCheckPublisherOptions>(options =>
{
    options.Delay = TimeSpan.FromSeconds(2);      // initial delay after startup (default: 5s)
    options.Period = TimeSpan.FromSeconds(30);    // execution interval (default: 30s)
    options.Predicate = check => check.Tags.Contains("sample");
});

builder.Services.AddSingleton<IHealthCheckPublisher, SampleHealthCheckPublisher>();
```

The community `AspNetCore.HealthChecks.UI` package builds on this pattern to provide a dashboard
that polls multiple services' health endpoints and a `HealthCheckPublisher` for pushing results —
not Microsoft-maintained, evaluate before adopting.

Back to the index: [dotnet-health-checks](dotnet-health-checks.md)
