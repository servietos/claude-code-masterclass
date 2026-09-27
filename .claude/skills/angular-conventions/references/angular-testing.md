# Writing Angular specs with Vitest

Author unit tests for Angular components, services, guards and signals with Vitest and `TestBed`.

This leaf answers "how do I write a spec for this thing". Three siblings answer the other questions:

| Arrival question | Leaf |
| --- | --- |
| How do I run the suite, and why does the run look wrong? | [`angular-test-execution`](angular-test-execution.md) |
| Where are the coverage gaps and how do I close them? | [`angular-test-coverage`](angular-test-coverage.md) |
| The spec fails for a reason that is not the code under test | [`angular-test-doubles`](angular-test-doubles.md) |

| You want to... | Read |
| --- | --- |
| Component spec: where the `.spec.ts` goes and what to name it, TestBed setup, `setInput`, driving real DOM events. | [angular-testing-component](angular-testing-component.md) |
| The spec throws `NG0201: No provider found for ActivatedRoute`, or the template uses `routerLink` / `routerLinkActive`. | [angular-testing-router-provider](angular-testing-router-provider.md) |
| HTTP service spec, or a functional `CanActivateFn` / `CanMatchFn` guard that calls `inject()`. | [angular-testing-services-guards](angular-testing-services-guards.md) |
| Test a computed signal or effect with no TestBed, or code with timers and observables (`fakeAsync`, `tick`, `done`). | [angular-testing-signals-async](angular-testing-signals-async.md) |

Call `httpMock.verify()` in `afterEach` of **every** HTTP spec, not just the first one.
