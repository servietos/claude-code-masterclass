# Add a Search Endpoint with dotnet-expert

Delegating a scoped backend task works when the route, the method signature and the persistence detail are decided before the agent is spawned. You research the existing controller, hand dotnet-expert a task prompt with no open decisions left in it, then verify the result with curl against a running API. What you keep is a working `GET /food/search?name=` endpoint in `catalog-service-cs` and a JSON result envelope an orchestrator could validate.

---

## Running the Starter API

Run these commands from the repository root:

```bash
cd demos/06-subagents/02-backend/catalog-service-cs
dotnet restore
dotnet run
```

The launch profile binds `http://localhost:5000`, seeds the SQLite database from `food.db`, and answers `GET /food` with five catalog items. Leave this terminal running while you work through the steps and stop it with Ctrl+C when you are done.

In a second terminal, start Claude Code in the same folder:

```bash
cd demos/06-subagents/02-backend/catalog-service-cs
claude
```

---

## Step 1: Identify What to Delegate

**Overview:** Before writing a task prompt for dotnet-expert, read the existing controller and domain model to confirm route patterns and available fields. A precise task prompt produces less back-and-forth than a vague one.

**Research / Planning / Discussion:**

```text
Read Controllers/FoodController.cs
and Domain/CatalogItem.cs.

List every public action method and its HTTP verb.
Then list every field on CatalogItem suitable for a text search filter,
with a one-line trade-off for each.
Recommend one field and explain why it fits the existing route pattern.
```

**Finding:** A good response names the five existing methods (GetFood, GetById, CreateFood, UpdateFood, DeleteFood) and surfaces `Name` and `Description` as candidate string fields. It recommends `Name` because it matches typical catalog lookup patterns and the route `GET /food/search?name=` fits alongside the existing `/food/{id}` route without needing a new controller. Push back if the response suggests a new controller or a non-string field like `Price`.

**Recipe:**

```text
Read Controllers/FoodController.cs
and Domain/CatalogItem.cs.
Summarize the existing routes and list which CatalogItem fields are searchable strings.
Recommend the best field for a name-filter query endpoint and name the route.
```

**Expected Outcome:** A short recommendation that names `Name` as the filter field and specifies the route as `GET /food/search?name={query}`.


---

## Step 2: Spawn dotnet-expert to Implement the Endpoint

**Overview:** Package the research findings into a scoped task prompt and spawn dotnet-expert to add the search endpoint with proper validation, async EF Core filtering, and HTTP 400 handling.

**Research / Planning / Discussion:**

```text
Based on what you found in Step 1, draft a task prompt for dotnet-expert that:
- Specifies the exact file path to edit.
- Names the route, HTTP verb, and query parameter.
- Lists the required behaviors: 400 on blank input, a case-insensitive EF Core name filter, async return.
- Asks dotnet-expert to return a JSON result with status, filesChanged, and errors.

Show the draft prompt and explain what would happen if any of those details were omitted.
```

**Finding:** A good response produces a self-contained task prompt that references `FoodController.cs` by its full relative path, specifies `IEnumerable<CatalogItem>` as the return type, and names the filter translation to use. Watch for `string.Contains`: SQLite compares with the binary collation, so `Contains` matches case-sensitively and `name=pi` would miss `Pizza Tartufo`. `EF.Functions.Like` translates to SQL `LIKE`, which is case-insensitive for ASCII. If the draft omits the return type or the 400 guard, ask Claude to add them before proceeding.

**Recipe:**

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

**Expected Outcome:** `FoodController.cs` contains a `SearchFood` method and `dotnet build` in the starter reports `0 Error(s)`. The JSON envelope the agent returns is model-dependent in wording, so read it for the file list rather than an exact string.


---

## Step 3: Verify the Endpoint Against the Running API

**Overview:** A compiling controller is not a working endpoint. Restart the API and exercise both paths of the new route, the match path and the guard path, before you accept the agent's result.

**Research / Planning / Discussion:**

```text
The API is running on http://localhost:5000 with the new /food/search endpoint.
List the cases worth testing for a query-string name filter over the seeded
catalog, including the ones most likely to fail silently.
For each case, give the exact curl command and the response you expect.
```

**Finding:** A good response covers more than the happy path: a lowercase fragment that only matches through case-insensitive comparison, a fragment matching nothing, a missing parameter, and a whitespace-only parameter. If it only proposes one successful lookup, ask for the negative cases as well.

**Recipe:**

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

**Expected Outcome:** `name=pi` returns a one-element array with `Pizza Tartufo`, `name=noodle` returns `Hand pulled Noodles`, `name=zzz` returns `[]`, and both the missing and whitespace-only parameter return HTTP 400. The finished result, including the `SearchFood` method, is in [`catalog-service-cs-solution/`](catalog-service-cs-solution/).

