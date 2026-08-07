---
name: project-adr-002-redis-session-cache
description: Sessions move to Redis with a TTL bound to AUTH_TOKEN_TTL_HOURS; migration in flight, James owns it
metadata:
  type: project
  modified: 2026-05-08T14:40:00.000Z
---

ADR-002 (2026-03-20) moves session state to Redis after auth load tests put the PostgreSQL session table at 40k rows/minute. Redis TTL matches AUTH_TOKEN_TTL_HOURS. Consequence: session data is lost on a Redis restart without persistence configured.

In-flight state as of Sprint 14: James owns the migration and targets Sprint 15, Maria reviews before merge. Re-verify this against the sprint notes before acting on it.
