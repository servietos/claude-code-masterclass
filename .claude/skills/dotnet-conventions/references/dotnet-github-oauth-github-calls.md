# GitHub OAuth: the two GitHub calls

## The two calls

**Start** — `POST https://github.com/login/device/code`, body `{ client_id, scope }`, header
`Accept: application/json`. Response: `device_code` (40 chars), `user_code` (8 chars w/ hyphen),
`verification_uri`, `expires_in` (~900s), `interval` (~5s). Scope example: `repo read:org`.

**Poll** — `POST https://github.com/login/oauth/access_token`, body
`{ client_id, device_code, grant_type }`, header `Accept: application/json`.
`grant_type` **must** be `urn:ietf:params:oauth:grant-type:device_code`. **No `client_secret`.**

```csharp
private const string GrantType = "urn:ietf:params:oauth:grant-type:device_code";

var req = new HttpRequestMessage(HttpMethod.Post, TokenUrl)
{
    Content = JsonContent.Create(new { client_id = ClientId, device_code = deviceCode, grant_type = GrantType }),
};
req.Headers.Accept.Add(new MediaTypeWithQualityHeaderValue("application/json"));
```

- `Accept: application/json` matters: GitHub's token endpoint returns **form-encoded** by default;
  with this header it returns JSON (`{ "access_token": ... }` or `{ "error": ... }`). GitHub accepts a
  JSON request body too (verified empirically) even though RFC/Entra examples use form-encoding.

Back to the index: [dotnet-github-oauth](dotnet-github-oauth.md)
