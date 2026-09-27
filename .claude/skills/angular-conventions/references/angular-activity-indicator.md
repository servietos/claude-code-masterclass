# Angular Activity Indicator (store-driven, request-counted + explicit activity)

One global busy indicator driven by the signal store: an HTTP request counter plus an explicit `aiActive` flag, combined into a single `isBusy` signal, with its interceptor, its shell binding and its pitfalls split out below.

> Formerly "loading indicator" (`withLoading`/`isLoading`). Generalized to `withActivity`/`isBusy` so the same bar can signal AI activity, not just HTTP loading.

| You want to... | Read |
| --- | --- |
| Writing or composing the withActivity slice, or flagging non-HTTP work (an AI run, a long compute) as busy? | [angular-activity-indicator-store-feature](angular-activity-indicator-store-feature.md) |
| Wiring the HTTP counter, or MSAL bearer tokens stopped being injected after adding withInterceptors? | [angular-activity-indicator-interceptor](angular-activity-indicator-interceptor.md) |
| Where does the bar render, what is app-gen-loader, and why is the old .app-loading-bar gone? | [angular-activity-indicator-shell-binding](angular-activity-indicator-shell-binding.md) |
| Bar stuck on, neighbors jumping when busy toggles, dots frozen bright, polling trips the bar, or writing the test? | [angular-activity-indicator-pitfalls](angular-activity-indicator-pitfalls.md) |
