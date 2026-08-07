# Install and Set Up Claude Code

Install Claude Code CLI, authenticate, and explore it through the VS Code extension.

## Where to Open Claude Code

This lab works against the harness this repository already ships, so open Claude Code at the repo root. It installs and authenticates the CLI and then runs the Hello World checks against this repository's own files. Nothing this lab creates belongs in the repo's `.claude/` directory.

There is nothing to scaffold and no project folder to change into: the clone you already made is the folder the session belongs in, so once your terminal sits in it you are already in the right place. Both commands work unchanged in PowerShell.

```bash
cd <the folder you cloned this repository into>
claude
```

If you start Claude Code with the Claude Terminal extension (`Ctrl+F1` / `Cmd+F1`), it opens in the VS Code workspace folder and reuses an already-open terminal, so it will not follow the `cd` above. Open the repository clone as the workspace folder (**File > Open Folder**) before pressing the shortcut, or run the commands above in a plain terminal.

If a step here has you write a harness file, put it in the lab's own folder, never in the repository's `.claude/`.

Work through the install track that matches your operating system first, because the command above only runs once the CLI is on your PATH.

---

## Track A: Windows

### Step 1: Install Node.js

1. Go to [nodejs.org](https://nodejs.org) and download the **LTS** installer (Node.js 18 or later required).
2. Run the installer, accepting all defaults.
3. Open a new PowerShell window and verify:

```powershell
node --version
npm --version
```

Both commands should print a version number.

### Step 2: Install Claude Code CLI

```powershell
npm install -g @anthropic-ai/claude-code
```

### Step 3: Authenticate

```powershell
claude
```

A browser window opens. Sign in with your Anthropic account or enter an API key when prompted. Once the terminal shows `Logged in`, close the browser tab.

### Step 4: Install Claude Desktop App

Download and install the Claude desktop application from [claude.ai](https://claude.ai). This provides a native desktop interface for interacting with Claude outside of VS Code.

1. Go to [claude.ai](https://claude.ai) in your browser.
2. Look for the download option in the bottom-left corner or the menu.
3. Download the Windows installer and run it.
4. Sign in with your Anthropic account (the same credentials used for the CLI).

---

## Track B: macOS

### Step 1: Install Homebrew

If Homebrew is not already installed:

```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```

### Step 2: Install Node.js

```bash
brew install node
```

Verify:

```bash
node --version
npm --version
```

### Step 3: Install Claude Code CLI

```bash
npm install -g @anthropic-ai/claude-code
```

### Step 4: Authenticate

```bash
claude
```

A browser window opens. Sign in with your Anthropic account or enter an API key when prompted. Once the terminal shows `Logged in`, close the browser tab.

### Step 5: Install Claude Desktop App

Download and install the Claude desktop application from [claude.ai](https://claude.ai). This provides a native desktop interface for interacting with Claude outside of VS Code.

1. Go to [claude.ai](https://claude.ai) in your browser.
2. Look for the download option in the bottom-left corner or the menu.
3. Download the macOS installer and run it.
4. Sign in with your Anthropic account (the same credentials used for the CLI).

---

## Track C: Linux Devcontainer

This track is for development in a Linux devcontainer environment. Node.js and npm are pre-installed.

### Before You Start: Launch the Devcontainer or Codespace

**Option 1: Devcontainer (Local)**
1. Clone or open the repository in VS Code.
2. Press `F1` and select **Dev Containers: Reopen in Container**.
3. Wait for the container to build and start.

**Option 2: GitHub Codespace (Cloud)**
1. Go to the repository on GitHub.
2. Click **Code** > **Codespaces** > **Create codespace on [branch]**.
3. Wait for the codespace to initialize in your browser.

> **Note on Line Endings:** If you see many unrelated git changes after starting the devcontainer (e.g., 170+ modified files), this is likely due to line ending normalization. To reset line endings while preserving your edits, run:
> ```bash
> git checkout --theirs -- . && git add . && git checkout --ours -- labs/01-fundamentals/01-setup-claude/readme.md
> ```
> This restores the original line endings for all files except the ones you've edited.

### Step 1: Configure Git

Before making commits, configure your Git identity within the devcontainer:

```bash
git config --global user.name "Your Name"
git config --global user.email "your.email@example.com"
```

Verify your configuration:

```bash
git config --global user.name
git config --global user.email
```

These settings allow you to make commits within the devcontainer environment.

### Step 2: Verify Node.js

```bash
node --version
npm --version
```

Both commands should print a version number. If not, install Node.js:

```bash
apt update && apt install -y nodejs npm
```

### Step 3: Install Claude Code CLI

You can install Claude Code CLI using npm:

```bash
npm install -g @anthropic-ai/claude-code
```

>Note: Alternatively, add it to your `.devcontainer/devcontainer.json` to install it automatically when the container starts:

```json
"postCreateCommand": "npm install -g @anthropic-ai/claude-code"
```

### Step 4: Authenticate

```bash
claude
```

A browser window will attempt to open. If no browser is available in the devcontainer, the CLI will provide an authentication link. Copy the link, open it in your host machine's browser, and complete the sign-in. Once the terminal shows `Logged in`, you are authenticated.

### Step 5: Install Claude Desktop App

Download and install the Claude desktop application on your host machine (not in the devcontainer). This provides a native desktop interface for interacting with Claude outside of VS Code.

1. Go to [claude.ai](https://claude.ai) in your browser.
2. Look for the download option in the bottom-left corner or the menu.
3. Download the installer for your host OS (Windows or macOS).
4. Install and sign in with your Anthropic account (the same credentials used for the CLI).

---

## Verify Your Installation

Run the following command in your terminal (PowerShell on Windows, Terminal on macOS):

```bash
claude --version
```

You should see a version string such as `1.x.x`. This confirms the CLI is installed and accessible from any directory.

---

## Install VS Code Extensions

### Claude Code Extension

1. Open VS Code.
2. Open the Extensions panel (`Ctrl+Shift+X` / `Cmd+Shift+X`).
3. Search for `anthropic.claude-code` or click [this marketplace link](https://marketplace.visualstudio.com/items?itemName=anthropic.claude-code).
4. Click **Install**.

After installation a Claude icon appears in the Activity Bar on the left.

### Claude Terminal Extension

1. In the same Extensions panel, search for `cjnoname.claude-terminal` or click [this marketplace link](https://marketplace.visualstudio.com/items?itemName=cjnoname.claude-terminal).
2. Click **Install**.

This extension integrates Claude directly into the VS Code terminal panel.

---

## Hello World

### In the terminal

Open the repository folder in VS Code, then open a terminal (`Ctrl+`` ` / `Cmd+`` `):

```bash
claude "What files are in this directory and what do they do?"
```

Claude should list and describe the files it finds.

### In the Claude panel

1. Click the Claude icon in the Activity Bar.
2. In the chat input, type:

```text
Hello! What is this project about?
```

Claude reads your workspace and responds with a summary.

### Inline suggestion

1. Open any source file.
2. Place the cursor at the end of a function or class.
3. Press `Ctrl+I` / `Cmd+I` to open the inline prompt.
4. Type `Add a docstring to this function` and press Enter.

Claude writes the docstring inline; accept it with Tab.
