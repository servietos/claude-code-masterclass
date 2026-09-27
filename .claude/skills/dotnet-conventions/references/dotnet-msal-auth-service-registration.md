# MSAL auth: AddMsalAuth service registration

## AppBuilder — Service Registration

```csharp
public static void AddMsalAuth(this WebApplicationBuilder builder)
{
    var cfg = builder.Configuration.Get<AppConfig>();
    if (!cfg.AuthEnabled) return;

    builder.Services.AddAuthentication(JwtBearerDefaults.AuthenticationScheme)
        .AddMicrosoftIdentityWebApi(builder.Configuration.GetSection("AzureAd"));
    builder.Services.AddAuthorization();
    // Do NOT add AuthorizeFilter via AddControllers here — use MapControllers().RequireAuthorization() instead
}
```

`AddMicrosoftIdentityWebApi` reads the `AzureAd` section and wires the full JWT Bearer pipeline including JWKS retrieval, signature validation, issuer/audience checks, and `Microsoft.Identity.Web` claim mapping.

**Critical: Never call `AddControllers()` twice.** If `AddMsalAuth` calls `AddControllers(options => options.Filters.Add(AuthorizeFilter))` and `Program.cs` calls `AddControllers()` again for JSON options, the filter from the first call is silently discarded.

Correct pattern — call `AddControllers` once in `Program.cs`:

```csharp
builder.AddMsalAuth();
builder.Services.AddControllers()
    .AddJsonOptions(options => options.JsonSerializerOptions.PropertyNamingPolicy = null);
```


Back to the index: [dotnet-msal-auth](dotnet-msal-auth.md)
