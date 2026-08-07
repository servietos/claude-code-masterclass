---
presents: demo-review-loop.md
budget: 4 min
beats: 3
---

# Present: Converge a Fix Through Review Rounds

A loop is orchestration with a stopping rule instead of a step count, and the interesting failures are all in the rule. Three beats: the reviewer gets no write tools, a noisy round is usually a briefing defect, and the second review round is the one that pays.

------

## Beats

### Beat 1: The reviewer gets no write tools (1 min)

**Open:** [Step 1: Implement, Then Review With No Write Tools](demo-review-loop.md#step-1-implement-then-review-with-no-write-tools)
**Say:** If the reviewer can fix what it finds, a round silently repairs things instead of reporting them, and the loop loses the record it exists to produce. Separate roles are what make the rounds observable.

**Result:** round 1 returned exactly one changed file. A single agent implementing a contract implements exactly the contract, so [`test-controllers.http`](catalog-service-cs-delegation-loops/test-controllers.http) was left untouched and nothing exercised the branches it had just written.

```csharp
            if (item == null || string.IsNullOrWhiteSpace(item.Name) || item.Price < 0 || item.InStock < 0)
```

**Gotcha:** compare that with the delegation demo, where a second agent owned the request file from the start. The loop finds it a round later; the fan-out never lost it.

### Beat 2: A noisy round is a briefing defect (1.5 min)

**Open:** [Step 2: Triage Before You Fix](demo-review-loop.md#step-2-triage-before-you-fix) · [`catalog-service-cs/Common/AppBuilder.cs`](catalog-service-cs/Common/AppBuilder.cs)
**Say:** A reviewer refutes as hard as its read-set allows. Twelve findings came back, and the ones that evaporate on contact are the ones answered by files the reviewer was never given. Triage belongs to the coordinator, because only the coordinator knows what it withheld.

```text
For each one, check it against the project rather than against the claim:
read catalog-service.csproj and Common/AppBuilder.cs before deciding.
```

**Result:** twelve became five accepted, six rejected, one deferred, and four of the six rejects are settled by one line each.

```csharp
        builder.Services.AddSingleton<AILogger>();
```

**Gotcha:** the reject list must ride along into the next round. Dedupe against everything seen, not everything fixed, or every rejected finding returns forever.

### Beat 3: The second review round is the one that pays (1.5 min)

**Open:** [Step 3: Fix, Review Again, and Stop on a Rule](demo-review-loop.md#step-3-fix-review-again-and-stop-on-a-rule)
**Say:** A fix creates surface the first reviewer never saw, which is the entire argument for looping. It is also why the loop needs a rule: a model told to refute will keep finding smaller things until you stop it.

**Result:** round 4 came back `"dry": false` with three new findings, two of them created by round 3's own duplicate-ID fix, and one in the request file [`test-controllers.http`](catalog-service-cs-delegation-loops/test-controllers.http)

```text
### Delete Food Item (e.g., ID 1)
DELETE {{baseUrl}}/food/1
```

**Gotcha:** the loop stopped on the cap, not on dryness. Say that out loud: "until it goes dry" is the pattern's name, not a promise it will.

## If the room asks

| Question | Answer |
|---|---|
| Why not just run more rounds? | Findings shrink and tokens do not. The coordinator decides when a round stops paying; the model never will. |
| What is a retry loop then? | The same shape at one round: a response that broke its contract goes back with the validation error and the task by reference, so one field gets corrected rather than the work redone. |
| Did the loop find everything the graph found? | It found the ordering defect one round later than the graph's reproduction lens, and only after a fix round had gone in. |
| Where does the stopping rule live? | In the coordinator's prompt, as dryness plus a cap. Both, because either alone stops too early or not at all. |
