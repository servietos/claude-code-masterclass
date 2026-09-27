# View and add SPA redirect URIs

## View Current SPA Redirect URIs

```bash
az ad app show \
  --id 54f03c51-f41a-4f1f-97ca-d219ee28ee50 \
  --query "{spa:spa.redirectUris, web:web.redirectUris}" \
  -o json
```

---

## Add a SPA Redirect URI

Azure CLI has no `--spa-redirect-uris` flag. Use `az rest` to PATCH via MS Graph.
**Always include ALL existing URIs — this call replaces the full list.**

```bash
az rest \
  --method PATCH \
  --uri "https://graph.microsoft.com/v1.0/applications(appId='54f03c51-f41a-4f1f-97ca-d219ee28ee50')" \
  --headers "Content-Type=application/json" \
  --body '{
    "spa": {
      "redirectUris": [
        "https://vouchersai.integrations.at/",
        "https://zealous-bay-02ad9c603.7.azurestaticapps.net/",
        "http://localhost:4200",
        "http://localhost:4200/NEW-URI-HERE"
      ]
    }
  }'
```

Verify after:

```bash
az ad app show \
  --id 54f03c51-f41a-4f1f-97ca-d219ee28ee50 \
  --query "spa.redirectUris" \
  -o json
```

---

## Adding a New Environment (e.g., staging)

When deploying a new environment, add its origin to the SPA redirect URIs before deploying:

```bash
az rest \
  --method PATCH \
  --uri "https://graph.microsoft.com/v1.0/applications(appId='54f03c51-f41a-4f1f-97ca-d219ee28ee50')" \
  --headers "Content-Type=application/json" \
  --body '{
    "spa": {
      "redirectUris": [
        "https://vouchersai.integrations.at/",
        "https://zealous-bay-02ad9c603.7.azurestaticapps.net/",
        "http://localhost:4200",
        "https://NEW-STAGING-URL.azurestaticapps.net/"
      ]
    }
  }'
```

Back to the index: [msal-angular-appreg](msal-angular-appreg.md)
