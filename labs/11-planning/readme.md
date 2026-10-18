# Labs - Module 11: Planning & Spec-Driven Development (Optional)

| Lab | Topic | Title | Track | Level | Time | Description |
|-----|-------|-------|-------|-------|------|-------------|
| 01 | From Scratch | [Drive a Feature Spec-First with Plan Mode](lab-01-spec-driven-from-scratch.md) | Core | Beginner | 1h 15m | Build a feature for a small notes CLI by going through Plan Mode end-to-end: clarification, constraint iteration, Extended Thinking, statefile authoring, work packages with contracts, and verified execution. |
| 02 | With Tooling | [Run the Same Feature Through Spec Kit and BMAD-METHOD](lab-02-spec-kit-and-bmad.md) | Optional | Intermediate | 1h 15m | Repeat the same feature with the `speckit-*` skills that `specify init` installs, then compare the generated artifacts against BMAD-METHOD's agent-produced PRD, architecture and story files. See how packaged tooling formalises the workflow you just did by hand. |
| 03 | Harvest | [Harvest the Current State of a Bike Rental Shop](lab-03-harvest-current-state.md) | Optional | Intermediate | 50m | Map a running rental shop from its code, database schema, process notes and spreadsheet with parallel subagents that append cited bullets to one shared ledger, then turn the ledger into a current-state document with a gap list and spot-check its claims against the sources. |

**Core** is the one lab that teaches this module's central capability; run it if you run nothing else. **Optional** labs go deeper, cover a second tool, or need an account you may not have. **Level** rates the lab itself: Beginner needs no prior Claude Code experience, Intermediate assumes you have configured a harness before, Advanced assumes you are comfortable with hooks, subagents, or headless scripting.

Core path: 1h 15m. All labs: 3h 20m.

Lab 02 builds the same feature as Lab 01 with packaged tooling, so it only pays off once Lab 01 has given you the by-hand baseline to compare against.

Each lab has a starter project folder and a finished counterpart beside it named `<starter>-solution/`: `01-plan-mode/notes-cli/` and `01-plan-mode/notes-cli-solution/` for Lab 01, `02-tooling/notes-cli-speckit/` and `02-tooling/notes-cli-speckit-solution/` for Lab 02. Lab 03 starts from `03-harvest/bike-rental-shop/` and has no solution folder, because its result is the `ledger.md` and `current-state.md` you write. All starters are already in the repo, so no Setup scaffolds anything: it only installs and runs. The starter stays pristine (no virtual environment, no database, no generated spec folders); install, run and generate inside it as you work, and use the solution folder as the completed reference when you want to compare.
