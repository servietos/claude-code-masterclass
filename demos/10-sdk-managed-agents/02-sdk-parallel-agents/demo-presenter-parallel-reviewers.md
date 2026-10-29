---
presents: demo-parallel-reviewers.md
budget: 4 min
beats: 4
---

# Present: Orchestrate Three Parallel Code Reviewers

Fan-out first, then the synthesis on top of it. Four beats: `Promise.all` over `query()`, the canary that proves isolation, the orchestrator that never reads the file, the exit code that refuses to move.

------

The pipeline ships complete, so [`parallel-reviewer-solution/`](parallel-reviewer-solution) holds no source diff: `diff -rq` against the starter reports only `package-lock.json`. Every result below is what one run emits, as the source guide records it.

## Beats

### Beat 1: wall clock tracks the slowest reviewer (1 min)

**Open:** [`parallel-reviewer/demo-02-parallel.ts`](parallel-reviewer/demo-02-parallel.ts) · the `Promise.all` block inside `main()` · [The Parallel Pattern](readme.md#the-parallel-pattern)
**Say:** Agent calls spend almost all their time waiting on a network, so three at once cost roughly what one costs. A fourth specialist is near free in wall clock, never in tokens.

```typescript
  const [security, perf, style] = await Promise.all([
    runReviewer(
      fileContents,
      "security",
      "You are a security specialist. Look for injection, authentication, and cryptography issues."
    ),
    ...
  ]);
```

**Result:** no file changes hands; Part B of the source guide records the timing

```text
Compare wall-clock times: the parallel block finishes in about 21 seconds, roughly the slowest single reviewer, well below the sum of the three.
```

**Gotcha:** the specialism is only the third argument, the `systemPrompt`, so fanning out wider is adding array entries.

### Beat 2: the canary is how you prove isolation before you ship (1 min)

**Open:** [`parallel-reviewer/demo-02-parallel.ts`](parallel-reviewer/demo-02-parallel.ts) · `isolationTest()` · [Session Isolation](readme.md#session-isolation)
**Say:** Leakage never announces itself, because a contaminated review still reads exactly like a review. A made-up word is the cheapest test available.

```typescript
  const CANARY = "XYZZY_CANARY_42";
  const opts: Options = { allowedTools: [], permissionMode: "acceptEdits" };

  // the empty first slot discards session A's text, only session B is searched for the canary
  const [, sessionBText] = await Promise.all([
    ...
  ]);

  console.log(`Isolation test: ${sessionBText.includes(CANARY) ? "FAIL (canary leaked!)" : "PASS"}`);
```

**Result:** no file, one printed line; Part C records what the run prints

```text
Isolation test: PASS
```

**Gotcha:** it runs first on every `npm run review`, so the room sees the guarantee before the results that depend on it.

### Beat 3: the orchestrator reads the reviews, never the file (1 min)

**Open:** [`parallel-reviewer/demo-02-parallel.ts`](parallel-reviewer/demo-02-parallel.ts) · the prompt inside `runOrchestrator()` · [The Orchestrator Pattern](readme.md#the-orchestrator-pattern)
**Say:** Withholding the source from the synthesis step is a deliberate decision. An agent that can read the file forms its own opinion, and reconciliation becomes a fourth review nobody authored.

```typescript
      prompt: `Synthesize the three specialist reviews below into one verdict.
Return ONLY valid JSON: { "deduplicated_findings": string[], "contradictions": string[], "verdict": "block"|"comment"|"approve", "rationale": string }

Security: ${JSON.stringify(security)}
Performance: ${JSON.stringify(perf)}
Style: ${JSON.stringify(style)}`,
```

**Result:** no file, one synthesized JSON object; Part D records what it contains

```text
The output shows deduplicated findings, any contradictions (usually an empty array here, since the reviewers agree), a verdict, and a rationale that leads with the SQL injection and the broken password hashing.
```

**Gotcha:** present the empty `contradictions` array as the honest reading of agreement, never as a missing feature.

### Beat 4: fixing one critical flaw does not move the exit code (1 min)

**Open:** [`parallel-reviewer/auth.ts`](parallel-reviewer/auth.ts) · `hashPassword` and `validateSession` · [Part E: Exit Code](demo-parallel-reviewers.md#part-e-exit-code-3-min)
**Say:** A quality gate scores the state of a file, never the work you just did. People misread that as a broken pipeline, usually minutes after their first fix.

```typescript
const sql = "SELECT * FROM users WHERE username = $1 AND password = $2";
const result = await db.query(sql, [username, hashPassword(password)]);
```

**Result:** no file lands in the solution; Part E records the gate after that fix, which still prints the `block` branch

```text
exit code: 2
```

**Gotcha:** MD5 with a static salt, an unbounded cache of password hashes, and a session check that accepts any 11-character string are each critical alone, so `block` stands until all are cleared.

## If the room asks

| Question | Answer |
|---|---|
| How do I know the sessions are genuinely isolated? | Run the canary once per new pipeline. `FAIL` means context crossed sessions and the pipeline is unreliable. |
| Why is `contradictions` empty? | The flaws here are blatant enough that all three reviewers agree, so there is nothing to reconcile. |
| Will the findings be identical between runs? | No, the wording is model-generated. The verdict is a judgement too, though every flaw here is critical, so runs land on `block`. |
| What does one run cost? | Six agent sessions (two canary, three reviewers, one orchestrator) at roughly a minute and a half wall clock. Check `/cost` before widening the fan-out. |
| Why is the solution folder the same as the starter? | Because the pipeline ships complete: the only addition is the `package-lock.json` that `npm install` writes. The fixes happen in `auth.ts`, and the run writes no file. |
