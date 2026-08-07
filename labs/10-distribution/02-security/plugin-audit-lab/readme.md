# Plugin Audit Workspace

The workspace for [Audit a Plugin Before You Install It](../../lab-02-plugin-security.md). Open Claude Code here, not at the repo root.

It ships nearly empty on purpose: everything this lab produces is yours to write. Setup clones the plugin you audit into `audit-target/`, which stays out of version control. Steps 1 to 5 write their findings into `audit/`. Step 6 writes its red-team plugin to `../malicious-example/`, a sibling of this folder; the finished reference for that one is checked in at `../malicious-example-solution/` and is read, never installed.
