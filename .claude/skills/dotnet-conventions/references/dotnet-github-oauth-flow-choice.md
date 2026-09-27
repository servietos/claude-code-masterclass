# GitHub OAuth: device flow vs web flow

## When to use device flow vs web flow

- **Device flow** — the operator registers **one** OAuth App once, ticks **Enable Device Flow**, and
  puts only its **public Client ID** in config. End users click "Sign in with GitHub", type a short
  code at `github.com/login/device`, and the server receives a token. No secret, no callback URL, no
  per-user or per-repo setup. This is the right default for a single-service / admin console.
- Web (redirect) flow needs a client **secret** and a registered **callback URL** — avoid it when a
  device flow will do; it pushes secret + redirect config onto every deployment.

Back to the index: [dotnet-github-oauth](dotnet-github-oauth.md)
