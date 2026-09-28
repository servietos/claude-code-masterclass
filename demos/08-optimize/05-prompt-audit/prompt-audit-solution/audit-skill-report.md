**Scope:** `.claude/skills/release-notes/SKILL.md` (only file in the skill). **Target model:** Claude Opus 5.5 (the model running this audit; the skill pins no model). The file is untracked, so there is no git blame and provenance comes from its idioms and line 21. Language is not relevant here; the surface is agent configuration only.

**Summary:** The skill is written for claude-3-opus, and line 21 says so. Three lines now work against Opus 5.5: the scratchpad incantation, the no-narration suppressor and the 100-word cap. Two facts it depends on are also missing from the repo: there is no `CHANGELOG.md` and no `v1.2.0` tag.

Counts: Group 1 has 7 findings, Group 2 has 3, Group 3 is not applicable (no tools) and Group 4 is not applicable (no request code).

| # | Location | Evidence | Pattern | Why obsolete | Confidence | Action |
|---|---|---|---|---|---|---|
| 1 | SKILL.md:21 | `This format was tuned for claude-3-opus, which padded its answers.` | 1d model-version workaround | A retired model's mitigation. It is also the stated reason for lines 14 and 17. | High | remove |
| 2 | SKILL.md:10 | `Think step by step inside <scratchpad> tags` | 1b scaffold replaced by API feature | Thinking is always on in Opus 5.5 and depth is set by `effort`. Asking for reasoning in the output can trigger a `reasoning_extraction` refusal. | High | replace-with-API-feature (`effort` frontmatter if wanted) |
| 3 | SKILL.md:17 | `IMPORTANT: Hold all findings until the very end. Do not narrate. No interim updates.` | 1d update suppressor | Opus 5.5 already under-narrates, so this makes it look silent. | High | remove |
| 4 | SKILL.md:14 | `Write at most 100 words per group.` | 1b/1f numeric cap | A cap tuned against claude-3-opus padding (line 21) that now cuts real content. | High | rewrite |
| 5 | SKILL.md:12 | `Read CHANGELOG.md.` | 2 volatile specifics | There is no `CHANGELOG.md` in the project. | High | rewrite (proposed only) |
| 6 | SKILL.md:11 | `git log --oneline v1.2.0..HEAD` | 2 volatile specifics | The repo has no `v1.2.0` tag. | High | rewrite (proposed only) |
| 7 | SKILL.md:10-15 | `STEP 1:` … `STEP 6:` | 1c step choreography | A hand-written script for a judgment task. Only "list commits, then group them" needs an order. | Medium | rewrite |
| 8 | SKILL.md:19 | `Do not use bold.` | 1d anti-formatting rule | Strips formatting a reader may want, and no reason is given. | Medium | remove |
| 9 | SKILL.md:19 | `Do not use emojis. … Avoid marketing words.` | 1e prohibition cluster (style, no provenance) | Style bans written against older models' habits. | Medium | rewrite positively |
| 10 | SKILL.md:3 | `"release notes", "write release notes", "draft release notes", …` | 2 trigger-case enumeration | Nine near-synonyms instead of one intent category. | Medium | rewrite |
| 11 | SKILL.md:19 | `Do not hallucinate.` | 1c signal | Idiom only; its companion `Do not invent commits` carries the real constraint. | Low | flag |

Kept: line 8 (a one-line role statement), `Do not invent commits` (a real constraint) and the Features/Fixes/Chores grouping (the author's own format).

**Proposed diff** (not applied; hunks 5 and 6 need your confirmation):

```diff
@@ finding 10: description
-description: Write release notes. Use when the user says "release notes", "write release notes", "draft release notes", "create release notes", "generate release notes", "make release notes", "release notes please", "notes for the release", "changelog notes".
+description: Write release notes from the git history since the last release. Use when the user asks for release notes or changelog notes in any phrasing.
```

```diff
@@ findings 2, 7: scaffold and step choreography
-STEP 1: Think step by step inside <scratchpad> tags before writing anything.
-STEP 2: Run `git log --oneline v1.2.0..HEAD` to list the commits.
-STEP 3: Read CHANGELOG.md.
-STEP 4: Group the commits into Features, Fixes and Chores.
-STEP 5: Write at most 100 words per group.
-STEP 6: Output ONLY the release notes, nothing else.
+List the commits since the last release, then group them into Features, Fixes and Chores. Output only the release notes.
```

```diff
@@ findings 5, 6: stale path and tag (proposed only)
+List the commits with `git log --oneline $(git describe --tags --abbrev=0)..HEAD`, or the full history when the repo has no tag.
```

```diff
@@ finding 4: numeric cap
+Keep each group scannable: one line per change, merging commits that describe the same change.
```

```diff
@@ finding 3: update suppressor
-IMPORTANT: Hold all findings until the very end. Do not narrate. No interim updates.
```

```diff
@@ findings 8, 9: style prohibitions
-Do not hallucinate. Do not invent commits. Do not use emojis. Do not use bold. Avoid marketing words.
+Do not invent commits: every line traces to a commit in the range. Write in plain, factual language.
```

```diff
@@ finding 1: fossil
-This format was tuned for claude-3-opus, which padded its answers.
```
