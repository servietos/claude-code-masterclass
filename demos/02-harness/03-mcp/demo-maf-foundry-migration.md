# Upgrade Microsoft Agent Framework Starter using the Microsoft Learn MCP

A documentation MCP server gives Claude the current API of a fast-moving framework instead of whatever it remembers. You connect the Microsoft Agent Framework starter to a live Azure AI Foundry project, query Microsoft Learn through its MCP server for the current patterns, then plan and apply the migration. You finish with a running sample on the current API and a clear split between drift a model can fix on its own and drift that needs a decision.

---

## Setup

This lab requires an Azure subscription with Azure AI Foundry enabled and at least one model deployment configured.

Open `demos/02-harness/03-mcp/maf-migration/.env` and fill in both values:

```ini
AZURE_PROJECT_ENDPOINT=https://<your-project>.services.ai.azure.com/api/projects/<project-id>
AZURE_MODEL_DEPLOYMENT=gpt-4o
```

You can find both values in the Azure AI Foundry portal: open your project, copy the endpoint from the project overview page, and copy the deployment name from the Models or Deployments tab.

Sign in to Azure so the credential chain can authenticate:

```bash
az login
```

Create a virtual environment, activate it, and install dependencies.

Bash:

```bash
cd demos/02-harness/03-mcp/maf-migration
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

PowerShell:

```powershell
cd demos/02-harness/03-mcp/maf-migration
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

Run the starter to confirm a working connection:

```bash
python main.py
```

A response printed to stdout from the agent confirms the setup is complete.

---

## Step 1: Discover What Has Changed in the Framework

**Overview:** The Microsoft Agent Framework is pre-release software with frequent breaking changes between releases. Before touching any code, use the Microsoft Learn MCP server to fetch current documentation and surface anything in the starter that has drifted from the recommended API.

**Research / Planning / Discussion:**

```text
Read the files demos/02-harness/03-mcp/maf-migration/main.py and
demos/02-harness/03-mcp/maf-migration/requirements.txt.

Search Microsoft Learn for the latest Microsoft Agent Framework (agent-framework)
documentation. Focus on:
- The current import paths for Agent and FoundryChatClient
- The constructor signature for FoundryChatClient
- The recommended environment variable names for the project endpoint and model deployment
- The recommended authentication approach for local development

List everything that differs from the current starter code. Do not edit any files yet.
```

**Finding:** Claude should produce a comparison list or table showing the current starter code versus what the docs now recommend. Look specifically for renamed classes, changed constructor parameter names, and updated environment variable names. If Claude says everything looks current, ask it to re-check the `FoundryChatClient` constructor signature and confirm the `AZURE_PROJECT_ENDPOINT` variable name against the latest MS Learn sample.

**Recipe:**

```text
Read demos/02-harness/03-mcp/maf-migration/main.py and requirements.txt.

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

---

## Step 2: Plan the Migration

**Overview:** With the gaps identified, decide which changes are safe to apply automatically and which require a decision before acting. This step prevents blindly applying a patch that may break authentication or swap in the wrong class.

**Research / Planning / Discussion:**

```text
Based on the comparison from Step 1, separate the changes into two groups:

Group A: safe to apply automatically (mechanical renames with no behavioral change)
Group B: changes that require a decision (multiple options, authentication strategy choices,
         or behavioral differences between old and new)

For each item in Group B, describe the tradeoff in one sentence.
Do not edit any files yet.
```

**Finding:** Claude should split the list cleanly. Authentication strategy (AzureCliCredential vs DefaultAzureCredential vs connection string) is almost always a Group B decision. If Claude puts everything in Group A, push back and ask whether the credential choice has any implications for CI environments or managed identity setups.

**Recipe:**

```text
Based on the Microsoft Learn documentation you found in Step 1, outline a migration plan
for demos/02-harness/03-mcp/maf-migration as a numbered list.

For each step, state: what file changes, what the old value is, and what the new value is.
Where a decision is needed, state the recommended option and one sentence of reasoning.

Keep AzureCliCredential for local development.
Do not edit any files yet.
```

**Expected Outcome:** A numbered migration plan listing every file change with before/after values, and a clear recommendation for any decision point.

---

## Step 3: Apply the Migration

**Overview:** Execute the migration plan, reinstall dependencies to pick up the pinned version, and verify the agent runs against your Foundry deployment.

**Research / Planning / Discussion:**

```text
Before applying the migration, read the current requirements.txt and check PyPI via
Microsoft Learn or web search for the latest published version of the agent-framework package.

Is the version in requirements.txt pinned? If not, what is the latest stable (or pre-release)
version available? One sentence answer.
```

**Finding:** Claude should confirm whether `requirements.txt` pins a version and name the latest available release. If the package has only pre-release versions, Claude should note that and include the `--pre` flag in the install command.

**Recipe:**

```text
Migrate demos/02-harness/03-mcp/maf-migration to the current Microsoft Agent
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

