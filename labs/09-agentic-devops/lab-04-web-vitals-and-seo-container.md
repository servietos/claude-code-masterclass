# Optimize Web Vitals and SEO on the Deployed App

Audit the `react-devops` app exactly as the public reaches it, through the Caddy edge on the Ubuntu box from Lab 01, and fix what the audit finds. You will hold a scored baseline under `.seo/`, a `.lighthouserc.json` that asserts LCP below 2500 ms, TBT below 200 ms and CLS below 0.1, and three fixes, each assigned to the layer that owns it: the site source or the Caddyfile.

On your own box nobody tells you which layer a finding belongs to. A missing meta description is a line in `index.html`; a missing `Content-Encoding` header is a line in the Caddyfile, and no amount of editing React changes it. Guessing the layer costs a rebuild and a redeploy per wrong guess, so this lab makes you name the layer first and prove each change on the deployed URL afterwards.

The teaching behind this lab is the topic [Agentic Optimization: Web Vitals and SEO](../../demos/09-agentic-devops/03-agentic-optimization/readme.md) and its demo [Optimize a Site on the Box with Agentic SEO and Lighthouse CI](../../demos/09-agentic-devops/03-agentic-optimization/demo-agentic-seo-optimization.md). The demo shows the loop on the box-stack sample; this lab runs it on the app you shipped yourself.

Each step contains:

- **Goal**: what you are building
- **Prompt or command**: what you run
- **Expected result**: what the outcome looks like

## Prerequisites

- **Lab 01 completed through Step 8, and not cleaned up.** The `box-target` container must be running with the Compose stack in `/opt/react-devops`, and the sibling folder [react-devops/](react-devops) must still hold `deploy/target-box/keys/box_key` and `deploy/box-local-ca.crt`. This lab reads both by relative path. If you ran Lab 01's Cleanup, repeat its Steps 2 to 8 first.
- **Node.js 20 or newer and Google Chrome** on your own machine. The `chrome-devtools` MCP server and Lighthouse CI both launch a local Chrome, and both start from `npx`. Check with `node --version` and open Chrome once so its first-run dialog is out of the way.
- **Claude Code 2.x** with the global `agentic-seo` skill installed. Check that `/agentic-seo` autocompletes inside a session.
- **Host ports 2222, 8080 and 8443** are the ones Lab 01 published; nothing in this lab changes them.
- **A shell**: Bash (git-bash or WSL on Windows, any shell on macOS and Linux) or PowerShell 7. Command blocks that differ between the shells ship a `powershell` twin directly below the `bash` one. The substitutions from Lab 01 apply unchanged: `curl.exe` for `curl`, `NUL` for `/dev/null`, `--ssl-revoke-best-effort` on every `curl.exe` call that passes `--cacert`, and a staged tar file where Bash pipes `docker save | ssh`.

You work in the starter at [react-devops-seo/](react-devops-seo). It is a pristine copy of the `react-devops` source plus two files the lab consumes: `.mcp.json`, which registers the `chrome-devtools` server with a hostname mapping for `app.box.test`, and `.claude/rules/seo.md`, the site-facts file the `agentic-seo` skill reads before any audit.

---

## Where to Open Claude Code

Open Claude Code inside the starter. `.mcp.json`, `.claude/rules/` and `.claude/agents/` load from the directory the session was launched in, so a session started at the repo root registers no `chrome-devtools` server and the skill never sees the site facts. Run this from the repo root; both commands work unchanged in PowerShell.

**Bash:**
```bash
cd labs/09-agentic-devops/react-devops-seo
claude
```

Approve the project-scoped `chrome-devtools` server when Claude Code asks. The repo's own `/.mcp.json` stays out of the session, which is intended: it carries servers this lab does not use.

---

## Step 1: Prove the edge answers before you audit it

**Goal:** Confirm the deployed URL responds with the app, and set up the shell helpers every later step reuses.

An audit of a URL that does not answer produces a confident report about an error page. Check the edge first with `curl --resolve`, which supplies the address `app.box.test` would resolve to, and verify the certificate chain against the CA you pulled off the box in Lab 01 and keep certificate verification on.

**Commands**, in a terminal you keep for the whole lab, run from `react-devops-seo`:

**Bash:**
```bash
export KEY=../react-devops/deploy/target-box/keys/box_key
export CA=../react-devops/deploy/box-local-ca.crt
export SSHO="-i $KEY -o IdentitiesOnly=yes -o UserKnownHostsFile=/dev/null -o StrictHostKeyChecking=no"
export DEPLOY="ssh -p 2222 $SSHO deploy@localhost"
edge() { curl -s --cacert "$CA" --resolve app.box.test:8443:127.0.0.1 "$@"; }
edge -o /dev/null -w '%{http_code}\n' https://app.box.test:8443/
edge https://app.box.test:8443/ | head -9
$DEPLOY 'cd /opt/react-devops && docker compose ps --format "{{.Service}} {{.Image}} {{.State}}"'
```

**PowerShell:**
```powershell
$Key = '../react-devops/deploy/target-box/keys/box_key'
$Ca = '../react-devops/deploy/box-local-ca.crt'
$SshOpts = @('-i',$Key,'-o','IdentitiesOnly=yes','-o','UserKnownHostsFile=NUL','-o','StrictHostKeyChecking=no')
function Deploy { ssh -p 2222 @SshOpts deploy@localhost @args }
function Edge { curl.exe -s --ssl-revoke-best-effort --cacert $Ca --resolve app.box.test:8443:127.0.0.1 @args }
Edge -o NUL -w '%{http_code}\n' https://app.box.test:8443/
Edge https://app.box.test:8443/ | Select-Object -First 9
Deploy 'cd /opt/react-devops && docker compose ps --format "{{.Service}} {{.Image}} {{.State}}"'
```

**Expected result:** `200`, then the first lines of the app's `index.html` showing `<title>React Food Shop</title>`, then two lines: `web` running the image tag Lab 01 left behind (`react-devops:v1` or `react-devops:v2`) and `caddy` running `caddy:2-alpine`. Note the web image tag now, because Step 7 replaces it. If the `curl` fails with a certificate error, the `CA` path is wrong for your current directory; if it fails to connect, the box container is not running.

---

## Step 2: Point the browser at the deployed hostname

**Goal:** Have the `chrome-devtools` MCP open `https://app.box.test:8443/` and read the page, the same way a reader of the public site would.

`app.box.test` resolves nowhere on your machine, and the edge's certificate comes from Caddy's local CA, which no browser trusts. The starter's `.mcp.json` solves both inside the MCP's own Chrome: `--chromeArg=--host-resolver-rules=MAP app.box.test 127.0.0.1` maps the name to your loopback, and `--acceptInsecureCerts` accepts the local CA. Nothing on your machine's resolver or trust store changes.

**Prompt:**

```text
Use the chrome-devtools MCP to open https://app.box.test:8443/ and report:
1. the document title
2. the text content of the h1
3. whether a meta description, a canonical link and any application/ld+json
   script exist in the DOM (answer with the evaluate_script result)
4. the console messages
Do not change any file.
```

If `/mcp` does not list `chrome-devtools` as connected, run `/exit`, start `claude` again in the starter and approve the server; `.mcp.json` is read at startup.

**Expected result:** The title `React Food Shop`, an h1 reading `React Food Shop`, no meta description, no canonical link and no JSON-LD script, and an empty console. Claude should not mention a certificate warning or a name-resolution failure; if it does, the two `args` in `.mcp.json` did not load.

---

## Step 3: Scope the audit to what the site actually contains

**Goal:** Fix the audit scope from the served bytes so the skill scores a one-page app as a one-page app.

`agentic-seo` scores four dimensions: Technical SEO, On-Page SEO, Content Quality and Authority. This site has one route, no sitemap and no blog, so several dimensions cannot score well because the content does not exist. A finding like "add a blog" is noise; the scope step keeps it out of the backlog.

**Prompt:**

```text
Load the agentic-seo skill and read .claude/rules/seo.md.

Before auditing, inspect the deployed site at https://app.box.test:8443/ with
the chrome-devtools MCP and report what it consists of: every route that
answers, the title tag, the meta description, the heading hierarchy, any
structured data, and the response headers of the HTML document and of one
JavaScript bundle under /assets/ (Content-Encoding, Cache-Control and the
protocol). Do not pass a Content-Encoding conclusion from a request that sent no
Accept-Encoding header.

Recommend an audit scope. Say explicitly which dimensions this site cannot
score well because the content does not exist yet, and keep them out of the
findings list.
```

**Expected result:** One HTML route plus `/healthz`, a title of `React Food Shop`, no meta description, no canonical, no Open Graph tags and no JSON-LD. The bundle response carries no `Content-Encoding` and no `Cache-Control`, and the protocol is `h2`. Claude recommends a scope that covers the home page only and names Content Quality and Authority as limited by the missing content. Push back if it invents a sitemap, a services page or a blog index, or if it reports compression as present from a request without `Accept-Encoding`: nginx in the app container never compresses, and the edge adds nothing yet.

---

## Step 4: Run the baseline audit

**Goal:** A scored snapshot of the deployed site written to `.seo/`.

The `agentic-seo` skill writes each run as a timestamped file under `.seo/YYYY-MM-DD/` and keeps a runs log in `.seo/readme.md`. The first run is your baseline: every later claim of improvement is a score delta against this file.

**Prompt:**

```text
Run a general SEO audit with the agentic-seo skill against the deployed site
https://app.box.test:8443/ through the Caddy edge, using the scope you
recommended. Production validation is explicitly requested: this host is the
only target, there is no local preview. Use the chrome-devtools MCP for runtime
checks. Score Technical SEO, On-Page SEO, Content Quality and Authority out of
10, write the snapshot to .seo/ and update the runs log.
```

**Expected result:** A file at `.seo/<today>/SEO_AUDIT-GENERAL-<hhmm>.md` and a `.seo/readme.md` runs log with one row. The snapshot carries four scores, a prioritized backlog and an impact score per finding. The backlog should include a missing meta description, missing structured data, and the missing text compression and cache headers on the bundle. Open the file and read the four scores once: you compare against them in Step 9.

---

## Step 5: Assert the Web Vitals thresholds with Lighthouse CI

**Goal:** A `.lighthouserc.json` that fails the run when LCP, TBT or CLS cross their limits, and the baseline numbers it produces.

Lighthouse CI measures against the same hostname, so it has to resolve the name and accept the local CA exactly as the MCP's Chrome does. The `chromeFlags` setting carries both flags into the Chrome that Lighthouse launches. The file also pins `numberOfRuns` to 3, because a single Lighthouse run varies by tens of milliseconds and the median of three is the number worth asserting on.

**Prompt:**

```text
Create .lighthouserc.json at the project root with exactly this content:

{
  "ci": {
    "collect": {
      "url": ["https://app.box.test:8443/"],
      "numberOfRuns": 3,
      "settings": {
        "chromeFlags": "--ignore-certificate-errors --host-resolver-rules=\"MAP app.box.test 127.0.0.1\""
      }
    },
    "assert": {
      "assertions": {
        "largest-contentful-paint": ["error", { "maxNumericValue": 2500 }],
        "total-blocking-time": ["error", { "maxNumericValue": 200 }],
        "cumulative-layout-shift": ["error", { "maxNumericValue": 0.1 }]
      }
    },
    "upload": { "target": "filesystem", "outputDir": ".lighthouseci" }
  }
}

Then run: npx --yes @lhci/cli@0.15.1 collect
followed by: npx --yes @lhci/cli@0.15.1 assert

Read the lhr-*.json files in .lighthouseci/ and write the median LCP in
milliseconds, the median TBT, the median CLS and the median Performance and
SEO category scores to .seo/vitals-before.md as a five-row table. Do not edit
any site file.
```

**Expected result:** `.lighthouserc.json` exists, `.lighthouseci/` holds three `lhr-*.json` files, and `assert` prints one line per assertion with a pass or fail marker. A single static page on a local box usually meets all three thresholds, so a clean assert is a normal baseline; if an assertion fails, write down which one, because it is a finding the fixes below must clear. `.seo/vitals-before.md` lists the five medians. `.lighthouseci/` is already in the starter's `.gitignore`.

---

## Step 6: Classify the top three findings by layer

**Goal:** A plan that names the owning layer, file and value for each of the top three findings, before any file changes.

The layer decides the redeploy. A source fix means a new image, shipped and recreated; a Caddyfile fix means one file written in place and a reload. Planning first is the cheap moment to catch a finding assigned to the wrong layer.

**Prompt:**

```text
Read the audit snapshot at .seo/<today>/SEO_AUDIT-GENERAL-<hhmm>.md and
.seo/vitals-before.md. List the top three findings by impact score from the
prioritized backlog. For each one, classify it as a "site source" fix or a
"Caddyfile" fix, then name:
- the exact file (index.html, or /opt/react-devops/Caddyfile on the box)
- the specific line or directive
- the fixed value
- the command that will prove it on the deployed URL

Do not fix anything yet.
```

**Expected result:** A table of three rows. The typical split is two source fixes and one Caddyfile fix: the meta description (and a sharper title) in `index.html`, a JSON-LD `WebSite` or `WebApplication` block in `index.html`, and `encode zstd gzip` inside the `app.box.test` block of the Caddyfile, proven with `curl -sI` and a `Content-Encoding` header. Cache headers on `/assets/*` are the usual fourth candidate. Push back if Claude proposes a Vite plugin or a build change for compression, or an nginx change for a header the edge owns: the lab keeps the app container as Lab 01 built it.

---

## Step 7: Fix the source findings and redeploy the image

**Goal:** Land the source-layer fixes from the plan in `index.html`, ship a new image tag and confirm the rendered page on the deployed URL.

The source layer redeploys through the loop from Lab 01: build, ship the image over SSH, point the stack at the new tag, recreate only `web`. A fresh tag matters. If the tag in the Compose file does not change, `up -d` finds nothing to recreate and the deploy reports success over the old page.

Pull the live Compose file first, so the edit starts from what the box runs:

**Bash:**
```bash
mkdir -p box
scp -P 2222 $SSHO deploy@localhost:/opt/react-devops/docker-compose.yml deploy@localhost:/opt/react-devops/Caddyfile box/
ls box
```

**PowerShell:**
```powershell
New-Item -ItemType Directory -Force box | Out-Null
scp -P 2222 @SshOpts deploy@localhost:/opt/react-devops/docker-compose.yml deploy@localhost:/opt/react-devops/Caddyfile box/
Get-ChildItem box
```

**Expected result:** `box/` holds `Caddyfile` and `docker-compose.yml`, both copied from the box. They are your working copies for this step and Step 8.

**Prompt:**

```text
Apply the site-source fixes from the plan. For each fix:
1. Edit index.html at the field named in the plan. The meta description must be
   between 70 and 160 characters and describe the app. Any JSON-LD goes in a
   <script type="application/ld+json"> block in <head> and must be valid JSON
   with @context https://schema.org.
2. Build the image: docker build -f dockerfile -t react-devops:seo-1 .
3. Ship it to the box: docker save react-devops:seo-1, then docker load on the
   box over ssh as the deploy user. Connection: ssh -p 2222 -i
   ../react-devops/deploy/target-box/keys/box_key -o IdentitiesOnly=yes -o
   UserKnownHostsFile=/dev/null -o StrictHostKeyChecking=no deploy@localhost
4. In box/docker-compose.yml set the web service image to react-devops:seo-1,
   then copy the file to /opt/react-devops/docker-compose.yml with scp, writing
   to that exact path.
5. On the box run: cd /opt/react-devops && docker compose up -d web
   (use up; restart keeps the old image).
6. Use the chrome-devtools MCP on https://app.box.test:8443/ to read the
   document title, the meta description and the JSON-LD script text, and
   confirm each matches the intended value.
Do not touch box/Caddyfile in this step. Report what you changed and what the
browser returned.
```

On PowerShell, add one sentence to item 3: "Stage the image with `docker save -o` to a tar file, copy it with `scp`, and load it with `docker load -i`; do not pipe the archive through PowerShell." The pipeline re-encodes binary data and corrupts the tar.

Then check the claims from your own terminal, because Claude's summary is a claim:

**Bash:**
```bash
$DEPLOY 'docker inspect react-devops-web --format "{{.Config.Image}}"'
edge https://app.box.test:8443/ | grep -iE '<title>|name="description"|ld\+json'
```

**PowerShell:**
```powershell
Deploy 'docker inspect react-devops-web --format "{{.Config.Image}}"'
Edge https://app.box.test:8443/ | Select-String -Pattern '<title>|name="description"|ld\+json'
```

**Expected result:** `react-devops:seo-1` as the running image, and the served HTML now contains the new `<title>`, a `<meta name="description" ...>` line and the `application/ld+json` script. In the browser, Claude reports the new title, a description of 70 to 160 characters and a JSON-LD object whose `@type` is the one the plan chose. The old tag is still on the box as an unused image, which is your rollback.

---

## Step 8: Fix the Caddyfile finding and prove the header on the wire

**Goal:** Apply the edge-layer fix to the Caddyfile on the box, reload Caddy, and see the changed header in a real response.

Compression, cache policy and the protocol all live in the edge. The Caddyfile is bind-mounted into the container, which binds the file's inode: a `mv` of a new file over the name leaves Caddy serving the old content while `caddy validate` reports a valid config. Writing to the exact path with `scp`, as in Lab 01, keeps the inode.

**Prompt:**

```text
Apply the Caddyfile fix from the plan to box/Caddyfile. Add the directive
inside the app.box.test site block only; the :8090 health block stays as it
is. Then:
1. Copy box/Caddyfile to /opt/react-devops/Caddyfile on the box with scp,
   writing to that exact path. Never mv a new file over it.
2. Validate and reload the edge on the box:
   cd /opt/react-devops && docker compose exec -T caddy caddy validate --config /etc/caddy/Caddyfile
   cd /opt/react-devops && docker compose exec -T caddy caddy reload --config /etc/caddy/Caddyfile
3. Prove the served bytes changed. Find the bundle path with
   curl -s --cacert ../react-devops/deploy/box-local-ca.crt --resolve app.box.test:8443:127.0.0.1 https://app.box.test:8443/
   and request it with curl -sI and the header Accept-Encoding: gzip (curl sends
   none by default, and Caddy only compresses when the client asks).
Report the full response headers of the bundle before and after, and say whether
the same header changed on the HTML document.
```

Then repeat the proof yourself:

**Bash:**
```bash
JS=$(edge https://app.box.test:8443/ | grep -o '/assets/[^"]*\.js' | head -1)
edge -sI -H 'Accept-Encoding: gzip' "https://app.box.test:8443$JS" | grep -iE 'HTTP/|content-encoding|vary|cache-control'
```

**PowerShell:**
```powershell
$Js = [regex]::Match((Edge https://app.box.test:8443/ | Out-String), '/assets/[^"]+\.js').Value
Edge -sI -H 'Accept-Encoding: gzip' "https://app.box.test:8443$Js" | Select-String -Pattern 'HTTP/|content-encoding|vary|cache-control'
```

**Expected result:** The bundle response now includes `Content-Encoding: gzip` (or `zstd` when the request asks for it) and `Vary: Accept-Encoding`, where Step 3 showed neither. If the plan also added a long-lived `Cache-Control` for `/assets/*`, that header appears too. Without the `Accept-Encoding` request header the same command returns no `Content-Encoding`, which is correct: compression is negotiated, and a check that forgets the header reports a fix that did not land.

---

## Step 9: Re-audit and compare against the baseline

**Goal:** Measure the same two things again and put the change in numbers.

A fix is only proven when the same measurement moves. The compare run reads the new snapshot against the first, so the baseline is referenced once, at the end, as a score delta.

**Prompt:**

```text
Run a second general SEO audit with the agentic-seo skill against
https://app.box.test:8443/ with the same scope, then run the compare workflow
between the two snapshots and write the comparison to .seo/.

Afterwards run npx --yes @lhci/cli@0.15.1 collect and
npx --yes @lhci/cli@0.15.1 assert, read the new lhr-*.json files and write the
same five medians to .seo/vitals-after.md. Finish with a table that lists the
three fixes, the layer each one lived in, and the evidence that proved each on
the deployed URL.
```

**Expected result:** A second `SEO_AUDIT-GENERAL-<hhmm>.md`, a comparison file, and a runs log with two rows. On-Page SEO rises because the meta description and structured data exist, and Technical SEO rises because the bundle is compressed. `.seo/vitals-after.md` shows the Performance score at or above the baseline and `assert` passes all three thresholds. The closing table has three rows: two marked "site source" with the title, description or JSON-LD evidence from the browser, and one marked "Caddyfile" with the `Content-Encoding` header from `curl -sI`.

---

## Cleanup

Everything this lab wrote locally lives in the starter and returns `git status` to clean when removed. The box keeps running the `seo-1` image and the edited Caddyfile until you tear it down; [Lab 01's Cleanup](lab-01-deploy-to-an-ubuntu-box-container.md#cleanup) does that, and Labs 02 and 03 deploy to the same box, so run it last.

**Bash:**
```bash
rm -rf .seo .lighthouseci box .lighthouserc.json
git checkout -- index.html
docker image rm react-devops:seo-1
git status --short
```

**PowerShell:**
```powershell
Remove-Item -Recurse -Force .seo, .lighthouseci, box, .lighthouserc.json
git checkout -- index.html
docker image rm react-devops:seo-1
git status --short
```

**Expected result:** `git status --short` prints nothing inside `react-devops-seo`.

## What You Just Practised

| Mechanic                                                         | Step | Use it for                                                             |
| ---------------------------------------------------------------- | ---- | ---------------------------------------------------------------------- |
| `curl --resolve` plus `--cacert` against the edge                | 1    | Proving the audited URL answers before any report is trusted           |
| Host mapping and insecure certs scoped to the MCP's own Chrome   | 2, 5 | Auditing a hostname with no DNS record and a local CA                  |
| Scoping an audit from the served bytes                           | 3    | Keeping fake findings out of the backlog of a one-page site            |
| Timestamped `.seo/` snapshots and a runs log                     | 4, 9 | A baseline every later improvement is measured against                 |
| Lighthouse CI assertions on LCP, TBT and CLS with a median of 3  | 5    | Failing a run on regressions with a number    |
| Classifying a finding as source or Caddyfile before editing      | 6    | Choosing the right redeploy loop the first time                        |
| New image tag, `up -d web` and a browser read of the DOM         | 7    | Source fixes that cannot silently deploy as a no-op                    |
| In-place write of a bind-mounted config, reload and `curl -sI`   | 8    | Edge fixes proven on the wire with the `Accept-Encoding` request header |
| Second audit plus compare                                        | 9    | Turning a fix into a score delta                                       |

[Lab 03](lab-03-hugo-blog-ubuntu-box-container.md) applies the same box to a static Hugo site. The demo [Optimize a Site on the Box with Agentic SEO and Lighthouse CI](../../demos/09-agentic-devops/03-agentic-optimization/demo-agentic-seo-optimization.md) adds the GitHub Actions workflow that repeats the Lighthouse run after every push.
