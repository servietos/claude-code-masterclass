---
presents: demo-delegation-fan-out.md
budget: 4 min
beats: 3
---

# Present: Fan One Task Out to Two Contracted Agents

Delegation keeps the plan in a prompt, which makes it the cheapest orchestration that works and the weakest one to enforce. Three beats: the file is the unit of disjointness, the coordinator writes the contract before the split, and a prompt-enforced contract is a request rather than a guarantee.

------

## Beats

### Beat 1: The unit of disjointness is the file (1 min)

**Open:** [Step 1: Cut the Slices](demo-delegation-fan-out.md#step-1-cut-the-slices) · [`catalog-service-cs/Controllers/FoodController.cs`](catalog-service-cs/Controllers/FoodController.cs)
**Say:** Two agents handed overlapping ownership both report success, and the damage only surfaces after both have written. Slice by file, not by task description, and the merge becomes concatenation instead of interpretation.

```text
Then propose two non-overlapping slices for a fan-out: which files each agent
owns exclusively, and what data would have to cross between them. If nothing
has to cross, say so.
```

**Result:** the starter's DELETE is the branch that decides the split, because it does not merely miss a 404, it crashes: `GetById(id)` binds a `Task`, which is never null.

```csharp
            var item = GetById(id);
            if (item != null)
            {
                ctx.Remove(item);
```

**Gotcha:** ask what data would cross an edge before accepting it. "The requests need the endpoints first" is an ordering habit, not a dependency.

### Beat 2: The coordinator writes the contract before the split (1.5 min)

**Open:** [Step 2: Write the Contract, Then Fan Out](demo-delegation-fan-out.md#step-2-write-the-contract-then-fan-out)
**Say:** Anything whose value is exactness gets written by the coordinator, never inferred in parallel by the agents that consume it. Fix the status codes first and the edge between the two agents disappears; leave them to agree at runtime and you get two faithful implementations of different contracts.

```text
Both build against this fixed contract. Neither may change it or add endpoints beyond it:
  1. POST /food returns 400 with a ProblemDetails body when the CatalogItem is invalid
     (Name null/empty/whitespace, Price negative, InStock negative), 201 with a
     Location header otherwise.
```

**Result:** the two `filesChanged` arrays came back disjoint and merged to three paths, with the backend slice in [`Controllers/FoodController.cs`](catalog-service-cs-delegation-solution/Controllers/FoodController.cs) and a new [`Shared/CatalogItemValidator.cs`](catalog-service-cs-delegation-solution/Shared/CatalogItemValidator.cs)

```csharp
            var item = await ctx.Food.FirstOrDefaultAsync(v => v.ID == id);
            if (item is null)
            {
                return NotFound();
            }
```

**Gotcha:** `Allowed paths` is the coordinator's own check, not a harness feature, so verify every returned path falls inside its declared prefix after the merge.

### Beat 3: A prompt-enforced contract is a request (1.5 min)

**Open:** [Step 3: Read What the Contract Did Not Buy You](demo-delegation-fan-out.md#step-3-read-what-the-contract-did-not-buy-you) · [`Shared/CatalogItemValidator.cs`](catalog-service-cs-delegation-solution/Shared/CatalogItemValidator.cs)
**Say:** The schema in a delegation prompt is an instruction to a model, and instructions get dropped. That is not an argument against delegation; it is the reason the coordinator checks the merged result, and the reason the next two shapes exist.

**Result:** the prompt said no inline comments. The validator came back documented anyway.

```csharp
        /// <summary>
        /// Validates the supplied <see cref="CatalogItem"/> against the catalog write-path rules:
```

**Gotcha:** which instruction a run drops is model-dependent, so read the merged result rather than looking for this exact miss.

## If the room asks

| Question | Answer |
|---|---|
| Why fan out rather than chain these two? | They exchange no data. Both build against a contract the coordinator fixed before either started. |
| What did the backend slice actually add? | `CatalogItemValidator.TryValidate`, 400 with ProblemDetails on POST and PUT, 404 on missing IDs, 201 with a Location header, and 204 on delete. |
| What breaks if the output schema is omitted? | One agent answers in prose, the merge reads nothing usable, and the coordinator continues on partial data instead of failing. |
| Is the decomposition the same on the next run? | No. It lives in a prompt, so the model re-derives it. Moving it into a script is the graph demo. |
