# Todo

## Merge 01-fundamentals topics 01, 02 and 03 into one short topic

Rationale: make room for advanced topics. Today `01-intro` (62 lines), `02-setup` (83) and
`03-editors` (47) repeat the same surfaces, extensions and install command three times, and two
claims are stale against code.claude.com/docs: npm with Node 18 is now an advanced option needing
Node 22, the native installer is recommended, and the Desktop app includes Claude Code.

Owner decisions (2026-10-23): keep the detail of the three master-TOC facets (Introduction,
Setup & Installation, Editors), so the page has one H2 per facet; npm stays as an optional appendix;
topics 04 to 08 renumber to 02 to 06.

### 1. New topic `01-get-started/readme.md` (H1 "Get Started with Claude Code", 165 lines)

- [x] "Introduction to Claude Code": the family as one table with the old per-product detail, why Claude Code, the `claude` examples
- [x] "Setup & Installation": native installer per OS, Homebrew and WinGet, sign-in, both VS Code extensions, verify with `claude --version`, `claude doctor` and a first prompt
- [x] "Editors: Terminal, Desktop App, VS Code": one H3 each plus Claude Code on the web; JetBrains and Cursor under VS Code
- [x] Slash commands `/login`, `/status`, `/doctor`, `/help` checked against code.claude.com/docs/en/commands
- [x] "Appendix: Install with npm (Optional)": Node.js 22 or later, npm install as a regular user on Windows
- [x] `01-intro/` moved to `01-get-started/`; `02-setup/` and `03-editors/` removed

### 2. Indexes

- [x] Module `readme.md`: one Topics row for the merged topic, labels renumbered; master TOC unchanged (facets, not folders)
- [x] 04..08 moved to 02..06 (`renumber-tree.sh`, then `git mv` by hand for the two .NET topics that held a lock)
- [x] Links repointed with `rewrite-links.py` (14 files; its unrelated trailing-slash edits in 11 files of modules 07, 08, 10, 11 reversed); prose paths, link labels and slide-spec `topic:`, `source:`, `media-file:` lines shifted (77 lines, 30 files); `.devcontainer/readme.md` .NET row
- [x] `dashboard/index.html` regenerated

### 3. Verify

- [x] `link-check.sh`: demos/01-fundamentals and labs/01-fundamentals 0 broken, 0 prefix defects
- [x] `link-rot.sh`: 14 of 16 URLs 200; claude.ai and claude.ai/code answer curl with 403 (bot block)
- [x] `fence-lang.py` 0 untagged; no em dashes or negative parallelism; brand-voice clean, the topic has no approved slash-command set in `rules.md`

### 4. Deck (owner: "yes update the deck", then "publish the update to onedrive")

- [x] OneDrive copy checked first: unchanged since the 2026-10-06 delivery, the repo deck only newer (notes on slides 3 and 5)
- [x] Specs and images renumbered with `permute-topic-specs.py` (02-01, 03-01 to 01-03, 01-04; 04..08 to 02..06; 38 moves)
- [x] Specs 00-02, 01-01, 01-03, 01-04: native installer, `claude doctor`, npm with Node 22 optional, Desktop includes Claude Code, six topics; SVGs 00-02, 01-03, 01-04 redrawn and swapped
- [x] `topics.json` six topics; `topics` rebuilt the overview and 6 dividers (31 slides to 29); `notes` 19 of 19, unmatched=0
- [x] `clean --skip 4` twice removed=0; `check_specs.py --legacy` problems=0 (9 pre-existing mix warnings); sheet and slides 10, 11 checked at full size
- [x] Delivered to OneDrive; `cmp` PPTX and PDF identical

Not touched: `labs/01-fundamentals/01-setup-claude` (still npm and Node 18), `pdf/handout.md`.

## Teach the plugin side of `.claude/rules/` in 08-distribution

Subject (owner, 2026-10-23): a plugin from a marketplace brings its own expert, and the expert gets
each repo's details from a rule. Example: `copilot-work-iq` from `integrations-marketplace`, its
`copilot-studio-expert`, and a repo's `.claude/rules/copilot-studio.md`. `02-harness` and `03-skills`
rules teaching stay as they are.

Owner decisions (2026-10-23): topic folder `05-repo-rules`; no demo, no lab; slides in the 08 deck;
an animated opener built on the Copilot Studio plugin; diagrams carry only a fixed label list.

- [x] Mechanism checked in the docs: no plugin component is a rules file, a plugin-root `CLAUDE.md`
  is not loaded, `paths` is the only field a rule reads, plugin agents carry a namespaced name
- [x] `05-repo-rules/readme.md`: expert from the marketplace, the repo's rule, the expert reads it first
- [x] Module `readme.md` Topics row, opening bullet; `demos/readme.md` TOC bullet; demo removed
- [x] `_images/plugin-repo-rules-overview.svg`: animated; Copilot Studio plugin with its agent and two skills installs into `~/.claude (global)`, the expert reads the real sections of `copilot-studio.md`
- [x] Specs `05-01` to `05-03` (diagram, split-code, diagram), `topics.json`, `99-01` order 20
- [x] SVGs and PNGs for `05-01` to `05-03`
- [x] Deck: three slides and the opener GIF after the divider, `normalize_cards`, `clean`, `notes`,
  `slide_quality.py` problems=0, delivered to OneDrive (pptx and PDF identical to the repo copies)
- [x] `link-check.sh` broken=0, `fence-lang.py` 0 untagged, no em dashes or negative parallelism

## 1. Verify the mechanism (official docs)

- [x] Plugin component list has no rules; a plugin-root `CLAUDE.md` is not loaded (`plugins-reference.md:665`)
- [x] `paths` is the only field a rule reads (`memory.md:246`); custom subagents load CLAUDE.md and project rules
- [x] Plugin agents ignore `hooks`, `mcpServers`, `permissionMode`; plugin hooks get `CLAUDE_PROJECT_DIR` (`hooks.md:480`)

### 2. Topic `05-plugins-and-repo-rules` (H1 "Give a Plugin Each Repo's Facts")

- [x] `readme.md`: opener SVG under the H1, then concept sections: a plugin ships global components;
  the repo half lives in `.claude/rules/<area>.md`; the `Owner agent:` line; a plugin agent reads its
  rules file first; a fenced JSON block in a rules file as config for a plugin hook; a plugin that
  scaffolds the area files; how our marketplace runs it. Slash-command table, Key Topics links
- [ ] `_images/plugin-repo-rules-overview.svg`: 1920x1080, animated (SMIL, static first frame shows
  every label), style from `pptx/images/03-01-what-moves.svg`, drawn by `image-producer`
- [x] Demo `demo-repo-rules.md` + presenter guide; starter `demo-repo-rules/` and
  `demo-repo-rules-solution/` (`acme-review-plugin` + `pricing-service`)
- [x] Module `readme.md`: opening bullet, Topics and Demos rows; `demos/readme.md` TOC bullet

### 3. Slides (`finished-deck-edits`, no Gamma)

- [x] Specs `05-01` to `05-04` (diagram, split-code, diagram-full, diagram), `topics.json`, `99-01` order 21
- [ ] SVGs drawn by `image-producer`, PNGs rendered
- [ ] `add_spec_slide.py` x4 after slide 24, `topics --footer`, opener GIF via `svg-gif` + `image-slide`
- [ ] `normalize_cards`, `clean` twice, `notes`, `sheet`, `slide_quality.py`, `deliver` (repo deck newer than OneDrive's)

### 4. Verify

- [x] Demo run headless (Claude Code 2.1.309): skill falls back without the file, scaffold writes
  it, `review-lead` delegated by `subagent_type`, `path_glob_match` logged, `freeze-guard` denies;
  PowerShell wiring gives the same deny and log; empty `frozen` lets the edit through
- [x] `fence-lang.py` 0 untagged, doc links 200, no em dashes or negative parallelism, brand-voice
  (`/agents` row replaced by `/plugin`, rule 7); topic has no approved slash-command set in `rules.md`
- [ ] `link-check.sh` once the opener exists; render the opener and check every frame

## Teach `.claude/rules/` as the repo-facts contract of global skills

Rationale: the course teaches rule mechanics (`02-constitution`) and the global sub-agent case
(`06/01-introduction:113`), never the global-skill side that the estate runs on: a skill names a
fixed rules file (`seo.md`, `content.md`, `docs.md`) and reads it first, because a path-scoped rule
is absent until Claude touches a matching file. Core class time about 10 min, lab optional.

### 1. Image hosting for Gamma (global skill `create-pptx`)

- [x] Prove the route with one 1-card Gamma call whose image URL carries a SAS token (2026-10-20: Gamma embedded the 04-01 diagram, 26 credits)
- [x] Storage account `integrationsmediacreator`, named by the owner
- [x] Private container `slide-production`, upload `<class>/<module>` per run, read-only user delegation SAS valid 4h, lifecycle rule deletes after 7 days
- [x] `gamma_deck.py prompt`: new `--url-suffix` appends the SAS query to every image URL
- [x] `gamma-deck.md:119-120`: private repos use the Azure route; raw GitHub stays for public repos
- Gamma reads the pictures while it generates and the exported PPTX embeds them, so the URLs die after 4h and nothing stays public
- This task spends no Gamma credits: the new cards go into the finished decks locally (`finished-deck-edits`)

### 2. Slide variety (global skill `create-pptx`)

Cause: every spec is bullets plus one side image, and `normalize_cards.py` restacks every card
into one of two layouts (diagram card, photo card).

- [x] Spec `layout:` archetypes: `diagram-full` (full-width diagram, one-line caption), `split-code` (file or code panel beside a diagram), `statement` (one sentence beside a supporting image)
- [x] `add_spec_slide.py` builds each archetype on the deck's own master (theme, Montserrat, Poppins)
- [x] `normalize_cards.py` leaves archetype cards as built
- [x] The Gamma prompt builder maps each archetype to a layout line for future decks
- [x] `check_specs.py` accepts a 1920-wide viewBox of any height for `diagram-full`

### 3. Teaching

- [x] `demos/02-harness/02-constitution/readme.md:124-132`: table row "Facts a global skill or agent reads" plus the load-timing sentence
- [x] `demos/03-skills/05-test-and-package/readme.md`: section "Give a Global Skill Your Repo's Facts" after "What Ships and What Stays Behind", Key Topics list
- [x] `demo-test-and-package-a-skill.md` and its presenter guide: 5-minute segment where the starter's skill moves its repo facts into `.claude/rules/`, starter and solution updated
- [x] `labs/03-skills/lab-06-*.md` with starter and solution, Optional, Advanced, about 20m: a repo-agnostic skill reads `.claude/rules/<area>.md` with `paths:`, an `InstructionsLoaded` hook shows it loads only on a match, the same skill runs against a second rules file
- [x] Row in `labs/03-skills/readme.md`; Topics and Demos tables in `demos/03-skills/readme.md` where affected
- [x] `brand-voice-code` pass on every changed file; grep for em dashes and negative parallelism

### 4. Slides (`finished-deck-edits`, no Gamma)

- [x] `02-harness`: spec `02-01` bullets and SVG get the fourth table row; `swap-image`, run-level text edit
- [x] `03-skills`: new spec `05-04` in a non-default archetype, SVG drawn by `image-producer`; `add_spec_slide.py`; renumber `99-01`
- [x] Per deck: `notes`, `clean` twice, `sheet`, look at every changed page; `cmp` against OneDrive, then `deliver` (2026-10-20, both decks identical to OneDrive after delivery)

### 5. Verify

- [x] Run the demo segment and the lab in a real session: the `InstructionsLoaded` log shows the rule loading only on a match (`path_glob_match` with `trigger_file_path` src/pricing.ts, absent in the run that read no src file)
- [x] Contact sheets of both decks, every changed slide checked

## Replace 01-fundamentals topic 05 with prompt caching

Rationale: `05-prompting-techniques` duplicated four of its five sections from
`04-constitution`, `02-harness/03-commands` and `08-optimize/04-memory-architectures`.
Prompt caching was taught nowhere in the course. Topic 06 stays: model choice is a
day-one decision and a model switch is one of the main cache invalidators.

- [x] Verify every cache claim against `code.claude.com/docs/en/prompt-caching.md` and `costs.md`
- [x] Create `05-prompt-caching/readme.md`
- [x] Create `05-prompt-caching/demo-cache-hit-rate.md`
- [x] Create the `cache-lab/` starter (no build, no dependencies)
- [x] Move the few-shot output-shape technique into `04-constitution/readme.md`
- [x] Trim the Console billing walkthrough out of `06-model-selection/readme.md`
- [x] Repoint the forward links in `04-constitution/demo-claude-md-constitution.md` and `06-model-selection/demo-model-routing.md`
- [x] Update the module `readme.md` Topics and Demos tables
- [x] Repoint the .NET 10 SDK row in `.devcontainer/readme.md` at `model-routing-api`
- [x] Delete `05-prompting-techniques/`
- [x] Run the brand-voice rules over every changed readme
- [ ] pptx specs `05-01` through `05-05` still describe the removed topic (out of scope, owner's call)

### Corrections the docs forced on the original plan

- Editing CLAUDE.md mid-session does **not** invalidate the cache. The edit also does not apply.
  This became Step 4 of the demo, because the failure mode is silent.
- `/usage` is the command that reports cache read and cache write tokens. `/cost` is an alias.
- An MCP server change only invalidates the cache when its tools load into the prefix. Deferred
  tools, the default on supported models, are safe.
- Exact cache write multipliers were left out of the course page. The Claude Code docs say only
  "a higher rate" for the one-hour TTL and "roughly 10%" for reads, so the page uses that wording.

### Review

Topic 05 is now prompt caching, teaching the three-layer prefix, the full invalidation and
safe-action lists, TTL selection by authentication method, per-directory cache scope, subagent
versus fork cache behaviour, and reading `cache read` against `cache write` in `/usage`.

The demo runs on `cache-lab/`, a dependency-free TypeScript sample with nothing to install.
Six steps: cold baseline, warm the cache across three turns, break it with `/model`, prove the
mid-session CLAUDE.md edit is inert until `/clear`, compare `/compact` with `/rewind`, then
write the discipline into CLAUDE.md. Every reading lands in `CACHE-NOTES.md`.

Brand-voice: no em dashes in the new prose, Mermaid uses quoted `<br/>` labels, no paragraph
over 4 sentences, all four documentation links verified 200. Rule 7 forced a module-wide switch
from `/cost` to `/usage`, applied to `06-model-selection/demo-model-routing.md` and the module
readme. The prompt caching topic is not in the approved slash-command table in
`brand-voice-code/references/rules.md`, so its set (`/usage`, `/context`, `/rewind`, `/compact`,
`/effort`) is flagged rather than matched to an existing row.

Not done: `labs/01-fundamentals/lab-03-prompting-techniques-and-plugins.md` still teaches the
five prompting techniques. It is self-contained, scaffolds its own project, and depends on
nothing that was deleted, so it was left in place.

## Move 07 topic 02 and lab-01 token counts to count_tokens

Blocked on a working `ANTHROPIC_API_KEY`: the four keys in the repo's `.env` files return 401.

- [ ] Swap `js-tiktoken` for `@anthropic-ai/sdk` 0.135.0 in both `count-tokens.ts` and `package.json` files of `02-caveman-compression`, counting against `claude-opus-5-5`
- [ ] Swap `tiktoken` for `anthropic` 1.15.0 in the lab's `tokens.py`
- [ ] Re-measure every demo and lab file and regenerate both `baseline.txt` files
- [ ] Update the counts in the topic readme bar table, demo, presenter guide, lab Steps 1 and 3, solution readme and the caveman `SKILL.md` band
- [ ] Add `ANTHROPIC_API_KEY` to the guides' prerequisites and a Module 07 row in `labs/readme.md`
- [ ] Update the caveman slides in `demos/07-optimize-observability/pptx/`
