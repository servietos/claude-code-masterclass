# Testing a bottom sheet

## Testing

Follow `angular-testing.md`'s Vitest conventions. `jsdom` does not implement
`HTMLDialogElement.showModal`/`close`, so polyfill them in your test setup
(toggling the `open` attribute) — then `sheet().open()` / `sheet().close()` work
in specs without further mocking:

```typescript
it('opens and closes the sheet, returning focus to the trigger', async () => {
  const trigger: HTMLButtonElement = fixture.nativeElement.querySelector('button');
  trigger.focus();

  component.sheet().open();
  fixture.detectChanges();
  expect(fixture.nativeElement.querySelector('dialog').hasAttribute('open')).toBe(true);

  component.sheet().close();
  await new Promise((r) => setTimeout(r, 0));
  expect(document.activeElement).toBe(trigger);
});
```

Back to the index: [angular-bottom-sheet](angular-bottom-sheet.md)
