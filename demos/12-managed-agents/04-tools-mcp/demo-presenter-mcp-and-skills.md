---
presents: demo-mcp-and-skills.md
budget: 4 min
beats: 4
---

# Present: Ground an Agent in Live Docs with MCP and a Skill

Two fields extend one Agent: `mcp_servers` reaches somewhere new, `skills` teaches a procedure. Four beats: the gap without them, the two-part MCP grant, the permission that decides whether the run finishes, and the skill paying for itself in the log.

------

## Beats

### Beat 1: the same task, twice, and the log tells them apart (1 min)

**Open:** [`learn-brief/brief.py`](learn-brief/brief.py) · the `agents.create` call · [Two Extension Points on the Agent](readme.md#two-extension-points-on-the-agent)
**Say:** The task text is identical in both runs. Everything that changes is Agent configuration, so the log is the only honest report of what the agent could actually reach.

```text
  tool_use      web_search {'query': 'Azure Container Apps billing Microsoft Learn'}
  tool_use      bash {'command': 'ls -la /mnt/skills; find /mnt/skills -maxdepth 3'}
  message       python-docx is available. I'll create the document directly since the skill directory appears empty in this session.
```

**Result:** [`learn-brief-solution/brief.py`](learn-brief-solution/brief.py) turns those three lines into a docs search and a skill read

**Gotcha:** the agent never says it lacked a tool; it substitutes and carries on, which is why nobody notices without the log.

### Beat 2: declaring a server is half of it (1 min)

**Open:** [`learn-brief-solution/brief.py`](learn-brief-solution/brief.py) · `mcp_servers` and the `mcp_toolset` entry · [Declaring an MCP Server](readme.md#declaring-an-mcp-server)
**Say:** Declaration and grant are separate on purpose. The declaration carries no credentials, so an Agent definition stays checkable into git while the secrets live in a vault the Session attaches.

```python
    mcp_servers=[
        {"type": "url", "name": "microsoft-learn", "url": "https://learn.microsoft.com/api/mcp"}
    ],
    tools=[
        {"type": "agent_toolset_20260401"},
        {"type": "mcp_toolset", "mcp_server_name": "microsoft-learn"},
    ],
```

**Result:** the call arrives under its own event type, not as a container tool

```text
  mcp_tool_use  microsoft_docs_search {'query': 'Azure Container Apps billing pricing'}
```

**Gotcha:** `mcp_server_name` is a string match against `name`; a server with no toolset entry fails validation rather than connecting quietly.

### Beat 3: an MCP tool asks before it runs (1 min)

**Open:** [`learn-brief-solution/brief.py`](learn-brief-solution/brief.py) · `default_config` on the toolset · [MCP Tools Default to Ask](readme.md#mcp-tools-default-to-ask)
**Say:** The default is ask, so an unattended script that ignores it looks like a fast empty run rather than a blocked one. `idle` means nobody is working, and waiting for a human is a way of not working.

```python
    "default_config": {"permission_policy": {"type": "always_allow"}},
```

**Result:** without that line the Session parks and the poll loop has to read the reason

```text
  status_idle   stop_reason=requires_action
```

**Gotcha:** answering that pause with `user.tool_confirmation` is module 05's demo; here we settle it in configuration and move on.

### Beat 4: the skill brings a procedure and a verification (1 min)

**Open:** [`learn-brief-solution/brief.py`](learn-brief-solution/brief.py) · the `skills` list · [Skills and Progressive Disclosure](readme.md#skills-and-progressive-disclosure)
**Say:** Attaching a skill costs a name and a description in context. The manifest is read only when the task calls for it, and that read is an ordinary container tool call you can point at on screen.

```python
    skills=[{"type": "anthropic", "skill_id": "docx"}],
```

**Result:** the skill renders the finished document and looks at it before claiming success

```text
  tool_use      read {'file_path': '/workspace/skills/docx/SKILL.md'}
  tool_use      bash {'command': 'cd /mnt/session/outputs && python /workspace/skills/docx/scripts/office/soffice.py --headless --c
  tool_use      read {'file_path': '/mnt/session/outputs/page-1.jpg'}
  message       The document renders correctly with a heading, three bullet findings, and source URLs.
```

**Gotcha:** nothing in the task asked for that check; it came with the skill, which is the difference between a procedure and an instruction.

## If the room asks

| Question | Answer |
|---|---|
| Where do credentials for a private MCP server go? | In a vault attached to the Session through `vault_ids`, matched to the server by URL. Never on the Agent. |
| Why did the first run produce a bigger file? | It improvised with `python-docx`; the skill's pipeline produces a leaner document and verifies it renders. |
| Does a skill cost context even when unused? | Only its name and description. The `SKILL.md` read is what puts the body in context. |
| The MCP tools do nothing and nothing errors. | The Environment is `limited` without `allow_mcp_servers`, so egress is denied at call time rather than at Agent creation. |
