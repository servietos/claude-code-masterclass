# Scale task execution with sub-agents and agent teams

- Why single-agent sequential hits a ceiling
- Frontmatter: model, tools, permissionMode
- Orchestrator and sub-agent decomposition patterns
- Agent communication: contracts and schema validation
- Domain agents: backend, frontend, QA
- Context isolation between parallel agents
- Retry and convergent loops
- Workflow graphs: barriers versus pipelines
- When a team beats sub-agents
- Four parts: lead, teammates, tasks, mailbox
- Enabling teams and session state
- Spawning teammates and choosing models
- Display modes and the agent panel
- Task states, dependencies, and claiming
- Direct and teammate-to-teammate messaging
- Competing hypotheses between teammates
- Plan approval and team hook gates
- Team sizing, conflicts, and cost

## Topics

| Topic | Description |
|-------|-------------|
| [01: Introduction](01-introduction/readme.md) | Why sequential single-agent execution hits a context ceiling, how sub-agent frontmatter controls identity, model, tools, and permission mode, how a global sub-agent picks up repo facts from `.claude/rules/`, and the clean-context isolation pattern that prevents domain bleed. |
| [02: Domain Agents](02-domain-agents/readme.md) | Three domain sub-agents in isolated context windows: a .NET agent with the `dotnet-conventions` skill and `microsoft-learn` MCP, an Angular v21+ agent wired to `angular-cli` and `chrome-devtools` MCPs, and a qa-agent with no implementation authority wired to Playwright and Chrome DevTools; the demos delegate a catalog API endpoint and apply the same permission-locked pattern to a test-only agent. |
| [03: Testing Agent Performance](03-testing-agent-performace/readme.md) | Evaluating an agent instead of trusting it: input and expected-output test cases, assertions, edge cases, and reading failures as signals to rewrite the agent's body instructions. |
| [04: Orchestration Patterns](04-orchestration/readme.md) | The three shapes of orchestration and where each keeps its control flow: delegation in a prompt (decomposition, allowed paths, JSON contracts), loops with a stopping rule (contract retries and convergent review rounds), and graphs in a script (nodes, real versus ordering edges, `parallel()` barriers versus `pipeline()` streaming, verification edges, and why topology sets the cost and latency bill). |
| [05: Agent Teams](05-agent-teams/readme.md) | The lead, teammates, shared task list and mailbox; how a team differs from sub-agents in communication and cost; enabling the experimental flag; the team config, inbox and task paths on disk; the limits that decide whether a team is the right tool. |
| [06: Parallel Review](06-parallel-review/readme.md) | Spawning teammates by name, writing a spawn prompt that survives the missing conversation history, choosing models, the agent panel and its keys, task states and dependencies, and steering a teammate by messaging it directly. |
| [07: Debate and Control](07-debate-and-control/readme.md) | Competing hypotheses as an escape from anchoring, plan approval before a teammate edits, the three team hook events and their exit-code-2 gates, sub-agent definitions reused as teammate roles, the permission boundary between agents, and sizing against cost. |

## Demos

| Topic | Description |
|-------|-------------|
| [02: Domain Agents](02-domain-agents/demo-add-food-item-endpoint.md) | Delegates a scoped backend task to dotnet-expert by adding a name-filter endpoint to the `catalog-service-cs` API. |
| [02: Domain Agents](02-domain-agents/demo-test-food-controller.md) | Writes and runs xUnit tests for `FoodController` with a permission-locked agent that never touches implementation files. |
| [04: Orchestration Patterns](04-orchestration/demo-delegation-fan-out.md) | Optional. Splits the write-path hardening of `catalog-service-cs` into two file-disjoint slices, fixes the HTTP contract before either agent starts, and merges two JSON responses instead of two paragraphs. |
| [04: Orchestration Patterns](04-orchestration/demo-review-loop.md) | Runs the same task as implement, review, fix, review again, triaging a noisy first round down to what the project's actual configuration supports and capping the loop when the second round is still not dry. |
| [04: Orchestration Patterns](04-orchestration/demo-workflow-graph.md) | Optional. Re-expresses the same split as a workflow script: schema-validated nodes fanned out with `parallel()`, the merge and the vote in plain JavaScript, and a perspective-diverse panel that returns a split verdict. |
| [06: Parallel Review](06-parallel-review/demo-parallel-review-team.md) | Three named reviewers take one lens each on the `catalog-service-cs` API, claim tasks off the shared list, and the lead merges their findings into one ranked report. |
| [07: Debate and Control](07-debate-and-control/demo-competing-hypotheses.md) | Optional. Five teammates hold one root-cause theory each for a chat loop that exits after a single exchange, argue each other down by name, and write the surviving explanation to a consensus file. |

Every demo has a presenter guide beside it (`demo-presenter-<slug>.md`) holding the same
teaching in timed beats, for delivery without running the demo live.

## Starter and Solution Folders

Work in each topic's starter; the topic 02 test demo drives two projects, so start Claude Code in the topic folder rather than inside a project. Topic 04 runs one task three ways against `catalog-service-cs`, so it ships one finished folder per shape: `catalog-service-cs-delegation-solution`, `catalog-service-cs-delegation-loops`, and `catalog-service-cs-delegation-graph`.

Topic 06 works in `06-parallel-review/catalog-service-cs`, topic 07 in `07-debate-and-control/session-loop-py`. Both starters run without a team, and neither carries a `.claude/` folder: the agent-teams flag is a global harness setting in `~/.claude/settings.json`. The finished result including the team's output file sits beside each starter in its `-solution` folder.

## Labs

| Lab | Description |
|-----|-------------|
| [Build a Specialized Documentation Agent with Brand-Voice Enforcement](../../labs/06-subagents-agent-teams/lab-01-specialized-agents.md) | Reason through tools, model choice, MCP wiring and brand-voice rules to build a documentation sub-agent. |
| [Build a Scoped Unit-Testing Agent with Minimal Permissions](../../labs/06-subagents-agent-teams/lab-02-unit-testing-agent.md) | Scope a testing sub-agent to one catalog-api stack with minimal Bash permissions and interface-only mocking, then evaluate its output. |
| [Orchestrate an Agentic Team to Deliver Customer Data Persistence](../../labs/06-subagents-agent-teams/lab-03-agentic-team.md) | Coordinate `dotnet-expert` and `angular-expert` as a team to add customer data persistence to the food-shop checkout page. |
| [Spawn a Review Team and Steer It](../../labs/06-subagents-agent-teams/lab-04-spawn-a-review-team.md) | Spawn three named reviewers on one unreviewed service, watch them claim tasks off the shared list, redirect one by message, and gate the fix behind plan approval. |

## Knowledge Check

### CQ-01: Reading the Dependency Shape

Three subtasks must run: B needs A's output and C needs B's. Which pattern applies?

- A) Fan-out, because three agents in parallel is always faster than three in sequence.
- B) Prompt chaining, where each stage's structured output becomes the next stage's input.
- C) Domain decomposition, one agent per subtask in its own worktree.
- D) A single agent handling all three in one generation, so no context is lost between stages.

**Answer: B**

The dependency structure picks the pattern, not preference. With a strict A to B to C chain, parallelism gives B an empty input and it fabricates one. A single generation, option D, produces the right answer sometimes but hides the intermediate results you need in order to retry one stage instead of all three.

### CQ-02: Why the Subagent Ignored the Context

A coordinator delegates to a summarizer, passing only the user's original question. The summarizer hallucinates details that the upstream search agent had already retrieved correctly. What is the fix?

- A) Enable context inheritance on the summarizer so it can read the search agent's window.
- B) Have the coordinator include the retrieved document text in the summarizer's invocation prompt.
- C) Raise the summarizer's temperature so it recalls more of the shared session state.
- D) Give both agents a shared vector store and pass the session id so the summarizer can query it.

**Answer: B**

Subagents are context-isolated by design, which is what keeps them cheap and focused, and the consequence is that the coordinator owns state projection. Anything the subagent needs has to be in the prompt it receives. Option D would work but adds infrastructure to solve a problem that is one prompt field wide.

### CQ-03: The Coordinator That Announces But Never Delegates

A coordinator has the Task tool in `allowedTools` and a well-formed subagent definition, yet it replies "I will hand this to the billing specialist" and stops. What is missing?

- A) A trigger field on the subagent definition mapping intents to the agent.
- B) An instruction in the coordinator's system prompt telling it when to spawn the subagent.
- C) A separate escalation tool, since Task alone cannot transfer session context.
- D) Fork-based session management to move the conversation into the billing context.

**Answer: B**

Tool availability is permission, not instruction. The coordinator can call Task and has no guidance about when it should, so it does the next most plausible thing and narrates the handoff. The system prompt is where the trigger lives.

### CQ-04: Shared Data for Parallel Agents

Two agents run in parallel and both need the user's current holdings. How should that data reach them?

- A) Run the first agent, append its output to the holdings, and pass the combined result to the second.
- B) Fetch the holdings once in the orchestration layer and inject the same snapshot into both agents' prompts.
- C) Have each agent fetch the holdings itself so the two stay fully independent.
- D) Store the holdings in a vector database and give both agents a retrieval tool.

**Answer: B**

One fetch, one snapshot, injected into both, is what guarantees the two agents reason over identical data. Option C reintroduces the risk that two fetches return different states, which is exactly the inconsistency that breaks a merge. Option A serialises work that had no dependency.

### CQ-05: Enforcing the Output Contract

An orchestrator receives a subagent response where `filesChanged` came back as a string instead of an array. What should it do?

- A) Coerce the string into a single-element array and continue, since the intent is clear.
- B) Send a retry prompt that repeats the task with the specific validation error attached.
- C) Discard the result and mark the whole pipeline failed.
- D) Lower the schema's strictness so both shapes validate.

**Answer: B**

The contract exists so structural drift surfaces immediately rather than corrupting the next stage. A retry carrying the exact violation gives the agent what it needs to correct one field, which usually succeeds on the first attempt. Silent coercion, option A, trains the pipeline to tolerate drift until a case appears where the intent is not clear.

### CQ-06: Sub-Agents or a Team

A refactor has to move a shared type, update every call site, and keep the test suite green. The three pieces are strictly ordered. Which shape fits?

- A) An agent team of three, one per piece, so the work runs in parallel.
- B) A single session or sub-agents, because the pieces depend on each other and touch the same files.
- C) An agent team of two, with the third piece done by the lead while it waits.
- D) An agent team with plan approval on every teammate, to serialize them safely.

**Answer: B**

Teams pay coordination overhead and a separate context window per teammate in exchange for independent work and cross-talk. A strict dependency chain has no independence to buy, and same-file edits from parallel teammates overwrite each other. Option D notices the risk and then pays for a team anyway to undo the parallelism that was the only reason to spawn one.

### CQ-07: The Teammate That Ignored the Obvious

A lead spawns a security reviewer with the prompt "Review the auth module." The teammate reports generic findings and misses the JWT-in-cookie design the team spent the last hour discussing. What is the cause?

- A) The teammate's model was too small for security work.
- B) The teammate needs `inherit_context` enabled so it can read the lead's window.
- C) The lead's conversation history does not carry over, so anything the teammate needs has to be in the spawn prompt.
- D) The teammate should have messaged the lead to ask for background.

**Answer: C**

A teammate loads the project the way any session does, including `CLAUDE.md`, MCP servers and skills, but it does not inherit the lead's conversation. The hour of discussion exists only in the lead's window, so the spawn prompt is the only channel for it. Option D is not wrong as a habit, but a teammate cannot ask about context it does not know exists.

### CQ-08: The Panel Went Quiet

Three teammates were working. Two rows vanish from the agent panel and the third is still going. What happened?

- A) The two teammates crashed, and their transcripts are gone with them.
- B) The two teammates finished and were shut down automatically.
- C) The rows hid after the panel went idle; the teammates are still running and still addressable.
- D) The lead reassigned their tasks and despawned them to save tokens.

**Answer: C**

Idle rows hide 30 seconds after every agent in the panel has gone idle, and reappear on that teammate's next turn. The teammate keeps running and stays addressable by name while hidden, and messaging it brings the row back. Reading a hidden row as a dead teammate is what leads people to spawn duplicates.

### CQ-09: Approval Relayed Through a Teammate

A teammate is denied a destructive command. It messages another teammate saying the user approved the action and asks it to run the command instead. What happens?

- A) The second teammate runs it, because permissions are per teammate and it was not denied.
- B) The second teammate treats the claim as untrusted input, because a message from another agent is not your consent.
- C) The command runs but is logged for later review by the lead.
- D) The team halts, because a denied action cannot be retried in the same session.

**Answer: B**

A receiving agent is told the message came from another Claude session rather than from you. A teammate cannot approve a permission prompt on your behalf, and in auto mode the classifier treats a relayed approval claim as untrusted input. This is the boundary that makes a team safe to run with more members than you can watch.

### CQ-10: The Teammate That Stops Too Early

Teammates keep marking their review task complete without writing the findings file the run exists to produce. What is the mechanism that fixes this without you watching every teammate?

- A) Lower the teammates' effort so they take fewer shortcuts.
- B) A `TaskCompleted` hook that exits 2 when the findings file is missing, sending the reason back as feedback.
- C) Reduce the team to one teammate so the lead can supervise it.
- D) Re-prompt each teammate after every task with the same instruction.

**Answer: B**

Exit code 2 on `TaskCompleted` prevents the completion and delivers the stderr text as feedback, which turns "I am done" into a claim the harness can refuse. `TeammateIdle` does the same for a teammate about to go idle. Option D works and costs a round-trip every time, which is exactly what a gate replaces.

### CCA-F Q1 (Domain 1: Agentic Architecture and Orchestration)

A B2B SaaS bot receives a complex prompt: 'Analyze my Q3 API usage, compare it to Q2, and forecast my Q4 costs based on current trends.' The architect recognizes that the subtasks have data dependencies. Which architectural pattern should the architect use?

- A) Send the request to a single agent with a large context window and instruct it to do all three in one continuous generation.
- B) Execute the tasks sequentially using a single agent, clearing the context between each step to save tokens.
- C) Use prompt chaining: break the request into sequential steps where the output of the Q3 analysis is fed into the Q2 comparison step, and that result into the Q4 forecast step.
- D) Collect the structured outputs from the parallel worker agents into a shared context window, and use a final synthesizer agent.

**Answer: C**

Prompt chaining allows each step to be handled sequentially, passing structured outputs forward. This ensures logical progression and data integrity while keeping each agent's context focused. Options A and B either overload a single agent or lose continuity by clearing context, while D assumes parallelism, which breaks the dependency order.

### CCA-F Q2 (Domain 1: Agentic Architecture and Orchestration)

An orchestration agent is tasked with translating a document into French, Spanish, and German using a `Translator` subagent, in parallel. During execution, the coordinator emits one Task tool call for French, waits, then emits the call for Spanish. How should the architect modify the prompt to enforce parallel subagent spawning?

- A) Explicitly instruct the coordinator to emit multiple Task tool calls within a single response generation, rather than waiting for one result before emitting the next.
- B) Require the coordinator to use fork-based session management to create three separate translation threads.
- C) Add a `ParallelExecution` tool to the coordinator's `allowedTools`.
- D) Update the `AgentDefinition` of the `Translator` to accept an array of languages in a single Task tool call payload.

**Answer: A**

When the LLM emits multiple tool-use blocks simultaneously, the execution engine can process these subagent tasks in parallel, significantly reducing total latency compared to serial execution.

### CCA-F Q6 (Domain 1: Agentic Architecture and Orchestration)

A telecom support system has a Coordinator that invokes a `RetentionOfferAgent`, passing only the user's most recent message ("I want to cancel my service now"). The subagent generates a generic $5 discount that ignores the user's specific past disputes. What is the architectural cause of this failure?

- A) Subagents have isolated context; the Coordinator must pass a summary of the user's billing disputes and sentiment to the subagent instead of just the last message.
- B) The Coordinator's task decomposition was too narrow; it should have invoked a `SentimentAnalysisAgent` in parallel.
- C) The `RetentionOfferAgent` requires a higher temperature setting to infer the user's frustration.
- D) The Coordinator failed to grant the subagent access to the shared session memory bus.

**Answer: A**

In a coordinator-subagent pattern, subagents are typically stateless and operate with isolated context. It is the Coordinator's responsibility to manage state projection, synthesizing the relevant history, intent, and sentiment into a concise summary.

### CCA-F Q7 (Domain 1: Agentic Architecture and Orchestration)

An automated DevOps troubleshooting system uses a sequential chain: `LogAgent` passes to `MetricsAgent` passes to `DiagnosisAgent`. The `MetricsAgent` fails intermittently, the `DiagnosisAgent` never receives the payload, the system hangs, and the SRE team must manually parse raw container logs. Which architectural pattern resolves this?

- A) Transition to a hub-and-spoke architecture where a Coordinator invokes each agent individually, captures the error, logs it centrally, and routes the available logs directly to the `DiagnosisAgent`.
- B) Implement a dead-letter queue within the `MetricsAgent` that emails the SRE team before terminating.
- C) Embed the API key directly into the `MetricsAgent`'s system prompt.
- D) Configure the `DiagnosisAgent` with a timeout so it generates a diagnosis from training data after 30 seconds.

**Answer: A**

A hub-and-spoke architecture using a Coordinator decouples the agents and makes error handling explicit, allowing it to catch errors, log them, and implement fallback logic.

### CCA-F Q9 (Domain 1: Agentic Architecture and Orchestration)

A financial analysis system extracts earnings data with a 'DataMiner' subagent and charts it with a 'Grapher' subagent. When the DataMiner passes findings back as a conversational summary, the Grapher frequently plots incorrect numbers or mislabels axes. What is the most robust architectural solution?

- A) Instruct the DataMiner to output its findings as a structured CSV or JSON array, and have the coordinator pass this exact structured output to the Grapher.
- B) Use fork-based session management to let the Grapher iteratively query the DataMiner in a private thread.
- C) Configure the Grapher to use a lower temperature setting.
- D) Add a DataValidation tool that compares the Grapher's output against the DataMiner's summary.

**Answer: A**

Structured output preserves exact, machine-readable numeric and field semantics, eliminating the ambiguity of free-form conversational summaries and maintaining data integrity across subagent boundaries.

### CCA-F Q11 (Domain 1: Agentic Architecture and Orchestration)

A multi-agent system writes a biography by assigning subagents to childhood, early career, and late career. The final synthesis reads like three disconnected essays and misses the lifelong evolution of the figure's political philosophy. What is the primary architectural flaw?

- A) The orchestrator's temporal partitioning was too narrow; it should have also partitioned by thematic scope.
- B) The subagents should have communicated directly with one another during the research phase.
- C) The synthesis step requires a significantly larger context window.
- D) The orchestrator should have assigned all research to a single, powerful agent.

**Answer: A**

Tasks can be partitioned both temporally and thematically. Failing to capture the cross-cutting theme is a direct result of relying solely on temporal decomposition; a robust strategy uses a hybrid approach.

### CCA-F Q12 (Domain 1: Agentic Architecture and Orchestration)

A firm processes daily earnings reports. For 95%, the agent extracts standard GAAP metrics. If it detects a 'going concern' warning, it must perform a deep, unpredictable forensic analysis. Which orchestration design best balances efficiency and thoroughness?

- A) A fixed prompt chain that always includes a forensic debt analysis step.
- B) A purely dynamic adaptive decomposition workflow for all reports.
- C) A cross-file integration pass that merges standard metrics with all footnote text before a fixed sequential analysis.
- D) A fixed pipeline for standard extraction that conditionally triggers a dynamic adaptive decomposition workflow if a warning is detected.

**Answer: D**

This balances efficiency and thoroughness by using a fixed pipeline for predictable tasks while conditionally triggering dynamic decomposition only when needed, keeping resource allocation proportional to task complexity.

### CCA-F Q14 (Domain 1: Agentic Architecture and Orchestration)

A legal research application uses a 'Searcher' agent and a 'Summarizer' subagent. The Searcher retrieves the correct documents, but the Summarizer hallucinates case details. The logs show the Summarizer's prompt contains only the user's original query. How should the architect resolve this?

- A) Enable the inherit_memory: true flag in the Summarizer's AgentDefinition.
- B) Increase the temperature of the Summarizer to improve document recall.
- C) Configure a shared vector database and pass the session_id to the Summarizer.
- D) Modify the coordinator's logic to explicitly include the Searcher's retrieved document text within the Summarizer's Task tool invocation prompt.

**Answer: D**

The coordinator is responsible for state management. The output generated by the Searcher must be explicitly passed as context within the Summarizer's Task tool invocation prompt.

### CCA-F Q15 (Domain 1: Agentic Architecture and Orchestration)

An enterprise support bot must escalate billing issues to a 'BillingResolution' subagent. The AgentDefinition exists and the Task tool is in the coordinator's allowedTools. During testing the coordinator replies 'I will transfer you to billing' without triggering the subagent. What is the most likely missing configuration?

- A) The AgentDefinition is missing the trigger_intent field.
- B) The coordinator's system prompt needs to explicitly instruct it to use the Task tool to spawn the subagent when billing issues are detected.
- C) The system is failing to use fork-based session management.
- D) The coordinator lacks the Escalate tool in its allowedTools.

**Answer: B**

Having the Task tool in allowedTools is not sufficient; the coordinator's system prompt must explicitly instruct it when to use the tool.

### CCA-F Q16 (Domain 1: Agentic Architecture and Orchestration)

A B2B SaaS bot receives a complex prompt with data dependencies (Q3 analysis must precede Q2 comparison, which must precede Q4 forecast). Which architectural pattern should the architect use?

- A) Execute the tasks sequentially using a single agent, clearing the context between each step to save tokens.
- B) Use prompt chaining: break the request into sequential steps where each output feeds the next, with each step handled by a dedicated agent or prompt.
- C) Collect the structured outputs from parallel worker agents into a shared context window and use a final synthesizer agent.
- D) Send the request to a single agent with a large context window in one continuous generation.

**Answer: B**

Anthropic's documentation on building effective agents lists prompt chaining as a foundational design pattern where the output of one LLM call becomes the input for the next. It avoids the complexity and cost of multi-agent parallelism when subtasks are not independent.

### CCA-F Q18 (Domain 1: Agentic Architecture and Orchestration)

A financial analysis platform has a Data-Fetcher subagent sending retrieved data directly to a Summarizer subagent. API rate limits cause the Data-Fetcher to fail intermittently, and the Summarizer hallucinates financial metrics. Which architectural change resolves this?

- A) Grant the Summarizer direct access to the Data-Fetcher's execution logs to parse rate limit error codes.
- B) Refactor to a hub-and-spoke model where the Data-Fetcher returns data to a Coordinator, which handles API errors and only invokes the Summarizer upon successful retrieval.
- C) Merge the Data-Fetcher and Summarizer into a single monolithic agent.
- D) Implement a shared memory bus where the Summarizer polls a status flag.

**Answer: B**

A hub-and-spoke model with a Coordinator centralizes error handling, validation, and retry logic. Ensuring the Summarizer is only invoked after successful retrieval prevents hallucinations caused by empty or failed inputs.

### CCA-F Q21 (Domain 1: Agentic Architecture and Orchestration)

An orchestration agent must translate a document into French, Spanish, and German in parallel, but emits one Task tool call at a time. How should the architect modify the prompt to enforce parallel subagent spawning?

- A) Explicitly instruct the coordinator to emit multiple Task tool calls within a single response generation.
- B) Add a `ParallelExecution` tool to the coordinator's `allowedTools`.
- C) Update the `AgentDefinition` of the `Translator` to accept an array of languages in a single Task tool call payload.
- D) Require the coordinator to use fork-based session management to create three separate translation threads.

**Answer: A**

When the LLM emits multiple tool-use blocks simultaneously, the execution engine can process these subagent tasks in parallel, significantly reducing total latency compared to serial execution.

### CCA-F Q22 (Domain 1: Agentic Architecture and Orchestration)

A wealth management bot decomposes a request into a `RiskAnalyzer` and a `StockRecommender` running in parallel. Both need the user's current holdings. How should the shared context be managed?

- A) Execute the `RiskAnalyzer` first, append its output to the holdings, and pass the combined data to the `StockRecommender`.
- B) Fetch the user's holdings once in the orchestration layer and inject this data as shared context into the system prompts of both parallel agents.
- C) Query the user's holdings twice, once inside each agent's execution loop.
- D) Store the holdings in a vector database and require both agents to use a RAG tool.

**Answer: B**

Fetching the data once at the orchestration layer and injecting it into both parallel agents ensures both work from an identical snapshot, which is essential for consistent multi-step task execution.

### CCA-F Q35 (Domain 2: Tool Design and MCP Integration)

A Level 1 IT Support agent with a `check_ticket_status` tool was given three escalation tools for Jira, PagerDuty, and Slack. It began incorrectly using the high-urgency PagerDuty tool for low-priority issues like password resets. What is the best architectural approach?

- A) Replace the 3 escalation tools with a single `escalate_ticket` tool that triggers a hardcoded script.
- B) Remove the 3 escalation tools from the L1 agent, keep the `check_ticket_status` tool, and route escalation requests to a specialized L2 Escalation agent.
- C) Keep all tools on the L1 agent but use `tool_choice: {"type": "any"}` to force priority evaluation.
- D) Give the L1 agent a `web_search` tool to look up the correct escalation policies.

**Answer: B**

This aligns with a tiered agent architecture. L1 agents should handle routine tasks with a limited toolset to improve focus and accuracy; complex tasks like escalations should route to a specialized L2 agent with the appropriate tools and context.

### CCA-F Q39 (Domain 2: Tool Design and MCP Integration)

An IT support bot has `reset_password`, `unlock_account`, and `provision_software` tools. The system prompt includes: 'Your primary goal is to help users unlock their potential and access their accounts.' When a user asks for a password reset, Claude frequently calls `unlock_account`. What is the root cause and best solution?

- A) Keyword-sensitive instructions in the system prompt are creating unintended tool associations; remove the metaphorical phrase.
- B) The tool names are too similar; rename `reset_password` to `change_credentials`.
- C) The tools have functional overlap; combine them into a single tool.
- D) The tool descriptions lack negative constraints; add 'Do not use for password resets' to `unlock_account`.

**Answer: A**

LLMs are highly sensitive to keywords in the system prompt. The metaphorical use of 'unlock' creates a strong semantic bias toward the matching tool name. Removing or rephrasing the metaphor is the most effective architectural fix.

### CCA-F Q56 (Domain 3: Claude Code Configuration and Workflow)

You are halfway through a complex, multi-file refactoring session and need to look up how a third-party payment webhook is handled in a massive, unrelated legacy module, without losing your current context. What is the most architecturally sound way to retrieve this information?

- A) Switch to plan mode to investigate the legacy module, then switch back to direct execution.
- B) Use direct execution to query the legacy module, as the context window is large enough for both tasks.
- C) Use the Explore subagent to investigate the legacy module, isolating the verbose output and returning only the necessary summary.
- D) Commit your changes, clear the context window, find the webhook info, then resume refactoring.

**Answer: C**

The Explore subagent allows isolated, investigative work in a separate context, capturing verbose output and returning only the essential summary. This prevents context bloat and maintains focus on the primary refactoring task.

### CCA-F Q71 (Domain 4: Prompt Engineering and Structured Output)

A DevOps team uses Claude to generate a CI/CD pipeline of 8 separate YAML files. Reviewing them in a single prompt, Claude fails to notice that an environment variable exported in `build.yml` is referenced with a different name in `deploy.yml`. How should the architect restructure the review process?

- A) Pass the generated YAML files to an independent review instance without the original context.
- B) Concatenate all 8 YAML files into a single JSON object, then prompt the model to parse the new structure.
- C) Implement a verification pass where the model self-reports a confidence score for each variable mapping.
- D) Split the review into per-file passes to validate local syntax, followed by a separate integration pass that analyzes cross-file data flow and variable references.

**Answer: D**

This multi-pass architecture validates local syntax first, then uses a dedicated integration pass focused on cross-file data flow. Narrowing the model's attention to dependencies between stages prevents overlooking mismatches.

### CCA-F Q73 (Domain 4: Prompt Engineering and Structured Output)

A security operations center analyzes daily access logs from 15 microservices, all concatenated into a single prompt. Claude identifies isolated brute-force attempts but misses coordinated attacks moving from `auth-service` to `billing-service`. Which architectural pattern best enables detection?

- A) Use an independent review instance to re-process the concatenated logs with a prompt focused on cross-service access patterns.
- B) Implement a verification pass where Claude self-reports a confidence score for each identified event.
- C) Increase the `max_tokens` limit and use extended thinking.
- D) Implement a multi-pass architecture: run a local pass on each log to extract suspicious IPs and timestamps, followed by a cross-file integration pass to correlate the extracted entities.

**Answer: D**

Extracting structured signals from each log independently reduces context dilution and the lost-in-the-middle effect. The cross-file integration pass then correlates these high-signal entities across services, enabling detection of lateral movement.

### CCA-F Q84 (Domain 5: Context Management and Reliability)

A pharmaceutical company synthesizes findings from hundreds of clinical trial documents using separate agents for extraction, summarization, and report generation. The final report states a drug's efficacy but loses the connection to the specific trial, patient population, and dosage. Which strategy is most effective for preserving claim-source mapping?

- A) Store the outputs of each agent in a vector database with metadata fields, and have the final agent retrieve similar chunks and append metadata.
- B) Combine all agents into a single monolithic agent with a very large context window.
- C) Add a structured instruction to each agent's prompt requiring a 'source mapping' object, which the final agent concatenates into the report.
- D) Mandate that every agent pass and receive data using a standardized JSON schema including a 'claim' field and a 'provenance' object (trial_id, document_url, patient_population_summary), and require the final agent's prompt to maintain this mapping.

**Answer: D**

This enforces a structured, machine-readable approach to provenance. Requiring every agent to pass and receive data in this format ensures provenance travels with each assertion through the entire workflow, enabling rigorous auditing in high-stakes environments.
