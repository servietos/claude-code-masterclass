# Architectural Decisions

## ADR-001: Adopt event sourcing for order state (2026-02-15)

Chosen over mutable DB records after INC-001 made replay requirements obvious.
Commands go to Kafka; OrderProjection listens and builds read models.
Consequence: eventual consistency for order status reads (accepted).

## ADR-002: Use Redis for session cache (2026-03-20)

Chosen after auth load tests showed PostgreSQL session table at 40k rows/minute.
Redis TTL matches AUTH_TOKEN_TTL_HOURS. No persistent session storage needed.
Consequence: session data lost on Redis restart without persistence config.

## ADR-003: API versioning via URL prefix (2026-05-01)

All routes prefixed with /v1/. Breaking changes increment to /v2/ without removing /v1/.
Adopted after mobile client breakage in the unversioned era.
