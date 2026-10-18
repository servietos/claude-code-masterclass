# Upgrade Microsoft Agent Framework Starter using the Microsoft Learn MCP

You connect the Microsoft Agent Framework starter to a live Microsoft Foundry project, query Microsoft Learn through its MCP server for the current patterns, then plan and apply the migration. You finish with a running sample on the current API and a clear split between drift a model can fix on its own and drift that needs a decision.

---

You work in [maf-migration/](maf-migration), and the migration edits it in place.

## Step 1: Discover What Has Changed in the Framework

The Microsoft Agent Framework is pre-release software with frequent breaking changes between releases. Use the Microsoft Learn MCP server to fetch current documentation and surface anything in the starter that has drifted from the recommended API.

```text
Read demos/04-mcp/01-intro/maf-migration/main.py and requirements.txt.
Use the microsoft-learn MCP server to search for:
- "Microsoft Agent Framework Python FoundryChatClient"
- "azure-ai-projects agent framework quickstart"
For each difference between the current starter and the documented API, produce a table
with three columns:
  Location | Current code | MS Learn recommendation

Classify each row as one of: breaking change, deprecation, or style drift.
Do not edit any files.
```

**Expected Outcome:** A comparison table covering at minimum the import paths, the `.env` variable names, and the `FoundryChatClient` constructor arguments, each with a classification.

Every row comes from a page the MCP server returned; if Claude says everything looks current, ask it to re-check the `FoundryChatClient` constructor signature against the latest MS Learn sample.

## Step 2: Plan the Migration

With the gaps identified, decide which changes are safe to apply automatically and which require a decision before acting.

```text
Based on the comparison from Step 1, separate the changes into two groups:

Group A: safe to apply automatically (mechanical renames with no behavioral change)
Group B: changes that require a decision (multiple options, authentication strategy choices,
         or behavioral differences between old and new)

For each item in Group B, describe the tradeoff in one sentence.
Do not edit any files yet.
```

**Expected Outcome:** Two clean groups, with the authentication strategy (`AzureCliCredential` vs `DefaultAzureCredential` vs connection string) in Group B.

If Claude puts everything in Group A, push back and ask whether the credential choice has any implications for CI environments or managed identity setups.

## Step 3: Apply the Migration

Before this prompt, copy `maf-migration/.env copy` to `maf-migration/.env`, fill in both values from your Foundry project, run `az login`, and activate a virtual environment in `maf-migration`. Then execute the plan, reinstall dependencies to pick up the pinned version, and verify the agent runs against your Foundry deployment.

```text
Migrate demos/04-mcp/01-intro/maf-migration to the current Microsoft Agent
Framework API following the plan from Step 2.
Apply changes in this order:
1. Update requirements.txt to pin the agent-framework package to the latest version.
2. Update .env variable names if they changed.
3. Update main.py: import paths, class names, constructor arguments.
Constraints:
- Keep AzureCliCredential for local development authentication.
- Keep the agent instruction string ("You are a helpful assistant.") unchanged.
- Keep the run prompt ("tell me about the microsoft agent framework") unchanged.
- Do not add error handling beyond what already exists.
- Do not add inline comments.
After editing, run:
  pip install -r requirements.txt
  python main.py
Show the agent output.
```

**Expected Outcome:** `requirements.txt` contains a pinned version, `main.py` imports without errors, and `python main.py` prints an agent response to stdout confirming the Foundry connection works with the updated API.

The constraints pin everything not under test, so a successful run has one explanation: the migrated API.
