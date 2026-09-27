# MSAL auth: AuthEnabled false locks out the dev box

## `AuthEnabled: false` plus `[Authorize]` locks you out of your own dev box

`if (!cfg.AuthEnabled) return;` means "no auth locally" only while no endpoint asks for it. Add
`[Authorize]` to a controller later and local development breaks in a way that reads like a bug in the
controller: every mutation returns 401 and no token can fix it, because the bare
`AddAuthentication().AddJwtBearer()` registered on that path has no authority configured, so nothing
validates. The endpoints are not open, they are unreachable.

Relax the policy, not the attribute, and gate it on the environment rather than on the flag alone:

```csharp
if (!cfg.AuthEnabled)
{
    builder.Services.AddAuthentication(JwtBearerDefaults.AuthenticationScheme).AddJwtBearer();

    if (builder.Environment.IsDevelopment())
        builder.Services.AddAuthorizationBuilder()
            .SetFallbackPolicy(null)
            .SetDefaultPolicy(new AuthorizationPolicyBuilder().RequireAssertion(_ => true).Build());
    else
        builder.Services.AddAuthorization();

    return;
}
```

Outside Development the endpoints stay locked, so an instance shipped with `AuthEnabled: false` by
mistake answers 401 rather than serving mutations anonymously. That is strictly safer than both the
early-return version and a plain `AddAuthorization()`.

**The trap this sets for tests.** `WebApplicationFactory` inherits the host environment, so an
integration test suite runs as Development, the permissive policy applies, and every `[Authorize]`
passes unconditionally. A test asserting "unauthenticated calls are rejected" then passes while
proving nothing. Pin the test host to a non-Development environment and let the suite's own auth
handler satisfy the real policy:

```csharp
builder.UseEnvironment("Test");
```

Verify by running the negative case: an unauthenticated request must return 401 in the test suite. If
it returns 200 or 201, the host is still Development. See `false-green-checks`, shape 6.


Back to the index: [dotnet-msal-auth](dotnet-msal-auth.md)
