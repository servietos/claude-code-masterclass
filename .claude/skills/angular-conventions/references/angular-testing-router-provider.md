# NG0201 in a template that uses routerLink

## `provideRouter` for `routerLink` templates

`TestBed.createComponent` instantiates the component's template directives. A template using
`routerLink`/`routerLinkActive` fails with `NG0201: No provider found for ActivatedRoute` unless the
router is provided. Add `provideRouter([])`:

```typescript
import { provideRouter } from '@angular/router';

TestBed.configureTestingModule({
  providers: [
    provideRouter([]),
    { provide: SomeStore, useValue: storeMock },
  ],
});
```

For pure logic checks (method delegation, signal wiring), read `createComponent(X).componentInstance`
directly without `detectChanges()`: the constructor and field initializers still run.

Back to the index: [angular-testing](angular-testing.md)
