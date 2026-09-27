# Docker HEALTHCHECK Wiring

## Wiring into a Docker `HEALTHCHECK`

A HEALTHCHECK is two dependencies, the endpoint and the probe binary, and only one of them is
visible in the app's code: `mcr.microsoft.com/dotnet/aspnet:*` ships with neither `curl` nor
`wget`, so the probe fails on the missing binary and the container reads `unhealthy` while serving
traffic perfectly. Install it in the runtime stage per
the global `docker-images` skill (`~/.claude/skills/docker-images/references/docker-dotnet.md`), and verify with
`docker inspect --format '{{.State.Health.Status}}'` rather than by reading the Dockerfile.

Once `/health` exists and the runtime image has `curl` (or `wget` on Alpine-based images):

```dockerfile
HEALTHCHECK --interval=10s --timeout=5s --retries=5 --start-period=15s \
  CMD curl -f http://localhost:8080/health || exit 1
```

Or the equivalent in `docker-compose.yml`:

```yaml
healthcheck:
  test: ["CMD-SHELL", "curl -f http://localhost:8080/health || exit 1"]
  interval: 10s
  timeout: 5s
  retries: 5
  start_period: 15s
```

Back to the index: [dotnet-health-checks](dotnet-health-checks.md)
