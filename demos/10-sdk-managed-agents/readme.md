# Build and host agents with the Agent SDK and Managed Agents

- Agent SDK: query() and sessions
- Agent SDK: parallel agents, orchestrator
- Managed Agents: Agent, Environment, Session
- Managed Agents: files, SSE stream
- Managed Agents: vaults, versions, policies
- Managed Agents: MCP servers, skills
- Human-in-the-Loop: approval gates
- Multiagent: outcomes, memory stores

## Topics

| Topic | Description |
|-------|-------------|
| [01: Core API Surface](01-sdk-basics/readme.md) | Where the Agent SDK sits next to the Messages API, Claude Code and Managed Agents; the `query()` async iterator and its options; resume, continue and fork; custom tools as in-process MCP servers; typed output; and the API-level output controls `tool_choice`, Structured Outputs and the Message Batches API. |
| [02: Parallel Agents](02-sdk-parallel-agents/readme.md) | The parallel pattern with `Promise.all`, the canary isolation test, the orchestrator pattern, and typed contracts across agent boundaries. |
| [03: Managed Agents Foundations](03-agent-foundations/readme.md) | When the hosted runtime pays off over running the loop yourself, the three resources (Agent, Environment, Session), and the session state machine. |
| [04: Sessions & Streaming](04-agent-sessions-streaming/readme.md) | Cloud containers with networking and file mounts, the SSE event model, mid-execution steering, session threads, and a 25-minute end-to-end demo that touches every primitive in one flow. |
| [05: Production Features](05-agent-production-features/readme.md) | Vaults with automatic token refresh, webhooks on `session.status_idled`, per-tool permission policies, agent versioning, Console observability, scheduled deployments, and the `ant` CLI for YAML-versioned resources. |
| [06: Tools & MCP](06-agent-tools-mcp/readme.md) | The two extension points on an Agent: MCP servers declared alongside an `mcp_toolset` grant with its own permission policy, and skills that mount a procedure into the container and load on demand. |
| [07: Human-in-the-Loop](07-agent-human-in-the-loop/readme.md) | The two blocking handoffs that drive approval gates, a 20-minute custom-tool HITL demo with allow and deny verdicts, and a migration path from the Messages API and the Agent SDK. |
| [08: Multiagent, Outcomes & Memory](08-agent-multiagent/readme.md) | Delegation with the `multiagent_20261001` block and session threads, outcomes graded against a rubric, memory stores that outlive the session, and one budget shared by every thread. |

Topics 01 and 02 run the agent loop in your own process with the Agent SDK in TypeScript. Topics 03 to 08 hand the same loop to Anthropic's cloud with Managed Agents in Python.

## Demos

| Topic | Description |
|-------|-------------|
| [01: Core API Surface](01-sdk-basics/demo-messages-api-to-sdk.md) | Four-step progression from a streaming `query()` call to a Zod-validated CI exit-code script. |
| [02: Parallel Agents](02-sdk-parallel-agents/demo-parallel-reviewers.md) | Three specialist agents review a flawed auth file in parallel, then an orchestrator synthesizes a typed verdict. |
| [03: Managed Agents Foundations](03-agent-foundations/demo-session-lifecycle.md) | Creates all three resources, polls one Session from `running` to `idle`, reads the persisted event log, and cleans up the two resources that are safe to delete. |
| [04: Sessions & Streaming](04-agent-sessions-streaming/demo-first-agent.md) | Uploads a CSV, mounts it on a Session, streams the analysis over SSE, and downloads the artifact the agent wrote. |
| [05: Production Features](05-agent-production-features/demo-agent-versioning.md) | Optional. Publishes two Agent versions, pins a Session to each, and shows the same `bash` call running unattended on one and pausing for `user.tool_confirmation` on the other. |
| [06: Tools & MCP](06-agent-tools-mcp/demo-mcp-and-skills.md) | Optional. Attaches the Microsoft Learn MCP server and the `docx` skill to one Agent, then reads the event log while a single turn searches the docs and writes a document you download. |
| [07: Human-in-the-Loop](07-agent-human-in-the-loop/demo-approval-gate.md) | Optional. Declares a custom tool, parks the Session at `requires_action`, and resumes it with both an allow and a deny verdict. |
| [08: Multiagent, Outcomes & Memory](08-agent-multiagent/demo-feedback-digest.md) | Optional. Turns one agent into a lead with a Haiku reader subagent, a rubric-graded outcome, a memory store and a session budget. |

Every demo has a presenter guide beside it (`demo-presenter-<slug>.md`) holding the same
teaching in timed beats, for delivery without running the demo live.

Every runnable project folder in this module is the starter you code in, and it stays pristine: no `node_modules`, no lockfile, no build output. Its finished counterpart sits beside it as `<starter>-solution/`, and that is where installs, lockfiles and runs live.

The TypeScript projects in topics 01 and 02 pin `@anthropic-ai/claude-agent-sdk` 0.3.302; install them with `npm install`. The Python projects from topic 03 on install with `pip install -r requirements.txt`. Topics 03 to 07 target `anthropic>=0.118.0`, because earlier releases have no `client.beta.agents` namespace at all, and topic 08 needs `anthropic>=1.15.0` for memory stores and the multiagent types.

> **Note:** Get your API key from the [API keys page of the Claude Console](https://platform.claude.com/settings/keys). On a Max or Team plan, [claim your monthly API credits](claim-funds.md) first.

## Labs

| Lab | Description |
|-----|-------------|
| [Embed Claude in a TypeScript Program](../../labs/10-sdk-managed-agents/lab-01-sdk-embed-claude.md) | Spawn Claude from inside your own program: one-shot calls, streaming, session resume, custom tools, typed output schemas, and a CI script. |
| [Run Parallel SDK Agents With Session Isolation](../../labs/10-sdk-managed-agents/lab-02-sdk-parallel-agents.md) | Build a review pipeline from three parallel SDK sessions plus an orchestrator that reconciles their findings, packaged as a CI job. |
| [Build a Managed Agent for Codebase Triage](../../labs/10-sdk-managed-agents/lab-03-agent-codebase-triage.md) | Mount a broken Python repo into a cloud Session and stream the fix loop, then publish a second Agent version with a custom tool and resume the parked Session with both verdicts. |
| [Review Code with Specialist Subagents, a Rubric and Team Memory](../../labs/10-sdk-managed-agents/lab-04-agent-review-team-memory.md) | Two read-only reviewer subagents, a graded review, a read-only conventions store and a read-write history a second session recalls. |

## Knowledge Check

### CQ-01: The Link Between Action and Observation

An application executes a tool and appends the result as plain text to the end of the last user message instead of using a `tool_result` block. The model starts hallucinating outputs and loses track of which calls it has made. Why?

- A) Plain text bypasses the model's safety filters, corrupting its situational awareness.
- B) Plain text has no `tool_use_id`, so the explicit link between the assistant's call and its result is broken and the model cannot map observations to actions.
- C) User messages are reserved for human input and cannot carry tool data at all.
- D) Plain text cannot carry an error flag, so every result reads as a success.

**Answer: B**

The Messages API expects a structured action-observation loop: `tool_use` from the assistant, `tool_result` from the user, joined by a matching `tool_use_id`. That id is what provides provenance. Without it the model loses the logical thread and starts inventing results. Option D names a real secondary consequence but not the root cause.

### CQ-02: Releasing a Forced Tool Call

A pipeline sets `tool_choice: {"type": "any"}` so the agent never replies conversationally. After the last step succeeds, the agent loops back to the first tool instead of stopping. What is the fix?

- A) Reduce the tool count so the agent has fewer options to re-evaluate.
- B) Switch `tool_choice` back to `auto` after the final required call, so the agent may stop and answer.
- C) Add a `return_status` field to the last tool's response so the agent knows it succeeded.
- D) Move the later tools to a separate subagent so the first agent has only one tool.

**Answer: B**

`any` forces a tool call on every turn, including the turn after there is nothing left to do. It is a per-request setting, so the pipeline releases it once the required sequence is complete and the model regains the option to produce a final message. The other options work around a constraint that the caller is imposing.

### CQ-03: Guaranteeing the Shape

A CI step needs the model to return a JSON object matching a fixed schema, every time. Which mechanism provides a guarantee rather than a likelihood?

- A) A detailed example of the desired JSON in the system prompt plus an instruction to follow it exactly.
- B) Structured Outputs: a JSON Schema supplied through `output_config.format`, which constrains decoding at the token level.
- C) A post-processing script that validates the output and repairs common structural errors.
- D) Zod validation on the parsed response, which throws on a mismatch.

**Answer: B**

Structured Outputs prevents a non-conforming response from being generated; everything else detects one after the fact. Zod is still valuable as a boundary check in SDK code, but it validates rather than constrains, so it answers a different question. Prompt examples raise the odds and guarantee nothing.

### CQ-04: Nullable Fields in an Extraction Schema

Clinical notes sometimes mention no prescribed medication. The model inconsistently omits the key, emits `"N/A"`, or invents a plausible drug. What resolves it?

- A) A system prompt requiring the key always be present and set to `"N/A"` when absent.
- B) A Structured Outputs schema declaring the field as `["string", "null"]`, so absence has an explicit representation.
- C) Few-shot examples in the prompt demonstrating a null value for the missing case.
- D) A post-processing script that inserts null when the key is missing.

**Answer: B**

An explicit null branch in the schema gives absence a legal value, so the model can represent "not mentioned" without omitting the key or fabricating content. Type arrays cost more to compile but are fully supported. The other three either encode a sentinel string as data or repair the output after the model already guessed.

### CQ-05: Batch or Synchronous

Which workload belongs on the Message Batches API?

- A) Inline code completions in an IDE extension, to control cost at high concurrency.
- B) Reprocessing five million legacy records overnight, where cost matters and nobody is waiting.
- C) A support bot replying to a live customer, because batching smooths traffic spikes.
- D) Any workload above a thousand requests, regardless of latency requirements.

**Answer: B**

The Batches API trades latency for cost with a completion window of up to 24 hours and no SLA inside it. That is right for overnight bulk work and wrong for anything a human is waiting on, which rules out A and C. Volume alone does not decide it; the question is whether anyone is blocked on the answer.

### CQ-06: Environment or Session

A team runs many analyses that share one container image but each mount a different input file. What belongs where?

- A) One Environment per analysis, each with its own file mounted at creation.
- B) One reusable Environment as the container template, with each Session mounting its own file as a resource.
- C) One Session reused across analyses, remounting a new file between runs.
- D) Neither; files must be streamed as base64 on every turn, as in the Messages API.

**Answer: B**

The Environment is the reusable container definition: package set, networking policy, mount point. Mounts belong to the Session, so one Environment can back many Sessions that each mount something different, and you avoid paying the cold-start cost per run. Option D describes the Messages API limitation that file mounts exist to remove.

### CQ-07: Opening the Stream

A client subscribes to a Session's event stream immediately after sending the first `user.message`, and the first few events are missing. What went wrong?

- A) The stream needs a replay window configured at Session creation.
- B) The stream carries only what happens after it opens and has no replay, so it must be opened before the first event is sent.
- C) The client subscribed to the wrong event family and the events were filtered out.
- D) Events emitted before the first `session.status_idle` are always suppressed.

**Answer: B**

Open the stream first, then send. Anything emitted before the subscription is gone from the stream. The companion rule covers reconnects: list the persisted events and dedupe by event id, because what was emitted during the disconnect is still queryable even though the stream will not replay it.

### CQ-08: Two Gates, Two Replies

An agent calls a tool your application implements, and the Session parks at `requires_action`. What does the client send back?

- A) `user.tool_confirmation` carrying the `tool_use_id`, allowing or denying the call.
- B) `user.custom_tool_result` carrying the `custom_tool_use_id` and the actual result.
- C) Either one; the platform accepts both and routes by Session state.
- D) A new `user.message` describing the outcome in prose.

**Answer: B**

The two handoffs are distinct and conflating them is the usual source of 400s. A permission policy gates a tool the platform knows how to run, so the reply is an allow or deny confirmation. A custom tool has no implementation on Anthropic's side, so your reply carries the result itself.

### CQ-09: Restricting an Agent's Toolset

A hosted agent must be able to read files and nothing else. Which knob enforces that?

- A) The `allowed_tools` permission allowlist, which auto-approves the read tool and denies everything else.
- B) The `tools` parameter, which defines the agent's toolset, with the read tool as its only entry.
- C) A system prompt instructing the agent to use only the read tool.
- D) Filesystem permissions on the mounted directory, set to read-only.

**Answer: B**

`tools` defines what the agent has; `allowed_tools` is a permission allowlist that auto-approves calls without restricting which tools exist. Least privilege means removing the capability, not pre-approving a subset of it. Option D is a useful second layer but does not stop the agent from attempting other tools.

### CQ-10: When the Gate Should Fire

A user in a billing dispute says "get me a manager". The agent has a working `dispute_charge` tool. What should it do?

- A) File the dispute first, then transfer, so the manager inherits a resolved case.
- B) Escalate immediately, without investigating or using the tool.
- C) Ask for the transaction date to verify the charge before escalating.
- D) Explain that it can file the dispute now, and ask whether the user still wants a manager.

**Answer: B**

An explicit request for a human on a sensitive financial matter is honoured immediately. Every other option overrides a request the user was entitled to make, whether by acting first, gating on a verification question, or negotiating. The design principle is that human oversight is not something the agent gets to talk the user out of.

### CCA-F Q4 (Domain 1: Agentic Architecture and Orchestration)

An agentic loop includes a `capture_screenshot` tool. When Claude calls this tool, the application successfully captures a base64-encoded PNG image of the current web page. The developer needs to pass this image back to Claude so it can analyze the UI. How should the developer construct the `tool_result` block to include the image?

- A) Convert the base64 image to a URL and pass the URL as a plain text string inside the tool_result block.
- B) Append the image as a separate user message immediately following the user message that contains the tool_result block.
- C) Images cannot be passed inside tool_result blocks; the developer must restart the conversation and provide the image in the initial prompt.
- D) Include an image content block containing the base64 data and media type within the content array of the tool_result block.

**Answer: D**

In the Anthropic Messages API, the `tool_result` block contains a `content` field that accepts an array of content blocks, which can include `text` and `image` blocks containing base64 data and the media type.

### CCA-F Q8 (Domain 1: Agentic Architecture and Orchestration)

An AI architect is managing two active sessions: Session A, containing a large volume of raw system logs, and Session B, containing the historical context and ongoing reasoning for a root cause analysis. The architect needs to continue the root cause investigation and also begin a separate architecture analysis for a proposed fix. Which session management strategy is most appropriate?

- A) Resume Session B; Start a new session for the architecture analysis.
- B) Start new sessions for both tasks, as any interruption requires a fresh context window.
- C) Resume both Session A and Session B, as Claude can automatically detect stale log data.
- D) Resume Session A; Start a new session for the log queries with a summary of the incident.

**Answer: A**

Resuming Session B preserves the valuable reasoning and narrative history of the investigation. Starting a new session for the architecture analysis ensures a clean, focused context window, isolating it from the investigation's history and preventing token waste.

### CCA-F Q13 (Domain 1: Agentic Architecture and Orchestration)

A cybersecurity agent uses a `scan_port` tool. The developer executes the tool and appends the result as a plain text string to the end of the last `user` message, rather than using a structured `tool_result` block. Claude begins hallucinating tool outputs and loses track of which ports it has scanned. Why does this cause model degradation?

- A) Plain text strings do not support the `is_error` flag, so the model misinterprets every scan result as a successful connection.
- B) Plain text strings bypass the model's internal safety filters, causing it to hallucinate malicious port activity.
- C) The developer must use a `system` message to inject plain text results, as `user` messages are strictly reserved for human input.
- D) Appending plain text instead of a structured `tool_result` block breaks the explicit linkage between the assistant's `tool_use_id` and the result, degrading the model's ability to reason about the action.

**Answer: D**

Claude's Messages API requires a structured action-observation loop where a tool_use is followed by a tool_result containing a matching tool_use_id. This linkage provides provenance and allows the model to reliably map observations back to specific actions.

### CCA-F Q19 (Domain 1: Agentic Architecture and Orchestration)

A data engineering team has spent 15 turns with Claude analyzing data skew in a PySpark ETL pipeline. They now want to evaluate two distinct architectural solutions: a broadcast hash join versus salting the skewed keys. Which session management strategy provides the most accurate comparison?

- A) Resume the session, implement the broadcast join, then use `--revert` to undo those turns before asking for the salting approach.
- B) Start two completely new sessions, providing the raw PySpark scripts to each.
- C) Continue in the same session, asking Claude to write both implementations sequentially.
- D) Use `fork_session` from the current state to create two isolated branches, allowing Claude to develop and evaluate each optimization strategy without context cross-contamination.

**Answer: D**

Forking is the ideal architectural pattern for A/B testing distinct solutions. It preserves the shared investigative context as a common baseline while creating isolated branches, preventing context leakage between them.

### CCA-F Q27 (Domain 2: Tool Design and MCP Integration)

A data pipeline agent has `fetch_record`, `transform_record`, and `load_record` tools. An architect sets `tool_choice: {"type": "any"}`. Production logs reveal that after successfully calling `load_record`, the agent gets stuck in a loop, often attempting to call `fetch_record` again. What is the primary cause and how should it be resolved?

- A) The `load_record` tool's response is missing a `return_status` field, causing the agent to assume the load failed.
- B) The agent has too many tools; `transform_record` and `load_record` should move to a separate sub-agent.
- C) The `tool_choice: {"type": "any"}` configuration forces the model to call a tool on every turn. The architect should switch to `{"type": "auto"}` after the final `load_record` step.
- D) The `any` configuration is unreliable for agents with more than one tool; the architect must switch to `{"type": "auto"}` for the entire process.

**Answer: C**

`tool_choice: {"type": "any"}` compels the model to use a tool in the current turn. The correct approach is to manage the tool_choice state, switching to `{"type": "auto"}` once the tool sequence is complete so the model can generate a final conversational response.

### CCA-F Q49 (Domain 3: Claude Code Configuration and Workflow)

An architect is integrating a third-party `/security-scan` tool using the Anthropic Agent SDK. To enforce least privilege, what is the most direct and effective method within the SDK to ensure the agent is only provided with the `ReadFile` tool?

- A) Add a system prompt instructing it to 'Only use the `ReadFile` tool and do not modify any files.'
- B) Configure the `tools` parameter in the Agent SDK's query options to include only the `ReadFile` tool.
- C) Run the agent in a sandboxed environment with the source directory set to read-only.
- D) Configure the `allowed_tools` parameter in the Agent SDK's query options to include only the `ReadFile` tool.

**Answer: B**

The tools parameter restricts which built-in tools are available to an agent. Official documentation confirms that tools defines the agent's toolset, while allowed_tools is a permission allowlist that auto-approves tools but does not restrict them.

### CCA-F Q62 (Domain 3: Claude Code Configuration and Workflow)

A DevOps engineer needs a model's output to be a JSON object containing a specific array of strings, but the current implementation sometimes produces malformed JSON. According to Anthropic's documentation, what is the most reliable method to ensure the model consistently returns valid JSON adhering to the required schema?

- A) Add a detailed example of the desired JSON array format to the system prompt with a `response_format` field.
- B) Use the 'Structured Outputs' feature by defining a JSON schema and providing it via the `output_config` parameter with `format` set to the schema, ensuring the output matches through constrained decoding.
- C) Define a tool with an `input_schema` specifying the array structure and set `tool_choice` to force that tool.
- D) Implement a post-processing script that validates and attempts to correct the output.

**Answer: B**

Structured Outputs is the officially recommended method for guaranteeing JSON schema compliance. The GA API uses output_config.format to specify the JSON Schema; the output_format parameter is deprecated. This constrains token generation to match the schema.

### CCA-F Q63 (Domain 4: Prompt Engineering and Structured Output)

A sentiment analysis pipeline uses a tool with a `sentiment` enum restricted to `["positive", "negative", "neutral"]`. For highly sarcastic or contradictory reviews, Claude randomly selects "positive" or "negative", skewing analytics. How should you adjust your schema design?

- A) Use `tool_choice: {"type": "auto"}` so Claude can refuse to answer.
- B) Force Claude to output a chain-of-thought reasoning field before the sentiment field.
- C) Add `"unclear"` to the `sentiment` enum values and instruct Claude to use it for ambiguous or highly sarcastic text.
- D) Change the schema to output a float between -1.0 and 1.0.

**Answer: C**

Adding an explicit enum value such as 'unclear' provides the model with a safe structured option when text doesn't fit the standard categories, reducing forced random guesses and allowing easy filtering of data points needing manual review.

### CCA-F Q64 (Domain 4: Prompt Engineering and Structured Output)

A marketing agency submits 100,000 product descriptions to the Message Batches API at 9:00 AM. At 3:00 PM the batch status is still `processing`. The campaign manager urgently needs the exact completion time. What is the correct architectural response?

- A) The Batch API processes at a guaranteed 20,000 requests per hour, so the job finishes at 2:00 PM.
- B) Call the `/batch/{id}/expedite` endpoint to force completion within 60 minutes.
- C) The Batch API provides no guaranteed latency SLA other than an up to 24-hour processing window, so an exact completion time cannot be predicted.
- D) The batch has stalled; cancel it and resubmit to reset the queue priority.

**Answer: C**

The Message Batches API trades lower cost for a completion window of up to 24 hours. Because the API does not provide a deterministic completion time or guaranteed processing rate, an architect cannot provide a specific ETA.

### CCA-F Q65 (Domain 4: Prompt Engineering and Structured Output)

A customer service bot uses `tool_choice: {"type": "auto"}` with a single `log_complaint` tool. For short messages like "Fix my billing!", the bot often replies conversationally instead of calling the tool. You need it to always call the tool. Which configuration change achieves this?

- A) Add a second tool called `log_short_complaint`.
- B) Increase the `temperature` parameter to 1.0.
- C) Change `tool_choice` to `{"type": "any"}`.
- D) Add a system prompt telling Claude to always use the tool.

**Answer: C**

Setting tool_choice to `{"type": "any"}` forces Claude to use one of the provided tools. Since log_complaint is the only tool available, this guarantees it will be called instead of generating a natural language response.

### CCA-F Q66 (Domain 4: Prompt Engineering and Structured Output)

A system extracts a list of `key_personnel` requiring an array of objects with `name` and `title`. For one document the model outputs a single object with comma-separated names instead. If the architect implements a retry-with-error-feedback loop, what is the expected outcome and why?

- A) The retry will succeed, but only with a completely different prompt and temperature setting.
- B) The retry will succeed because the source document contains the necessary information, and the error feedback explicitly describes the schema violation.
- C) The retry will fail because the model cannot restructure data once it has decided on an initial format.
- D) The retry will fail because structural output errors indicate the required information is absent from the source.

**Answer: B**

The source document contains the necessary information, and the error feedback explicitly describes the schema violation, allowing the model to identify its structural mistake and reformat the data correctly.

### CCA-F Q69 (Domain 4: Prompt Engineering and Structured Output)

A team migrating to native tool use passes the JSON schema in the `tools` array and sets `tool_choice: {"type": "tool", "name": "extract_data"}`. Their application crashes because it is still parsing the `text` block, which is now often empty. What architectural change is required?

- A) Inject the JSON schema into the system prompt in addition to the `tools` array.
- B) Update the application to extract the structured JSON from the `input` object within the `tool_use` block of Claude's response, rather than the `text` block.
- C) Set the `temperature` parameter to 0.0 to prevent conversational filler.
- D) Change `tool_choice` to `{"type": "any"}` to output the JSON into the `text` block.

**Answer: B**

When using native tool use, the model generates a tool_use content block. The structured data corresponding to the defined JSON schema is located within the input object of that block, not the legacy text block.

### CCA-F Q70 (Domain 4: Prompt Engineering and Structured Output)

A system processes purchase orders where the final total is sometimes misprinted. Which schema design and prompt strategy is most effective for detecting mismatches between the printed total and the sum of line items?

- A) Extract all line items and the printed total in a single pass, then use a second call to recalculate the sum, comparing in application code.
- B) Extract the line items and the printed total as separate fields. Calculate the sum of the line items in application code and compare against the extracted printed total, flagging any mismatch.
- C) Ask the model to verify its own arithmetic by recomputing the total before outputting, including both values in the output.
- D) Include fields for `stated_total` and `calculated_total` and have the model populate both, then compare in the application.

**Answer: B**

Extracting both values independently and performing the arithmetic in deterministic application code eliminates model hallucination or miscalculation, aligning with the recommended practice of validating model outputs with external logic when precision is critical.

### CCA-F Q72 (Domain 4: Prompt Engineering and Structured Output)

An enterprise is preparing to process 5 million legacy records using the Message Batches API at approximately $10,000 per run. The architect mandates two days refining the prompt on a stratified sample of 1,000 records using the synchronous API. What is the primary architectural justification?

- A) Prompt refinement on a sample set maximizes first-pass success rates, reducing the iterative resubmission costs and delays of large-volume batch processing.
- B) The Batch API permanently throttles submission limits for accounts with high failure rates.
- C) Resubmitting failed documents requires manual intervention for each individual document.
- D) The synchronous API uses a different, more accurate underlying model than the Batch API.

**Answer: A**

Validating the prompt on a representative subset lets the team catch and fix issues early, avoiding the high cost and time of reprocessing millions of records.

### CCA-F Q75 (Domain 4: Prompt Engineering and Structured Output)

A global law firm uses Claude to translate merger agreements from Japanese to English, and wants human translators to review only clauses where the AI is uncertain about legal nuances. Which design pattern best implements this calibrated review routing?

- A) Run a verification pass where a model evaluates the translated clauses, self-reports a confidence score, and routes those below a threshold to human translators.
- B) Instruct the model to insert a `[NEEDS REVIEW]` tag next to any translated sentence containing ambiguous legal terminology, and route tagged sentences to human translators.
- C) Split the contract into clauses, translate each independently, then run an integration pass to reconcile terminology and style.
- D) Use an independent Claude instance to translate the document a second time and route clauses with discrepancies to human review.

**Answer: B**

This directly targets clauses with potential legal nuance issues. Anthropic's research and industry best practices support flagging high-risk segments for human attention, and the tagging mechanism creates a calibrated, targeted review process.

### CCA-F Q76 (Domain 4: Prompt Engineering and Structured Output)

A system extracts a 'shipper_reference_id' from bills of lading. After several failed retries on one document, the model consistently returns `null`. Manual review confirms the ID is not present in the document; it was only in the email the document was attached to. What is the most appropriate system action?

- A) Modify the prompt to search the document's metadata fields, such as embedded XMP or EXIF data.
- B) Log the failure, halt the retry loop for this document, and flag it for manual review with a reason of 'Required information not present in source document.'
- C) Switch to a more advanced model and attempt the extraction again.
- D) Continue the retry loop with more aggressive prompts.

**Answer: B**

Logging the specific failure and halting the retry loop prevents wasted tokens and hallucinations. Flagging for manual review allows a human to reconcile the missing data and provides an audit trail for data quality issues.

### CCA-F Q77 (Domain 4: Prompt Engineering and Structured Output)

You are extracting `Patient ID`, `Diagnosis`, and `PrescribedMedication` from varied clinical notes. Some notes do not mention a medication, causing the model to inconsistently output `null`, omit the field, or hallucinate one. What is the most robust and recommended approach?

- A) Use the native `Structured Outputs` feature by providing a JSON schema in the `output_format` parameter, defining `PrescribedMedication` with a type of `["string", "null"]`.
- B) Rely on a system prompt instructing the model to always include the key and set it to `"N/A"`.
- C) Add few-shot examples demonstrating extraction with `PrescribedMedication` set to `null`.
- D) Use a post-processing script to insert a `null` value if the key is missing.

**Answer: A**

Structured Outputs with a JSON schema is the recommended approach for schema-compliant generation. Defining the field as `["string", "null"]` explicitly allows it to be a string or null, ensuring the model always includes the key and correctly represents missing data.

### CCA-F Q78 (Domain 4: Prompt Engineering and Structured Output)

A customer support pipeline uses a router agent followed by extraction agents. For a VIP client all tickets are billing-related, and you want to bypass the router and directly extract billing details, even though the system prompt still contains general support instructions. How can you guarantee Claude immediately executes the billing extraction?

- A) Set `tool_choice: {"type": "tool", "name": "extract_billing"}` and remove the tool definition from the `tools` array.
- B) Remove the general support instructions from the system prompt and set `tool_choice: {"type": "auto"}`.
- C) Set `tool_choice: {"type": "any"}` and only provide the `extract_billing` tool in the request's `tools` array.
- D) Set `tool_choice: {"type": "tool", "name": "extract_billing"}` in the API request to force the specific tool execution.

**Answer: D**

Setting `tool_choice: {"type": "tool", "name": "extract_billing"}` forces Claude to use exactly that tool, bypassing any system prompt instructions. This is the recommended method for guaranteeing a specific tool call.

### CCA-F Q79 (Domain 4: Prompt Engineering and Structured Output)

An ingestion pipeline receives mixed documents including resumes, invoices, and legal contracts. You need a single API call where Claude classifies and extracts into a structured JSON object that must always be valid and never conversational. Which configuration is most robust and officially recommended?

- A) Set `tool_choice: {"type": "auto"}` and provide a system prompt instructing Claude to only output JSON.
- B) Define three separate tools and set `tool_choice: {"type": "any"}`.
- C) Use the `output_config.format` parameter with a JSON Schema that defines the desired structure.
- D) Use a pre-processing step to classify the document, then make a second API call forcing the specific tool.

**Answer: C**

Setting `output_config.format` to json_schema enables Structured Outputs, which leverages constrained decoding at the token level, guaranteeing every response strictly complies with the supplied JSON Schema in a single API call.

### CCA-F Q80 (Domain 4: Prompt Engineering and Structured Output)

A legal discovery platform uses `extract_privileged_info` and `extract_public_info` tools. For very short emails Claude often ignores both and outputs conversational text, but every email must result in a structured JSON record. How should the API request be configured?

- A) Set `tool_choice: {"type": "any"}` to guarantee Claude calls one of the provided tools instead of outputting conversational text.
- B) Set `tool_choice: {"type": "auto"}` and add a system prompt stating "CRITICAL: Never output conversational text."
- C) Combine both tools into a single schema, make all fields required, and set `tool_choice: {"type": "auto"}`.
- D) Set `tool_choice: {"type": "tool", "name": "extract_public_info"}` and dynamically switch if it fails.

**Answer: A**

Setting `tool_choice: {"type": "any"}` forces Claude to select at least one of the provided tools, ensuring a structured tool response for every request even when the input is uninformative.

### CCA-F Q81 (Domain 4: Prompt Engineering and Structured Output)

A company developing an AI-powered IDE extension providing inline code completions proposes routing all completion requests through the Message Batches API to manage costs. Why should the architect reject this proposal?

- A) The Batch API cannot handle the high concurrency of thousands of developers submitting simultaneously.
- B) The Batch API requires a minimum payload size that a single completion prompt cannot meet.
- C) The Batch API does not support the specific Claude models required for code generation.
- D) Code completion is a blocking workflow requiring near real-time latency, making the Batch API's up to 24-hour processing window entirely inappropriate.

**Answer: D**

Inline code completion demands near real-time latency to provide immediate feedback as developers type. The Batch API's processing window is designed for asynchronous, non-urgent tasks.

### CCA-F Q89 (Domain 5: Context Management and Reliability)

An automated threat intelligence feed aggregates unstructured forum chatter, structured CVE metrics, and tabular financial loss data. The synthesis agent outputs a single markdown document, which breaks tabular formatting and loses the key-value structure downstream tools require. What is the best architectural approach?

- A) Define a strict multi-part JSON schema for the synthesis agent's output with distinct objects for narrative_analysis (string), cve_specs (array of key-value pairs), and financial_impact (2D array), allowing the frontend UI to render each natively.
- B) Pre-process all inputs into plain text paragraphs before synthesis so the agent only generates standard prose.
- C) Deploy three separate synthesis agents and concatenate their raw text outputs into a single text file.
- D) Instruct the agent to embed tabular data in `<table>` elements and CVE metrics in `<dl>` lists, relying on the model to generate valid HTML.

**Answer: A**

A strict multi-part JSON schema provides specific containers for each content type, ensuring data integrity. This lets frontend components render each type natively and downstream security tools parse specific keys programmatically without loss of fidelity.

### CCA-F Q91 (Domain 5: Context Management and Reliability)

A financial services bot helps users dispute credit card charges. A user states, "I don't recognize this $500 charge from Target. Get me a manager." The bot has a `dispute_charge` tool that can resolve this. According to conversational AI design best practices, which represents the most appropriate next step?

- A) The bot should ask the user for the date of the transaction to verify the charge before escalating.
- B) The bot should immediately honor the explicit request for a human agent without attempting to investigate or use the dispute tool.
- C) The bot should execute the `dispute_charge` tool first, then transfer to a manager to confirm.
- D) The bot should explain that it can file the dispute immediately, and ask if they still want a manager.

**Answer: B**

When a user explicitly requests a human agent for a sensitive issue like a charge dispute, the bot should immediately escalate without further investigation. Anthropic's Claude Constitution emphasizes not undermining appropriate human oversight, and industry standards recommend instant handoff for urgent, high-risk, or financial topics.

### CCA-F Q92 (Domain 5: Context Management and Reliability)

A junior developer suggests adding this to a support assistant's system prompt: 'Evaluate the complexity of the user's issue. Output a confidence score from 0 to 100 indicating your ability to solve it. If your confidence is below 80, trigger the escalate_to_tier2 tool.' Why is this approach flawed?

- A) Self-reported confidence scores are unreliable proxies for actual case complexity and LLMs frequently hallucinate their own confidence levels.
- B) The LLM should use a sentiment analysis tool on the error logs to determine complexity.
- C) The prompt should instead evaluate the user's technical proficiency score.
- D) The confidence threshold of 80 is too high and will cause excessive escalations.

**Answer: A**

Self-reported confidence scores from LLMs are notoriously unreliable and poorly calibrated. Best practices recommend objective, testable escalation triggers such as rule-based heuristics, rubric-based evaluation, or external classification models.

### CCA-F Q93 (Domain 5: Context Management and Reliability)

A B2B SaaS support bot uses a `get_tenant_id` tool based on the user's email domain. A user from a conglomerate (`@megacorp.com`) asks to provision a sandbox, and the tool returns 14 active tenant IDs across global subsidiaries. What is the most robust architectural pattern to resolve this ambiguity?

- A) Escalate to a human account manager immediately because 14 matches indicates a database synchronization error.
- B) Select the tenant ID with the most recent login activity as the default heuristic.
- C) Provision the sandbox in a temporary, unassigned environment and ask the user to link it later.
- D) Prompt the user for a specific subsidiary name, billing ID, or other identifier to clarify the exact tenant match.

**Answer: D**

Prompting the user for a more specific identifier ensures safety and accuracy before executing a requested action, preserving the bot's autonomy while maintaining high reliability.

### CCA-F Q95 (Domain 5: Context Management and Reliability)

A banking assistant uses a `lookup_customer` tool that accepts a name. A user asks for their balance and provides 'Maria Garcia'. The tool returns four different customer profiles. How should the architect instruct the model to handle this?

- A) Cross-reference the chat session's IP address with each profile's last known IP and select the closest match.
- B) Immediately escalate to a human agent with all four profiles.
- C) Ask the user for an additional identifier, such as the last four digits of their account number or their date of birth, to clarify the match.
- D) Select the profile with the most recent login activity.

**Answer: C**

Asking for an additional identifier is the standard and most reliable pattern for disambiguation, ensuring the correct identity is established through user-provided verification and balancing security, user experience, and automation.

### CCA-F Q96 (Domain 5: Context Management and Reliability)

A financial services agent has a strict SLA policy: 'Provide a 10% billing credit for any unplanned downtime exceeding 4 hours.' A customer reports a 5-hour outage and requests a 100% refund, claiming a resulting regulatory fine. The policy knowledge base is silent on liability for secondary damages. How should the agent be designed to respond?

- A) Immediately escalate the request to a human agent, flagging it as high-priority due to policy ambiguity and the potential for significant financial and reputational damage.
- B) Offer the standard 10% credit as an initial resolution, and escalate only if the customer rejects it.
- C) Autonomously deny the 100% refund and issue the standard 10% credit, adhering strictly to the SLA policy.
- D) Ask the customer for official documentation of the regulatory fine before escalating.

**Answer: A**

Documented best practices for AI governance mandate escalation of high-priority issues involving policy ambiguity and substantial risk. Unclear liability for secondary damages plus a possible regulatory fine triggers predefined escalation paths to human decision-makers.

### CCA-F Q98 (Domain 5: Context Management and Reliability)

A user interacting with a mortgage application bot is asked for 'Gross Annual Income'. They reply with monthly take-home pay, then with household savings after clarification, then upload a picture of their credit score. What is the most appropriate architectural pattern for the bot's next action?

- A) Trigger an escalation to a human agent due to an inability to make meaningful progress in the conversation.
- B) Calculate a self-reported confidence score on the user's financial literacy and escalate if below 50%.
- C) Loop back to the first explanation of Gross Annual Income with simpler language and bullet points.
- D) Use a heuristic to estimate the Gross Annual Income from the monthly take-home pay.

**Answer: A**

After several failed clarification attempts, the bot has failed to make meaningful progress. Escalating to a human agent is the standard architectural pattern to resolve persistent ambiguity in high-stakes domains like finance.
