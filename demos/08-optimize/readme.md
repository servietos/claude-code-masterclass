# Optimize the Agentic Harness for Cost and Continuous Learning

- Token cost across teams and sprints
- Caveman compression with zero rule loss
- Autoresearch loop: iterate, promote, revert
- Memory architectures: statefile and graph
- Prompt audit: dated instructions, stale references, contradictions

## Topics

| Topic | Description |
|-------|-------------|
| [01: Introduction](01-intro/readme.md) | Why context is a recurring cost: what CLAUDE.md charges on every turn, the four dimensions of optimization (context, memory, skills, workflow), and the autoresearch loop as the meta-strategy that keeps the harness improving. |
| [02: Caveman Compression](02-caveman-compression/readme.md) | Token counting and context compression on a TypeScript Fastify REST API: baseline measurement with js-tiktoken, caveman-mode rewrite targeting 60-75% reduction, and a rule-by-rule parity check that confirms no enforcement was lost in translation. |
| [03: Autoresearch Loop](03-autoresearch-loop/readme.md) | Skill quality experiments on this repo's own `class-dashboard` skill: a deterministic TypeScript scoring harness over captured runs, the three core metrics plus the domain metric that carries the skill's own risk, single-variable iteration discipline, and the promote/revert decision rule. |
| [04: Memory Architectures](04-memory-architectures/readme.md) | A four-way token benchmark in TypeScript comparing in-context loading, a STATE.md statefile summary, Claude Code's auto-memory index plus typed files, and knowledge graph retrieval on the same incident corpus, plus the write policy that caps what any of them can recall and a decision table mapping project shape to the right architecture. The graph approach is modelled with a static entity-relation file and a pre-retrieved subgraph prompt; no MCP server ships with the project. |
| [05: Prompt Audit](05-prompt-audit/readme.md) | `/doctor prompt-audit` and `/claude-api prompt-audit` over a harness: the target model the audit judges against, the pattern families from pressure language to stale references and contradicting files, the keep list, the confidence levels that decide what reaches the proposed diff, and the re-audit that closes the loop. |

## Demos

| Topic | Description |
|-------|-------------|
| [02: Caveman Compression](02-caveman-compression/demo-caveman-compression.md) | Install the shipped Fastify API starter, count baseline tokens with js-tiktoken, apply caveman compression targeting 60-75% reduction, and verify rule parity before swapping the file in. |
| [03: Autoresearch Loop](03-autoresearch-loop/demo-autoresearch-loop.md) | Run a full propose-evaluate-promote cycle on the live `class-dashboard` skill: baseline three captured runs, let the numbers pick the target metric, change one sentence, re-measure under identical conditions, and let the rule decide. |
| [04: Memory Architectures](04-memory-architectures/demo-memory-architectures.md) | Benchmark in-context loading, a STATE.md statefile, an auto-memory index plus the one file it points at, and knowledge graph retrieval on the same incident corpus, and read the per-question token cost side by side. The benchmark counts tokens; recall strength is a qualitative label, not a measurement. |
| [05: Prompt Audit](05-prompt-audit/demo-prompt-audit.md) | Audit a five-file harness with `/doctor prompt-audit`, verify the high-confidence findings against the project, narrow the audit to one skill with `/claude-api prompt-audit`, apply the proposed diff, and re-audit until no finding reaches the diff. |

Every demo has a presenter guide beside it (`demo-presenter-<slug>.md`) holding the same
teaching in timed beats, for delivery without running the demo live.

## Starter and Solution Folders

Work in each topic's starter (for example `caveman-compression/`); the finished, runnable result is beside it in `<starter>-solution/`.

## Labs

| Lab | Description |
|-----|-------------|
| [Compress a Bloated Harness with Caveman Mode](../../labs/08-optimize/lab-01-caveman-compress.md) | Rewrite a bloated `CLAUDE.md` as a caveman, measure the token drop with tiktoken, verify behaviour holds, and codify the prompt as a skill. |
| [Evolve a Skill with Deterministic Experiments](../../labs/08-optimize/lab-02-evolve-via-metrics.md) | Measure a skill with a deterministic harness over `claude -p --output-format json`, then run a propose-evaluate-revert loop to improve it. |
| [Compare Four Memory Architectures on the Same Recall Task](../../labs/08-optimize/lab-03-memory-architectures.md) | Measure in-context loading, an episodic statefile, the MCP knowledge-graph server, and Claude Code's auto-memory with one token counter. |

## Knowledge Check

### CQ-01: Where Verbose Output Belongs

An agent must search a large repository, and the search returns thousands of lines. Where should that output land?

- A) In the main agent's context, so it can reason over the complete result set.
- B) In a subagent that runs the search, processes the output, and returns only the consolidated list the coordinator needs.
- C) In a scratchpad file the main agent reads back in full on the next turn.
- D) Nowhere: raise `max_tokens` so the main agent can absorb it without truncation.

**Answer: B**

Delegating a verbose discovery task to a subagent keeps the raw output in a context that gets discarded, and returns only the distilled answer to the coordinator that has to keep planning. Option C moves the bytes to disk and then reads them straight back, which costs the same context. Option D raises the ceiling without changing the fact that the coordinator is now full of noise.

### CQ-02: Compact or Clear

A session is at 90% of its context limit after a long exploration phase, and the developer still needs the architectural understanding it produced. What is the right move?

- A) `/clear`, then re-run the exploration commands to rebuild a smaller picture.
- B) `/compact`, which distils the history into a summary that preserves the goals and findings.
- C) Start a new session and paste the raw command output back in.
- D) Delete the oldest messages manually until the window has room.

**Answer: B**

`/compact` replaces the conversation with a high-fidelity summary, which is exactly the trade you want when the *conclusions* matter and the raw transcript does not. `/clear` discards those conclusions, and options C and D pay to reconstruct or hand-prune what compaction does in one step.

### CQ-03: Surviving a Long Session

An agent correctly identifies a critical detail in the first ten minutes of a two-hour audit, then contradicts it in the final report. What is the architectural fix?

- A) Lower the temperature so recall is more deterministic.
- B) Require the agent to write key findings to a scratchpad file and reference that file when producing the report.
- C) Split the audit across two agents so neither runs long enough to degrade.
- D) Re-run the audit and compare the two reports for discrepancies.

**Answer: B**

This is context degradation: the early finding was pushed out or overwritten as the window filled. Externalizing key findings to a file gives them a home outside the context window and a deterministic point to read from at report time. Temperature does not govern what is still in the window, and option D detects the problem without preventing it.

### CQ-04: Trimming at the Tool Boundary

A tool returns thousands of lines of JSON when only two fields matter, and repeated calls flood the context. What is the cleanest fix?

- A) Instruct the agent to ignore the irrelevant fields when reading the response.
- B) Wrap the tool so it returns only the needed fields before the result enters the context.
- C) Have the agent delete previous tool results from the history before each new call.
- D) Convert the output from JSON to YAML to reduce the token count.

**Answer: B**

Trimming at the tool boundary means the noise never enters the context at all, which is both cheaper and more reliable than asking the model to look past it. Option A still pays for every token. Option D shaves a percentage off a problem that is orders of magnitude too large.

### CCA-F Q37 (Domain 2: Tool Design and MCP Integration)

You are tasked with modifying the authentication flow in a 500-file repository with no prior knowledge of the codebase. A junior developer suggests finding all files containing 'auth' in the name and Reading them all at once to build context. Why should you reject this approach and what should you do instead?

- A) Reject it because `Glob` cannot filter by filename. Instead, use Bash `find` to locate all 'auth' files, then `Read` the entire list.
- B) Reject it because `Edit` is faster for tracing. Instead, use `Edit` to inject logging into all files containing 'auth'.
- C) Reject it because authentication flows are in the database. Instead, `Read` the database schema and migration files.
- D) Reject it because Reading all files upfront overwhelms the context window. Instead, use `Grep` to find the login entry point and `Read` files sequentially.

**Answer: D**

Reading all files upfront creates a bloated context, degrading performance and increasing token usage. The recommended approach is to use Grep to locate a relevant entry point, then sequentially Read files by following imports and function calls.

### CCA-F Q51 (Domain 3: Claude Code Configuration and Workflow)

A developer observes that a long-running Claude agent, which was correctly adhering to the project's strict TypeScript interfaces in the morning, begins generating code with `any` types in the afternoon. The codebase has not been modified. What is the most effective first step to troubleshoot this degradation?

- A) Pin the `@anthropic-ai/sdk` version to an older release with stricter type inference defaults.
- B) Use a command to inspect the agent's current context or memory, comparing its state from the morning session to the afternoon session to confirm if the relevant TypeScript rule files have been dropped.
- C) Check Anthropic's status page for recent infrastructure incidents.
- D) Move all TypeScript rules from `.claude/rules/` into the root `CLAUDE.md`.

**Answer: B**

Inspecting the agent's current context or memory is the most direct way to confirm whether the rule files have been dropped due to context window limitations, verifying the root cause of the behavioral degradation.

### CCA-F Q83 (Domain 5: Context Management and Reliability)

An autonomous coding assistant needs to find all instances of deprecated lifecycle methods across 500 React components. The main agent runs `grep`, reads the massive terminal output directly into its context, and then attempts to plan the upgrade, frequently hitting context limits. How should the architect redesign this workflow?

- A) Increase the `max_tokens` parameter on the main agent to accommodate the large `grep` outputs.
- B) Instruct the main agent to write the raw `grep` output to a scratchpad file, then read back only the file paths.
- C) Programmatically trigger the /compact command after every single `grep` execution.
- D) Spawn a specialized subagent to execute the `grep` commands, process the verbose output, and return only a consolidated list of affected files to the main coordinating agent.

**Answer: D**

Spawning a specialized subagent for data-intensive tasks is a recommended context management pattern. Processing and summarizing raw output into a concise, actionable format allows the main coordinator to maintain a clean context focused on high-level planning.

### CCA-F Q85 (Domain 5: Context Management and Reliability)

An AI database administrator agent uses an `execute_explain_plan` tool returning thousands of lines of JSON. When comparing three query variations, the agent forgets the user's original performance goal by the third tool call, even though only `Total_Cost` and `Execution_Time` are relevant. How should the architect optimize this interaction?

- A) Switch the tool output format from JSON to YAML to consume fewer tokens.
- B) Instruct the agent to use a `delete_message` tool to remove previous execution plans from the context history.
- C) Use a vector database to store the execution plans and pass only semantic embeddings to the agent.
- D) Implement a wrapper around the `execute_explain_plan` tool that trims the verbose JSON output to only return the `Total_Cost` and `Execution_Time` fields before the result accumulates in the context.

**Answer: D**

Trimming the verbose output at the tool boundary prevents irrelevant data from accumulating in the context window, keeping the agent focused on the comparison, reducing token usage, and preserving the original goal across multiple tool calls.

### CCA-F Q86 (Domain 5: Context Management and Reliability)

During an automated security audit, the coordinating agent correctly identifies a proprietary hashing function in the first 10 minutes. An hour later, generating the final vulnerability report, it incorrectly states the system uses standard SHA-256 and misses a critical flaw. What is the root cause and the most appropriate architectural solution?

- A) The agent experienced context degradation; the architecture should require the agent to maintain and reference a scratchpad file of key findings.
- B) The agent's temperature was set too low, preventing creative recall.
- C) The crash recovery manifest was corrupted; the system should validate its integrity using a checksum.
- D) The subagent delegation failed; the main agent should perform all cryptographic analysis directly.

**Answer: A**

This illustrates context degradation, where early findings are lost or overwritten as the context window fills. Requiring a scratchpad file of key findings ensures critical discoveries are preserved and explicitly used during final report generation.

### CCA-F Q88 (Domain 5: Context Management and Reliability)

A developer using Claude Code to explore a complex Python backend runs several verbose `tree` and `cat` commands, and the CLI warns the session is at 90% of its context limit. The developer still needs to write a new feature based on this structure but wants to avoid losing the architectural context. What is the most effective action?

- A) Spawn a subagent to write the new feature, instructing it to replicate the parent's architectural context.
- B) Export the current state to a manifest file, restart the CLI, and manually paste the raw `tree` output back in.
- C) Execute the `/compact` command to have the model summarize the verbose discovery output, reducing context usage while retaining key architectural insights.
- D) Delete the system's scratchpad file to free up context space, then re-run the `tree` command.

**Answer: C**

The `/compact` command is a primary strategy for context engineering within Claude Code. It distills the conversation history into a high-fidelity summary, preserving key goals and progress.

### CCA-F Q90 (Domain 5: Context Management and Reliability)

A travel booking agent handles multi-city itineraries where users change dates and flight numbers over a 50-turn conversation. The bot occasionally books the wrong flight because it is confused by earlier, discarded preferences. What is the best way to manage this context?

- A) Reduce the context window to only the last 5 turns.
- B) Ask the user to re-type their entire desired itinerary before executing the final booking tool.
- C) Use a higher top_p setting to increase determinism.
- D) Implement a background process that extracts the currently agreed-upon transactional facts into a persistent 'current itinerary' block injected at the top of every prompt.

**Answer: D**

Extracting and maintaining a persistent, structured 'current itinerary' block ensures the model has an authoritative, up-to-date source of truth, preventing confusion from older, discarded preferences.

### CCA-F Q99 (Domain 5: Context Management and Reliability)

An AI system synthesizes information about a product from three documents: a January press release, a March technical blog post detailing a feature change, and a June user manual with final specifications. The summary incorrectly presents these as three separate, competing product descriptions. What is the most effective way to enable a correct temporal interpretation?

- A) Feed all documents into the context window at once as a single, unstructured block of text.
- B) Use a vector search to find the document most semantically relevant to 'final product specification' and pass only that one to the synthesis agent.
- C) Architect the system to first extract key events from each document into a structured list of objects with a 'publication_date' and 'event_description', then pass this time-sorted list to a synthesis agent prompted to write a chronological narrative.
- D) Only process the most recent document to establish a single source of truth.

**Answer: C**

Extracting key events into structured objects with publication dates creates explicit temporal metadata. Deterministically sorting them before synthesis provides a clear chronological framework and resolves version conflicts based on provenance.

### CCA-F Q101 (Domain 5: Context Management and Reliability)

An engineer designed an agentic system to find all test files in a massive repository. The main agent executes `find . -name "*test*"`, returning 15,000 lines directly into its context, and immediately fails to respond coherently to subsequent prompts. What architectural anti-pattern did the engineer commit?

- A) Failing to increase the `top_p` parameter to handle the large volume of context.
- B) Failing to delegate verbose discovery tasks to a subagent that could process the output and return only a summarized list or specific insights to the main agent.
- C) Failing to use a scratchpad file to persist the 15,000 lines across conversation turns.
- D) Failing to implement a crash recovery manifest before running the `find` command.

**Answer: B**

In large-scale codebase exploration, verbose discovery tasks should be delegated to a subagent that processes the raw output and returns only a summarized list, preventing context overload in the main agent.
