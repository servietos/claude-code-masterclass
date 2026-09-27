# What v5 broke: removed and moved APIs

## MSAL Browser v5 — Breaking API Changes

| What changed | Before (v4) | After (v5) |
|---|---|---|
| Account storage events | `instance.enableAccountStorageEvents()` | Remove — always enabled |
| Account added/removed events | `EventType.ACCOUNT_ADDED / REMOVED` | `EventType.LOGIN_SUCCESS / LOGOUT_SUCCESS` |
| Logout | `authService.logout()` | `authService.logoutRedirect()` or `logoutPopup()` |
| Navigate after redirect | `auth.navigateToLoginRequestUrl: true` in config | Pass to `handleRedirectObservable({ navigateToLoginRequestUrl })` |
| Popup redirect handler | `handleRedirectObservable()` anywhere | `APP_INITIALIZER` (see msal-angular.md) |
| Platform broker (Windows) | Default off | **Default on** — must set `allowPlatformBroker: false` |

### `BrowserAuthOptions` — removed properties

`navigateToLoginRequestUrl` is **no longer a valid key** in the `auth` config block. Remove it from `MSALInstanceFactory`. Pass it to `handleRedirectObservable()` if needed — set it `false` there when login can start from the same URL as `redirectUri` (e.g. a landing page with `redirectUri: '/'`), or the redirect return hangs on `/?state=...`.

## MSAL Angular v5 — Breaking Changes

| What changed | Before (v4) | After (v5) |
|---|---|---|
| `MsalService.logout()` | Available | Removed — use `logoutRedirect()` / `logoutPopup()` |
| `protectedResourceMap` matching | Loose by default | **Strict by default** — use `path/*` wildcards |
| `handleRedirectObservable(hash)` | Accepts hash string | Deprecated — pass `{ hash: '...' }` options object |
| Token injection to `inject(TOKEN)` | String-based | Type-based — TypeScript errors without explicit types |

Back to the index: [msal-version-changes](msal-version-changes.md)
