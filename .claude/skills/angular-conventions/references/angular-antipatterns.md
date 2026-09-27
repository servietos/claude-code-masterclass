# Angular Anti-Patterns

Patterns that must not appear in Angular v22+ code.

| You want to... | Read |
|---|---|
| Is constructor DI, *ngIf/*ngFor/ngClass, @HostBinding, NgModule or CommonModule still allowed, and what replaces it? | [legacy-syntax](angular-antipatterns-legacy-syntax.md) |
| What replaces BehaviorSubject, subscribe() in ngOnInit, class-based NgRx reducers or jasmine.createSpyObj? | [state-data-testing](angular-antipatterns-state-data-testing.md) |
| NG0950 required-input error, or an @if block that renders nothing while the button toggling it still flips state. | [signal-inputs](angular-antipatterns-signal-inputs.md) |
| Removed @angular/material and @angular/cdk but it still looks like Material: what CSS and markup must also go? | [material-teardown](angular-antipatterns-material-teardown.md) |
| Neighbors shift when a spinner or status badge toggles, .sr-only text takes width, or a paused animation freezes mid-frame. | [constant-footprint-indicator](angular-antipatterns-constant-footprint-indicator.md) |
| Re-hosted a shared table or form and its rows look dead, selection is hard-pinned, or clicking a row shows no feedback. | [composition-wiring](angular-antipatterns-composition-wiring.md) |
| A button writes to the store correctly but the user sees nothing, and the bug disappears at wide layout widths. | [dead-control](angular-antipatterns-dead-control.md) |
