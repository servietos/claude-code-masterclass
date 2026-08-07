---
presents: demo-agentic-seo-optimization.md
budget: 5 min
beats: 5
---

# Present: Optimize a Site on the Box with Agentic SEO and Lighthouse CI

An optimization loop runs against the deployed site rather than a local build, and half the backlog belongs to the edge. Five beats: the audit scope, the on-page surface, the layer split, the served-bytes check, the CI gate.

------

This topic ships no starter. The run writes `.seo/` snapshots and `.lighthouserc.json` at the repository root, and edits topic 02's [`box-stack/`](../02-ssh-deployment/box-stack).

## Beats

### Beat 1: scope the audit to what exists, and say what cannot score (1 min)

**Open:** [`box-stack/app/`](../02-ssh-deployment/box-stack/app) · [Step 1: Establish an SEO Baseline](demo-agentic-seo-optimization.md#step-1-establish-an-seo-baseline)
**Say:** An audit scores a site against a template of what a complete site has, so a one-page deployment always looks incomplete. Decide up front which dimensions cannot improve.

```text
Summarize what you found and recommend an audit scope. Say explicitly which
dimensions this site cannot score well on because the content does not exist
yet, rather than treating them as findings to fix.
```

**Result:** a scored GENERAL snapshot at `.seo/YYYY-MM-DD/SEO_AUDIT-GENERAL-hhmm.md` plus a new row in `.seo/readme.md` (both written by Step 1, neither in the repository), scoped to one page and `/healthz`.

**Gotcha:** asked for an audit of a one-page site, a model will happily produce findings for a sitemap, a services page and a blog index; push back and the scope collapses.

### Beat 2: the entire discoverable surface of the deployed site (1 min)

**Open:** [`box-stack/app/index.html`](../02-ssh-deployment/box-stack/app/index.html) · [readme.md](readme.md#the-agentic-seo-skill)
**Say:** What a crawler can state about a page comes from a small fixed set of declarations near the top of the document. A missing tag is not a default, it is silence.

```html
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Box Stack</title>
```

**Result:** the baseline audit reports one title, no meta description, no canonical tag, no Open Graph tags and no JSON-LD; four fields, all landing back in this one file, which the app image copies in verbatim with no build step.

**Gotcha:** Content Quality and Authority stay low for reasons no fix in this demo addresses, which is exactly what beat 1 declared out of scope.

### Beat 3: on your own box, the fix layer is a decision (1 min)

**Open:** [readme.md](readme.md#where-caddy-owns-the-fix) · [Step 3: Implement SEO Fixes from the Baseline Audit](demo-agentic-seo-optimization.md#step-3-implement-seo-fixes-from-the-baseline-audit)
**Say:** Response headers, compression and protocol version belong to whatever terminates the connection; markup and assets belong to the application. A managed platform silently handled the first group.

```markdown
| Enable text compression | Caddyfile | `encode zstd gzip` inside the site block |
| Serve static assets with an efficient cache policy | Caddyfile | `header /assets/* Cache-Control "public, max-age=31536000, immutable"` on fingerprinted paths |
| Use HTTP/2, Uses HTTPS, HSTS | Caddyfile | Already supplied by automatic TLS; verify rather than add |
| Properly size images, defer offscreen images | Site source | Templates, layouts, and the build pipeline |
| Missing meta description, title, structured data | Site source | Front matter and templates, the `agentic-seo` territory |
```

**Result:** the edge half of the backlog lands in [`box-stack/Caddyfile`](../02-ssh-deployment/box-stack/Caddyfile), which today holds only the `:8090` health probe and no `encode` or `header` directive

```caddyfile
:8090 {
	handle /healthz {
		respond "ok" 200
	}
}
```

**Gotcha:** a plan proposing a build-pipeline change for a missing `Content-Encoding` header has misread the owner, and this app has no build pipeline to change.

### Beat 4: the fix is confirmed in the rendered output, never in the diff (1 min)

**Open:** [Step 3: Implement SEO Fixes from the Baseline Audit](demo-agentic-seo-optimization.md#step-3-implement-seo-fixes-from-the-baseline-audit) · [`box-stack/Caddyfile`](../02-ssh-deployment/box-stack/Caddyfile)
**Say:** Once a site is deployed there are two copies of every file, and the one you edit is not the one anyone measures. The check that counts comes from the deployed URL.

```text
2. Redeploy the box with the SSH loop, then navigate to the affected page in
   the browser against the deployed URL, never a local build
3. Confirm the rendered output matches the intended value using the
   chrome-devtools MCP (check the <title> tag and JSON-LD output)
...
For a Caddyfile fix, write the file in place on the box rather than moving a new
file over the name, reload the edge, and prove the served bytes changed with
curl -sI on the deployed URL.
```

**Result:** the pass closes with a TECHNICAL snapshot written under `.seo/YYYY-MM-DD/` (Step 3), beside the GENERAL baseline from beat 1; the copies it measures are the ones on the box under `/opt/box-stack/`.

**Gotcha:** a bind mount binds the inode, so `mv`-ing a new Caddyfile over the name leaves the old one served while `caddy validate` reports success.

### Beat 5: the threshold is the gate, and it runs after the deploy (1 min)

**Open:** [readme.md](readme.md#github-actions-web-vitals-collection) · [Step 2: Add a Lighthouse CI Workflow](demo-agentic-seo-optimization.md#step-2-add-a-lighthouse-ci-workflow)
**Say:** A metric that is reported is a dashboard; a metric that can fail a build is a control, and one severity setting is the difference. Measure through the edge or the number is one nobody receives.

```text
The job should:
1. Run after the SSH deploy job completes (use `needs:`)
2. Install @lhci/cli with npm install -g
3. Run lhci autorun --collect.url="https://${{ vars.APP_HOST }}/"
4. Assert LCP < 2500ms, TBT < 200ms, CLS < 0.1
5. Upload .lighthouseci/ as the artifact "lighthouse-results"
```

**Result:** `.lighthouserc.json` lands at the repository root and a `lighthouse` job joins [`.github/workflows/`](../../../.github/workflows) behind a `needs:` on the SSH deploy job (both written by Step 2)

```json
    "assert": {
      "preset": "lighthouse:recommended",
      "assertions": {
        "largest-contentful-paint": ["error", { "maxNumericValue": 2500 }],
        "total-blocking-time": ["error", { "maxNumericValue": 200 }],
        "cumulative-layout-shift": ["error", { "maxNumericValue": 0.1 }]
      }
    },
```

**Gotcha:** `error` rather than `warn` turns performance into a mandatory gate, and the three numbers are Google's "Good" thresholds.

## If the room asks

| Question | Answer |
|---|---|
| Why not audit a local build or the container port, which is quicker? | Compression, cache headers, HTTP/2 and TLS live in Caddy; on the throwaway box, port 8080 maps to Caddy's own 80, so that target does qualify. |
| Why will HTTPS, HTTP/2 and HSTS stay red locally? | A throwaway host has no publicly trusted certificate, so the local audit runs over HTTP; a real VM goes green with no source change. |
| Can Step 4 be presented rather than run? | Only in part: it needs a push, a real workflow run and a public hostname, so present the gate and leave the run to self-study. |
| Why is the concurrency group named after the box rather than the app? | Every deploy on one host shares the same Docker layer store, and two runs with one reaching `docker image prune -f` corrupt each other's layers. |
