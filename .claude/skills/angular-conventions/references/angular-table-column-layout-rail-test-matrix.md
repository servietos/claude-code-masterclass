# Test matrix: orientations times rail states

This is the test matrix for the container-query conversion in [angular-table-column-layout-container-query](angular-table-column-layout-container-query.md).

### The matrix is orientations times rail states

Checking each viewport once measures one rail state and proves nothing about the
other. Toggle the rail with its own button (a real click), never by writing to
the store, so the rendered state is the one under test.

| viewport | rail | container | `.sl-ident` | name lines |
| --- | --- | --- | --- | --- |
| 1032 x 1376 | expanded | 704 | 224.0 | 2 |
| 1032 x 1376 | collapsed | 856 | 259.4 | 1 |
| 1376 x 1032 | expanded | 1014 | 338.4 | 1 |
| 1376 x 1032 | collapsed | 1166 | 414.4 | 1 |

Those two viewports are the iPad Pro 13" (1032 x 1376 portrait, 1376 x 1032
landscape). The older 12.9" is 1024 x 1366, and **1024 is the most common
breakpoint value there is**, so that device's portrait width lands exactly on
the boundary of a rule written without thinking about it. Test the boundary
value itself, not only the values either side.

Back to the index: [angular-table-column-layout](angular-table-column-layout.md)
