# Tool parameters take the natural key, not the surrogate id

## A tool parameter takes the natural key, not the surrogate id

The REST controller beside the tool is called by a SPA that already holds the row it is acting on, so
`?listId=2` costs it nothing. The tool is called by a model reading prose, and a surrogate id is a
value it cannot know without a lookup it will sometimes skip, so the same argument has to arrive as
the name a human would say:

```csharp
[McpServerTool(Name = "get_secret")]
[Description("Returns one secret by its exact name within one list.")]
public async Task<SecretDto?> GetSecret(
    [Description("The exact list name as returned by list_secret_lists.")] string list,
    [Description("The exact secret name as returned by list_secrets.")] string name,
    CancellationToken cancellationToken = default) =>
    await repository.GetAsync(
        await lists.RequireIdAsync(list, cancellationToken),
        name,
        version,
        cancellationToken);
```

Three rules make that safe:

- **The repository keeps taking the id.** Resolution lives in one `RequireIdAsync(name, ct)` on the
  lookup repository, and the tool class is the only caller. Do not push name resolution into the
  entity repositories: every method would then carry two ways to say the same thing.
- **An unresolved name throws with the valid set in the message**, `Unknown list 'Web'. The store
  holds: Ext. Resources, Web Accounts.` A model recovers from that in one turn; from
  `ArgumentException: listId` it guesses.
- **Say where the name comes from** in the `[Description]`, naming the tool that returns it. That is
  what makes the id-free chain discoverable: `list_secret_lists` -> `list_secrets` -> `get_secret`.

The same split applies to any lookup whose rows a human names: customer, repo, environment, slot. The
id is an implementation detail of the database, and the tool surface is not the database.

Back to the index: [dotnet-mcp-tool-design](dotnet-mcp-tool-design.md)
