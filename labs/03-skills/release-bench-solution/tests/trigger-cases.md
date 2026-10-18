| # | Expected | Fires | Observed | Verdict | Prompt |
|---|---|---|---|---|---|
| 1 | fire | 3/3 | fire | pass | Write the release notes for this version from the commit list. |
| 2 | fire | 3/3 | fire | pass | What should I tell our users about what shipped since the last release? |
| 3 | fire | 3/3 | fire | pass | Turn data/commits.txt into a changelog entry for customers. |
| 4 | fire | 3/3 | fire | pass | Draft the announcement of what changed in this version for the customer newsletter. |
| 5 | no-fire | 3/3 | fire | **FAIL** | Bump the version in package.json to 2.5.0. |
| 6 | no-fire | 3/3 | fire | **FAIL** | Explain what semantic versioning means for the major number of this package. |
| 7 | no-fire | 0/3 | no-fire | pass | Write a one-line commit message for a fix to the CSV export. |
| 8 | no-fire | 0/3 | no-fire | pass | Explain the difference between a git tag and a git branch. |
