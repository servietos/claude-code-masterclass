# KPI band markup, modifiers and grid rules

## KPI bands

A KPI band replaces explanatory prose with figures. Value first, then label, then a one-line
provenance sub-label:

```html
<ul class="page-kpis" aria-label="Engagement to date">
  @for (kpi of kpis(); track kpi.key) {
    <li class="page-kpi">
      <span class="page-kpi-value" [class.accent]="kpi.accent" [class.compact]="kpi.compact">{{ kpi.value }}</span>
      <span class="page-kpi-label">{{ kpi.label }}</span>
      <span class="page-kpi-sub">{{ kpi.sub }}</span>
    </li>
  }
</ul>
```

Three modifiers earn their keep:

| Modifier | Why |
| --- | --- |
| `--kpi-cols` custom property | One custom property drives the column count; media queries override the property (`6 → 3 → 2`) instead of restating `grid-template-columns` per breakpoint. |
| `.compact` on the value | Long values (a date range, a hostname) wrap to two lines and grow **every** tile in the row, because grid rows are equal height. A smaller font on just those tiles keeps the band one line tall. |
| `.page-kpis--sub` on the band | A view that carries its own figures under a page-level band needs one step less weight, or the two bands read as repetition instead of hierarchy. Same grammar, smaller value font, tighter padding. |

Always set `grid-template-columns: repeat(var(--kpi-cols), minmax(0, 1fr))` — `minmax(0, 1fr)` (not
`1fr`) is what stops a long unbroken value from blowing out the track.

Add `font-variant-numeric: tabular-nums` on the band so figures do not jitter between states.

Back to the index: [angular-page-chrome](angular-page-chrome.md)
