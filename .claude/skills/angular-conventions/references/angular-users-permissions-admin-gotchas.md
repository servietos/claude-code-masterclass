# Store collisions, Entra admin allow-list, dev bypass, MsalInterceptor

Items 2 to 5 of the load-bearing gotchas list; item 1 (the guard and the local session) has its own leaf.

2. **Duplicate store member names are silently dropped.** If a `withAuth` member (e.g. a `permissions`
   computed) collides with a `withAdmin` member (e.g. `permissions` state) on the composed store,
   `@ngrx/signals` keeps only one (console warning, no compile error), silently breaking permission checks.
   Give every member a unique name across composed features (e.g. `userPermissions`).
3. **Entra admins are an allow-list, not DB rows.** List the server's admin-email allow-list (`GET
   /auth/admins`) as read-only "Entra Administrator" rows, separate from managed DB users; grant/revoke Entra
   admins by editing that config (server restart reloads it), not the users table. Local users get roles from
   the DB.
4. **Dev bypass:** with auth disabled, seed a `DEV_SUPERUSER` (`['*']`) so guards pass and the admin UI is
   reachable without login; the server's `/auth/me` should mirror this (return an admin identity).
5. **Replacing `MsalInterceptor`:** the official `MsalInterceptor` unconditionally attaches an Entra token to
   matched URLs, which fights local-token auth. Replace it with the custom local-first interceptor above;
   keep the MSAL providers (`MSAL_INSTANCE`, `MSAL_GUARD_CONFIG`, `MsalService`, `MsalGuard`,
   `MsalBroadcastService`).

Back to the index: [angular-users-permissions-admin](angular-users-permissions-admin.md)
