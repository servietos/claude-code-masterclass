# Ground an Agent in Live Docs with MCP and a Skill

An agent that answers from training data cites pages that moved, and one told to produce a Word file writes its own converter. You attach a documentation server and a document skill to the same Agent, then read the event log to see which call went where. Plan for 15 minutes; you finish holding a `.docx` the agent researched, built, and checked itself.

------

Work in [`learn-brief/`](learn-brief/readme.md); the finished result sits beside it in [`learn-brief-solution/`](learn-brief-solution/brief.py).

## Run it

```bash
cd demos/12-managed-agents/04-tools-mcp/learn-brief
pip install -r requirements.txt
python brief.py
```

## Step 1: See what the agent does without either extension

The starter creates an Agent with the built-in toolset only, sends one task, and prints the tool calls in order. Run it before changing anything.

Expected output:

```text
  tool_use      web_search {'query': 'Azure Container Apps billing Microsoft Learn'}
  tool_use      bash {'command': 'find / -iname "*docx*" -path "*skill*" 2>/dev/null; find
  tool_use      bash {'command': 'ls -la /mnt/skills; find /mnt/skills -maxdepth 3'}
  message       python-docx is available. I'll create the document directly since the skill directory appears empty in this session.
  status_idle   stop_reason=end_turn
```

The task named a docs search and the docx skill, and got neither: generic web search stood in for the first, and three `find` calls hunting for a skill directory stood in for the second. Both gaps are configuration, not capability.

## Step 2: Declare the MCP server

`mcp_servers` names the connection. Add it to the `agents.create` call in `brief.py`:

```python
    mcp_servers=[
        {
            "type": "url",
            "name": "microsoft-learn",
            "url": "https://learn.microsoft.com/api/mcp",
        }
    ],
```

**Expected result:** re-running now fails validation. A declared server with no toolset granting access is an error, which is the API making the two-part shape explicit rather than silently connecting to something no tool can call.

## Step 3: Grant the toolset and settle the permission

The grant is a second entry in `tools`, matched to the server by name. The policy is what lets the run finish unattended.

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

**Expected result:** the search now runs on the orchestration layer and shows up under its own event type:

```text
  mcp_tool_use  microsoft_docs_search {'query': 'Azure Container Apps billing pricing'}
```

Drop the `default_config` line and the same call parks the Session instead, which is the shape the poll loop already handles:

```text
  status_idle   stop_reason=requires_action
```

## Step 4: Attach the skill

One line adds the document procedure. The version defaults to the latest.

```python
    skills=[{"type": "anthropic", "skill_id": "docx"}],
```

**Expected result:** the `find` hunt from Step 1 is replaced by a single read of the skill's manifest, and the agent then uses the helper the skill ships rather than improvising a converter:

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

## Step 5: Download what the run produced

Files written to `/mnt/session/outputs/` are captured by the Files API. Listing them takes both beta headers, because it is a Files endpoint taking a Managed Agents parameter:

```python
output_dir = Path(__file__).parent / "outputs"
output_dir.mkdir(exist_ok=True)
for entry in client.beta.files.list(
    scope_id=session.id, betas=["managed-agents-2026-04-01"]
).data:
    target = (output_dir / entry.filename).resolve()
    client.beta.files.download(entry.id).write_to_file(target)
    print(f"\ndownloaded   {entry.filename}  {entry.size_bytes} bytes")
    print(f"saved to     {target}")
```

**Expected result:**

```text
downloaded   container-apps-brief.docx  9215 bytes
saved to     D:\git-customers\claude-code-masterclass\demos\12-managed-agents\04-tools-mcp\learn-brief\outputs\container-apps-brief.docx
```

Open it. The headings, bullets, and links came from the docs the MCP search returned in the same turn. The byte count moves run to run because the agent writes the document fresh each time.

## Verify

The full run separates the two extension points in one log: `mcp_tool_use` for the server call, `tool_use` for everything the container did, including loading the skill. The Console trace URL the script prints replays the same sequence with span timings.

## Cleanup

The script deletes the Session and the Environment on the way out and leaves the Agent, which stays reusable. Delete the downloaded `outputs/` folder if you do not want the artifact.

## Common Failure

A poll loop that breaks on `session.status_idle` alone reports an empty run whenever an MCP tool waits for confirmation, because `requires_action` is an idle state. Break on the `stop_reason`, not on the status.
