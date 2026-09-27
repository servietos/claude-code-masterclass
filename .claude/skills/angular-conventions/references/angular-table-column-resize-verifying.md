# Verifying a resize change, and why geometry reads go stale

## Verifying

Geometry reads go stale. On this page `getBoundingClientRect` **and**
`offsetWidth` both returned a column at 347px and the wrapper overflowing by 196px
while a screenshot of the same moment showed the table fitting perfectly, with the
column at its correct 157px. Forcing a reflow (writing `scrollLeft`) made the reads
agree with the pixels.

So:

- **A screenshot is the ground truth.** Confirm the visual result first.
- If you need numbers, force a reflow before reading, and prefer a **behavioural**
  test to a geometry read: set `wrapper.scrollLeft = 999`, read it back, and set it
  to 0. A value of 0 proves there is no horizontal overflow; a non-zero value is
  the exact overflow. That cannot go stale the way a measured box can.
- Verify in the **same browser profile the user has**, with the storage keys
  removed. A different profile has different storage and a different window size,
  which is precisely how the two defects above passed an agent's own verification.

Check after any change: drag grows/shrinks and clamps at the minimum, the trailing
click does not sort, dblclick resets, arrows adjust, the width survives a reload,
and the flexible column never renders below its minimum in any visibility
combination.

Back to the index: [angular-table-column-resize](angular-table-column-resize.md)
