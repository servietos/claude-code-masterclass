# Converge a Fix Through Review Rounds

One implementation round ships whatever the first agent happened to think of, and one review round catches whatever the first reviewer happened to look at. You run the same write-path hardening as implement, review, triage, fix, review again, deciding in the coordinator which findings the project's real configuration supports.

------

Work in `catalog-service-cs/`; the finished result is beside it in [`catalog-service-cs-delegation-loops/`](catalog-service-cs-delegation-loops/readme.md).

## Step 1: Implement, Then Review With No Write Tools

The reviewer must not be able to fix what it finds, or a round quietly repairs things and you lose the record. Splitting the two roles is what makes the loop observable.

```text
Round 1. Spawn dotnet-expert against this contract, in this folder only:
  1. POST /food returns 400 with a ProblemDetails body when the CatalogItem is invalid
     (Name null/empty/whitespace, Price negative, InStock negative), 201 with a
     Location header otherwise.
  2. PUT /food returns 400 on the same rules, 404 when the ID does not exist, 200 otherwise.
  3. DELETE /food/{id} returns 404 when the ID does not exist, 204 otherwise.
  4. GET /food/{id} returns 404 when the ID does not exist.
Keep GET /food untouched. Run dotnet build and confirm zero errors.

Round 2. Then spawn a read-only reviewer with no write tools. Give it
Controllers/FoodController.cs, Domain/CatalogItem.cs, Infrastructure/FoodDBContext.cs
and test-controllers.http, and the same contract as the claim under test.
Tell it to REFUTE the claim rather than confirm it, to default to reporting when
uncertain, and to ignore style. It returns:
{ "findings": [ { "id", "file", "symbol", "claim", "severity" } ], "summary" }
```

Round 1 returns one changed file, and `test-controllers.http` is untouched, so nothing exercises the branches it just wrote. Round 2 returns 12 findings against that one file, ranging from a real partial-update overwrite to a claim that the injected `AILogger` is not registered anywhere.

The findings arrive as a record, because the reviewer had no tool to repair them with.

## Step 2: Triage Before You Fix

A reviewer refutes as hard as its read-set allows, so an under-briefed one inflates the round with findings that the project's configuration already answers. Triage is the coordinator's job and it is what keeps the loop convergent.

```text
Here are the 12 findings from the review round.
For each one, check it against the project rather than against the claim:
read catalog-service.csproj and Common/AppBuilder.cs before deciding.
Sort them into accept, reject, and defer. For every reject, name the file that
settles it. Do not fix anything yet.
```

Twelve findings become five accepted, six rejected, and one deferred. Four of the six rejects trace to two files the reviewer was never given:

```csharp
        builder.Services.AddSingleton<AILogger>();
```

If it accepts a finding on the strength of the reviewer's confidence alone, push back and ask which file settles it.

## Step 3: Fix, Review Again, and Stop on a Rule

The second review round is the one that pays, because a fix creates surface the first reviewer never saw. It is also where the loop needs a stopping rule, since a model asked to refute will keep finding smaller things indefinitely.

```text
Round 3. Spawn dotnet-expert to fix exactly the five accepted findings and nothing else.
Pass it the project facts already settled, so it does not re-litigate them: the csproj
does not enable Nullable, TreatWarningsAsErrors is false, AILogger is a registered
singleton, and the database is SQLite. Run dotnet build and confirm zero errors.
Round 4. Spawn the reviewer again with the same contract, plus the list of finding ids
already SEEN: the five that were fixed AND the six that were rejected. Tell it to report
only findings that are new, not a rewording of a seen one, and to return
{ "findings": [...], "dry": true | false, "summary" }.
Dedupe against everything seen, never against everything fixed: a rejected finding that
is not on the seen list comes back every round and the loop never converges.
Stop when a round comes back dry, or after this second review round either way.
```

Round 4 came back `"dry": false` with three new findings, and two of them exist only because round 3's duplicate-ID fix created them.

The loop stopped on the cap, which is the honest outcome for a reviewer prompted to refute.
