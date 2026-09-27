# NG0950: a Parent's :param Not Reaching a Child

#### A parent's `:param` needs `paramsInheritanceStrategy: 'always'` to reach a child input

`withComponentInputBinding()` alone is not enough when the `:param` is declared on a **parent** route
and consumed by a **child** component. Angular's default strategy is `emptyOnly`, which merges a
parent's params into a child only through path-less (empty-path) segments. Give the parent named
children and the merge stops: the child's `input.required<string>()` is never set and throws
`NG0950: Input "id" is required but no value is available yet` (see `angular-antipatterns.md` for the
other cause of that same error).

NG0950 is the loud version, and only a **required** input produces it. A plain `input<string>()` on the
same child simply stays at its default forever: no error, no console line, and a page that renders with
one field permanently empty. Check the strategy first whenever a child reads a parent's `:param` and
gets nothing, whether or not anything threw.

What makes it hard to spot is that the component worked before it moved:

```typescript
// worked: the param and the component sit on one route
{ path: 'projects/:id', loadComponent: () => import('./project-detail').then(m => m.ProjectDetail) }

// throws NG0950: :id is now on the parent, and 'draft' is not an empty path
{
  path: 'projects/:id',
  loadComponent: () => import('./project-shell').then(m => m.ProjectShell),
  children: [
    { path: 'draft', component: ProjectDraft },          // id = input.required<string>()
    { path: 'storyboard', component: ProjectStoryboard },
    { path: 'composition', component: ProjectComposition },
  ],
}
```

Fix it once in `provideRouter`, not by re-reading the param from `ActivatedRoute.parent` in every child:

```typescript
import { provideRouter, withComponentInputBinding, withRouterConfig } from '@angular/router';

provideRouter(
  routes,
  withComponentInputBinding(),
  withRouterConfig({ paramsInheritanceStrategy: 'always' }),
)
```

`withRouterConfig` takes one options object, so an app already passing it for `onSameUrlNavigation`
adds the key to that object rather than calling the feature twice.

**Proving it still holds**: route-test a child, never the shell. With the strategy set, navigate to
`/projects/42/draft` and assert the child renders `42`; then delete the `withRouterConfig` line and
re-run, and require NG0950. A test that passes both ways is asserting on the shell, which receives the
param either way.

Back to the index: [angular-routing](angular-routing.md)
