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
| Browser shows a CORS block plus `500`; API log has `No authenticationScheme was specified, and there was no DefaultChallengeScheme found` from `AuthorizationMiddlewareResultHandler`, while the source registers the schemes on its policy | The running `dotnet watch` process predates the auth wiring (startup registration is applied-but-inert, see [restart matrix](dotnet-watch-restart-matrix.md)); the CORS header is missing only because the challenge throws | Probe with no token: `500` is the stale process, `401` the current code. Compare the listener's `StartTime` with the auth file's mtime; prove the source on a build copy on another port; ask the owner to restart. No code or CORS change |
| Authorization not enforced at all | `UseAuthorization()` absent from pipeline | Add after `UseAuthentication()` |
| Audience set to `api://<guid>`, token `aud` is bare GUID | `accessTokenAcceptedVersion: 2` issues bare GUID tokens | Switch `Audience` to bare GUID, or configure `ValidAudiences` with both |


Back to the index: [dotnet-msal-auth](dotnet-msal-auth.md)
