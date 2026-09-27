# GitHub OAuth: where the Client ID lives

## Configuration — Client ID in `appsettings.json`, never `.env`

The device-flow Client ID is a **public identifier**, not a secret. It belongs in `appsettings.json`
(or the DB config registry) — not in `.env` and not in a compose env var:

```json
"GitHub": { "ClientId": "Ov23li..." }
```

```csharp
public string? ClientId => config["GitHub:ClientId"] is { Length: > 0 } id ? id : null;
public bool IsConfigured => !string.IsNullOrWhiteSpace(ClientId);
```

Rationale: device flow uses **no client secret**, so there is nothing secret to protect. `.env` is
Docker Compose's mechanism for infra values Compose itself consumes (SQL passwords, ports, Caddy
hostnames) — application config that the .NET app reads at runtime goes in appsettings.json/DB. The
standard .NET env override (`GitHub__ClientId`) still works if a deployment ever needs it.

Back to the index: [dotnet-github-oauth](dotnet-github-oauth.md)
