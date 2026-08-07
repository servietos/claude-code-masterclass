# Labs - Module 08: Optimizing the Agentic Harness & Continuous Learning

| Lab | Topic | Title | Track | Level | Time | Description |
|-----|-------|-------|-------|-------|------|-------------|
| 01 | Compression | [Compress a Bloated Harness with Caveman Mode](lab-01-caveman-compress.md) | Core | Intermediate | 1h | Compress a bloated CLAUDE.md by instructing Claude to rewrite it "as a caveman": terse, no articles, no hedging. Measure the token drop with tiktoken, verify behaviour is preserved, then codify the prompt as a reusable skill. |
| 02 | Metrics | [Evolve a Skill with Deterministic Experiments](lab-02-evolve-via-metrics.md) | Optional | Advanced | 1h 15m | Take an existing skill, measure its quality with a deterministic harness over `claude -p --output-format json`, then run an autoresearch loop (propose, evaluate, revert) to improve correctness and abort rate. Builds on the "manual x3, codify" pattern from Module 03. |
| 03 | Memory | [Compare Four Memory Architectures on the Same Recall Task](lab-03-memory-architectures.md) | Optional | Advanced | 1h 15m | Compare four memory architectures on one recall task: in-context prompt loading, an episodic statefile, the official MCP knowledge-graph memory server, and Claude Code's own auto-memory pinned into the lab folder. Measure every architecture with the same token counter, then audit both the ingestion schema and the write policy against the source corpus. |

**Core** is the one lab that teaches this module's central capability; run it if you run nothing else. **Optional** labs go deeper, cover a second tool, or need an account you may not have. **Level** rates the lab itself: Beginner needs no prior Claude Code experience, Intermediate assumes you have configured a harness before, Advanced assumes you are comfortable with hooks, subagents, or headless scripting.

Core path: 1h. All labs: 3h 30m.

Lab 01 is Core because the compression technique is immediately reusable on any project and the lab is self-contained.

Each lab has its own project inside this module's topic folders and ships a completed reference beside it. All three starters are already in the repo, so no lab scaffolds anything.

| Lab | You work in | Completed reference |
|---|---|---|
| 01 | [`01-compression/caveman-lab/`](01-compression/caveman-lab/readme.md) | [`01-compression/caveman-lab-solution/`](01-compression/caveman-lab-solution/readme.md) |
| 02 | [`02-evolution/release-notes-lab/`](02-evolution/release-notes-lab/readme.md) | [`02-evolution/release-notes-lab-solution/`](02-evolution/release-notes-lab-solution/readme.md) |
| 03 | [`03-memory/memory-lab/`](03-memory/memory-lab/readme.md) | [`03-memory/memory-lab-solution/`](03-memory/memory-lab-solution/readme.md) |

Lab 01's `caveman-lab` belongs to this module and is already checked in at `labs/08-optimize/01-compression/caveman-lab/`, so change into it and run `npm install` rather than creating anything.

Tooling the labs assume on `PATH`: Node and npm (Lab 01, Lab 03), Python 3.10 or newer with `tiktoken` installed in a per-lab virtual environment (all three labs), `git` and `jq` (Lab 02).
