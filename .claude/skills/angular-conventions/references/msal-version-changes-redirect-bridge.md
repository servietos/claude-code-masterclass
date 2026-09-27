# Redirect bridge: when it is needed

### The redirect bridge is OPTIONAL, do not add one by reflex

v5 added COOP support via a redirect bridge page, exposed as the subpath export `@azure/msal-browser/redirect-bridge` (visible in the package's `exports` map, `dist/redirect_bridge/index.mjs`). Its own doc comment: "Processes the authentication response from the redirect URL. For SSO and popup scenarios broadcasts it to the main frame. For redirect scenario navigates to the home page."

**Decision rule:**

| Your app | Bridge needed? |
| --- | --- |
| Redirect-only (`InteractionType.Redirect`, `loginRedirect`), path-based routing | **No.** Add nothing. |
| Hash-based routing (`withHashLocation()`) | **Yes, recommended.** Without it the auth response lands in the URL and collides with the hash router. |
| Popup or `ssoSilent` under COOP headers | **Yes.** |
| `logoutRedirect` | Optional. If present on the `postLogoutRedirectUri` page it returns the user to the origin. |

Confirm the precedent before adding one: `admin.integrations.at` runs msal-browser 5.18.0 with **no** bridge page (its `public/` holds only `favicon.ico`), because it is redirect-only with path routing. If you do add one, remember it must be a built file rather than an inline script when the CSP is `script-src 'self'`.

Back to the index: [msal-version-changes](msal-version-changes.md)
