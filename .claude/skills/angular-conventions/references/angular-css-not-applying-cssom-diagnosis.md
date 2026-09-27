# Diagnose first: is the rule even in the page?

## Diagnose first: is the rule even in the page?

Read the CSSOM. It is the only ground truth for "did my edit actually reach the browser" — the file on
disk, a green build, and a hard reload all lie about this.

```js
let hits = [];
for (const ss of document.styleSheets) {
  let rules; try { rules = ss.cssRules } catch (e) { continue }   // cross-origin sheets throw
  for (const r of rules) if ((r.cssText || '').includes('.my-selector')) hits.push(r.cssText);
}
hits;
```

Then compare the served rule text against the file:

| CSSOM shows | Meaning | Fix |
| --- | --- | --- |
| The **old** declarations | The dev server is serving a stale bundle | Restart the dev server (below) |
| The **new** declarations, but `getComputedStyle` disagrees with them | A real CSS bug — specificity, cascade, or a rule that cannot match | Fix the CSS (below) |
| The rule is absent entirely | Wrong component scope, or the file is not imported | Check `styleUrl` / the selector's `_ngcontent` scope |

Pair it with the computed value of the property you are fighting:

```js
getComputedStyle(document.querySelector('.my-selector')).flexDirection
```

A green `ng build` proves the file compiles. It proves nothing about whether the rule matches.

Back to the index: [angular-css-not-applying](angular-css-not-applying.md)
