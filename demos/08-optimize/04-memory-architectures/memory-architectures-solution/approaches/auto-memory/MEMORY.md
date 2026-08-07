# Memory Index

- [INC-001 pool exhaustion](project-inc-001-pool-exhaustion.md): PaymentsService pool capped at 5 against 40 concurrent checkouts, triggered ADR-001
- [ADR-002 Redis session cache](project-adr-002-redis-session-cache.md): sessions move to Redis with a TTL bound to AUTH_TOKEN_TTL_HOURS, James owns the migration
- [Auth TTL and Redis TTL move together](feedback-auth-ttl-pairing.md): never change one without the other, INC-002 was exactly that drift
- [Reindex needs an exit-code check](feedback-reindex-exit-code.md): the Elasticsearch reindex fails silently past 100k records unless the exit code is alerted on
- [New to the Kafka consumer path](user-kafka-onboarding.md): spell out the ADR-001 event-sourcing steps rather than assuming them
- [Incident and decision records](reference-incident-log.md): where the source records live when a memory is not enough
