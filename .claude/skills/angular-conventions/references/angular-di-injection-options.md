# Injection Options: optional, self, skipSelf, host

## Injection Options

### Optional Injection

```typescript
@Component({...})
export class My {
  // Returns null if not provided
  private analytics = inject(Analytics, { optional: true });
  
  trackEvent(name: string) {
    this.analytics?.track(name);
  }
}
```

### Self, SkipSelf, Host

```typescript
@Component({
  providers: [Local],
})
export class Parent {
  // Only look in this component's injector
  private local = inject(Local, { self: true });
}

@Component({...})
export class Child {
  // Skip this component, look in parent
  private parentService = inject(ParentSvc, { skipSelf: true });

  // Only look up to host component
  private hostService = inject(Host, { host: true });
}
```

Back to the index: [angular-di](angular-di.md)
