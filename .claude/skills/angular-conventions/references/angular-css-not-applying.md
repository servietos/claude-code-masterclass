# A CSS change that has no effect

Two failure modes look identical from the outside: you edit a stylesheet, the build goes green, the page
reloads, and the layout is unchanged. One is a CSS bug that fails silently; the other is a build that
never shipped your file. Tell them apart before editing anything else, because the fixes are opposite.

A green `ng build` proves the file compiles. It proves nothing about whether the rule matches.

| You want to... | Read |
| --- | --- |
| Start here: read the CSSOM to tell a stale bundle from a real CSS bug before editing anything. | [cssom-diagnosis](angular-css-not-applying-cssom-diagnosis.md) |
| The CSSOM shows the old declarations and hard reloads do nothing: ng serve is wedged, restart it. | [stale-dev-server](angular-css-not-applying-stale-dev-server.md) |
| An @container rule half-applies: children reflow but the parent keeps its base layout. | [container-query](angular-css-not-applying-container-query.md) |
| A Tailwind hover: or cursor- utility never applies on an element that also carries a hand-written global class. | [unlayered-global](angular-css-not-applying-unlayered-global.md) |
| Markup renders at UA defaults because the class was found in a sibling component's scoped CSS. | [component-scope](angular-css-not-applying-component-scope.md) |
| A wrapper's rule for its projected child never fires, so a bottom-aligned footer floats above the pane. | [projected-content](angular-css-not-applying-projected-content.md) |
| Text stays bold although font-weight is already 400, or you need to prove a face is really variable. | [font-weight](angular-css-not-applying-font-weight.md) |
| Only the deployed app is unstyled: inlineCritical plus a script-src CSP leaves the sheet on media=print. | [inline-critical-csp](angular-css-not-applying-inline-critical-csp.md) |
| After the fix: measure same-line, widths and the wrap threshold in-page instead of resizing the window. | [verify-reflow](angular-css-not-applying-verify-reflow.md) |
