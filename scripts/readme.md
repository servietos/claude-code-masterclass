# Scripts

## install-class-windows.ps1

Installs the class toolchain natively on Windows, so a learner can run every module without Docker or the dev container. It mirrors `.devcontainer/devcontainer.json` and `.devcontainer/post-create.sh`.

### Prerequisite

`winget` (ships with Windows 11, otherwise install **App Installer** from the Microsoft Store). Run the script from an elevated terminal so the machine-wide installers do not prompt.

### Run

```powershell
pwsh ./scripts/install-class-windows.ps1
```

```powershell
pwsh ./scripts/install-class-windows.ps1 -VerifyOnly
```

### What it does

Every step is idempotent: a tool already on `PATH` is skipped, so re-running the script only fills gaps.

| Step | Installs |
|---|---|
| Core runtimes | Git, .NET 10 SDK, Node.js 22 LTS, Python 3.12, uv, Microsoft OpenJDK 21, Maven, PowerShell 7 |
| Cloud and DevOps | Azure CLI, Azure Developer CLI, Terraform, GitHub CLI, Hugo Extended 0.128.0, Docker Desktop, VS Code |
| Claude Code | `npm install -g @anthropic-ai/claude-code` |
| Bicep | `az bicep install` |
| Browser | `npx playwright install chrome`, used by the `playwright` and `chrome-devtools` MCP servers |
| VS Code extensions | Read from the `customizations.vscode.extensions` list in `.devcontainer/devcontainer.json`, so the two stay in sync |

It closes with a version table for the whole toolchain, printing `MISSING` in red for anything that did not land.

### Switches

| Switch | Effect |
|---|---|
| `-VerifyOnly` | Prints the version table and exits, installs nothing |
| `-SkipDocker` | Leaves Docker Desktop out, for a machine that already has a container runtime |
| `-SkipVSCode` | Leaves VS Code and its extensions out |
| `-SkipExtensions` | Installs VS Code but not the extension list |
| `-SkipBrowser` | Skips the Playwright Chrome download |

## build-pdf.ps1

Renders each module's participant handout to an A4 PDF.

### Prerequisite

Python with the `reportlab` package:

```bash
pip install reportlab
```

### Run

```powershell
pwsh ./scripts/build-pdf.ps1
```

### What it does

The script scans `demos/*/pdf/handout.md` and writes a PDF next to each source file, named after the module folder. `demos/01-fundamentals/pdf/handout.md` becomes `demos/01-fundamentals/pdf/01-fundamentals.pdf`. A new module handout is picked up automatically, no edit required.

Rendering runs through `md2pdf.py`, a reportlab renderer that handles headings, paragraphs, tables, lists, blockquotes, fenced code blocks, links, and inline formatting. Fenced code blocks render as monospaced blocks with the language tag shown, and the content is preserved verbatim. Text uses Arial and Consolas from `C:/Windows/Fonts`, embedded as TrueType subsets.

### Handout structure

The source markdown drives four layout features:

| Feature | How to write it |
|---|---|
| Cover page | A YAML front matter block with `eyebrow`, `title`, `blurb`, `edition`, and `footer`. The cover carries no page footer |
| Contents | A line containing only `[TOC]`, which renders dot leaders and real page numbers on a second build pass |
| Chapter start | Any `#` heading. Each one starts a new page, gets the accent rule, and becomes a contents entry |
| Chapter eyebrow | An `####` heading directly above the `#` heading, for example `#### CHAPTER 1`. It stays with its title across the page break |

`edition` accepts several lines separated by ` | `. Every other page carries the `footer` text on the left and the page number on the right.

## rebuild_project.py

Rebuilds the GitHub project board for this repository, setting the theory, demos, labs, and slides status of every module.
