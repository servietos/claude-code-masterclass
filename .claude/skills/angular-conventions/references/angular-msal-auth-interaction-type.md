# MSAL interaction type: popup versus redirect

## Interaction Type — Critical Rule

**Never mix popup and redirect in the same app.** Pick one and use it everywhere:

| Concern | Popup | Redirect |
|---|---|---|
| `MsalGuard interactionType` | `Popup` | `Redirect` |
| `MsalInterceptor interactionType` | `Popup` | `Redirect` |
| `login()` method | `loginPopup()` | `loginRedirect()` |

**Recommended: use Redirect.** Popup flow has a cross-window session storage problem in Angular standalone — the popup loads the full Angular app, `APP_INITIALIZER` runs `handleRedirectObservable()` in the popup context, but the cached token request lives in the main window's session storage only. Result: `no_token_request_cache_error` in the popup, login hangs indefinitely.


Back to the index: [angular-msal-auth](angular-msal-auth.md)
