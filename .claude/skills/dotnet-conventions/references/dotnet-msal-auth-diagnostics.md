# MSAL auth: diagnostic JwtBearerEvents block

## Diagnostic JwtBearerEvents (dev only)

When 401 reasons are opaque, wire this block AFTER `AddMicrosoftIdentityWebApi`. It preserves the library's handlers and adds logging on top:

```csharp
using System;
using System.Text;
using Microsoft.AspNetCore.Authentication.JwtBearer;
using Microsoft.IdentityModel.Logging;

if (builder.Environment.IsDevelopment())
    IdentityModelEventSource.ShowPII = true;   // reveals actual aud/iss values in IDX errors

builder.Services.Configure<JwtBearerOptions>(
    JwtBearerDefaults.AuthenticationScheme,
    options =>
    {
        var existing = options.Events ?? new JwtBearerEvents();
        options.Events = new JwtBearerEvents
        {
            OnMessageReceived = async ctx =>
            {
                if (existing.OnMessageReceived is not null) await existing.OnMessageReceived(ctx);
                var auth = ctx.Request.Headers.Authorization.ToString();
                var preview = string.IsNullOrEmpty(auth) ? "<MISSING>" : auth[..Math.Min(40, auth.Length)] + "...";
                Console.WriteLine($"[JwtBearer] OnMessageReceived path={ctx.Request.Path} authHeader={preview}");
            },
            OnTokenValidated = async ctx =>
            {
                if (existing.OnTokenValidated is not null) await existing.OnTokenValidated(ctx);
                Console.WriteLine($"[JwtBearer] OnTokenValidated aud={ctx.Principal?.FindFirst("aud")?.Value} iss={ctx.Principal?.FindFirst("iss")?.Value} scp={ctx.Principal?.FindFirst("scp")?.Value}");
            },
            OnAuthenticationFailed = async ctx =>
            {
                if (existing.OnAuthenticationFailed is not null) await existing.OnAuthenticationFailed(ctx);
                var sb = new StringBuilder();
                var ex = ctx.Exception;
                while (ex is not null) { sb.AppendLine(ex.GetType().FullName + ": " + ex.Message); ex = ex.InnerException; }
                Console.WriteLine($"[JwtBearer] OnAuthenticationFailed\n{sb}");
            },
            OnChallenge = async ctx =>
            {
                if (existing.OnChallenge is not null) await existing.OnChallenge(ctx);
                Console.WriteLine($"[JwtBearer] OnChallenge error={ctx.Error} description={ctx.ErrorDescription} failure={ctx.AuthenticateFailure?.Message}");
            }
        };
    });
```

Remove or gate behind `IsDevelopment()` before shipping. `IdentityModelEventSource.ShowPII = true` must only be set in development — it prints actual claim values (email, tenant, object ID) to the console.


Back to the index: [dotnet-msal-auth](dotnet-msal-auth.md)
