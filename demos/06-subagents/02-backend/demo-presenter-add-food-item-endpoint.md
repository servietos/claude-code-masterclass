---
presents: demo-add-food-item-endpoint.md
budget: 4 min
beats: 4
---

# Present: Add a Search Endpoint with dotnet-expert

A delegated backend task succeeds or fails on the task prompt, because the thing that goes silently wrong is the thing a build cannot check. Four beats: the decision made before the spawn, the prompt with nothing left to decide, the `EF.Functions.Like` filter, and the curl checks that exercise both paths.

------

## Beats

### Beat 1: The route is decided before the agent is spawned (1 min)

**Open:** [`Controllers/FoodController.cs`](catalog-service-cs/Controllers/FoodController.cs) · [`Domain/CatalogItem.cs`](catalog-service-cs/Domain/CatalogItem.cs) · [Step 1: Identify What to Delegate](demo-add-food-item-endpoint.md#step-1-identify-what-to-delegate)
**Say:** Delegation quality is settled before any agent exists, in the decisions a compiler cannot check. Research spent before the spawn is what bounds how far the change can spread.

```text
Read Controllers/FoodController.cs
and Domain/CatalogItem.cs.

List every public action method and its HTTP verb.
Then list every field on CatalogItem suitable for a text search filter,
with a one-line trade-off for each.
Recommend one field and explain why it fits the existing route pattern.
```

**Result:** `Name` won, and the endpoint landed inside the existing [`Controllers/FoodController.cs`](catalog-service-cs-solution/Controllers/FoodController.cs) with no new controller file

```csharp
        // http://localhost:PORT/food/search?name=pi
        [HttpGet("search")]
        public async Task<ActionResult<IEnumerable<CatalogItem>>> SearchFood([FromQuery] string name)
```

**Gotcha:** push back if the response proposes a new controller or a non-string field like `Price`, because either answer widens the change beyond one file.

### Beat 2: A task prompt with no decisions left in it (1 min)

**Open:** [Step 2: Spawn dotnet-expert to Implement the Endpoint](demo-add-food-item-endpoint.md#step-2-spawn-dotnet-expert-to-implement-the-endpoint) · [`.claude/agents/dotnet-expert.md`](../../../.claude/agents/dotnet-expert.md)
**Say:** Every detail left out of a task prompt becomes a round trip or a guess made on your behalf. Hand over the judgement, never the decisions.

```text
  Add a new action method to FoodController:

    [HttpGet("search")]
    public async Task<ActionResult<IEnumerable<CatalogItem>>> SearchFood([FromQuery] string name)
...
  - The project has implicit usings disabled: add every using the new code needs.
  - Run dotnet build to confirm zero errors.

Return: { "status", "filesChanged", "summary", "errors" }
```

**Result:** the implicit-usings line bought the one import the starter lacks, in [`Controllers/FoodController.cs`](catalog-service-cs-solution/Controllers/FoodController.cs)

```diff
 using System.Collections.Generic;
+using System.Linq;
 using System.Threading.Tasks;
```

**Gotcha:** the `Return:` envelope makes the result machine-readable for an orchestrator.

### Beat 3: EF.Functions.Like, not Contains (1 min)

**Open:** [`Infrastructure/FoodDBContext.cs`](catalog-service-cs/Infrastructure/FoodDBContext.cs) · the seeded `Pizza Tartufo` row in `OnModelCreating`
**Say:** The defects delegation produces are rarely the ones a build catches: they compile, they read naturally, and they are wrong only against real data. Query translation is the classic case.

```text
  Requirements:
  - Return HTTP 400 if name is null or whitespace.
  - Filter Food with EF.Functions.Like on the Name column so the match is case-insensitive.
  - Use async/await; follow the existing primary-constructor DI pattern.
```

**Result:** the guard and the `LIKE` filter both shipped, in [`SearchFood`](catalog-service-cs-solution/Controllers/FoodController.cs)

```csharp
            if (string.IsNullOrWhiteSpace(name))
            {
                return BadRequest("Query parameter 'name' is required.");
            }

            var matches = await ctx.Food
                .Where(item => EF.Functions.Like(item.Name, $"%{name}%"))
                .ToArrayAsync();
```

**Gotcha:** `string.Contains` compiles and passes review, but SQLite's binary collation means `name=pi` would never match `Pizza Tartufo`.

### Beat 4: A compiling endpoint is not a working endpoint (1 min)

**Open:** [Step 3: Verify the Endpoint Against the Running API](demo-add-food-item-endpoint.md#step-3-verify-the-endpoint-against-the-running-api) · [`test-controllers.http`](catalog-service-cs/test-controllers.http)
**Say:** A green build proves only that the code is well-formed. The cases that carry proof are the negative ones, because a happy-path check passes just as happily over a wrong implementation.

```text
  curl "http://localhost:5000/food/search?name=pi"
  curl "http://localhost:5000/food/search?name=noodle"
  curl "http://localhost:5000/food/search?name=zzz"
  curl -i "http://localhost:5000/food/search"
  curl -i "http://localhost:5000/food/search?name=%20"
```

**Result:** two of the five checks were kept, in [`test-controllers.http`](catalog-service-cs-solution/test-controllers.http)

```diff
+### Search Food by Name
+GET {{baseUrl}}/food/search?name=pi
+Content-Type: application/json
+
+### Search Food with a Blank Name (expects HTTP 400)
+GET {{baseUrl}}/food/search?name=%20
```

**Gotcha:** `zzz` returning `[]` rather than a 404 is a deliberate contract choice, worth pinning out loud so a later agent cannot change it.

## If the room asks

| Question | Answer |
|---|---|
| How big is the whole delegated payload? | One action method, one `using`, and two requests: [`catalog-service-cs-solution/`](catalog-service-cs-solution/readme.md) is the entire record. |
| Why does the JSON envelope not come back word for word? | The wording is model-dependent; read it for the `filesChanged` list, not for an exact string. |
| Where would `Bash(rm:*)` be blocked? | Not in agent frontmatter: command-level rules live in [`settings.json`](../../../.claude/settings.json) under `permissions.deny` and cover every sub-agent in the session. |
| Why does dotnet-expert get an MCP server of its own? | The `mcpServers` block in [`dotnet-expert.md`](../../../.claude/agents/dotnet-expert.md) wires `microsoft-learn` into this agent only, and an MCP tool must also appear in `tools`. |
| Should a search endpoint return 404 for no matches? | An empty array is the choice made here, and Step 3 pins it. |
