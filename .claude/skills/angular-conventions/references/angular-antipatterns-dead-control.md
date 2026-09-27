# A control whose feedback panel is not in the DOM

## A control whose only feedback lives in a conditionally-rendered panel

```html
@if (wideLayout() || activeTab() === 'preview') {
  <app-preview [media]="store.selected()" />
}
```

```html
<button (click)="store.select(item)">...</button>
```

Clicking the button updates the store correctly and the user sees nothing, because the element that would show the change is not in the DOM. The default tab is the other one. Every part of the data path works and the control reads as dead.

- A `@if` on a tab, a disclosure or a breakpoint removes the output element, so a correct signal write has nowhere to land. `@if` is not `[hidden]`: there is no element to inspect and no transition to notice.
- Any control whose only feedback lives in a conditionally-rendered panel must bring that panel forward when it fires. Emit from the control, and let the shell switch the tab or open the panel.
- Diagnose it the same way: before tracing the handler or the store, click the control in the running page and read back both the state and whether the output element exists. `document.querySelector('[data-testid="..."]')` returning null is the answer, not the state being wrong.
- The wide-layout arm of the condition hides the bug on your machine: at a width where both panels render, the same click looks fine.
Back to the index: [angular-antipatterns](angular-antipatterns.md)
