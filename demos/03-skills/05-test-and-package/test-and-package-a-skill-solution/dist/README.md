# Code Reviewer

Ask for a second opinion on your changes in plain language and get back a merge decision you can act
on: blocking problems separated from suggestions, every finding pinned to a file and line, and an
explicit statement of what the change is missing in tests. It works on what you have not committed
yet, on a whole branch, and on a Pull Request someone else opened.

## Install in Claude Code

1. Copy the `code-reviewer/` folder into `.claude/skills/` in your project, or into
   `~/.claude/skills/` to have it everywhere.
2. Start Claude Code in that project. The skill loads itself when a request matches; nothing to enable.

## Install in Claude.ai

1. Zip the `code-reviewer/` folder so the archive contains the folder, not a loose `SKILL.md`.

   ```powershell
   Compress-Archive -Path code-reviewer -DestinationPath code-reviewer.zip
   ```

   ```bash
   zip -r code-reviewer.zip code-reviewer
   ```

2. Open Settings > Capabilities > Skills and upload the zip.
3. Toggle the skill on.

## Try it

```text
Can you go through my diff before I push? I do not want to break anything.
```

You get a Summary, a Critical / Improvements / Nitpicks split, a Test Coverage line, and either
Approved or Request Changes.

## Requirements

`git` on the PATH. Pull Request review additionally needs the GitHub CLI (`gh`) authenticated; local
and branch review work without it.

## Measured impact

Not yet measured. The comparison protocol and the reason this run could not execute it are recorded in
the skill's own `tests/baseline-comparison.md`. No before and after figures are quoted here until two
real sessions have been captured.
