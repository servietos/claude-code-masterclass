# Lumen Team Roles

- **Priya Raghunathan**, platform lead. Owns alert routing and the on-call model, final escalation point for a P1, approves silences longer than 24 hours. Based in Berlin.
- **Maya Ostrowski**, senior engineer. Owns the metric pipeline end to end: ingest, Kafka topics, rollup and the ClickHouse schema. Runs the quarterly capacity plan. Based in Warsaw.
- **Nadia Fischer**, senior engineer. Owns dashboards and the dashboard registry, reviews every dashboard pull request, led the remediation of INC-2026-021. Based in Zurich.
- **Tomas Lindqvist**, engineer. Owns the query service and its cache, shares the primary and secondary on-call rotations with Priya and Dana. Based in Stockholm.
- **Dana Weiss**, engineer. Owns integrations with other internal tools and the OTLP client libraries, shares both on-call rotations. Based in Tel Aviv.
- **Rui Almeida**, engineer, joined 2026-02-02. Owns the terraform modules and the DR cluster `lumen-eu-dr`. Not yet in the on-call rotation, scheduled to join it in Q3 2026.

Review rules: a change to `alerts/routes.yaml` needs Priya, a change to the ClickHouse schema needs Maya, a change under `dashboards/` needs Nadia, and a change to an integration adapter needs Dana. Anything touching two areas needs both owners. The team runs a weekly platform review on Thursdays at 14:00 CET where owners walk through their area's error budget burn.
