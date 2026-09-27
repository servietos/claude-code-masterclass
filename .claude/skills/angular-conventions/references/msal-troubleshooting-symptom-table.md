# MSAL Angular - Symptom Lookup Table

## Troubleshooting

| Symptom | Cause | Fix |
|---|---|---|
| **Blank page the moment auth is enabled, no console error** | Nothing calls `ensureInitialized()` at startup, so the guard's observable never resolves | Call it once from the root component constructor and gate `<router-outlet>` on a `ready` signal |
| **Redirect loop bouncing through Microsoft** | A custom interceptor calls `acquireTokenRedirect` on failure, and/or the bootstrap hits a non-existent `/api/auth/me` (404) that clears the user | Use `MsalInterceptor` + `protectedResourceMap` (silent acquire only); read the user from `AccountInfo`, not `/me` |
| `Authorization` header missing | `protectedResourceMap` key does not match request URL | Add `/*` wildcard suffix to the key |
| `Authorization` header missing | `withInterceptorsFromDi()` absent from `provideHttpClient` | Add it to `app.config.ts` |
| 401 even with valid login | `requestedAccessTokenVersion` is null (v1 token) | Set to 2 on app registration |
| 401 with `"You do not have permission to view this directory or page."` | Easy Auth is blocking the request | Disable / remove Easy Auth from App Service |
| Token not attached to requests | `protectedResourceMap` key doesn't match request URL (most often a missing `*` wildcard under strictMatching) | Verify key ends with `/api/*` and matches `environment.apiUrl` exactly |
| First request 401s, subsequent succeed | HTTP call fires before MSAL settles | Gate calls behind `inProgress$` reaching `InteractionStatus.None` |
| `redirect_uri` mismatch (AADSTS50011) | `redirectUri: '/'` resolves to `origin + '/'` (trailing slash) but the registration has no trailing slash (or vice-versa) | Make `environment.msal.redirectUri` an explicit absolute URL that matches the registered SPA redirect URI exactly |
| Redirect loop on login | `redirectUri` not registered as SPA redirect URI | Add to app registration under SPA platform |
| Stuck on `/?state=...` after login | Login started from the same URL as `redirectUri` with `navigateToLoginRequestUrl` defaulting to `true` | Pass `{ navigateToLoginRequestUrl: false }` to `handleRedirectObservable()` and let the app handle post-login navigation |
| Logout redirects to `login.microsoftonline.com` / shows "pick an account to sign out" | `logoutRedirect()` always hits the Entra end-session endpoint; with no account it adds the account-picker | For local-only sign-out use `instance.clearCache({ account })` + in-app navigate; for full sign-out pass `{ account }` to skip the picker (see Logout section) |

## See Also

- [`angular-msal-auth.md`](angular-msal-auth.md) - provider wiring, `protectedResourceMap`, `app.config.ts`
- [`msal-auth-patterns.md`](msal-auth-patterns.md) - `AuthService`, guards, logout, the auth toggle
- [`msal-angular-appreg.md`](msal-angular-appreg.md) - Entra app registration via Azure CLI
- [`msal-version-changes.md`](msal-version-changes.md) - which major to run, and what each one broke

Back to the index: [msal-troubleshooting](msal-troubleshooting.md)
