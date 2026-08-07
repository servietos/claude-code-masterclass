# Review Run 01 (pre-patch skill)

Target: `fixtures/discount.ts`, a new untracked file in the working tree.

Gathering step actually executed, following `SKILL.md` section 2 "For Local Changes":

```bash
git status --porcelain
git diff -- demos/03-skills/05-test-and-package | wc -l        # 0
git diff --staged -- demos/03-skills/05-test-and-package | wc -l # 0
```

`git status` listed the folder as `??`; both diff commands returned zero lines, so the file content had to be read directly. That gap is recorded in `functional-results.md` as property F0.

## Review output produced by the skill

### Summary

One new file introduces a percentage discount helper and a sync call that talks to a remote endpoint. The math is compact but unguarded, and the file carries a live-looking credential.

### Findings

**Critical**

- `fixtures/discount.ts:1` - a bearer token is hardcoded as a module constant (`sk-live-4f9c21ab7d0e`). Anything importing this module ships the secret into the bundle, and rotating it means a code change plus a redeploy. Move it to an injected config value or an environment variable.
- `fixtures/discount.ts:4` - `100 / percent` is unguarded. `percent = 0` does not throw in TypeScript; it yields `Infinity`, so `applyDiscount(100, 0)` returns `0` and the caller silently charges nothing. Verified by running the function: `applyDiscount(100, 0) = 0`. Validate the input range before dividing.

**Improvements**

- `fixtures/discount.ts:3` - the name says "apply discount" but the function returns the discount amount, not the discounted price: `applyDiscount(100, 10)` returns `10`. Rename it or return `price - amount`, because a caller reading the signature will get this backwards.
- `fixtures/discount.ts:8` - `syncDiscounts` returns the raw `Response` without checking `response.ok`, so a 401 from an expired token reaches the caller as a resolved promise.

**Nitpicks**

- `fixtures/discount.ts:4` - `factor` is an indirection over `percent / 100`; dividing by a reciprocal makes the intent harder to read than multiplying.

### Conclusion

Request Changes. The hardcoded credential alone blocks merge.
