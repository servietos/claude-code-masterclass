# Lumen Incidents, Q1 2026

## INC-2026-014, 2026-01-22, lumen-ingest

Duration 47 minutes. A customer service shipped a label `request_id` on a counter metric and created 1.9 million new series in 6 minutes. The cardinality cap held and ingest dropped the new series, but the drop path logged one line per dropped series and saturated the log pipeline, which pushed ingest pods into CPU throttling. Root cause: unbounded logging on the drop path. Fix: log a per-minute aggregate instead of a per-series line, shipped 2026-01-24.

## INC-2026-021, 2026-02-19, lumen-dashboards

Duration 2 hours 12 minutes. The dashboards service returned HTTP 500 for 214 of the 312 saved dashboards. Root cause: the YAML to JSON registry migration completed on 2026-02-18 wrote panel `targets` as a JSON object where the renderer expected an array, and every dashboard authored before 2025-11 used the older shape. The migration was validated against a sample of 20 recently edited dashboards, none of which used the old shape, so the defect passed review. Fix: a repair job that normalised `targets` to an array plus a schema check in CI, shipped 2026-02-19. Nadia Fischer led the remediation.

## INC-2026-033, 2026-03-08, lumen-rollup

Duration 88 minutes. Kafka broker `kafka-3` lost its disk and the consumer group rebalanced twice in a row. Rollup lag peaked at 41 minutes and `RollupLagHigh` paged at 02:14 CET. Root cause: the rebalance strategy was `range`, so every replica reshuffled its partitions. Fix: switched to cooperative sticky rebalancing, shipped 2026-03-11.
