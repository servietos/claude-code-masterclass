# Add a Search Endpoint with dotnet-expert

Delegating a scoped backend task works when the route, the method signature and the persistence detail are decided before the agent is spawned. You hand dotnet-expert a task prompt with no open decisions left in it, then verify the result with curl against a running API.

---

Work in `catalog-service-cs/`: start the API with `dotnet run` (it binds `http://localhost:5000`) and open Claude Code in a second terminal; the finished result is in [`catalog-service-cs-solution/`](catalog-service-cs-solution).

## Step 1: Spawn dotnet-expert to Implement the Endpoint

Package the decisions into a scoped task prompt and spawn dotnet-expert to add the search endpoint with proper validation, async EF Core filtering, and HTTP 400 handling.

```text
You are an orchestrator. Spawn dotnet-expert with the following task.

Agent: dotnet-expert
Task:
  Read Controllers/FoodController.cs
  and Infrastructure/FoodDBContext.cs.

  Add a new action method to FoodController:

    [HttpGet("search")]
    public async Task<ActionResult<IEnumerable<CatalogItem>>> SearchFood([FromQuery] string name)

  Requirements:
  - Return HTTP 400 if name is null or whitespace.
  - Filter Food with EF.Functions.Like on the Name column so the match is case-insensitive.
  - Use async/await; follow the existing primary-constructor DI pattern.
  - The project has implicit usings disabled: add every using the new code needs.
  - Run dotnet build to confirm zero errors.

Return: { "status", "filesChanged", "summary", "errors" }
```

The guard and the filter in [`Controllers/FoodController.cs`](catalog-service-cs-solution/Controllers/FoodController.cs):

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

`dotnet build` reports `0 Error(s)`; `EF.Functions.Like` translates to SQL `LIKE`, which is case-insensitive for ASCII, where SQLite's binary collation makes `string.Contains` miss `Pizza Tartufo` for `name=pi`.

## Step 2: Verify the Endpoint Against the Running API

A compiling controller is not a working endpoint. Restart the API and exercise both paths of the new route, the match path and the guard path, before you accept the agent's result.

```text
Stop the running API, restart it with dotnet run in the starter folder,
then run these checks and report the status code and body of each:

  curl "http://localhost:5000/food/search?name=pi"
  curl "http://localhost:5000/food/search?name=noodle"
  curl "http://localhost:5000/food/search?name=zzz"
  curl -i "http://localhost:5000/food/search"
  curl -i "http://localhost:5000/food/search?name=%20"

Tell me which checks pass and fix the controller if any of them do not.
```

`name=pi` returns a one-element array with `Pizza Tartufo`, `name=noodle` returns `Hand pulled Noodles`, `name=zzz` returns `[]`, and both the missing and whitespace-only parameter return HTTP 400.

The negative cases carry the proof: a happy-path lookup passes just as happily over a wrong implementation.
