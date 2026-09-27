# Registering MSAL and local JWT side by side

## Multiple Authentication Schemes

When running both MSAL JWT and a local JWT scheme, register them as separate named schemes and add a policy scheme to pick between them:

```csharp
builder.Services.AddAuthentication(options =>
{
    options.DefaultScheme = "Smart";
    options.DefaultChallengeScheme = "Smart";
})
.AddPolicyScheme("Smart", "Smart", options =>
{
    options.ForwardDefaultSelector = ctx =>
    {
        var auth = ctx.Request.Headers.Authorization.ToString();
        if (auth.StartsWith("Bearer "))
        {
            // local tokens carry auth_type=local in header or are distinguishable by issuer
            // simplest: try local scheme first, fall back to Entra
            return "Local";
        }
        return JwtBearerDefaults.AuthenticationScheme;
    };
})
.AddMicrosoftIdentityWebApi(
    builder.Configuration.GetSection("AzureAd"),
    jwtBearerScheme: JwtBearerDefaults.AuthenticationScheme)
.EnableTokenAcquisitionToCallDownstreamApi()
.AddInMemoryTokenCaches()
;

builder.Services.AddAuthentication()
    .AddJwtBearer("Local", options =>
    {
        options.TokenValidationParameters = new TokenValidationParameters
        {
            ValidateIssuer = true,
            ValidIssuer = builder.Configuration["Auth:LocalJwt:Issuer"],
            ValidateAudience = true,
            ValidAudience = builder.Configuration["Auth:LocalJwt:Audience"],
            ValidateIssuerSigningKey = true,
            IssuerSigningKey = new SymmetricSecurityKey(
                Encoding.UTF8.GetBytes(builder.Configuration["Auth:LocalJwt:SigningKey"]!))
        };
    });
```

If MSAL is gated behind `Auth:Enabled`, keep the policy scheme conditional on that flag so the local scheme can stand alone when Entra is off.

Back to the index: [dotnet-local-auth-rbac](dotnet-local-auth-rbac.md)
