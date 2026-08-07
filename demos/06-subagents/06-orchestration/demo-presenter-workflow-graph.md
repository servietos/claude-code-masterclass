---
presents: demo-workflow-graph.md
budget: 4 min
beats: 3
---

# Present: Run the Same Split as a Workflow Graph

A graph moves the plan from a prompt into a script, which changes what a contract is: from something requested to something checked. Three beats: only edges that carry data are real, the deterministic parts leave the model entirely, and three lenses disagree in public where one verifier would have passed.

------

## Beats

### Beat 1: Only edges that carry data are real (1 min)

**Open:** [Step 1: Find the Edges That Are Real](demo-workflow-graph.md#step-1-find-the-edges-that-are-real)
**Say:** Most graphs are too narrow because ordering habits are drawn as dependencies. Delete every edge that carries no data and the work that looked sequential turns out to be concurrent. Name each surviving edge by the data crossing it, never by "then".

```text
For each pair, state whether an edge exists and name the specific data that crosses
it. Where the only justification is "this has to happen after that", say so and mark
the edge as ordering, not data.
```

**Result:** two edges survive, both inbound to verification, and the merge is not agent work at all.

**Gotcha:** the same question kills the edge from the controller node to the request-file node. Neither reads the other; both read a contract fixed before the run.

### Beat 2: The deterministic part leaves the model (1.5 min)

**Open:** [Step 2: Write the Graph as a Script](demo-workflow-graph.md#step-2-write-the-graph-as-a-script) · `/workflows` while it runs
**Say:** In a prompt the schema is an instruction the model may drop. Here the harness forces each node through a structured-output tool and retries on mismatch, so the consumer gets a validated object rather than prose to parse. The merge and the vote are then plain JavaScript costing zero tokens.

```javascript
const survived = verdicts.filter(v => !v.refuted).length
const passes = survived >= 2
verdicts.filter(v => v.refuted).forEach(v => log(`dissent (${v.lens}): ${v.why}`))
```

**Result:** two nodes ran concurrently under Implement and merged to three paths, and the validator this run produced records one model error per broken rule, in [`Shared/CatalogItemValidator.cs`](catalog-service-cs-delegation-graph/Shared/CatalogItemValidator.cs)

```csharp
            if (item.Price < 0)
                modelState.AddModelError(nameof(CatalogItem.Price), "Price cannot be negative.");
```

**Gotcha:** a failed node resolves to `null`, so filter before merging or the script crashes on the one thing it was meant to survive.

### Beat 3: Three lenses disagree in public (1.5 min)

**Open:** [Step 3: Read the Split Vote](demo-workflow-graph.md#step-3-read-the-split-vote)
**Say:** One verifier gives one opinion, and a confident wrong opinion reaches the user unchallenged. Three different lenses catch failures redundancy cannot, because identical skeptics are blind in the same direction.

**Result:** `1/3 lenses failed to refute`, so the run did not pass. The reproduction lens found the defect neither implement node could see: the file's own pre-existing `DELETE /food/1` runs before the new `PUT` labelled 200 and sends `"id": 1`, so that request returns 404.

```text
### Delete Food Item (e.g., ID 1)
DELETE {{baseUrl}}/food/1
```

**Gotcha:** node 1 never opened the request file and node 2 never opened the controller, so that defect exists only in the merged result. That is what a verification edge is for.

## If the room asks

| Question | Answer |
|---|---|
| Why `parallel()` here rather than `pipeline()`? | The verify nodes read both implement results together, which is a genuine barrier. Everywhere else, prefer `pipeline()`. |
| Why not three identical skeptics? | A price endpoint fails in unrelated ways: a missing guard is correctness, a mass-assignment write is security, a request that never fires is reproduction. Redundancy cannot catch what one lens is blind to. |
| Does a majority vote make it true? | No. It is a model judgement, not a test result, which is why the script logs every dissent instead of averaging them. |
| When should I not write a graph? | When the request did not ask for one. A run can spawn dozens of agents; describe it and the rough cost, then let the person decide. |
