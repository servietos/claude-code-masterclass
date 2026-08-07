# Lumen Metric Pipeline

Metrics enter through `lumen-ingest`, which accepts OTLP over gRPC and a legacy StatsD shim on UDP 8125. Peak sustained volume in March 2026 was 2.4 million data points per second, with a daily average of 1.6 million.

Collection rules:

- Every metric carries the mandatory labels `service`, `env`, `team` and `region`. Ingest rejects a series that is missing `team`, which is the single most common onboarding failure.
- Cardinality is capped at 250,000 active series per service. Breaching the cap triggers the `CardinalityCapExceeded` alert and ingest starts dropping the newest series, never the oldest.
- The StatsD shim is deprecated and is scheduled for removal in Q4 2026.

Aggregation happens in `lumen-rollup`. It writes three resolutions: 10 second (retained 48 hours), 1 minute (retained 30 days) and 1 hour (retained 400 days). Rollup runs 12 replicas and processes a Kafka partition at roughly 200,000 points per second per replica.

Storage sits in ClickHouse cluster `ch-lumen-01`. The `metrics_10s` table uses a `ReplicatedMergeTree` engine partitioned by day and ordered by `(service, metric, timestamp)`. Compression averages 11 to 1.

The pipeline's known weak point is rollup lag during a Kafka rebalance: a rolling restart of `lumen-rollup` typically costs 90 seconds of lag, and the `RollupLagHigh` alert fires above 120 seconds. Maya Ostrowski owns the pipeline and reviews its capacity plan every quarter.
