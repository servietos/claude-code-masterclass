# Column picker placement in the filter bar

## Placement

Put the trigger at the far right end of the existing filter bar, after the other
filter controls, with the same label-above-control treatment so its label lines up
with theirs:

```
[ SEARCH ................flexible............. ]  [ TYPE v ]  [ Columns v ]
```

The search field keeps absorbing the remaining width, the other filters keep their
natural width and shift left, and the picker is pinned right (`ml-auto`). Preserve
whatever `flex-col` / `sm:flex-row` stacking the bar already has.

A trigger button opening a checkbox list beats a right-click context menu here:
nothing signals that a context menu exists.

Back to the index: [angular-table-column-visibility](angular-table-column-visibility.md)
