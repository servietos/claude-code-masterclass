---
name: release-notes
description: Write release notes for the commits since the latest tag. Use when the user asks for release notes or changelog notes in any phrasing.
---

# Release Notes

You are an expert technical writer.

List the commits since the latest tag: find the tag with `git describe --tags --abbrev=0`, then run `git log --oneline <tag>..HEAD`.
Read CHANGELOG.md and group the commits into Features, Fixes and Chores. Keep each group short.
Output only the release notes.

Do not hallucinate. Do not invent commits. Do not use emojis. Do not use bold. Avoid marketing words.
