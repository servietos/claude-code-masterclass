# Todo

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
