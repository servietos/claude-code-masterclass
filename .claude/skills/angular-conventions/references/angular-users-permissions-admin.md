# User & Permission Admin UI (RBAC + mixed auth)

A reusable Angular pattern for a **user/role/permission administration UI** backed by **mixed auth**
(Entra ID/MSAL for humans + a local username/password JWT for a service/debug account). Pairs with the
global **`add-mixed-auth`** skill (the full-stack auth design) — this file is the **Angular client** half.

**Use when** building or extending: an admin users screen, a permission matrix, role management, a
dual-auth client (local token + MSAL), a token interceptor, or an admin route guard. Triggers:
"user admin UI", "permission admin", "roles screen", "RBAC UI", "mixed auth client", "local login form",
"admin guard", "adminEmails".

| You want to... | Read |
| --- | --- |
| What do the withAuth and withAdmin store slices expose, and which /users, /roles, /permissions and /auth endpoints do they call? | [angular-users-permissions-admin-store-slices](angular-users-permissions-admin-store-slices.md) |
| Wiring the token interceptor, local session storage, auth service, admin screens, adminGuard or the /login route? | [angular-users-permissions-admin-client-wiring](angular-users-permissions-admin-client-wiring.md) |
| A locally-logged-in admin gets bounced to the Entra redirect, or every gated route breaks for local (LocalJwt) accounts? | [angular-users-permissions-admin-guard-local-session](angular-users-permissions-admin-guard-local-session.md) |
| Permission checks silently stopped working, Entra admins will not save, need a no-login dev bypass, or MsalInterceptor fighting the local token? | [angular-users-permissions-admin-gotchas](angular-users-permissions-admin-gotchas.md) |

Never route past this one: **The guard MUST honor a local session before deferring to `MsalGuard`.**
