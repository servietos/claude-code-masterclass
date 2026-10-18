# Orchestrate Three Parallel Code Reviewers

Three specialist reviewers run concurrently over one deliberately flawed [`auth.ts`](parallel-reviewer/auth.ts), and an orchestrator turns their three JSON reports into a single verdict. You compare sequential against `Promise.all` wall clock, watch a canary prove the sessions are isolated, then fix flaws until the CI exit code moves. You end up holding the fan-out plus synthesis pipeline in [`demo-02-parallel.ts`](parallel-reviewer/demo-02-parallel.ts), whose completed reference is the sibling folder [`parallel-reviewer-solution/`](parallel-reviewer-solution).

------

You need Node 18 or newer and working Claude credentials: either a logged-in `claude` CLI or your key in `demos/10-sdk-managed-agents/.env`, which the script loads itself (see the [module readme](../readme.md)). The full run spawns six agent sessions and takes roughly a minute and a half.

```bash
cd demos/10-sdk-managed-agents/02-parallel-agents/parallel-reviewer
npm install
npm run review
```

### Part A: Sequential Baseline (3 min)

Replace the `Promise.all` block in `main()` with three sequential awaits and re-run. This is the strawman; it works, but the total time adds up all three reviewers.

```typescript
const security = await runReviewer(fileContents, "security", "You are a security specialist. Look for injection, authentication, and cryptography issues.");
const perf = await runReviewer(fileContents, "performance", "You are a performance specialist. Look for memory leaks, unbounded growth, and inefficiency.");
const style = await runReviewer(fileContents, "code style", "You are a TypeScript specialist. Look for type safety problems, naming issues, and structural weaknesses.");
```

The existing `console.time("parallel")` and `console.timeEnd("parallel")` around the block already report the wall-clock time, so note the number before restoring the parallel version.

### Part B: Parallel with Promise.all (5 min)

Restore the `Promise.all` and re-run. Compare wall-clock times: the parallel block finishes in about 21 seconds, roughly the slowest single reviewer, well below the sum of the three.

Each reviewer reliably surfaces its own specialty finding:
- Security: SQL injection in `loginUser`, MD5 with a static salt in `hashPassword`
- Performance: unbounded `cache` object with no eviction in `hashPassword`
- Style: `db: any` type annotation, weak `token.length > 10` in `validateSession`

Expect heavy overlap. The flaws in this file are blatant enough that every reviewer usually reports most of them, and the exact wording changes between runs because the output is model-generated. That overlap is the point of Part D: deduplicating it is the orchestrator's job.

### Part C: Isolation Test (4 min)

The isolation test runs automatically at the start of `npm run review`. Session A receives a canary word in its prompt; Session B runs in parallel without it. The test searches Session B's output for the canary.

```text
Isolation test: PASS
```

### Part D: Orchestrator (5 min)

The orchestrator session receives the three JSON outputs and synthesizes them. The output shows deduplicated findings, any contradictions (usually an empty array here, since the reviewers agree), a verdict, and a rationale that leads with the SQL injection and the broken password hashing. Every flaw in this file is critical, so runs land on `block`, but the verdict is a model judgement and the wording of the rationale is model-generated and differs each time.

### Part E: Exit Code (3 min)

The verdict maps to a CI exit code on the 0, 1, 2 convention: `approve` exits 0 and CI proceeds, `comment` exits 1 and CI posts the findings without failing, `block` exits 2 and CI stops. The script prints the number it is about to use.

```text
exit code: 2
```

Now fix the SQL injection in `02-parallel-agents/parallel-reviewer/auth.ts`, replacing the interpolated template literal with a parameterized query:

```typescript
const sql = "SELECT * FROM users WHERE username = $1 AND password = $2";
const result = await db.query(sql, [username, hashPassword(password)]);
```

```bash
npm run review
```

The exit code does not move yet, and that is the lesson. MD5 with a static salt, a cache holding plaintext passwords, and a `validateSession` that accepts any 11-character string are each critical on their own, so the orchestrator keeps returning `block`. Clear all of them (a real KDF with a per-user salt, no credential cache, a verified session token) before the pipeline drops to `comment` or `approve`. The exact code you land on is a model judgement, so aim for 1 or 0 and read whatever the run prints.
