# Deploy autonomous action using Managed Agents

- Cloud containers with network and files
- Steering agents mid-execution via SSE
- OAuth vaults and token refresh
- Callable-agent patterns with isolated threads
- Session lifecycle: idle, running, termination
- Human-in-the-loop approval gates
- Managed Agents vs. Messages API
- Versioning agents as deployable units

## Topics

| Topic | Description |
|-------|-------------|
| [01: Foundations](01-foundations/readme.md) | Position Managed Agents on the spectrum from the Messages API to Claude Code, learn when the hosted runtime pays off, and master the three resources (Agent, Environment, Session) plus the session state machine. |
| [02: Sessions & Streaming](02-sessions-streaming/readme.md) | Cloud containers with networking and file mounts, the SSE event model, mid-execution steering, subagent threads, and a 25-minute end-to-end demo that touches every primitive in one flow. |
| [03: Production Features](03-production-features/readme.md) | Vaults with automatic token refresh, webhooks on `session.status_idled`, per-tool permission policies, agent versioning, Console observability, and the `ant` CLI for YAML-versioned resources. |
| [04: Tools & MCP](04-tools-mcp/readme.md) | The two extension points on an Agent: MCP servers declared alongside an `mcp_toolset` grant with its own permission policy, and skills that mount a procedure into the container and load on demand. |
| [05: Human-in-the-Loop](05-human-in-the-loop/readme.md) | The two blocking handoffs that drive approval gates, a 20-minute custom-tool HITL demo with allow and deny verdicts, and a migration path from the Messages API. |

## Demos

| Topic | Description |
|-------|-------------|
| [01: Foundations](01-foundations/demo-session-lifecycle.md) | Creates all three resources, polls one Session from `running` to `idle`, reads the persisted event log, and cleans up the two resources that are safe to delete. |
| [02: Sessions & Streaming](02-sessions-streaming/demo-first-agent.md) | Uploads a CSV, mounts it on a Session, streams the analysis over SSE, and downloads the artifact the agent wrote. |
| [03: Production Features](03-production-features/demo-agent-versioning.md) | Publishes two Agent versions, pins a Session to each, and shows the same `bash` call running unattended on one and pausing for `user.tool_confirmation` on the other. |
| [04: Tools & MCP](04-tools-mcp/demo-mcp-and-skills.md) | Attaches the Microsoft Learn MCP server and the `docx` skill to one Agent, then reads the event log while a single turn searches the docs and writes a document you download. |
| [05: Human-in-the-Loop](05-human-in-the-loop/demo-approval-gate.md) | Declares a custom tool, parks the Session at `requires_action`, and resumes it with both an allow and a deny verdict. |

Every demo has a presenter guide beside it (`demo-presenter-<slug>.md`) holding the same
teaching in timed beats, for delivery without running the demo live.

Every demo ships as a starter you run and a `-solution` folder holding the completed reference. Install with `pip install -r requirements.txt` before starting. The scripts target `anthropic>=0.118.0`; earlier releases have no `client.beta.agents` namespace at all.

> **Note:** every script in this module reads your key from `.env` in this folder, which is git-ignored. Create it before the first run and paste your own key into it, one `KEY=value` per line and no quotes:
>
> ```text
> ANTHROPIC_API_KEY=sk-ant-api03-...
> ```
>
> Each script loads that file itself, resolved from its own location, so nothing has to be exported into the shell first and the run works from any working directory:
>
> ```python
> load_dotenv(Path(__file__).resolve().parents[2] / ".env")
> ```
>
> A key already in the environment wins over the file, so an `ant auth login` profile or an exported `ANTHROPIC_API_KEY` still takes precedence.

## Labs

| Lab | Description |
|-----|-------------|
| [Build a Managed Agent for Codebase Triage](../../labs/12-managed-agents/lab-01-managed-agent-codebase-triage.md) | Mount a broken Python repo into a cloud Session and stream the fix loop, then publish a second Agent version with a custom tool and resume the parked Session with both verdicts. |

## Knowledge Check

### CQ-01: Environment or Session

A team runs many analyses that share one container image but each mount a different input file. What belongs where?

- A) One Environment per analysis, each with its own file mounted at creation.
- B) One reusable Environment as the container template, with each Session mounting its own file as a resource.
- C) One Session reused across analyses, remounting a new file between runs.
- D) Neither; files must be streamed as base64 on every turn, as in the Messages API.

**Answer: B**

The Environment is the reusable container definition: package set, networking policy, mount point. Mounts belong to the Session, so one Environment can back many Sessions that each mount something different, and you avoid paying the cold-start cost per run. Option D describes the Messages API limitation that file mounts exist to remove.

### CQ-02: Opening the Stream

A client subscribes to a Session's event stream immediately after sending the first `user.message`, and the first few events are missing. What went wrong?

- A) The stream needs a replay window configured at Session creation.
- B) The stream carries only what happens after it opens and has no replay, so it must be opened before the first event is sent.
- C) The client subscribed to the wrong event family and the events were filtered out.
- D) Events emitted before the first `session.status_idle` are always suppressed.

**Answer: B**

Open the stream first, then send. Anything emitted before the subscription is gone from the stream. The companion rule covers reconnects: list the persisted events and dedupe by event id, because what was emitted during the disconnect is still queryable even though the stream will not replay it.

### CQ-03: Two Gates, Two Replies

An agent calls a tool your application implements, and the Session parks at `requires_action`. What does the client send back?

- A) `user.tool_confirmation` carrying the `tool_use_id`, allowing or denying the call.
- B) `user.custom_tool_result` carrying the `custom_tool_use_id` and the actual result.
- C) Either one; the platform accepts both and routes by Session state.
- D) A new `user.message` describing the outcome in prose.

**Answer: B**

The two handoffs are distinct and conflating them is the usual source of 400s. A permission policy gates a tool the platform knows how to run, so the reply is an allow or deny confirmation. A custom tool has no implementation on Anthropic's side, so your reply carries the result itself.

### CQ-04: Restricting an Agent's Toolset

A hosted agent must be able to read files and nothing else. Which knob enforces that?

- A) The `allowed_tools` permission allowlist, which auto-approves the read tool and denies everything else.
- B) The `tools` parameter, which defines the agent's toolset, with the read tool as its only entry.
- C) A system prompt instructing the agent to use only the read tool.
- D) Filesystem permissions on the mounted directory, set to read-only.

**Answer: B**

`tools` defines what the agent has; `allowed_tools` is a permission allowlist that auto-approves calls without restricting which tools exist. Least privilege means removing the capability, not pre-approving a subset of it. Option D is a useful second layer but does not stop the agent from attempting other tools.

### CQ-05: When the Gate Should Fire

A user in a billing dispute says "get me a manager". The agent has a working `dispute_charge` tool. What should it do?

- A) File the dispute first, then transfer, so the manager inherits a resolved case.
- B) Escalate immediately, without investigating or using the tool.
- C) Ask for the transaction date to verify the charge before escalating.
- D) Explain that it can file the dispute now, and ask whether the user still wants a manager.

**Answer: B**

An explicit request for a human on a sensitive financial matter is honoured immediately. Every other option overrides a request the user was entitled to make, whether by acting first, gating on a verification question, or negotiating. The design principle is that human oversight is not something the agent gets to talk the user out of.

### CCA-F Q8 (Domain 1: Agentic Architecture and Orchestration)

An AI architect is managing two active sessions: Session A, containing a large volume of raw system logs, and Session B, containing the historical context and ongoing reasoning for a root cause analysis. The architect needs to continue the root cause investigation and also begin a separate architecture analysis for a proposed fix. Which session management strategy is most appropriate?

- A) Resume Session B; Start a new session for the architecture analysis.
- B) Start new sessions for both tasks, as any interruption requires a fresh context window.
- C) Resume both Session A and Session B, as Claude can automatically detect stale log data.
- D) Resume Session A; Start a new session for the log queries with a summary of the incident.

**Answer: A**

Resuming Session B preserves the valuable reasoning and narrative history of the investigation. Starting a new session for the architecture analysis ensures a clean, focused context window, isolating it from the investigation's history and preventing token waste.

### CCA-F Q19 (Domain 1: Agentic Architecture and Orchestration)

A data engineering team has spent 15 turns with Claude analyzing data skew in a PySpark ETL pipeline. They now want to evaluate two distinct architectural solutions: a broadcast hash join versus salting the skewed keys. Which session management strategy provides the most accurate comparison?

- A) Resume the session, implement the broadcast join, then use `--revert` to undo those turns before asking for the salting approach.
- B) Start two completely new sessions, providing the raw PySpark scripts to each.
- C) Continue in the same session, asking Claude to write both implementations sequentially.
- D) Use `fork_session` from the current state to create two isolated branches, allowing Claude to develop and evaluate each optimization strategy without context cross-contamination.

**Answer: D**

Forking is the ideal architectural pattern for A/B testing distinct solutions. It preserves the shared investigative context as a common baseline while creating isolated branches, preventing context leakage between them.

### CCA-F Q49 (Domain 3: Claude Code Configuration and Workflow)

An architect is integrating a third-party `/security-scan` tool using the Anthropic Agent SDK. To enforce least privilege, what is the most direct and effective method within the SDK to ensure the agent is only provided with the `ReadFile` tool?

- A) Add a system prompt instructing it to 'Only use the `ReadFile` tool and do not modify any files.'
- B) Configure the `tools` parameter in the Agent SDK's query options to include only the `ReadFile` tool.
- C) Run the agent in a sandboxed environment with the source directory set to read-only.
- D) Configure the `allowed_tools` parameter in the Agent SDK's query options to include only the `ReadFile` tool.

**Answer: B**

The tools parameter restricts which built-in tools are available to an agent. Official documentation confirms that tools defines the agent's toolset, while allowed_tools is a permission allowlist that auto-approves tools but does not restrict them.

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
