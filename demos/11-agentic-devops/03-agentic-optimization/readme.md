# Agentic Optimization: Web Vitals and SEO

This topic covers two automation loops that keep a deployed site fast and discoverable. The site is the one from [SSH Deployment](../02-ssh-deployment/readme.md): a container on the Ubuntu box, published to the internet by the Caddy edge. GitHub Actions collects Core Web Vitals against that hostname after every redeploy using Lighthouse CI, and feeds structured results back into the repository. Claude Code then drives the optimization loop: run the `agentic-seo` skill to audit the site, analyze the Vitals data alongside the SEO findings, implement targeted fixes, and verify the results with a follow-up audit.

## GitHub Actions Web Vitals Collection

Lighthouse CI runs after the deploy job and asserts minimum thresholds for LCP, TBT, and CLS on every push. The workflow uploads the JSON report as a build artifact so Claude Code can retrieve it with `gh run download` and reason over the raw numbers without visiting a browser.

The deploy job is the SSH loop from topic 02, so the audit measures exactly what the public sees, TLS and reverse proxy included:

```yaml
name: Deploy and Check Web Vitals
on:
  push:
    branches: [main]

concurrency:
  group: box-deploy
  cancel-in-progress: false

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Redeploy over SSH
        run: |
          install -m 600 -D /dev/stdin ~/.ssh/id_deploy <<< "${{ secrets.BOX_SSH_KEY }}"
          ssh -i ~/.ssh/id_deploy -o IdentitiesOnly=yes -o StrictHostKeyChecking=accept-new \
            ${{ secrets.BOX_USER }}@${{ secrets.BOX_HOST }} '
              cd /opt/box-stack
              docker compose pull app
              docker compose up -d app
              docker image prune -f'

  lighthouse:
    needs: deploy
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: '22'
      - run: npm install -g @lhci/cli
      - name: Run Lighthouse CI
        run: lhci autorun --collect.url="https://${{ vars.APP_HOST }}/"
      - uses: actions/upload-artifact@v4
        with:
          name: lighthouse-results
          path: .lighthouseci/
```

The `concurrency` group is named after the box rather than the app, because every deploy on one host shares the same Docker layer store. Two runs pulling at once, with one of them reaching `docker image prune -f` first, corrupt each other's layers.

The companion `.lighthouserc.json` declares the default target URL and the thresholds that the workflow asserts:

```json
{
  "ci": {
    "collect": {
      "url": ["https://app.example.at/"],
      "numberOfRuns": 3
    },
    "assert": {
      "preset": "lighthouse:recommended",
      "assertions": {
        "largest-contentful-paint": ["error", { "maxNumericValue": 2500 }],
        "total-blocking-time": ["error", { "maxNumericValue": 200 }],
        "cumulative-layout-shift": ["error", { "maxNumericValue": 0.1 }]
      }
    },
    "upload": {
      "target": "temporary-public-storage"
    }
  }
}
```

Example prompt to set up the Lighthouse CI workflow using the deployment agent:

```text
Use the deployment agent to add a Lighthouse CI job to the existing deploy
workflow, running after the SSH deploy job via needs:.

Requirements:
- Target https://${{ vars.APP_HOST }}/, the hostname Caddy serves, never the
  container port and never localhost
- Assert LCP < 2500ms, TBT < 200ms, CLS < 0.1
- Upload the .lighthouseci/ folder as an artifact named "lighthouse-results"
- Fail the workflow if any assertion fails
- Add a concurrency group named after the box, cancel-in-progress: false

Create .lighthouserc.json at the repo root with the URL placeholder
https://app.example.at/ so the user can fill in the real hostname.
```

Auditing the container port directly, or a local build, skips the edge entirely. Compression, cache headers, HTTP/2, and TLS negotiation all live in Caddy, so a run that bypasses it reports scores the public will never see.

## Where Caddy Owns the Fix

On a managed host the platform silently handled part of the Lighthouse report. On your own box it does not, which means a chunk of the audit backlog is now edge configuration rather than site source. Recognising which is which is what keeps the fix loop short.

| Lighthouse finding | Where the fix lives | What to change |
|---|---|---|
| Enable text compression | Caddyfile | `encode zstd gzip` inside the site block |
| Serve static assets with an efficient cache policy | Caddyfile | `header /assets/* Cache-Control "public, max-age=31536000, immutable"` on fingerprinted paths |
| Use HTTP/2, Uses HTTPS, HSTS | Caddyfile | Already supplied by automatic TLS; verify rather than add |
| Properly size images, defer offscreen images | Site source | Templates, layouts, and the build pipeline |
| Missing meta description, title, structured data | Site source | Front matter and templates, the `agentic-seo` territory |

Two mechanics matter when the fix lands in the Caddyfile. Write the file in place (`cat > /opt/box-stack/Caddyfile`), because a file bind mount binds the inode: `mv` a new file over the name and the container keeps serving the old one while `caddy validate` reports success. Then reload the edge and re-run the audit, since a passing config proves nothing about the served bytes.

```bash
docker compose exec caddy caddy reload --config /etc/caddy/Caddyfile
curl -sI https://app.example.at/ | grep -iE 'content-encoding|cache-control|alt-svc'
```

```powershell
docker compose exec caddy caddy reload --config /etc/caddy/Caddyfile
curl.exe -sI https://app.example.at/ | Select-String -Pattern 'content-encoding|cache-control|alt-svc'
```

## The agentic-seo Skill

The `agentic-seo` skill provides a complete SEO audit and optimization loop. It routes requests to the correct leaf skill: a general health audit, a technical runtime audit driven by browser inspection, on-page optimization (title tags, meta descriptions, JSON-LD schema), before/after snapshot comparison, and AI/GEO citation analysis. Load the skill by typing `/agentic-seo` and describe the scope of work.

For audit-only runs, the skill scores each dimension (Technical SEO, On-Page SEO, Content Quality, Authority) and writes a timestamped snapshot under `.seo/`. For optimization runs, it reads the audit findings and applies targeted fixes to templates, front matter, or layout files, then re-checks the affected routes in the browser to confirm the fix landed.

The two prompts below name several routes, which is the shape for a real content site. The site the demo deploys to the box is deliberately one static page, so scope the audit to that page and read these as the template you scale up to.

Example prompt to trigger a full audit:

```text
Run a full SEO audit using the agentic-seo skill against the deployed site,
through the Caddy edge rather than a local build. Audit the homepage, two
service pages, and the blog index. Score Technical SEO, On-Page SEO, Content
Quality, and Authority out of 10. Write the snapshot to .seo/ and update the
runs log.
```

Example prompt for a targeted optimization sprint:

```text
Read the latest .seo/ snapshot. The On-Page SEO score is below 7.
Fix the top three on-page issues: update the title tag and meta description
for the homepage, add a Course JSON-LD block to the training page, and fix
the H1/H2 hierarchy on the services page. After making changes, re-run
the technical audit on those three routes and confirm the fixes rendered.
```

## Connecting Vitals Data and SEO Work

The most productive pattern is to let the Lighthouse CI workflow surface regressions automatically, then hand the failing artifact to Claude for root-cause analysis and a targeted fix. Download the artifact, ask Claude to identify which template or asset caused the regression, implement the fix, and push; the next CI run confirms the threshold passes again.

```text
Download the latest "lighthouse-results" artifact from the most recent
failed workflow run using gh run download.

Read the JSON report and identify which metric failed and on which URL.
Trace the LCP regression to the specific image, script, or CSS block
responsible using the chrome-devtools MCP to inspect the live page.
State whether the fix belongs in the site source or in the Caddyfile before
implementing it, and verify the LCP drops below 2500ms in the browser
against the live hostname before pushing.
```

## Helpful Claude Slash Commands

| Command | Usage |
|---|---|
| `/agentic-seo` | Run a full SEO audit or targeted optimization pass on the current project |
| `/mcp` | Confirm the `chrome-devtools` MCP server is connected before auditing the live hostname |
| `/security-review` | Audit the deploy workflow for SSH key exposure and permission scope |
| `/review` | Review SEO, Caddyfile, and performance changes before pushing to the deploy branch |

## Key Topics covered in this module

- [Lighthouse CI documentation](https://github.com/GoogleChrome/lighthouse-ci/blob/main/docs/getting-started.md)
- [Core Web Vitals thresholds](https://web.dev/articles/vitals)
- [Caddy `encode` directive](https://caddyserver.com/docs/caddyfile/directives/encode): the one-line fix for the text-compression audit
- [Caddy `header` directive](https://caddyserver.com/docs/caddyfile/directives/header): cache-control headers for the efficient-cache-policy audit
- [GitHub Actions artifact upload and download](https://docs.github.com/en/actions/writing-workflows/choosing-what-your-workflow-does/storing-and-sharing-data-from-a-workflow)
- [Claude Code Sub-Agents](https://code.claude.com/docs/en/sub-agents)
- [Structured data (JSON-LD) reference](https://developers.google.com/search/docs/appearance/structured-data/intro-structured-data)
- [Google Search Console Core Web Vitals report](https://support.google.com/webmasters/answer/9205520)
