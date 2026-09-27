# .NET GitHub OAuth (Device Flow)

How to let a self-hosted ASP.NET Core service authenticate as a GitHub user — to clone private
repos and list the user's repositories — with **one click, no client secret, and no callback URL**.
Use the **OAuth device flow** (RFC 8628), not the web/redirect flow.

> **Validate against sources.** Cross-check the protocol against **GitHub docs** (Authorizing OAuth
> apps → Device flow) and **Microsoft Learn** (`microsoft-learn` MCP → "OAuth 2.0 device authorization
> grant", RFC 8628). Both agree on the rules below; the `slow_down` rule is the one implementations
> most often get wrong.

| You want to... | Read |
|---|---|
| Choosing between the device flow and the web/redirect flow for a self-hosted service or admin console. | [dotnet-github-oauth-flow-choice](dotnet-github-oauth-flow-choice.md) |
| Where does the device-flow Client ID belong, and why is it not a secret in .env or a compose env var? | [dotnet-github-oauth-client-id-config](dotnet-github-oauth-client-id-config.md) |
| What exactly do the start and token requests to github.com look like: body, grant_type, Accept header, response fields? | [dotnet-github-oauth-github-calls](dotnet-github-oauth-github-calls.md) |
| Writing the start/poll/repos endpoints, carrying device_code in the body not a cookie, and using the stored token to clone. | [dotnet-github-oauth-controller](dotnet-github-oauth-controller.md) |
| The UI hangs on "waiting" after the user authorized, or start returns device_flow_disabled: poll error map plus preflight checklist. | [dotnet-github-oauth-polling-backoff](dotnet-github-oauth-polling-backoff.md) |

- Honor `slow_down` (+5s) — otherwise infinite "waiting".
