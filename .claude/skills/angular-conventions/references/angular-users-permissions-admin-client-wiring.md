# Dual-auth client wiring, admin screens and routes

These are the client-side halves of the Shape section: the interceptor, the local-session helper, the auth service, the admin screens, the guard and the login route.

- **Dual-auth client:** a functional `HttpInterceptorFn` that (a) passes through when auth is disabled,
  (b) only decorates API-base calls, (c) skips any public/unauthenticated API paths, (d) attaches the
  **local token first** (with a 401 → clear-session + redirect-to-login handler), and (e) falls back to MSAL
  `acquireTokenSilent`. A local-session helper stores `{token, expiresAt}` in a per-app localStorage key. A
  two-path auth service does `init()`/restore (local token → `GET /auth/me`; else MSAL restore),
  `loginLocal(user,pwd)` (`POST /auth/login` → save session → `GET /auth/me`), MSAL `login()`, `logout()`,
  and a `whenReady()` gate.
- **Screens** (build with the host app's component toolkit — Material, Tailwind, or a custom `ux` library —
  do NOT assume Material): `admin-users` (table + name/role filter + a read-only "Entra admins" section from
  `adminEmails`, add/edit dialog, delete-confirm, password reset), `admin-permissions` (role selector +
  Lesen/Bearbeiten checkbox matrix over the app's routes, cascade rules, dirty-track + save), plus `user-dialog`
  and `roles-dialog`. An `adminGuard` protects the admin routes; an unguarded `/login` route hosts the local
  form + Entra button.

Back to the index: [angular-users-permissions-admin](angular-users-permissions-admin.md)
