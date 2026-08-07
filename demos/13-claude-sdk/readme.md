# Build multi-agent pipelines using the Agent SDK

- Agent SDK in the platform stack
- The `query()` async iterator
- Session resume, custom tools, typed output
- The Messages API tool loop
- Parallel agents and session isolation
- Orchestrator pattern and verdict contracts
- Constraining output: `tool_choice` and Structured Outputs
- Packaging a pipeline as GitHub Actions

## Topics

| Topic | Description |
|-------|-------------|
| [01: Positioning and Mental Model](01-positioning/readme.md) | Where the Agent SDK sits in the Messages API, Claude Code, Managed Agents stack; when to use it instead of the Messages API; and how the `query()` async iterator maps to the internal tool loop. |
| [02: Core API Surface and Demo 1](02-api-surface/readme.md) | The three knobs on `query()`, session resume, custom tools as in-process MCP servers, and typed output with Zod; demo scripts live in [`sdk-basics/`](02-api-surface/sdk-basics/). |
| [03: Parallel Agents, Session Isolation, and Demo 2](03-parallel-agents/readme.md) | The parallel pattern with `Promise.all`, the canary isolation test, the orchestrator pattern, and typed contracts across agent boundaries; demo lives in [`parallel-reviewer/`](03-parallel-agents/parallel-reviewer/). |
| [04: Output Control](04-output-control/readme.md) | The three API-level controls that remove the model's discretion: the four `tool_choice` values and the loop that `any` causes, Structured Outputs through `output_config.format` with token-level constrained decoding, and the Message Batches API with its 24-hour window. |

Every runnable project folder in this module is the starter you code in, and it stays pristine: no `node_modules`, no lockfile, no build output. Its finished counterpart sits beside it as `<starter>-solution/`, and that is where installs, lockfiles and runs live. So [`sdk-basics/`](02-api-surface/sdk-basics/) pairs with [`sdk-basics-solution/`](02-api-surface/sdk-basics-solution/), and [`parallel-reviewer/`](03-parallel-agents/parallel-reviewer/) pairs with [`parallel-reviewer-solution/`](03-parallel-agents/parallel-reviewer-solution/).

> **Note:** every `query()` call is billed, and every demo script in this module reads your key from `.env` in this folder, which is git-ignored. Create it before the first run and paste your own key into it, one `KEY=value` per line and no quotes:
>
> ```text
> ANTHROPIC_API_KEY=sk-ant-api03-...
> ```
>
> Each script loads that file itself, resolved from its own location, so nothing has to be exported into the shell first and the run works from any working directory:
>
> ```ts
> config({ path: fileURLToPath(new URL("../../.env", import.meta.url)), quiet: true });
> ```
>
> A key already in the environment wins over the file, so a logged-in `claude` CLI or an exported `ANTHROPIC_API_KEY` still takes precedence.

## Demos

| Topic | Description |
|-------|-------------|
| [Core API Surface](02-api-surface/demo-messages-api-to-sdk.md) | Four-step progression from a streaming `query()` call to a Zod-validated CI exit-code script. |
| [Parallel Agents](03-parallel-agents/demo-parallel-reviewers.md) | Three specialist agents review a flawed auth file in parallel, then an orchestrator synthesizes a typed verdict. |

Every demo has a presenter guide beside it (`demo-presenter-<slug>.md`) holding the same
teaching in timed beats, for delivery without running the demo live.

## Labs

| Lab | Description |
|-----|-------------|
| [Embed Claude in a TypeScript Program](../../labs/13-claude-sdk/lab-01-embed-claude.md) | Spawn Claude from inside your own program: one-shot calls, streaming, session resume, custom tools, typed output schemas, and a CI script. |
| [Run Parallel SDK Agents With Session Isolation](../../labs/13-claude-sdk/lab-02-parallel-sdk-agents.md) | Build a review pipeline from three parallel SDK sessions plus an orchestrator that reconciles their findings, packaged as a CI job. |

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

### CCA-F Q4 (Domain 1: Agentic Architecture and Orchestration)

An agentic loop includes a `capture_screenshot` tool. When Claude calls this tool, the application successfully captures a base64-encoded PNG image of the current web page. The developer needs to pass this image back to Claude so it can analyze the UI. How should the developer construct the `tool_result` block to include the image?

- A) Convert the base64 image to a URL and pass the URL as a plain text string inside the tool_result block.
- B) Append the image as a separate user message immediately following the user message that contains the tool_result block.
- C) Images cannot be passed inside tool_result blocks; the developer must restart the conversation and provide the image in the initial prompt.
- D) Include an image content block containing the base64 data and media type within the content array of the tool_result block.

**Answer: D**

In the Anthropic Messages API, the `tool_result` block contains a `content` field that accepts an array of content blocks, which can include `text` and `image` blocks containing base64 data and the media type.

### CCA-F Q13 (Domain 1: Agentic Architecture and Orchestration)

A cybersecurity agent uses a `scan_port` tool. The developer executes the tool and appends the result as a plain text string to the end of the last `user` message, rather than using a structured `tool_result` block. Claude begins hallucinating tool outputs and loses track of which ports it has scanned. Why does this cause model degradation?

- A) Plain text strings do not support the `is_error` flag, so the model misinterprets every scan result as a successful connection.
- B) Plain text strings bypass the model's internal safety filters, causing it to hallucinate malicious port activity.
- C) The developer must use a `system` message to inject plain text results, as `user` messages are strictly reserved for human input.
- D) Appending plain text instead of a structured `tool_result` block breaks the explicit linkage between the assistant's `tool_use_id` and the result, degrading the model's ability to reason about the action.

**Answer: D**

Claude's Messages API requires a structured action-observation loop where a tool_use is followed by a tool_result containing a matching tool_use_id. This linkage provides provenance and allows the model to reliably map observations back to specific actions.

### CCA-F Q27 (Domain 2: Tool Design and MCP Integration)

A data pipeline agent has `fetch_record`, `transform_record`, and `load_record` tools. An architect sets `tool_choice: {"type": "any"}`. Production logs reveal that after successfully calling `load_record`, the agent gets stuck in a loop, often attempting to call `fetch_record` again. What is the primary cause and how should it be resolved?

- A) The `load_record` tool's response is missing a `return_status` field, causing the agent to assume the load failed.
- B) The agent has too many tools; `transform_record` and `load_record` should move to a separate sub-agent.
- C) The `tool_choice: {"type": "any"}` configuration forces the model to call a tool on every turn. The architect should switch to `{"type": "auto"}` after the final `load_record` step.
- D) The `any` configuration is unreliable for agents with more than one tool; the architect must switch to `{"type": "auto"}` for the entire process.

**Answer: C**

`tool_choice: {"type": "any"}` compels the model to use a tool in the current turn. The correct approach is to manage the tool_choice state, switching to `{"type": "auto"}` once the tool sequence is complete so the model can generate a final conversational response.

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
