# Health Checks in ASP.NET Core

Reference for adding real `/health` endpoints — liveness, readiness, and dependency probes —
independent of hosting style (minimal hosting vs. `Startup.cs`) or endpoint style (minimal APIs
vs. MVC controllers). Health checks work identically across all four combinations.

| You want to... | Read |
| --- | --- |
| Add /health; MapHealthChecks vs UseHealthChecks | [registering](dotnet-health-checks-registering.md) |
| Probe SQL Server, EF Core, an API; own IHealthCheck | [dependency-and-custom](dotnet-health-checks-dependency-and-custom.md) |
| Restart vs pull from the LB; tag checks per endpoint | [liveness-readiness](dotnet-health-checks-liveness-readiness.md) |
| Richer JSON body, status codes, caching | [response-shape](dotnet-health-checks-response-shape.md) |
| Push status on a timer instead of being polled | [publisher](dotnet-health-checks-publisher.md) |
| Stop it leaking internals; RequireHost is not enough | [security](dotnet-health-checks-security.md) |
| 401 on an MCP server; AllowAnonymous ignored | [mcp-server](dotnet-health-checks-mcp-server.md) |
| Container reads unhealthy; Dockerfile HEALTHCHECK | [docker](dotnet-health-checks-docker.md) |
| Detect someone else's endpoint without writing code | [detect-existing](dotnet-health-checks-detect-existing.md) |
| Expose the build; every field reads "unknown" | [about-endpoint](dotnet-health-checks-about-endpoint.md) |
| Map 404, CORS failure and unhealthy to a colour | [probe-states](dotnet-health-checks-probe-states.md) |

Default to `MapHealthChecks` — it composes with `RequireAuthorization()` and other endpoint
metadata, and supports mapping multiple tagged endpoints cleanly.
