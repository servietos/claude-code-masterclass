# MSAL Angular — AuthService, Guards, Logout

The application-level patterns that sit on top of the MSAL providers: a cached `AuthService`, functional guards in both directions, the two kinds of logout, and running the same build with auth off.

| You want to... | Read |
|---|---|
| Wire AuthService, `ensureInitialized()` at startup and `authGuard`, and fix a blank page with auth on | [msal-auth-patterns-authservice-bootstrap](msal-auth-patterns-authservice-bootstrap.md) |
| Fix a Login button that does nothing on one machine but works on a fresh profile, or `BrowserAuthError: interaction_in_progress` | [msal-auth-patterns-redirect-subscribe](msal-auth-patterns-redirect-subscribe.md) |
| Choose the logout call: terminate the Entra session, or clear tokens locally with no redirect to Microsoft | [msal-auth-patterns-logout](msal-auth-patterns-logout.md) |
| Send an already signed-in user straight to the app shell instead of the landing or login view | [msal-auth-patterns-public-only-guard](msal-auth-patterns-public-only-guard.md) |
| Run the same build open in dev and protected in prod from one `authEnabled` / `Auth:Enabled` flag | [msal-auth-patterns-auth-toggle](msal-auth-patterns-auth-toggle.md) |

**The critical rule: something must call `ensureInitialized()` at startup (the root
component) or the guard's observable never resolves and the app renders a blank page.**
