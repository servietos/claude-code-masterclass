# Fitting or shortening visible text is a copy job

## Fitting text to one line is a copy job, not a CSS job

Asked to make five tile captions one-liners, an agent added `text-overflow: ellipsis` and shipped
`DNS löst den Namen zur festen I...` and `Feste IP, auf die alle Domains zei...`. Every caption fitted
on one line; none of them could be read. It satisfied the stated constraint exactly.

**Shorten the sentence** until it fits with room to spare. Never satisfy a length constraint on prose
with `text-overflow`, `white-space: nowrap`, or `-webkit-line-clamp`. Terse noun phrases are fine and
usually better: `DNS löst den Namen auf.`, `Feste IP für alle Domains.`

When delegating this, state the acceptance criterion as **"no ellipsis is rendered and no caption
wraps"**, not "make it fit on one line" — the second phrasing has a cheap wrong answer and an agent
will find it.

## Strip decoration from a badge, keep the noun

A badge is read out of context: away from the column header or the icon that would have supplied its
referent. `20` sitting next to a shield icon and four compliance pills means nothing; `Tests: 20`
means something. When an instruction says to shorten a label, remove the decoration (units, verbs,
`von 11 fehlgeschlagen`) and keep the noun that says what the number counts.

Back to the index: [angular-page-chrome](angular-page-chrome.md)
