# Lumen Architecture Overview

Lumen is the internal observability platform. It runs five services in the `lumen-prod` Kubernetes cluster in `eu-central-1`, split across three availability zones.

- `lumen-ingest` receives OpenTelemetry OTLP traffic on port 4317 and writes to Kafka topic `lumen.raw` (24 partitions, 7 day retention).
- `lumen-rollup` consumes `lumen.raw`, aggregates to 10 second, 1 minute and 1 hour resolutions, and writes to the ClickHouse cluster `ch-lumen-01` (6 nodes, 18 TB usable).
- `lumen-query` serves the read API on `https://lumen.internal/api/v2` with a p99 latency budget of 800 ms.
- `lumen-alerts` evaluates alert rules every 30 seconds and pushes notifications to the routing layer.
- `lumen-dashboards` renders saved dashboards and holds the dashboard registry in Postgres database `lumen_meta`.

Data flows one way: ingest to Kafka, Kafka to rollup, rollup to ClickHouse, ClickHouse to query, query to dashboards and alerts. Nothing reads Kafka except `lumen-rollup`, which keeps the replay story simple: reset the consumer group offset and the last seven days rebuild themselves.

Deployment is GitOps. Every service ships from the `lumen-platform` repo through Argo CD, one application per service, with `lumen-prod` synced automatically and `lumen-eu-dr` synced manually. Rollouts are canary at 10 percent for 15 minutes, then full. The platform carries a 99.9 percent monthly availability objective measured on `lumen-query` success rate, and it burned 41 percent of its error budget in Q1 2026.
