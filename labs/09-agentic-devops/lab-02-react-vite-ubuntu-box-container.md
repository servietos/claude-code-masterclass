# Deploy a React + Vite App to the Ubuntu Box

Build and deploy the `react-devops` app using Claude Code and Docker. You will build the app image on your own machine, ship it to the Ubuntu box from Lab 01 over SSH, run it there, and prove it serves. Where Lab 01 put a Caddy edge and a TLS certificate in front of the app, this lab is the direct route: the app's own nginx container, published on a port, reached over an SSH tunnel.

This lab is an optional companion to the module's core lab, [Deploy a Containerized React App to an Ubuntu Box over SSH](lab-01-deploy-to-an-ubuntu-box-container.md). Both labs deploy this same `react-devops` app to the same box. Lab 01 hardened the box, built a Caddy edge and terminated TLS, so it teaches the operational spine of a deployment. This lab drops the edge and the certificate to isolate the one thing a managed platform hides: how the build artifact actually gets onto the host and becomes a running, reachable service.

Each step contains:

- **Goal**: what you are building
- **Prompt or command**: what you run
- **Expected result**: what the outcome looks like

## Prerequisites

- **Lab 01 completed at least through Step 4.** The box from [lab-01-deploy-to-an-ubuntu-box-container.md](lab-01-deploy-to-an-ubuntu-box-container.md) must be running with `deploy` created, Docker installed with the Compose plugin, and the `vfs` storage driver in place. Everything below assumes that box. If you also ran Lab 01 Step 5, root SSH is closed on it, which is why every command in this lab connects as `deploy` and never as `root`: a `root@localhost` login on a hardened box answers `Permission denied (publickey)`.
- **Docker**: Docker Desktop or Docker Engine, running before you start. The app image builds here and runs on the box.
- **A shell**: Bash (git-bash or WSL on Windows, any shell on macOS and Linux) or PowerShell 7. Every command block that is not byte-identical across the two ships a `powershell` twin below the `bash` one. Three substitutions recur and each fails silently rather than loudly: `UserKnownHostsFile=NUL` instead of `/dev/null`, `curl.exe` instead of `curl`, and a staged tar file instead of `docker save | ssh`, because PowerShell's pipeline carries .NET objects and corrupts a binary stream.
- **No GitHub account and no Node install.** The app's `dockerfile` is multi-stage and runs `npm ci` and `npm run build` inside the build container.

You work in the starter at [react-devops/](react-devops) throughout. Everything this lab adds goes into the same `deploy/` folder Lab 01 created.

---

## Where to Open Claude Code

This lab reuses the harness from Lab 01, so open Claude Code inside the lab project rather than at the repo root. The harness is project-scoped: `CLAUDE.md`, `.claude/settings.json` hooks, `.claude/agents/`, `.claude/skills/`, `.claude/commands/` and `.mcp.json` all load from the directory the session was launched in. A session opened at the repo root leaves nothing you write here loadable.

The starter is already in this repo, so there is nothing to scaffold: change into it and start the session there. Run this from the repo root; both commands work unchanged in PowerShell.

**Bash:**
```bash
cd labs/09-agentic-devops/react-devops
claude
```

If you start Claude Code with the Claude Terminal extension (`Ctrl+F1` / `Cmd+F1`), it opens in the VS Code workspace folder and reuses an already-open terminal, so it will not follow the `cd` above. Open `react-devops` as the workspace folder (**File > Open Folder**) before pressing the shortcut, or run the command above in a plain terminal.

> Note: you can also skip the folder switch entirely and name the path in the prompt instead, working from a session opened anywhere in the repo:

```text
In labs/09-agentic-devops/react-devops build the app image and ship it to the box ....
```

That works for any step whose result is just files or commands. Launching inside the starter is what makes the repository a monorepo to this lab rather than the project: the repo's own `/CLAUDE.md`, `/.claude/` and `/.mcp.json` stay out of the session, and every path in the prompts below is relative to the lab folder.

---

## Step 1: Confirm the box is up and reachable

**Goal:** Prove the box from Lab 01 still answers on SSH before you build anything.

The box keeps running between labs; if you restarted Docker or rebooted, bring it up again with the exact compose file Lab 01 created. Connect as `deploy`, the user Lab 01 Step 4 created: Lab 01 Step 5 set `PermitRootLogin no`, so `root@localhost` is refused on a box that finished that lab, and `deploy` is in the `docker` group and can answer every question below.

**Bash:**
```bash
docker compose -f deploy/target-box/docker-compose.yml up -d
export DEPLOY='ssh -p 2222 -i deploy/target-box/keys/box_key -o IdentitiesOnly=yes -o UserKnownHostsFile=/dev/null -o StrictHostKeyChecking=no deploy@localhost'
$DEPLOY 'whoami; . /etc/os-release && echo $PRETTY_NAME; docker info --format "{{.Driver}}"'
```

**PowerShell:**
```powershell
docker compose -f deploy/target-box/docker-compose.yml up -d
$SshOpts = @('-i','deploy/target-box/keys/box_key','-o','IdentitiesOnly=yes','-o','UserKnownHostsFile=NUL','-o','StrictHostKeyChecking=no')
function Deploy { ssh -p 2222 @SshOpts deploy@localhost @args }
Deploy 'whoami; . /etc/os-release && echo $PRETTY_NAME; docker info --format "{{.Driver}}"'
```

A string variable is not a command prefix in PowerShell, so `$DEPLOY` becomes an options array plus a function. Both live only in the session that defined them, exactly as the Bash export does, and every later block in this lab calls them. Run these from `labs/09-agentic-devops/react-devops`: the `-i` path is relative, and from any other directory `ssh` finds no key and reports `Permission denied (publickey)`. Single quotes are literal in both shells, so the remote command reaches the box untouched.

**Expected result:** `deploy` on `Ubuntu 24.04.x LTS`, with the storage driver `vfs` from Lab 01 Step 4. If the driver reads `overlayfs` or `overlay2`, the Lab 01 `daemon.json` did not land: write `/etc/docker/daemon.json` with `{ "storage-driver": "vfs" }` and restart docker inside the box before continuing, or the first container run on the box fails with an overlay mount error.

---

## Step 2: Build the app image

**Goal:** Produce a runnable image of the app on your own machine.

The starter ships a multi-stage `dockerfile`: a `node:22-alpine` build stage that runs `npm ci` and `npm run build`, and an `nginx:1.27-alpine` runtime stage that serves `dist/` with the SPA fallback in `conf/nginx.conf`. Nothing about it needs changing. Note the lowercase filename: Docker looks for `Dockerfile` by default, so pass `-f dockerfile` explicitly.

Lab 01 left `vite.config.ts` without a `base` line, which is what this lab wants: the app serves from the domain root. If a `base: '/react-devops/'` line has appeared, remove it before building, or expect every URL below to need the `/react-devops/` prefix.

**Commands:**

**Bash:**
```bash
docker build -f dockerfile -t react-devops:lab2 .
```

**Expected result:** The build ends with `naming to docker.io/library/react-devops:lab2`. The tag is a local one, deliberately not the `v1` Lab 01 shipped, so the two stacks can sit side by side on the box without a name collision.

---

## Step 3: Ship the image to the box without a registry

**Goal:** Get the image onto the box using nothing but SSH.

There is no registry between your machine and the box. Stream the image over the connection with a pipe: `docker save` writes the image as a tar stream, `gzip` compresses it, and `docker load` on the far side reads it back. This command is why the lab needs a bash shell.

**Commands:**

**Bash:**
```bash
docker save react-devops:lab2 | gzip -1 | $DEPLOY 'docker load'
$DEPLOY 'docker images react-devops'
```

**PowerShell:**
```powershell
docker save react-devops:lab2 -o deploy/react-devops-lab2.tar
scp -P 2222 @SshOpts deploy/react-devops-lab2.tar deploy@localhost:/tmp/
Deploy 'docker load -i /tmp/react-devops-lab2.tar && rm /tmp/react-devops-lab2.tar'
Deploy 'docker images react-devops'
```

This is the one command in the lab that changes shape rather than spelling. **PowerShell's pipeline carries .NET objects, not bytes**, and re-encodes anything crossing it as text, so the Bash pipe would hand the far side a corrupted tar and `docker load` would fail on an archive it cannot read. Stage the image as a file, copy it with `scp`, load it from disk. Still no registry, still only SSH.

**Expected result:** `docker load` prints `Loaded image: react-devops:lab2`, and `docker images` on the box lists `react-devops lab2`. The stream is a few tens of megabytes and takes well under a minute over a local connection.

---

## Step 4: Run the app on the box

**Goal:** Start the app container on the box and publish it on a port nothing else uses.

Lab 01's Caddy stack holds the box's published 80 and 443, so this app publishes a dedicated host port instead: 8081 on the box's own interface. `--name` keeps the container findable, `--restart unless-stopped` keeps it running across reboots, and `-p 8081:80` publishes the container's nginx port on the box.

**Commands:**

**Bash:**
```bash
$DEPLOY 'docker run -d --name react-devops-lab2 --restart unless-stopped -p 8081:80 react-devops:lab2'
$DEPLOY 'docker ps --filter name=react-devops-lab2 --format "{{.Names}}  {{.Status}}  {{.Ports}}"'
```

**PowerShell:**
```powershell
Deploy 'docker run -d --name react-devops-lab2 --restart unless-stopped -p 8081:80 react-devops:lab2'
Deploy 'docker ps --filter name=react-devops-lab2 --format "{{.Names}}  {{.Status}}  {{.Ports}}"'
```

**Expected result:** The container reports `Up` and `0.0.0.0:8081->80/tcp` in the `PORTS` column. The app is now listening on the box, but nothing on your host can reach port 8081 of the box yet, because Docker Desktop only forwards the ports the compose file declared (2222, 8080, 8443).

---

## Step 5: Prove the app serves, through an SSH tunnel

**Goal:** Verify the running container from your own machine.

The box is a container on your host, so its published ports are not reachable directly: Docker Desktop's NAT only exposes what the compose file mapped. The SSH tunnel is the general tool here, and it is exactly how you would reach a service on a remote VM that listens on a private interface. A second SSH session forwards your local port 8081 to the box's 8081:

**Commands (in a second terminal, or as a background job):**

**Bash:**
```bash
ssh -p 2222 -i deploy/target-box/keys/box_key -o IdentitiesOnly=yes \
    -o UserKnownHostsFile=/dev/null -o StrictHostKeyChecking=no -N -L 8081:localhost:8081 deploy@localhost
```

**PowerShell:**
```powershell
ssh -p 2222 -i deploy/target-box/keys/box_key -o IdentitiesOnly=yes -o UserKnownHostsFile=NUL -o StrictHostKeyChecking=no -N -L 8081:localhost:8081 deploy@localhost
```

Then, in your original terminal:

**Bash:**
```bash
curl -s -o /dev/null -w '%{http_code}\n' http://localhost:8081/
curl -s http://localhost:8081/ | head -5
```

**PowerShell:**
```powershell
curl.exe -s -o NUL -w '%{http_code}\n' http://localhost:8081/
curl.exe -s http://localhost:8081/ | Select-Object -First 5
```

Two substitutions, both silent failures if you skip them: `curl` on its own resolves to `Invoke-WebRequest` on Windows PowerShell and takes none of these flags, and `-o /dev/null` names a real file under `C:\dev\` rather than discarding the body.

**Expected result:** `200` from the first curl, and the app's `index.html` from the second. The `-N` flag means no remote command runs; the session exists only to forward. The tunnel stays open while you verify, and closes with `Ctrl+C`.

On a real VM the tunnel is the same command with `deploy@<public-ip>` and the two `KnownHosts` options dropped, and it is the honest way to preview a service that should not be on the public interface yet.

---

## Step 6: Hand the deploy to Claude

**Goal:** Let Claude build, ship, and run the app from the facts it already has.

The box is bootstrapped and the pattern is proven, so delegate the whole loop. Claude knows the key, the host, and the ports from Lab 01; give it the one new fact it needs, the tag, and let it carry out the exact steps you just ran.

**Prompt:**

```text
Deploy the react-devops app to the box from Lab 01.

1. Build the app image locally with: docker build -f dockerfile -t react-devops:lab2 .
2. Stream it to the box: docker save react-devops:lab2 | gzip -1 | ssh -p 2222 -i deploy/target-box/keys/box_key -o IdentitiesOnly=yes -o UserKnownHostsFile=/dev/null -o StrictHostKeyChecking=no deploy@localhost "docker load"
3. On the box, run: docker run -d --name react-devops-lab2 --restart unless-stopped -p 8081:80 react-devops:lab2
4. Prove it is live: open an SSH tunnel to the box (ssh -N -L 8081:localhost:8081 ...) and curl http://localhost:8081/ expecting HTTP 200.

Report the build digest, the docker load line, the container state, and the HTTP status. Do not change anything else on the box.
```

On PowerShell, give Claude the staged form in steps 2 and 4 instead: `docker save react-devops:lab2 -o deploy/react-devops-lab2.tar`, then `scp` it to `/tmp/` and `docker load -i` it on the box, with `UserKnownHostsFile=NUL` throughout and `curl.exe` for the check. A prompt that names a Bash pipe leaves the agent to guess which shell it runs in, which is the ambiguity worth removing before you delegate.

**Expected result:** Claude reports the container running with `0.0.0.0:8081->80/tcp`, and an HTTP 200 from the app through the tunnel. If the container is already running from Step 4, it should say so rather than start a second one; the `--name` collision is the tell.

---

## Step 7: Redeploy a new tag and prove it moved

**Goal:** Ship a second build and confirm the served app changed, from the container state and the served bytes.

A deploy that reports success over an unchanged site is the failure mode this module keeps returning to. Record a distinguishing byte first, so "the site changed" is checkable rather than asserted.

**Prompt:**

```text
Create public/version.txt containing exactly the text v2, then redeploy the app:

1. Rebuild the image with tag react-devops:lab2-v2 and stream it to the box as before.
2. On the box: docker run -d --name react-devops-lab2-v2 -p 8082:80 react-devops:lab2-v2 (do not stop the old container).
3. Through the tunnel on port 8082, curl http://localhost:8082/version.txt and report the body.

Report the container state and the version.txt body.
```

**Expected result:** The new container serves `v2` from `/version.txt`. Independent proof comes from the box: `docker ps` shows both containers, and the new one carries the `lab2-v2` tag. Two versions side by side is also the honest way to test a rollout: verify the new one before you stop the old one.

Stop the old container when you are done:

**Bash:**
```bash
$DEPLOY 'docker rm -f react-devops-lab2'
```

**PowerShell:**
```powershell
Deploy 'docker rm -f react-devops-lab2'
```

---

## Cleanup

Stop and remove this lab's containers:

**Bash:**
```bash
$DEPLOY 'docker rm -f react-devops-lab2 react-devops-lab2-v2'
```

**PowerShell:**
```powershell
Deploy 'docker rm -f react-devops-lab2 react-devops-lab2-v2'
```

The box itself stays: it is shared with Lab 01, and Lab 03 deploys to it next.

---

## What You Just Practised

| Mechanic                                          | Step | Use it for                                                  |
| ------------------------------------------------- | ---- | ----------------------------------------------------------- |
| Confirming a long-lived host before building      | 1    | Every session against a box that keeps running between days |
| Building an image from the committed `dockerfile` | 2    | Reproducing a build without a local toolchain               |
| `docker save` piped into `docker load` over SSH   | 3    | Shipping an image when no registry exists                   |
| A dedicated publish port per service              | 4    | Running several apps on one host without a port war         |
| SSH tunnel for verification                       | 5    | Reaching a service on a private interface honestly          |
| Delegating the proven loop to Claude              | 6    | Turning a rehearsed sequence into a repeatable instruction  |
| A distinguishing byte in the new build            | 7    | Proving a redeploy moved the served content                 |

[Lab 03](lab-03-hugo-blog-ubuntu-box-container.md) deploys a Hugo blog to the same box, which is the static-generator half of this one: the build produces files instead of an image, and the nginx container serves them directly.
