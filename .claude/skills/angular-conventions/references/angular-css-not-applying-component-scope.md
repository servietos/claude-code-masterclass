# Cause 4: the class exists, but in another component's stylesheet

## Cause 4: the class exists, but in another component's stylesheet

Component styles are scoped by an `_ngcontent-*` attribute, so a class name is only global if it was
written in `styles.css`. Reusing a class you found in a sibling component's CSS produces no error, no
warning, and no styling: the element renders with the browser's defaults.

This one arrives most often through delegation. A prompt says "reuse the existing `.kv` row treatment",
the agent greps, finds `.kv` in `infra-panel.css`, uses the class name in a different component, and
reports the work as done. The build is green and every test passes, because neither has an opinion
about whether a rule matched.

The tell is UA-default rendering of semantic markup, which reads as "unfinished" rather than "broken":

```html
<!-- .kv / .kv-row live in another component's stylesheet, so this is an unstyled <dl> -->
<dl class="kv">
  <div class="kv-row"><dt>Datenbank</dt><dd>verbunden</dd></div>
</dl>
```

A bare `<dl>` renders `dt` as a block and indents `dd` by the UA's `margin-inline-start: 40px`, so
label and value stack instead of forming a two-column row and every row costs double the height. In a
height-constrained surface (a dialog capped at 50vh) that is the difference between fitting and not.

Diagnose with the CSSOM query above: the rule text **is** present in the page (the other component
shipped it), but its selector carries a different `_ngcontent` attribute than your element. Present in
the CSSOM, absent from `getComputedStyle`, is the signature.

Fix by deciding where the rule belongs:

1. **Copy the declarations into the consuming component's own stylesheet** when the treatment is local
   to that component. Set `margin: 0` on `dd` explicitly, since you are now overriding a UA default.
2. **Promote it to global `styles.css`** only when it is genuinely shared page chrome, knowing that
   reflavors every current and future user of the class.

When delegating, name the file a reusable rule lives in and state whether it is global or
component-scoped. "Reuse the existing X styling" without that is an instruction to copy a class name,
which is exactly the failure.

Back to the index: [angular-css-not-applying](angular-css-not-applying.md)
