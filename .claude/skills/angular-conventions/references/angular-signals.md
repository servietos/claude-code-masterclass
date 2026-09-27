# Angular Signals

Signals are Angular's reactive primitive for state management. They provide synchronous, fine-grained reactivity. Pick the leaf that matches your question.

| You want to... | Read |
| --- | --- |
| What do signal(), computed() and linkedSignal() do, and how do I stop a write from firing when only an unrelated field changed? | [primitives](angular-signals-primitives.md) |
| How do I run a side effect when a signal changes, clean it up, exclude a signal from tracking, or log state changes? | [effects](angular-signals-effects.md) |
| Endless identical HTTP requests after a component with an effect() mounts, or a zoneless browser hang, while the effect's named deps never change. | [effect-loops](angular-signals-effect-loops.md) |
| How does a component hold its own state, derived state and actions with signals? Full TodoList worked example. | [component-state](angular-signals-component-state.md) |
| How do I turn an Observable into a signal, or a signal into an Observable so RxJS operators can run on it? | [rxjs-interop](angular-signals-rxjs-interop.md) |
| Where does shared state live: a service with private writable plus public readonly signals, or a full single-state-object store with selectors and actions? | [service-store](angular-signals-service-store.md) |
| How do I fetch async data with signals, read its loading/error status, give it a default value, or skip loading until a param exists? | [resource](angular-signals-resource.md) |
| How do I build a form field with signals carrying value, touched, dirty, validators, errors and reset? | [forms](angular-signals-forms.md) |
| How do I debounce a search box driven by a signal, or apply an update immediately and roll it back when the request fails? | [async](angular-signals-async.md) |
| How do I test a component's signals and computeds, or a signal store's selectors, with TestBed and HttpTestingController? | [testing](angular-signals-testing.md) |

**Rule:** read your intended dependency signals explicitly at the top of the effect, then wrap any side-effecting call (anything that issues HTTP or otherwise touches shared store signals) in `untracked()`:
