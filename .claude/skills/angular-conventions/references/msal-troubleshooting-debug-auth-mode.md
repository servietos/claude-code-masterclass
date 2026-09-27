# MSAL Angular - Debug Auth Mode

## Debug Auth Mode

`environment.development.ts` sets `authEnabled: false` to disable MSAL entirely during local development. The mechanic relies on three pieces working together:

| File | Role |
|---|---|
| `src/app/auth/auth.tokens.ts` | Declares `AUTH_ENABLED` injection token backed by `environment.authEnabled` |
| `src/app/auth/auth.service.ts` | `init()` checks `AUTH_ENABLED`; when false, calls `store.setUser({ email: 'claude@debug.local', isAdmin: true })` |
| `app.html` | Gates the authenticated shell components (e.g. `<app-{shell-nav}>`, `<app-{primary-feature}>`) on `@if (store.isAuthenticated())` |

`store.isAuthenticated()` is a computed signal that returns `user() !== null`. When `authEnabled` is false and `init()` seeds the debug user, the signal is true and the full shell renders. When auth is disabled WITHOUT seeding a user, `store.isAuthenticated()` stays false and the entire app shell (nav, primary feature surfaces, admin features) is hidden.

The `/login` route redirects to `/` when auth is off. The guard and MSAL interceptor are bypassed.

**Rule:** never set `authEnabled: false` without verifying that `auth.service.ts init()` seeds a fallback user. Prod `environment.ts` stays `authEnabled: true` and must not be changed.

Back to the index: [msal-troubleshooting](msal-troubleshooting.md)
