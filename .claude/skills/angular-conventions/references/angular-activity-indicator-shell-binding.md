# Binding the indicator in the shell

## 5. Bind the indicator in the shell

Bind global chrome to `store.isBusy()`. Zoneless + OnPush safe — it's a signal read.

This app's indicator is `app-gen-loader` (`src/ui/src/app/shared/gen-loader/`), a
"dot-wave" component ported from `rahimi-carpets`' carpet-visualizer, living in
the top-nav's right cluster (not the app shell root) so it sits directly next
to other status affordances (e.g. the cost entry point in
`shared/top-nav/top-nav.component.html`):

```html
<!-- shared/top-nav/top-nav.component.html -->
<app-gen-loader [active]="isBusy()" />
```

```ts
// shared/top-nav/top-nav.component.ts
isBusy = this.appStore.isBusy;
```

`app-gen-loader` is purely presentational (`active = input(false)`) — it
doesn't inject `AppStore` itself, so any host can drive it from whatever
signal represents "busy" for that surface. It stays mounted in the DOM at a
constant intrinsic width whether `active` is true or false (dim + paused when
idle, animating when active), so neighboring icons never jump when the busy
state toggles. Colors come from the brand tokens (`--color-brand` /
`--color-brand-deep`) per `bico-brand`, so it reads gold on the charcoal
top-nav (`bg-ink`).

The former `.app-loading-bar` (a thin fixed sweep bar pinned to the viewport
top, rendered from `app.component.html`) has been retired in favor of this —
do not reintroduce it; the dot-wave in the top-nav is now the single global
busy indicator.

Back to the index: [angular-activity-indicator](angular-activity-indicator.md)
