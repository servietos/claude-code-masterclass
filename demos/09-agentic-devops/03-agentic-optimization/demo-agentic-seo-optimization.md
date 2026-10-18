# Optimize a Site on the Box with Agentic SEO and Lighthouse CI

On a host you operate yourself, half an SEO and performance backlog belongs to the Caddy edge. You end up holding timestamped audits under `.seo/`, a `.lighthouserc.json` with real thresholds, and a workflow that re-checks both on every redeploy.

---

## Step 1: Establish an SEO Baseline

Run the session from the repository root and audit `http://localhost:8080/`, which the target box maps to port 80 inside, where Caddy listens. Scope the audit to what exists, then let the `agentic-seo` skill write its scored snapshot to `.seo/YYYY-MM-DD/SEO_AUDIT-GENERAL-hhmm.md`:

```text
Load the agentic-seo skill. Before running the audit, read the site source at
demos/09-agentic-devops/02-ssh-deployment/box-stack/app/ and report what the
deployed site actually consists of: every route the server answers, and for each
HTML route the title tag, the meta description, the heading hierarchy and any
structured data.

Summarize what you found and recommend an audit scope. Say explicitly which
dimensions this site cannot score well on because the content does not exist
yet, and leave them out of the findings to fix. Then run that scope against
http://localhost:8080/ and write the scored snapshot to
.seo/YYYY-MM-DD/SEO_AUDIT-GENERAL-hhmm.md.
```

Claude should report one HTML route plus `/healthz`, a `<title>` of `Box Stack`, no meta description, no canonical tag, no Open Graph tags and no JSON-LD; push back if it invents a sitemap, a services page or a blog index.

## Step 2: Add a Lighthouse CI Workflow

A Lighthouse CI job in the deploy workflow collects Core Web Vitals on every push and fails the build when LCP, CLS, or TBT regress past the defined thresholds.

```text
Add a Lighthouse CI job to the deploy workflow at .github/workflows/box-deploy.yml.
The repository has no SSH deploy workflow yet, so create that file with a deploy
job that redeploys the box over SSH, then add the Lighthouse job.

The job should:
1. Run after the SSH deploy job completes (use `needs:`)
2. Install @lhci/cli with npm install -g
3. Run lhci autorun --collect.url="https://${{ vars.APP_HOST }}/"
4. Assert LCP < 2500ms, TBT < 200ms, CLS < 0.1
5. Upload .lighthouseci/ as the artifact "lighthouse-results"

Create .lighthouserc.json at the repo root with the collect and assert settings
nested under a top-level `ci` key, containing:
- collect.url set to https://app.example.at/ as the default target
- collect.numberOfRuns: 3
- assert.preset: "lighthouse:recommended"
- the three assertions above
```

Lighthouse runs after the SSH deploy job and targets the hostname Caddy serves; push back if Claude proposes the raw container port or a local build.

## Step 3: Implement SEO Fixes from the Baseline Audit

Plan the top three findings by the layer that owns them, then apply each one and confirm it in the rendered output on the deployed URL:

```text
Read the audit snapshot at .seo/YYYY-MM-DD/SEO_AUDIT-GENERAL-hhmm.md.
List the top three findings by impact score from the prioritized backlog.
For each finding, classify it as a site-source fix or a Caddyfile fix, then name
the exact file that needs to change, the specific line or field, and what the
fixed value should look like.
Do not fix anything yet, only plan the changes.
```

```text
Apply the top three fixes identified in the research step.
For each fix:
1. Edit the exact file and field identified in the plan
2. Redeploy the box with the SSH loop, then navigate to the affected page in
   the browser against the deployed URL, never a local build
3. Confirm the rendered output matches the intended value using the
   chrome-devtools MCP (check the <title> tag and JSON-LD output)
For a Caddyfile fix, write the file in place on the box and never move a new
file over the name, reload the edge, and prove the served bytes changed with
curl -sI on the deployed URL.
```

Edits land in `box-stack/app/index.html`, in `box-stack/Caddyfile`, or in both; a plan that proposes a build-pipeline change for a missing `Content-Encoding` header has misread which layer owns the finding.
