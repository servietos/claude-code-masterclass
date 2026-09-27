# Bumping a test-environment major (jsdom)

## 4. Test-environment majors: gate on the Node floor and on what the tests assert

### 4. Test-environment majors: gate on the Node floor and on what the tests assert

jsdom 28 to 30 crosses two majors. Both breaking changes were Node engine bumps:

```bash
npm view jsdom@30.0.1 engines --json   # {"node":"^22.22.2 || ^24.15.0 || >=26.0.0"}
node --version                         # must satisfy it, and so must CI and Docker
```

The real risk is not the engine but the behaviour your tests depend on. jsdom 29 replaced the entire CSSOM implementation and 30 changed `getComputedStyle()` to return pixels, so the deciding check was whether anything asserts on computed style:

```bash
grep -rn "getComputedStyle\|computedStyle" src/
```

Zero hits made the bump safe, and the full suite passing on the new version confirmed it. **Rule: for a test-env dependency, identify which behaviour the majors changed, grep for tests that depend on it, then let the suite decide.** Note that raising the floor to `^24.15.0` means a contributor on 24.14 now sees `EBADENGINE`; that is advisory only unless an `.npmrc` sets `engine-strict`, so check for one.

Back to the index: [angular-update](angular-update.md)
