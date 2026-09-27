# Renaming a Route Segment Safely

## Renaming a Route Segment

Renaming `/deployment` to `/operations` is **not** a one-line edit in the routes file. The old name
leaks into files the compiler will never connect to the route definition, and into visible copy that no
grep for `path:` will ever surface. Sweep all six categories before declaring it done.

| # | Where the old name hides | Symptom if missed |
| --- | --- | --- |
| 1 | `path:` in the route config | The route 404s (or hits the catch-all) |
| 2 | `routerLink` in templates | Dead nav link |
| 3 | **URL strings inside components** | Compiles and renders, but derived state is silently wrong |
| 4 | **Guards / resolvers building `UrlTree`s** | Redirect lands on the old, now nonexistent path |
| 5 | **Visible copy echoing the old name** | Page contradicts its own nav item |
| 6 | Docs, skills, READMEs, E2E specs | Stale instructions that outlive everyone's memory |

Category 5 is the one that gets discovered by the user rather than by you, one item at a time. The nav
link's own text is only the first tier: the same word typically also sits in the page eyebrow, in
section headings, and in tab labels, in three different files, none of which contain the URL at all.
Grepping the segment finds none of them, because the copy says `Deployment` while the route says
`/deployment`.

**So enumerate before editing.** Grep the bare *word*, case-insensitively, across templates and
component TypeScript, and put the full list of visible occurrences in front of the user up front:

```bash
grep -rni "deployment" --include="*.html" --include="*.ts" src/app | grep -v "\.spec\.ts"
```

Then ask which tiers should follow the rename, because they are genuinely independent decisions: a
section heading like `App Deployments` describes its *content* and may be better renamed to something
accurate rather than mechanically to the new nav word. Doing one tier and waiting to be told about the
next turns a single change into three round trips.

Categories 3 and 4 are the dangerous ones because nothing fails loudly. A tab shell that derives its
active tab from the URL is the classic case:

```ts
// Breaks silently on rename: builds fine, no tab ever matches, always falls back to tabs[0]
readonly activeTab = computed(
  () => this.tabs.find((tab) => this.url().includes(`/deployment/${tab.path}`)) ?? this.tabs[0],
);
```

Same for a guard that hardcodes the segment while building a redirect:

```ts
return router.createUrlTree([tab === 'graph' ? '/deployment' : '/dashboard'], { queryParams });
```

Find every occurrence before editing anything, and grep for the bare segment rather than only `path:`:

```bash
grep -rn "/deployment" --include="*.ts" --include="*.html" src/
```

### Keep the old URL working

Existing links, bookmarks, and anything already shared with a customer must not break. Add a legacy
alias, and use `pathMatch: 'prefix'` rather than `'full'`: a local (non-absolute) `redirectTo` with
prefix matching automatically carries the remaining segments over, so child routes forward too.

```ts
{ path: 'operations', /* ...the real route with its children... */ },

// Legacy alias: /deployment/fleet -> /operations/fleet, /deployment -> /operations
{ path: 'deployment', redirectTo: 'operations', pathMatch: 'prefix' },

{ path: '**', redirectTo: '' },   // aliases must come BEFORE the catch-all
```

With `pathMatch: 'full'` only the bare `/deployment` would redirect and every deep link would fall
through to the catch-all instead.

### Scope discipline

"Change the URL" means the URL. A route segment, the component file/folder, the class name, and the
nav label are four independent things that merely happen to share a word today. Rename only what was
asked: leaving `DeploymentPage` and `deployment.data.ts` untouched under an `/operations` URL is
correct, not an inconsistency to tidy up. Verify the result by loading both the new URL and the old
one, and confirm the active-state highlight still follows the route.
Back to the index: [angular-routing-patterns](angular-routing-patterns.md)
