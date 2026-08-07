# Project Knowledge Base

## Incidents

| ID | Date | Root Cause | Owner |
|---|---|---|---|
| INC-001 | 2026-03-12 | PaymentsService pool exhaustion (max 5 → fixed to 50). Triggered ADR-001. | Maria Chen |
| INC-002 | 2026-04-03 | JWT TTL mismatch: staging 1h vs prod 24h (PR #412). Fixed via AUTH_TOKEN_TTL_HOURS env var. | James Park |
| INC-003 | 2026-04-28 | Elasticsearch reindex silent failure at 100k records. Fixed: job monitoring + Slack alert. | Sofia Reyes |

## Decisions

| ID | Date | Decision | Consequence |
|---|---|---|---|
| ADR-001 | 2026-02-15 | Event sourcing for orders (Kafka + OrderProjection). Triggered by INC-001. | Eventual consistency for order reads. |
| ADR-002 | 2026-03-20 | Redis session cache (TTL = AUTH_TOKEN_TTL_HOURS). | Session loss on Redis restart without persistence. |
| ADR-003 | 2026-05-01 | URL versioning via /v1/ prefix. Breaking changes go to /v2/. | None |

## Active Risks

- Redis restart without persistence wipes sessions (ADR-002 consequence)
- Auth TTL and Redis TTL must stay in sync (see ADR-002)
- Alex Kim (new) still completing Kafka consumer walkthrough
