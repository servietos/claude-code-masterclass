# Toggle-able auth: one flag across Angular and the .NET API

## Toggle-able auth (one flag, both ends)

Gate the whole thing behind a single `environment.authEnabled` flag so the app runs open during
development and flips to protected for prod:
- Frontend: spread MSAL providers only when enabled — `...(environment.authEnabled ? msalProviders : [])`; guards return `true` early when disabled.
- Backend (.NET): read `Auth:Enabled`; when **true** register `AddMicrosoftIdentityWebApi("AzureAd")` and an `AdminOnly` policy = `RequireAuthenticatedUser()`; when **false** register `AdminOnly` = `RequireAssertion(_ => true)` (allow-all) and skip `UseAuthentication`. Annotate protected controllers with `[Authorize(Policy = "AdminOnly")]` — it then enforces when enabled and is a no-op when disabled, with no per-toggle edits. Keep genuinely public endpoints (e.g. a read-only content feed another site consumes) un-annotated / `[AllowAnonymous]`.

Back to the index: [msal-auth-patterns](msal-auth-patterns.md)
