# MSAL Angular - Setups That Must Never Be Used

## Popup Failure Mode (do not repeat)

Symptoms:

- Popup opens, user authenticates, popup stays open
- Main window stays at login screen
- Console in popup: `BrowserAuthError: no_token_request_cache_error`

Root cause: The popup window loads Angular, `APP_INITIALIZER` calls `handleRedirectObservable()`, MSAL tries to do a full redirect exchange but the original token request is in the **main window's session storage** (not the popup's). MSAL fails before sending `postMessage` back to opener.

Fix: switch to redirect flow (see `msal-angular.md`).

## Do NOT Enable Easy Auth Alongside MSAL Angular

**App Service Easy Auth and `Microsoft.Identity.Web` must never coexist.** Easy Auth intercepts requests at the infrastructure layer before .NET sees them. If `unauthenticatedClientAction` is not `AllowAnonymous`, it returns 401/redirect responses that override the app's own auth logic.

If Easy Auth was previously enabled on the App Service, delete and recreate the App Service — disabling it via CLI is unreliable when `configVersion: v2` is active.

## Anti-pattern: hand-rolled token interceptor → redirect loop

Do not write a custom interceptor that calls `acquireTokenRedirect` (or `loginRedirect`) on
failure. Combined with a missing/404 user-load call it produces an infinite loop: API call →
silent acquire fails → `acquireTokenRedirect` → Microsoft → back to app → user-load 404 →
clear user → guard → API call → … Use `MsalInterceptor` + `protectedResourceMap`, which only
acquires **silently** and never triggers interaction from inside the HTTP pipeline.

Back to the index: [msal-troubleshooting](msal-troubleshooting.md)
