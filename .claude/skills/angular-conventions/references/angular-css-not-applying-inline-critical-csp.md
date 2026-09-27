# Cause 6: the production build inlined critical CSS and the CSP blocked it

## Cause 6: the production build inlined critical CSS and the CSP blocked it

This one only appears **after deploying**. Local `ng serve` looks perfect, the production build is green,
and the deployed app renders with no styling at all: raw stacked text, no colours, no layout.

With `optimization.styles.inlineCritical` on (the default in a production configuration), the Angular
build rewrites the stylesheet link into a deferred load:

```html
<link rel="stylesheet" href="styles-XXXX.css" media="print" onload="this.media='all'">
```

The sheet is fetched but applies to `print` only until that inline `onload` handler flips `media`. Under a
`Content-Security-Policy` with `script-src 'self'` and no `'unsafe-inline'`, the browser refuses to run the
handler, `media` never flips, and the entire stylesheet stays inert. There is no build error and no failed
request: the CSS downloads with a 200 and simply never applies.

```jsonc
// angular.json → architect.build.configurations.production
"optimization": {
  "scripts": true,
  "fonts": true,
  "styles": { "minify": true, "inlineCritical": false }
}
```

Set it before the first deploy of any SPA that ships its own CSP, which is every container image whose
nginx or Caddy config sets security headers. Confirm it from the deployed page rather than the build log:

```js
[...document.querySelectorAll('link[rel=stylesheet]')].map(l => [l.href, l.media])
```

Any row whose media is still `print` is this bug. A console entry about a blocked inline event handler is
the corroborating signal, and it is easy to miss among CSP noise.

Back to the index: [angular-css-not-applying](angular-css-not-applying.md)
