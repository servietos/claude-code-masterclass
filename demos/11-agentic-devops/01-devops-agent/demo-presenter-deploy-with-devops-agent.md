---
presents: demo-deploy-with-devops-agent.md
budget: 6 min
beats: 6
---

# Present: Build a Deployment Agent and Prove Its Deploy Loop

A deployment agent is a file with three separate gates, and the report it returns is something a caller has to be able to reject. Six beats: the frontmatter, the manifest, the refusals, the body rule, the host check, the response contract.

------

Topic 01 ships no starter, so the run writes into topic 02's [`box-stack/`](../02-ssh-deployment/box-stack), where everything it creates is git-ignored.

**Shell:** in PowerShell the `$BOX` connection is a function called as `BOX ...`, because a command held in a string will not invoke, and `UserKnownHostsFile` reads `NUL`, because `/dev/null` creates a literal `dev\null` file.

## Beats

### Beat 1: an agent has three gates, and only one of them mentions the shell (1 min)

**Open:** [readme.md](readme.md#the-agent-file) · [`.claude/agents/github-devops-agent.md`](../../../.claude/agents/github-devops-agent.md) · [Step 1: Write the agent definition](demo-deploy-with-devops-agent.md#step-1-write-the-agent-definition)
**Say:** Deployment risk is not application risk, so it gets its own reviewable file. A colleague reads it in a diff instead of discovering it during an incident.

```text
Compare the two on four dimensions and answer in a table:
  - the frontmatter fields each one sets, and what each field actually gates
  - the shell verbs each one allows, and the job each verb does
  - the MCP servers each one attaches, and what breaks without them
  - what each one is told to read before it acts
```

**Result:** `.claude/agents/ssh-deploy-agent.md` plus `.claude/settings.json` (written by Step 1, in [`box-stack/`](../02-ssh-deployment/box-stack)), three allow verbs and four denies

```yaml
model: sonnet
tools: [Read, Write, Edit, Bash, Glob, Grep]
```

```json
"permissions": {
  "allow": ["Bash(ssh:*)", "Bash(git:*)", "Bash(ls:*)"],
  "deny": ["Bash(rm:*)", "Bash(npm:*)", "Bash(node:*)", "Bash(dotnet:*)"]
}
```

**Gotcha:** `tools` decides what exists, the settings rules decide what runs without you, the body decides what it may conclude. A `permissions:` block written into agent frontmatter is silently inert; there is no such field.

### Beat 2: connection facts are read, never remembered (1 min)

**Open:** [readme.md](readme.md#the-manifest-is-the-source-of-truth) · [Step 2: Write the manifest the agent reads instead of remembering](demo-deploy-with-devops-agent.md#step-2-write-the-manifest-the-agent-reads-instead-of-remembering)
**Say:** Anything an agent holds in context it can get subtly wrong on the next run, and a conversation has no version history. A committed file is diffable before it ships.

```text
For each field in that example, tell me what goes wrong if the agent infers the
value instead of reading it. Rank the fields by how expensive the failure is and
say which failure is silent rather than loud.
```

**Result:** `deploy-manifest.json` lands next to `target-box/` (written by Step 2, in [`box-stack/`](../02-ssh-deployment/box-stack)), holding every host, port, user, key path, image tag and URL

```json
{
  "host": "127.0.0.1",
  "sshPort": 2222,
  "user": "root",
  "keyFile": "target-box/keys/box_key",
...
  "verifyUrls": ["http://localhost:8080/"]
}
```

**Gotcha:** the manifest holds paths, never secrets, and `user` is the single field that changes once the topic 02 bootstrap creates the `deploy` account.

### Beat 3: a narrow allowlist does not fail the run, it hands you decisions (1.5 min)

**Open:** [readme.md](readme.md#the-shell-allowlist) · [Step 3: Run it with a too-narrow allowlist and read the refusals](demo-deploy-with-devops-agent.md#step-3-run-it-with-a-too-narrow-allowlist-and-read-the-refusals)
**Say:** The refusals are a better inventory of what the job needs than anything you would write in advance. Get the whole list in writing before answering any of it.

```text
Before I change any permission: list every shell command you were blocked on or
expect to need, one line each. For each one give the exact command, the reason
the deployment cannot proceed without it, and whether it runs on my machine or
on the box.
```

**Result:** exactly one rule joins `.claude/agents/ssh-deploy-agent.md` in [`box-stack/`](../02-ssh-deployment/box-stack), `"Bash(scp:*)"`, the deny list gains nothing, and the re-run gets the stack file onto the box

```text
total 12
drwxr-xr-x 2 root root 4096 Jul 29 09:14 .
drwxr-xr-x 1 root root 4096 Jul 29 09:14 ..
-rw-r--r-- 1 root root  231 Jul 29 09:14 docker-compose.yml
bash: line 1: docker: command not found
```

**Gotcha:** the last column sorts the list: `scp` runs on your machine and belongs to the deployment interface, while `docker exec box-target ...` is the local emulator leaking into the plan.

### Beat 4: what a verb-level allowlist cannot express goes in the body (0.5 min)

**Open:** [`target-box/`](../02-ssh-deployment/box-stack/target-box) · [Step 3: Run it with a too-narrow allowlist and read the refusals](demo-deploy-with-devops-agent.md#step-3-run-it-with-a-too-narrow-allowlist-and-read-the-refusals)
**Say:** A permission rule matches a command string, so it can name the program and never the purpose. Constraints that depend on purpose have to be stated in language.

```text
   Reach the box only over ssh and scp. Never touch the box through my local
   Docker daemon, never exec into the container that hosts it, and never read
   target-box/. Those paths exist because the target is a container on my
   laptop; on a real VM they do not exist at all.
```

**Result:** those four lines are appended to the body of `.claude/agents/ssh-deploy-agent.md` in [`box-stack/`](../02-ssh-deployment/box-stack), which now carries four allow rules and one body rule.

**Gotcha:** no allowlist entry can tell a legitimate `docker` command apart from one reaching into the local emulator, which is why this lands as prose rather than a pattern.

### Beat 5: every command completed and the deployment still did not happen (1 min)

**Open:** [readme.md](readme.md#the-deploy-then-prove-loop) · [Step 4: Ask for a report you cannot check](demo-deploy-with-devops-agent.md#step-4-ask-for-a-report-you-cannot-check)
**Say:** A transcript records what was attempted and a host records what is true. Reading the host directly costs one command.

```bash
$BOX root@127.0.0.1 'docker ps; ls /opt/box-stack; curl -s -o /dev/null -w "%{http_code}\n" http://localhost:8080/'
```

**Result:** the run's whole footprint on the box is one file, `/opt/box-stack/docker-compose.yml`, copied from the `agent-compose.yml` the agent wrote in [`box-stack/`](../02-ssh-deployment/box-stack)

```text
bash: line 1: docker: command not found
docker-compose.yml
000
```

**Gotcha:** the agent's sentence may have said as much, but only because the model chose to: a sentence has no field to inspect and no empty array to reject.

### Beat 6: `verifiedUrls` and `containerState` are the contract's teeth (1 min)

**Open:** [readme.md](readme.md#the-structured-response-contract) · [Step 5: Put the proof in the contract and re-run](demo-deploy-with-devops-agent.md#step-5-put-the-proof-in-the-contract-and-re-run)
**Say:** An orchestrator has to decide whether to believe the report, and prose gives it nothing to check. Design the fields a caller can reject it on.

```json
      "verifiedUrls": [{ "url": "<url>", "httpStatus": 0 }],
      "containerState": [{ "service": "<name>", "state": "<state>", "health": "<health>" }],
      "summary": "<one sentence describing what was deployed>",
      "errors": ["<message>"]
    }
```

**Result:** the re-run returns one JSON object with both evidence arrays empty, forced by the `## Verification` and `## Response` sections Step 5 appends to `.claude/agents/ssh-deploy-agent.md` in [`box-stack/`](../02-ssh-deployment/box-stack)

```json
{
  "status": "partial",
...
  "filesChanged": ["/opt/box-stack/docker-compose.yml"],
  "verifiedUrls": [],
  "containerState": [],
...
  "errors": ["bash: line 1: docker: command not found"]
}
```

**Gotcha:** present that as the demo working, because two empty arrays are what an orchestrator rejects on a schema check rather than on a reading of English.

## If the room asks

| Question | Answer |
|---|---|
| Why not allow `Bash(*)` once and get on with it? | The emulator commands share a verb with the legitimate ones; only where each runs separates them, one rule at a time. |
| Does `Bash(ssh:*)` not already hand over the whole box? | It does; the allowlist never constrains the far side, so the guardrail there is the deploy user's own privileges. |
| Which manifest field hurts most when it is inferred? | The image tag, silently: `docker compose pull` on a stale tag exits 0, `up -d` sees no change, and the run reports success over an unchanged site. |
