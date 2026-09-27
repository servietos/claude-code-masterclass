# Testing Authorization Without a Blanket Test Factory

## A shared test factory that authenticates everything cannot test authorization

The usual `WebApplicationFactory` override replaces the default scheme with a handler returning
`AuthenticateResult.Success`, so controller tests need no token. Every suite sharing that factory
then runs as an authenticated user, including the one asserting what an **un**authenticated caller
may see. Such a test passes before the feature works and after, and the green tick is about nothing.

Seen on an MCP tool list: the assertion "an anonymous `tools/list` returns exactly the five public
tools" was green while an anonymous caller could both list and call the two private ones.

- Give the auth-sensitive suite a factory that leaves authentication alone. A
  `protected virtual bool UseTestAuthentication => true` on the shared factory, overridden to `false`
  in a subclass, costs three lines and no duplication of the config.
- Assert both directions: what the anonymous caller sees, and that the authenticated caller sees
  strictly more. Only the pair distinguishes "filtered correctly" from "not filtered at all".
- Prove it by removing one `[Authorize]`, watching the suite go red, and restoring it.

Back to the index: [dotnet-testing](dotnet-testing.md)
