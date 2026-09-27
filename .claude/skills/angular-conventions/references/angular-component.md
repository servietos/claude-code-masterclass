# Angular Component

Create standalone components for Angular v20+. Components are standalone by default—do NOT set `standalone: true`.

Authoring one Angular component, end to end.

| You want to... | Read |
| --- | --- |
| Component file shape for v20+, and the ng generate commands | [anatomy](angular-component-anatomy.md) |
| Required/optional/aliased/transformed inputs, outputs, [(value)] two-way binding | [inputs-outputs](angular-component-inputs-outputs.md) |
| Class, style, attribute or event on the host (no @HostBinding/@HostListener); attribute directives | [host](angular-component-host.md) |
| @if/@for/@switch instead of *ngIf, [class.x]/[style.x] instead of ngClass/ngStyle, NgOptimizedImage | [template-syntax](angular-component-template-syntax.md) |
| Project content into named slots; reference an element, child component or projected child | [projection-queries](angular-component-projection-queries.md) |
| inject() instead of the constructor; ngOnInit, ngOnDestroy, afterRender, afterNextRender | [di-lifecycle](angular-component-di-lifecycle.md) |
| Pass AXE and WCAG AA: ARIA attributes, keyboard support, visible focus | [accessibility](angular-component-accessibility.md) |
| Parent/child data flow, and when shared state moves into a signal-based root service | [communication](angular-component-communication.md) |
| Lazy-load a heavy block, @defer triggers, what renders while loading or after failure | [defer-errors](angular-component-defer-errors.md) |
