# Create Teaching

Focus on the markdown file in the current folder and the content in its sub-folders.

$ARGUMENTS

**Process:**

1. Read a reference document if provided for tone/style guidance.
2. Read source files in the folder to extract key features and technologies.
3. Rewrite or enhance the description with: what it does + notable features.

**Output structure (in order):**

1. Description content
2. `## Helpful Claude Slash Commands` — 2-column table (Command | Usage) with slash commands relevant to the topic; never include `/create-teaching` or `/create-lab` — these are internal authoring commands
3. `## Key Topics covered in this module` — relevant documentation links; keep and update existing ones, or add the most relevant official docs if none exist

**Rules:**

- What each item demonstrates: use case, technology stack, and 1-2 standout technical details
- Separate multiple items with a paragraph
- Reference files and scripts by name with links where possible; use repo-absolute paths (starting with `/`) for assets outside the module's folder, relative paths for assets within it
- Validate image links; fix broken ones, add descriptive captions, and place images in the text flow where they fit
- Include code snippets only if relevant; update outdated ones in fenced code blocks
- No bold or italic in descriptions
- Max 3 sentences per paragraph
- Add prompts in fenced code blocks
