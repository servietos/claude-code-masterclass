# Lumen Roadmap

## Near term

1. **Exemplar support, Q3 2026.** Attach trace exemplars to rollup buckets so a latency spike on `DASH-0042` links straight to a slow trace. Owner Maya Ostrowski. Blocked on a ClickHouse schema change that adds a `trace_id` column to `metrics_10s`.
2. **Alert rule linting, Q3 2026.** A CI check that rejects a rule without a runbook link, without a tier, or with an evaluation window shorter than 60 seconds. Owner Priya Raghunathan. Motivated by the 31 percent of P1 pages in Q1 that had no runbook.
3. **Dashboard schema v3, Q4 2026.** Formal JSON schema for dashboards with validation in CI, closing the class of defect behind INC-2026-021. Owner Nadia Fischer.

## Long term bet

**Query federation across regions, 2027.** Today `lumen-query` serves only `eu-central-1` and the DR cluster is a cold standby. The bet is a federated query layer that fans a single query out to per-region ClickHouse clusters and merges results, which would turn the DR cluster into a live read replica and unlock a US region without a second UI. The open questions are merge semantics for partially failed fan-outs, the cost of cross-region egress at current volume, and whether the p99 latency budget of 800 ms survives a fan-out at all.
