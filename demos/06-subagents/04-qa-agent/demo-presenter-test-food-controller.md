---
presents: demo-test-food-controller.md
budget: 4 min
beats: 4
---

# Present: Unit Test with a Permission-Locked Agent

An agent's boundary has a mechanical half (the tool allowlist) and a written half (a scope section, because `Write` and `Edit` carry no path filter). Four beats cover both halves, the reason no dependency here can be mocked, and the payoff: a test-only agent that finds a real defect and reports it instead of fixing it.

------

## Beats

### Beat 1: A tool the agent never receives cannot be misused (1 min)

**Open:** [Step 1: Define the catalog-test-agent](demo-test-food-controller.md#step-1-define-the-catalog-test-agent) · [`.claude/settings.json`](../../../.claude/settings.json)
**Say:** Only the mechanical half of a boundary survives the agent misreading its own instructions. A capability never granted cannot be talked into existence by a persuasive task prompt.

```yaml
name: catalog-test-agent
...
model: sonnet
tools:
  - Read
  - Write
  - Edit
  - Glob
  - Grep
  - Bash
```

**Result:** the run writes `catalog-test-agent.md` into [`.claude/agents/`](../../../.claude/agents/), which the repo does not ship: the four committed agents there are `angular-expert`, `dotnet-expert`, `github-devops-agent` and `playwright-expert`.

**Gotcha:** there is no field here for `Bash(rm:*)`, because command-level rules live in `settings.json` under `permissions.deny` and cover the whole session.

### Beat 2: Write and Edit carry no path filter, so the scope is prose (1 min)

**Open:** [`Controllers/`](catalog-service-cs/Controllers) · [`Domain/`](catalog-service-cs/Domain) · [`Infrastructure/`](catalog-service-cs/Infrastructure) · [`AppInsights/`](catalog-service-cs/AppInsights), the four folders the scope declares read-only
**Say:** Tool grants are whole tools, never paths, so `Write` grants writing anywhere the session can write. Everything narrower lives in prose the agent may or may not honour.

```markdown
## Scope

Work only inside demos/06-subagents/04-qa-agent. Read source files under catalog-service-cs, and create or edit files only under catalog-service-cs.Tests.

Never modify implementation files. Controllers, Domain, Infrastructure, AppInsights, Program.cs and catalog-service.csproj are read-only for you. Report defects you find instead of fixing them.
```

**Result:** the written rule held, and every file the run wrote sits in [`catalog-service-cs.Tests-solution/`](catalog-service-cs.Tests-solution/readme.md); this topic's `catalog-service-cs/` is still identical to the copy in [`02-backend/`](../02-backend/catalog-service-cs).

**Gotcha:** the last sentence of the scope is what makes this a QA agent rather than a fixer, and it is an instruction, not a permission.

### Beat 3: No interface in the source means no mock (1 min)

**Open:** [`Infrastructure/FoodDBContext.cs`](catalog-service-cs/Infrastructure/FoodDBContext.cs) · [`AppInsights/AILogger.cs`](catalog-service-cs/AppInsights/AILogger.cs), concrete classes with no interface between them
**Say:** A mock needs a seam, and code that never declared an interface offers none. The honest substitute is the real dependency configured to be cheap and isolated.

```text
  Use the EF Core in-memory provider with a unique database name per test; the seed
  data in FoodDBContext.OnModelCreating is applied by Database.EnsureCreated().
  Build AILogger from a TelemetryClient whose TelemetryConfiguration sets
  DisableTelemetry = true, and a configuration holding the key "title".
  Do not use Moq or any mock library; no interfaces exist in the source.
```

**Result:** `NewContext` is the substitute the agent chose, in [`FoodControllerTests.cs`](catalog-service-cs.Tests-solution/FoodControllerTests.cs)

```csharp
    private static FoodDBContext NewContext()
    {
        var options = new DbContextOptionsBuilder<FoodDBContext>()
            .UseInMemoryDatabase(Guid.NewGuid().ToString())
            .Options;
        var ctx = new FoodDBContext(options);
        ctx.Database.EnsureCreated();
        return ctx;
```

**Gotcha:** a fresh database name per test keeps the runs isolated, and `EnsureCreated()` is what applies the seed data from `OnModelCreating`.

### Beat 4: The defect the agent may report but not repair (1 min)

**Open:** [`Controllers/FoodController.cs`](catalog-service-cs/Controllers/FoodController.cs) · `DeleteFood`, the un-awaited `GetById` call
**Say:** An agent barred from implementation code has one honest move when it meets a real bug: pin the behaviour, name the cause, hand the repair on. Keeping the checker separate from the fixer keeps the suite an independent verdict.

```csharp
        [HttpDelete("{id}")]
        public async Task<ActionResult> DeleteFood(int id)
        {
            var item = GetById(id);
            if (item != null)
            {
                ctx.Remove(item);
                await ctx.SaveChangesAsync();
            }
```

**Result:** the agent pinned the bug instead of fixing it, in [`FoodControllerTests.cs`](catalog-service-cs.Tests-solution/FoodControllerTests.cs)

```csharp
    public async Task DeleteFood_WithExistingId_ThrowsBecauseGetByIdIsNotAwaited()
    {
        using var ctx = NewContext();
        var controller = NewController(ctx);
        var ex = await Assert.ThrowsAsync<InvalidOperationException>(() => controller.DeleteFood(3));
        Assert.Contains("Task<CatalogItem>", ex.Message);
        Assert.Equal(5, await ctx.Food.CountAsync());
    }
```

**Gotcha:** the one-word fix (`var item = await GetById(id);`) belongs to an implementation agent, which is what makes a permission lock produce better output rather than less.

## If the room asks

| Question | Answer |
|---|---|
| Does the suite actually pass? | `Passed! - Failed: 0, Passed: 7, Skipped: 0, Total: 7`, verified on .NET SDK 10.0.110 in [`catalog-service-cs.Tests-solution/`](catalog-service-cs.Tests-solution/readme.md); two of the seven assert a failure and still pass. |
| Why is the `UnitTest1.cs` placeholder still there? | Deleting files is outside the agent's scope, so it reports the file instead; the learner removes it, which is why the run is 7 tests rather than 8. |
| What actually stops `Write` from hitting `Controllers/`? | Nothing mechanical: the tool list removes whole tools, not paths, so the path rule is written and then verified by reading the diff. |
| Why construct a real `AILogger`? | It is a concrete class with no interface, and `DisableTelemetry = true` keeps the test run offline. |
