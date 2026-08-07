---
name: create-module-pptx
description: >-
  Build a real PowerPoint deck for a module in demos/ using the slide generator
  bundled in this skill's own build/ folder. Distils the module's topic readmes and
  presenter guides into an essentials-only slide set, writes it as generator YAML
  into that module's pptx/ folder, renders the .pptx, and validates it. Trigger
  phrases: create slides, create module pptx, generate slides, build the module
  deck, topic to slides, pptx from readme, make a deck.
tools:
  - Read
  - Write
  - Glob
  - Bash
---

# Create a Module Deck

$ARGUMENTS

Turn one module's topic readmes into a rendered `.pptx`, built by the generator this
skill carries. No external service is involved.

## The generator ships with the skill

Everything the build needs lives under this skill folder, so it runs in any checkout:

- `build/`: the renderers (`build_pptx.py`, `layouts.py`, `diagrams.py`, `design.py`,
  `helpers.py`, `theme.py`, `diagram_engines.py`) plus `lint_content.py` and
  `validate.py`
- `images/icons/`: the module and role icons the renderers resolve by name. The
  `divider` slide picks up `module-NN.png` from here on its own.

The only external requirements are Python with `python-pptx`, `pyyaml` and `lxml`,
and, for `diagram_type: d2` only, the `d2` binary on `PATH`. Nothing else is fetched.

### Delivery mechanics

Four scripts sit beside the renderers for the steps after a deck builds. Each takes
the deck path, so they work for a module deck and for a combined one alike:

| Script | What it does |
|---|---|
| `build/make_pdf.sh <deck.pptx>` | LibreOffice export re-distilled through Ghostscript. Needed because LibreOffice embeds variable fonts as Type-3, which crashes Acrobat on open |
| `build/package.sh <deck.pptx> <NAME> <VERSION> [LANG]` | Writes the versioned client pair into `<deck folder>/dist/` |
| `build/fetch_icons.py` | Downloads Lucide SVG icons, recolors them by stroke attribute, rasterizes to PNG for `images/icons/` |
| `build/demo_engines.py` | Smoke-tests the `d2` and chart diagram types end to end through `render_deck` |

## Inputs

`$ARGUMENTS` is a path to a module root, for example `demos/01-fundamentals`.
If no path is given, ask for one before proceeding.

## Outputs

Both land in that module's `pptx/` folder:

- `module-NN.yaml`: the slide content, in the generator's schema
- `module-NN.pptx`: the rendered deck

## The slide budget is the point of this skill

Four slides are always frame: `divider`, `objectives`, `lab`, `takeaways`. Everything
else is topic budget, and the budget is **2 to 4 slides per topic**, never more.

| Topics in the module | Deck size |
|---|---|
| 4 | ~20 |
| 6 | 20 to 26 |
| 9 | 20 to 26 |
| 10 | 25 to 28 |

Spend the budget unevenly on purpose. Give the extra slide to the topics carrying the
most mechanism (the longest readmes, the ones with a real procedure), and hold the
thin topics to two. Say in the summary which topics got extra and why.

This is a distillation task, not a summarisation task. For each topic, name the single
idea a developer must leave the room knowing, build the slides around that, and drop
the rest. The readme remains the reference; the slide is the hook.

A deck that runs past ~28 slides stops being a teaching deck and becomes a document
that nobody presents.

## Steps

### 1. Resolve the module

Glob `[0-9][0-9]-*/readme.md` directly under the module root. Read the module's own
`readme.md` for the topic table, the module title, and the schedule row that gives
`day` and `time`. Glob `[0-9][0-9]-*/demo-presenter-*.md` as well: those are the
second source, and step 3 says what to take from them.

### 2. Read the schema

Read `references/slide-schema.md` in this skill folder. It lists every slide type,
every field, and the length limits. Do not invent fields: an unrecognised field is
silently dropped by the renderer.

### 3. Distil each topic

For each topic readme, extract:

- the one idea that must survive
- the most concrete artifact in the topic: a real command, a settings key, a
  measured number, a file path

Then choose the slide type that fits **that** material. Vary the types across the
module. A deck where every slide is `bullets` teaches nothing that a readme does not,
and more than four slides sharing one `diagram_type` reads as a template.

Prefer, in rough order: `diagram` (comparison, decision, architecture, flow),
`terminal`, `code`, `table`, `content`, `bullets`. Use `statement` once or twice as a
pivot, never more.

Give every `terminal` and `code` slide a `side` rail. The panel is sized to its own
lines and leaves the right third of the slide empty otherwise, and that space is
where the prerequisite, the trap or the cost belongs. The rail never restates the
panel's lines; if all you can put there is a paraphrase, leave it off.

### 3b. Take the recipes from the presenter guides

A topic readme states the idea; the `demo-presenter-<slug>.md` beside its demo already
holds the idea reduced to a beat, and that is what a slide is. Read every presenter
guide in the module and mine three things:

- **The recipe.** The quoted command, prompt, settings block or script fragment under
  a beat. It has been run, so it is the concrete artifact step 3 asks for. Lift it
  onto a `code` or `terminal` slide and keep it byte for byte, only trimming lines to
  fit the panel limits. Never paraphrase a recipe into prose.
- **The Result.** What the run actually returned: the JSON envelope, the exit code,
  the measured turn count and cost. These are recorded numbers, so put them on the
  slide as output lines rather than predicting what a run would print.
- **The Gotcha and the "If the room asks" table.** This is rail and `notes` material.
  A Gotcha is exactly the trap the `side` rail exists to carry, and it never restates
  the panel, which is the rule the rail already has to satisfy.

Not every beat earns a slide. A four-beat guide against a two-slide topic budget means
picking the one or two beats that carry the topic's single idea and dropping the rest;
the guide stays the reference for delivery. Where a module ships each script twice
(`.sh` and `.ps1`), the guide's **Shell** line names the differences that are fatal
rather than merely different: that belongs in a rail item or a `content` column, not
in a second slide.

A topic with no demo has no presenter guide. Distil it from the readme alone.

### 4. Write the YAML

Write `<module-root>/pptx/module-NN.yaml`. Start with the header keys
(`module`, `title`, `day`, `time`, `chapter`, `chapter_total`, `chapter_label`),
then `slides`.

Every slide carries `notes`: one or two sentences telling the presenter what to
emphasise and what to skip under time pressure.

### 5. Lint the YAML before building

Run every command below from the repo root. `SKILL` is this skill's folder.

```bash
SKILL=.claude/skills/create-module-pptx
python $SKILL/build/lint_content.py demos/01-fundamentals/pptx/module-01.yaml
```

PowerShell: `$SKILL = ".claude/skills/create-module-pptx"`, then the same three
commands with `$SKILL/build/...`.

This catches what the build cannot: a field the renderer does not read (the content is
silently dropped), a `caption` on a type that discards it, a one-sided `variant`, and
every length limit. It must report `findings: 0`.

### 6. Build

```bash
python $SKILL/build/build_pptx.py \
  --content demos/01-fundamentals/pptx/module-01.yaml \
  --out demos/01-fundamentals/pptx/module-01.pptx \
  --no-opener
```

`--no-opener` omits the course chapter opener, which belongs to a combined deck, not
to a standalone module deck.

### 7. Validate, and prove it opens

```bash
python $SKILL/build/validate.py demos/01-fundamentals/pptx/module-01.pptx
```

`Total findings: 0` is the pass condition. Two failure classes matter:

- `NON-INTEGER-COORD`: a renderer leaked a float into an OOXML coordinate. PowerPoint
  refuses the file outright with "PowerPoint could not open the file". Fix the
  renderer in `$SKILL/build/`, never the YAML.
- `TEXT-overflow` / `OOB-*`: content spills off the slide. Shorten the YAML text.

A clean validator run is necessary but not sufficient. Confirm the file actually
opens:

```powershell
$pp = New-Object -ComObject PowerPoint.Application
$d = $pp.Presentations.Open("<abs path>.pptx", $true, $false, $false)
Write-Output "OK slides=$($d.Slides.Count)"; $d.Close(); $pp.Quit()
```

### 8. Print a summary

    module-01.yaml   16 slides   10 topics
    module-01.pptx   built, validator findings: 0, opens in PowerPoint: yes

    Two slides granted to: 04-constitution, 05-prompt-caching
    Types used: diagram x6, terminal x3, code x2, table x2, statement x1, ...

## Write it right the first time

Every limit below has produced a real lint finding. Writing to them costs nothing; a
patch round after the lint costs a full pass over the file.

| Element | Limit | Where it bites |
|---|---|---|
| Slide title | 45 | every type |
| List item (`objectives`, `takeaways`, `bullets`, `lab` steps, column items) | 60 | the two frame types are the usual offenders |
| `subtitle` | 60 | shorter than a list item, and easy to miss |
| Table cell | 55 | 5 body rows, 2 columns |
| `side` rail item | 44 | the tightest limit in the schema |
| `side` rail heading | 30 | |
| Code line beside a rail | 56 | plain code lines allow more, so a rail added later breaks them |
| Terminal line beside a rail | 50 | |

Two shapes the linter cannot forgive:

- `caption` on a `decision`, `comparison`, `table`, `bullets`, `content` or `callout`
  is read and then discarded. The linter names the type and tells you to move it to
  `subtitle`. Only `code`, `terminal`, `flow` and `architecture` render one.
- A field that does not exist on the type is dropped in silence, so `outcome` on
  `takeaways` or `caption` where `subtitle` was meant loses the line without any
  error at build time.

### Quote prose scalars by default

A plain YAML scalar ends at the first `: `, so a colon inside a `notes`, `subtitle`,
`text`, `caption` or `desc` value fails the load with `mapping values are not allowed
here` and a line number. This is the single most common authoring error in this skill,
and it survives review because the sentence reads correctly.

Write prose values quoted from the start:

```yaml
  notes: "Splitting sidesteps it: each agent gets what it needs."
  subtitle: "One rule: pipeline unless a stage needs the whole set"
```

Rewriting the sentence to avoid the colon is equally fine, and often better prose.

## The chapter map

`chapter`, `chapter_total` and `chapter_label` go in the file header beside `module`
and `day`. They are not divider-only: the label rides the header of every content
slide. Keep them consistent across modules:

| Modules | chapter | chapter_label |
|---|---|---|
| 01, 02 | 1 | Foundations |
| 03 | 2 | Extending the Agent |
| 04 | 3 | Connecting Systems |
| 05 | 4 | Automation |
| 06, 07 | 5 | Planning and Teams |

`chapter_total` is 5. Leaving the keys out falls back to a derived map that does not
follow `demos/` numbering.

## Rules

- No em dashes in any field. Use a comma, colon, semicolon, or parentheses.
- Titles are title case with no trailing period, max 45 characters.
- Lint before you build. `lint_content.py` catches every limit above plus the
  discarded-field shapes; the build itself reports none of them.
- Mermaid is not a slide type here. Diagrams are rendered natively by
  `diagram_type`, or as D2 source via `diagram_type: d2`.
