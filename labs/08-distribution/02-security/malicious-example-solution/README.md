# DO NOT INSTALL: deliberately malicious teaching plugin

This folder is a red-team teaching artifact for Module 08, Lab 02, Step 6. Every file here is intentionally hostile and is annotated with `# ATTACK:` comments so it is unambiguous.

## Safety rules

- Do NOT run `claude --plugin-dir` against this folder.
- Do NOT execute `hooks/postuse-exfil.sh` or `mcp-server/server.py`.
- Do NOT copy any file out of this folder without its `# ATTACK:` comments.
- The exfiltration destination is `https://example.invalid/`, a reserved TLD that does not resolve, so nothing fires even if a line is run by accident. Confirmed non-resolving during authoring.

## What it demonstrates

Three attack vectors, one per audit step in the lab:

| Attack | File | Caught by |
|---|---|---|
| Hook exfiltration of `.env` | `hooks/postuse-exfil.sh` | Step 2 (hook audit) |
| MCP description/implementation mismatch | `mcp-server/server.py` | Step 3 (MCP audit) |
| Skill prompt injection | `skills/helpful-helper/SKILL.md` | Step 4 (skill audit) |

See `HOW-THIS-WAS-CAUGHT.md` for the mapping and the exact red flag in each.
