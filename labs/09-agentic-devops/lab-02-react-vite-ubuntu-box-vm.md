# Deploy a React + Vite App to the Ubuntu Box (Azure Lab VM)

Build and deploy the `react-devops` app using Claude Code and Docker. You will build the app image on your lab VM, ship it to the Ubuntu box from Lab 01 over SSH, run it there, and prove it serves. Where Lab 01 put a Caddy edge and a TLS certificate in front of the app, this lab is the direct route: the app's own nginx container, published on a port, reached over an SSH tunnel.

This is the Azure lab VM edition of [Lab 02](lab-02-react-vite-ubuntu-box-container.md), an optional companion to the module's core lab, [Deploy a Containerized React App to an Ubuntu Box over SSH](lab-01-deploy-to-an-ubuntu-box-vm.md). Both labs deploy this same `react-devops` app to the same box. Lab 01 hardened the box, built a Caddy edge and terminated TLS, so it teaches the operational spine of a deployment. This lab drops the edge and the certificate to isolate the one thing a managed platform hides: how the build artifact actually gets onto the host and becomes a running, reachable service.

Each step contains:

- **Goal**: what you are building
- **Prompt or command**: what you run
- **Expected result**: what the outcome looks like

## Prerequisites

- **Lab 01 completed at least through Step 4.** The box from [lab-01-deploy-to-an-ubuntu-box-vm.md](lab-01-deploy-to-an-ubuntu-box-vm.md) must be running on your lab VM with `deploy` created, Docker installed with the Compose plugin, and the `vfs` storage driver in place. Everything below assumes that box. If you also ran Lab 01 Step 5, root SSH is closed on it, which is why every command in this lab connects as `deploy`: a `root@localhost` login on a hardened box answers `Permission denied (publickey)`.
- **Your lab VM, connected and signed in** as in [Connect to the lab VM](lab-01-deploy-to-an-ubuntu-box-vm.md#connect-to-the-lab-vm), with the repository cloned to `~/claude-code-masterclass`. Docker Engine on the VM builds the app image; the box runs it.
- **No GitHub account and no Node install.** The app's `dockerfile` is multi-stage and runs `npm ci` and `npm run build` inside the build container.

Every command in this lab runs in Bash on the VM, inside the `tmux` session from Lab 01 (`tmux attach -t lab`, or `tmux new -s lab` after a VM restart). You work in the starter at [react-devops/](react-devops) throughout. Everything this lab adds goes into the same `deploy/` folder Lab 01 created.

---

## Where to Open Claude Code

This lab reuses the harness from Lab 01, so open Claude Code inside the lab project. The harness is project-scoped: `CLAUDE.md`, `.claude/settings.json` hooks, `.claude/agents/`, `.claude/skills/`, `.claude/commands/` and `.mcp.json` all load from the directory the session was launched in. A session opened at the repo root leaves nothing you write here loadable.

The starter is already in the clone, so there is nothing to scaffold: change into it and start the session there. Do the same `cd` in your control shell (`Ctrl+b c` opens one in tmux), because every relative path below starts from this folder.

```bash
cd ~/claude-code-masterclass/labs/09-agentic-devops/react-devops
claude
```

> Note: you can also skip the folder switch entirely and name the path in the prompt instead, working from a session opened anywhere in the repo:

```text
In labs/09-agentic-devops/react-devops build the app image and ship it to the box ....
```

That works for any step whose result is just files or commands. Launching inside the starter makes the lab folder the project and the repository a monorepo around it: the repo's own `/CLAUDE.md`, `/.claude/` and `/.mcp.json` stay out of the session, and every path in the prompts below is relative to the lab folder.

---

## Step 1: Confirm the box is up and reachable

**Goal:** Prove the box from Lab 01 still answers on SSH before you build anything.

The box keeps running between labs. If the lab VM was stopped and started again, bring the box up with the exact compose file Lab 01 created. Connect as `deploy`, the user Lab 01 Step 4 created: Lab 01 Step 5 set `PermitRootLogin no`, so `root@localhost` is refused on a box that finished that lab, and `deploy` is in the `docker` group and can answer every question below.

```bash
docker compose -f deploy/target-box/docker-compose.yml up -d
export DEPLOY='ssh -p 2222 -i deploy/target-box/keys/box_key -o IdentitiesOnly=yes -o UserKnownHostsFile=/dev/null -o StrictHostKeyChecking=no deploy@localhost'
$DEPLOY 'whoami; . /etc/os-release && echo $PRETTY_NAME; docker info --format "{{.Driver}}"'
```

The export lives only in the shell that ran it, and every later block in this lab calls it. Run these from `labs/09-agentic-devops/react-devops`: the `-i` path is relative, and from any other directory `ssh` finds no key and reports `Permission denied (publickey)`. Single quotes keep the remote command literal, so it reaches the box untouched.

**Expected result:** `deploy` on `Ubuntu 24.04.x LTS`, with the storage driver `vfs` from Lab 01 Step 4. If the driver reads `overlayfs` or `overlay2`, the Lab 01 `daemon.json` did not land: write `/etc/docker/daemon.json` with `{ "storage-driver": "vfs" }` and restart docker inside the box before continuing, or the first container run on the box fails with an overlay mount error.

---

## Step 2: Build the app image

**Goal:** Produce a runnable image of the app on your lab VM.

The starter ships a multi-stage `dockerfile`: a `node:22-alpine` build stage that runs `npm ci` and `npm run build`, and an `nginx:1.27-alpine` runtime stage that serves `dist/` with the SPA fallback in `conf/nginx.conf`. Nothing about it needs changing. Note the lowercase filename: Docker looks for `Dockerfile` by default, so pass `-f dockerfile` explicitly.

Lab 01 left `vite.config.ts` without a `base` line, which is what this lab wants: the app serves from the domain root. If a `base: '/react-devops/'` line has appeared, remove it before building, or expect every URL below to need the `/react-devops/` prefix.

**Commands:**

```bash
docker build -f dockerfile -t react-devops:lab2 .
```

**Expected result:** The build ends with `naming to docker.io/library/react-devops:lab2`. The tag is a local one and differs from the `v1` Lab 01 shipped, so the two stacks can sit side by side on the box without a name collision.

---

## Step 3: Ship the image to the box without a registry

**Goal:** Get the image onto the box using nothing but SSH.

There is no registry between your lab VM and the box. Stream the image over the connection with a pipe: `docker save` writes the image as a tar stream, `gzip` compresses it, and `docker load` on the far side reads it back.

**Commands:**

```bash
docker save react-devops:lab2 | gzip -1 | $DEPLOY 'docker load'
$DEPLOY 'docker images react-devops'
```

**Expected result:** `docker load` prints `Loaded image: react-devops:lab2`, and `docker images` on the box lists `react-devops lab2`. The stream is a few tens of megabytes and takes well under a minute, since the box sits on the same VM.

---

## Step 4: Run the app on the box

**Goal:** Start the app container on the box and publish it on a port nothing else uses.

Lab 01's Caddy stack holds the box's published 80 and 443, so this app publishes a dedicated host port: 8081 on the box's own interface. `--name` keeps the container findable, `--restart unless-stopped` keeps it running across reboots, and `-p 8081:80` publishes the container's nginx port on the box.

**Commands:**

```bash
$DEPLOY 'docker run -d --name react-devops-lab2 --restart unless-stopped -p 8081:80 react-devops:lab2'
$DEPLOY 'docker ps --filter name=react-devops-lab2 --format "{{.Names}}  {{.Status}}  {{.Ports}}"'
```

**Expected result:** The container reports `Up` and `0.0.0.0:8081->80/tcp` in the `PORTS` column. The app is now listening on the box, but the lab VM cannot reach port 8081 of the box yet, because the box container publishes only the ports its compose file declared (2222, 8080, 8443).

---

## Step 5: Prove the app serves, through an SSH tunnel

**Goal:** Verify the running container from your lab VM.

The box is a container on your lab VM, so its published ports are reachable from the VM only where the compose file mapped them. The SSH tunnel is the general tool here, and it is exactly how you would reach a service on a remote host that listens on a private interface. A second SSH session forwards the VM's local port 8081 to the box's 8081:

**Commands (in another shell on the VM, `Ctrl+b c` in tmux, or as a background job):**

```bash
ssh -p 2222 -i deploy/target-box/keys/box_key -o IdentitiesOnly=yes \
    -o UserKnownHostsFile=/dev/null -o StrictHostKeyChecking=no -N -L 8081:localhost:8081 deploy@localhost
```

Run it from `labs/09-agentic-devops/react-devops`, where the relative key path resolves. Then, in your control shell:

```bash
curl -s -o /dev/null -w '%{http_code}\n' http://localhost:8081/
curl -s http://localhost:8081/ | head -5
```

**Expected result:** `200` from the first curl, and the app's `index.html` from the second. The `-N` flag means no remote command runs; the session exists only to forward. The tunnel stays open while you verify, and closes with `Ctrl+C`.

On a real host the tunnel is the same command with `deploy@<public-ip>` and the two `KnownHosts` options dropped, and it is the honest way to preview a service that should not be on the public interface yet.

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

**Expected result:** Claude reports the container running with `0.0.0.0:8081->80/tcp`, and an HTTP 200 from the app through the tunnel. If the container is already running from Step 4, it should say so and leave that container in place; the `--name` collision is the tell.

---

## Step 7: Redeploy a new tag and prove it moved

**Goal:** Ship a second build and confirm the served app changed, from the container state and the served bytes.

A deploy that reports success over an unchanged site is the failure mode this module keeps returning to. Record a distinguishing byte first, so "the site changed" is something you can check.

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

```bash
$DEPLOY 'docker rm -f react-devops-lab2'
```

---

## Cleanup

Stop and remove this lab's containers:

```bash
$DEPLOY 'docker rm -f react-devops-lab2 react-devops-lab2-v2'
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

[Lab 03](lab-03-hugo-blog-ubuntu-box-vm.md) deploys a Hugo blog to the same box, which is the static-generator half of this one: the build produces static files, and the nginx container serves them directly.
