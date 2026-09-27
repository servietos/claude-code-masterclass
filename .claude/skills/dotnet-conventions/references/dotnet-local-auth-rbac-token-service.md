# LocalTokenService reference implementation

## LocalTokenService

Issue a JWT with one `permission` claim per permission. Replace all permissions with `*` for Administrator users before minting the token:

```csharp
public class LocalTokenService(IConfiguration config)
{
    public string Issue(User user, IEnumerable<string> permissions)
    {
        var claims = new List<Claim>
        {
            new(ClaimTypes.NameIdentifier, user.Id.ToString()),
            new(ClaimTypes.Name, user.Name),
            new("auth_type", "local")
        };

        foreach (var p in permissions)
            claims.Add(new Claim("permission", p));

        var key = new SymmetricSecurityKey(
            Encoding.UTF8.GetBytes(config["Auth:LocalJwt:SigningKey"]!));
        var creds = new SigningCredentials(key, SecurityAlgorithms.HmacSha256);

        var token = new JwtSecurityToken(
            issuer: config["Auth:LocalJwt:Issuer"],
            audience: config["Auth:LocalJwt:Audience"],
            claims: claims,
            expires: DateTime.UtcNow.AddDays(7),
            signingCredentials: creds);

        return new JwtSecurityTokenHandler().WriteToken(token);
    }
}
```

Back to the index: [dotnet-local-auth-rbac](dotnet-local-auth-rbac.md)
