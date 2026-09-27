# Logout: full Entra sign-out vs. local-only clearCache (v5)

## Logout: server sign-out vs. local-only (v5)

`logoutRedirect()` always navigates the browser to the Entra end-session endpoint
(`login.microsoftonline.com/.../oauth2/v2.0/logout`), clearing the IdP session and — **if no
account is passed — showing a "pick an account to sign out" interstitial** before returning to
`postLogoutRedirectUri`. Choose the call by intent:

| Goal | Call |
|---|---|
| Full sign-out (terminate the Entra session too) | `msalService.logoutRedirect({ account })` — pass the active account to skip the account-picker |
| **Local-only** sign-out (clear tokens, stay on-site, **no** redirect to Microsoft) | `msalService.instance.clearCache({ account })` then `router.navigate(['/'])` |

```typescript
logout(): void {
  this._isLoggedIn.set(false);
  this._userName.set('');
  const account =
    this.msal?.instance.getActiveAccount() ?? this.msal?.instance.getAllAccounts()[0];
  if (account) {
    this.msal!.instance.clearCache({ account }); // local-only: wipes that account's tokens, zero network
  }
  this.router.navigate(['/']);                    // guard reads the now-false isLoggedIn() signal
}
```

**MSAL v5 gotcha:** the documented `logoutRedirect({ onRedirectNavigate: () => false })` "skip
server sign-out" snippet does **not compile** in msal-browser v5 — `onRedirectNavigate` was
removed from the per-request `EndSessionRequest` type (it now lives only on the global
`BrowserAuthOptions`). Use `instance.clearCache(request?: ClearCacheRequest)` with `{ account }`
instead (verified against `@azure/msal-browser` 5.15). **Trade-off:** a local-only logout leaves
the Entra **server session active**, so a later login can complete silently without re-prompting —
usually the desired SPA UX; use full `logoutRedirect({ account })` when the IdP session must end too.

Back to the index: [msal-auth-patterns](msal-auth-patterns.md)
