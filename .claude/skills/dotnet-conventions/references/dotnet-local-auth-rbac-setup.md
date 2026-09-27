# First-time setup: seeded users and Local JWT settings

## Seeding Local Users

When `Auth:Enabled` is `true`, the user-management endpoints require a bearer token, so seed via direct DB insert instead of the API.

Generate BCrypt hashes with a small helper tool (e.g., a console app using `BCrypt.Net.BCrypt.HashPassword(password, 11)`) so they match the API's `Verify` call exactly.

Rows needed:
- `Users` (name, active)
- `UserCredentials` (username, BCrypt hash at work factor 11, active)
- `UserRoles` (one row per role)

Verify end to end: `POST /api/auth/login` should return a JWT containing `"permission": "*"` for admins; `GET /api/auth/me` with that token should report `isAdmin: true`.

## appsettings — Local JWT Section

```json
"Auth": {
  "Enabled": true,
  "LocalJwt": {
    "Issuer": "your-app",
    "Audience": "your-app",
    "SigningKey": "<min-32-char-secret>"
  },
  "AdminEmails": ["admin@example.com"]
}
```

On Azure App Service, set these via double-underscore env vars:

```bash
az webapp config appsettings set -g <rg> -n <app> --settings \
  "Auth__LocalJwt__SigningKey=<secret>"
```

The App Service must have the `SigningKey` set or every local-JWT request returns 503/401.

Back to the index: [dotnet-local-auth-rbac](dotnet-local-auth-rbac.md)
