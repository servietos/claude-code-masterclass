# Deploy a Containerized React App to an Ubuntu Box over SSH (Azure Lab VM)

Take the `react-devops` app all the way onto a Linux host you operate yourself. You will bring up a throwaway Ubuntu target, prove SSH access before building anything, bootstrap and harden the host, ship a container image without a registry, put a Caddy edge in front of it with TLS, then hand the redeploy loop to a deployment sub-agent and check its claims against the host.

This is the Azure lab VM edition of [Lab 01](lab-01-deploy-to-an-ubuntu-box-container.md). You work on an Ubuntu 24.04 VM in Azure that your instructor created for you, with Docker Engine, Node.js, Google Chrome and Claude Code already installed, so your own machine needs nothing beyond an SSH client. The target is a container running `sshd` on that VM, standing in for a second host. Every command you and the agent run against it is the same command you would run against a hyperscaler VM: moving to a real one means swapping `-p 2222 ... root@localhost` for `root@<public-ip>` and dropping the two `KnownHosts` options.

Each step contains:

- **Goal**: what you are building
- **Prompt or command**: what you run
- **Expected result**: what the outcome looks like

## Prerequisites

- **Your lab VM**: the access data your instructor handed out, with the VM's public IP, the user `azureuser` and a password. The VM runs Ubuntu 24.04, and cloud-init installed Docker Engine with the Compose plugin, Node.js 24, Google Chrome and Claude Code on its first boot. Its network security group admits SSH on port 22 only, so everything this lab publishes stays reachable from the VM alone. The instructor creates the VMs with [create-lab-vm.azcli](create-lab-vm.azcli), which installs the tools through [cloud-init.yaml](cloud-init.yaml) and writes each VM's access data to `azure-linux.md`.
- **An SSH client on your own machine**: `ssh` ships with Windows 10 and 11, macOS and Linux. Confirm with `ssh -V`.
- **Ports 2222, 8080 and 8443 free on the VM**: the box publishes SSH on 2222 and the edge's 80 and 443 on 8080 and 8443. A fresh lab VM has all three free.
- **Claude Code 2.x**: preinstalled on the VM. Step 9 writes a sub-agent definition, which needs a 2.x harness.
- **No GitHub account and no cloud subscription of your own.** Node is not needed for the build either: the app's `dockerfile` is multi-stage and runs `npm ci` and `npm run build` inside the build container.

Every command in this lab runs in Bash on the VM. You work in the starter at [react-devops/](react-devops) throughout. Everything this lab adds goes into a new `deploy/` folder and a new `.claude/agents/` folder inside it, both of which the Cleanup section removes.

---

## Connect to the lab VM

Connect from a terminal on your own machine and enter the password from your access data:

```bash
ssh azureuser@<public-ip>
```

On the first login, wait until cloud-init has finished installing the tools, then disconnect:

```bash
cloud-init status --wait
exit
```

Connect again. The second login picks up the `docker` group membership cloud-init granted to `azureuser`; in the first session every `docker` command fails with a permission error on the Docker socket. Then check the tools and clone the repository:

```bash
ssh azureuser@<public-ip>
docker compose version
claude --version
git clone https://github.com/alexander-kastil/claude-code-masterclass.git
```

Start `claude` once and sign in. The VM has no browser of its own, so open the sign-in URL Claude Code prints in your own machine's browser and paste the code back into the SSH session. Then leave with `/exit`.

A dropped connection ends every process started in it, Claude Code included. Run the rest of the lab inside `tmux` so it survives:

```bash
tmux new -s lab
```

After a reconnect, `tmux attach -t lab` brings back Claude Code and your shell variables. `Ctrl+b c` opens a new window and `Ctrl+b n` switches between them; this lab uses one window for Claude Code and a second one, your control shell, for the commands.

**Expected result:** `status: done` before the first disconnect; after reconnecting, the Compose plugin's version, a 2.x Claude Code version, and the repository cloned to `~/claude-code-masterclass`.

---

## Where to Open Claude Code

This lab builds its own harness, so open Claude Code inside the lab project. The harness is project-scoped: `CLAUDE.md`, `.claude/settings.json` hooks, `.claude/agents/`, `.claude/skills/`, `.claude/commands/` and `.mcp.json` all load from the directory the session was launched in. A session opened at the repo root leaves the `ssh-deploy-agent` you write in Step 9 inert, with no error to tell you.

The starter is already in the clone, so there is nothing to scaffold: change into it and start the session there. Do the same `cd` in your control shell, because every relative path below starts from this folder.

```bash
cd ~/claude-code-masterclass/labs/09-agentic-devops/react-devops
claude
```

> Note: you can also skip the folder switch entirely and name the path in the prompt instead, working from a session opened anywhere in the repo:

```text
In labs/09-agentic-devops/react-devops write the deployment stack under deploy/ ....
```

That works for any step whose result is just files, the `deploy/` stack in Step 7 included. It does not work for Step 9: `.claude/agents/` loads from the directory the session was launched in, so a root session writes `ssh-deploy-agent.md` into the lab folder and then never lists it in `/agents`. Launch inside the starter from Step 1 onward.

If `/agents` does not list the `ssh-deploy-agent` you write in Step 9, restart the session with `/exit` then `claude` and check again.

Launching inside the starter makes the lab folder the project and the repository a monorepo around it: the repo's own `/CLAUDE.md`, `/.claude/` and `/.mcp.json` stay out of the session. You read them from the repo root without ever writing into them, and every path in the prompts below is relative to the lab folder.

---

## Step 1: Download and run the Ubuntu image

**Goal:** Prove Docker pulls and runs the `ubuntu:24.04` image before you build anything on top of it.

A deployment target starts with a base image you have never run. Pull it and run it bare first, so that a failure here costs one command to fix: the image must download and execute a real command on the VM's Docker before it becomes the foundation of a hardened box.

**Commands:**

```bash
docker pull ubuntu:24.04
docker run --rm ubuntu:24.04 bash -c '. /etc/os-release && echo $PRETTY_NAME'
```

**Expected result:** `24.04 LTS` (with the current point release, for example `Ubuntu 24.04.4 LTS`). The container ran, printed the version line, and removed itself. On a real target host this step is replaced by the provider's image selection and a first `ssh root@<ip> 'cat /etc/os-release'`: same goal, prove the base runs before anything else.

---

## Step 2: Build the throwaway Ubuntu target

**Goal:** Turn that image into an SSH host that answers on port 2222 and can run a nested Docker daemon.

Generate the keypair first. The image bakes the public half into `root`'s `authorized_keys` at build time, which beats bind-mounting it: `sshd` refuses an `authorized_keys` file that is group-writable, and a bind mount easily arrives with exactly those permissions.

**Commands:**

```bash
mkdir -p deploy/target-box/keys
ssh-keygen -t ed25519 -f deploy/target-box/keys/box_key -N "" -C "box-lab"
```

**Prompt:**

```text
Create a throwaway Ubuntu SSH target for this lab.

1. deploy/target-box/Dockerfile
   - FROM ubuntu:24.04
   - install openssh-server, systemd, systemd-sysv, sudo, iproute2, ca-certificates,
     curl and gnupg with DEBIAN_FRONTEND=noninteractive, then clean the apt lists
   - create /run/sshd and enable the ssh service
   - COPY keys/box_key.pub to /root/.ssh/authorized_keys, 700 on /root/.ssh and
     600 on the file
   - CMD ["/sbin/init"]

2. deploy/target-box/docker-compose.yml with one service named "box"
   - build: . and container_name: box-target
   - privileged: true
   - tmpfs: /run and /run/lock
   - volumes: a named volume box-docker mounted at /var/lib/docker
   - ports: 2222:22, 8080:80 and 8443:443
   - declare the named volume box-docker

Do not add a healthcheck and do not start anything.
```

Two of those requirements are load-bearing and both are concessions to running the box as a container. `privileged: true` plus `/sbin/init` and the two tmpfs mounts are what make `systemctl` and `ufw` behave the way they do on a VM. The named volume at `/var/lib/docker` gives the nested Docker daemon a real filesystem: without it, `overlay2` on top of the box's own overlay refuses to start and Step 4 fails with a storage-driver error that looks nothing like a Docker problem.

Deliberately absent is a bind mount of the VM's `/sys/fs/cgroup`. `privileged: true` already gives the box a usable cgroup namespace, so systemd needs nothing mounted. If the compose file carries a cgroup mount anyway, remove it before the first start.

Now build and start it:

```bash
docker compose -f deploy/target-box/docker-compose.yml up -d --build
docker compose -f deploy/target-box/docker-compose.yml ps
```

**Expected result:** One container named `box-target`, service `box`, `Up`, with `0.0.0.0:2222->22/tcp`, `0.0.0.0:8080->80/tcp` and `0.0.0.0:8443->443/tcp`. A real host needs none of the privileged flags; they are the price of running a second host as a container on your lab VM.

---

## Step 3: Prove SSH access before you build anything

**Goal:** Confirm you can actually get in, before an image, a Compose file or a certificate exists.

The biggest time sink in any deployment is wiring images and config against a host nobody has logged into yet. `-o IdentitiesOnly=yes` is mandatory: without it `ssh` offers every default key in your agent first, the server cuts you off after `MaxAuthTries`, and a perfectly correct key reports `Permission denied`.

**Commands**, in your control shell:

```bash
export BOX='ssh -p 2222 -i deploy/target-box/keys/box_key -o IdentitiesOnly=yes -o UserKnownHostsFile=/dev/null -o StrictHostKeyChecking=no'
$BOX root@localhost 'whoami; . /etc/os-release && echo $PRETTY_NAME'
ssh-keygen -l -f deploy/target-box/keys/box_key.pub
```

Single quotes keep the remote command literal, so pipes and `$PRETTY_NAME` reach the box's own shell untouched.

**Expected result:** `root` on `Ubuntu 24.04.x LTS`, and a fingerprint line for your public key. Keep this shell: it is your control shell for the rest of the lab, and the shell variable only exists in it. If you lose it, reattach with `tmux attach -t lab` or reconnect, `cd` back into `react-devops` and run the `export` again.

The two `KnownHosts` options are here only because this box gets a new host key on every rebuild. Never carry them to a real host, where an unexpected host key is a warning you want.

Now hand the connection details to Claude:

**Prompt:**

```text
Our deployment target for this lab is an Ubuntu 24.04 host reachable as:

  ssh -p 2222 -i deploy/target-box/keys/box_key -o IdentitiesOnly=yes \
      -o UserKnownHostsFile=/dev/null -o StrictHostKeyChecking=no root@localhost

Confirm you can reach it and report exactly three things: the OS release, whether
Docker is installed, and the contents of /root/.ssh/authorized_keys reduced to key
fingerprints. Do not print the key material.

Do not change anything on the host yet.
```

**Expected result:** Claude reports Ubuntu 24.04, no Docker, and one `ed25519` fingerprint that matches the `ssh-keygen -l` output above. Match keys by fingerprint: a key file's name routinely names a different registered key, and a box created before a key existed never received it, which is the other half of the same failure.

---

## Step 4: Bootstrap the box

**Goal:** A non-root deploy user, automatic security patching, Docker Engine with the Compose plugin, and a stack directory the deploy user owns.

Everything in this step happens while root SSH still works, so a mistake here costs one command to fix. Docker in particular goes in before hardening, while you are still root-capable.

**Prompt:**

```text
Bootstrap the box. Run apt non-interactively (DEBIAN_FRONTEND=noninteractive).

1. Create user "deploy" with --disabled-password and no sudo. Copy
   /root/.ssh/authorized_keys to /home/deploy/.ssh/authorized_keys, owned
   deploy:deploy, 700 on the directory and 600 on the file.
2. apt-get update and upgrade, then install ufw, fail2ban, unattended-upgrades,
   ca-certificates, curl and gnupg. Enable unattended-upgrades non-interactively
   and enable and start fail2ban.
3. Install Docker Engine from the official Docker apt repository: the GPG key in
   /etc/apt/keyrings, the repository for this Ubuntu codename, then docker-ce,
   docker-ce-cli, containerd.io, docker-buildx-plugin and docker-compose-plugin.
   Enable and start docker. Do not use the get.docker.com script and do not
   install the standalone docker-compose binary.
4. Before anything runs on it, write /etc/docker/daemon.json containing
   { "storage-driver": "vfs" } and restart docker. Without this, the nested
   daemon fails its very first container run with an overlay mount error:
   "mount source: overlay ... err: invalid argument".
5. Add deploy to the docker group.
6. Create /opt/react-devops and chown it to deploy:deploy.

Do not touch the SSH configuration or the firewall yet. Report the engine and
compose plugin versions, the effective storage driver from docker info, and the
exact commands you ran.
```

The upgrade and the Docker install together take a few minutes on a fresh image. **Long installs over SSH must survive the session.** On a real host run them detached (`nohup ... >log 2>&1 &`) and poll the log, because a killed SSH session sends `SIGHUP` to a foreground remote command and can wedge a package manager mid-configure. Here the box sits on your lab VM and is disposable, so the foreground run is acceptable.

`vfs` is a concession to the nested setup, like the privileged flags. The box's root filesystem is already an overlay on the lab VM and overlay-on-overlay is not supported, so the nested daemon must fall back to `vfs`, which copies every layer in full and costs disk and speed, but works. A real host's Docker daemon keeps its default `overlay2`; never carry the `daemon.json` to one.

Check the claims against the host, the only evidence that counts:

```bash
$BOX root@localhost 'id deploy; stat -c "%a %U:%G %n" /home/deploy/.ssh/authorized_keys; docker compose version; docker info --format "{{.Driver}}"; systemctl is-enabled docker; id -nG deploy; ls -ld /opt/react-devops; cat /etc/apt/apt.conf.d/20auto-upgrades'
```

**Expected result:** `deploy` exists with `600 deploy:deploy` on its `authorized_keys`, `docker compose` answers with the plugin's version, the storage driver is `vfs`, the service is `enabled` so it survives a reboot, `deploy` is in the `docker` group, `/opt/react-devops` is owned by `deploy`, and both `APT::Periodic` keys are `"1"`. Version numbers will differ from anyone else's; the shape of the eight answers will not.

Group membership is granted at process start, which is why `deploy` joins `docker` before anything runs as that user.

---

## Step 5: Close the door, then close the ports

**Goal:** Key-only SSH with root login disabled, and exactly three inbound ports, without locking yourself out.

This is the step that locks people out of their own boxes. The moment `PermitRootLogin no` takes effect, a wrong key stops being an inconvenience and becomes a rebuild, so the proof comes first and it comes from a session you keep open.

**Command**, in a **third shell on the VM that you leave open** for the rest of this step (`Ctrl+b c` in tmux, or a second SSH session from your machine):

```bash
cd ~/claude-code-masterclass/labs/09-agentic-devops/react-devops
ssh -p 2222 -i deploy/target-box/keys/box_key -o IdentitiesOnly=yes \
    -o UserKnownHostsFile=/dev/null -o StrictHostKeyChecking=no deploy@localhost
```

Run `id` and `docker ps` in it to confirm the user and its Docker access, then leave it sitting there. An already-open session survives an `sshd` restart, so it is your way back in if the next prompt gets the config wrong.

**Prompt:**

```text
Harden the box. I have an open deploy session as a fallback.

1. In /etc/ssh/sshd_config set PermitRootLogin no, PasswordAuthentication no and
   PubkeyAuthentication yes. Check /etc/ssh/sshd_config.d/ for any file that
   overrides those and fix it there too. Validate with sshd -t before restarting,
   then restart ssh and report the effective values from sshd -T.
2. Configure ufw: default deny incoming, default allow outgoing, allow 22/tcp,
   80/tcp and 443/tcp, then enable it without an interactive prompt. Nothing else
   gets an inbound rule. Report the full ufw status.
```

Root SSH is closed now and `deploy` has no `sudo`, so both checks run out of band through the container, which is the nested equivalent of a provider's serial console. Run them in your control shell:

```bash
docker compose -f deploy/target-box/docker-compose.yml exec -T box \
  /usr/sbin/sshd -T | grep -E '^(permitrootlogin|passwordauthentication|pubkeyauthentication) '
docker compose -f deploy/target-box/docker-compose.yml exec -T box ufw status verbose
$BOX root@localhost 'whoami'
```

**Expected result:** `permitrootlogin no`, `passwordauthentication no`, `pubkeyauthentication yes`; `ufw` active with `deny (incoming)` and exactly `22/tcp`, `80/tcp` and `443/tcp` allowed; and the last command refused, while your fallback shell keeps working.

`sshd -T` is the check that matters, because it prints the configuration the daemon actually runs. Ubuntu's config starts with `Include /etc/ssh/sshd_config.d/*.conf` and `sshd` keeps the first value it obtains. A dropped-in file carrying `PasswordAuthentication yes` therefore beats your edit further down, while the file you edited reads exactly as intended.

Ports 80 and 443 open before anything listens on them, because the edge in Step 7 needs port 80 reachable for its first certificate challenge and a firewall rule added after that challenge fails does not un-fail it. Worth knowing for the real thing: **`ufw` does not filter Docker's published ports.** Docker writes its own DNAT rules ahead of the `INPUT` chain `ufw` manages, so a container published with `ports:` is reachable even when `ufw` denies that port. The rule that actually keeps an app private is `expose:` with no `ports:` entry, which is what Step 7 uses.

---

## Step 6: Build the image and ship it without a registry

**Goal:** Get a runnable app image onto the box using nothing but SSH.

The starter already ships a multi-stage `dockerfile`: a `node:22-alpine` build stage that runs `npm ci` and `npm run build`, and an `nginx:1.27-alpine` runtime stage that serves `dist/` with the SPA fallback in `conf/nginx.conf`. Nothing about it needs changing. Note the lowercase filename: Docker looks for `Dockerfile` by default, so pass `-f dockerfile` explicitly.

If `vite.config.ts` carries a `base: '/react-devops/'` line, the app serves under a sub-path here too. Remove the `base` line for this lab, or expect every URL below to need the `/react-devops/` prefix.

**Commands:**

```bash
docker build -f dockerfile -t react-devops:v1 .
export DEPLOY='ssh -p 2222 -i deploy/target-box/keys/box_key -o IdentitiesOnly=yes -o UserKnownHostsFile=/dev/null -o StrictHostKeyChecking=no deploy@localhost'
docker save react-devops:v1 | gzip -1 | $DEPLOY 'docker load'
$DEPLOY 'docker images react-devops'
```

**Expected result:** The local build ends with `naming to docker.io/library/react-devops:v1`, `docker load` prints `Loaded image: react-devops:v1`, and `docker images` on the box lists `react-devops v1`. The stream is a few tens of megabytes and takes well under a minute, since the box sits on the same VM.

**The tag you shipped and the tag your Compose file names must be identical.** This is the single most common deployment failure in the whole module: name the image `react-devops:v1` here and `react-devops:latest` in Step 7, and Compose treats it as an image it does not have, tries to pull `react-devops:latest` from Docker Hub, and fails on a public repository that does not exist. In a registry-based pipeline the same mismatch is worse, because `docker compose pull` on an unchanged tag exits 0, `up -d` sees no change, and the deploy reports success over an unchanged site.

Streaming an image over SSH is a bootstrap move, appropriate exactly once: before a registry exists. The steady state is CI building and pushing an image and the box only pulling it, which is what Step 9's manifest describes.

---

## Step 7: Put a Caddy edge in front of the app

**Goal:** A two-service Compose stack where the app is reachable only through a reverse proxy that owns TLS.

**Prompt:**

```text
Write the deployment stack for the box under deploy/.

1. deploy/docker-compose.yml with two services on one bridge network named "edge":
   - web: image react-devops:v1, container_name react-devops-web,
     restart unless-stopped, expose ["80"] and NOT ports, healthcheck
     ["CMD", "wget", "-qO-", "http://127.0.0.1:80/"] with interval 30s,
     timeout 5s, retries 3
   - caddy: image caddy:2-alpine, restart unless-stopped, ports 80:80 and 443:443,
     volumes ./Caddyfile:/etc/caddy/Caddyfile:ro plus named volumes caddy_data
     at /data and caddy_config at /config, healthcheck
     ["CMD-SHELL", "wget -qO- http://127.0.0.1:8090/healthz || exit 1"]
   - declare the edge network and both named volumes
   - do not add depends_on to either service

2. deploy/Caddyfile with two blocks:
   - :8090 with a handle for /healthz responding "ok" 200
   - app.box.test with "tls internal", a handle for /healthz responding "ok" 200,
     and a catch-all handle that reverse_proxy to web:80

Hardcode app.box.test. Do not introduce any environment variable.
```

Five of those constraints are the lesson:

- **`expose` on `web`, with no `ports`.** `expose` publishes nothing to the host, so the app is reachable only from inside the `edge` network. Caddy becomes the single public listener on the box, which is the whole point of an edge.
- **The healthcheck probes `127.0.0.1`.** Busybox `wget` tries `::1` first for `localhost` while nginx binds IPv4 only, so a `localhost` probe produces a permanently unhealthy container that is in fact serving fine.
- **`caddy_data` is a named volume.** It holds the ACME account key and the issued certificates. Losing it means re-issuing everything, and on a real host that spends real rate limit.
- **The health probe sits on port 8090 and inside the host block.** A bare `:80 { respond /healthz 200 }` takes port 80 away from Caddy for every hostname on the box, killing every HTTP-to-HTTPS redirect and every ACME challenge on it.
- **No environment variable in the Caddyfile.** An empty Compose variable expands to an empty directive, Caddy rejects the whole config, and the edge crash-loops. Compose's `${VAR:-}` sets the variable to an empty string, which counts as set, so Caddy's own `{$VAR:default}` fallback never fires.

Copy the two files to the box and bring the stack up. Note that `scp` spells the port `-P` while `ssh` spells it `-p`:

```bash
scp -P 2222 -i deploy/target-box/keys/box_key -o IdentitiesOnly=yes \
    -o UserKnownHostsFile=/dev/null -o StrictHostKeyChecking=no \
    deploy/docker-compose.yml deploy/Caddyfile deploy@localhost:/opt/react-devops/
$DEPLOY 'cd /opt/react-devops && docker compose config -q && docker compose up -d'
$DEPLOY 'cd /opt/react-devops && docker compose ps'
```

Two unrelated failures both say "permission denied" here, and the prefix on the line tells you which. `deploy@localhost: Permission denied (publickey)` is authentication, and since Step 6 just authenticated with the same key and the same options, the cause lies in the shell: the `-i` path is relative, so any shell not sitting in `labs/09-agentic-devops/react-devops` finds no key file. `scp: /opt/react-devops/docker-compose.yml: Permission denied` is the far-side filesystem after a successful login, and it means Step 4's item 6 did not land, leaving the directory owned by `root`. Check the owner:

```bash
$DEPLOY 'ls -ld /opt/react-devops'
```

If it reads `root root`, repair it through the container, because root SSH is closed by now:

```bash
docker compose -f deploy/target-box/docker-compose.yml exec -T box chown deploy:deploy /opt/react-devops
```

Then re-run the `scp`. Step 4's verification block was there to catch exactly this, so a failure here usually means nobody read that block's output.

Smoke test from inside the network before you touch a browser or a certificate, which needs no open port at all:

```bash
$DEPLOY 'cd /opt/react-devops && docker compose exec -T caddy wget -qO- http://web:80/ | head -5'
```

**Expected result:** Both services `running`, `web` with no host port in the `PORTS` column and `caddy` holding `80` and `443`, and the smoke test printing the app's `index.html`. Caddy resolved `web` by its service name over the `edge` network.

**Never `mv` a new file onto a bind-mounted config file:** a file mount binds the inode, so `cat > Caddyfile.new && mv Caddyfile.new Caddyfile` swaps the inode behind the name and the container keeps serving the old file forever, while `caddy validate` cheerfully reports a valid configuration. Always write to the exact path, which is what the `scp` above does.

---

## Step 8: Prove the hostname on the edge, without DNS

**Goal:** Verify TLS and host-based routing on a hostname that resolves nowhere, and understand exactly what changes on a real host.

`curl --resolve` supplies the address the hostname would resolve to, so every hostname on an edge can be proven live before any DNS record exists. `tls internal` made Caddy issue the certificate from its own local CA, so pull that CA root off the box and verify the chain properly; `-k` would skip exactly that check.

**Commands:**

```bash
$DEPLOY 'docker exec $(docker ps -qf name=caddy) cat /data/caddy/pki/authorities/local/root.crt' > deploy/box-local-ca.crt
curl -s --cacert deploy/box-local-ca.crt --resolve 'app.box.test:8443:127.0.0.1' \
     -o /dev/null -w '%{http_code}\n' https://app.box.test:8443/
curl -s --cacert deploy/box-local-ca.crt --resolve 'app.box.test:8443:127.0.0.1' \
     https://app.box.test:8443/healthz
echo | openssl s_client -connect 127.0.0.1:8443 -servername app.box.test 2>/dev/null \
  | openssl x509 -noout -issuer -dates -ext subjectAltName
curl -s -o /dev/null -w '%{http_code}\n' http://127.0.0.1:8080/
$DEPLOY 'docker ps --format "{{.Names}}  {{.Ports}}"'
```

**Expected result:** `200` for the app, `ok` from `/healthz`, an issuer containing `Caddy Local Authority` over a `DNS:app.box.test` subject alternative name, a `308` to `https://127.0.0.1/` for the plain-HTTP request that arrived with no matching hostname, and a `docker ps` listing where only the Caddy container has a host port.

That redirect is Caddy's automatic HTTPS upgrade answering before any routing happens, which is the proof that nothing arriving on port 80 reaches the app: routing goes by `Host` header. The empty `PORTS` column on `react-devops-web` is the proof that `expose` did its job.

Read the certificate by its subject alternative name. Caddy issues leaf certificates with an empty subject DN and carries the hostname only in the SAN extension, so `openssl x509 -subject` prints a bare `subject=` on a certificate that is entirely correct.

**On a real host, one line changes.** Delete `tls internal`, point an A record for the hostname at the box, and the same site block makes Caddy request a publicly trusted Let's Encrypt certificate over the HTTP-01 challenge and renew it automatically, at which point the issuer line above reads `C=US, O=Let's Encrypt`.

That is also the one ordering rule that no amount of retrying fixes: **never add a hostname's site block until that hostname already resolves to the box.** Let's Encrypt caps failed validations at five per account per hostname per hour, and Caddy then backs off exponentially, so the backoff timer keeps running long after you correct the record. You fix DNS and the hostname still does not serve. Ship and fully verify the stack over the raw address first, exactly as you just did, and add each site block only after that record resolves.

---

## Step 9: Hand the redeploy loop to a deployment agent

**Goal:** A sub-agent scoped to deployment verbs that sources every value from a committed manifest.

You have now run the loop by hand, so you know what every check should say, which is the right moment to delegate it. The agent gets its own context window and a manifest as its only source of facts. Its narrow shell allowlist lives in `.claude/settings.json` beside it, because sub-agent frontmatter has no `permissions` field.

**Prompt:**

```text
Create three files.

1. deploy/manifest.json, the single source of truth for this deployment:
   { "host": "localhost", "sshPort": 2222, "user": "deploy",
     "keyFile": "deploy/target-box/keys/box_key",
     "stackPath": "/opt/react-devops",
     "appHost": "app.box.test",
     "services": {
       "web":   { "image": "react-devops:v1", "internalPort": 80 },
       "caddy": { "image": "caddy:2-alpine", "publishedPorts": [80, 443] } },
     "verifyUrls": ["https://app.box.test:8443/", "https://app.box.test:8443/healthz"],
     "caCert": "deploy/box-local-ca.crt" }

2. .claude/agents/ssh-deploy-agent.md with YAML frontmatter:
   - name: ssh-deploy-agent
   - description: deployment specialist for this app on an Ubuntu host reached over
     SSH, applied for "deploy to the box", "ship the new tag", "the site is down
     after a deploy"
   - model: sonnet
   - tools: [Read, Write, Edit, Bash, Glob, Grep]
   - no permissions key: sub-agent frontmatter has no such field

   Body rules:
   - Read deploy/manifest.json before every operation and source every host, port,
     user, path and image tag from it. If a value is not in the manifest, ask for
     it and write it there. Never infer one.
   - Prove SSH access before changing anything.
   - Report success only with two independent proofs: an HTTP status for every
     entry in verifyUrls, and container state from the host showing the running
     image matches the manifest tag.
   - Stop and ask when a host port or container name is already taken, when a
     container was already unhealthy before the deploy, or when cleanup would
     remove a volume or a credential file.
   - Return a single JSON object with no prose and no Markdown fences, with keys:
     status (success|failure|partial), target, imageTags, verifiedUrls
     (url + httpStatus), containerState (service + state + health), summary, errors.

3. .claude/settings.json with the shell allowlist for this project:
   - permissions.allow: Bash(ssh:*), Bash(scp:*), Bash(docker:*), Bash(ls:*)
   - permissions.deny: Bash(rm:*), Bash(npm:*), Bash(node:*)
```

**Expected result:** `deploy/manifest.json`, `.claude/agents/ssh-deploy-agent.md` and `.claude/settings.json` exist, the agent's frontmatter carries no `permissions` key, and `/agents` lists `ssh-deploy-agent`. The allowlist applies to every session in this project, the agent's included.

The deny list is doing real work: `npm` and `node` are denied so the agent cannot drift into building an image locally that nobody else can reproduce, and `rm` is denied because the most expensive mistake on a shared host is a confident cleanup of somebody else's volume. Note what the allowlist cannot do: `Bash(ssh:*)` still runs any command on the far side of the connection, so the guardrail that actually holds on the host is the `deploy` user's own privileges.

---

## Step 10: Redeploy through the agent and prove the new build is live

**Goal:** Ship a second tag and confirm from container state that it is the one being served.

Record the container count first, because "nothing else on the box moved" is the check that matters most on a shared host:

```bash
$DEPLOY 'docker ps -q | wc -l'
curl -s --cacert deploy/box-local-ca.crt \
     --resolve 'app.box.test:8443:127.0.0.1' https://app.box.test:8443/version.txt | head -1
```

That second command returns the first line of the app's `index.html`, and it returns it with status `200`. Nothing serves `/version.txt` yet, but `conf/nginx.conf` carries the SPA fallback `try_files $uri $uri/ /index.html`, so every unknown path answers `200` with the app shell. **Record the body as your before state on a site with a SPA fallback:** a status check here would read `200` before the deploy and `200` after it, and prove nothing either way. Now create the file, build the new tag, and delegate the rollout:

**Prompt:**

```text
Create public/version.txt containing exactly the text v2, then update
deploy/manifest.json so services.web.image is react-devops:v2.

Then use the ssh-deploy-agent subagent to deploy this app to the box. It should:
- build the image locally as react-devops:v2 using the lowercase dockerfile
- stream it to the box with docker save piped into docker load over ssh
- update the image tag in /opt/react-devops/docker-compose.yml on the box to match
  the manifest, writing to that exact path
- run docker compose up -d web (docker compose restart keeps the old image)
- verify every URL in the manifest using the CA certificate the manifest names
- return the JSON contract from its definition and nothing else
```

The project's shell allowlist denies `npm` and allows `docker`, so the build runs through Docker as intended. **A config change needs a recreate:** `env_file` and `image:` bind at container create time, so `docker compose restart` keeps the old image forever and only `up -d` recreates the container.

Now audit the agent's answer against the host yourself:

```bash
$DEPLOY 'docker inspect react-devops-web --format "{{.Config.Image}} {{.Image}}"'
$DEPLOY 'docker image inspect react-devops:v2 --format "{{.Created}}"'
curl -s --cacert deploy/box-local-ca.crt --resolve 'app.box.test:8443:127.0.0.1' \
     https://app.box.test:8443/version.txt
$DEPLOY 'docker ps -q | wc -l; docker ps --filter health=unhealthy --format "{{.Names}}"'
```

**Expected result:** The JSON object arrives with `status: "success"`, an `imageTags` entry of `react-devops:v2`, an `httpStatus` of 200 for both `verifyUrls`, and `containerState` showing both services running. Independently, `Config.Image` reads `react-devops:v2`, the image `Created` timestamp is from the last few minutes, `/version.txt` now returns `v2` where it returned the app shell before, the container count is unchanged, and no container is listed unhealthy.

Reject a `success` that arrives with an empty `verifiedUrls` array. A green run only proves the SSH commands exited 0, and they also exit 0 when the rollout was a no-op: had the manifest said `v2` while the shipped tag was still `v1`, Compose would have found no change to make and the agent would have had nothing to report but success.

---

## Cleanup

Run this last. [Lab 02](lab-02-react-vite-ubuntu-box-vm.md) and [Lab 03](lab-03-hugo-blog-ubuntu-box-vm.md) deploy to this same box, so tearing it down ends them too.

Bring the stack down on the box, then remove the box itself along with the named volume holding its nested Docker data:

```bash
$DEPLOY 'cd /opt/react-devops && docker compose down'
docker compose -f deploy/target-box/docker-compose.yml down -v
docker image rm react-devops:v1 react-devops:v2
```

`-v` is the part that matters. Without it the `box-docker` volume survives, carrying every image the nested daemon loaded, and a `vfs` daemon stores images uncompressed and unlayered, so that runs to gigabytes.

Everything this lab wrote locally sits in three paths inside the starter. Removing them returns `git status` to clean:

```bash
rm -rf deploy .claude
rm -f public/version.txt
git status --short
```

**Expected result:** `docker ps` lists no `box-target` and no `react-devops-*` container, and `git status --short` prints nothing. The private key went with `deploy/`, which is the point: it authorised root on a host and has no reason to outlive it.

## What You Just Practised

| Mechanic                                                   | Step  | Use it for                                                       |
| ---------------------------------------------------------- | ----- | ---------------------------------------------------------------- |
| Pull and run the base image before building on it          | 1     | Proving the foundation exists before it becomes a host           |
| Access-first ordering with `-o IdentitiesOnly=yes`         | 3     | Every first contact with a host, before any build or config work |
| Matching keys by fingerprint                               | 3     | Diagnosing a "correct" key that is refused                       |
| Non-root deploy user, `unattended-upgrades`, `fail2ban`    | 4     | The standing security posture of any long-lived host             |
| `vfs` storage driver for a nested daemon                   | 4     | Docker-in-Docker inside a container                              |
| Second open session before disabling root and password SSH | 5     | Any hardening change that could lock you out                     |
| `sshd -T` to read the effective config                     | 5     | Reading the config the daemon actually runs                      |
| `docker save` piped into `docker load` over SSH            | 6     | First bring-up, before a registry exists                         |
| Shipped tag equals the Compose `image:` ref                | 6, 10 | Preventing the silent no-op deploy                               |
| `expose` with no `ports`, behind a single edge             | 7     | Keeping app containers off the public interface                  |
| `curl --resolve` plus `--cacert`                           | 8     | Proving a hostname and its TLS chain before DNS exists           |
| Site block only after the record resolves                  | 8     | Not burning the certificate authority's failed-validation budget |
| Manifest as the agent's only source of facts               | 9     | Making a deploy reproducible by a person as well as an agent     |
| Two independent proofs and a JSON contract                 | 10    | Rejecting an asserted success                                    |

[Lab 02](lab-02-react-vite-ubuntu-box-vm.md) deploys this same app to the same box over a simpler pipeline: no edge, no certificate, no sub-agent, just the image shipped, run, and verified through a tunnel. [Lab 03](lab-03-hugo-blog-ubuntu-box-vm.md) does the same for a static Hugo site whose toolchain lives entirely inside the build.
