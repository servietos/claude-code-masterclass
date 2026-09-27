# MSAL auth: AzureAd config section and audience

## AzureAd Config Section

Must be in `appsettings.json` (not only in `appsettings.Development.json`) so the production App Service can read it:

```json
"AzureAd": {
  "Instance": "https://login.microsoftonline.com/",
  "TenantId": "<tenantId>",
  "ClientId": "<clientId>",
  "Audience": "<clientId>"
}
```

`AddMicrosoftIdentityWebApi` reads `GetSection("AzureAd")`. The section name must match exactly.

### Audience — v1 vs v2 Tokens

**`Audience` must match the token's `aud` claim EXACTLY** (string comparison). Which value to use depends on the app registration's `accessTokenAcceptedVersion`:

| Manifest `accessTokenAcceptedVersion` | Token `aud` claim | API `Audience` config |
|---|---|---|
| `null` or `1` (v1 tokens) | `api://<clientId>` | `api://<clientId>` |
| `2` (v2 tokens) | bare `<clientId>` GUID | `<clientId>` (no `api://` prefix) |

Setting `Audience` to `api://<guid>` when the token is v2 produces `IDX10214: Audience validation failed`.

To accept both token versions (version-agnostic), configure `ValidAudiences` explicitly:

```csharp
builder.Services.Configure<JwtBearerOptions>(
    JwtBearerDefaults.AuthenticationScheme,
    options =>
    {
        options.TokenValidationParameters.ValidAudiences =
            [clientId, $"api://{clientId}"];
    });
```

## AppConfig Mapping

```csharp
public class AppConfig
{
    public bool AuthEnabled { get; set; }
    public AzureAdConfig AzureAd { get; set; }
    // ...
}

public class AzureAdConfig
{
    public string Instance { get; set; }
    public string TenantId { get; set; }
    public string ClientId { get; set; }
    public string Audience { get; set; }
}
```


Back to the index: [dotnet-msal-auth](dotnet-msal-auth.md)
