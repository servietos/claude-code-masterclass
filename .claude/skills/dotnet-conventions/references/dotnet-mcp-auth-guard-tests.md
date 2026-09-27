# Pinning the MCP tool surface with guard tests

Context: the move from two MCP projects to per-tool `[Authorize]` on one server (see [dotnet-mcp-auth-per-tool-authorize](dotnet-mcp-auth-per-tool-authorize.md)).

Rules that survive the change:

- **Pin the surface with a guard test**, now three assertions rather than one: the anonymous
  `tools/list` equals an explicit array, the authenticated list adds exactly the private names, and
  an anonymous `tools/call` on a private tool is refused without returning data.
- **Prove the guard by watching it fail.** Remove one `[Authorize]`, run, see red, restore, see
  green. Without that, a filter that silently is not wired reads as a pass.
- The trust boundary is the **data**, not the transport. An anonymous `/mcp` serving exactly what an
  already-anonymous REST endpoint serves adds no exposure.
- Split into two projects only for a reason 2.2 does not solve: separate deployment, separate
  scaling, or a network boundary the data actually needs.


Back to the index: [dotnet-mcp-auth](dotnet-mcp-auth.md)
