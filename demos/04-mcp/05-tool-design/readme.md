# Design Tools Claude Will Actually Pick

A server that exposes the right capability and still gets ignored is the most common MCP failure, and it is never a protocol bug. Claude selects a tool by reading its name, its description, and its schema, so those three fields are the interface.

------

## Granular Beats Generic

One `manage_aws_resource` tool with an action enum and conditional dependencies is a construction task the model gets wrong. Four narrow tools with flat schemas (`restart_ec2`, `scale_asg`, `create_snapshot`) turn a malformed payload into a recoverable wrong pick.

| Symptom | Fix |
|---|---|
| Frequent invalid-payload errors | Split into purpose-built tools with flat schemas |
| Correct call, wrong answer extracted | Split by output contract, not just by action |
| Model reasons about which fields apply | One tool per valid combination |

## The Description Is the Routing Signal

When Claude writes a Python script instead of calling the tool that does the job better, the description failed to say why the tool is preferable.

```text
Weak:   "Trains a model."
Routes: "Starts a cloud training run. Provisions GPU instances, loads the
         dataset, and initiates the job. Use this instead of writing local
         boto3 or torch scripts, which will fail without GPU hardware."
```

Names that read as near-synonyms get conflated whatever the descriptions say, so rename first: `update_contact` and `log_interaction` become `modify_contact_details` and `record_communication_event`, `register_user` and `enroll_student` become `create_platform_account` and `add_to_course`. A metaphor in the system prompt pulls the same way, so "help users unlock their potential" biases the model toward `unlock_account`.

## Resources for Bulk Reads, Tools for Actions

An agent that loops `get_policy_document` a few hundred times hits rate limits and loses the thread of what it was asked. Expose the catalog as an MCP resource and it is one read; keep tools for side effects and per-item lookups.

## How a Tool Should Fail

An error result is an instruction to the model: its structure decides whether the agent retries, escalates, or gives up.

```json
{
  "isError": true,
  "errorCategory": "permission",
  "isRetryable": false,
  "message": "Insufficient privileges to reset executive passwords. Escalation to Tier 3 required."
}
```

| Failure | Category | Retryable |
|---|---|---|
| Caller lacks the privilege | `permission` | `false` |
| Malformed input, wrong date format | `validation` | `false` |
| Upstream timeout, rate limit | `transient` | `true` |

A retryable permission denial loops against a wall, and `isError: false` on a failure makes the agent build on a result it never got. A search that matched nothing ran correctly, so it is a success with zero rows, not `SearchFailed`.

## When the Tool Count Outgrows the Context

Tool definitions occupy the context window before the session does any work. Mark most tools `defer_loading: true` and the agent starts with the Tool Search Tool plus whatever you flagged as always-on, loading the rest on demand for up to an 85% reduction in tool-definition tokens.

```json
{
  "name": "get_policy_document",
  "description": "Fetches one IAM policy document by ARN.",
  "defer_loading": true
}
```

Reach for it past ten tools, past 10,000 tokens of definitions, or when wiring several servers into one agent.

## Helpful Claude Slash Commands

| Command | Usage |
|---|---|
| `/mcp` | List every connected server and the tools it contributes |
| `/context` | Measure how much of the window tool definitions consume before deciding what to defer |
| `/cost` | Compare eager loading of every server against deferred loading |

## Key Topics covered in this module

- [Tool use overview](https://platform.claude.com/docs/en/build-with-claude/tool-use): schema design, descriptions, and how Claude selects among tools
- [Tool Search Tool and deferred loading](https://platform.claude.com/docs/en/build-with-claude/tool-use): loading definitions on demand instead of at session start
- [MCP Resources](https://modelcontextprotocol.io/docs/learn/architecture): read-heavy data exposed as resources rather than tool calls
- [Errors and error handling](https://platform.claude.com/docs/en/api/errors): retryable versus terminal categories and the HTTP status they map to
