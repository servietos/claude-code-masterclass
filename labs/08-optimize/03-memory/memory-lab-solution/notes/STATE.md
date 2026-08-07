# Lumen, Project State

## People

- Priya Raghunathan, platform lead, alert routing and on-call model, final P1 escalation.
- Maya Ostrowski, senior engineer, metric pipeline: ingest, Kafka, rollup, ClickHouse schema.
- Nadia Fischer, senior engineer, dashboards and dashboard registry, led INC-2026-021 remediation.
- Tomas Lindqvist, engineer, query service and cache, on primary and secondary on-call.
- Dana Weiss, engineer, all five integrations and OTLP client libraries, on both rotations.
- Rui Almeida, engineer since 2026-02-02, terraform modules and DR cluster, not yet on-call.

## Architecture

- Five services in `lumen-prod` (eu-central-1, three AZs): ingest, rollup, query, alerts, dashboards.
- One-way flow: OTLP to `lumen-ingest`, Kafka `lumen.raw`, `lumen-rollup`, ClickHouse `ch-lumen-01`, query.
- `lumen-query` serves `https://lumen.internal/api/v2` under a p99 budget of 800 ms.
- GitOps through Argo CD from `lumen-platform`, canary 10 percent for 15 minutes.
- 99.9 percent monthly availability objective, 41 percent of the error budget burned in Q1 2026.

## Pipelines

- Peak ingest 2.4M data points per second (March 2026), daily average 1.6M.
- Mandatory labels `service`, `env`, `team`, `region`; missing `team` is rejected.
- Cardinality cap 250,000 active series per service, newest series dropped on breach.
- Rollup resolutions: 10s for 48 hours, 1m for 30 days, 1h for 400 days.
- Alert tiers: P1 pages PagerDuty `lumen-primary` (ack in 5 minutes), P2 to `#lumen-alerts` and pages after 30 minutes, P3 opens a `LUM` Jira ticket.
- P1 escalation: primary, secondary after 10 minutes, Priya after 25 minutes, incident channel after 60 minutes.
- On-call: weekly primary rotation handing over Tuesdays 10:00 CET, shared by Priya, Tomas and Dana; secondary is the same three offset by one week.

## Incidents

- 2026-01-22, INC-2026-014, lumen-ingest, 47 min: unbounded per-series logging on the cardinality drop path saturated the log pipeline and throttled ingest.
- 2026-02-19, INC-2026-021, lumen-dashboards, 2 h 12 min: the 2026-02-18 YAML to JSON registry migration wrote panel `targets` as an object where the renderer expected an array, breaking 214 of 312 dashboards; the migration was validated only against 20 recently edited dashboards.
- 2026-03-08, INC-2026-033, lumen-rollup, 88 min: a lost Kafka broker plus `range` rebalancing reshuffled every partition, lag peaked at 41 minutes.

## Integrations

- Beacon data lake, highest volume by far (380 GB per day, about 11 TB per month), top risk schema drift with no contract test.
- Slack, roughly 12,000 messages per month, top risk rate limits during an alert storm.
- Jira `LUM`, roughly 400 issues per month, top risk webhook echo loops.
- Atlas CMDB, nightly sync of about 4,000 records, top risk a stale sync routing alerts to a dead team.
- PagerDuty `lumen-primary`, roughly 900 events per month, top risk a silent routing key rotation.

## Roadmap

- Exemplar support, Q3 2026, Maya, blocked on a ClickHouse `trace_id` column.
- Alert rule linting in CI, Q3 2026, Priya, driven by 31 percent of Q1 P1 pages having no runbook.
- Dashboard schema v3 with CI validation, Q4 2026, Nadia.
- Long-term bet: cross-region query federation in 2027, turning the DR cluster into a live read replica.
