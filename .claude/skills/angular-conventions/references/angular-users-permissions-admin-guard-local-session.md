# The admin guard must honor a local session before MsalGuard

## Gotchas (load-bearing)

1. **The guard MUST honor a local session before deferring to `MsalGuard`.** `MsalGuard` only checks
   `msalService.instance.getAllAccounts().length`, which is **always 0 for a local (LocalJwt) login** — so a
   guard that blindly defers to `MsalGuard` when auth is enabled calls `loginRedirect()` and bounces a
   locally-authenticated admin out to Entra, breaking every gated route for local accounts. The guard must
   `await whenReady()` and allow when the store reports an authenticated user (local OR Entra), falling
   through to `MsalGuard` only when there is **no** session. This is the correctness crux of client-side
   mixed auth — cover it with an E2E "login as the local account → reach an admin route" test.

Back to the index: [angular-users-permissions-admin](angular-users-permissions-admin.md)
