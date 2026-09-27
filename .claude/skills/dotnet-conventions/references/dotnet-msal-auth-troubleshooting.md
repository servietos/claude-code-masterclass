# MSAL auth troubleshooting table

## Troubleshooting

| Symptom | Cause | Fix |
|---|---|---|
| Every authenticated endpoint 401s on localhost with `AuthEnabled: false` | `[Authorize]` is enforced but the fallback `AddJwtBearer()` has no authority, so no token validates | Permissive default policy gated on `IsDevelopment()`, per the section above |
| Integration test asserting 401 passes trivially, and so does everything else | `WebApplicationFactory` inherited the Development environment and its permissive policy | `builder.UseEnvironment("Test")` on the factory |
| 401 from Azure with `"You do not have permission to view this directory"` | Easy Auth is intercepting requests | Delete and recreate the App Service without Easy Auth |
| 401 even with valid Bearer token | `requestedAccessTokenVersion` is null, issuing v1 tokens with wrong issuer | Set to `2` on app registration |
| 401 even after adding `UseAuthorization()` | `AddControllers()` called twice — second call silently replaces the filter | Consolidate to one `AddControllers()` call; use `MapControllers().RequireAuthorization()` |
| CORS error in browser before auth | `UseCors` placed before `UseRouting` | Move `UseCors` after `UseRouting` |
| Authorization not enforced at all | `UseAuthorization()` absent from pipeline | Add after `UseAuthentication()` |
| Audience set to `api://<guid>`, token `aud` is bare GUID | `accessTokenAcceptedVersion: 2` issues bare GUID tokens | Switch `Audience` to bare GUID, or configure `ValidAudiences` with both |


Back to the index: [dotnet-msal-auth](dotnet-msal-auth.md)
