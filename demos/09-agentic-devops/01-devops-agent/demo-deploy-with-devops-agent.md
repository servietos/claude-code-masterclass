# Build a Deployment Agent and Prove Its Deploy Loop

A deployment sub-agent is a reviewable file with three separate gates, and you write one here: frontmatter, a shell allowlist scoped to this target, a manifest it reads, and a contract that makes it prove a result. You end up holding an agent definition, a `deploy-manifest.json`, and a structured JSON response whose empty evidence arrays let a caller reject a deploy that never happened.

------

Work in topic 02's [`box-stack/`](../02-ssh-deployment/box-stack) with the box started bare (no Docker, no deploy user) as its [readme](../02-ssh-deployment/box-stack/readme.md#start-and-destroy-the-target) shows; everything this run writes there is git-ignored.

## Step 1: Write the agent definition

A sub-agent is a file, so building one means deciding in writing which tools exist for it, which shell verbs run without a decision from you, and what its system prompt tells it to do. Create `.claude/agents/ssh-deploy-agent.md` in this folder with exactly this frontmatter and body:

```text
---
name: ssh-deploy-agent
description: >-
  Deployment specialist for a containerized app on an Ubuntu host reached over SSH.
model: sonnet
tools: [Read, Write, Edit, Bash, Glob, Grep]
---
Read deploy-manifest.json before every operation. Every host, port, user, key
path, image tag and URL comes from that file. If a value you need is not in the
manifest, stop and ask for it and then write it there. Never reconstruct one
from the conversation.
```

Then scope the shell in `.claude/settings.json` (allow `Bash(ssh:*)`, `Bash(git:*)` and `Bash(ls:*)`; deny `Bash(rm:*)`, `Bash(npm:*)`, `Bash(node:*)` and `Bash(dotnet:*)`). Write `deploy-manifest.json` beside `target-box/` with host `127.0.0.1`, `sshPort` `2222`, `user` `root`, `keyFile` `target-box/keys/box_key`, `stackPath` `/opt/box-stack`, image `nginx:1.27-alpine` on `hostPort` `8080`, and `verifyUrls` `http://localhost:8080/`.

Run `/agents` and `ssh-deploy-agent` appears in the project list; its frontmatter carries no `permissions` key, because sub-agent frontmatter has no such field.

## Step 2: Run it with a too-narrow allowlist and read the refusals

Ask the agent to deploy the web service from `deploy-manifest.json`; the first run is blocked, and how you answer the block is the actual lesson.

```text
Use the ssh-deploy-agent to deploy the web service described in deploy-manifest.json.
```

Get the whole list in writing in the same session, allow only the one verb it justifies, and re-run:

```text
Before I change any permission: list every shell command you were blocked on or
expect to need, one line each. For each one give the exact command, the reason
the deployment cannot proceed without it, and whether it runs on my machine or
on the box.
```

```text
total 12
drwxr-xr-x 2 root root 4096 Jul 29 09:14 .
drwxr-xr-x 1 root root 4096 Jul 29 09:14 ..
-rw-r--r-- 1 root root  231 Jul 29 09:14 docker-compose.yml
bash: line 1: docker: command not found
```

The last column sorts the list: `scp` runs on your machine and earns `Bash(scp:*)`, while `docker exec box-target ...` is the emulator leaking into the plan.

## Step 3: Put the proof in the contract and re-run

Two independent proofs are required because neither is sufficient: a live check says something answers, and a container check says the thing answering is the build you shipped. Append this to the agent file below its existing body and run the deployment one more time:

```text
## Verification
A command exiting 0 is not a proof. An empty proof is a failure, never a success.
## Response
Return one JSON object and nothing else: no prose, no Markdown fence.
Leave verifiedUrls and containerState empty when you could not gather them, and
put the blocking error in errors. Never fill either array with a value you did
not read from the host.
```

```json
{
  "status": "partial",
  "verifiedUrls": [],
  "containerState": [],
  "errors": ["bash: line 1: docker: command not found"]
}
```

Your `status` may come back `failure` or `partial`; the two empty arrays will not, and an orchestrator can reject them on a schema check.
