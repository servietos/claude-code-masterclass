# Module 4: Consuming & Designing MCP Tools

- MCP architecture: servers, clients, transports
- Connecting remote and hosted endpoints
- Wrapping REST APIs as MCP servers
- Implementing custom MCP servers from scratch
- Authenticating: OAuth, API keys, token flows
- Building MCP apps as agentic interfaces
- Hosting and deploying for teams
- Tool list caching with prompt caching
- Connector-backed artifact pages
- Tool design: granularity, descriptions, contracts

## Topics

| Topic | Description |
|-------|-------------|
| [01: Intro](01-intro/readme.md) | MCP architecture essentials: client-server model, stdio vs. HTTP transports, and how hosts connect to compliant servers without bespoke integration code. |
| [02: MCP Server](02-mcp/readme.md) | Building a production-style MCP server in C# .NET 10 with ASP.NET Core, Streamable HTTP transport, EF Core SQLite persistence, and six HR management tools. |
| [03: MCP Apps](03-mcp-apps/readme.md) | The MCP Apps extension that renders interactive interfaces inline in compliant hosts, plus a C# QR code MCP server that returns a generated PNG. |
| [04: Artifact Connectors](04-artifact-connectors/readme.md) | Published artifact pages that call MCP connectors at view time: why a local `.mcp.json` server cannot be reached from a page, the connector declaration made at publish time, calls running as the viewer rather than the author, and the sharing limits that follow. |
| [05: Tool Design](05-tool-design/readme.md) | Why an exposed capability still gets ignored: granular tools over one generic schema, the description as the routing signal, naming pairs the model will not conflate, resources for bulk reads, the `isError` and `isRetryable` contract, and `defer_loading` once the tool count outgrows the context window. |

## Demos

| Topic | Description |
|-------|-------------|
| [02: MCP Server](02-mcp/demo-hr-mcp-server.md) | Starts the C# HR MCP server on port 47002, verifies its six snake-case tools with the MCP Inspector CLI, calls two of them against seeded SQLite data, and registers the endpoint in `.mcp.json`. |
| [03: MCP Apps](03-mcp-apps/demo-qr-code-mcp-app.md) | Runs the C# QR code server over Streamable HTTP and stdio, reads the `type: image` content block `generate_qr` returns, and proves the server exposes no `ui://` view resource. |
| [04: Artifact Connectors](04-artifact-connectors/demo-last-two-emails.md) | Publishes a page that fetches your two most recent emails through the claude.ai Microsoft 365 connector on every open. |

Every demo has a presenter guide beside it (`demo-presenter-<slug>.md`) holding the same
teaching in timed beats, for delivery without running the demo live.

## Runnable Projects

Every runnable project ships twice. The folder a guide walks you through is the **starter** and stays pristine: no `node_modules`, no lockfile, no `bin/`, no `obj/`, no build output. Its completed counterpart lives beside it as `<starter>-solution/`, and that is the only folder that gets installed, built and run. Each guide names its solution folder once as the finished reference and otherwise keeps pointing at the starter.

## Labs

| Lab | Description |
|-----|-------------|
| [Modernize Angular with the Angular MCP](../../labs/04-mcp/lab-01-modernizing-angular-mcp.md) | Use the Angular MCP to evaluate and progressively modernize `food-shop-ng` with signals, OnPush, and zoneless architecture. |
| [Build the EventTrack Registration MCP Server](../../labs/04-mcp/lab-02-eventtrack-mcp-server.md) | Build a headless Python MCP server for events and attendee registrations, then drive the workflow through Claude Code. |
| [Drive an Interactive PDF Viewer with MCP Apps](../../labs/04-mcp/lab-03-pdf-viewer-mcp-app.md) | Build and register the PDF MCP server, then open, navigate, annotate and save documents in Claude Desktop's embedded viewer. |
| [Fly a 3D Globe with the Map MCP App](../../labs/04-mcp/lab-04-map-mcp-app.md) | Build and run the Map MCP App, then geocode landmarks and fly a 3D globe to their coordinates. |
| [Wrap a Python MCP App in a Custom Skill](../../labs/04-mcp/lab-05-authoring-an-mcp-python-skill.md) | Mine the QR Code MCP server as a reference and extract its patterns into a reusable `mcp-python` skill. |

## Knowledge Check

### CQ-01: Picking a Transport

A server must be reachable by several developers and a CI runner, with bearer-token authentication. Which transport does the `.mcp.json` entry declare?

- A) `stdio`, because the host owns the process lifecycle and that is the most reliable option.
- B) `http` for Streamable HTTP, because remote and multi-tenant deployments need it and it supports bearer tokens.
- C) `sse`, because Server-Sent Events is the standard for multi-client servers.
- D) Either `stdio` or `http`; the choice only affects latency, not capability.

**Answer: B**

Stdio pipes JSON-RPC over the standard streams of a child process the host spawns, so it cannot serve a remote or shared consumer at all. Streamable HTTP is required for remote or multi-tenant deployments and supports bearer tokens, API keys, and OAuth 2.0. SSE transport still exists for backward compatibility but is deprecated for new implementations.

### CQ-02: A Tool or a Resource

An agent needs to reason over a catalog of several hundred policy documents that changes daily. Exposing it as tools produces hundreds of sequential calls and rate-limit failures. What should the server expose instead?

- A) One tool that returns the whole catalog, called once at session start.
- B) The catalog as an MCP resource, which the host reads into context in a single step.
- C) The same tools, with a caching layer so repeat calls are cheap.
- D) A prompt template that embeds the catalog, surfaced as a slash command.

**Answer: B**

Resources are the MCP primitive for large, read-heavy data the host should pull into context, as opposed to tools, which are for actions and per-item lookups. Reading a resource once replaces an exploratory tool-calling loop that both burns rate limit and drifts the agent away from its original goal. Caching, option C, reduces cost without fixing the interaction pattern.

### CQ-03: The Tool That Never Gets Called

A team ships a well-implemented MCP tool for querying their log system. Claude keeps writing Python to parse raw logs instead. What is the first thing to fix?

- A) Remove the Bash tool from the agent's environment so scripting is not an option.
- B) The tool description, which must state what the tool handles and why it beats writing a script.
- C) Move the server registration from the project `.mcp.json` to the user-global config to raise its priority.
- D) Rename the tool to match the shell command it replaces so the model reaches for it by habit.

**Answer: B**

Claude selects tools from their semantic metadata, so a vague description leaves script-writing as the better-understood path. A description that names the capability, states what the tool handles on the caller's behalf, and says when to prefer it over the obvious alternative is the actual routing signal. There is no priority ordering by config location, which rules out option C.

### CQ-04: Designing the Error Response

An MCP tool call is rejected by the backend because the caller lacks the privilege. How should the tool report it?

- A) `isError: true`, `errorCategory: "transient"`, `isRetryable: true`, so the agent tries again shortly.
- B) `isError: true`, `errorCategory: "permission"`, `isRetryable: false`, with a message naming the escalation path.
- C) `isError: false` with an explanatory message, so the agent's error recovery loop does not fire.
- D) `isError: true`, `errorCategory: "validation"`, `isRetryable: true`, prompting the caller for a different identifier.

**Answer: B**

The error fields are instructions to the model. A permission denial is terminal, so marking it retryable sends the agent into a loop against a wall, and mislabelling it as validation sends it to ask the user for different input that will fail the same way. Option C is worse still: the agent treats a failure as success and builds on a result it never received.

### CQ-05: Too Many Tools

An agent connects to six MCP servers whose combined tool definitions exceed 10,000 tokens before any work begins. What is the recommended response?

- A) Consolidate all six behind one monolithic orchestrator server exposing a unified tool set.
- B) Mark most tools `defer_loading: true` so the agent starts with the Tool Search Tool and loads definitions on demand.
- C) Connect to only two servers per session and restart when the agent needs a different pair.
- D) Accept the cost, since tool definitions are cached and therefore effectively free after the first turn.

**Answer: B**

Deferred loading is the mechanism built for this: the agent sees a lightweight Tool Search Tool plus whatever stays eagerly loaded, then discovers and loads the definitions a given task needs. Anthropic measures up to an 85% reduction in tool-definition tokens, and recommends it past ten tools or 10,000 tokens of definitions. Option A hides the tools behind one schema but moves the routing problem into a server you now maintain.

### CCA-F Q23 (Domain 2: Tool Design and MCP Integration)

An infrastructure management agent uses a generic `manage_aws_resource` tool. To prevent destructive actions, the developer implemented a complex 500-line JSON schema with strict `enum` validations, conditional dependencies, and nested objects. The agent now frequently fails to construct valid JSON payloads, resulting in API errors. What is the recommended architectural alternative?

- A) Distribute the generic tool across multiple subagents, giving each subagent the exact same tool but providing different few-shot examples in their system prompts.
- B) Increase the model's temperature to allow it to creatively bypass the strict `enum` validations when generating the complex schema.
- C) Keep the generic tool but set `tool_choice: {"type": "tool", "name": "manage_aws_resource"}` to force the model to focus its entire context window on schema generation.
- D) Replace the single generic tool with 4 to 5 constrained, purpose-built tools (e.g., `restart_ec2`, `scale_asg`) that utilize simple, flat JSON schemas.

**Answer: D**

The best practice for tool design is to replace overloaded, generic tools with smaller, purpose-built tools. This reduces the cognitive load on the model, simplifies the JSON schemas, and significantly increases the reliability of tool calling and API adherence.

### CCA-F Q24 (Domain 2: Tool Design and MCP Integration)

A security auditing agent is tasked with reviewing IAM policies across hundreds of AWS accounts to identify overly permissive roles. The agent currently uses a `list_policies` tool, followed by iterating through each policy with a `get_policy_document` tool. This results in hundreds of sequential API calls, frequently hitting AWS rate limits and causing the agent to lose track of its original goal. What is the most effective architectural change to resolve this?

- A) Expose a pre-compiled catalog of all IAM policy documents as an MCP resource, allowing the agent to ingest the entire dataset without exploratory tool calls.
- B) Update the agent's system prompt to strictly limit its analysis to 10 policies per session to avoid triggering rate limits.
- C) Implement a caching layer within the `get_policy_document` tool to store previously fetched policies in a local SQLite database.
- D) Combine the two tools into a single `analyze_all_policies` tool that uses a smaller LLM to pre-filter the policies before returning them to the main agent.

**Answer: A**

Exposing a pre-compiled catalog as an MCP resource shifts the interaction pattern from many exploratory, sequential tool calls to a single data access step. MCP Resources are designed for large, read-heavy datasets, which minimizes rate-limit pressure and prevents the context drift that occurs during repetitive tool-calling loops.

### CCA-F Q25 (Domain 2: Tool Design and MCP Integration)

A CRM assistant has two tools: `update_contact` and `log_interaction`. The descriptions are 'Updates a customer contact record' and 'Logs a contact interaction'. When users say 'Update John's record to show we spoke today,' Claude calls `update_contact` and attempts to stuff the conversation notes into the `email` field, causing a validation error. How should the architect redesign the tool interfaces to prevent this?

- A) Add a negative constraint to the system prompt instructing Claude to 'Never use update_contact for logging calls or meetings.'
- B) Change the `update_contact` schema to include a `notes` field, then silently drop that field in the backend to prevent validation errors.
- C) Rename `update_contact` to `modify_contact_details` and `log_interaction` to `record_communication_event`, updating descriptions to explicitly contrast when to use each.
- D) Merge the tools into a single `manage_crm_record` tool and let the backend CRM API route the payload based on the presence of notes.

**Answer: C**

Renaming the tools to reflect distinct intents and rewriting the descriptions to explicitly contrast their use cases provides Claude with clearer semantic boundaries. This reduces tool selection errors and prevents the model from forcing conversation data into unrelated fields due to naming ambiguity.

### CCA-F Q28 (Domain 2: Tool Design and MCP Integration)

A network diagnostic agent uses a `run_diagnostics` tool, which executes ping, traceroute, DNS resolution, and port scans simultaneously, returning a massive 20,000-token JSON response. When users ask 'Is port 443 open on server A?', Claude calls the tool but often hallucinates the answer because the specific port status is buried deep in the massive output. Which tool design strategy best resolves this?

- A) Split the generic tool into `run_ping`, `run_traceroute`, `check_dns`, and `scan_ports` for narrow, purpose-specific output contracts.
- B) Increase the model's temperature to 0.9 so it samples less common tokens and surfaces the port status buried in the 20,000-token JSON response.
- C) Update the tool description to instruct Claude to parse the JSON response for the `port_443` field and report its value before answering the user.
- D) Modify the system prompt to require Claude to output a `<thinking>` block that extracts the `port_443` field from the JSON before answering.

**Answer: A**

Anthropic's documentation recommends specialized, granular tools with clear output contracts to improve accuracy and reduce hallucinations. Splitting a broad tool into purpose-specific functions means the model receives only the relevant data for the query, avoiding token bloat.

### CCA-F Q29 (Domain 2: Tool Design and MCP Integration)

A machine learning team provides a custom `train_model` MCP tool that automatically provisions GPU instances, loads datasets, and initiates training jobs in the cloud. However, when developers prompt Claude Code to 'start a training run for the new image classifier', the agent frequently attempts to write and execute raw Python scripts using `boto3` and `torch` locally, which fails due to missing hardware. How should the architect fix this?

- A) Uninstall the `boto3` and `torch` libraries from the local development environment.
- B) Move the `train_model` tool configuration from the project's `.mcp.json` file to the user's global `~/.claude.json` to elevate its priority.
- C) Enhance the `train_model` tool description to explicitly state that it handles all infrastructure and dependencies, and is the required method over writing local scripts.
- D) Change the custom `train_model` tool's execution mode to asynchronous.

**Answer: C**

Enhancing the tool description is the most effective way to influence agent behavior. Explicitly stating that the tool handles infrastructure provisioning and dependency management provides the semantic guidance Claude needs to prefer it over generating local code.

### CCA-F Q30 (Domain 2: Tool Design and MCP Integration)

A QA engineering team has developed a custom visual_diff_analyzer MCP tool that uses a specialized computer vision model to compare UI screenshots. However, when developers prompt Claude Code to 'compare the staging UI to production', the agent consistently attempts to use built-in bash tools to run diff or cmp on the raw image binaries, which fails. What is the most architecturally appropriate way to correct this behavior?

- A) Remove the built-in bash tools from the agent's execution environment by applying a strict restriction policy in the .mcp.json file.
- B) Configure the custom tool as an MCP resource instead of a tool, forcing the agent to read the visual diff passively.
- C) Rename the custom tool to diff to intentionally overwrite the built-in tool in the agent's tool registry.
- D) Enhance the visual_diff_analyzer tool description to explicitly detail its computer vision capabilities, expected image inputs, and why it must be used instead of standard binary comparison tools.

**Answer: D**

Claude selects tools based on the semantic descriptions in the MCP server metadata. Detailing specific use cases, input requirements, and superiority over standard utilities gives Claude's reasoning engine what it needs to route the task to the specialized tool.

### CCA-F Q32 (Domain 2: Tool Design and MCP Integration)

An architect is reviewing a pull request that adds a new custom MCP server to a team's repository. The server provides a tool called `analyze_logs` for querying a proprietary log aggregation system. During testing, the architect notices that Claude Code frequently ignores this tool and instead tries to write custom Python scripts to download and parse raw log files. What is the most likely cause of this behavior?

- A) The log aggregation system's API is returning data in JSON format, which Claude Code cannot process natively.
- B) The `analyze_logs` tool description lacks sufficient detail about its capabilities, outputs, and why it is superior to manual script execution.
- C) The environment variables for the log aggregation system were not properly expanded in the .mcp.json configuration.
- D) The custom MCP server was configured in the ~/.claude.json file instead of the project's .mcp.json file.

**Answer: B**

LLMs rely on tool descriptions and metadata to decide whether a tool suits a task. If the description is vague or lacks clear information about efficiency and schema, the model defaults to its inherent capability to write and execute scripts as a better-understood path.

### CCA-F Q34 (Domain 2: Tool Design and MCP Integration)

An internal IT support agent uses an MCP tool to reset user passwords. A junior helpdesk staff member asks the agent to reset the CEO's password. The tool's backend denies the request due to insufficient privileges. How should the tool's error response be structured to ensure the agent handles this scenario correctly without hallucinating or retrying?

- A) Set `isError: true`, `errorCategory: "transient"`, `isRetryable: true`, and a message asking the agent to try again later.
- B) Set `isError: true`, `errorCategory: "permission"`, `isRetryable: false`, and `message: "Insufficient privileges to reset executive passwords. Escalation to Tier 3 required."`
- C) Set `isError: true`, `errorCategory: "validation"`, `isRetryable: true`, so the agent prompts the helpdesk staff to re-enter the CEO's user ID.
- D) Set `isError: false` and a message stating the reset failed, so the agent does not trigger its internal error recovery loop.

**Answer: B**

Marking isError: true with errorCategory: "permission" and isRetryable: false clearly signals a non-recoverable authorization failure. This prevents automated retry loops and provides a clear, actionable message guiding the agent toward the correct escalation path.

### CCA-F Q38 (Domain 2: Tool Design and MCP Integration)

An enterprise architecture team is designing an agentic workflow that needs to interact with a growing number of internal systems, currently including a PostgreSQL database, a Jira instance, and a proprietary CRM. They anticipate adding dozens more tools in the next year and plan to expose each system via its own MCP server. What is the most scalable and efficient architectural approach for managing tool discovery and context usage?

- A) Deploy separate MCP servers and use a 'Tool Search Tool' with `defer_loading: true` for most tools, so the agent dynamically discovers and loads only the tool definitions it needs.
- B) Build a single, monolithic 'Orchestrator' MCP server that wraps all other APIs, exposing a unified tool set to the agent.
- C) Deploy separate MCP servers for each system and configure the agent to connect to all of them at session start, loading every tool definition into the context window.
- D) Deploy an MCP Gateway and Registry and configure the agent to query the registry with structured tool names.

**Answer: A**

Anthropic introduced the Tool Search Tool as a core feature for advanced tool use. By setting `defer_loading: true` on most tools, the agent initially sees only the lightweight Tool Search Tool and any critical tools, reducing token usage by up to 85% in internal testing. It is recommended when tool definitions exceed 10,000 tokens or more than 10 tools are available.

### CCA-F Q40 (Domain 2: Tool Design and MCP Integration)

A developer is building a travel booking tool that integrates with Claude. The tool's backend API requires dates to be in `YYYY-MM-DD` format. A user provides a date as `MM/DD/YYYY`, causing a parsing error in the backend. Following the error handling principles outlined in Anthropic's API documentation, how should the tool's API respond to this invalid request?

- A) Automatically convert the date format in the backend without informing the user, to save tokens and reduce latency.
- B) Return a validation error, such as an HTTP 400 `invalid_request_error`, indicating that the request is not retryable and include a clear message specifying the required `YYYY-MM-DD` format.
- C) Return a validation error, such as an HTTP 400 `invalid_request_error`, indicating that the request is retryable and include a message stating the required format.
- D) Return a generic business error indicating the request is not retryable and stating the flight cannot be booked due to an invalid date.

**Answer: B**

Client-side issues like malformed requests should return an HTTP 400 error with a type like invalid_request_error. These errors are not retryable because the same invalid request will fail again. The response should include a clear message specifying the expected format.

### CCA-F Q41 (Domain 2: Tool Design and MCP Integration)

An e-learning platform assistant has two tools: `enroll_student` (adds an existing user to a course) and `register_user` (creates a brand new account on the platform). Users frequently say 'Register me for the Advanced Python class.' Claude calls `register_user` instead of `enroll_student`, causing the action to fail since the user already has an account. How should the architect fix this misrouting?

- A) Rename `register_user` to `create_platform_account` and `enroll_student` to `add_to_course`, updating descriptions to clearly differentiate their purposes.
- B) Combine both tools into `manage_user_lifecycle` and use an `action_type` parameter to differentiate the intent.
- C) Modify the `register_user` backend logic to automatically enroll the user in the course if an account already exists.
- D) Add a `check_account_exists` tool and instruct Claude to always call it before deciding which tool to use.

**Answer: A**

Renaming the tools to create_platform_account and add_to_course aligns with API design best practices for clarity and avoids ambiguity. This directly addresses the misrouting by making the tools' purposes self-evident to Claude.

### CCA-F Q94 (Domain 5: Context Management and Reliability)

A legal research agent is tasked with finding case precedents regarding a highly specific and obscure patent law. After executing a well-formed query against the legal database, the database returns zero matching cases. How should the subagent communicate this to the coordinator?

- A) Throw a `SearchTimeoutError` to signal that the query could not be completed within the expected time.
- B) Suppress the empty result and return a closely related, but technically incorrect, case precedent to ensure the workflow continues without interruption.
- C) Return a generic 'Search Failed' error to indicate that the legal database could not process the request.
- D) Return a structured response indicating a successful query execution with zero matches, ensuring the coordinator knows this is a valid empty result rather than an access failure.

**Answer: D**

Returning a structured response indicating successful execution with zero matches accurately communicates that the search completed without errors but found no data. This semantic clarity allows the coordinator to proceed with informed logic, such as broadening the search or checking alternative sources.
