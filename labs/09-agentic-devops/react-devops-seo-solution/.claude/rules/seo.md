# SEO site facts

- Source folder: the project root. The only HTML template is `index.html`; the React app mounts into `#root`.
- Audited host: `https://app.box.test:8443/`, the Caddy edge on the Ubuntu box from Lab 01. Auditing the deployed URL is intended here; there is no local preview.
- Routes: `/` (the single-page app) and `/healthz` (plain text, answered by Caddy). Every other path returns the app shell through the nginx SPA fallback.
- Title suffix: none. Gated apps: none.
- Layers: the site source builds into the `web` container (nginx). The `Caddyfile` on the box at `/opt/react-devops/Caddyfile` owns compression, cache headers, HTTP/2 and TLS.
- Not on this site and not findings: sitemap, blog, services pages, authority signals, multi-language alternates.
