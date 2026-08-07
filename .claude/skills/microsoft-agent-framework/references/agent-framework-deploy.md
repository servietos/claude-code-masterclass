# Agent Framework Deployment

## Agent Type Decision

| `kind` in `agent.yaml` | Deployment method |
| --- | --- |
| `hosted` | Container via `azd deploy` (see [Container Deployment](#container-deployment)) |
| `prompt` | REST API `POST .../agents/{name}/versions` (see [Prompt Agent Deployment](#prompt-agent-deployment)) |

**Critical**: `azd deploy` is for container (hosted) agents ONLY. Do NOT use it for `kind: prompt` agents.

---

## Prompt Agent Deployment

A `kind: prompt` agent has no container — it runs entirely inside Foundry using a model + instructions + tools. Deploy it by creating a new version via the Foundry REST API.

### Auth

```powershell
az account set --subscription "<foundry-subscription-id>"
$token = az account get-access-token --scope "https://ai.azure.com/.default" --query accessToken -o tsv
$headers = @{ "Authorization" = "Bearer $token"; "Content-Type" = "application/json" }
```

Scope MUST be `https://ai.azure.com/.default` — not `management.azure.com`.

### Create a New Version (PowerShell)

```powershell
$body = @{
    definition = @{
        kind         = "prompt"
        model        = "gpt-5.4-mini"          # never gpt-4.1
        instructions = $instructions            # read from agent.yaml
        temperature  = 0.2
        tools        = @(@{ type = "web_search" })
        tool_choice  = "auto"
    }
} | ConvertTo-Json -Depth 10

$BASE = "https://<account>.services.ai.azure.com/api/projects/<project>"
$result = Invoke-RestMethod -Uri "$BASE/agents/<name>/versions?api-version=v1" `
    -Headers $headers -Method POST -Body $body
Write-Host "Version $($result.version) | status: $($result.status)"
```

### Version Activation

New versions become `active` automatically — Foundry routes 100% traffic to `@latest`. No separate activation call is needed.

### Verify After Deploy

```powershell
$agent = Invoke-RestMethod -Uri "$BASE/agents/<name>?api-version=v1" -Headers $headers -Method GET
$agent.versions.latest | Select-Object version, status
$agent.versions.latest.definition | Select-Object model
```

### Sync agent-metadata.yaml

After every deploy, update `.foundry/agent-metadata.yaml`:

```yaml
agentVersion: "<new-version-number>"
```

### Deployment Checklist (Prompt Agent)

1. `agent.yaml` has the correct `model`, `instructions`, `temperature`, and `tools`
2. Instructions contain ONLY what was explicitly asked for — remove any AI-generated rules not requested
3. `az account set` to the correct Foundry subscription (check `src/config.json`)
4. Run deploy PowerShell block, confirm version number and `status: active`
5. Update `agentVersion` in `.foundry/agent-metadata.yaml`

---

## Container Deployment

## When to Use

- Deploying an agent container to Foundry
- Rebuilding the container after code changes
- Verifying post-deploy health
- Fixing RBAC or container sizing issues
- First-time provisioning with `azd up`

## Deploy Commands

```bash
# First time (provision + deploy)
azd up

# Subsequent (rebuild container only)
azd deploy

# Monitor logs
azd ai agent monitor

# Show status
azd ai agent show
```

Note: `azd ai agent deploy` does not exist. Use `azd deploy`.

## Deployment Checklist

### Pre-deploy
1. `agent.yaml` declares matching `resources` values
2. `requirements.txt` is up to date with all new dependencies
3. `.env` keys for new external services are set
4. If new `FoundryAgents` config was added, `appsettings.json` is updated

### Post-deploy
5. Verify agent is responding: `azd ai agent show`
6. Test via HTTP client with sample payload
7. Check logs for errors: `azd ai agent monitor`

## Container Sizing

Valid CPU/memory pairs (fixed 1:2 ratio):

| vCPU | Memory |
| --- | --- |
| 0.5 | 1.0Gi |
| 1.0 | 2.0Gi |
| 2.0 | 4.0Gi |
| 4.0 | 8.0Gi |

## Common Issues

| Symptom | Cause | Fix |
| --- | --- | --- |
| `No such file '/app/main.py'` | Wrong COPY context in Dockerfile | `COPY src/<project>/ .` |
| `PermissionDenied` on agents/write | Missing RBAC | Assign Azure AI User role |
| Container OOM | Undersized resources | Bump to next CPU/memory pair |
