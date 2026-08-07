# Unit Test with a Permission-Locked Agent

An agent's boundary has a mechanical half (the `tools` allowlist the harness enforces) and a written half (a scope section, because `Write` and `Edit` carry no path filter). You define `catalog-test-agent` with both, spawn it to write and run xUnit tests for `FoodController`, and watch it report a defect it is not allowed to fix. You end up with a `catalog-service-cs.Tests` project whose suite documents the un-awaited `GetById` call inside `DeleteFood`.

------

## Setup

Start at the topic folder, not inside the starter: the demo has the agent create `catalog-service-cs.Tests` as a sibling of `catalog-service-cs`, so both projects have to sit inside the working directory.

```bash
cd demos/06-subagents/04-qa-agent
claude
```

---

## Step 1: Define the catalog-test-agent

**Overview:** Create the agent definition file at `.claude/agents/catalog-test-agent.md` with a minimal tool list and a hard scope constraint. The test-only half is a written rule in the agent body, since `Write` and `Edit` carry no path filter: state it explicitly and name the directories that stay off limits.

**Research / Planning / Discussion:**

```text
Read .claude/agents/ to list any existing agent definition files.
Then read catalog-service-cs/Controllers/FoodController.cs.

What dotnet sub-commands are required to create a new xUnit project, restore packages,
and run the test suite? List the minimum set.
Does FoodController depend on any interface types defined in the source code?
List any interfaces present in the catalog-service-cs directory.
```

**Finding:** A good response names `dotnet new xunit`, `dotnet restore`, `dotnet build`, and `dotnet test` as the required commands; confirms that `FoodDBContext` and `AILogger` have no corresponding interfaces in the source; and concludes that the EF Core in-memory provider is the appropriate substitute for a real DbContext in tests. If the response recommends Moq for `FoodDBContext`, push back: there is no `IFoodDBContext` interface to mock against. `AILogger` is a concrete class too, so the tests construct a real one from a `TelemetryClient` with `DisableTelemetry = true`.

**Recipe:**

````text
Create the file .claude/agents/catalog-test-agent.md with exactly this content:

```yaml
---
name: catalog-test-agent
description: Writes and runs xUnit unit tests for catalog-service-cs at demos/06-subagents/04-qa-agent/catalog-service-cs. Reads source files, identifies untested public methods, writes test classes, runs dotnet test, and reports pass/fail results.
model: sonnet
tools:
  - Read
  - Write
  - Edit
  - Glob
  - Grep
  - Bash
---

## Scope

Work only inside demos/06-subagents/04-qa-agent. Read source files under catalog-service-cs, and create or edit files only under catalog-service-cs.Tests.

Never modify implementation files. Controllers, Domain, Infrastructure, AppInsights, Program.cs and catalog-service.csproj are read-only for you. Report defects you find instead of fixing them.

## Testing Rules

- Use xUnit as the test framework.
- Name test methods using the pattern MethodName_Scenario_ExpectedBehavior.
- Never mock a dependency unless an interface for it already exists in the source code.
```
````

**Expected Outcome:** `.claude/agents/catalog-test-agent.md` exists, and `@catalog-test-agent` resolves in the @-mention typeahead with the `tools` list as written.


---

## Step 2: Spawn the Agent to Write and Run Tests

**Overview:** Delegate the test-writing task to `catalog-test-agent` with a fully scoped prompt that names every action method and specifies the in-memory EF Core provider. The agent creates the test project, writes test classes, and reports pass/fail back to the orchestrator.

**Research / Planning / Discussion:**

```text
Read catalog-service-cs/Controllers/FoodController.cs.

For each of the five public action methods, describe one happy-path scenario and one
edge-case scenario that xUnit tests could cover using an in-memory EF Core database.
Note any method where the edge case depends on prior database state.
```

**Finding:** A good response produces ten scenario descriptions covering GetFood, GetById, CreateFood, UpdateFood, and DeleteFood. Watch for `DeleteFood`: the source code calls `GetById` (which returns a `Task`) and checks the result without awaiting it, which is a real bug in the implementation. Every call to `DeleteFood` throws `InvalidOperationException: The entity type 'Task<CatalogItem>' was not found`, for an existing id as well as an unknown one. A sharp response flags this; the agent may not edit implementation files, so the tests pin the broken behavior and name the cause instead of working around it silently.

**Recipe:**

```text
You are an orchestrator. Spawn catalog-test-agent with the following task.

Agent: catalog-test-agent
Task:
  Read catalog-service-cs/Controllers/FoodController.cs
  and catalog-service-cs/Domain/CatalogItem.cs.

  Create a new xUnit test project at
  catalog-service-cs.Tests
  using "dotnet new xunit". The template writes a UnitTest1.cs placeholder holding one
  empty passing test; report that it is still there rather than deleting it, because
  removing files is outside your scope.

  Add the Microsoft.EntityFrameworkCore.InMemory package, version 10.0.2,
  matching the EF Core version used by the service.
  Add a project reference to ../catalog-service-cs/catalog-service.csproj.

  Write a test class FoodControllerTests covering all five public action methods:
  - GetFood: returns all five seeded items
  - GetById: returns the item when it exists; returns null when ID is not found
  - CreateFood: persists the item and returns it
  - UpdateFood: sets EntityState.Modified and returns the item
  - DeleteFood: assert that it throws InvalidOperationException for an existing ID
    and for an unknown ID, because GetById is called without await

  Use the EF Core in-memory provider with a unique database name per test; the seed
  data in FoodDBContext.OnModelCreating is applied by Database.EnsureCreated().
  Build AILogger from a TelemetryClient whose TelemetryConfiguration sets
  DisableTelemetry = true, and a configuration holding the key "title".
  Do not use Moq or any mock library; no interfaces exist in the source.
  Name methods using MethodName_Scenario_ExpectedBehavior.
  Run dotnet test and report the results.

Return: { "status", "testsPassed", "testsFailed", "errors", "summary" }
```

**Expected Outcome:** `catalog-service-cs.Tests/FoodControllerTests.cs` exists in the topic folder. Delete the `UnitTest1.cs` placeholder yourself (the agent is not allowed to), then running `dotnet test` from that directory reports `Passed! - Failed: 0, Passed: 7`; with the placeholder still in place the run reports `Passed: 8`. `catalog-test-agent` returns a summary naming the un-awaited `GetById` call inside `DeleteFood` as a defect for an implementation agent to fix. The exact test count and wording depend on the scenarios the agent chooses; the seven-test shape is what the reference solution produces.

The finished project is in [`catalog-service-cs.Tests-solution/`](catalog-service-cs.Tests-solution/readme.md); run `dotnet test` there to see the target state.

