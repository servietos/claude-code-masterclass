# MSAL auth common pitfalls

## Common Pitfalls

- **`Audience` set to `api://<guid>` while app issues v2 tokens** — IDX10214. The single most common 401 cause on this stack. Fix by switching to the bare GUID or by configuring `ValidAudiences` with both.
- **No `[Authorize]` attribute anywhere, but 401 still fires.** Look for `MapControllers().RequireAuthorization()` in `Program.cs` — it applies a fallback policy to every controller globally.
- **`UseCors` called AFTER `UseAuthentication`.** Correct order is CORS first; otherwise preflight `OPTIONS` requests may be rejected before CORS headers are written.
- **Secrets in committed `appsettings*.json`.** `Microsoft.Identity.Web` reads `AzureAd:ClientCredentials` from config; rotate any committed secret and move to user-secrets or Key Vault.
- **A per-endpoint `[AllowAnonymous]` under a global `RequireAuthorization()` has a twin in the SPA.** The MSAL `protectedResourceMap` carries a `null` entry for the same path so the interceptor sends no token. Audit the two as one decision, keyed on who calls the endpoint: a caller already behind MSAL needs neither half, so remove both; a caller outside the SPA keeps both. Removing only the attribute breaks the SPA call with a 401.

Back to the index: [dotnet-msal-auth](dotnet-msal-auth.md)
