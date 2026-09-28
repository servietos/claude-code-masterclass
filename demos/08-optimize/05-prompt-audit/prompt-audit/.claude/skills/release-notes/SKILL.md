---
name: release-notes
description: Write release notes. Use when the user says "release notes", "write release notes", "draft release notes", "create release notes", "generate release notes", "make release notes", "release notes please", "notes for the release", "changelog notes".
---

# Release Notes

You are an expert technical writer.

STEP 1: Think step by step inside <scratchpad> tags before writing anything.
STEP 2: Run `git log --oneline v1.2.0..HEAD` to list the commits.
STEP 3: Read CHANGELOG.md.
STEP 4: Group the commits into Features, Fixes and Chores.
STEP 5: Write at most 100 words per group.
STEP 6: Output ONLY the release notes, nothing else.

IMPORTANT: Hold all findings until the very end. Do not narrate. No interim updates.

Do not hallucinate. Do not invent commits. Do not use emojis. Do not use bold. Avoid marketing words.

This format was tuned for claude-3-opus, which padded its answers.
