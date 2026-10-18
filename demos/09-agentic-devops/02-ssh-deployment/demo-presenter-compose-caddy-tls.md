---
presents: demo-compose-caddy-tls.md
budget: 4 min
beats: 4
---

# Present: Ship the App with Compose, Caddy and TLS

An application goes behind one public edge, and the certificate request is a gate you check before you run it. Four beats: the security boundary, the one directive, the chain proof, the redeploy.

------

**Shell:** beats quote Bash; in PowerShell `DEPLOY` and `SCP` are functions called as `DEPLOY ...` and `SCP ...`, because a command held in a string will not invoke, and `UserKnownHostsFile` reads `NUL`, because `/dev/null` creates a literal `dev\null` file.

## Beats

### Beat 1: `expose` and `ports` are the security boundary (1 min)

**Open:** [`box-stack/docker-compose.yml`](box-stack/docker-compose.yml) · [Step 1: Finish the Compose file with a single public edge](demo-compose-caddy-tls.md#step-1-finish-the-compose-file-with-a-single-public-edge)
**Say:** On your own box, what the internet can reach is decided entirely by fields you write. Exactly one container faces the public and every other one is reachable only through it.

```text
  caddy: caddy:2-alpine, restart unless-stopped, publishes 80 and 443,
         mounts ./Caddyfile read-only at /etc/caddy/Caddyfile,
         named volumes caddy_data at /data and caddy_config at /config
  app:   internal port 8080 only
```

**Result:** [`box-stack-solution/docker-compose.yml`](box-stack-solution/docker-compose.yml), where the edge holds the only published ports and `app` gains `expose: 8080` with no host mapping

```yaml
  caddy:
    image: caddy:2-alpine
    restart: unless-stopped
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./Caddyfile:/etc/caddy/Caddyfile:ro
      - caddy_data:/data
      - caddy_config:/config
```

**Gotcha:** `expose` opens a port on the internal network and `ports` opens it on the host, so confusing them puts the app on the public internet at 8080.

### Beat 2: one directive is the entire difference from production (1 min)

**Open:** [`box-stack/Caddyfile`](box-stack/Caddyfile) · [Step 2: Write the Caddyfile and prove the certificate](demo-compose-caddy-tls.md#step-2-write-the-caddyfile-and-prove-the-certificate)
**Say:** Routing, health probe, automatic redirect and certificate lifecycle all run identically on a laptop. That leaves exactly one open question, which is who signs.

```text
Finish Caddyfile. Keep the existing :8090 block exactly as it is, and add one
site block:

- Site box.example.at, served with Caddy's internal CA (tls internal)
- /healthz inside that site responds "ok" with 200, ordered before the proxy
- everything else reverse proxies to app:8080
```

**Result:** one site block is the whole addition to [`box-stack-solution/Caddyfile`](box-stack-solution/Caddyfile), with `tls internal` as its first directive

```text
box.example.at {
	tls internal

	handle /healthz {
		respond "ok" 200
	}

	handle {
		reverse_proxy app:8080
	}
}
```

**Gotcha:** a bare `:80` block here would take port 80 from every hostname and kill every HTTP-01 challenge, which is why the box-level probe sits on `:8090`.

### Beat 3: prove the chain, do not wave it through (1 min)

**Open:** [`box-stack-solution/Caddyfile`](box-stack-solution/Caddyfile) · [Step 2: Write the Caddyfile and prove the certificate](demo-compose-caddy-tls.md#step-2-write-the-caddyfile-and-prove-the-certificate)
**Say:** A check that only passes with verification switched off has not passed. Supply the trust anchor explicitly and read back whether validation succeeded.

```bash
$DEPLOY 'curl -sS --cacert /tmp/box-root.crt --resolve box.example.at:443:127.0.0.1 -o /dev/null -w "http=%{http_code} verify=%{ssl_verify_result}\n" https://box.example.at/'
$DEPLOY 'echo | openssl s_client -connect 127.0.0.1:443 -servername box.example.at 2>/dev/null | openssl x509 -noout -issuer -dates'
```

**Result:** the chain validated against the root Caddy generated into the `caddy_data` volume on the box, never a file in the repository

```text
http=200 verify=0
issuer=CN = Caddy Local Authority - ECC Intermediate
notBefore=Jul 29 20:56:13 2026 GMT
notAfter=Jul 30 08:56:13 2026 GMT
```

**Gotcha:** `verify=0` means the chain validated against a root you supplied, the exact check `curl -k` skips, and `--resolve` proved the hostname live with no DNS record anywhere.

### Beat 4: `restart` never picks up a new image (1 min)

**Open:** [`box-stack/app/index.html`](box-stack/app/index.html) · [Step 3: Redeploy and prove the new version is live](demo-compose-caddy-tls.md#step-3-redeploy-and-prove-the-new-version-is-live)
**Say:** Compose verbs read like synonyms and act on different objects. Choosing the wrong one produces no error, no warning and no change.

```bash
$DEPLOY 'cd /opt/box-stack && sed -i "s/Build 2/Build 3/" app/index.html && docker compose build -q app && docker compose restart app && sleep 2'
$DEPLOY 'curl -sS --cacert /tmp/box-root.crt --resolve box.example.at:443:127.0.0.1 https://box.example.at/ | grep -o "Build ."'
$DEPLOY 'cd /opt/box-stack && docker compose up -d app && sleep 2'
$DEPLOY 'curl -sS --cacert /tmp/box-root.crt --resolve box.example.at:443:127.0.0.1 https://box.example.at/ | grep -o "Build ."'
```

**Result:** after `restart` the page still reads `Build 2` and after `up -d` it reads `Build 3`, while `image: box-app:latest` in [`box-stack-solution/docker-compose.yml`](box-stack-solution/docker-compose.yml) never changes across either verb.

**Gotcha:** the image reference binds at container create time, so `restart` reuses the existing container and its existing image indefinitely; `env_file` behaves identically.

## If the room asks

| Question | Answer |
|---|---|
| `docker compose ps` says `health: starting`. What is wrong? | Nothing. The healthcheck has a 30 second interval and no `start_period`, so the first probe fires about thirty seconds in. |
| Why does `80/tcp` appear next to `8080/tcp` on the app container? | `app/Dockerfile` builds on `nginx:1.27-alpine`, which declares `EXPOSE 80`, and an inherited `EXPOSE` cannot be withdrawn. Neither number has a host mapping. |
| What exactly changes for a real domain on a real VM? | Two edits to one site block: the real hostname in the site address, and the `tls internal` line deleted. |
