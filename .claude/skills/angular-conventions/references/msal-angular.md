# Angular MSAL — Standalone Setup Reference

> Angular 22 standalone + `@azure/msal-angular ^6.x` + `@azure/msal-browser ^5.x`

Wiring, bootstrapping, auth state, migration and config values for MSAL in a standalone Angular app.

| You want to... | Read |
|---|---|
| Wire MSAL into a standalone app: the instance, guard and interceptor factories, and why APP_INITIALIZER owns handleRedirectObservable(). | [msal-angular-provider-setup](msal-angular-provider-setup.md) |
| Know what to put in main.ts and app.config.ts, and why bootstrapping MsalRedirectComponent or `<app-redirect>` is wrong for standalone. | [msal-angular-bootstrap](msal-angular-bootstrap.md) |
| Track the signed-in account from msalSubject$/inProgress$, loginRedirect, and sign out locally without a Microsoft round-trip. | [msal-angular-auth-state-service](msal-angular-auth-state-service.md) |
| Upgrade an existing app from MSAL v4 to v5: the removed APIs, renamed event types and config moves to tick off, plus related MSAL leaves. | [msal-angular-v4-to-v5-migration](msal-angular-v4-to-v5-migration.md) |
| Copy the concrete clientId, authority, redirectUri and protectedScopes into environment.ts, and see what each must match in the app registration. | [msal-angular-environment-config](msal-angular-environment-config.md) |

**Do NOT also call `handleRedirectObservable()` in `AuthStateService`** — `APP_INITIALIZER` is the single owner.
