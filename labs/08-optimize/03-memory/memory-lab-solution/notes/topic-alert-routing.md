# Lumen Alert Routing

`lumen-alerts` evaluates rules every 30 seconds and routes notifications through three tiers.

- **P1** pages the on-call engineer immediately through PagerDuty service `lumen-primary`. Acknowledgement is expected within 5 minutes.
- **P2** posts to the Slack channel `#lumen-alerts` and pages only if unacknowledged for 30 minutes.
- **P3** opens a ticket in the `LUM` Jira project and never pages.

Escalation for a P1 runs primary on-call, then secondary on-call after 10 minutes without acknowledgement, then the platform lead Priya Raghunathan after 25 minutes. A P1 that is still open after 60 minutes automatically opens an incident channel named `#inc-lumen-<date>` and notifies the duty incident commander.

Priya Raghunathan owns the alert-routing area. Her on-call rotation is a weekly primary rotation that hands over on Tuesdays at 10:00 CET, shared with Tomas Lindqvist and Dana Weiss, so each of the three engineers carries primary roughly one week in three. Secondary on-call is a separate weekly rotation staffed by the same three people offset by one week.

Handoff rules: the outgoing primary writes a handover note in `#lumen-oncall` listing open incidents, silenced alerts with their expiry, and any rollout in flight. A silence longer than 24 hours needs Priya's approval, and silences without an expiry are rejected by policy. Routing changes ship as code in `lumen-platform/alerts/routes.yaml` and require one review from the alert-routing owner.
