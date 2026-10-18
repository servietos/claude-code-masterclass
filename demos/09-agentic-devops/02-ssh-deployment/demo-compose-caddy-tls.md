# Ship the App with Compose, Caddy and TLS

You complete the Compose file with the single public Caddy edge it is missing, write the Caddyfile site blocks, then prove the certificate and the redeploy. You end up holding one published edge, a verified TLS chain, and the single directive that separates the local internal certificate authority from a real one.

------

Work in [`box-stack/`](box-stack) on the box from [Bootstrap and Harden an Ubuntu Host over SSH](demo-bootstrap-and-harden.md), with `$DEPLOY` and `$SCP` set up like that demo's `$BOX` for `deploy@localhost`; the finished files live in [box-stack-solution/](box-stack-solution/readme.md).

## Step 1: Finish the Compose file with a single public edge

Exactly one container publishes ports, and every application container is reachable only through it: `expose` declares a port on the internal network, `ports` publishes it on the host interface. Ship `app/` and the finished file to `/opt/box-stack`, bring up `app` alone, and prove it answers with no TLS in the path:

```text
Finish docker-compose.yml. Keep the existing app service with its build and image
values exactly as they are, and add what is missing:
  caddy: caddy:2-alpine, restart unless-stopped, publishes 80 and 443,
         mounts ./Caddyfile read-only at /etc/caddy/Caddyfile,
         named volumes caddy_data at /data and caddy_config at /config
  app:   internal port 8080 only
- app must not publish any port on the host.
Write the file only. Do not ship it or start anything.
```

```bash
$DEPLOY 'cd /opt/box-stack && docker compose ps app; docker compose exec -T app wget -qO- http://127.0.0.1:8080/healthz'
```

```text
NAME              IMAGE            COMMAND                  SERVICE   CREATED          STATUS                            PORTS
box-stack-app-1   box-app:latest   "/docker-entrypoint.…"   app       10 seconds ago   Up 9 seconds (health: starting)   80/tcp, 8080/tcp
ok
```

No host mapping appears in the `PORTS` column, which is `expose` doing its job; compare [`box-stack-solution/docker-compose.yml`](box-stack-solution/docker-compose.yml).

## Step 2: Write the Caddyfile and prove the certificate

Caddy's internal certificate authority issues a certificate from a local root, and everything else in the file is identical to the public case. Prove the certificate against that root, because `curl -k` skips exactly the check you are trying to make:

```text
Finish Caddyfile. Keep the existing :8090 block exactly as it is, and add one
site block:
- Site box.example.at, served with Caddy's internal CA (tls internal)
- /healthz inside that site responds "ok" with 200, ordered before the proxy
- everything else reverse proxies to app:8080
Do not use a bare :80 block anywhere in this file. Explain in one sentence why
not, then ship the file to /opt/box-stack/Caddyfile and bring the whole stack up
with docker compose up -d.
```

```bash
$DEPLOY 'cd /opt/box-stack && docker compose exec -T caddy cat /data/caddy/pki/authorities/local/root.crt > /tmp/box-root.crt'
$DEPLOY 'curl -sS --cacert /tmp/box-root.crt --resolve box.example.at:443:127.0.0.1 -o /dev/null -w "http=%{http_code} verify=%{ssl_verify_result}\n" https://box.example.at/'
```

```text
http=200 verify=0
```

`verify=0` means the chain validated, and deleting the `tls internal` line from [`box-stack-solution/Caddyfile`](box-stack-solution/Caddyfile) is the whole cutover to a real domain.

## Step 3: Redeploy and prove the new version is live

A deploy that changes nothing exits 0 and reports success, which is why the last step is a proof. Have Claude change the footer marker in `app/index.html` from `Build 1` to `Build 2` and deploy it to the box, then prove that `restart` and `up -d` act differently:

```bash
$DEPLOY 'cd /opt/box-stack && sed -i "s/Build 2/Build 3/" app/index.html && docker compose build -q app && docker compose restart app && sleep 2'
$DEPLOY 'curl -sS --cacert /tmp/box-root.crt --resolve box.example.at:443:127.0.0.1 https://box.example.at/ | grep -o "Build ."'
$DEPLOY 'cd /opt/box-stack && docker compose up -d app && sleep 2'
$DEPLOY 'curl -sS --cacert /tmp/box-root.crt --resolve box.example.at:443:127.0.0.1 https://box.example.at/ | grep -o "Build ."'
```

After `restart` the page still reads `Build 2` and after `up -d` it reads `Build 3`, because the image reference binds at container create time.
