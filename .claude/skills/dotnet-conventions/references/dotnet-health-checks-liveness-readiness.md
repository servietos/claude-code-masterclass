# Liveness vs. Readiness

## Liveness vs. readiness

Two different questions, worth separating once past a trivial app:

- **Liveness** — "is the process alive and not deadlocked?" Keep cheap and fast; a restart is the
  right response if this fails. Exclude all dependency checks.
- **Readiness** — "can it serve real traffic right now?" (DB reachable, migrations applied, caches
  warm.) A failing readiness check shouldn't trigger a restart — the process is fine, it's just not
  ready yet.

Tag dependency checks `"ready"` and filter by tag per endpoint:

```csharp
app.MapHealthChecks("/health/live", new HealthCheckOptions
{
    Predicate = _ => false                              // exclude everything — liveness only
});

app.MapHealthChecks("/health/ready", new HealthCheckOptions
{
    Predicate = check => check.Tags.Contains("ready")   // only dependency checks
});
```

Point Docker's `HEALTHCHECK` (and container-orchestrator restart policies) at `/health/live`. Point
a load balancer or readiness gate at `/health/ready`. Kubernetes readiness probe example:

```yaml
readinessProbe:
  httpGet:
    path: /health/ready
    port: 80
  initialDelaySeconds: 30
  timeoutSeconds: 1
```

For startup work that must finish before an app is ready (e.g. a slow config download), register a
singleton `IHealthCheck` that a `BackgroundService` flips to healthy on completion, tagged `"ready"`
— don't restart the process while it's still starting up. There's no separate Kubernetes-style
"startup probe" concept in ASP.NET Core health checks — model it as a readiness check instead.

Filtering by multiple tags is OR logic — a check runs if it matches any tag in the predicate:

```csharp
Predicate = check => check.Tags.Contains("foo_tag") || check.Tags.Contains("baz_tag")
```

Back to the index: [dotnet-health-checks](dotnet-health-checks.md)
