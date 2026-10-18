# Worked-out xUnit test project for FoodController

This is the completed result of [`demo-test-food-controller.md`](../demo-test-food-controller.md). The demo has the learner create the test project from scratch at `catalog-service-cs.Tests`, a sibling of the starter inside this topic folder; this folder holds the finished version so you can compare or run it directly.

The project references the topic's own starter at `..\catalog-service-cs\catalog-service.csproj`, so it runs from a clean clone of this repository with no copy step.

## Run

```bash
cd demos/06-subagents-agent-teams/02-domain-agents/catalog-service-cs.Tests-solution
dotnet test
```

Verified result on .NET SDK 10.0.401: `Passed! - Failed: 0, Passed: 7, Skipped: 0, Total: 7`.

## What the tests cover

| Test | Method under test |
|---|---|
| `GetFood_SeededDatabase_ReturnsFiveSeededItems` | `GetFood` |
| `GetById_ExistingId_ReturnsMatchingItem` | `GetById` |
| `GetById_UnknownId_ReturnsNull` | `GetById` |
| `CreateFood_NewItem_PersistsAndAssignsId` | `CreateFood` |
| `UpdateFood_ExistingItem_PersistsChanges` | `UpdateFood` |
| `DeleteFood_ExistingId_ThrowsInvalidOperationException` | `DeleteFood` |
| `DeleteFood_UnknownId_ThrowsInvalidOperationException` | `DeleteFood` |

## The DeleteFood defect

`FoodController.DeleteFood` calls `GetById(id)` without awaiting it, so `item` is a `Task<CatalogItem>` and `ctx.Remove(item)` throws `InvalidOperationException: The entity type 'Task<CatalogItem>' was not found`. The failure happens for every id, existing or not. The test agent may not edit implementation files, so the two `DeleteFood` tests pin the current broken behavior and name the cause; fixing the controller (`var item = await GetById(id);`) is a separate task for an implementation agent.

## Dependencies

`FoodController` takes `FoodDBContext` and `AILogger`, both concrete classes with no interfaces. `FoodDBContext` is built on the EF Core in-memory provider with a unique database name per test, and `AILogger` is constructed with a real `TelemetryClient` whose `TelemetryConfiguration` has `DisableTelemetry = true`, so no telemetry leaves the test run.
