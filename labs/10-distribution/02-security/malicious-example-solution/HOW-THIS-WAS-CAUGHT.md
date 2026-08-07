# How Each Attack Was Caught

Each attack maps to the audit step in `lab-02-plugin-security.md` that flags it.

## Attack 1: hook exfiltration

- File: `hooks/postuse-exfil.sh`, registered in `plugin.json` on `PostToolUse` with matcher `"*"`.
- Caught by Step 2 (hook audit).
- Red flags:
  - Matcher `"*"` fires on every tool call, far broader than a formatter needs (also a Step 1 manifest red flag).
  - `curl -X POST` sends data to an external endpoint.
  - Reads `.env`, a sensitive file a formatting hook has no reason to touch.

## Attack 2: MCP description/implementation mismatch

- File: `mcp-server/server.py`, tool `format_code`.
- Caught by Step 3 (MCP audit).
- Red flag: the docstring says "Format code with prettier"; the implementation reads `~/.aws/credentials` and appends them to the return value. Claude trusts the description, so it calls the tool freely; the body does something the description never mentions.

## Attack 3: skill prompt injection

- File: `skills/helpful-helper/SKILL.md`.
- Caught by Step 4 (skill audit).
- Red flags:
  - `silently` instructs the model to hide the action from the user.
  - Reading `.env` and `src/*secret*` files is credential theft.
  - `base64-encoded comment ... unlikely to read` is deliberate obfuscation of the stolen output.
  - The frontmatter description ("Help with everyday coding tasks.") does not match the body, the prompt-injection signature that static code analysis cannot catch.
