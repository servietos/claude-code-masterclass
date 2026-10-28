# Git

Facts for the global `/git-*` commands.

- Upstream: `alexander-kastil/claude-code-masterclass`. Contributors push to their fork (`origin`) and open pull requests against the upstream.
- Base branch: `master`. Feature branches are `feature/<name>`.
- Pre-push check: `pytest dashboard/test_evaluate.py -v`, the test `.github/workflows/update-class-dashboard.yml` runs on every push to `master`.
- Release and sideload: none. The repo ships no VS Code extension and has no release branch, so `/git-deploy-marketplace` and `/git-sideload` stop here.
