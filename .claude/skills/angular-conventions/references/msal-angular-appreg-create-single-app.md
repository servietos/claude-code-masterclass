# Create one registration serving SPA and API

## Create a New App Registration from Scratch (single-app SPA + API)

One registration serves both the SPA and the protected API. Order matters: the scope must exist before it can be pre-authorized (two separate PATCH calls).

```bash
APP_ID=$(az ad app create --display-name "my-app" --sign-in-audience AzureADMyOrg --query appId -o tsv)
SCOPE_ID=$(python -c "import uuid; print(uuid.uuid4())")

az rest --method PATCH \
  --uri "https://graph.microsoft.com/v1.0/applications(appId='$APP_ID')" \
  --headers "Content-Type=application/json" \
  --body "{
    \"identifierUris\": [\"api://$APP_ID\"],
    \"spa\": { \"redirectUris\": [\"http://localhost:4200\"] },
    \"api\": {
      \"requestedAccessTokenVersion\": 2,
      \"oauth2PermissionScopes\": [{
        \"id\": \"$SCOPE_ID\",
        \"adminConsentDescription\": \"Access the API as the signed-in user\",
        \"adminConsentDisplayName\": \"Access the API\",
        \"userConsentDescription\": \"Access the API as you\",
        \"userConsentDisplayName\": \"Access the API\",
        \"isEnabled\": true, \"type\": \"User\", \"value\": \"access_as_user\"
      }]
    }
  }"

az rest --method PATCH \
  --uri "https://graph.microsoft.com/v1.0/applications(appId='$APP_ID')" \
  --headers "Content-Type=application/json" \
  --body "{ \"api\": { \"preAuthorizedApplications\": [{ \"appId\": \"$APP_ID\", \"delegatedPermissionIds\": [\"$SCOPE_ID\"] }] } }"

az ad sp create --id "$APP_ID"
```

Gotchas:

- `uuidgen` does not exist in git bash on Windows — use `python -c "import uuid; print(uuid.uuid4())"`. An empty `$SCOPE_ID` produces Graph errors `Cannot convert the literal '' to the expected type 'Edm.Guid'` and `Empty or null value specified in the 'delegatedPermissionIds' set`.
- Pre-authorizing the app for its own scope (second PATCH) skips the consent prompt entirely.
- `requestedAccessTokenVersion: 2` means the access token `aud` is the bare appId GUID — configure the API's `AzureAd:Audience` accordingly (an `api://GUID` audience causes `IDX10214`).
- Pass JSON bodies via a temp file (`--body @/tmp/body.json`) when quoting gets hairy in bash.

Back to the index: [msal-angular-appreg](msal-angular-appreg.md)
