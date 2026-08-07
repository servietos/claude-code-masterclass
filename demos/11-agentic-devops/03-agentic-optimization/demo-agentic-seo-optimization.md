# Optimize a Site on the Box with Agentic SEO and Lighthouse CI

On a host you operate yourself, half an SEO and performance backlog belongs to the Caddy edge rather than the markup. You take a scored baseline with the `agentic-seo` skill, add a Lighthouse CI job that gates LCP, TBT and CLS after the deploy, apply the top findings to whichever layer owns them, then compare the snapshots. You end up holding timestamped audits under `.seo/`, a `.lighthouserc.json` with real thresholds, and a workflow that re-checks both on every redeploy.

---

## Running the Lab Starter

This demo targets the site running on the Ubuntu box from [SSH Deployment](../02-ssh-deployment/readme.md), served by the Caddy edge. Run the session from the repository root, because the workflow you extend and the site source both live there. The copies that actually serve traffic are the ones on the box under `/opt/box-stack/`; the starter copies are what you edit and ship.

Against the throwaway box on your own machine, audit `http://localhost:8080/`, which the target box maps to port 80 inside, where Caddy listens. The box also publishes `8443` for HTTPS, but a throwaway host has no publicly trusted certificate, so audit over HTTP locally and expect the HTTPS, HTTP/2 and HSTS audits to stay red.

---

## Step 1: Establish an SEO Baseline

**Overview:** Run a full SEO audit using the `agentic-seo` skill before making any changes.

**Research / Planning / Discussion:**

```text
Load the agentic-seo skill. Before running the audit, read the site source at
demos/11-agentic-devops/02-ssh-deployment/box-stack/app/ and report what the
deployed site actually consists of: every route the server answers, and for each
HTML route the title tag, the meta description, the heading hierarchy and any
structured data.

Summarize what you found and recommend an audit scope. Say explicitly which
dimensions this site cannot score well on because the content does not exist
yet, rather than treating them as findings to fix.
```

**Finding:** Claude should report one HTML route plus `/healthz`, a `<title>` of `Box Stack`, no meta description, no canonical tag, no Open Graph tags and no JSON-LD. On a one-page site the useful scope is that page and nothing else, so push back if Claude invents a sitemap, a services page or a blog index; none of those exist in `app/`. Content Quality and Authority will score low for reasons no fix in this demo addresses, and saying so up front is what keeps Step 3 focused on the findings that are real.

**Recipe:**

```text
Run a full SEO audit using the agentic-seo skill on the deployed page at the
site root.

Audit the deployed site through the Caddy edge, not a local build. Check:
- Rendered title tag and meta description (length, uniqueness, keyword relevance)
- H1/H2 hierarchy
- Canonical tag
- JSON-LD structured data output
- Open Graph tags

Score Technical SEO, On-Page SEO, Content Quality, and Authority out of 10.
Write the full snapshot to .seo/YYYY-MM-DD/SEO_AUDIT-GENERAL-hhmm.md and
update .seo/readme.md with the new row.
```

**Expected Outcome:** A timestamped audit file exists under `.seo/`. The audit contains a scored table with at least four dimensions and a prioritized backlog of findings. The `.seo/readme.md` runs log has a new row for today's run.


---

## Step 2: Add a Lighthouse CI Workflow

**Overview:** A Lighthouse CI job in the deploy workflow collects Core Web Vitals on every push and fails the build when LCP, CLS, or TBT regress past the defined thresholds.

**Research / Planning / Discussion:**

```text
Read the existing deploy workflow at .github/workflows/ and identify the job
that redeploys the container on the box over SSH.

Where should the Lighthouse CI job run: before or after that deploy job?
What URL should Lighthouse target: the container's published port on the box,
the hostname Caddy serves, or a local build of the site?
What are reasonable starting thresholds for LCP, TBT, and CLS on a
content-focused site?
```

**Finding:** Claude should explain that Lighthouse must run after the SSH deploy job (so the live host reflects the latest image) and target the hostname Caddy serves rather than the container port. Thresholds should align with Google's "Good" thresholds: LCP below 2500ms, TBT below 200ms, CLS below 0.1. Push back if Claude proposes the raw container port or a local build; the test is whether the request passes through the edge, so the box's published Caddy port qualifies and `web:8080` does not.

**Recipe:**

```text
Add a Lighthouse CI job to the existing deploy workflow at .github/workflows/.

The job should:
1. Run after the SSH deploy job completes (use `needs:`)
2. Install @lhci/cli with npm install -g
3. Run lhci autorun --collect.url="https://${{ vars.APP_HOST }}/"
4. Assert LCP < 2500ms, TBT < 200ms, CLS < 0.1
5. Upload .lighthouseci/ as the artifact "lighthouse-results"

Also add a concurrency group to the workflow, named after the box rather than
the app, with cancel-in-progress: false, so two deploys never pull layers
against the same Docker daemon at once.

Create .lighthouserc.json at the repo root with:
- collect.url set to https://app.example.at/ as the default target
- collect.numberOfRuns: 3
- assert.preset: "lighthouse:recommended"
- the three assertions above

Commit both files. Do not trigger the workflow yet.
```

**Expected Outcome:** `.lighthouserc.json` exists at the repo root. The deploy workflow has a new `lighthouse` job with `needs:` pointing at the SSH deploy job, and a box-scoped `concurrency` block. No workflow run has been triggered yet.


---

## Step 3: Implement SEO Fixes from the Baseline Audit

**Overview:** Apply the highest-priority findings from the Step 1 audit.

**Research / Planning / Discussion:**

```text
Read the audit snapshot at .seo/YYYY-MM-DD/SEO_AUDIT-GENERAL-hhmm.md.

List the top three findings by impact score from the prioritized backlog.
For each finding, classify it as a site-source fix or a Caddyfile fix, then name
the exact file that needs to change, the specific line or field, and what the
fixed value should look like.
Do not fix anything yet, only plan the changes.
```

**Finding:** Claude should return a precise change plan listing file paths, field names, and proposed values for each of the top three issues. Look for specificity: "replace the `<title>` in `box-stack/app/index.html` from `Box Stack` with `Box Stack: a container deployed over SSH`, and add a `<meta name="description">` beneath it" is a good response. A vague list like "improve title tags" is not. Push back if Claude does not reference actual file paths.

Check the layer classification just as closely. A plan that proposes a build-pipeline change for a missing `Content-Encoding` header has misread which layer owns the finding, and this app has no build pipeline to change.

**Recipe:**

```text
Apply the top three fixes identified in the research step.

For each fix:
1. Edit the exact file and field identified in the plan
2. Redeploy the box with the SSH loop, then navigate to the affected page in
   the browser against the deployed URL, never a local build
3. Confirm the rendered output matches the intended value using the
   chrome-devtools MCP (check the <title> tag and JSON-LD output)
4. Note the fix as confirmed

For a Caddyfile fix, write the file in place on the box rather than moving a new
file over the name, reload the edge, and prove the served bytes changed with
curl -sI on the deployed URL.

After all three fixes are applied and verified in the browser, run only the
technical SEO audit (agentic-seo-audit-technical) on the deployed page and write
the result to .seo/ as a TECHNICAL series snapshot.
```

**Expected Outcome:** Targeted edits land in `box-stack/app/index.html`, in `box-stack/Caddyfile`, or in both, depending on which layer owns each finding. A technical audit snapshot exists under `.seo/`. The snapshot notes each fixed field as correct in the rendered output. No unrelated files were modified.


---

## Step 4: Verify Improvements and Compare Snapshots

**Overview:** Push the changes, let the Lighthouse CI workflow run, then compare the post-fix audit against the original baseline.

**Research / Planning / Discussion:**

```text
Read both .seo/ snapshots: the original GENERAL audit from Step 1 and the
TECHNICAL audit from Step 3.

Which dimensions improved and by how much? Are there any regressions?
What does the Lighthouse CI workflow need to report for this run to be
considered a success?
```

**Finding:** Claude should produce a delta table showing before/after scores for each dimension and flag any dimension that did not improve or regressed. Look for at least a 0.5-point gain in On-Page SEO if title tags and meta descriptions were fixed. If Claude claims improvement without reading the actual snapshot files, push back.

**Recipe:**

```text
Commit the changes from Step 3 on a scratch branch and push that branch. Do not
push to main and do not open a pull request. Trigger the deployment workflow
manually against your branch:

  gh workflow run deploy.yml --ref <your-branch>

After the Lighthouse CI job completes:
1. Run gh run download to retrieve the "lighthouse-results" artifact
2. Read the LCP, TBT, and CLS values from the JSON report
3. Confirm all three metrics pass the thresholds defined in .lighthouserc.json
4. Run the agentic-seo-compare skill to compare the Step 1 GENERAL snapshot
   with today's TECHNICAL snapshot
5. Report the score delta and whether the Lighthouse CI job passed

Return a summary in this format:
- SEO score before / after per dimension
- Lighthouse CI result: pass / fail with metric values
- Next recommended action from the backlog
```

**Expected Outcome:** The GitHub Actions workflow shows a green Lighthouse CI job. The score delta section shows improvement in at least the dimensions targeted in Step 3. The comparison file exists at `.seo/YYYY-MM-DD/SEO_AUDIT-TECHNICAL-comparrison.md`.

