# No ch measure caps on prose in a dashboard app

## Prose runs the full container width

**Do not put a `ch` measure cap on prose in a dashboard app.** No `max-width: 60ch` on a lede, no
`72ch` on an error paragraph, no `82ch` on a section intro. The "65 characters is optimal measure"
advice comes from article typography and does not apply to a wide operations UI, where the customer
reads a short sentence above a full-width grid and the cap just leaves a ragged column of dead space.

This recurs because it is the default instinct of whoever writes the next component's stylesheet.
One codebase accumulated nine of them, one per component, and each fix removed only the reported
instance. When you remove one, **grep the whole app** (`max-width:\s*\d+ch`) and remove them all.

Two categories are legitimate and must survive the sweep:

| Keep | Why |
| --- | --- |
| Identity chips (`.user-chip`, `.user-badge`, a name next to a logout button) | They pair `max-width` with `overflow: hidden; text-overflow: ellipsis` — the cap *is* the truncation mechanism |
| Headline caps (`h1 { max-width: 28ch }`) | A deliberate wrap decision about a display face, not a measure applied to body copy. Decide separately, do not sweep blind |

Back to the index: [angular-page-chrome](angular-page-chrome.md)
