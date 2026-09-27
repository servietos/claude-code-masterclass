# MSAL Angular — Troubleshooting

Every failure mode of an MSAL Angular SPA in one place: what the symptom means, where the fault sits, and the fix. Read this when auth is wired but misbehaving.

| You want to... | Read |
|---|---|
| The API returns 401: is the token missing or rejected, and the five checks from Authorization header to protectedResourceMap wildcard. | [msal-troubleshooting-401](msal-troubleshooting-401.md) |
| Look up a symptom (blank page, missing Authorization header, redirect loop, AADSTS50011, logout account picker) and its one-line fix. | [msal-troubleshooting-symptom-table](msal-troubleshooting-symptom-table.md) |
| Auth hangs or loops right after a config choice: popup flow, Easy Auth alongside MSAL, or a hand-rolled token interceptor. | [msal-troubleshooting-forbidden-setups](msal-troubleshooting-forbidden-setups.md) |
| Running locally with authEnabled: false, or the whole app shell renders blank once auth is switched off. | [msal-troubleshooting-debug-auth-mode](msal-troubleshooting-debug-auth-mode.md) |

**App Service Easy Auth and `Microsoft.Identity.Web` must never coexist.**
