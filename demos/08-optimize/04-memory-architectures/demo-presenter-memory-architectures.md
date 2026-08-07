---
presents: demo-memory-architectures.md
budget: 5 min
beats: 5
---

# Present: Design a Memory Architecture for Long Sessions

One question, four prompts, and the only variable is what gets loaded: the whole corpus, a condensed statefile, an index plus the one file it pointed at, or a retrieved subgraph. Five beats: the fixed benchmark, condensation as a bet, the index that has a hard cap, the graph's two-edge lookup, and the recall column that is an opinion.

------

**Shell:** this topic ships no file for the learner to write, so [`memory-architectures-solution/`](memory-architectures-solution/) is byte-identical to the starter outside `node_modules/`; confirm it with `diff -rq memory-architectures memory-architectures-solution`, or on Windows with `Compare-Object (Get-ChildItem memory-architectures -Recurse -File -Name) (Get-ChildItem memory-architectures-solution -Recurse -File -Name)`, since `diff` there is an alias for `Compare-Object`.

## Beats

### Beat 1: One question, three prompts, and the only variable is what you load (1 min)

**Open:** [`benchmark.ts`](memory-architectures/benchmark.ts) · the shared `question` and the three prompt constructions under it
**Say:** Comparing memory architectures means anything only when the task is held still and the retrieved context is the single thing that varies. Otherwise the numbers are three anecdotes about three different questions.

```typescript
  const question =
    "Question: What was the root cause of INC-001, and which ADR was adopted as a direct consequence of that incident?";
  const inContextPrompt = `Below is the complete knowledge base for this project.\n\n---\n\n${fullCorpus}\n\n---\n\n${question}`;
  const inContextTokens = countTokens(inContextPrompt);

  const stateFile = await readRelative("approaches/statefile/STATE.md");
  const statefilePrompt = `${stateFile}\n\n${question}`;
  const statefileTokens = countTokens(statefilePrompt);
```

**Result:** no file; the payload is what a verified `npm run benchmark` prints over three static prompt files

```text
Corpus size: 623 tokens (incidents + decisions + team-notes)

| Approach         | Tokens/question   | Tokens/session (×30)   | Recall strength       |
|------------------|-------------------|------------------------|-----------------------|
| In-context       |               665 |                  19950 | Highest               |
| Statefile        |               361 |                  10830 | Good                  |
| Auto-memory      |               406 |                  12180 | Good (index-capped)   |
| Knowledge graph  |               157 |                   4710 | Strong (relational)   |
```

**Gotcha:** every number is a token count over a file on disk, so the three prompt files being static is what makes the run reproduce exactly.

### Beat 2: Condensation is a bet on which facts you will be asked about (1 min)

**Open:** [`approaches/statefile/STATE.md`](memory-architectures/approaches/statefile/STATE.md) · the `## Incidents` table · [`corpus/incidents.md`](memory-architectures/corpus/incidents.md)
**Say:** A statefile is cheap because someone already decided which facts were worth keeping, long before the question arrived. The saving and the risk come out of the very same act.

```text
Condense the corpus into a single STATE.md that preserves every fact that could become a recall question.
Load STATE.md with @approaches/statefile/STATE.md.
Ask the same question. Measure the token cost.
```

**Result:** no file; one row answers the benchmark question outright, ADR link included, and the whole statefile prompt prices at 361 tokens

```markdown
| ID | Date | Root Cause | Owner |
|---|---|---|---|
| INC-001 | 2026-03-12 | PaymentsService pool exhaustion (max 5 → fixed to 50). Triggered ADR-001. | Maria Chen |
| INC-002 | 2026-04-03 | JWT TTL mismatch: staging 1h vs prod 24h (PR #412). Fixed via AUTH_TOKEN_TTL_HOURS env var. | James Park |
| INC-003 | 2026-04-28 | Elasticsearch reindex silent failure at 100k records. Fixed: job monitoring + Slack alert. | Sofia Reyes |
```

**Gotcha:** anything the condensation dropped is not merely slower to reach later, it is gone for the rest of the session.

### Beat 3: Auto-memory is a statefile with a hard cap and a model holding the pen (1 min)

**Open:** [`approaches/auto-memory/MEMORY.md`](memory-architectures/approaches/auto-memory/MEMORY.md) · [`approaches/auto-memory/project-inc-001-pool-exhaustion.md`](memory-architectures/approaches/auto-memory/project-inc-001-pool-exhaustion.md) · the `modified` field
**Say:** The index is the only part charged on every turn, so its 200-line limit is a truncation risk, not a cost risk. Everything past it is silently dropped at the next load, and the model is the one deciding what goes in.

```markdown
- [INC-001 pool exhaustion](project-inc-001-pool-exhaustion.md): PaymentsService pool capped at 5 against 40 concurrent checkouts, triggered ADR-001
- [Auth TTL and Redis TTL move together](feedback-auth-ttl-pairing.md): never change one without the other, INC-002 was exactly that drift
```

**Result:** no file; the budget block a verified `npm run benchmark` prints under the table

```text
Auto-memory index budget (MEMORY.md loads at session start):
  Lines: 8 of 200
  Bytes: 881 of 25600
  Recurring: 213 tokens/turn for the index, 167 once for the file it pointed at
```

**Gotcha:** 406 beats 361 in the table only because the benchmark charges the file body on all 30 turns; the recurring line is what actually happens, and it puts auto-memory below the statefile over a session.

### Beat 4: A graph makes recall a two-node lookup (1 min)

**Open:** [`approaches/knowledge-graph/graph.json`](memory-architectures/approaches/knowledge-graph/graph.json) · the `relations` array · [`approaches/knowledge-graph/prompt.md`](memory-architectures/approaches/knowledge-graph/prompt.md)
**Say:** Entities and relations turn a relational question into a handful of edges instead of a scan across prose. The saving is largest exactly where a statefile is weakest.

```text
Ingest the corpus into an MCP memory server as entities and relations.
Query by entity IDs: INC-001, ADR-001.
Load only the retrieved subgraph into the prompt.
Ask the same question. Measure the token cost.
```

**Result:** no file; the question is two edges out of one node, and the retrieved subgraph prices at 157 tokens

```json
  "relations": [
    { "from": "INC-001", "relation": "triggered", "to": "ADR-001" },
    { "from": "INC-001", "relation": "root_cause", "to": "PaymentsService", "detail": "pool exhaustion: max 5, peak 40 concurrent" },
    { "from": "INC-002", "relation": "root_cause", "to": "AUTH_TOKEN_TTL_HOURS", "detail": "staging 1h vs prod 24h mismatch" },
    { "from": "ADR-002", "relation": "depends_on", "to": "AUTH_TOKEN_TTL_HOURS", "detail": "Redis TTL must match auth TTL" }
  ]
```

**Gotcha:** no MCP memory server ships here, so `graph.json` and the retrieval prompt stand in for ingestion and query; the demo measures the shipped prompt, not a live server.

### Beat 5: The benchmark counts tokens, and the recall column is an opinion (1 min)

**Open:** [`benchmark.ts`](memory-architectures/benchmark.ts) · the `recall` fields and the decision guide at the bottom · [readme.md](readme.md#run-the-benchmark)
**Say:** A comparison with one measured axis and one authored axis is still useful, provided nobody reads the two as equally hard. The honest conclusion is a rule keyed on the shape of the project.

```typescript
      recall: "Highest",
...
      recall: "Strong (relational)",
...
  console.log("Decision guide:");
  console.log("  One-shot task, corpus loaded once       => use in-context");
  console.log("  Ongoing project, stable facts           => use statefile");
  console.log("  Corrections that outlive the session    => use auto-memory");
  console.log("  Entity-relation queries, many turns     => use knowledge graph");
```

**Result:** no file; those string literals are exactly what reaches the `Recall strength` column of the table in Beat 1, beside two counted columns.

**Gotcha:** saying out loud that `recall` is hard-coded is the most honest minute of this demo, and it is what stops the room choosing by the smallest number.

## If the room asks

| Question | Answer |
|---|---|
| Why is the statefile still 361 tokens when `STATE.md` is short? | Because the corpus itself is only 623 tokens; on a realistic corpus the ratio widens sharply. |
| Is the knowledge graph the obvious winner then? | Per turn, yes. The cost it hides is ingestion plus a retrieval layer, and this project ships neither. |
| Did any approach get the answer wrong? | Not this question: all three answer it. Differences surface on facts the condensation dropped. |
| Why project over 30 turns? | Architecture choice only pays across a session; the `TURNS` constant turns a 500-token gap into the number that decides the design. |
| Can I combine them? | Yes, and the decision guide implies it: statefile for stable facts, graph for entity-relation queries, in-context for one-shot work. |
| Who decides what lands in auto-memory? | The model does, which is why the readme's write policy exists: trigger, trust, volatility, conflict handling. Recall is capped by what got written. |
