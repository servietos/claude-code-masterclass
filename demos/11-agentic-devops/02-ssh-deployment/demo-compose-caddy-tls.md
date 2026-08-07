# Ship the App with Compose, Caddy and TLS

Shipping an app onto the box you hardened is mostly an ordering rule, not a command: DNS must resolve and the proxy must be answering on 80 and 443 before the first certificate request, because a premature attempt turns a five-minute fix into an hours-long wait. You complete the Compose file with the single public Caddy edge it is missing, write the Caddyfile site blocks, then prove the certificate and the redeploy instead of asserting them. You end up holding one published edge, a verified TLS chain, and the single directive that separates the local internal certificate authority from a real one.

------

Budget thirty minutes.

The box is still the container from [Bootstrap and Harden an Ubuntu Host over SSH](demo-bootstrap-and-harden.md), reachable as `deploy@localhost` on port 2222. A container on your laptop cannot hold a public DNS record, so it cannot obtain a publicly trusted certificate; you run the same Caddy configuration with its internal certificate authority instead, and Step 5 names the single line that changes for a real domain on a real VM.

## Setup

Run this demo from the same folder and the same shell as the previous one.

```bash
cd demos/11-agentic-devops/02-ssh-deployment/box-stack
claude
```

The two files you complete in this demo are at that folder's root. `docker-compose.yml` has the `app` service and no edge, and `Caddyfile` has the side-port health probe and no site blocks. The finished versions live beside the starter in [box-stack-solution/](box-stack-solution/readme.md) as the completed reference.

Confirm the box from the previous demo is still up and still yours:

```bash
export DEPLOY='ssh -p 2222 -i target-box/keys/box_key -o IdentitiesOnly=yes -o UserKnownHostsFile=/dev/null -o StrictHostKeyChecking=no deploy@localhost'
export SCP='scp -P 2222 -i target-box/keys/box_key -o IdentitiesOnly=yes -o UserKnownHostsFile=/dev/null -o StrictHostKeyChecking=no'
$DEPLOY 'whoami; docker compose version; id -nG'
```

PowerShell cannot run a command it holds in a string, so define functions instead of variables. `UserKnownHostsFile` becomes `NUL` here, because Win32-OpenSSH takes the Bash form literally and creates a file called `dev\null` in the current folder:

```powershell
function DEPLOY { ssh -p 2222 -i target-box/keys/box_key -o IdentitiesOnly=yes -o UserKnownHostsFile=NUL -o StrictHostKeyChecking=no deploy@localhost @args }
function SCP { scp -P 2222 -i target-box/keys/box_key -o IdentitiesOnly=yes -o UserKnownHostsFile=NUL -o StrictHostKeyChecking=no @args }
DEPLOY 'whoami; docker compose version; id -nG'
```

Every later `$DEPLOY ...` and `$SCP ...` line in this demo runs as `DEPLOY ...` and `SCP ...` in PowerShell; only the leading `$` comes off.

Expected result: `deploy`, a version string from the Compose plugin, and a group list containing `docker` (next to the `users` group `adduser` gave the account). If any of the three is missing, run the bootstrap demo first; this demo changes nothing about access, users or the firewall and assumes all of it.

## Step 1: Create the stack directory out of band

The stack lives at `/opt/box-stack`, and `deploy` cannot create it: the previous demo gave that user no `sudo`, which is exactly the restriction you want at deploy time. Creating a directory under `/opt` and handing it to `deploy` is a one-time root act, so it happens out of band through the container, the laptop equivalent of a provider's serial console.

```bash
docker compose -f target-box/docker-compose.yml exec -T box \
  bash -c 'mkdir -p /opt/box-stack && chown -R deploy:deploy /opt/box-stack'
$DEPLOY 'stat -c "%a %U:%G %n" /opt/box-stack'
```

Expected output:

```text
755 deploy:deploy /opt/box-stack
```

Expected result: the deploy user owns the stack directory, so nothing in the deploy path from here on needs `sudo`. On a real VM this is one `ssh root@<ip>` command run during bootstrap, before root login is closed, or one `sudo` from an admin account afterwards. Getting it out of the way now is deliberate: a deploy step that needs root privileges is a deploy step that will eventually run as root.

Now brief Claude in the session you opened in Setup:

```text
Our deployment target for this session is the Ubuntu box from the previous demo:

  ssh -p 2222 -i target-box/keys/box_key -o IdentitiesOnly=yes \
      -o UserKnownHostsFile=/dev/null -o StrictHostKeyChecking=no deploy@localhost

The stack directory is /opt/box-stack, owned by deploy. Root SSH is closed and
deploy has no sudo, so everything from here on runs as deploy.

Read app/ and docker-compose.yml and report: what port the app listens on, which
user it runs as, what paths it serves, what image tag the Compose file names, and
which services the Compose file is still missing. Do not change anything on the
host or write any files yet.
```

Expected result: Claude reports port 8080, the `nginx` user, `/` and `/healthz`, the tag `box-app:latest`, and one service present (`app`) with no edge, no network and no volumes. Those facts are the entire input to the file you finish in Step 2, which is why reading them beats recalling them. If Claude reports a port it did not read in `app/nginx.conf`, stop and ask where the number came from.

## Step 2: Finish the Compose file with a single public edge

The edge pattern is one rule with one exception: exactly one container publishes ports, and every application container is reachable only through it. `expose` declares a port on the internal network, `ports` publishes it on the host interface, and confusing the two is how an application that was supposed to sit behind a proxy ends up answering the internet directly on 8080.

```text
Finish docker-compose.yml. Keep the existing app service with its build and image
values exactly as they are, and add what is missing:

  caddy: caddy:2-alpine, restart unless-stopped, publishes 80 and 443,
         mounts ./Caddyfile read-only at /etc/caddy/Caddyfile,
         named volumes caddy_data at /data and caddy_config at /config
  app:   internal port 8080 only

Rules:
- app must not publish any port on the host.
- Both services get a healthcheck that probes 127.0.0.1, not localhost.
- Do not add depends_on to the caddy service.
- caddy_data must be a named volume, not a bind mount.
- Put both services on one bridge network named box-net.

Write the file only. Do not ship it or start anything.
```

The result should look like this:

```yaml
name: box-stack

services:
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
    networks:
      - box-net
    healthcheck:
      test: ["CMD-SHELL", "wget -qO- http://127.0.0.1:8090/healthz || exit 1"]
      interval: 30s
      timeout: 5s
      retries: 3

  app:
    build: ./app
    image: box-app:latest
    restart: unless-stopped
    expose:
      - "8080"
    networks:
      - box-net
    healthcheck:
      test: ["CMD", "wget", "-qO-", "http://127.0.0.1:8080/healthz"]
      interval: 30s
      timeout: 5s
      retries: 3

networks:
  box-net:
    driver: bridge

volumes:
  caddy_data: {}
  caddy_config: {}
```

Expected result: four constraints in the prompt map to four lines you can point at. `expose` on `app` keeps it off the public interface, and `127.0.0.1` in both healthchecks avoids a false unhealthy container, because busybox `wget` resolves `localhost` to `::1` first while `app/nginx.conf` says `listen 8080` and binds IPv4 only. Caddy happens to bind both families, so writing the literal address in both probes is about removing the question rather than fixing two bugs. The absent `depends_on` matters on a shared box: an edge that depends on an app service resurrects a deleted app container every time the edge is recreated. And `caddy_data` holds the certificate authority account key and every issued certificate, so a bind mount that a cleanup script deletes costs you a fresh round of issuance.

## Step 3: Ship the app and bring it up with no TLS in the path

Verify the application completely before any hostname, any certificate and any published port are involved. There is no registry here, so the image is built on the box under the exact tag the Compose file names. In a pipeline the `build:` line goes away, `image:` becomes a registry reference, and the box only pulls; what has to stay identical across that switch is the tag the Compose file names, because a mismatch there makes the first pipeline run a silent no-op rather than a replacement.

```bash
$DEPLOY 'mkdir -p /opt/box-stack/app'
$SCP -r app/. deploy@localhost:/opt/box-stack/app/
$SCP docker-compose.yml deploy@localhost:/opt/box-stack/docker-compose.yml
$DEPLOY 'cd /opt/box-stack && docker compose build app && docker compose up -d app'
```

`scp -r` rather than a `tar` stream piped into `ssh`: PowerShell decodes and re-encodes bytes crossing a native-to-native pipe, so a gzip stream arrives corrupt there while the same line is fine in Bash. `scp` moves the bytes over the same connection with no local pipe at all, and the trailing `.` in `app/.` copies the directory's contents rather than nesting a second `app/` inside the target.

Prove the app answers without opening a single port:

```bash
$DEPLOY 'cd /opt/box-stack && docker compose ps app; docker compose exec -T app wget -qO- http://127.0.0.1:8080/healthz'
```

Expected output:

```text
NAME              IMAGE            COMMAND                  SERVICE   CREATED          STATUS                            PORTS
box-stack-app-1   box-app:latest   "/docker-entrypoint.…"   app       10 seconds ago   Up 9 seconds (health: starting)   80/tcp, 8080/tcp
ok
```

Expected result: one running container answering `ok` on its own loopback, with no host mapping anywhere in the `PORTS` column, which is `expose` doing its job. Two parts of that line are worth reading rather than skipping.

`health: starting` is not a problem to fix. The healthcheck runs on a 30 second `interval` with no `start_period`, so the first probe fires about thirty seconds in and the status only then flips to `(healthy)`; a container that reads `starting` eight seconds after `up -d` is behaving exactly as configured. Re-run the command after half a minute if you want to watch it change.

`80/tcp` appears next to `8080/tcp` because `app/Dockerfile` builds on `nginx:1.27-alpine`, which declares `EXPOSE 80` in its own layers, and Docker offers no way to withdraw an inherited `EXPOSE`. It costs nothing here: an exposed port is a declaration on the internal network, and neither number has a host mapping in front of it. `ports:` is what would put one there, which is the distinction the whole step is about.

The file has to be named `docker-compose.yml` on the box or every bare `docker compose` command fails with `no configuration file provided`; the alternative is passing `-f` in every invocation, including the ones inside your CI workflow.

This app reads no configuration, so there is no env file in this demo. On a real stack there is, and it arrives the same way the Compose file just did: written straight to its final path with `cat > /opt/<stack>/env/<svc>.env`, `chmod 600`, owned by `deploy`, never in git and never baked into the image. [Phase 4 of the topic page](readme.md#phase-4-ship-the-app-behind-a-single-edge) has the two commands, and Step 6 below has the trap that follows them.

## Step 4: Check the preconditions before the first certificate request

This is the step the whole module is built around. Caddy asks a public certificate authority for a certificate the moment a site block for a hostname loads, and that request fails unless two things are already true. Both are outside the deploy: they belong to DNS and to the network, each with its own owner and its own latency.

| Precondition | How the agent checks it | What a premature attempt costs |
|---|---|---|
| The hostname resolves to this box | `dig +short <host>` against several public resolvers, then compare with the box address | The authority validates a name pointing elsewhere, or nowhere, and the validation fails |
| Port 80 is reachable from the internet | `curl -sS -o /dev/null -w '%{http_code}' http://<host>/` from outside the box | The HTTP-01 challenge cannot be answered, so every attempt fails |
| The edge is actually listening | `ss -lntp` on the box showing 80 and 443 | A restarting or crash-looping edge fails the challenge while looking configured |

Failure here is not free, and it is not self-healing. Let's Encrypt caps failed validations at five per account, per hostname, per hour, and Caddy then backs off exponentially, so the backoff timer keeps running long after you correct the DNS record. You fix the record in a minute and the hostname still does not serve, which is what makes "start it early and let it retry" the most expensive shortcut available. With several hostnames on one box, one premature `compose up` burns the budget for all of them at once.

Run the checks against your box and read the first one carefully:

```bash
$DEPLOY 'getent hosts box.example.at || echo "NO RECORD: box.example.at does not resolve"'
$DEPLOY 'ss -lntp | grep -E ":(80|443) " || echo "nothing is listening on 80 or 443 yet"'
```

Expected output:

```text
NO RECORD: box.example.at does not resolve
nothing is listening on 80 or 443 yet
```

Expected result: both preconditions for a publicly trusted certificate are unmet, and you know that before touching the edge rather than after burning five validations. That is the whole discipline: the check comes first, and its answer decides what you configure next. On a real VM the same two commands read `box.example.at has address 203.0.113.10` and two listening sockets, and only then does a public site block go into the Caddyfile.

The correct ordering when a real record is on its way is to pre-stage rather than wait. Verify the stack over the internal network as you did in Step 3, put the real `host { reverse_proxy ... }` block in the Caddyfile commented out, and lower the record's TTL to 300 beforehand. Confirm propagation by querying the parent zone directly with `dig +norecurse @<tld-nameserver> <domain> NS`, because one public resolver agreeing with you proves only that one cache is warm. Then uncomment the block, restart the edge, and confirm issuance in the logs.

## Step 5: Write the Caddyfile and prove the certificate

Now that you know the hostname does not resolve publicly, configure the path that works on this box: Caddy's internal certificate authority, which issues a certificate from a local root instead of asking a public authority for one. Everything else in the file is identical to the public case, including the routing, the health probe and the automatic redirect from HTTP.

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

The result should look like this:

```caddyfile
:8090 {
	handle /healthz {
		respond "ok" 200
	}
}

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

Claude's one sentence should say that a bare `:80 { ... }` block takes port 80 away from Caddy for every hostname on the box, killing all HTTP-to-HTTPS redirects and every HTTP-01 challenge, which is why the box-level probe lives on the side port the starter already provides. Now prove the certificate rather than assuming it. Pull the internal root out of the edge container and verify against it, because `curl -k` skips exactly the check you are trying to make:

```bash
$DEPLOY 'cd /opt/box-stack && docker compose exec -T caddy cat /data/caddy/pki/authorities/local/root.crt > /tmp/box-root.crt'
$DEPLOY 'curl -sS --cacert /tmp/box-root.crt --resolve box.example.at:443:127.0.0.1 -o /dev/null -w "http=%{http_code} verify=%{ssl_verify_result}\n" https://box.example.at/'
$DEPLOY 'echo | openssl s_client -connect 127.0.0.1:443 -servername box.example.at 2>/dev/null | openssl x509 -noout -issuer -dates'
$DEPLOY 'cd /opt/box-stack && docker compose logs caddy | grep -i "certificate obtained"'
```

Expected output:

```text
http=200 verify=0
issuer=CN = Caddy Local Authority - ECC Intermediate
notBefore=Jul 29 20:56:13 2026 GMT
notAfter=Jul 30 08:56:13 2026 GMT
caddy-1  | {"level":"info","ts":1785358573.4058652,"logger":"tls.obtain","msg":"certificate obtained successfully","identifier":"box.example.at","issuer":"local"}
```

Expected result: HTTP 200 with `verify=0`, meaning the chain validated rather than being waved through. Note what `--resolve` just did: it proved the hostname is live on this edge with no DNS record existing anywhere, which is the tool that makes the Step 4 ordering safe rather than merely cautious. Your timestamps and the exact intermediate name will differ; the two fields that matter are the issuer and the `certificate obtained successfully` line naming the identifier.

The twelve hours between `notBefore` and `notAfter` are worth a glance, because a publicly trusted certificate would read months. Caddy issues internal certificates with a deliberately short life and renews them in the background, which is safe precisely because the local authority is one `docker compose exec` away rather than a rate-limited public service.

**What changes for a real domain on a real VM:** two edits to one site block, and nothing else in the stack. Put the real hostname in the site address, and delete the `tls internal` line, because that single directive is the entire difference between a local root and a public one. A site block with no `tls` directive and no `auto_https off` makes Caddy request a publicly trusted Let's Encrypt certificate over HTTP-01 and renew it automatically, and the same four verification commands then report `issuer=C = US, O = Let's Encrypt` with `--cacert` dropped because the system trust store already contains that root.

Two habits belong to the public path only. If it works with `curl -k` but not without, it has not worked: report the ACME error instead of falling back to a self-signed certificate. And add CAA records only after the first certificate has issued, because a wrong CAA record does not degrade issuance, it blocks it outright.

## Step 6: Redeploy and prove the new version is live

A deploy that changes nothing exits 0 and reports success, which is why the last step is a proof rather than a command. Change the build, roll it out, and show three separate facts: the response body changed, the container is running a different image, and nothing else on the box moved.

```text
Redeploy the app with a visible change:

1. Edit app/index.html and change the build marker in the footer from "Build 1"
   to "Build 2". Change nothing else.
2. Ship app/ to /opt/box-stack/app on the box.
3. Rebuild box-app:latest on the box, keeping the tag identical.
4. Recreate only the app service. Do not touch the caddy service.
5. Report the image ID before and after, and the container name.
```

Verify all three facts yourself:

```bash
$DEPLOY 'curl -sS --cacert /tmp/box-root.crt --resolve box.example.at:443:127.0.0.1 https://box.example.at/ | grep -c "Build 2"'
$DEPLOY 'docker inspect box-stack-app-1 --format "{{.Config.Image}} {{.Image}}"'
$DEPLOY 'docker image inspect box-app:latest --format "{{.Created}}"'
$DEPLOY 'docker ps -q | wc -l; docker ps --filter health=unhealthy --format "{{.Names}}"'
```

Expected output:

```text
1
box-app:latest sha256:8f2c1a...
2026-07-29T09:31:12.442Z
2
```

Expected result: the new marker is in the response, the container's resolved image ID is the one you just built, the creation timestamp is minutes old, and the box still runs exactly two containers with none unhealthy. The tag never changed, which is the realistic case: a moving tag such as `latest` or a release tag rebuilt in place means the tag alone tells you nothing, and only the image ID and the timestamp distinguish the new build from the old one.

That is also why `compose up -d` recreated the container while `compose restart` would not have. Prove that claim rather than taking it, because it is the failure that produces the longest debugging sessions:

```bash
$DEPLOY 'cd /opt/box-stack && sed -i "s/Build 2/Build 3/" app/index.html && docker compose build -q app && docker compose restart app && sleep 2'
$DEPLOY 'curl -sS --cacert /tmp/box-root.crt --resolve box.example.at:443:127.0.0.1 https://box.example.at/ | grep -o "Build ."'
$DEPLOY 'cd /opt/box-stack && docker compose up -d app && sleep 2'
$DEPLOY 'curl -sS --cacert /tmp/box-root.crt --resolve box.example.at:443:127.0.0.1 https://box.example.at/ | grep -o "Build ."'
```

Expected result: after `restart` the page still reads `Build 2`, and after `up -d` it reads `Build 3`. The image reference binds at container create time, so `restart` reuses the existing container and its existing image indefinitely with no error anywhere. `env_file` behaves identically, which is why the rule on the topic page is `up -d <service>` after touching either one, never `restart`.

One caveat worth carrying forward: never `mv` a new file onto a bind-mounted config file. A file mount binds the inode rather than the path, so `cat > Caddyfile.new && mv Caddyfile.new Caddyfile` leaves the container serving the old file indefinitely while `caddy validate` reports a valid configuration and `caddy reload` exits 0. Write in place, which is what the `scp` to an exact path did in Step 3 and Step 5, and diagnose a suspicious reload by comparing `docker exec box-stack-caddy-1 stat -c %i /etc/caddy/Caddyfile` with `stat -c %i` on the host path.

## Helpful Claude Slash Commands

| Command | Usage |
|---|---|
| `/memory` | Record the stack path, the image tag and the hostname in `CLAUDE.md`, so the agent reads them instead of reconstructing a port number from an old conversation |
| `/permissions` | Add `Bash(scp:*)` and `Bash(docker:*)` alongside `Bash(ssh:*)`, since shipping files and building an image are separate verbs from reaching the host |
| `/compact` | Drop the build output and log tails before the TLS step, which is the point in the demo where the window fills fastest |
| `/agents` | Hand the Step 6 redeploy loop to `ssh-deploy-agent` once you know by hand what each of the three proofs should say |

## Key Topics Covered in This Demo

- [Compose file services reference](https://docs.docker.com/reference/compose-file/services/): `expose` versus `ports`, `build` and the `healthcheck` block used by both services
- [Compose up reference](https://docs.docker.com/reference/cli/docker/compose/up/): why a changed image recreates a container and a restart does not
- [Caddy automatic HTTPS](https://caddyserver.com/docs/automatic-https): what makes Caddy request a public certificate, and the two preconditions it cannot check for you
- [Caddy tls directive](https://caddyserver.com/docs/caddyfile/directives/tls): `tls internal`, the local certificate authority, and where its root lives inside the container
- [Caddy reverse_proxy directive](https://caddyserver.com/docs/caddyfile/directives/reverse_proxy): resolving an upstream by service name over the shared Compose network
- [Let's Encrypt rate limits](https://letsencrypt.org/docs/rate-limits/): the failed-validation cap that makes the ordering in Step 4 a rule rather than a preference
- [Let's Encrypt challenge types](https://letsencrypt.org/docs/challenge-types/): HTTP-01 and the DNS-01 alternative for issuing before a record points at the box
- [curl manual](https://curl.se/docs/manpage.html#--resolve): `--resolve` and `--cacert`, the two options that prove a hostname and its chain without DNS

