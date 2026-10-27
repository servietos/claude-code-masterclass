# Unit Test with a Permission-Locked Agent

An agent's boundary has a mechanical half (the `tools` allowlist the harness enforces) and a written half (a scope section, because `Write` and `Edit` carry no path filter). You define `catalog-test-agent` with both, spawn it to write and run xUnit tests for `FoodController`, and watch it report a defect it is not allowed to fix.

------

Start `claude` in the topic folder, so the agent can create `catalog-service-cs.Tests` as a sibling of the `catalog-service-cs` starter; the finished project is in [`catalog-service-cs.Tests-solution/`](catalog-service-cs.Tests-solution/readme.md).

## Step 1: Define the catalog-test-agent

Create the agent definition with a minimal tool list and a hard scope constraint. The test-only half is a written rule in the agent body, since `Write` and `Edit` carry no path filter.

````text
Create the file .claude/agents/catalog-test-agent.md with exactly this content:

```yaml
---
name: catalog-test-agent
description: Writes and runs xUnit unit tests for catalog-service-cs at demos/05-subagents-agent-teams/02-domain-agents/catalog-service-cs. Reads source files, identifies untested public methods, writes test classes, runs dotnet test, and reports pass/fail results.
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

Work only inside demos/05-subagents-agent-teams/02-domain-agents. Read source files under catalog-service-cs, and create or edit files only under catalog-service-cs.Tests.

Never modify implementation files. Controllers, Domain, Infrastructure, AppInsights, Program.cs and catalog-service.csproj are read-only for you. Report defects you find instead of fixing them.
```
````

`.claude/agents/catalog-test-agent.md` exists, and `@catalog-test-agent` resolves in the @-mention typeahead with the `tools` list as written.

The `tools` list is the half the harness enforces; the scope section is the half only the agent can honour.

## Step 2: Spawn the Agent to Write and Run Tests

Delegate the test-writing task with a fully scoped prompt that specifies the in-memory EF Core provider. The agent creates the test project, writes test classes, and reports pass/fail back to the orchestrator.

```text
You are an orchestrator. Spawn catalog-test-agent with the following task.

Agent: catalog-test-agent
Task:
  Create a new xUnit test project at
  catalog-service-cs.Tests
  using "dotnet new xunit". The template writes a UnitTest1.cs placeholder holding one
  empty passing test; report that it is still there rather than deleting it, because
  removing files is outside your scope.
  Add the Microsoft.EntityFrameworkCore.InMemory package, version 10.0.2,
  matching the EF Core version used by the service.
  Add a project reference to ../catalog-service-cs/catalog-service.csproj.
  Write a test class FoodControllerTests covering all five public action methods:
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

Delete the `UnitTest1.cs` placeholder yourself (the agent is not allowed to), then running `dotnet test` reports `Passed! - Failed: 0, Passed: 7`. `catalog-test-agent` returns a summary naming the un-awaited `GetById` call inside `DeleteFood` as a defect for an implementation agent to fix.

The agent may not edit implementation files, so the tests pin the broken behavior and name the cause.
