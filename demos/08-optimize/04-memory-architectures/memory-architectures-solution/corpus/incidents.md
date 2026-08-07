# Incident Log

## INC-001: Payment Gateway Timeout (2026-03-12)

**Severity:** P1
**Duration:** 47 minutes
**Root cause:** Connection pool exhaustion in PaymentsService. Max connections set to 5; peak load reached 40 concurrent checkout requests.
**Fix:** Increased pool size to 50. Added circuit breaker with 10s timeout.
**Owner:** Maria Chen

## INC-002: User Auth Token Expiry Bug (2026-04-03)

**Severity:** P2
**Duration:** 2 hours
**Root cause:** JWT expiry set to 1 hour in staging config, but to 24 hours in prod config. Inconsistency introduced in PR #412 during the environment consolidation.
**Fix:** Unified config via env var AUTH_TOKEN_TTL_HOURS. Default: 24.
**Owner:** James Park

## INC-003: Search Index Stale Data (2026-04-28)

**Severity:** P2
**Duration:** 6 hours
**Root cause:** Elasticsearch reindex job failed silently when product catalog exceeded 100k records. No alerting on job exit code.
**Fix:** Added job exit monitoring and Slack alert on failure. Reindex runs at 02:00 UTC.
**Owner:** Sofia Reyes
