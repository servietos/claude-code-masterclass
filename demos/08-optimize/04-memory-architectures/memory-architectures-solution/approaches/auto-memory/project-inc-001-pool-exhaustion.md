---
name: project-inc-001-pool-exhaustion
description: INC-001 root cause was PaymentsService connection pool exhaustion, and it triggered ADR-001
metadata:
  type: project
  modified: 2026-03-14T08:05:00.000Z
---

INC-001 (2026-03-12, P1, 47 minutes) was connection pool exhaustion in PaymentsService: max connections were set to 5 while peak load reached 40 concurrent checkout requests. Fixed by raising the pool to 50 and adding a circuit breaker with a 10s timeout. Owner: Maria Chen.

ADR-001 (event sourcing for order state) was adopted as a direct consequence. Commands go to Kafka and OrderProjection builds the read models; order status reads are eventually consistent.
