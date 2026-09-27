# Angular MSAL Authentication — Overview

How to wire MSAL Angular with `@azure/msal-angular ^5.x` and `@azure/msal-browser ^5.x` for an Angular 22 standalone SPA talking to a protected .NET API.

**Never mix popup and redirect in the same app.** **Recommended: use Redirect.**

| You want to... | Read |
|---|---|
| Popup or redirect; `no_token_request_cache_error`. | [interaction-type](angular-msal-auth-interaction-type.md) |
| Environment azure block; MSAL provider factories. | [providers-setup](angular-msal-auth-providers-setup.md) |
| 401, no Authorization header, no `IDX*` error: map key missing `/*`. | [protected-resource-map](angular-msal-auth-protected-resource-map.md) |
| Relative URLs + `apiUrl` interceptor: MSAL sees the SPA origin. | [interceptor-order](angular-msal-auth-interceptor-order.md) |
| `MsalInterceptor` dropped, no bearer token attached. | [app-config](angular-msal-auth-app-config.md) |

## See Also

- [`msal-auth-patterns.md`](msal-auth-patterns.md) - `AuthService`, functional guards, logout, the auth toggle
- [`msal-troubleshooting.md`](msal-troubleshooting.md) - blank page, redirect loop, missing `Authorization` header, 401 triage
- [`msal-version-changes.md`](msal-version-changes.md) - which major to run and what each one broke
- [`msal-angular.md`](msal-angular.md) - client wiring deep-dive: full provider setup, `APP_INITIALIZER`, `AuthStateService`
- [`msal-angular-appreg.md`](msal-angular-appreg.md) - Entra app registration via Azure CLI
