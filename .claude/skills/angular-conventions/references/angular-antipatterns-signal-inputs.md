# Required signal inputs and NG0950

## Signal inputs

| Wrong | Correct |
|---|---|
| Reading a required `input()` from a field initializer | Read it from `computed`, `linkedSignal`, `effect`, or a lifecycle hook |
| `signal({ x: this.someComputedOnInput() })` as a field | `linkedSignal({ source: () => this.input().id, computation: () => ({ ... }) })` |

Required inputs are not set until after construction, so touching one while instance fields initialize throws
**`NG0950: Input "x" is required but no value is available yet`**. The failure mode is nasty: the component
never constructs, so the enclosing `@if` renders *nothing* while the button that toggles it still flips state.
It reads as "the feature was never built" rather than as an error, and the only evidence is the console.

```ts
// WRONG: calls a computed that reads this.item() during field init
protected readonly model = signal<Form>({ title: this.defaultTitle(), body: '' });

// RIGHT: lazy, and re-derives only when the selected record actually changes
protected readonly model = linkedSignal<number, Form>({
  source: () => this.item().id,
  computation: () => ({ title: this.defaultTitle(), body: '' }),
});
```

Key the `source` on a stable id rather than the object itself: a re-emitted identical object would otherwise
reset the signal and wipe whatever the user had typed. `linkedSignal` stays writable, so Signal Forms can bind
to it directly.

Back to the index: [angular-antipatterns](angular-antipatterns.md)
