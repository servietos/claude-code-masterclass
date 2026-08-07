# Build a Deployment Agent and Prove Its Deploy Loop

A deployment sub-agent is a reviewable file with three separate gates, and you write one here: frontmatter, a shell allowlist scoped to this target, a manifest it reads instead of remembering, and a contract that makes it prove a result rather than describe one. You run it against a deliberately bare throwaway Ubuntu box, answer the permission refusals one verb at a time, and check its prose report against the host. You end up holding an agent definition, a `deploy-manifest.json`, and a structured JSON response whose empty evidence arrays let a caller reject a deploy that never happened.

------

Budget twenty minutes; Docker is the only thing you need installed, and there is no cloud account anywhere in this demo.

---

## Setup

```bash
cd demos/11-agentic-devops/02-ssh-deployment/box-stack
ssh-keygen -t ed25519 -f target-box/keys/box_key -N "" -C "box-demo"
docker compose -f target-box/docker-compose.yml up -d --build
claude
```

The box must start **bare** for this demo, with no Docker and no deploy user on it, because the run you build here is supposed to hit a real wall and report it honestly. If you have already worked through the topic 02 bootstrap, reset the box first with `docker compose -f target-box/docker-compose.yml down -v` and bring it back up.

---

## Step 1: Write the agent definition

**Overview:** A sub-agent is a file, so building one means deciding four things in writing: which tools exist for it, which shell verbs run without a decision from you, which MCP servers it can reach, and what its system prompt tells it to do. You write a first draft here that is deliberately incomplete in two places, and each of those gaps is a later step.

**Research / Planning / Discussion:**

```text
Read ../../01-devops-agent/readme.md and ../../../../.claude/agents/github-devops-agent.md.

Compare the two on four dimensions and answer in a table:
  - the frontmatter fields each one sets, and what each field actually gates
  - the shell verbs each one allows, and the job each verb does
  - the MCP servers each one attaches, and what breaks without them
  - what each one is told to read before it acts

Then tell me which of those verbs and servers have no job at all against a plain
Ubuntu host that pulls a public image, and why.
```

**Finding:** Claude should separate `tools` (which tools exist for the agent) from `permissions.allow` (which Bash commands run without a decision from you), because they are two different gates and only the second one talks about shell verbs. On the last question the answer worth having is that `gh` has no job here (no CI built this image) and neither does the `github` MCP server, so both come out. If Claude reproduces the readme's six-verb list wholesale without asking what this target needs, push back: the list is per target, not a template.

**Recipe:**

```text
Create .claude/agents/ssh-deploy-agent.md in this folder with exactly this
frontmatter and body, and nothing else:

---
name: ssh-deploy-agent
description: >-
  Deployment specialist for a containerized app on an Ubuntu host reached over SSH.
  Owns access checks, stack file placement, image rollout and live verification.
  Apply when the task is "deploy to the box", "bring up the stack", or
  "roll out a new image tag".
model: sonnet
tools: [Read, Write, Edit, Bash, Glob, Grep]
---

You deploy one containerized stack to one Ubuntu host over SSH.

Read deploy-manifest.json before every operation. Every host, port, user, key
path, image tag and URL comes from that file. If a value you need is not in the
manifest, stop and ask for it and then write it there. Never reconstruct one
from the conversation.

Prove SSH access before you write anything, place anything or pull anything.

Stop and ask instead of deciding when a container name or host port is already
taken, when a container was already unhealthy before you started, when the key
authenticates as a different user than the manifest names, or when a cleanup
would remove a volume, an image or a credential file.

Do not add anything I did not ask for. In particular do not add a verification
section yet.
```

Then scope the shell. Agent frontmatter names tools, not verbs, so the command-level rules go in `.claude/settings.json` beside the agent:

```text
Create .claude/settings.json in this folder with a permissions block that allows
Bash(ssh:*), Bash(git:*) and Bash(ls:*), and denies Bash(rm:*), Bash(npm:*),
Bash(node:*) and Bash(dotnet:*). Nothing else.
```

**Expected Outcome:** `.claude/agents/ssh-deploy-agent.md` exists in the folder you launched Claude from, which is why the agent will be discoverable at all. Run `/agents` and `ssh-deploy-agent` appears in the project list. The allowlist in `settings.json` has three verbs, the deny list has four, and there is no `docker` and no `scp` in either. There is no `permissions` key in the agent's own frontmatter, because sub-agent frontmatter has no such field: writing one there looks like a boundary and enforces nothing.

---

## Step 2: Write the manifest the agent reads instead of remembering

**Overview:** Connection details are exactly the facts a model will happily reconstruct from a conversation two days old, and a reconstructed port number is a deploy against the wrong service. The manifest makes those facts committed, reviewable and diffable, so a wrong value is something you can read rather than something you have to debug.

**Research / Planning / Discussion:**

```text
Read the "The Manifest Is the Source of Truth" section of ../../01-devops-agent/readme.md.

For each field in that example, tell me what goes wrong if the agent infers the
value instead of reading it. Rank the fields by how expensive the failure is and
say which failure is silent rather than loud.

Then tell me which fields this local box needs that a hyperscaler VM would not.
```

**Finding:** Claude should name the image tag as the expensive one and the silent one: `docker compose pull` on a stale tag exits 0, `up -d` sees no change, and the run reports success over an unchanged site. The fields specific to this box are the non-standard `sshPort` and the two `KnownHosts` options, which exist only because the target is disposable and gets a new host key on every rebuild. If Claude suggests putting the key material or a registry password in the manifest, push back: the manifest holds paths, never secrets.

**Recipe:**

```text
Create deploy-manifest.json in this folder with exactly this content:

{
  "host": "127.0.0.1",
  "sshPort": 2222,
  "user": "root",
  "keyFile": "target-box/keys/box_key",
  "sshOptions": [
    "-o IdentitiesOnly=yes",
    "-o UserKnownHostsFile=/dev/null",
    "-o StrictHostKeyChecking=no"
  ],
  "stackPath": "/opt/box-stack",
  "services": {
    "web": {
      "image": "nginx:1.27-alpine",
      "internalPort": 80,
      "hostPort": 8080
    }
  },
  "verifyUrls": ["http://localhost:8080/"]
}
```

**Expected Outcome:** `deploy-manifest.json` sits next to `target-box/`, and every value the agent needs is in it. `user` is `root` because the box is still bare; once the topic 02 bootstrap creates the `deploy` user, that one field changes and nothing else does. `verifyUrls` uses `localhost` on purpose, because the service binds the host's internal network and the check therefore has to run on the host.

---

## Step 3: Run it with a too-narrow allowlist and read the refusals

**Overview:** The first run is blocked, and how you answer the block is the actual lesson. A narrow allowlist does not fail a run, it converts every missing verb into a decision you make, and reflexively widening the list at that prompt is how an agent's permission set quietly grows into a general-purpose shell.

**Research / Planning / Discussion:**

```text
Use the ssh-deploy-agent to deploy the web service from deploy-manifest.json.

Read every connection value from deploy-manifest.json. Do not take any host,
port, user, key path or image tag from this message or from memory.

1. Prove access first and report the OS release you found.
2. Write the Compose file for the web service as agent-compose.yml in this folder,
   then place it at stackPath/docker-compose.yml on the box. Do not read or edit
   the docker-compose.yml or Caddyfile already in this folder; those are topic 02's
   starter stubs and are not part of this deployment.
3. Pull the image the manifest names and bring the service up.
4. Report what happened.

When a command you need is not permitted, stop and tell me the exact command and
what it was for. Do not look for another way to run it.
```

You will be asked to decide on at least one command. Before you answer anything, get the whole list in writing:

```text
Before I change any permission: list every shell command you were blocked on or
expect to need, one line each. For each one give the exact command, the reason
the deployment cannot proceed without it, and whether it runs on my machine or
on the box.
```

**Finding:** The last column is what sorts the list. `scp`, placing the stack file at `stackPath`, runs on your machine and is genuinely part of the deployment interface, so it earns a permanent allow rule. Anything that runs on your machine only because this box happens to be a local container (`docker exec box-target ...`, `docker compose -f target-box/docker-compose.yml exec box ...`) is the emulator leaking into the plan, and no allowlist entry can tell those `docker` commands apart from the legitimate ones. If Claude proposes `Bash(*)`, or hands you a list of five verbs to add at once, refuse the whole proposal and ask again for one verb per justified command.

**Recipe:**

```text
Two changes, and nothing else.

1. In .claude/agents/ssh-deploy-agent.md add exactly one rule to permissions.allow:
     "Bash(scp:*)"
   Leave every other rule as it is, and add nothing to the deny list.

2. Append this rule to the body, because a verb-level allowlist cannot express it:

   Reach the box only over ssh and scp. Never touch the box through my local
   Docker daemon, never exec into the container that hosts it, and never read
   target-box/. Those paths exist because the target is a container on my
   laptop; on a real VM they do not exist at all.

Then re-run the deployment with the same four steps.
```

**Expected Outcome:** The agent file has four allow rules (`ssh`, `scp`, `git`, `ls`) and one new body rule. The re-run gets past file placement: `ssh` into the box yourself and the Compose file is there.

```bash
export BOX='ssh -p 2222 -i target-box/keys/box_key -o IdentitiesOnly=yes -o UserKnownHostsFile=/dev/null -o StrictHostKeyChecking=no'
$BOX root@127.0.0.1 'ls -la /opt/box-stack; docker compose version'
```

PowerShell cannot run a command it holds in a string, so define a function instead of a variable. `UserKnownHostsFile` becomes `NUL` here, because Win32-OpenSSH takes the Bash form literally and creates a file called `dev\null` in the current folder:

```powershell
function BOX { ssh -p 2222 -i target-box/keys/box_key -o IdentitiesOnly=yes -o UserKnownHostsFile=NUL -o StrictHostKeyChecking=no @args }
BOX root@127.0.0.1 'ls -la /opt/box-stack; docker compose version'
```

Every later `$BOX ...` line in this demo runs as `BOX ...` in PowerShell; only the leading `$` comes off.

Expected output:

```text
total 12
drwxr-xr-x 2 root root 4096 Jul 29 09:14 .
drwxr-xr-x 1 root root 4096 Jul 29 09:14 ..
-rw-r--r-- 1 root root  231 Jul 29 09:14 docker-compose.yml
bash: line 1: docker: command not found
```

The six-verb list on the theory page became four here. `gh` came out because no pipeline built this image and local `docker` came out because every container command runs on the far side of the connection, which is the same reason the body rule exists.

---

## Step 4: Ask for a report you cannot check

**Overview:** The box has a stack file on it and no Docker, so the deployment cannot have happened. This step asks for the result in prose, which is the default shape of every agent answer, and then compares that prose against the host.

**Research / Planning / Discussion:**

```text
Ask the ssh-deploy-agent one question and nothing more:

  Is the web service deployed? Answer in one sentence.
```

Then check the host yourself, from your own terminal:

```bash
$BOX root@127.0.0.1 'docker ps; ls /opt/box-stack; curl -s -o /dev/null -w "%{http_code}\n" http://localhost:8080/'
```

Expected output:

```text
bash: line 1: docker: command not found
docker-compose.yml
000
```

**Finding:** Read the one-sentence answer against those three lines. Nothing is running, nothing answers on 8080, and the only thing that changed on the box is one file. The sentence may well have told you that, and that is the point rather than a reprieve: it told you because the model chose to, not because anything you wrote required it. A sentence has no field to inspect and no empty array to reject, so there is no version of it a caller can refuse automatically.

**Recipe:**

```text
Ask the agent to grade its own last answer:

  Which parts of your previous sentence did you verify against the host, and
  which parts did you infer from the commands you ran exiting without an error?
  List them in two columns.
```

**Expected Outcome:** Two columns, and the verified one is short. Placing a file was verified, the service running was not, and a `docker compose` invocation that never reached a Docker binary is not evidence of anything either way. This is the gap the next step closes, and it closes in the agent definition rather than in your prompt, because a rule you have to remember to type is a rule that goes missing on the run that matters.

---

## Step 5: Put the proof in the contract and re-run

**Overview:** The verification requirement and the response shape belong in the agent file, so every caller gets them whether or not they asked. Two independent proofs are required because neither is sufficient: a live check says something answers, and a container check says the thing answering is the build you shipped.

**Research / Planning / Discussion:**

```text
Read the "The Deploy-Then-Prove Loop" and "The Structured Response Contract"
sections of ../../01-devops-agent/readme.md.

For our manifest, write out the exact command for each proof in the claims table.
Then answer this: if the agent must return that JSON object and it has no
evidence to put in verifiedUrls or containerState, what status is honest, and
what should a caller do with it?
```

**Finding:** Claude should land on `verifiedUrls` and `containerState` being the contract's teeth: they are the two fields a caller can check are non-empty before believing a `success`. Either `partial` or `failure` is defensible for our run, since one file did land on the box, and what must not happen is `success` with empty evidence. If Claude offers to report `success` because the commands it could run all completed, push back: a green command is not a live service.

**Recipe:**

```text
Append this to .claude/agents/ssh-deploy-agent.md, below what is already in the
body. Change nothing that is already there.

## Verification

A deployment is not finished until two independent proofs exist, and you may
never report success from the middle of the run.

1. Every URL in verifyUrls answers 200. Run the check on the host, because the
   service binds the internal network:
       ssh <sshOptions> -p <sshPort> -i <keyFile> <user>@<host> \
         'curl -s -o /dev/null -w "%{http_code}" <url>'
2. The container serving the service runs the image tag the manifest names, and
   the stack is healthy:
       ssh ... 'docker inspect <name> --format "{{.Image}} {{.Config.Image}}"'
       ssh ... 'docker compose ps'
       ssh ... 'docker ps --filter health=unhealthy --format "{{.Names}}"'

Record the container count on the host before and after the run and report both.
A command exiting 0 is not a proof. An empty proof is a failure, never a success.

## Response

Return one JSON object and nothing else: no prose, no Markdown fence.

    {
      "status": "success | failure | partial",
      "target": "<user>@<host>:<port>",
      "imageTags": ["<tag>"],
      "filesChanged": ["<relative-path>"],
      "verifiedUrls": [{ "url": "<url>", "httpStatus": 0 }],
      "containerState": [{ "service": "<name>", "state": "<state>", "health": "<health>" }],
      "summary": "<one sentence describing what was deployed>",
      "errors": ["<message>"]
    }

Leave verifiedUrls and containerState empty when you could not gather them, and
put the blocking error in errors. Never fill either array with a value you did
not read from the host.
```

Then run the deployment one more time, unchanged:

```text
Use the ssh-deploy-agent to deploy the web service from deploy-manifest.json,
reading every value from that file. Return the structured response.
```

**Expected Outcome:** One JSON object, no prose around it, shaped like this:

```json
{
  "status": "partial",
  "target": "root@127.0.0.1:2222",
  "imageTags": ["nginx:1.27-alpine"],
  "filesChanged": ["/opt/box-stack/docker-compose.yml"],
  "verifiedUrls": [],
  "containerState": [],
  "summary": "Stack file placed at /opt/box-stack; the image could not be pulled because Docker is not installed on the host.",
  "errors": ["bash: line 1: docker: command not found"]
}
```

Your `status` may come back `failure` instead of `partial` and the wording of `summary` will differ; the two empty arrays will not. That is a result an orchestrator can reject on a schema check rather than on a reading of English, and it is the same object shape you would get from a real VM. To turn it into a `success`, the box needs the thing it is missing: go and bootstrap it in [Bootstrap and Harden an Ubuntu Host over SSH](../02-ssh-deployment/demo-bootstrap-and-harden.md), then flip `user` in the manifest to `deploy` and run this exact prompt again.

## Helpful Claude Slash Commands

| Command | Usage |
|---|---|
| `/agents` | Confirm `ssh-deploy-agent` was picked up from this folder, and open its definition to add the one allow rule in Step 3 |
| `/permissions` | Read the effective `allow` and `deny` rules before answering a permission prompt, so you widen one verb rather than the whole shell |
| `/context` | Check the window before the Step 5 re-run, because SSH transcripts and `docker` output fill it faster than application work |
| `/rewind` | Undo a bad edit to the agent file; remember it restores your files and the conversation, never the box |

## Key Topics Covered in This Demo

- [Claude Code sub-agents](https://code.claude.com/docs/en/sub-agents): the frontmatter fields written in Step 1 and how an agent gets its own context window
- [Claude Code settings and permissions](https://code.claude.com/docs/en/settings): the `allow` and `deny` rule syntax, and what happens to a command that matches neither
- [Claude Code MCP](https://code.claude.com/docs/en/mcp): attaching servers to one agent, and why this target needs fewer of them than a cloud one
- [OpenSSH ssh(1) manual](https://man.openbsd.org/ssh): `IdentitiesOnly` and `BatchMode`, the options that make the access check in Step 3 trustworthy
- [Docker Compose CLI reference](https://docs.docker.com/reference/cli/docker/compose/): `pull`, `up -d` and `ps`, the three commands the deploy phase runs over the wire
- [docker inspect reference](https://docs.docker.com/reference/cli/docker/inspect/): the `--format` expression that proves which image a running container was created from

