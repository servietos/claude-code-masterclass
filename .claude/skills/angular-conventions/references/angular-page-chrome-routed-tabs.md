# Turning stacked sections into routed tabs

## Converting stacked sections into routed tabs

Prefer **child routes** over a local `signal()` for tab state: routes give deep links, working
browser back, and a shareable URL per view.

```ts
{
  path: 'deployment',
  loadComponent: () => import('./deployment-page').then((m) => m.DeploymentPage),
  canActivate: [authGuard],
  children: [
    { path: '', redirectTo: 'fleet', pathMatch: 'full' },
    { path: 'fleet', loadComponent: () => import('./infra-panel').then((m) => m.InfraPanel) },
    { path: 'graph', loadComponent: () => import('./graph-tab').then((m) => m.GraphTab) },
    { path: '**', redirectTo: 'fleet' },
  ],
}
```

Route straight to the existing standalone components; no wrapper component is needed. Keep the
`redirectTo` **and** the `**` fallback so a stale bookmark lands on the first tab instead of a blank
outlet.

Tab nav markup, with `ariaCurrentWhenActive` for assistive tech:

```html
<nav class="view-nav" aria-label="Views">
  @for (tab of tabs; track tab.path) {
    <a [routerLink]="tab.path" routerLinkActive="active"
       ariaCurrentWhenActive="page" [routerLinkActiveOptions]="linkMatch">{{ tab.label }}</a>
  }
</nav>
```

```ts
readonly linkMatch: IsActiveMatchOptions = {
  paths: 'exact', queryParams: 'subset', matrixParams: 'ignored', fragment: 'ignored',
};
```

### Reading the active tab in the shell

To show a per-tab lede without a wrapper component, derive it from navigation rather than injecting
route data:

```ts
private readonly url = toSignal(
  this.router.events.pipe(
    filter((e): e is NavigationEnd => e instanceof NavigationEnd),
    map((e) => e.urlAfterRedirects),
  ),
  { initialValue: this.router.url },
);

readonly activeTab = computed(
  () => this.tabs.find((t) => this.url().includes(`/deployment/${t.path}`)) ?? this.tabs[0],
);
```

`initialValue: this.router.url` matters: `NavigationEnd` has usually already fired by the time the
shell is constructed, so without it the first render has no active tab.

Back to the index: [angular-page-chrome](angular-page-chrome.md)
