| Row | Expected | Predicted | Confidence | Reason |
|---|---|---|---|---|
| 1 | fire | fire | high | "releases" and "changelogs" in the description match "release notes" |
| 2 | fire | fire | medium | "release" matches "since the last release"; nothing else in the prompt matches |
| 3 | fire | fire | high | "changelogs" in the description matches "changelog entry" |
| 4 | fire | fire | low | Only "version" overlaps with "versions"; no release or changelog wording |
| 5 | no-fire | fire | low | "versions" matches a version edit, which is a likely false positive |
| 6 | no-fire | no-fire | low | Shares the stem of "versioning", but the prompt asks for an explanation and the description says "Handles" |
| 7 | no-fire | no-fire | high | "commit message" and "CSV export" match none of "releases", "versions" or "changelogs" |
| 8 | no-fire | no-fire | medium | "tag" could link to releases; the description names no tags |
