# Local Auth + DB RBAC (dual-auth alongside MSAL)

Pattern for apps that pair Entra ID (MSAL) sign-in with a parallel local username/password login backed by database RBAC. Use when a project needs both a browser-facing MSAL flow and a programmatic or admin login that does not require Entra.

- **UI contract (critical)**: the frontend computes `isAdmin` purely as `permissions.includes('*')`; it does not read an `isAdmin` field. The API must therefore put `*` into the permissions array, not only set a boolean.

| You want to... | Read |
| --- | --- |
| Know the tables, claims and policies, and why `"*"` goes in the permissions array | [architecture](dotnet-local-auth-rbac-architecture.md) |
| Run an Entra JWT scheme and a local JWT scheme in one API | [auth-schemes](dotnet-local-auth-rbac-auth-schemes.md) |
| Mint the local HS256 JWT, one claim per permission, `"*"` for Administrator | [token-service](dotnet-local-auth-rbac-token-service.md) |
| Write the login handler: BCrypt verify, load RBAC, return token plus permissions | [login-endpoint](dotnet-local-auth-rbac-login-endpoint.md) |
| Let the client discover who it is, with `isAdmin` derived from roles | [me-endpoint](dotnet-local-auth-rbac-me-endpoint.md) |
| Create the first admin user and set Issuer, Audience, SigningKey, AdminEmails | [setup](dotnet-local-auth-rbac-setup.md) |
| Fix: local admin has no rights, admin UI redirects, TypeLoadException, 401/503 | [pitfalls](dotnet-local-auth-rbac-pitfalls.md) |
