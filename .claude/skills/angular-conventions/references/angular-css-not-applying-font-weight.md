# Cause 5: the font file cannot honour the weight you declared

## Cause 5: the font file cannot honour the weight you declared

`font-weight: 300` against a font family that only ships a static 400 face does not error, does not warn,
and does not fall back visibly. The browser either renders 400 outright or synthesizes a faux-light, so
the heading looks *approximately* right in a screenshot while being a different weight than the one the
design calls for. Nothing in the build, the CSSOM or `getComputedStyle` disagrees with you:
`getComputedStyle(el).fontWeight` faithfully returns `300` because that is what the cascade resolved. It
says nothing about what was rasterized.

The same trap sits in `@font-face`. Declaring `font-weight: 100 900` over a static file is legal CSS and
the browser accepts the range without checking the file, so the declaration is not evidence either.

**The cheap check comes first, and it is a grep, not a measurement.** Before reaching for `fontTools` or
advance widths, list the faces the app actually loads for that family:

```bash
grep -n -A4 "font-family: *['\"]?Montserrat" src/<app>/src/styles.css | grep -n "font-weight"
```

A display family is routinely loaded at heading weights only (700/800/900 and nothing lighter). An element
set in that family renders at the nearest AVAILABLE weight, so `font-weight: 400` on it is a no-op and the
text stays bold no matter what the declaration says. This is the shape the failure takes in a real app: a
list view whose value cells already declared `font-weight: 400` and still rendered bold, because the cells
carried `font-family: var(--font-display)` and that family had no face below 700.

**When the family has no face at the weight you want, the fix is the family, not the weight.** Dropping the
display-font override so the element inherits the body family (which does ship 300-700) is the only edit
that changes what is rasterized; editing the number again changes nothing and reads in the diff as though
it should have. So when a weight declaration is already correct and the text is still bold, stop editing
the weight and go look at which family the element is in.

**Prove the face is variable before you declare a weight it might not have.**

The reliable check is the font's table directory: a variable font carries an `fvar` (font variations) table.

```bash
python -c "from fontTools.ttLib import TTFont; print(sorted(TTFont('font.woff2').keys()))"
```

`fonttools` (with `brotli` for WOFF2) is the correct tool. If it is not available, decode the table
directory by hand, and know the trap that makes the obvious shortcut lie:

- **A byte-grep for the literal string `fvar` in a WOFF2 finds nothing even when the table is present.**
  WOFF2 replaces each 4-byte tag with a one-byte flag whose low 6 bits index a fixed known-tags table
  (`fvar` is index 47, `gvar` 48, `avar` 39). Only tags absent from that table (index 63) are written out
  literally, which is why `STAT` and `HVAR` *do* show up in a raw grep. Finding `STAT` is a good hint the
  font is variable; not finding `fvar` is not evidence of anything.

The empirical proof needs no tooling at all and is the one to fall back on: **measure advance widths
across the weight axis in the live page.**

```js
const el = document.createElement('span');
el.style.cssText = 'position:absolute;visibility:hidden;white-space:pre;font-size:100px;font-family:"YourFamily"';
el.textContent = 'Handgloves 0123456789';
document.body.appendChild(el);
const out = {};
for (const w of [100, 200, 300, 400, 500, 600, 700, 800, 900]) {
  el.style.fontWeight = w;
  out[w] = Math.round(el.getBoundingClientRect().width * 100) / 100;
}
el.remove(); out;
```

| Widths look like | Meaning |
| --- | --- |
| Distinct and monotonically increasing across the range | A real variable face: the engine is interpolating |
| One value repeated, with a jump only at 700 | A single static face plus synthetic bold |
| Two or three clusters | Only the static faces actually loaded; every other weight snaps to the nearest |

Distinct monotonic widths are the only evidence that a declared weight is genuinely rendered. Take that
measurement before you write a weight into a design token, and before you report a typography change as
done, because a screenshot cannot tell the difference and neither can review.

Back to the index: [angular-css-not-applying](angular-css-not-applying.md)
