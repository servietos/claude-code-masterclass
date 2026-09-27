# Local auth + DB RBAC: the model and the isAdmin contract

## Architecture

- **Local login**: `POST /api/auth/login` (AuthController) verifies the password with `BCrypt.Net.BCrypt.Verify` against a `UserCredentials` row, then a `LocalTokenService` issues an HS256 JWT with `auth_type: local` and one `permission` claim per permission.
- **RBAC tables**: `Users` (identity), `UserCredentials` (BCrypt hash, work factor 11), `UserRoles`, `Roles`, `RolePermissions`, `Permissions`.
- **Admin rule (local)**: a local user holding the `Administrator` role gets its permission list replaced with `["*"]` in both the login response/JWT and `/api/auth/me`, plus `isAdmin: true` in `/me`. The DB itself stores named permissions, not a literal `*`.
- **Server policy**: `AdminPolicy.IsAdmin` accepts Entra principals via an `AdminEmails` config list (or the `"*"` wildcard entry) and local principals via a `permission` claim with value `*`. The `AdminOnly` authorization policy calls this for both auth types.
- **UI contract (critical)**: the frontend computes `isAdmin` purely as `permissions.includes('*')`; it does not read an `isAdmin` field. The API must therefore put `*` into the permissions array, not only set a boolean.

Back to the index: [dotnet-local-auth-rbac](dotnet-local-auth-rbac.md)
