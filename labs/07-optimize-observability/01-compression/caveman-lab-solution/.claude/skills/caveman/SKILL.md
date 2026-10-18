---
name: caveman
description: Rewrite a prose harness file in caveman speech to cut its token cost while preserving every rule. Use when CLAUDE.md or a skill body has grown verbose and its token cost shows up in every turn.
---

# Caveman Compression

## When to use

When CLAUDE.md, a skill body, or any prose harness file has grown verbose and you want to reduce its token cost without losing rules.

## Steps

1. Read the target file in full.
2. Rewrite it in caveman speech:
   - Drop articles (a, an, the).
   - Drop copulas (is, are, was, were) wherever droppable.
   - Drop hedging (please, kindly, generally, usually, it would be good to, you should).
   - Imperatives only.
   - Preserve every rule with the same enforceability.
   - Preserve section headings and code fences exactly.
3. Save the result alongside the original as `<filename>.caveman.<ext>`.
4. Run a token counter on both and report the reduction percentage.
5. State whether rationale prose was kept or dropped, because that is the difference between roughly 50 and roughly 78 percent.
6. Recommend a behaviour parity test before replacing the original.

## Anti-patterns

- Do not merge sections to save tokens.
- Do not drop rules even if they seem redundant in the original.
- Do not "improve" rules: preserve their wording's effect, not their phrasing.
