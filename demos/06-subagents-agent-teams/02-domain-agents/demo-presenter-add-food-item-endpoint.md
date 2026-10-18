---
presents: demo-add-food-item-endpoint.md
budget: 4 min
beats: 3
---

# Present: Add a Search Endpoint with dotnet-expert

A delegated backend task succeeds or fails on the task prompt, because the thing that goes silently wrong is the thing a build cannot check. Three beats: the prompt with nothing left to decide, the `EF.Functions.Like` filter, and the curl checks that exercise both paths.

------

## Beats

### Beat 1: A task prompt with no decisions left in it (1 min)

**Open:** [Step 1: Spawn dotnet-expert to Implement the Endpoint](demo-add-food-item-endpoint.md#step-1-spawn-dotnet-expert-to-implement-the-endpoint) · [`.claude/agents/dotnet-expert.md`](../../../.claude/agents/dotnet-expert.md)
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

### Beat 2: The EF.Functions.Like filter (2 min)

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
                return BadRequest();
            }
            var items = await ctx.Food
                .Where(f => EF.Functions.Like(f.Name, $"%{name}%"))
                .ToArrayAsync();
            return Ok(items);
```

**Gotcha:** `string.Contains` compiles and passes review, but SQLite's binary collation means `name=pi` would never match `Pizza Tartufo`.

### Beat 3: A compiling endpoint is not a working endpoint (1 min)

**Open:** [Step 2: Verify the Endpoint Against the Running API](demo-add-food-item-endpoint.md#step-2-verify-the-endpoint-against-the-running-api) · [`test-controllers.http`](catalog-service-cs/test-controllers.http)
**Say:** A green build proves only that the code is well-formed. The cases that carry proof are the negative ones, because a happy-path check passes just as happily over a wrong implementation.

```text
  curl "http://localhost:5000/food/search?name=pi"
  curl "http://localhost:5000/food/search?name=noodle"
  curl "http://localhost:5000/food/search?name=zzz"
  curl -i "http://localhost:5000/food/search"
  curl -i "http://localhost:5000/food/search?name=%20"
```

**Result:** the five checks against [`catalog-service-cs-solution/`](catalog-service-cs-solution/readme.md) came back as follows

```text
GET /food/search?name=pi       200  [{"id":5,"name":"Pizza Tartufo","price":24,"inStock":4,"pictureUrl":"pizza.jpg","description":"Pizza truffle is ..."}]
GET /food/search?name=noodle   200  [{"id":1,"name":"Hand pulled Noodles","price":17,"inStock":9,"pictureUrl":"hand-pulled-noodles.png","description":"Hand pulled noodles ..."}]
GET /food/search?name=zzz      200  []
GET /food/search               400  application/problem+json
GET /food/search?name=%20      400  application/problem+json
```

**Gotcha:** `zzz` returning `[]` with status 200 is a deliberate contract choice, worth pinning out loud so a later agent cannot change it.

## If the room asks

| Question | Answer |
|---|---|
| How big is the whole delegated payload? | One action method, one `using`, and two requests: [`catalog-service-cs-solution/`](catalog-service-cs-solution/readme.md) is the entire record. |
| Why does the JSON envelope not come back word for word? | The wording is model-dependent; read it for the `filesChanged` list, where the exact string varies. |
| Why does dotnet-expert get an MCP server of its own? | The `mcpServers` block in [`dotnet-expert.md`](../../../.claude/agents/dotnet-expert.md) wires `microsoft-learn` into this agent only, and an MCP tool must also appear in `tools`. |
