# Fan One Task Out to Two Contracted Agents

Handing a whole feature to one agent serialises work that had no reason to be serial, and handing it to two without file boundaries lets both write the same file. You split the write-path hardening of `FoodController` into two disjoint slices, fix the interface yourself before either agent starts, and merge two JSON responses.

------

Work in `catalog-service-cs/`; the finished result is beside it in [`catalog-service-cs-delegation-solution/`](catalog-service-cs-delegation-solution/readme.md).

## Step 1: Cut the Slices

The unit of disjointness is the file. Two agents handed overlapping ownership both report success, and the damage surfaces only after both have written.

```text
Read Controllers/FoodController.cs and Domain/CatalogItem.cs in this folder.
The write path returns no error status codes at all. List every place a caller
could send something invalid or missing and get a 200 or a crash instead.
Then propose two non-overlapping slices for a fan-out: which files each agent
owns exclusively, and what data would have to cross between them. If nothing
has to cross, say so.
```

A good response names the DELETE branch as the one that crashes, because `var item = GetById(id)` binds a `Task`, which is never null, and concludes that nothing crosses between the two slices once the status codes are fixed in advance.

If it draws an edge from the controller slice to the request-file slice because the requests "need the endpoints first", push back and ask what data would actually cross it.

## Step 2: Write the Contract, Then Fan Out

The coordinator writes anything whose value is exactness before the fan-out. Here that is the status-code contract: both agents build against it, and neither is allowed to invent its own version.

```text
You are an orchestrator. Spawn these two agents in parallel and wait for both.
Both build against this fixed contract. Neither may change it or add endpoints beyond it:
  1. POST /food returns 400 with a ProblemDetails body when the CatalogItem is invalid
     (Name null/empty/whitespace, Price negative, InStock negative), 201 with a
     Location header otherwise.
  2. PUT /food returns 400 on the same rules, 404 when the ID does not exist, 200 otherwise.
  3. DELETE /food/{id} returns 404 when the ID does not exist, 204 otherwise.
  4. GET /food/{id} returns 404 when the ID does not exist.
Agent 1: dotnet-expert
Allowed paths: Controllers/, Shared/
Task: implement the contract in FoodController. Keep GET /food untouched. Follow the
  existing style: primary-constructor injection, EF Core through the injected
  FoodDBContext, async/await. Run dotnet build and confirm zero errors.
Agent 2: general-purpose
Allowed paths: test-controllers.http
Task: keep every existing request and append one ###-separated request per status code
  in the contract, each with a comment line naming the expected status. Use the existing
  @baseUrl variable and 9999 as the ID that does not exist. Do not open FoodController.cs.
Both return ONLY:
{ "status": "success" | "failure" | "partial", "filesChanged": ["<path>"], "summary": "<one sentence>", "errors": [] }
```

Two JSON responses come back whose `filesChanged` arrays are disjoint, merging to three paths: `Controllers/FoodController.cs` plus a new `Shared/CatalogItemValidator.cs`, and `test-controllers.http`. The request slice wrote `test-controllers.http` from the contract alone while the controller was still being edited.

## Step 3: Read What the Contract Did Not Buy You

A contract enforced through a prompt is an instruction to a model. Checking the merged result against the instructions is the coordinator's last job, and it is where prompt-enforced contracts show their limit.

```text
Compare what came back against what I asked for.
1. Does every path in the merged filesChanged fall inside that agent's allowed paths?
2. The dotnet-expert prompt said "no inline comments in the code". Read
   Shared/CatalogItemValidator.cs and report whether that instruction held.
3. Name every status code in the contract that the merged result does not produce.
Report each as held or violated. Do not fix anything.
```

The path check passes, and in this run the comment instruction holds: [`Shared/CatalogItemValidator.cs`](catalog-service-cs-delegation-solution/Shared/CatalogItemValidator.cs) came back with no comments at all.

Which instruction a given run drops is model-dependent, so read your own merged result.
