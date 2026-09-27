# Fix part 1: pin the layout with table-fixed

## Fix, part 1: pin the layout

```html
<table class="w-full table-fixed text-sm">
```

`table-fixed` (CSS `table-layout: fixed`) makes column widths come from the
`<th>` widths and the table width only, never from cell content. Widths are then
computed once from the header row instead of being re-derived per page.

Consequences to handle, not optional:

- Overflow no longer auto-expands a column, so any cell whose content can exceed
  its width needs `truncate` (or an explicit wrap rule). Long emails and free-text
  date fields are the usual offenders. Prefer truncation with the full value still
  reachable through an existing expand-row control over a `title` tooltip.
- Responsive columns (`hidden lg:table-cell`, `hidden xl:table-cell`) keep working:
  a `display: none` column does not participate in the fixed layout at all.

Back to the index: [angular-table-column-layout](angular-table-column-layout.md)
