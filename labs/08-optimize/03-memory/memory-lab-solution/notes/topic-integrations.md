# Lumen Integrations

Five integrations connect Lumen to other internal tools. Dana Weiss owns all five.

1. **PagerDuty** (`lumen-primary` service). Outbound only, roughly 900 events per month. Main risk: a routing key rotation breaks paging silently, so the adapter sends a synthetic heartbeat event every hour.
2. **Slack** (`#lumen-alerts`, `#lumen-oncall`). Outbound, roughly 12,000 messages per month. Main risk: Slack rate limits during an alert storm, mitigated by batching P2 notifications into a 60 second window.
3. **Jira** (`LUM` project). Bidirectional, roughly 400 issues per month. Main risk: a webhook loop when Lumen updates an issue that Jira then echoes back, guarded by an origin marker on every update.
4. **Atlas CMDB**. Inbound service ownership data, one full sync per night, about 4,000 records. Main risk: a stale sync assigns alerts to a team that no longer exists, so a sync older than 36 hours fails the `CmdbSyncStale` check.
5. **Beacon data lake**. This is by far the highest data volume integration: `lumen-rollup` exports the 1 hour resolution table to Beacon every night, 380 GB per day compressed, about 11 TB per month, which is more than all four other integrations combined by three orders of magnitude. The team considers its main risk to be schema drift: Beacon consumers read the exported Parquet files directly, so any ClickHouse column rename silently breaks downstream jobs the next morning, and there is no contract test between Lumen and Beacon today. A schema contract is a candidate for Q4 2026 but is not yet scheduled.
