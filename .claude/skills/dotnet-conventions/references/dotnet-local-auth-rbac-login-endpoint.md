# POST /api/auth/login reference implementation

The local login handler: BCrypt verify, load roles and permissions, return token plus permissions.

## Login Endpoint

```csharp
[HttpPost("login")]
[AllowAnonymous]
public async Task<IActionResult> Login(LoginRequest req)
{
    var credential = await db.UserCredentials
        .AsNoTracking()
        .Include(c => c.User)
            .ThenInclude(u => u.UserRoles)
                .ThenInclude(ur => ur.Role)
                    .ThenInclude(r => r.RolePermissions)
                        .ThenInclude(rp => rp.Permission)
        .FirstOrDefaultAsync(c => c.Username == req.Username && c.Active);

    if (credential is null || !BCrypt.Net.BCrypt.Verify(req.Password, credential.PasswordHash))
        return Unauthorized();

    var isAdmin = credential.User.UserRoles.Any(ur => ur.Role.Name == "Administrator");
    var permissions = isAdmin
        ? ["*"]
        : credential.User.UserRoles
            .SelectMany(ur => ur.Role.RolePermissions)
            .Select(rp => rp.Permission.InternalName)
            .Distinct()
            .ToList();

    var token = tokenService.Issue(credential.User, permissions);
    return Ok(new { token, permissions, isAdmin });
}
```

Back to the index: [dotnet-local-auth-rbac](dotnet-local-auth-rbac.md)
