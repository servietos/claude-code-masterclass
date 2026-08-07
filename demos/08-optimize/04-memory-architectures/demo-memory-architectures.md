# Design a Memory Architecture for Long Sessions

Four ways of giving a long session access to the same knowledge (loading the whole corpus, condensing it into a statefile, letting Claude Code write its own memory files, retrieving only a subgraph) trade token cost against recall risk in different directions. You put one fixed question to all four over the same incident-log corpus and run a benchmark that counts what each prompt costs. You end up with a comparison table projecting cost over a 30-turn session, plus a decision guide naming the corpus size and access pattern each architecture suits.

------

The [memory-architectures/](memory-architectures/) folder contains the corpus files, approach prompts, and benchmark script used in this demo.

## Setup

Work directly in the starter:

```bash
cd demos/08-optimize/04-memory-architectures/memory-architectures
claude
```

## The Corpus

Three files represent a fictional SaaS incident log:

- `corpus/incidents.md`: three P1/P2 incidents with root causes, owners, and fix details
- `corpus/decisions.md`: three architectural decisions with rationale and consequences
- `corpus/team-notes.md`: sprint notes with team membership and active risks

Each architecture answers the same question: "What was the root cause of INC-001 and which ADR was triggered as a consequence?" The benchmark counts the tokens each approach spends on that question; the recall column is a qualitative label, not a measurement. The `result.md` file in each approach folder holds the answer that approach produces.

## Architecture 1: In-Context

Load the entire corpus into every prompt turn:

```text
Load the full corpus into the prompt for every question.
Ask: what was the root cause of INC-001 and which ADR was triggered as a consequence?
Measure the token cost with npm run benchmark.
```

## Architecture 2: Statefile

Pre-summarize all corpus facts into a single compact STATE.md:

```text
Condense the corpus into a single STATE.md that preserves every fact that could become a recall question.
Load STATE.md with @approaches/statefile/STATE.md.
Ask the same question. Measure the token cost.
```

## Architecture 3: Auto-Memory

Load the index every turn and read only the file whose index line matches:

```text
Read the memory index at @approaches/auto-memory/MEMORY.md.
Follow only the index line that matches the question, and read that file.
Ask the same question. Measure the token cost.
```

The six files under `approaches/auto-memory/` are shaped like a real store at `~/.claude/projects/<project>/memory/`: a `MEMORY.md` index plus `project`, `feedback`, `user` and `reference` files carrying a `modified` timestamp. The benchmark charges the index plus one file body on all 30 turns, which overcharges it; the recurring line under the table separates the per-turn index cost from the one-off body.

## Architecture 4: Knowledge Graph

Retrieve only the subgraph relevant to each query:

```text
Ingest the corpus into an MCP memory server as entities and relations.
Query by entity IDs: INC-001, ADR-001.
Load only the retrieved subgraph into the prompt.
Ask the same question. Measure the token cost.
```

No MCP memory server ships with the project: `graph.json` and `approaches/knowledge-graph/prompt.md` stand in for the ingestion and retrieval steps, and the benchmark counts that shipped prompt.

## Run the Benchmark

```bash
npm install
npm run benchmark
```

A verified run on the shipped corpus prints 623 corpus tokens and 665 / 361 / 406 / 157 tokens per question for in-context, statefile, auto-memory, and knowledge graph, plus an index budget of 8 lines and 881 bytes against the 200-line and 25KB limits. Every input file is static, so those numbers reproduce exactly.

Auto-memory costs more per question than the statefile here and less per session: 213 of its 406 tokens are the index, charged on every turn, and the remaining 167 are the file body, charged once.

The completed, installed and run-verified version of this project is `memory-architectures-solution/`.
