# Labs - Module 11: Agentic DevOps

| Lab | Topic          | Title                                                                                           | Track    | Level        | Time   | Description                                                                                                                                                                                                                                             |
| --- | -------------- | ----------------------------------------------------------------------------------------------- | -------- | ------------ | ------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 01  | SSH Deployment | [Deploy a Containerized React App to an Ubuntu Box over SSH](lab-01-deploy-to-an-ubuntu-box.md) | Core     | Advanced     | 1h 30m | Bring up a throwaway Ubuntu target, bootstrap and harden it, ship the `react-devops` image without a registry, front it with a Caddy edge that owns TLS, then hand the redeploy loop to a deployment sub-agent and audit its evidence against the host. |
| 02  | Container Apps | [Deploy a React + Vite App to the Ubuntu Box](lab-02-react-vite-ubuntu-box.md)                  | Optional | Intermediate | 45m    | Build the `react-devops` image, ship it over SSH to the Lab 01 box, run it in its own nginx container on a dedicated port, and prove it serves through an SSH tunnel.                                                                                   |
| 03  | Static Sites   | [Deploy a Hugo Blog to the Ubuntu Box](lab-03-hugo-blog-ubuntu-box.md)                          | Optional | Intermediate | 1h 15m | Generate two blog posts with Claude Code, build the Clarity blog inside a container so no Hugo install is needed, then ship and serve it on the same box, ending with a redeploy that proves the new post is live.                                      |

**Core** is the one lab that teaches this module's central capability; run it if you run nothing else. **Optional** labs go deeper or cover a second build pipeline. **Level** rates the lab itself: Beginner needs no prior Claude Code experience, Intermediate assumes you have configured a harness before, Advanced assumes you are comfortable with hooks, subagents, or headless scripting.

Core path: 1h 30m. All labs: 3h 30m.

Every lab needs a working Docker installation, which is why no figure includes a Docker install.

Lab 01 is Core because it is the module itself: a containerized app on a plain Ubuntu host reached over SSH, which is the deployment every demo in this module builds toward. It is rated Advanced because it hardens a live host, writes a scoped sub-agent, and requires you to distinguish an agent's claim from the host's answer. Labs 02 and 03 are the same host reached through a simpler pipeline: the edge and the certificate are dropped so each lab isolates one delivery path, Lab 02 the containerized app build, Lab 03 a static site whose entire toolchain lives inside the build.

Every path here stays account-light. Every lab needs only Docker on your own machine, because the deployment target is a throwaway Ubuntu container running `sshd` that stands in for a VM. No lab in this module needs a cloud subscription, a credit card, or a provider console.

## Prerequisites

- Every lab needs **Docker Desktop or Docker Engine** running, with `docker compose` v2 available, plus a **bash shell** (git-bash or WSL on Windows) for its `ssh` and pipe syntax. It needs no GitHub account and no local Node or Hugo install, because every build runs inside a container. On Windows, [Install WSL and Docker Desktop](install-docker-desktop.md) covers both in one pass.
- Lab 01 needs **Claude Code 2.x**, because Step 9 writes a sub-agent definition.
- Labs 02 and 03 build on Lab 01: they need its box running with the `deploy` user, Docker, and the `vfs` storage driver in place.

## Starters and Solutions

| Lab | You build                                                                                                                                                          | Completed reference                                                                                                                                                                                                                                               |
| --- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------ | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 01  | The target box, the Compose and Caddy stack, the manifest and the deploy agent, all inside `react-devops/` under a `deploy/` folder the lab's Cleanup step removes | None checked in. The nearest finished example of the same Compose and Caddy pattern is the module demo [Ship the App with Compose, Caddy and TLS](../../demos/11-agentic-devops/02-ssh-deployment/demo-compose-caddy-tls.md) and its `box-stack-solution/` folder |
| 02  | The image tag and the container commands in `react-devops/`                                                                                                        | `react-devops-solution/`                                                                                                                                                                                                                                          |
| 03  | The `baseURL`, both blog posts and the containerized `dockerfile` in the Hugo starter at `my-blog/`                                                                | `my-blog-solution/`                                                                                                                                                                                                                                               |

Lab 01 and Lab 02 share the same starter at `react-devops/`. Work there and keep it pristine: no `node_modules`, no build output, no test reports committed back. Build your own result from the guide first and treat a solution folder as a check, not a starting point.

`publish-blog/` is a design reference only. It is a real deployed Hugo site kept here so you can read its configuration and build. Never use it as a working directory for any lab.

The starter's `.gitignore` already covers `playwright-report/`, `test-results/`, `blob-report/` and `playwright/.cache/`, so running the end-to-end suite leaves `git status` clean. `package-lock.json` is committed on purpose: the Dockerfile's `npm ci` needs it. No lab in this module requires the end-to-end suite.
