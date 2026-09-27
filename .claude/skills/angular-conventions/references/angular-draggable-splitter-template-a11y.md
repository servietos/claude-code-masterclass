# Splitter template and divider ARIA

## Template — content projection + accessible divider

Project the two panes by attribute selector; the divider is the accessible
`separator`.

```html
<div class="ux-splitter__pane ux-splitter__pane--left">
  <ng-content select="[slot-left]" />
</div>

<div
  class="ux-splitter__divider"
  [class.is-dragging]="dragging()"
  role="separator"
  aria-orientation="vertical"
  aria-label="Resize panels"
  [attr.aria-valuemin]="min()"
  [attr.aria-valuemax]="max()"
  [attr.aria-valuenow]="rightWidth()"
  tabindex="0"
  (pointerdown)="onPointerDown($event)"
  (pointermove)="onPointerMove($event)"
  (pointerup)="onPointerUp($event)"
  (pointercancel)="onPointerUp($event)"
  (keydown.arrowleft)="growRight(); $event.preventDefault()"
  (keydown.arrowright)="shrinkRight(); $event.preventDefault()"
></div>

<div class="ux-splitter__pane ux-splitter__pane--right">
  <ng-content select="[slot-right]" />
</div>
```

**Accessibility (WAI-ARIA `separator` with resize):** `role="separator"` +
`aria-orientation="vertical"` + `tabindex="0"` makes it focusable; keep
`aria-valuemin/max/now` bound to the live signal so screen readers announce the
size; Arrow Left/Right nudge by `step` (note the direction: when the *right* pane
resizes, ArrowLeft grows it). `$event.preventDefault()` stops the arrow keys from
scrolling.

## Accessibility

`role="separator"`, `aria-orientation="vertical"`, `tabindex="0"`, live
`[attr.aria-valuemin/max/now]="…"`, and `(keydown.arrowleft)="growRight()"` /
`(keydown.arrowright)="shrinkRight()"` (both `preventDefault()`). German aria-label
"Bereichsgröße anpassen".


Back to the index: [angular-draggable-splitter](angular-draggable-splitter.md)
