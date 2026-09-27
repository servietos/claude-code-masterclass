# Replacing a paragraph with figures without losing facts

## Prose → figures, without losing facts

When replacing a paragraph with KPIs, **every fact in the paragraph must land somewhere.** The
paragraph usually contains two different things:

- **Quantities** → KPI tiles (count, total, rate, span, sources).
- **Scope statements** ("we include X, we deliberately exclude Y") → a two-column list with distinct
  markers, not another paragraph:

```html
<div class="scope">
  <div class="scope-col scope-col--in">   <p class="scope-h">In the record</p>          <ul class="scope-list">…</ul></div>
  <div class="scope-col scope-col--out">  <p class="scope-h">Deliberately excluded</p>  <ul class="scope-list">…</ul></div>
</div>
```

Use a glyph *and* a colour on the markers (`✓` green / `✕` red via `::before`), never colour alone —
colour-only meaning fails WCAG and fails for anyone printing the page.

Back to the index: [angular-page-chrome](angular-page-chrome.md)
