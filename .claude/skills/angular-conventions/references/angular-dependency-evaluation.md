# Evaluating a Frontend Dependency Before Adopting It

Answer "is library X worth adding" with measured numbers, before a line of integration code is
written. Complements [`angular-bundle-optimization`](angular-bundle-optimization.md), which fixes a
budget that a dependency has *already* broken; this reference stops that from happening.

Four gates, in order. Any one of them can kill the candidate on its own, so run them cheapest
first. Never quote a size from memory or from bundlephobia.

| You want to... | Read |
| --- | --- |
| Is this package still maintained? Read version, publish date and weekly downloads when npmjs.com returns 403. | [registry-health](angular-dependency-evaluation-registry-health.md) |
| Considering an ngx-* or ng-* wrapper? Check the wrapper's health separately, or drop it and instantiate the library directly. | [wrapper-trap](angular-dependency-evaluation-wrapper-trap.md) |
| How big is the candidate and can the initial budget take it? Measure with esbuild+gzip, then decide eager vs lazy. | [bundle-weight](angular-dependency-evaluation-bundle-weight.md) |
| Will this editor or converter silently rewrite stored content? Run this before adopting anything with its own AST. | [format-fidelity](angular-dependency-evaluation-format-fidelity.md) |
| Gates are run: how do I report the call, and did I miss a step? The verdict format plus the eight-point audit. | [verdict-and-checklist](angular-dependency-evaluation-verdict-and-checklist.md) |
| Want a full run of all four gates with real numbers? The 2026-08-16 markdown-editor evaluation for admin.integrations.at. | [worked-example](angular-dependency-evaluation-worked-example.md) |
