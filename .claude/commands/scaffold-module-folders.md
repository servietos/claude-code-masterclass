# Scaffold Module Folders

$ARGUMENTS

Given the parent folder path and list of items above, create one subfolder per item with:
- A zero-padded numeric prefix (01-, 02-, 03-, …)
- A short 1-2 word folder name derived from the item's essence
- A `readme.md` inside each folder whose only content is `# <original item text>`
- A `pptx/` subfolder inside each folder, containing an empty `readme.md`

Rules:
- Folder names: lowercase, hyphen-separated, 1-2 meaningful words max
- File name: exactly `readme.md` (lowercase)
- Heading: exact original item text, prefixed with `# `
- No extra content in the readme files
- Create all folders and files in parallel

Expected usage:
```text
/scaffold-module-folders demos/01-fundamentals

Introduction to Claude Code
Setup & Installation
Editors
Context Engineering
```
