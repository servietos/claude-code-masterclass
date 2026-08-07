# Compare Four Memory Architectures on the Same Recall Task

Run the same recall task against four memory architectures (pasting notes into the prompt, maintaining an episodic `STATE.md`, indexing into the official MCP knowledge-graph memory server, and letting Claude Code write its own auto-memory), then measure tokens and recall accuracy across all four. Finish by auditing what your ingestion schema and your write policy each lost.

Each step contains:
- **Goal**: what you are building
- **Prompt**: paste this into Claude Code (or a shell command, where noted)
- **Expected result**: what the outcome looks like

> **Why this matters:** "Memory" is a loaded term that covers at least four distinct architectures with very different cost and accuracy profiles. Knowing which one to reach for is a harness-design decision, not a tooling preference.

Work in [`03-memory/memory-lab/`](03-memory/memory-lab/readme.md). It ships the eight-note corpus, the three recall questions, and `tokens.py`, the `tiktoken` counter from [Lab 01](lab-01-caveman-compress.md), so every architecture is measured with the same instrument.

The completed reference for this lab is [`03-memory/memory-lab-solution/`](03-memory/memory-lab-solution/readme.md). Build your own version first and use the solution to check your token numbers.

## Where to Open Claude Code

This lab builds its own harness, so open Claude Code inside the lab project rather than at the repo root. The harness is project-scoped: `CLAUDE.md`, `.claude/settings.json` hooks, `.claude/agents/`, `.claude/skills/`, `.claude/commands/` and `.mcp.json` all load from the directory the session was launched in. A session opened at the repo root leaves everything you write here inert, with no error to tell you.

The starter is already in this repo, so there is nothing to scaffold: change into it and start the session there. Run this from the repo root; both commands work unchanged in PowerShell.

```bash
cd labs/08-optimize/03-memory/memory-lab
claude
```

If you start Claude Code with the Claude Terminal extension (`Ctrl+F1` / `Cmd+F1`), it opens in the VS Code workspace folder and reuses an already-open terminal, so it will not follow the `cd` above. Open `memory-lab` as the workspace folder (**File > Open Folder**) before pressing the shortcut, or run the command above in a plain terminal.

> Note: you can also skip the folder switch entirely and name the path in the prompt instead, working from a session opened anywhere in the repo:

```text
In labs/08-optimize/03-memory/memory-lab condense every notes/topic-*.md file into notes/STATE.md ....
```

That works for the statefile, and for any step whose result is just files. It does not work for the memory server or for auto-memory: `.mcp.json` and `.claude/settings.json` both load from the directory the session was launched in, so a root session writes them into the lab folder and then neither connects the server Step 3 depends on nor honours the store location Step 4 sets. Launch inside `memory-lab` from Step 1 onward.

Restart the session with `/exit` then `claude` after any edit to `.claude/settings.json` or `.mcp.json`, because both are read at startup.

Launching inside the starter is what makes the repository a monorepo to this lab rather than the project: the repo's own `/CLAUDE.md`, `/.claude/` and `/.mcp.json` stay out of the session, and you read them from the repo root without ever writing into them. Every path in the prompts below is relative to the lab folder.

---

## Setup: Install the Token Counter

The corpus is already in the starter. `notes/` holds eight `topic-*.md` research notes about "Lumen", a fictional internal observability platform, 200 to 400 words each, carrying the people's names, incident dates and dashboard IDs the recall questions target. Every architecture is measured against that same corpus, which is what lets you compare your numbers with the solution's directly.

`tiktoken` is a third-party PyPI package, so install it into a virtual environment first. Never install it globally.

```bash
python -m venv .venv
./.venv/Scripts/python.exe -m pip install tiktoken
./.venv/Scripts/python.exe tokens.py notes/topic-architecture-overview.md
```

On Linux or macOS use `.venv/bin/python` instead of `.venv/Scripts/python.exe`.

**Expected result:** the counter prints one line, and it is the line the solution measured:

```text
notes/topic-architecture-overview.md: 375
```

The `topic-` prefix is load-bearing. Step 2 writes a condensed statefile next to these notes, and every step that loads the corpus globs `notes/topic-*.md` so the summary never gets counted as if it were a source note.

---

## Define Three Recall Questions

You will run these exact three questions against every memory architecture so results are comparable. They ship in the starter as `recall-questions.txt`, so there is nothing to type:

```text
Recall Q1: "Who owns the alert-routing area and what is their on-call rotation?"
Recall Q2: "Summarise the root cause of the 2026-Q1 incident that affected the dashboards service."
Recall Q3: "Which integration has the highest data volume and what does the team consider its main risk?"
```

Measure that file the same way you measured a note: it is 70 tokens, the fixed overhead every architecture pays.

```text
recall-questions.txt: 70
```

---

## Step 1: In-Context Memory (Baseline)

**Goal:** Load the entire notes corpus into the prompt, ask the three recall questions, record cost and quality.

First measure the whole corpus so the cost number is measured rather than guessed. Setup counted one note; run `tokens.py` over each `notes/topic-*.md` file and total them, or extend the script to accept several paths.

**Prompt:**

```text
Read every notes/topic-*.md file in full. Then answer the three questions in recall-questions.txt. Format your output as:

  ## In-Context Run
  - tokens_in_context: <total tokens of the notes you loaded, measured with tokens.py>
  - tokens_question_overhead: <tokens of recall-questions.txt, measured with tokens.py>

  ## Q1
  Answer: ...
  Source: notes/<file>.md (quote the supporting line)

  ## Q2
  Answer: ...
  Source: notes/<file>.md (quote the supporting line)

  ## Q3
  Answer: ...
  Source: notes/<file>.md (quote the supporting line)

Save the output to results/in-context.md.
```

**Expected result:** A `results/in-context.md` with three accurate answers, each carrying a supporting quote. Token cost is the headline number. The starter's corpus is 1,816 words and totals **2,859 tokens** under `cl100k_base`, so your total should be that exact number; a different one means you globbed something other than the eight `topic-*.md` files. You pay it on every turn that needs the corpus. This is the highest-recall, highest-cost architecture.

> Do not try to read a per-turn token total out of `/cost`. `/cost` is an alias of `/usage` and reports session-level cost and usage, not the tokens of a single turn. Measure the inputs you control with `tokens.py` instead, which is what makes the three architectures comparable at all.

---

## Step 2: Episodic Statefile

**Goal:** Compress the eight notes into a single `STATE.md` that holds the *condensed* facts, then answer the same questions reading only the statefile.

**Prompt:**

```text
Read every notes/topic-*.md file. Then write notes/STATE.md as a condensed, structured summary with these sections:

  # Lumen: Project State

  ## People
  [bullet list: name, role, area]

  ## Architecture
  [3 to 5 bullets of the most load-bearing facts]

  ## Pipelines
  [metric pipeline plus alert routing in 4 to 6 bullets]

  ## Incidents
  [one line per past incident: date, service, root cause]

  ## Integrations
  [bullet list: integration name, volume tier, top risk]

  ## Roadmap
  [3 near-term plus 1 long-term, one line each]

Target length: under 600 words.

Then measure it with tokens.py. Then in a fresh chat (use /clear), read only notes/STATE.md and answer the three questions from recall-questions.txt with the same output format as Step 1, but save to results/statefile.md.
```

**Expected result:** A `notes/STATE.md` under 600 words, then a `results/statefile.md` with three answers and source quotes now pointing at sections of `STATE.md` rather than at the raw notes. Token cost drops sharply: the solution's 509-word statefile measures **917 tokens**, roughly a third of the in-context corpus. Recall stays good for facts that survived the condensation and gets weaker for incidentally specific details (exact metric thresholds, for instance) that were summarised away.

Because `STATE.md` sits beside the notes but does not match `notes/topic-*.md`, re-running Step 1 or Step 3 will not ingest the summary as if it were a ninth source note.

---

## Step 3: Knowledge-Graph Memory via the Official MCP Server

**Goal:** Register the official MCP knowledge-graph memory server, ingest the notes as entities and relations, then answer the questions by retrieving from the graph instead of from prompt context.

### Setup: Register the MCP Memory Server

The official knowledge-graph memory server lives at [modelcontextprotocol/servers/src/memory](https://github.com/modelcontextprotocol/servers/tree/main/src/memory) and publishes as `@modelcontextprotocol/server-memory`. It stores entities (each with a type and a list of observations) and directed relations between them. Confirm it resolves before you register it:

```bash
npm view @modelcontextprotocol/server-memory version
```

Create `.mcp.json` in the lab project, at `labs/08-optimize/03-memory/memory-lab/.mcp.json`, and never at the repository root. The minimal registration is:

```json
{
  "mcpServers": {
    "memory": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-memory"]
    }
  }
}
```

With no `MEMORY_FILE_PATH` the server writes `memory.jsonl` inside its own package directory in the npx cache, which every project that starts the server this way then shares, and which disappears when the cache is cleared. A *relative* `MEMORY_FILE_PATH` is resolved against that same server directory, not against your project, so it has to be absolute. Prefer this form and substitute your own absolute path:

```json
{
  "mcpServers": {
    "memory": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-memory"],
      "env": { "MEMORY_FILE_PATH": "<absolute path to your memory-lab folder>/memory.jsonl" }
    }
  }
}
```

Restart Claude Code (`/exit`, then `claude`). A project-scoped server has to be approved before it connects: the first session after the restart asks you to approve it, and until you do, `claude mcp list` reports `memory: npx -y @modelcontextprotocol/server-memory - Pending approval (run 'claude' to approve)`. After approving, confirm with `/mcp` that `memory` is connected.

The running server identifies itself as `memory-server` version `0.6.3` on protocol `2025-06-18` and exposes nine tools:

| Tool | Kind |
|---|---|
| `create_entities`, `create_relations`, `add_observations` | write |
| `delete_entities`, `delete_observations`, `delete_relations` | destructive |
| `read_graph`, `search_nodes`, `open_nodes` | read only |

Note what `search_nodes` actually is: case-insensitive **substring matching** over entity names, entity types and observation strings. There are no embeddings and no similarity scoring anywhere in this server. That single fact predicts most of the recall behaviour you are about to measure.

### Ingest the Notes

**Prompt:**

```text
Use the memory MCP server to ingest the notes/topic-*.md files as a knowledge graph.

For each note file:
  1. Extract entities (people, services, integrations, incidents, dashboards). Each becomes an entity with an entityType and observations.
  2. Extract relations between entities ("owns", "depends_on", "affected_by", "integrates_with"). Each becomes a relation with from/to/relationType.
  3. Call create_entities and create_relations on the memory MCP tools to populate the graph.

Because search_nodes is substring matching, store the load-bearing prose verbatim as observations rather than paraphrasing it away.

After ingestion, call read_graph and save the structure (entity count, relation count, top 5 most-connected entities) to results/graph-summary.md.
```

**Expected result:** `/mcp` shows `memory` connected with no errors, and `graph-summary.md` shows something like 25 to 40 entities and 30 to 60 relations, with services and team members as the most-connected nodes. The knowledge graph is now queryable independently of conversation context, and it persists on disk at your `MEMORY_FILE_PATH`.

### Answer the Recall Questions

**Prompt:**

```text
In a fresh chat (/clear), do NOT read any files from notes/. Use only the memory MCP server's search_nodes and read_graph tools.

Answer the three questions from recall-questions.txt. For each, also report which memory tool call returned the answer, and measure the tokens of that tool's result with tokens.py so the retrieval cost is comparable to Steps 1 and 2.

Save the output to results/knowledge-graph.md.
```

**Expected result:** A `results/knowledge-graph.md` with three answers, each labelled with the MCP tool call that retrieved it and the measured size of what that call returned. A targeted `search_nodes` hit loads only the matched entities and their observations, which is a small fraction of the corpus; a fallback to `read_graph` loads everything and costs more than Step 1 did. Recall is good on relational questions (Q1, Q3) where the answer is an entity or an edge, and weak on the narrative question (Q2's root cause) unless the causal prose was stored verbatim as an observation, because substring matching cannot paraphrase.

---

## Step 4: Auto-Memory, Pinned Into the Lab

**Goal:** Let Claude Code write its own memory store from the corpus, then answer the same questions from the index plus whichever files it points at, and separate the cost you pay every turn from the cost you pay once.

The first three architectures are ones you build. This one already exists: auto-memory is on by default, and Claude Code decides for itself what is worth keeping. That makes it the only architecture here whose recall quality is set by a write policy rather than by a retrieval mechanism.

### Setup: Pin the Store Into the Lab

The store location is derived from the **git repository**, not from the folder you launched in, so every worktree and subdirectory of one repo shares a single directory at `~/.claude/projects/<project>/memory/`. This lab folder is inside the course repo, so an unpinned run would file Lumen notes alongside the course's own memories, and put them somewhere `tokens.py` cannot conveniently reach.

Create `.claude/settings.json` in the lab project, at `labs/08-optimize/03-memory/memory-lab/.claude/settings.json`, and substitute your own absolute path:

```json
{
  "autoMemoryEnabled": true,
  "autoMemoryDirectory": "<absolute path to your memory-lab folder>/auto-memory"
}
```

The value has to be absolute or start with `~/`, which is the same trap as `MEMORY_FILE_PATH` in Step 3 arriving from a different direction: a relative path here is not resolved against your project either. A project-scoped `autoMemoryDirectory` is honoured only after you accept the workspace trust dialog for the folder, the same gate that governs hooks.

Restart Claude Code (`/exit`, then `claude`), then run `/memory` and confirm the auto memory folder it offers to open is the one inside the lab.

### Write the Memories

**Prompt:**

```text
Read every notes/topic-*.md file. Then record, as auto-memory, what a future session would need in order to answer questions about Lumen without reading the notes again.

Keep MEMORY.md to one line per entry: a link and a short hook, nothing else. Put the detail in a separate file per area beside it: team and on-call rotation, architecture, metric pipeline, alert routing, incidents, integrations, dashboards, roadmap.

Give every memory file frontmatter with a name, a one-line description used to judge relevance before loading it, and a metadata.type of project, feedback, user or reference.

Then report the line count and the byte size of MEMORY.md, and say how each compares to the 200-line and 25KB limits it is loaded under.
```

**Expected result:** an `auto-memory/` folder holding `MEMORY.md` plus one file per area, and `/memory` opening that folder rather than the course repo's. The index is the file that loads at every session start, capped at the first 200 lines or 25KB, whichever comes first; everything past that is silently dropped on the next load, so this architecture fails by truncation where the others fail by cost. Measure both with `tokens.py`: the index is the recurring charge, the area files are read only when an index line looks relevant.

Claude wrote these files, so their exact token counts are yours and will not match anyone else's. Two things must hold regardless: the index is a small fraction of the 2,859-token corpus, and it sits well inside both limits.

### Answer the Recall Questions

**Prompt:**

```text
In a fresh chat (/clear), do NOT read any file under notes/. Work only from the auto-memory index and the memory files its lines point at.

Answer the three questions from recall-questions.txt with the same output format as Step 1. For each, name the memory file that answered it.

Measure auto-memory/MEMORY.md and every memory file you opened with tokens.py, and report the index cost separately from the file cost, because the index is charged on every turn and a file body only on the turn that reads it.

Save the output to results/auto-memory.md.
```

**Expected result:** A `results/auto-memory.md` with three answers, each naming the memory file behind it, and a two-part cost rather than a single number. Where an answer is thin, the cause is upstream: the write step dropped the fact, or the index line describing the file was too vague for it to look relevant. That is the difference between this architecture and the other three, and Step 6 audits it directly.

---

## Step 5: Four-Way Comparison

**Goal:** Tabulate the trade-offs across all four architectures.

**Prompt:**

```text
Read results/in-context.md, results/statefile.md, results/knowledge-graph.md, and results/auto-memory.md.

Produce results/comparison.md with this exact table, filling the token column from your tokens.py measurements rather than from estimates:

  | Architecture | Tokens per question | Q1 accuracy | Q2 accuracy | Q3 accuracy | Setup cost | Maintenance cost |
  |---|---|---|---|---|---|---|
  | In-context (Step 1) | | | | | none | none |
  | Statefile (Step 2) | | | | | one-time write | rewrite on note change |
  | Knowledge graph (Step 3) | | | | | MCP server plus ingest | re-ingest on note change |
  | Auto-memory (Step 4) | | | | | one settings entry plus one write pass | the model rewrites as it learns |

For the auto-memory row, give the token column as index-per-turn plus file-when-read rather than collapsing the two into one number.

Score accuracy as: Full (answer plus correct source), Partial (answer right, source missing or wrong), Wrong, or Refused.

Then write a verdict section, "When to reach for each", with one sentence per architecture.
```

**Expected result:** A `comparison.md` filled in with measured numbers. On the solution corpus the token column starts from 2,859 for in-context and 917 for the statefile, with the graph row varying per question depending on whether `search_nodes` hit or the run fell back to `read_graph`, and the auto-memory row carrying two figures because its index and its file bodies are charged on different schedules.

The expected pattern: in-context wins accuracy at high cost, the statefile is the best ratio for a stable corpus, the knowledge graph wins on relational questions at low retrieval cost while losing on narrative ones, and auto-memory lands near the statefile on recall while costing far less over a long session, because only the index recurs. The verdict typically lands on: use in-context for one-shot tasks, a statefile when you want to control the condensation yourself, auto-memory when the facts worth keeping are the ones that surface during the work, and a knowledge graph when your data is genuinely entity-and-relation shaped.

---

## Step 6: Audit the Schema and the Write Policy (Optional Bonus)

**Goal:** Look at the graph as a structure rather than as an answer source, judge how much of the corpus your ingestion schema captured, then apply the same scrutiny to what the write step chose to remember.

> This course ships no `/graphify` command, and there is no such Claude Code built-in or bundled marketplace skill. If you want automated graph extraction here, you have to supply the skill yourself at `.claude/skills/graphify/SKILL.md` inside this lab project. The step below is built on `read_graph`, which the server you already registered really does expose.

**Prompt:**

```text
Call read_graph and save the raw JSON to results/graph.json. Then write a short Node or Python script that reads it and reports:
  - entity count and relation count
  - degree (relations touching it) per entity, sorted descending
  - orphan entities with degree 0
  - entity types present, and how many entities carry each

Save the report to results/graph-audit.md.
```

Then ask Claude:

```text
Read results/graph-audit.md and the notes/topic-*.md corpus, then answer in results/graph-audit.md:
  - Which facts in the notes never became an entity, a relation, or an observation?
  - Which orphan entities exist only because a note mentioned a name in passing?
  - Q2 recalled poorly from the graph. Which specific observation, stored verbatim, would have fixed that?
  - Would you trust this ingestion schema on a corpus ten times this size, and what would you change first?
```

**Expected result:** A `results/graph-audit.md` that names the losses concretely. The recurring lesson is that a knowledge graph is only as good as the schema you ingested with: relations you did not model cannot be retrieved, and narrative causality survives only if you stored the prose verbatim as an observation. For a corpus of this size a careful manual ingestion wins on quality; at ten times the size the ingestion itself becomes the bottleneck, which is the point at which automated extraction stops being optional.

### Audit the Write Policy

The graph audit asks what your schema failed to model. The same question applies to Step 4, where the model chose what to write, so recall is capped by that choice long before retrieval gets a turn.

**Prompt:**

```text
Read auto-memory/MEMORY.md, every file it points at, and the notes/topic-*.md corpus. Then append a "Write policy" section to results/graph-audit.md answering:

  - Trigger: which facts were written that no future session will need, and which of them are the ones crowding the 200-line index?
  - Trust: does any memory record something as a rule about how to work that actually arrived from a note rather than from me?
  - Volatility: which entries go stale on a timescale of days (on-call rotation, roadmap dates, in-flight migrations), and does each one carry a re-verify instruction or an expiry?
  - Conflict: if a note is corrected tomorrow, which existing memory file gets updated, and which would end up contradicted by a second file landing beside it?

Then rewrite one index line so a future session would actually judge that file relevant to Q2, and say what was wrong with the original.
```

**Expected result:** A "Write policy" section naming specific files rather than restating the four fields. The finding that matters most is the volatility one: a memory holding the on-call rotation or a roadmap date reads as current forever unless it says otherwise, and the `modified` timestamp Claude Code stamps into the frontmatter is the only signal of its age. When a fact turns out to be wrong, the fix is to update or delete that file, never to add a correcting one beside it, because two contradictory memories retrieved together are worse than neither.

---

## What You Just Practised

| Architecture | Step | Best for |
|---|---|---|
| In-context loading | 1 | One-shot tasks where loading the corpus once is cheaper than building infrastructure |
| Statefile (episodic) | 2 | Ongoing project work where a condensed summary suffices and updates are infrequent |
| Knowledge graph via MCP | 3 | Entity-and-relation-shaped data where retrieval cost matters across many turns |
| Auto-memory with a pinned store | 4 | Facts that surface during the work, where only a capped index recurs per turn |
| Measured comparison instead of intuition | 5 | Any architecture choice you will have to defend later |
| Auditing a schema and a write policy against the corpus | 6 | Judging whether either will survive a larger corpus |

This finishes Module 08. You can now compress a harness ([Lab 01](lab-01-caveman-compress.md)), measure and evolve a skill ([Lab 02](lab-02-evolve-via-metrics.md)), and choose the right memory architecture for the recall task in front of you (this lab).
