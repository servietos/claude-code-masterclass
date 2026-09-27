# Registering a Health Endpoint

## Package

`Microsoft.Extensions.Diagnostics.HealthChecks` — part of the shared framework since .NET 6, no
extra NuGet package needed for the basics.

## Basic probe

```csharp
var builder = WebApplication.CreateBuilder(args);

builder.Services.AddControllers();          // existing controllers, unaffected
builder.Services.AddHealthChecks();

var app = builder.Build();

app.MapControllers();
app.MapHealthChecks("/health");

app.Run();
```

Classic `Startup.cs` wiring is the same shape: `services.AddHealthChecks()` in
`ConfigureServices`, `endpoints.MapHealthChecks("/health")` inside `UseEndpoints` in `Configure`.

With no checks registered, the app is "healthy" if it can respond at all — this alone satisfies a
basic Docker `HEALTHCHECK`.

## `MapHealthChecks` vs. `UseHealthChecks`

| | `MapHealthChecks` (routing) | `UseHealthChecks` (middleware) |
|---|---|---|
| Where | Endpoint, evaluated with other routes | Anywhere in the pipeline, before routing |
| Auth | Composable — `app.MapHealthChecks("/health").RequireAuthorization()` | Not endpoint-aware |
| Multiple endpoints | Yes — call it once per path/tag combination | Awkward |
| Short-circuit | `app.MapHealthChecks("/health").ShortCircuit()` | Always terminates the pipeline on match |

Default to `MapHealthChecks` — it composes with `RequireAuthorization()` and other endpoint
metadata, and supports mapping multiple tagged endpoints cleanly. Only reach for `UseHealthChecks`
when a health check must run in front of routing (rare).

Back to the index: [dotnet-health-checks](dotnet-health-checks.md)
