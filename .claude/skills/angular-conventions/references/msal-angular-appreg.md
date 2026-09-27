# MSAL Angular — App Registration Reference

> App registration in Azure AD (Entra ID) for SPA apps using MSAL Angular 22+ with PKCE auth code flow.

Creating, inspecting and fixing that registration, and the errors each setting produces.

**Always include ALL existing URIs — this call replaces the full list.**

| You want to... | Read |
|---|---|
| Need the client id, tenant id, scope or registered URIs for vouchers-ai or ct-member-db? | [known-apps](msal-angular-appreg-known-apps.md) |
| Creating a new registration from scratch where one app is both the SPA and the protected API? | [create-single-app](msal-angular-appreg-create-single-app.md) |
| Creating two registrations, an API that exposes the scope and a SPA that consumes it, via az CLI? | [create-api-plus-spa](msal-angular-appreg-create-api-plus-spa.md) |
| Adding, replacing or listing SPA redirect URIs, including the origin for a new staging environment? | [redirect-uris](msal-angular-appreg-redirect-uris.md) |
| Seeing redirect_uri_mismatch or AADSTS50011, or unsure whether a URI belongs under SPA or Web? | [redirect-uri-matching](msal-angular-appreg-redirect-uri-matching.md) |
| Blank page after login on https localhost, or AADSTS9002326 at the token exchange? | [localhost-port-trap](msal-angular-appreg-localhost-port-trap.md) |
| Verifying requestedAccessTokenVersion, platform and implicit grant before coding, or hitting Need admin approval? | [required-settings](msal-angular-appreg-required-settings.md) |
