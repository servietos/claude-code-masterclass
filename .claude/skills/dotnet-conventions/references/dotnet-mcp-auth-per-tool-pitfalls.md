# Why per-tool authorization silently does nothing

Context: wiring per-tool `[Authorize]` on a single MCP server (see [dotnet-mcp-auth-per-tool-authorize](dotnet-mcp-auth-per-tool-authorize.md)).

Three things this gets wrong if you skip them:

- **The attribute belongs on the method.** Verify a class-level `[Authorize]` on the
  `[McpServerToolType]` before relying on it; the per-method attribute is what was proven to work.
- **An anonymous endpoint never runs a custom auth handler.** With `.AllowAnonymous()` on `MapMcp`,
  ASP.NET Core authenticates only the default scheme, so an `X-API-Key` handler registered as a
  second scheme is never invoked and the key-bearing caller reads as anonymous. Naming the scheme in
  the policy does not fix it: a policy evaluated inside the filter checks the *current* principal.
  Authenticate it explicitly before `UseAuthorization`:

  ```csharp
  app.Use(async (ctx, next) =>
  {
      if (ctx.User.Identity?.IsAuthenticated != true && ctx.Request.Headers.ContainsKey("X-API-Key"))
      {
          var result = await ctx.AuthenticateAsync("ApiKey");
          if (result.Succeeded) ctx.User = result.Principal!;
      }
      await next();
  });
  ```

- **An always-authenticated test handler hides the whole feature.** A `WebApplicationFactory` that
  replaces the default scheme with a handler returning `AuthenticateResult.Success` makes every
  request authenticated, so the tool list is complete for "anonymous" callers and the guard test
  passes while measuring nothing. Give the MCP tests a factory that leaves authentication alone.


Back to the index: [dotnet-mcp-auth](dotnet-mcp-auth.md)
