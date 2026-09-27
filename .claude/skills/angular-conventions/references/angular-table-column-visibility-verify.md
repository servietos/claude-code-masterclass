# Verifying the column picker

## Verifying

Same rules as the resize leaf: a screenshot is the ground truth, geometry reads go
stale, and a behavioural `scrollLeft` probe beats a measured box. Verify in the
user's own browser profile with the storage keys removed.

Check, at minimum:

- [ ] Default set renders with the hidden-by-default column off and no overflow.
- [ ] All columns on: no column below its minimum; excess becomes a scrollbar.
- [ ] Down to a single checked column: last checkbox disabled, table not empty.
- [ ] Toggle survives a reload; a wrong-version payload falls back to defaults.
- [ ] Explicit-on column stays visible below its breakpoint; untouched column still
      follows it.
- [ ] Two layers open, one ESC, only the top one closes; focus returns to the trigger.

Back to the index: [angular-table-column-visibility](angular-table-column-visibility.md)
