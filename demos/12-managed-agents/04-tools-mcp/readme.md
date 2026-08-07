# Extend an Agent with MCP Servers and Skills

## Two Extension Points on the Agent

An Agent starts with the built-in toolset: `bash`, `read`, `write`, `edit`, `glob`, `grep`, `web_fetch`, `web_search`. Two fields on `agents.create` extend it, and they solve different problems.

| Field | What it adds | Lives where |
|---|---|---|
| `mcp_servers` + `mcp_toolset` | Tools a third party exposes over MCP: Linear issues, GitHub pull requests, Microsoft Learn search | The orchestration layer calls the server; nothing is installed in the container |
| `skills` | Procedures and helper scripts for a task the model already has tools for: build a `.docx`, a `.xlsx`, a `.pptx` | Mounted into the container at `/workspace/skills/<name>/` |

The split is capability against procedure. An MCP server gives the agent somewhere new to reach; a skill gives it a documented way to do something with what it already reaches.

## Declaring an MCP Server

`mcp_servers` declares the connection and carries no credentials. A separate `mcp_toolset` entry in `tools` grants access, matched by name.

```python
agent = client.beta.agents.create(
    name="learn-researcher",
    model="claude-sonnet-5",
    mcp_servers=[
        {"type": "url", "name": "microsoft-learn", "url": "https://learn.microsoft.com/api/mcp"}
    ],
    tools=[
        {"type": "agent_toolset_20260401"},
        {"type": "mcp_toolset", "mcp_server_name": "microsoft-learn"},
    ],
)
```

`mcp_server_name` must match a `name` in `mcp_servers`, and a server with no toolset entry is a validation error. Maximum 20 servers per Agent, names unique.

Servers that need authentication read their credentials from a vault attached at Session creation through `vault_ids`, matched to the server by URL. The Microsoft Learn endpoint is public, so this topic needs no vault; [Run Managed Agents in Production](../03-production-features/readme.md#oauth-vaults-and-token-refresh) owns the credential path.

## MCP Tools Default to Ask

An MCP tool call arrives with `evaluated_permission` set to `ask`. The Session parks at `session.status_idle` with `stop_reason.type` of `requires_action` and waits for a `user.tool_confirmation` event naming the `agent.mcp_tool_use` event id.

For an unattended run, set the policy on the toolset instead:

```python
{
    "type": "mcp_toolset",
    "mcp_server_name": "microsoft-learn",
    "default_config": {"permission_policy": {"type": "always_allow"}},
}
```

A poll loop that breaks on `session.status_idle` alone reads that pause as a finished turn and reports an empty result. Break on a `stop_reason` other than `requires_action`. The confirmation round-trip itself belongs to [Gate an Agent on Human Approval](../05-human-in-the-loop/readme.md).

## Skills and Progressive Disclosure

Skills attach by id and default to the latest version. Anthropic ships `docx`, `xlsx`, `pptx`, and `pdf`; custom skills carry a `skill_...` id from the Skills API.

```python
skills=[
    {"type": "anthropic", "skill_id": "docx"},
    {"type": "custom", "skill_id": "skill_abc123", "version": "latest"},
]
```

Maximum 20 per Agent. Attaching a skill costs almost no context: the model sees the skill's name and description, and the full `SKILL.md` enters context only when the task calls for it. That read is visible in the event log as an ordinary `agent.tool_use` of `read` against `/workspace/skills/docx/SKILL.md`, which is why the topic's demo shows the log rather than describing the mechanism.

A skill folder also ships executable helpers. The `docx` skill carries `scripts/office/soffice.py`, which the agent uses to render its own output and check the result before reporting success.

Skills require the `read` tool, so an Agent that clears `tools` while `skills` is non-empty is rejected.

## Custom Skills Through the Skills API

Custom skills are workspace resources with their own versions, created outside the Managed Agents endpoints and referenced by id.

| Operation | Method | Path |
|---|---|---|
| Create skill | `POST` | `/v1/skills` |
| List skills | `GET` | `/v1/skills` |
| Create version | `POST` | `/v1/skills/{skill_id}/versions` |
| List versions | `GET` | `/v1/skills/{skill_id}/versions` |
| Delete version | `DELETE` | `/v1/skills/{skill_id}/versions/{version}` |

These endpoints use the `skills-2025-10-02` beta header, which the SDK sets on every `client.beta.skills` call. Pinning a `version` on the Agent gives a skill the same reproducibility that a pinned Agent version gives a Session.

## Networking Has to Allow the Server

An Environment with `networking.type` of `limited` denies egress by default, so the container cannot reach an MCP endpoint until you say so:

```python
config={
    "type": "cloud",
    "networking": {"type": "limited", "allow_mcp_servers": True},
}
```

Without `allow_mcp_servers` or an explicit `allowed_hosts` entry, the tools fail silently at call time rather than at Agent creation. An `unrestricted` Environment has no such gate.

## Reading the Event Log

The log separates the two extension points, which makes routing observable per call:

| Event | Meaning |
|---|---|
| `agent.mcp_tool_use` / `agent.mcp_tool_result` | A tool on a connected MCP server ran on the orchestration layer |
| `agent.tool_use` / `agent.tool_result` | A built-in tool ran in the container, including the `read` that loads a skill |

Files the agent writes to `/mnt/session/outputs/` are captured by the Files API. Listing them takes both beta headers, because it is a Files endpoint taking a Managed Agents parameter:

```python
client.beta.files.list(scope_id=session.id, betas=["managed-agents-2026-04-01"])
```

Indexing lags the idle event by a second or two, so an empty list right after the turn ends is worth one retry.

## Hands-On Demo

[Ground an Agent in Live Docs with MCP and a Skill](demo-mcp-and-skills.md) attaches the Microsoft Learn MCP server and the `docx` skill to one Agent, then reads the event log to watch a single turn search the docs, load the skill, and write a `.docx` you download.

## Helpful Claude Slash Commands

| Command | Usage |
|---|---|
| `/mcp` | List the MCP servers the local session reaches, and copy the URL you are about to declare on the Agent |
| `/permissions` | Draft the local allow rules that become the toolset's `permission_policy` in the hosted Agent |
| `/context` | Compare what a locally loaded skill costs against the description-only cost of attaching it to an Agent |

## Key Topics covered in this module

- [MCP Connector](https://platform.claude.com/docs/en/managed-agents/mcp-connector): server declaration, toolset grants, and vault matching by URL
- [Skills](https://platform.claude.com/docs/en/managed-agents/skills): packaging, versions, and the loading model
- [Agent Skills](https://platform.claude.com/docs/en/agents-and-tools/skills): `SKILL.md` structure and progressive disclosure
- [Tools](https://platform.claude.com/docs/en/managed-agents/tools): the built-in toolset and per-tool configuration
- [Files](https://platform.claude.com/docs/en/managed-agents/files): session outputs, listing by scope, and download
