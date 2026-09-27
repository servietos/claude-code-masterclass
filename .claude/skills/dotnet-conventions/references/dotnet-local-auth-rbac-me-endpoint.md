# GET /api/auth/me reference implementation

## Me Endpoint

The `/api/auth/me` endpoint must derive `isAdmin` from roles, not hardcode it:

```csharp
[HttpGet("me")]
public async Task<IActionResult> Me()
{
    var authType = User.FindFirstValue("auth_type");

    if (authType == "local")
    {
        var userId = int.Parse(User.FindFirstValue(ClaimTypes.NameIdentifier)!);
        var user = await db.Users
            .AsNoTracking()
            .Include(u => u.UserRoles).ThenInclude(ur => ur.Role)
                .ThenInclude(r => r.RolePermissions).ThenInclude(rp => rp.Permission)
            .FirstOrDefaultAsync(u => u.Id == userId);

        if (user is null) return Unauthorized();

        var isAdmin = user.UserRoles.Any(ur => ur.Role.Name == "Administrator");
        var permissions = isAdmin
            ? new List<string> { "*" }
            : user.UserRoles
                .SelectMany(ur => ur.Role.RolePermissions)
                .Select(rp => rp.Permission.InternalName)
                .Distinct()
                .ToList();

        return Ok(new { user.Name, permissions, isAdmin });
    }

    // Entra path — derive from AdminEmails config or DB RBAC
    // ...
}
```

Back to the index: [dotnet-local-auth-rbac](dotnet-local-auth-rbac.md)
