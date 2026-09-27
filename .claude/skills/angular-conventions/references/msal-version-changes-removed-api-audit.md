# Pre-bump removed-API grep audit

### Removed-API audit checklist

Run these greps over `src/` before bumping. Each maps to a documented v5/v6 break:

| Check | Command | Why |
| --- | --- | --- |
| `protectedResourceMap` strict matching | `grep -rn "protectedResourceMap" src/` | v5 makes `strictMatching` the default. Bare base URLs stop matching subpaths, and the symptom is a 401 with **no** `Authorization` header. Keys need an explicit `/*` suffix. An app with no `MsalInterceptor` at all is unaffected. |
| Removed `logout()` | `grep -rn "\.logout(" src/` | Removed entirely; use `logoutRedirect()` / `logoutPopup()`. A local-only `instance.clearCache({ account })` sign-out is unaffected, it is a different API. |
| Removed config keys | `grep -rn "temporaryCacheLocation\|claimsBasedCachingEnabled\|storeAuthStateInCookie\|secureCookies\|cacheMigrationEnabled\|skipAuthorityMetadataCache\|supportsNestedAppAuth\|encodeExtraQueryParams" src/` | All dropped from `BrowserAuthOptions` / `CacheOptions` in v5. |
| Renamed system options | `grep -rn "asyncPopups\|iframeHashTimeout\|windowHashTimeout" src/` | `asyncPopups` became `navigatePopups` with **reversed** logic; the hash timeouts became `iframeBridgeTimeout` / `popupBridgeTimeout`. |
| Removed account getters | `grep -rn "getAccountByHomeId\|getAccountByLocalId\|getAccountByUsername" src/` | Replaced by `getAccount()` with a parameter object. |
| Request param consolidation | `grep -rn "authorizePostBodyParams\|tokenBodyParameters\|tokenQueryParameters" src/` | All fold into `extraParameters`. |

Surviving untouched across v4 to v6: `new PublicClientApplication(...)`, `getActiveAccount`, `getAllAccounts`, `setActiveAccount`, `clearCache`, `loginRedirect`, `EventType.LOGIN_SUCCESS` / `LOGOUT_SUCCESS`, and the `auth.*` / `cache.cacheLocation` / `system.allowPlatformBroker` config keys.

Back to the index: [msal-version-changes](msal-version-changes.md)
