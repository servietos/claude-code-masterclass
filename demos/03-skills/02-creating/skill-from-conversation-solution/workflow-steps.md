# Decision Steps Behind sales-by-region.js

The worked answer to Step 2 of the demo guide: the decision sequence, not the code.

1. **Confirm the input schema.** Needed from the user: the record shape (`region` string, `product` string, `amount` number) and which fields are required. Decision made alone: treat a missing or non-numeric `amount` as `0` rather than throwing. Artifact that moved the conversation on: an agreed data contract.
2. **Define the output contract.** Needed: how the caller consumes the result. Decision: return an array of `{ region, total }` rather than a keyed object, because an array carries the sort order. Artifact: a named return shape with a stated sort (total descending).
3. **Implement the aggregation.** Needed: nothing further from the user once the contract exists. Decision: accumulate into a `Map` for insertion-stable grouping, then materialize and sort. Artifact: `salesByRegion(records)`.
4. **Add the formatting layer.** Needed: the exact line template (`Region: <name>  Revenue: $<total>`). Decision: keep currency formatting in the formatter and leave `salesByRegion` free of presentation concerns. Artifact: `formatReport(results)`.
5. **Embed a runnable verification sample.** Needed: how the learner proves it works. Decision: 8 records across 3 regions at the bottom of the same file so `node sales-by-region.js` is the whole test loop, with no test framework and no dependencies. Artifact: verified stdout.

Verified stdout for the embedded sample:

```text
Region: East  Revenue: $2450.00
Region: North  Revenue: $2146.00
Region: South  Revenue: $2031.00
```
