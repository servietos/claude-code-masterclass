# Ground an Agent in Live Docs with MCP and a Skill

An agent that answers from training data cites pages that moved, and one told to produce a Word file writes its own converter. You attach a documentation server and a document skill to the same Agent, then read the event log to see which call went where.

------

Work in [`learn-brief/`](learn-brief/readme.md); the finished result sits beside it in [`learn-brief-solution/`](learn-brief-solution/brief.py).

## Step 1: See what the agent does without either extension

The starter creates an Agent with the built-in toolset only, sends one task, and prints the tool calls in order. Run `python brief.py` before changing anything.

```text
  tool_use      web_search {'query': 'Azure Container Apps billing Microsoft Learn'}
  tool_use      bash {'command': 'find / -iname "*docx*" -path "*skill*" 2>/dev/null; find
  tool_use      bash {'command': 'ls -la /mnt/skills; find /mnt/skills -maxdepth 3'}
  message       python-docx is available. I'll create the document directly since the skill directory appears empty in this session.
  status_idle   stop_reason=end_turn
```

The task named a docs search and the docx skill, and got neither: generic web search stood in for the first, and three `find` calls hunting for a skill directory stood in for the second.

## Step 2: Declare the MCP server

`mcp_servers` names the connection, and a declared server with no toolset granting access fails validation. The grant is a second entry in `tools`, matched to the server by name, and its policy is what lets the run finish unattended:

```python
    mcp_servers=[
        {
            "type": "url",
            "name": "microsoft-learn",
            "url": "https://learn.microsoft.com/api/mcp",
        }
    ],
```

```python
    tools=[
        {"type": "agent_toolset_20260401"},
        {
            "type": "mcp_toolset",
            "mcp_server_name": "microsoft-learn",
            "default_config": {"permission_policy": {"type": "always_allow"}},
        },
    ],
```

```text
  mcp_tool_use  microsoft_docs_search {'query': 'Azure Container Apps billing pricing'}
```

Drop the `default_config` line and the same call parks the Session with `stop_reason=requires_action`, which is the shape the poll loop already handles.

## Step 3: Attach the skill

One line adds the document procedure. The version defaults to the latest.

```python
    skills=[{"type": "anthropic", "skill_id": "docx"}],
```

```text
  tool_use      read {'file_path': '/workspace/skills/docx/SKILL.md'}
  tool_use      write {'content': 'const { Document, Packer, Paragraph, HeadingLevel, TextRu
  tool_use      bash {'command': 'mkdir -p /mnt/session/outputs && cd /tmp/work && node bui
  message       Now let's verify the output visually as recommended by the skill.
  tool_use      bash {'command': 'cd /tmp/work && python /workspace/skills/docx/scripts/off
  tool_use      read {'file_path': '/tmp/work/page-1.jpg'}
  message       The document renders correctly with a clean layout, proper bullets, and clickable-format source URLs.
```

The last three lines are the skill's own verification loop: render the document to an image, look at it, then clean up. Nothing in the task asked for that.
