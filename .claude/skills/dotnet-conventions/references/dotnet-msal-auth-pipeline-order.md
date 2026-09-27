# MSAL auth: middleware order and CORS

## Program.cs — Middleware Order

The correct middleware order when using `Microsoft.Identity.Web`:

```csharp
app.UseStaticFiles();
app.UseRouting();        // 1. Routing first
app.UseCors("AllowAll"); // 2. CORS after routing
if (cfg.AuthEnabled)
{
    app.UseAuthentication(); // 3. Authentication
    app.UseAuthorization();  // 4. Authorization (MUST follow Authentication)
}

// 5. Endpoint-level authorization — never omit RequireAuthorization in production
if (cfg.AuthEnabled)
    app.MapControllers().RequireAuthorization();
else
    app.MapControllers();
```

`UseCors` must come AFTER `UseRouting` — placing it before breaks CORS policy matching.

`UseAuthorization` must always follow `UseAuthentication` — if it is absent, the authorization middleware never runs and all requests pass through unchallenged.

## CORS Note

`AllowAnyOrigin().AllowAnyMethod().AllowAnyHeader()` does NOT strip the `Authorization` header — that header is not considered a CORS "credential". `AllowCredentials()` is not needed for bearer-token auth. (CORS credentials apply to cookies and `XHR.withCredentials`.)


Back to the index: [dotnet-msal-auth](dotnet-msal-auth.md)
