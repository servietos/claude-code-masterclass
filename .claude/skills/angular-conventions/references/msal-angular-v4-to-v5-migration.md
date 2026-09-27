# MSAL v4 to v5 migration checklist

## Checklist for MSAL v4 to v5 Migration

- [ ] Remove `enableAccountStorageEvents()` call
- [ ] Replace `EventType.ACCOUNT_ADDED` with `LOGIN_SUCCESS`, `ACCOUNT_REMOVED` with `LOGOUT_SUCCESS`
- [ ] Replace `authService.logout()` with `logoutRedirect()` or `logoutPopup()`
- [ ] Move `navigateToLoginRequestUrl` out of `BrowserAuthOptions` and into the `handleRedirectObservable({ navigateToLoginRequestUrl: false })` call
- [ ] Add `allowPlatformBroker: false` to `system` config
- [ ] Add `APP_INITIALIZER` with `handleRedirectObservable()`
- [ ] Remove `MsalRedirectComponent` bootstrap and `<app-redirect>` from index.html
- [ ] Remove any `handleRedirectObservable()` call from service constructors
- [ ] Set `InteractionType.Redirect` consistently (guard + interceptor + login method)
- [ ] Update `protectedResourceMap` keys to use `path/*` wildcards (strictMatching is now default)
- [ ] Replace `loginPopup()` with `loginRedirect()` in login method
- [ ] Replace any `PopupRequest` type with `RedirectRequest`


## See Also

- [`msal-version-changes.md`](msal-version-changes.md) - which major to run, v4 to v6 upgrade
- [`angular-msal-auth.md`](angular-msal-auth.md) - provider wiring, `protectedResourceMap`, `app.config.ts`
- [`msal-auth-patterns.md`](msal-auth-patterns.md) - `AuthService`, guards, logout
- [`msal-troubleshooting.md`](msal-troubleshooting.md) - 401 triage and every other failure mode


Back to the index: [msal-angular](msal-angular.md)
