# CI Failure Log

A CSV export of failed pipeline runs, one row per failure: date, service, stage, error, duration_min, triggered_by.

- ci-failures.csv is the source of truth. Never edit it unless the task says so.
- check-totals.py prints failures and lost minutes per service; run it to cross-check any number you publish.
- Write every page you build to the pages/ folder as a single self-contained .html file.
