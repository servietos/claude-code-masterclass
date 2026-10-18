# agents-sandbox

Three small, unrelated modules used by the agents view demo. Each one is a separate chore for a separate background session, and no two chores touch the same file.

| File | Chore it carries |
|---|---|
| `src/greet.js` | Undocumented exports |
| `src/parse.js` | No input validation; throws on malformed input |
| `src/format.js` | No tests |

The demo runs in place: this course repository is already a git repository, which is all a background session needs to isolate itself into a worktree under `.claude/worktrees/`.