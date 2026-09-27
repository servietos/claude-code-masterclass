# Activity interceptor and its registration

## 2. The functional interceptor (HTTP side)

```ts
// store/activity.interceptor.ts
export const activityInterceptor: HttpInterceptorFn = (req, next) => {
  const store = inject(AppStore);
  store.requestStarted();
  return next(req).pipe(finalize(() => store.requestFinished()));
};
```

`finalize` fires on success, error, **and** cancellation, so the counter never leaks.

## 3. Registration — the `withInterceptorsFromDi` coexistence gotcha

This app already registers MSAL's interceptor via **DI** (`withInterceptorsFromDi()`). Add the functional activity interceptor with `withInterceptors([...])` **alongside** it — do not replace the DI form or MSAL bearer-token injection breaks:

```ts
// app.config.ts
provideHttpClient(
  withInterceptorsFromDi(),           // keep — MSAL
  withInterceptors([activityInterceptor]),
  withFetch(),
),
```

Back to the index: [angular-activity-indicator](angular-activity-indicator.md)
