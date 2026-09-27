# Detecting an Existing Health Endpoint

## Detecting an existing health endpoint without writing code

Useful for tooling (like an onboarding pipeline) that wants to *use* a health endpoint if one
exists, without injecting code into someone else's repo. A safe, read-only signal check:

- Search source for `MapHealthChecks(` or `UseHealthChecks(` (minimal hosting or `Startup.cs`).
- Search for a controller route matching `health` (`[Route("health")]`, `[HttpGet("health")]`).
- Search `.csproj` files for an `AspNetCore.HealthChecks.*` or
  `Microsoft.Extensions.Diagnostics.HealthChecks*` package reference as a corroborating signal.

If none of these match, treat the endpoint as absent and fall back to a TCP-level check
(e.g. `bash -c '</dev/tcp/127.0.0.1/<port>'`) rather than guessing at a path that may 404.

Back to the index: [dotnet-health-checks](dotnet-health-checks.md)
