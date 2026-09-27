# Page rhythm: one eyebrow, one H1, no repeated tab label

## The rhythm

Every page in the set repeats the same four-part structure, in this order:

```
eyebrow + H1   ->   KPI band   ->   tab nav   ->   view (router-outlet)
```

Non-negotiable rules:

1. **Exactly one eyebrow and one H1 per page.**
2. **A tab label is the name of its section, so a view never repeats its own tab label as a heading.**
3. A view may carry an H2 only when it *says more* than its tab (`Conversation` → `Conversation record`
   is a near-echo and adds nothing; `Billing` → `Billing: engagement to date` earns its place).

### The "double headline" smell

The most common failure is promoting a panel into a tab but leaving the panel's own header behind:

```html
<!-- WRONG: two eyebrow+headline pairs stacked, ~120px apart -->
<section class="page-hero">
  <p class="eyebrow">Deployment · Green &amp; Blue</p>
  <h1>Where every app actually runs.</h1>
</section>
<app-infra-panel />   <!-- which itself renders: eyebrow "Infrastructure" + h2 "Fleet & Ports" -->
```

When a panel becomes a tab, **delete its header in the same change** — the tab label now carries it.
A panel that was designed as a standalone block almost always ships its own eyebrow, title and KPI
rail; all three move up to the page shell or disappear.

Back to the index: [angular-page-chrome](angular-page-chrome.md)
