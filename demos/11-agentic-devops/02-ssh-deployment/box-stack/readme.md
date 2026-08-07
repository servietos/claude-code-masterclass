# box-stack Starter for the SSH Deployment Demos

Two things live here: the throwaway Ubuntu target that stands in for a VM, and the static app that gets deployed onto it. Everything the demos run or read is checked in; the two files you complete during them ship as stubs. The finished versions of those two files are in [../box-stack-solution/](../box-stack-solution/) as the completed reference.

| File | Contents |
|---|---|
| `target-box/Dockerfile` | Ubuntu 24.04 with `systemd`, `sshd` and `rsyslog`, and deliberately no Docker, so the agent installs it |
| `target-box/docker-compose.yml` | The stand-in VM: privileged, host cgroups, `2222` mapped to SSH and `8080`/`8443` mapped to the box's `80`/`443` |
| `target-box/keys/` | Empty. Step 1 of the bootstrap demo writes `box_key` here, and the image bakes the public half into root's `authorized_keys` |
| `app/index.html` | The whole application: one static page, no build step and no npm. The `Build 1` marker in the footer is the byte you change to prove a redeploy |
| `app/nginx.conf` | nginx listening on `8080` as a non-root user, with a `/healthz` route for the container healthcheck |
| `app/Dockerfile` | Copies the page into `nginx:1.27-alpine`, drops to the `nginx` user, declares the healthcheck against `127.0.0.1` |
| `docker-compose.yml` | Stub. The stack that ships onto the box: the `app` service is given, the Caddy edge is yours to write |
| `Caddyfile` | Stub. The edge health probe on side port `8090` is given, the site blocks are yours to write |

## Two Compose Files, Two Different Jobs

`target-box/docker-compose.yml` builds and runs the target. It only ever appears with an explicit `-f target-box/docker-compose.yml`, and it never gets copied to the box, because on a real VM the provider does its job.

The `docker-compose.yml` at this folder's root is the application stack that ships onto the box and runs there. It is named `docker-compose.yml` on purpose: a bare `docker compose` on the box only finds a file with that exact name, which is what a deploy step over SSH runs.

## Start and Destroy the Target

The image bakes the public key at build time, so the keypair has to exist before the build. Baking beats bind-mounting: `sshd` refuses a group-writable `authorized_keys`, and a bind mount from a Windows host arrives with exactly those permissions.

```bash
ssh-keygen -t ed25519 -f target-box/keys/box_key -N "" -C "box-demo"
docker compose -f target-box/docker-compose.yml up -d --build
docker compose -f target-box/docker-compose.yml ps
```

The box holds every change either demo makes, so removing it is a complete reset:

```bash
docker compose -f target-box/docker-compose.yml down -v
```

`-v` is not optional here. Two named volumes carry the nested Docker daemon's data, and leaving them behind means the next box starts with the previous demo's images and containers already on it.

## Why the Target Looks Nothing Like a Real VM Inside

The container is privileged, runs `/sbin/init` and shares the host's cgroup namespace, which is what makes `systemctl`, `ufw` and a nested Docker daemon behave the way they do on a VM. The two volumes on `/var/lib/docker` and `/var/lib/containerd` are the other half: the nested daemon cannot stack an overlay filesystem on top of the container's own overlay filesystem, and a volume gives it a real one to write to.

A real VM needs none of that. Every command the agent runs against this box is the command it would run against a hyperscaler VM, and moving to a real one means swapping `-p 2222 root@localhost` for `root@<public-ip>` and dropping the `StrictHostKeyChecking` overrides.

## What You Author

The `Caddyfile` needs its site blocks and the Compose file needs the `caddy` service, the internal network, the named volumes and the `expose` that keeps the app off the public interface.

The starter stays pristine: no generated keys, no `.env`, no certificates, no container state. `target-box/keys/`, any `*.env`, and the files the topic 01 demo writes here (`deploy-manifest.json`, `agent-compose.yml`, `.claude/`) are all git-ignored, so a run leaves nothing behind but the files you deliberately edited.

The topic 01 demo, [Build a Deployment Agent and Prove Its Deploy Loop](../../01-devops-agent/demo-deploy-with-devops-agent.md), also runs from this folder, because it needs the same throwaway target. It writes its own agent and manifest and never touches the two stubs above.
