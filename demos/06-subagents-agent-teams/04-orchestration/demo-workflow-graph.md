# Run the Same Split as a Workflow Graph

A prompt-driven fan-out re-derives its plan on every run, and its contract is a sentence the model may or may not honour. You re-express the same two-slice split as a script where the fan-out is a `parallel()` call, the contract is a schema the harness validates, and the single verification opinion becomes three lenses whose vote is counted in JavaScript.

------

Work in `catalog-service-cs/`; the finished result is beside it in [`catalog-service-cs-delegation-graph/`](catalog-service-cs-delegation-graph/readme.md).

## Step 1: Find the Edges That Are Real

Every edge you delete is work that can run at the same time, so the map is written before the script. An edge exists only where one node needs another node's output.

```text
Two units of work harden the write path of this API:
  A  implements the contract in Controllers/ and Shared/
  B  appends one request per status code to test-controllers.http
Both build against a status-code contract fixed before either starts. A third unit
checks that the result is correct.
Model this as a directed graph. For each pair, state whether an edge exists and name
the specific data that crosses it. Where the only justification is "this has to happen
after that", say so and mark the edge as ordering, not data.
Then list every step above that is not agent work at all, but plain code.
```

Two data edges, both inbound to verification, and a code-only list that includes the merge and the vote count. If it draws an edge from A to B because the requests need the endpoints first, ask what data would actually cross it.

## Step 2: Write the Graph as a Script

The map becomes a script, so the decomposition is identical on every run. The word "workflow" in the prompt is the opt-in, and the harness forces each node through a structured-output tool and retries on mismatch.

```text
Write and run a workflow for hardening the write path of this API.
Structure:
  - meta with name, description, and two phases: Implement and Verify
  - a shared schema requiring status, filesChanged (array of strings) and summary
  - parallel() over two nodes in Implement, both returning that schema:
      node 1, agentType dotnet-expert, owns Controllers/ and Shared/, implements the contract
      node 2 owns test-controllers.http only and must not open FoodController.cs
  - merge the filesChanged arrays in the script body, not in an agent
  - three Verify nodes over the lenses correctness, security and reproduction, each
    prompted to REFUTE the claim that the contract is correctly implemented and to
    default to refuted when uncertain, each returning { lens, refuted, why, evidence }
  - the feature passes only if at least two of three fail to refute; count that in the
    script body and log every dissenting lens
The contract both implement nodes build against:
  1. POST /food returns 400 with a ProblemDetails body when the CatalogItem is invalid
     (Name null/empty/whitespace, Price negative, InStock negative), 201 with a
     Location header otherwise.
  2. PUT /food returns 400 on the same rules, 404 when the ID does not exist, 200 otherwise.
  3. DELETE /food/{id} returns 404 when the ID does not exist, 204 otherwise.
  4. GET /food/{id} returns 404 when the ID does not exist.
Filter out null results before merging, since a failed node resolves to null.
```

`/workflows` shows two node boxes running together under Implement, then three under Verify, and the vote is arithmetic in the script body:

```javascript
const survived = verdicts.filter(v => !v.refuted).length
const passes = survived >= 2
verdicts.filter(v => v.refuted).forEach(v => log(`dissent (${v.lens}): ${v.why}`))
```

## Step 3: Read the Split Vote

A single verifier produces a single opinion, and a confident wrong opinion passes straight to you. Three lenses disagree in public, which is the outcome worth reading.

```text
Report the workflow's verdict field by field:
  - the vote, as survived over total
  - for each lens, refuted true or false, its why, and its evidence line
  - which of the two implement nodes could have caught each dissent on its own
Do not fix anything yet.
```

This run returned `1/3 lenses failed to refute`, so `passes` came back `false`: the reproduction lens found that the file's own pre-existing `DELETE {{baseUrl}}/food/1` runs before the new `PUT` labelled 200 and sends `"id": 1`, so that request returns 404. Node 1 never opened the request file and node 2 never opened the controller, so the defect exists only in the merged result, which is exactly where a verification edge sits.
