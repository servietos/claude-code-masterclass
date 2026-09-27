# Check the type ladder when unifying headings

## Check the type ladder when unifying headings

Unifying headline styles reliably exposes an inverted scale. Measure the computed sizes before
declaring the system consistent:

| Level | Treatment |
| --- | --- |
| H1 (page hero) | uppercase display, `clamp(24px, 3.2vw, 40px)` |
| H2 (view heading) | uppercase display, `clamp(19px, 2.1vw, 27px)` |
| H3 (block heading) | uppercase display, `15px`, `letter-spacing: .06em` |

A real case: the H3 helper class was `clamp(20px, 2.4vw, 26px)` while the H2 class was
`clamp(22px, 2.6vw, 32px)` — at most viewport widths the H3 rendered as large as the H2, so the page
had no hierarchy at all. Sentence-case vs uppercase hid it until both were made uppercase.

Likewise, when two components render "the same" tile with different internal order (value-then-label
vs label-then-value from a `<dl>`), align the **surface** — radius, padding, font sizes, borders — and
accept the order difference where the markup semantics require it (`<dt>` must precede `<dd>`).

Back to the index: [angular-page-chrome](angular-page-chrome.md)
