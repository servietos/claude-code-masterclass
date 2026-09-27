# Angular HTTP: Sentinel Infinite-Scroll Traps

Troubleshooting for the sentinel variant of the infinite-scroll pattern.

### Sentinel-driven infinite scroll: three traps that all look identical

Swapping the "Load More" button for an `IntersectionObserver` sentinel introduces three failure modes that
present the same way (nothing ever loads) and stack on top of each other. Rule them out in this order.

**1. The sentinel has zero area.** An empty `<div #sentinel>` collapses to height 0, and IntersectionObserver
reports an empty intersection rect for a zero-area target, so it never intersects even when scrolled fully
into view. Give it real height and pre-load before the exact bottom:

```ts
this.observer = new IntersectionObserver(
  (entries) => { if (entries.some(e => e.isIntersecting)) this.maybeLoadMore(); },
  { rootMargin: '300px' },
);
```
```html
<div #sentinel aria-hidden="true" class="h-4"></div>
```

**2. Nothing on the page actually scrolls.** If the app shell already owns the scroll container, a feature root
of `h-full` is pinned to that height and its card's `overflow-hidden` clips the rows instead of overflowing, so
`scrollHeight === clientHeight` and the sentinel is unreachable. Feature roots must not set `h-full`. Diagnose:

```js
[...document.querySelectorAll('*')].filter(el =>
  el.scrollHeight > el.clientHeight + 20 &&
  ['auto','scroll','overlay'].includes(getComputedStyle(el).overflowY))   // empty array = nothing scrolls
```

**3. You are verifying in a tab that is not being rendered.** A browser-automation tab commonly reports
`document.visibilityState === "hidden"`, and a non-rendered tab never delivers intersections. Setting
`scrollTop` from JS will load nothing, and even an independently attached probe observer fires zero times,
while screenshots still work and make the page look live. Verify with the automation tool's *real* scroll
input, and check `document.visibilityState` before concluding the observer is broken.

Also keep sorting and paging on the same side. Once paging is server-side, a client-side sort only reorders
the rows already fetched while looking like a full sort. Move sorting to the server or remove the affordance.

Back to the index: [angular-http-patterns](angular-http-patterns.md)
