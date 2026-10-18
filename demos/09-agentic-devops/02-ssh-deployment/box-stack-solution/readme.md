# Compose and Caddy Reference for the Box Stack

The two files [box-stack/](../box-stack/readme.md) leaves as stubs, finished. This is a reference to compare against. Run the demos in the starter, which owns the target, the app and the keys.

| Decision | Where it shows up |
|---|---|
| The edge is the only public listener | `caddy` publishes `80` and `443`; `app` gets `expose`, never `ports` |
| The certificate survives a recreate | `caddy_data` is a named volume, because it holds the ACME account key and the issued certificates |
| No `depends_on` on an app service | recreating a shared edge must not resurrect or restart an app container |
| Health probe on a side port | `:8090` in the `Caddyfile` answers `/healthz`; the Compose file adds no edge healthcheck |
| App healthcheck probes `127.0.0.1` | `app/Dockerfile` `HEALTHCHECK`: busybox `wget` tries `::1` first, while nginx binds IPv4 only |

## The `tls internal` Line

`box.example.at` carries `tls internal`, which is the one line that differs from a production Caddyfile. A container on a laptop holds no public DNS record, so no public authority can validate that name; `tls internal` issues the certificate from Caddy's own local root instead, and everything else (the routing, the health probe, the automatic redirect from HTTP) behaves exactly as it does in the public case. Verify it with `curl --resolve box.example.at:443:127.0.0.1 --cacert <the local root>`, which proves the hostname and its chain on this edge with no DNS record anywhere.

Deleting that single line is the whole cutover to a real domain, and the ordering rule around it is what the module teaches. Caddy asks Let's Encrypt for a certificate the moment a site block names a hostname with no `tls` directive, and Let's Encrypt caps failed validations at five per hostname per hour before Caddy starts backing off exponentially. So the public form of the block waits until the record already resolves to the box, which is why the demo checks resolution and listening sockets before it writes this file at all.
