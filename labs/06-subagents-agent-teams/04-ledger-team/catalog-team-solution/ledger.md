# Catalog defect ledger

| ID | Test | Defect | File | Status | Fixed by | Verified by |
| --- | --- | --- | --- | --- | --- | --- |
| D1 | FoodControllerTests.DeleteFood_ExistingId_RemovesItem | Observed: DeleteFood(4) throws InvalidOperationException "The entity type 'Task<CatalogItem>' was not found" because GetById is not awaited and the Task is passed to ctx.Remove. Expected: item 4 is removed and Ok is returned. | catalog-service-cs/Controllers/FoodController.cs | verified | catalog-fixer | catalog-tester |
| D2 | FoodControllerTests.DeleteFood_UnknownId_ReturnsOkAndKeepsData | Observed: DeleteFood(999) throws InvalidOperationException because the un-awaited Task is never null and is passed to ctx.Remove. Expected: Ok is returned and no data changes. | catalog-service-cs/Controllers/FoodController.cs | verified | catalog-fixer | catalog-tester |

Status moves open, fixed, verified; catalog-tester adds rows and sets verified or open; catalog-fixer sets fixed and fills Fixed by; nobody deletes a row.
