---
name: user-kafka-onboarding
description: New to the ADR-001 Kafka consumer path; spell out the event-sourcing steps rather than assuming them
metadata:
  type: user
  modified: 2026-05-06T11:00:00.000Z
---

Alex Kim joined in Sprint 14 and is still working through the ADR-001 Kafka consumer walkthrough.

When the work touches order state, name the command topic, the consumer, and the projection explicitly instead of writing "the usual event-sourcing flow". Read models come from OrderProjection, and order status reads are eventually consistent.
