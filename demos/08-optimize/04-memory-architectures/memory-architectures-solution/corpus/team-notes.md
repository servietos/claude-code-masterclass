# Team Notes

## Sprint 14 (2026-05-01 to 2026-05-14)

**Team:** Maria Chen (lead), James Park, Sofia Reyes, Alex Kim (new joiner)
**Goal:** Ship paginated product search and close INC-003 root cause permanently

### Completed
- INC-003 fix: job monitoring and alerting
- Product search endpoint with Elasticsearch pagination
- ADR-003 implemented: all routes now under /v1/

### In progress
- Redis session cache migration (James, targeting Sprint 15)
- Alex onboarding: completing ADR-001 Kafka consumer walkthrough

### Notes
- Do not change auth TTL without updating Redis TTL to match, see ADR-002
- James owns the Redis migration; Maria reviews before merge
