# Module 9: Agentic DevOps & Automation

This module is built around one deployment: a containerized app running on a plain Ubuntu host that you reach over SSH. The host can come from any hyperscaler (Azure, AWS, GCP, Hetzner, a VM under your desk), because nothing in the module depends on a provider API. That is the point: once the agent has SSH, a package manager and Docker, the deployment target stops being a vendor decision.

SSH is also the sharpest place to learn agentic operations. There is no `what-if` preview, no declarative reconciler, and no rollback that someone else wrote. The agent reads the state of a live host, decides, acts, and has to prove the result, which is exactly the loop the rest of the course has been building toward.

- Deployment sub-agent frontmatter and scope
- Shell allowlist scoped to deploy verbs
- Manifest as the source of truth
- The deploy-then-prove contract
- Access first, then bootstrap
- Non-root deploy user, key-only SSH
- Firewall and unattended upgrades
- Docker Engine with Compose plugin
- Caddy edge and its TLS certificate
- DNS before the first ACME attempt
- Core Web Vitals on every deploy
- The `agentic-seo` audit skill
- Fix-verify loop without manual intervention

## Topics

| Topic | Description |
|-------|-------------|
| [01: The Deployment Agent](01-devops-agent/readme.md) | The sub-agent that owns the deploy loop: frontmatter, a shell allowlist scoped to the verbs a deployment actually needs, a manifest as the single source of truth instead of model memory, and the deploy-then-prove contract that makes success verifiable rather than asserted. |
| [02: SSH Deployment](02-ssh-deployment/readme.md) | Access first, then bootstrap: a non-root deploy user, key-only SSH, firewall and unattended upgrades, Docker Engine with the Compose plugin, then the app and a Caddy edge that gets its own TLS certificate. Covers the ordering trap that no amount of retrying fixes: DNS and the reverse proxy must answer before the first ACME attempt. |
| [03: Web Vitals and SEO](03-agentic-optimization/readme.md) | Keeping the deployed site fast and discoverable: Core Web Vitals collected on every deploy, the `agentic-seo` skill for the audit, and the fix-verify loop that closes without manual intervention. |

## Demos

| Topic | Description |
|-------|-------------|
| [01: The Deployment Agent](01-devops-agent/demo-deploy-with-devops-agent.md) | Build the deployment sub-agent: scope its shell allowlist, point it at a deployment manifest, and have it report a structured result an orchestrator can validate. |
| [02: SSH Deployment](02-ssh-deployment/demo-bootstrap-and-harden.md) | Bring up a throwaway Ubuntu target, then drive the agent through access, hardening and Docker install, checking each claim against the host rather than the transcript. |
| [02: SSH Deployment](02-ssh-deployment/demo-compose-caddy-tls.md) | Ship the app: Compose file, Caddy edge, and the DNS-before-ACME ordering, ending with a certificate the agent proves is real. |
| [03: Web Vitals and SEO](03-agentic-optimization/demo-agentic-seo-optimization.md) | Audit the deployed site with the `agentic-seo` skill and a Lighthouse run, apply targeted fixes, and verify the delta. |

Every demo has a presenter guide beside it (`demo-presenter-<slug>.md`) holding the same
teaching in timed beats, for delivery without running the demo live.

## Starter and Solution Folders

Work in `box-stack/`; the finished result is beside it in `box-stack-solution/`, and the starter stays pristine.

## Labs

| Lab | Description |
|-----|-------------|
| [Deploy a Containerized React App to an Ubuntu Box over SSH](../../labs/09-agentic-devops/lab-01-deploy-to-an-ubuntu-box.md) | Bootstrap and harden a throwaway Ubuntu target, ship the image without a registry, front it with a Caddy edge that owns TLS, then hand the redeploy loop to a sub-agent and audit its evidence. |
| [Deploy a React + Vite App to the Ubuntu Box](../../labs/09-agentic-devops/lab-02-react-vite-ubuntu-box.md) | Build the `react-devops` image, ship it over SSH, run it in its own nginx container on a dedicated port, and prove it serves through an SSH tunnel. |
| [Deploy a Hugo Blog to the Ubuntu Box](../../labs/09-agentic-devops/lab-03-hugo-blog-ubuntu-box.md) | Generate two posts, build the Clarity blog inside a container so no Hugo install is needed, then ship it and redeploy to prove the new post is live. |

## Knowledge Check

### CQ-01: Scoping the Shell Allowlist

A deployment agent needs SSH access to a live host. How should its shell permissions be scoped?

- A) Allow all `Bash`, since a deployment can require any command and blocking one mid-rollout is worse than the risk.
- B) Allowlist the specific verbs a deployment actually needs, so anything outside that set requires explicit approval.
- C) Deny all `Bash` and route every command through a custom MCP server that wraps the approved operations.
- D) Allow all `Bash` but add a `CLAUDE.md` rule listing the commands the agent should restrict itself to.

**Answer: B**

A scoped allowlist is the balance the module builds: the agent runs the deploy loop without an approval prompt per command, and anything outside the deployment vocabulary stops for a human. Option A gives an agent unrestricted root-equivalent access to a live host. Option D writes the restriction somewhere that does not enforce it.

### CQ-02: The Single Source of Truth

Across sessions, what should the agent read to know which image tag, host, and ports a deployment uses?

- A) Its own memory of the previous deployment, carried forward with session resume.
- B) A manifest file in the repository that the agent reads at the start of every deploy.
- C) The live host's running container configuration, queried over SSH.
- D) The most recent successful GitHub Actions run log.

**Answer: B**

A manifest in the repo is versioned, reviewable, and identical for every session and every operator. Model memory, option A, silently drifts and cannot be diffed. Option C reads the current state rather than the intended state, so it can never detect that the host is wrong, and option D makes deployment configuration a byproduct of CI history.

### CQ-03: Deploy Then Prove

A rollout finishes and the agent reports success. What makes that report trustworthy?

- A) A zero exit code from the deployment command.
- B) A verification step in the agent's contract: fetch the live endpoint, check the response, and report the observed result.
- C) The absence of errors in the container logs during the rollout window.
- D) A screenshot of the deployment tool's output.

**Answer: B**

A successful command means the command ran, not that the service works: a container can start and immediately fail its health check, or serve the previous image. The deploy-then-prove contract is what turns "success" from an assertion into an observation. Options A and C are necessary but not sufficient.

### CQ-04: Why the Target Is Not a Vendor Decision

This module deploys to a plain Ubuntu host over SSH rather than a managed platform service. What is the pedagogical reason?

- A) SSH deployment is cheaper, so the material stays accessible to more learners.
- B) Once the agent has SSH, a package manager, and Docker, the target stops being a vendor decision, and SSH removes the safety nets that hide what agentic operations actually require.
- C) Managed platforms do not expose enough API surface for an agent to operate them.
- D) Container deployment is the only pattern that works identically across cloud providers.

**Answer: B**

Nothing in the module depends on a provider API, so the same loop runs on any host from any hyperscaler. SSH is also the sharpest teaching surface precisely because there is no dry-run preview, no declarative reconciler, and no rollback someone else wrote: the agent reads live state, acts, and has to prove the result.
