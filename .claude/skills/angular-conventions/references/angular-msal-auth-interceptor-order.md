# Interceptor order with a base-URL rewrite

### Interceptor ordering when combined with a base-URL rewrite interceptor

If you issue relative URLs (`http.get('/api/inventory')`) and rely on a functional interceptor to prefix `environment.apiUrl`, that rewrite MUST run before `MsalInterceptor` sees the request — otherwise MSAL matches the relative URL against `window.location.origin` (the SPA host, not the API host) and never matches the map. With `provideHttpClient(withInterceptors([apiBaseInterceptor]), withInterceptorsFromDi())` the functional interceptor is registered first, so it runs first — correct. The robust alternative (used by the vouchers-ai reference app) is to issue absolute `${environment.apiUrl}/api/...` URLs at the call site so MSAL always sees the final URL regardless of interceptor order.

Back to the index: [angular-msal-auth](angular-msal-auth.md)
