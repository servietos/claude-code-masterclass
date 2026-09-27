# Re-hosting a shared component without wiring its outputs

## Component Composition

| Wrong | Correct |
|---|---|
| Re-hosting a shared form/table pair but binding only inputs, hard-pinning selection (`entries()[0]`) | Diff the new host against the canonical host's template and wire every output too (`(selectEntry)`, `(entryChange)`) plus selection state |
| Selection without feedback (row click changes state but no visual) | Pass a `selectedId` input and render the `bg-surface-alt` selected style (voucher-list convention) |

Real case: `voucher-booking-wiz` embedded `voucher-edit-table` without `(selectEntry)` while `voucher-edit-container` binds it — booking lines looked dead ("details not editable").


Back to the index: [angular-antipatterns](angular-antipatterns.md)
