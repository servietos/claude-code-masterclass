# .NET MSAL Authentication (Microsoft.Identity.Web)

How to wire `Microsoft.Identity.Web` in an ASP.NET Core 10 API for JWT Bearer authentication against Entra ID.

**`Audience` must match the token's `aud` claim EXACTLY** (string comparison): bare `<clientId>` for v2, `api://<clientId>` for v1. Mismatch is `IDX10214`, the most common 401 here.

| You want to... | Read |
|---|---|
| Pick the package version; requestedAccessTokenVersion | [app-registration](dotnet-msal-auth-app-registration.md) |
| Register the auth services in the builder | [service-registration](dotnet-msal-auth-service-registration.md) |
| Order the middleware; CORS | [pipeline-order](dotnet-msal-auth-pipeline-order.md) |
| Fill the AzureAd section; v1 vs v2 audience | [config](dotnet-msal-auth-config.md) |
| App Service settings; Easy Auth | [app-service](dotnet-msal-auth-app-service.md) |
| Log aud, iss and the failure exception | [diagnostics](dotnet-msal-auth-diagnostics.md) |
| Decode a 401 and the IDX codes | [401-triage](dotnet-msal-auth-401-triage.md) |
| AuthEnabled false locks out the dev box | [disabled-dev](dotnet-msal-auth-disabled-dev.md) |
| Look up a symptom | [troubleshooting](dotnet-msal-auth-troubleshooting.md) |
| Check the anti-patterns before shipping | [pitfalls](dotnet-msal-auth-pitfalls.md) |
