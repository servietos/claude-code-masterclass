# Slide Schema

The authoritative renderer set is `build/layouts.py` in this skill folder. A field not
listed here is silently ignored by the renderer, so inventing one loses content
without raising an error.

Every slide is a YAML mapping with a `type` key. Every slide may carry
`notes: "<presenter sentences>"`, which lands in the PowerPoint speaker notes.
Always write notes.

## Frame types

| Type | Fields |
|---|---|
| `divider` | `module_number` (int), `title`, `time`, `subtitle?`, `icon?` |
| `objectives` | `title`, `items` (max 6 strings), `subtitle?` |
| `lab` | `title`, `duration`, `steps` (max 5 strings), `outcome` |
| `takeaways` | `title`, `items` (max 5 strings), `subtitle?` |

## Content types

| Type | Fields |
|---|---|
| `bullets` | `title`, `items` (3 to 5 strings), `subtitle?` |
| `content` | `title`, `columns` (2 entries of `{heading, items}`), `subtitle?` |
| `table` | `title`, `headers` (2 strings), `rows` (max 5 pairs), `subtitle?` |
| `code` | `title`, `language`, `code` (block scalar), `caption?`, `subtitle?`, `side?` |
| `terminal` | `title`, `window`, `lines` (list of `{t, text}`), `caption?`, `subtitle?`, `side?` |
| `callout` | `title`, `text` (one strong sentence), `subtitle?` |
| `statement` | `kicker`, `text`, `attribution?`. **No `title` field.** |
| `quote` | `text`, `author` |
| `chart` | `title`, `chart_type`, `series`, `value_suffix?`, `note?` |
| `discussion` | `title`, `prompt` |

`terminal` line kinds (`t`): `comment`, `cmd`, `out`, `ok`, `err`.

## The two-column option

A `terminal` or `code` panel is sized to its own lines, so on its own it leaves
the right third of the slide empty. `side` fills that space with a companion
card and turns the slide into two columns:

```yaml
- type: terminal
  title: Install, Authenticate, Verify
  window: claude
  lines:
    - { t: cmd, text: "node --version" }
  side:
    heading: "Before you start"        # max 30 chars
    items:                             # max 5, each max 44 chars
      - "Node.js 18+ is the only hard dependency"
```

The rail carries what the session does not show: the prerequisite, the trap,
the cost. Never restate the panel's own lines. Both cards render at the same
height, so a rail with five items also gives the panel more room.

Two length rules apply only when `side` is present, because the panel is
narrower: terminal lines cap at 50 characters and code lines at 56. Past that
the whole block renders one size down. `lint_content.py` enforces all of it.

A `side` and a `caption` compete for the same explanation. Prefer the rail, and
keep `caption` for a single line that belongs directly under the panel.

## Diagram types

`type: diagram` always carries `title`, `diagram_type`, and an optional `caption`.
The remaining fields depend on `diagram_type`:

| `diagram_type` | Fields |
|---|---|
| `comparison` | `left` and `right`, each `{heading, items, variant?}`; `variant` is `good` or `bad` |
| `architecture` | `rows`: a list of rows, each row a list of `{label, role, icon?}`; `role` is `primary`, `secondary`, or `wide` |
| `decision` | `nodes`: max 4 entries of `{q, a}` |
| `flow` | `steps`: max 5 entries, each either a plain string or `{label, desc}` |
| `sequence` | `actors` (list of strings), `messages` |
| `metrics` | `cards`: list of `{value, label}`, `highlight_index?` |
| `quadrant` | `quadrants`, `x_axis`, `y_axis` |
| `d2` | `d2`: a D2 source block scalar |

`architecture` rows are a **list of lists**. One inner list per stacked row:

```yaml
rows:
  - - { label: "~/.claude/CLAUDE.md: global, personal", role: "wide" }
  - - { label: "<repo>/CLAUDE.md: team rules, checked in", role: "primary" }
```

## File header

A module content file starts with these top-level keys, then `slides`:

```yaml
module: 1
title: "Claude Code Fundamentals"
day: 1
time: "09:00 - 10:30"
slides:
  - type: divider
    ...
```

## Renderer traps

These are verified against `layouts.py` and `diagrams.py`. Each one loses content or
misleads the audience without raising any error at build time.

1. **`caption` is only rendered by `code`, `terminal`, and `diagram_type` `flow` and
   `architecture`.** On `comparison`, `decision`, `table`, `bullets`, `content` and
   `callout` it is read from the YAML and then discarded. Put the point in `subtitle`
   or in a list item instead.
2. **A one-sided `variant` on a comparison paints the other side red.** The renderer
   only goes neutral when *neither* side sets `variant`. Set it on both sides or on
   neither, and reserve it for a genuine safe-versus-dangerous contrast.
3. **Terminal line kind `err` is accepted but not styled**, rendering identically to
   `out`. If a line is a warning, carry the signal in the text (`"WARN: ..."`).
4. **Keep `terminal` to 9 lines or fewer.** The renderer measures the block and
   steps the type down until it fits, so nothing spills any more, but a tenth
   line buys a smaller font rather than more teaching.
5. **A `flow` step box is small.** Keep `label` under 22 characters and
   `label` plus `desc` under 56, or the text spills out of the box.

`build/lint_content.py` checks all four, plus the length limits below.

## Length limits

The deck validator flags text that overflows its box. Stay inside these:

| Element | Limit |
|---|---|
| Slide title | 45 characters |
| Bullet or list item | 60 characters |
| Table cell | 55 characters |
| Table rows | 5 body rows, 2 columns |
| `decision` nodes | 4 |
| `flow` steps | 5 |
| `objectives` items | 6 |

## Reference file

`demos/01-fundamentals/pptx/module-01.yaml` is a working file that exercises most of
these types. Read it when a field shape is unclear.
