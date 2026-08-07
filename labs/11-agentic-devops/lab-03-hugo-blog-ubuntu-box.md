# Deploy a Hugo Blog to the Ubuntu Box

Build and deploy a static blog using Hugo, Claude Code, and Docker. You will open a Hugo starter that already ships the Clarity theme, let Claude generate two realistic blog posts, then containerize the build and ship the blog to the same Ubuntu box from Lab 01. Where Lab 02 shipped a React app as an image, this lab ships a blog that is built inside a container, so the toolchain never has to exist on your machine.

Hugo is a static site generator written in Go. It turns Markdown files into a complete website in milliseconds without a database or server runtime. Content lives in plain text files versioned with Git, themes are swapped by changing a single config value, and the built output is a folder of static HTML that any web server can serve.

This lab is optional. The module's core lab, [Deploy a Containerized React App to an Ubuntu Box over SSH](lab-01-deploy-to-an-ubuntu-box.md), ships a containerized app to a host you own and operate over SSH. Lab 02 ships a React app the same way. This lab is the static-generator half: the build produces files instead of an app bundle, and the same `docker save` pipe carries them to the same box.

Each step contains:

- **Goal**: what you are building
- **Prompt or command**: what you run
- **Expected result**: what the outcome looks like

## Prerequisites

- **Lab 01 completed through Step 4.** The box from [lab-01-deploy-to-an-ubuntu-box.md](lab-01-deploy-to-an-ubuntu-box.md) must be running with `deploy` created and Docker installed with the `vfs` storage driver.
- **Docker**: Docker Desktop or Docker Engine, running before you start. The blog builds inside a container and runs on the box.
- **A shell**: Bash (git-bash or WSL on Windows, any shell on macOS and Linux) or PowerShell 7. Every command block that is not byte-identical across the two ships a `powershell` twin below the `bash` one. Three substitutions recur and each fails silently rather than loudly: `UserKnownHostsFile=NUL` instead of `/dev/null`, `curl.exe` instead of `curl`, and a staged tar file instead of `docker save | ssh`, because PowerShell's pipeline carries .NET objects and corrupts a binary stream.
- **No Hugo install and no GitHub account.** The multi-stage `dockerfile` downloads Hugo Extended inside its build stage, and the box receives the finished image over SSH.

You work in the starter at [my-blog/](my-blog/) throughout. It is a bare Hugo site with the Clarity theme vendored under `themes/clarity`, so there is nothing to scaffold and nothing to download. The finished reference, including both posts and the containerized build, lives at [my-blog-solution/](my-blog-solution/). Open it only if you get stuck.

The sample blog in [publish-blog/](publish-blog/) is a **design reference only**. Read it to see how a real Clarity site is configured, but never `cd` into it and never build inside it. It is somebody else's deployed site, wired to its own domain.

---

## Where to Open Claude Code

This lab builds its own harness, so open Claude Code inside the lab project rather than at the repo root. The harness is project-scoped: `CLAUDE.md`, `.claude/settings.json` hooks, `.claude/agents/`, `.claude/skills/`, `.claude/commands/` and `.mcp.json` all load from the directory the session was launched in. A session opened at the repo root leaves everything you write here inert, with no error to tell you.

The starter is already in this repo, so there is nothing to scaffold: change into it and start the session there. Run this from the repo root; both commands work unchanged in PowerShell.

**Bash:**
```bash
cd labs/11-agentic-devops/my-blog
claude
```

If you start Claude Code with the Claude Terminal extension (`Ctrl+F1` / `Cmd+F1`), it opens in the VS Code workspace folder and reuses an already-open terminal, so it will not follow the `cd` above. Open `my-blog` as the workspace folder (**File > Open Folder**) before pressing the shortcut, or run the commands above in a plain terminal.

> Note: you can also skip the folder switch entirely and name the path in the prompt instead, working from a session opened anywhere in the repo:

```text
In labs/11-agentic-devops/my-blog create a blog post at content/posts/getting-started-with-ai.md ....
```

That works for any step whose result is just files, both blog posts included. It does not work for the `/init` in Step 3: `CLAUDE.md` is written into the directory the session was launched in, so a root session rewrites the repository's own `CLAUDE.md` instead of the blog's. Launch inside `my-blog` from Step 3 onward.

Launching inside `my-blog` is what makes the repository a monorepo to this lab rather than the project: the repo's own `/CLAUDE.md`, `/.claude/` and `/.mcp.json` stay out of the session. You read them from the repo root without ever writing into them, and every path in the prompts below is relative to the lab folder.

Steps 1 and 2 need no session at all, so check the box and look at the theme first, then come back and open Claude Code here.

---

## Step 1: Confirm the box is up

**Goal:** Prove the box from Lab 01 still answers on SSH.

The box keeps running between labs; if you restarted Docker or rebooted, bring it up again with the exact compose file Lab 01 created. Connect as `deploy`, the user Lab 01 Step 4 created: if you also ran Lab 01 Step 5, that step set `PermitRootLogin no`, so `root@localhost` answers `Permission denied (publickey)` on a box that finished the core lab. The commands below assume you are inside `my-blog/`, so the box's files are one folder up:

**Bash:**
```bash
docker compose -f ../react-devops/deploy/target-box/docker-compose.yml up -d
ssh -p 2222 -i ../react-devops/deploy/target-box/keys/box_key -o IdentitiesOnly=yes \
    -o UserKnownHostsFile=/dev/null -o StrictHostKeyChecking=no deploy@localhost \
    'whoami; . /etc/os-release && echo $PRETTY_NAME; docker info --format "{{.Driver}}"'
```

**PowerShell:**
```powershell
docker compose -f ../react-devops/deploy/target-box/docker-compose.yml up -d
$SshOpts = @('-i','../react-devops/deploy/target-box/keys/box_key','-o','IdentitiesOnly=yes','-o','UserKnownHostsFile=NUL','-o','StrictHostKeyChecking=no')
function Deploy { ssh -p 2222 @SshOpts deploy@localhost @args }
Deploy 'whoami; . /etc/os-release && echo $PRETTY_NAME; docker info --format "{{.Driver}}"'
```

A string variable is not a command prefix in PowerShell, so the `$DEPLOY` export used later in this lab becomes an options array plus a function. Both live only in the session that defined them, and every later block calls them. Single quotes are literal in both shells, so the remote command reaches the box untouched.

Repeated refused logins are not free here: Lab 01 installed `fail2ban`, and a handful of failures bans the address the connection came from, after which every attempt closes with `Connection closed by ...` and no mention of a ban. Clear it through the container with `docker exec box-target fail2ban-client set sshd unbanip <address>`.

**Expected result:** `deploy` on `Ubuntu 24.04.x LTS`, with the storage driver `vfs` from Lab 01 Step 4. If the driver reads `overlayfs` or `overlay2`, the Lab 01 `daemon.json` did not land: write `/etc/docker/daemon.json` with `{ "storage-driver": "vfs" }` and restart docker inside the box before continuing, or the first container run on the box fails with an overlay mount error.

---

## Step 2: Look at the Theme

**Goal:** Know which theme the starter ships and where the alternatives live.

The starter carries the [Clarity](https://github.com/chipzoller/hugo-clarity) theme as plain files under `themes/clarity`, checked in rather than added as a Git submodule, because a submodule committed inside this course repository would register as a nested gitlink. `hugo.toml` already points at it with `theme = "clarity"`, and every command below assumes Clarity.

Open your browser and go to [https://themes.gohugo.io/tags/blog/](https://themes.gohugo.io/tags/blog/) to see the alternatives. Each card links to a live demo and a GitHub repository. Swapping themes in a site of your own means cloning that repository into `themes/<name>` and changing the one `theme` line in `hugo.toml`.

**Expected result:** `themes/clarity/theme.toml` exists in the starter and declares `min_version = "0.128.0"`. The containerized build uses Hugo 0.164.0, which satisfies it.

---

## Step 3: Open the Site and Point It at Its Local URL

**Goal:** Prove the starter builds, set the site's URL, and give Claude its context.

The blog is served by a container on the box, so its `baseURL` is the URL you will reach it on, not a public domain. The starter already carries the tunnel URL from Step 8, `http://localhost:8083/`, which is how every asset link the theme emits will resolve.

Open `hugo.toml` and confirm the `baseURL` line reads as below. Change only that line if it does not; do not add a second `baseURL` line, because TOML rejects a duplicate key and every later Hugo command then fails with `unmarshal failed: toml: key baseURL is already defined`.

```toml
baseURL = 'http://localhost:8083/'
locale = 'en-us'
title = 'My New Hugo Project'
theme = "clarity"
```

Change only that line; do not add a second `baseURL` line, because TOML rejects a duplicate key and every later Hugo command then fails with `unmarshal failed: toml: key baseURL is already defined`.

With Claude Code running in `my-blog/`, or with the folder open in VS Code and the Claude panel active, send:

**Prompt:**

```text
/init
```

Then follow up with:

```text
Update the CLAUDE.md: this is a Hugo static blog. The theme is clarity. Content goes in content/posts/. Each post uses TOML front matter with these fields: date (RFC3339), title (string), draft (boolean, set to false for published posts), tags (array of strings). Do not add any other rules.
```

**Expected result:** `hugo.toml` carries `http://localhost:8083/` in `baseURL`, and a `CLAUDE.md` exists in `my-blog/` describing the content path and front matter format.

---

## Step 4: Add the First Blog Post

**Goal:** Let Claude generate a realistic mock post in the correct Hugo format.

**Prompt:**

```text
Create a blog post at content/posts/getting-started-with-ai.md.

Front matter (TOML, between +++ markers):
- date: today's date in RFC3339 format including timezone offset
- title: "Getting Started with AI-Assisted Development"
- draft: false
- tags: ["AI", "Development"]

Write 300 words of content with three sections: an introduction paragraph, a section titled "Practical Tips" with three bullet points, and a closing paragraph.
```

**Expected result:** A file at `content/posts/getting-started-with-ai.md` with valid TOML front matter and three sections of Markdown content.

---

## Step 5: Add the Second Blog Post

**Goal:** Add a second post on a different topic.

**Prompt:**

```text
Create a blog post at content/posts/github-actions-for-beginners.md.

Front matter (TOML, between +++ markers):
- date: today's date in RFC3339 format including timezone offset
- title: "GitHub Actions for Beginners"
- draft: false
- tags: ["DevOps", "GitHub"]

Write 300 words of content with three sections: an introduction to GitHub Actions, a section titled "A Practical Use Case" describing a deployment scenario, and a getting-started paragraph.
```

**Expected result:** A file at `content/posts/github-actions-for-beginners.md` with valid TOML front matter and three sections.

---

## Step 6: Build the blog inside a container

**Goal:** Produce a runnable image whose only contents are the finished site.

The whole Hugo toolchain lives inside the build. The multi-stage `dockerfile` downloads Hugo Extended 0.164.0 from the official `.deb` release, runs `hugo --minify`, and copies the resulting `public/` into an `nginx:1.27-alpine` runtime stage. Nothing about Hugo needs to exist on your machine.

**Prompt:**

```text
Create a dockerfile in this folder with two stages:

1. Build stage, FROM golang:1.24, named "hugo":
   - apt-get update, install wget
   - download https://github.com/gohugoio/hugo/releases/download/v0.164.0/hugo_extended_0.164.0_linux-amd64.deb
     and install it with dpkg -i
   - WORKDIR /site, COPY . .
   - RUN hugo --minify

2. Runtime stage, FROM nginx:1.27-alpine:
   - COPY --from=hugo /site/public /usr/share/nginx/html

Do not add EXPOSE or CMD: the base image's defaults serve on port 80.
```

Then build it:

**Bash:**
```bash
docker build -f dockerfile -t my-blog:v1 .
```

**Expected result:** The build ends with `naming to docker.io/library/my-blog:v1`. Two details are load-bearing:

- **Hugo 0.164.0, not 0.128.0.** The theme's `theme.toml` says `min_version = "0.128.0"`, but `hugo.Data.menu` in `themes/clarity/layouts/partials/header.html` needs a newer Hugo. With 0.128.0 the build fails on `can't evaluate field Data in type interface {}`, a Clarity bug that reads as a theme problem. 0.164.0 is the current winget release and builds Clarity cleanly.
- **The lowercase filename.** Docker looks for `Dockerfile` by default, so pass `-f dockerfile` explicitly.

---

## Step 7: Ship the blog to the box and run it

**Goal:** Get the image onto the box and serve it on a port nothing else uses.

**Commands:**

**Bash:**
```bash
export DEPLOY='ssh -p 2222 -i ../react-devops/deploy/target-box/keys/box_key -o IdentitiesOnly=yes -o UserKnownHostsFile=/dev/null -o StrictHostKeyChecking=no deploy@localhost'
docker save my-blog:v1 | gzip -1 | $DEPLOY 'docker load'
$DEPLOY 'docker run -d --name my-blog --restart unless-stopped -p 8083:80 my-blog:v1'
$DEPLOY 'docker ps --filter name=my-blog --format "{{.Names}}  {{.Status}}  {{.Ports}}"'
```

**PowerShell:**
```powershell
docker save my-blog:v1 -o my-blog-v1.tar
scp -P 2222 @SshOpts my-blog-v1.tar deploy@localhost:/tmp/
Deploy 'docker load -i /tmp/my-blog-v1.tar && rm /tmp/my-blog-v1.tar'
Deploy 'docker run -d --name my-blog --restart unless-stopped -p 8083:80 my-blog:v1'
Deploy 'docker ps --filter name=my-blog --format "{{.Names}}  {{.Status}}  {{.Ports}}"'
```

This is the one command in the lab that changes shape rather than spelling. **PowerShell's pipeline carries .NET objects, not bytes**, and re-encodes anything crossing it as text, so the Bash pipe would hand the far side a corrupted tar and `docker load` would fail on an archive it cannot read. Stage the image as a file, copy it with `scp`, load it from disk. Still no registry, still only SSH.

**Expected result:** `docker load` prints `Loaded image: my-blog:v1`, and the container reports `Up` and `0.0.0.0:8083->80/tcp`. The stream is a few megabytes, smaller than the React image from Lab 02, because it carries only static files.

---

## Step 8: Prove the blog serves, through an SSH tunnel

**Goal:** Verify the running blog from your own machine.

As in Lab 02, the box's published ports are not reachable directly from your host: Docker Desktop only forwards the ports the compose file declared. An SSH tunnel forwards your local port 8083 to the box's 8083:

**Commands (in a second terminal, or as a background job):**

**Bash:**
```bash
ssh -p 2222 -i ../react-devops/deploy/target-box/keys/box_key -o IdentitiesOnly=yes \
    -o UserKnownHostsFile=/dev/null -o StrictHostKeyChecking=no -N -L 8083:localhost:8083 deploy@localhost
```

**PowerShell:**
```powershell
ssh -p 2222 -i ../react-devops/deploy/target-box/keys/box_key -o IdentitiesOnly=yes -o UserKnownHostsFile=NUL -o StrictHostKeyChecking=no -N -L 8083:localhost:8083 deploy@localhost
```

Then, in your original terminal:

**Bash:**
```bash
curl -s -o /dev/null -w '%{http_code}\n' http://localhost:8083/
curl -s http://localhost:8083/ | grep -o '<title>[^<]*</title>' | head -1
curl -s http://localhost:8083/ | grep -o 'Getting Started with AI-Assisted Development\|GitHub Actions for Beginners' | sort -u
```

**PowerShell:**
```powershell
curl.exe -s -o NUL -w '%{http_code}\n' http://localhost:8083/
curl.exe -s http://localhost:8083/ | Select-String -CaseSensitive -AllMatches '<title>[^<]*</title>' | ForEach-Object { $_.Matches.Value } | Select-Object -First 1
curl.exe -s http://localhost:8083/ | Select-String -CaseSensitive -AllMatches 'Getting Started with AI-Assisted Development|GitHub Actions for Beginners' | ForEach-Object { $_.Matches.Value } | Sort-Object -Unique
```

`Select-String` is the `grep` counterpart, and three of its differences bite here. `-AllMatches` plus `$_.Matches.Value` is what makes it print the matched text rather than the whole line, which is `grep -o`. The alternation is a plain `|` because `Select-String` takes a .NET regex, where `grep`'s escaped `\|` would mean a literal pipe character. And `-CaseSensitive` is not decoration: matching is case-insensitive by default, so a post title differing only in case would satisfy a check meant to be exact.

Both twins keep only the first `<title>` match. `<title>` is not exclusive to the document head: Clarity inlines its icons as SVG and every one of them carries its own `<title>` for accessibility, so the unfiltered match prints a dozen lines of `open-menu`, `twitter` and `to-top` under the one you wanted. The head title is emitted first, so taking one match is enough.

**Expected result:** `200`, a `<title>My New Hugo Project</title>` line, and both post titles in the listing. The titles prove the two posts rendered; the title line proves the theme compiled.

---

## Step 9: Redeploy with a new post and prove it moved

**Goal:** Ship a second build and confirm the served site changed, from the served bytes.

A deploy that reports success over an unchanged site is the failure mode this module keeps returning to. Add a distinguishing page first, so "the site changed" is checkable rather than asserted.

**Prompt:**

```text
Create a blog post at content/posts/hello-ubuntu-box.md with the same front
matter format as the others, title "Hello Ubuntu Box", draft false, and one
paragraph of content. Then rebuild the image as my-blog:v2 and redeploy it to
the box on port 8084 with container name my-blog-v2, without stopping the old
container.

Report the container state and the HTTP status of
http://localhost:8084/posts/hello-ubuntu-box/ through the tunnel.
```

**Expected result:** The new container serves the new post at `http://localhost:8084/posts/hello-ubuntu-box/`, and `docker ps` on the box shows both containers. The `v2` tag on the second container is the independent proof, the same shape Lab 02 Step 7 used.

Stop the old container when you are done:

**Bash:**
```bash
$DEPLOY 'docker rm -f my-blog'
```

**PowerShell:**
```powershell
Deploy 'docker rm -f my-blog'
```

---

## Cleanup

Stop and remove this lab's containers:

**Bash:**
```bash
$DEPLOY 'docker rm -f my-blog my-blog-v2'
```

**PowerShell:**
```powershell
Deploy 'docker rm -f my-blog my-blog-v2'
Remove-Item -Force my-blog-v1.tar, my-blog-v2.tar
```

The staged tar files are the PowerShell path's own leftovers, tens of megabytes each, and the Bash path never creates them because its image goes straight down the pipe.

The box itself stays: it is shared with Lab 01 and Lab 02.

---

## What You Just Practised

| Mechanic | Step | Use it for |
|---|---|---|
| Confirming a long-lived host before building | 1 | Every session against a box that keeps running between days |
| A toolchain that lives only in the build | 6 | Reproducing a build without installing its toolchain |
| Pinning the build tool to a version that works | 6 | Avoiding a theme's undeclared minimum |
| `docker save` piped into `docker load` over SSH | 7 | Shipping an image when no registry exists |
| A dedicated publish port per service | 7 | Running several apps on one host without a port war |
| SSH tunnel for verification | 8 | Reaching a service on a private interface honestly |
| A distinguishing page in the new build | 9 | Proving a redeploy moved the served content |

[Lab 01](lab-01-deploy-to-an-ubuntu-box.md) is the full version of what Labs 02 and 03 simplified: the same box, with a Caddy edge, TLS, and a deployment sub-agent in front of the app.

