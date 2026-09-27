# router.url Carries the Query String

## Gotcha: `router.url` includes the query string, so exact-match route checks break on deep links

`router.url` and `NavigationEnd.urlAfterRedirects` carry the **full URL including `?query` and `#fragment`**. A route-derived `computed()` / `linkedSignal()` that decides behavior by **exact equality** on that value silently falls through the moment any query param is present:

```typescript
// current URL signal (from router.url / NavigationEnd)
private currentUrl = toSignal(/* … router.events → urlAfterRedirects … */, { initialValue: this.router.url });

// BUG: returns null as soon as the route is reached with a query param
mode = computed(() => {
  const url = this.currentUrl();
  if (url === '/orders')   return 'a';   // fails for '/orders?reopenId=16'
  if (url === '/invoices') return 'b';
  return null;                           // ← unintended fallback on any deep link
});
```

Symptom: a route-conditional feature works from a plain in-app navigation but **misbehaves when the same route is reached WITH a query param** — e.g. reopening a modal/wizard via `/orders?reopenId=16` picks the *wrong* variant because the exact match fails and a downstream `?? 'fallback'` kicks in. It looks like a state bug but it's the URL comparison.

Fix — strip query/fragment before an exact-equality compare, and keep exact equality (do NOT loosen to `startsWith`, which would wrongly match sub-routes like `/orders/123`):

```typescript
const url = this.currentUrl().split('?')[0].split('#')[0];
if (url === '/orders') return 'a';
```

Note: `startsWith` checks (e.g. auto-expand a nav group for a route tree) are already immune since the query suffix rides along harmlessly; it is **exact-equality** checks that are the trap. Read the query param itself via `ActivatedRoute.queryParamMap` (a flat object for the whole URL), not by parsing `router.url`.

Back to the index: [angular-routing](angular-routing.md)
