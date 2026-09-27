# Review step pickers show "No results": the missing route resolver

## Review step pickers show "No results"

- **The review step's entity selects need the resources loaded — resolve them on the host route.** The Objekt/Produkt pickers on step 2 read AppStore resource lists (`store.houseKeyValues` / `productKeyValues`, backed by `withResources`). Those are empty until `ResourcesService.loadAllResources()` runs, which only happens on a fresh login warm-up or via the `allResourcesResolver` wired onto the `planning`/`timesheet` route trees. If the wizard's host route (e.g. `/tasks/new` in `tasks.routes.ts`) does **not** wire `resolve: { resolved: allResourcesResolver }`, the `ux-filter-select` correctly renders **"No results"** — the picker isn't broken, its input array is just empty. Because it depends on whether the user already visited a resource-loading route, the bug reads as *intermittent* ("again the filter is broken with no data"). Fix: add the resolver to the route (see [`angular-routing`](angular-routing.md) → Resolvers).

Back to the index: [file-import-wiz](file-import-wiz.md)
