# Observed pitfalls in local auth + RBAC

## Pitfalls (each one was observed)

1. **Stripping `*` in the permission pipeline** (login response, token service, `/me`) silently makes local admins impossible while unit tests still pass. Check every place permissions are projected.
2. **Hardcoding `isAdmin: false` for `auth_type: local` in `/me`** breaks the admin UI at runtime only; derive it from roles.
3. **Editing the auth controller under a running `dotnet watch`** is a structural (rude) edit: hot reload fails with `TypeLoadException` and the API serves that exception for every request until the watch is manually restarted. Verify with a live request after the change.
4. **E2E tests written against the broken behavior** can pass by asserting the bug ("admin redirects away") as expected. Tests must encode the requirement, not the current output.
5. **Missing `SigningKey` on App Service** causes the API to fail at startup or return 401/503 for all requests. Always provision this setting before first deploy.

Back to the index: [dotnet-local-auth-rbac](dotnet-local-auth-rbac.md)
