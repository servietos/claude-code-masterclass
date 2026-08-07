# Knowledge Graph Result

INC-001 root cause: PaymentsService connection pool exhaustion (max 5 connections; peak load required 40 concurrent).

ADR-001 was adopted as a direct consequence: the graph records INC-001 triggered ADR-001 (event sourcing for orders).
