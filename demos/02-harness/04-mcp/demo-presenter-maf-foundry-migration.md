---
presents: demo-maf-foundry-migration.md
budget: 5 min
beats: 5
---

# Present: Upgrade Microsoft Agent Framework Starter using the Microsoft Learn MCP

A deliberately outdated starter, the current API looked up through the Microsoft Learn MCP server, then migrated. A room walks away treating a documentation MCP server as the source of truth for a moving API, and knowing which drift needs a decision.

------

This topic ships no `-solution` folder on purpose: the right-hand column moves with every pre-release, so a checked-in answer would be stale before the class runs. The run edits the starter in place, on four surfaces.

## Beats

### Beat 1: the starter is wrong on purpose, and the names disagree with the code (1 min)

**Open:** [`maf-migration/readme.md`](maf-migration/readme.md) · the bug warning and step 4's variable names · [`maf-migration/main.py`](maf-migration/main.py) · the two `os.getenv` calls
**Say:** Setup instructions drift before code does, because nothing compiles them. A crash names its own cause; a polite message about missing configuration names nothing.

```text
!!! There is a bug in this sample with the config !!!
...
4. Fill in .env:
   - PROJECT_ENDPOINT is your Azure AI Foundry project endpoint.
   - MODEL_DEPLOYMENT is your Azure AI Foundry model deployment name.
```

**Result:** the shipped `maf-migration/.env` (gitignored, so no link reaches it) already carries the names `main.py` reads, not the readme's

```ini
AZURE_PROJECT_ENDPOINT=
AZURE_MODEL_DEPLOYMENT=gpt-5.2
```

**Gotcha:** following the readme's names produces the guard-clause message and no agent call, which is the expensive failure because it looks like configuration rather than a bug.

### Beat 2: nothing is pinned, and the package is pre-release (1 min)

**Open:** [`maf-migration/requirements.txt`](maf-migration/requirements.txt) · all three lines · [`maf-migration/readme.md`](maf-migration/readme.md) · the `--pre` install in step 3
**Say:** An unpinned dependency means today's install and next week's are different software, with nothing recording which one produced a result. Pre-release status makes the model's remembered API wrong by construction.

```text
agent-framework
azure-identity
python-dotenv
```

**Result:** no new file: the migration's first edit lands in this same file as a pinned `agent-framework`, and nothing in the starter records a version today

**Gotcha:** `agent-framework` is pre-release software with breaking changes between releases, which is why the starter readme installs with `--pre`.

### Beat 3: the import path, the class name and the keyword names all move independently (1 min)

**Open:** [`maf-migration/main.py`](maf-migration/main.py) · the `agent_framework` imports and the `FoundryChatClient` call · [Step 1: Discover What Has Changed in the Framework](demo-maf-foundry-migration.md#step-1-discover-what-has-changed-in-the-framework)
**Say:** Sort the differences by when the failure surfaces, not by size. A wrong module path stops the program at import; a parameter that still exists with changed meaning runs and returns the wrong answer.

```python
from agent_framework import Agent
from agent_framework.foundry import FoundryChatClient
from azure.identity import AzureCliCredential
...
    client = FoundryChatClient(
        project_endpoint=project_endpoint,
        model=model_deployment,
        credential=AzureCliCredential(),
    )
```

**Result:** no new file: these exact lines become the Current code column of the Step 1 table, and two of the four in-place edits below

**Gotcha:** every row of that table should cite a Learn page rather than a recollection.

### Beat 4: mechanical renames and decisions are different work (1 min)

**Open:** [Step 2: Plan the Migration](demo-maf-foundry-migration.md#step-2-plan-the-migration) · the Group A / Group B split · [`maf-migration/main.py`](maf-migration/main.py) · the `AzureCliCredential()` argument
**Say:** Substitutions with one correct answer are safe to hand over wholesale; choices with several are not. Draw the split before any edit, not while reading a diff.

```text
Group A: safe to apply automatically (mechanical renames with no behavioral change)
Group B: changes that require a decision (multiple options, authentication strategy choices,
         or behavioral differences between old and new)

For each item in Group B, describe the tradeoff in one sentence.
```

**Result:** no new file: the credential landed in Group B, which is why Beat 5's Constraints pin `AzureCliCredential` before any edit is applied

**Gotcha:** if everything lands in Group A, push back and ask what the credential choice implies for a CI runner with no signed-in user.

### Beat 5: the constraints are what make the final run proof of anything (1 min)

**Open:** [Step 3: Apply the Migration](demo-maf-foundry-migration.md#step-3-apply-the-migration) · the Constraints list in the Recipe · [`maf-migration/main.py`](maf-migration/main.py)
**Say:** A successful run proves something only when exactly one variable moved. Constraints nail down everything not under test so a green result has one explanation.

```text
Constraints:
- Keep AzureCliCredential for local development authentication.
- Keep the agent instruction string ("You are a helpful assistant.") unchanged.
- Keep the run prompt ("tell me about the microsoft agent framework") unchanged.
- Do not add error handling beyond what already exists.
- Do not add inline comments.
```

**Result:** four in-place edits and an agent response on stdout from `python main.py`; nothing is checked in, which is why there is no solution folder to link

```text
maf-migration/requirements.txt   agent-framework            -> pinned to a real release
maf-migration/.env               AZURE_PROJECT_ENDPOINT     -> whatever the docs now name
maf-migration/main.py            agent_framework.foundry    -> current import path
maf-migration/main.py            FoundryChatClient(...)     -> current class and keywords
```

**Gotcha:** the ban on added error handling is the one people skip, because a `try/except` around the client converts a real migration failure into a printed message and hides the result.

## If the room asks

| Question | Answer |
|---|---|
| Why keep `AzureCliCredential` rather than `DefaultAzureCredential`? | The credential is a Group B decision with CI and managed-identity consequences, so it is fixed up front and left alone. |
| What if the Learn lookup says the starter is already current? | Ask it to re-check the `FoundryChatClient` signature and the `AZURE_PROJECT_ENDPOINT` name against the newest sample; "looks current" is what a search that found nothing returns. |
| Does this need a live Azure subscription? | Yes for the final run: a Foundry project endpoint, a model deployment, and `az login`. Steps 1 and 2 need neither. |
