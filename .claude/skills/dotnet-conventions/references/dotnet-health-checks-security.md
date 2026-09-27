# Securing a Health Endpoint

## Security

A health endpoint can leak internal details (dependency names, exception messages via a custom
`ResponseWriter`). For anything beyond a bare liveness check, either restrict `/health/ready` to
internal network access or gate it behind auth:

```csharp
app.MapHealthChecks("/health/ready", readinessOptions).RequireAuthorization();
```

Keep `/health/live` anonymous and cheap — orchestrators need to reach it without a token.

`RequireHost` alone isn't a security boundary — `HttpRequest.Host` is client-supplied and can be
spoofed. If restricting a health endpoint to a specific port, chain `RequireAuthorization()` after
it rather than relying on the host/port match alone:

```csharp
app.MapHealthChecks("/healthz")
    .RequireHost("*:5001")
    .RequireAuthorization();
```

Back to the index: [dotnet-health-checks](dotnet-health-checks.md)
