# Lumen Dashboards

`lumen-dashboards` serves 312 saved dashboards from the registry in Postgres database `lumen_meta`. Dashboards are addressed by a stable identifier such as `DASH-0042`, which never changes even when the title does.

Standard dashboards every service is expected to have:

- `DASH-0001` Platform Overview: request rate, error rate, p50 and p99 latency for all five services.
- `DASH-0007` Ingest Health: OTLP acceptance rate, rejected series, cardinality per service.
- `DASH-0012` Rollup Lag: Kafka consumer lag per partition, replica throughput.
- `DASH-0042` Query Latency: p99 by endpoint, cache hit ratio, slow query log count.
- `DASH-0088` Alert Volume: alerts fired by tier, acknowledgement time, silence count.

Team conventions for a new dashboard: title starts with the owning service name, every panel names its unit, no panel queries a range longer than 30 days at 10 second resolution (the query cost is disproportionate), and every dashboard declares an owner team in its description. A dashboard without an owner is archived automatically after 90 days of no views.

Dashboards are defined as JSON in `lumen-platform/dashboards/` and applied by Argo CD, so the browser editor is read-only in production. Nadia Fischer owns the dashboards area and reviews new dashboard pull requests. The registry migration that moved dashboards from YAML to JSON completed on 2026-02-18 and is the direct cause of the February incident recorded in the incidents note.
