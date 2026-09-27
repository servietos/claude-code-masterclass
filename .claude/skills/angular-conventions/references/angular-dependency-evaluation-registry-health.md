# Gate 1: package health from the npm registry API

## Gate 1 — Health, from the registry API and not the website

`WebFetch` on `npmjs.com/package/<name>` returns **HTTP 403**. Do not conclude the package is
missing; use the registry and downloads APIs, which are open:

```bash
for p in "@milkdown/crepe" "@toast-ui/editor" "@codemirror/lang-markdown"; do
  enc=$(echo "$p" | sed 's|/|%2F|')
  echo -n "$p :: "
  curl -s "https://registry.npmjs.org/$enc" \
    | python -c "import sys,json;d=json.load(sys.stdin);v=d['dist-tags']['latest'];print(v,d['time'][v],d['versions'][v].get('license'))"
  echo -n "   weekly :: "
  curl -s "https://api.npmjs.org/downloads/point/last-week/$enc" \
    | python -c "import sys,json;print(json.load(sys.stdin).get('downloads'))"
done
```

Read three fields and stop: **latest version**, **publish date of that version**, **weekly
downloads**. Publish date is the maintenance signal; downloads alone are not, because a dead
package coasts on transitive installs for years (`@toast-ui/editor`: 227k downloads a week, last
release February 2023).

Also check `dist-tags`: a package whose `latest` is stale but which has a newer `beta` is a
project that stalled mid-rewrite, not a maintained one.

Never report health from a blog post, an aggregator score, or a search summary. Those lag and
they average across a scope you did not choose. Query the registry.

Back to the index: [angular-dependency-evaluation](angular-dependency-evaluation.md)
