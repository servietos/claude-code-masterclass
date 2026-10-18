# Publish a Plugin Through a Team Catalog

Release the Lab 01 `notes-toolkit` plugin through an `acme` team catalog, then tighten the catalog entry from a moving branch to a release tag and a full commit sha, so a teammate installs exactly the version you shipped.

Each step contains:
- **Goal**: what you are building
- **Prompt or command**: what you run
- **Expected result**: what the outcome looks like

> **Why this matters:** A plugin on your disk has no address. Today a teammate gets your work by copying a folder, and the copy drifts from the original with the first edit. A catalog gives the plugin a name a teammate can install, and a pin on that entry decides whether they receive every change you make or only the release you approved.

> **Two folders:** the starter at [`03-publish/release-desk/`](03-publish/release-desk/) holds the finished Lab 01 plugin as `notes-toolkit/` and nothing else: no repository, no catalog, no tag. You create the repository, the tag and the `acme-catalog/` beside it. The completed result is checked in as [`03-publish/release-desk-solution/`](03-publish/release-desk-solution/); build your own first and use it to compare.

---

## Where to Open Claude Code

Open one terminal for the Claude Code session and keep a second one for shell commands, both inside the starter. The catalog, the plugin repository and the commands in every prompt below resolve relative to `release-desk/`. Run this from the repo root:

```bash
cd labs/08-distribution/03-publish/release-desk
claude
```

Do not work at the repo root. The plugin repository you create in Step 2 sits inside `notes-toolkit/`, and its tags belong to that folder only. Creating it there keeps every tag, commit and installed catalog away from this course repository.

This lab registers a marketplace and installs a plugin on your machine. The last step removes both, so run it to the end.

---

## Setup: Look at the Starter

The starter is the plugin you built in Lab 01, packaged and ready:

```text
release-desk/
└── notes-toolkit/
    ├── .claude-plugin/plugin.json      name notes-toolkit, version 0.1.0
    ├── .gitignore                      local artifacts (.venv, __pycache__, node_modules)
    ├── .mcp.json                       notes-mcp server
    ├── commands/notes-flow.md
    ├── hooks/hooks.json                scope-gate on Write and Edit
    ├── hooks/scope-gate.sh
    ├── hooks/scope-gate.ps1
    ├── mcp-server/                     requirements.txt and server.py
    ├── skills/notes-extract/SKILL.md
    ├── skills/notes-prioritise/SKILL.md
    └── README.md
```

Prove that it has no release identity yet. From the second terminal, in `release-desk/`:

```bash
git -C notes-toolkit rev-parse --show-toplevel
```

**Expected result:** the root path of this course repository. The plugin sits inside it and has no repository of its own, which is the gap the next steps close.

---

## Step 1: Validate the Plugin Before Release

**Goal:** Catch manifest and frontmatter defects before they are tagged into a release, and read the one hint the validator gives about distribution.

A release is permanent once a teammate pins to it. `--strict` turns warnings into failures, which is the setting a release gate should use.

**Command:**

```bash
claude plugin validate --strict notes-toolkit
```

**Expected result:** `Validation passed`, preceded by an advice block that says the README has no line installing `notes-toolkit` from a marketplace, and suggests `/plugin install notes-toolkit --marketplace <owner>/<repo>`. Advice does not change the verdict. You act on it in Step 3.

---

## Step 2: Give the Plugin Its Own Repository

**Goal:** Put the plugin in a repository of its own, so a tag on it describes this plugin and nothing else.

`claude plugin tag` tags the git repository that contains the plugin path, whatever your current folder is. Inside the course repository it would tag the wrong thing. A plugin repository per plugin is also how a team publishes: the catalog points at that repository.

**Command:**

```bash
git -C notes-toolkit init -b main
git -C notes-toolkit add -A
git -C notes-toolkit commit -m "notes-toolkit 0.1.0"
claude plugin tag --dry-run notes-toolkit
```

**Expected result:** the dry run prints the identity it derived and the commands it would run, and creates nothing:

```text
Plugin:  notes-toolkit
Version: 0.1.0 (from plugin.json)
Tag:     notes-toolkit--v0.1.0
```

A closing line confirms the dry run, then the output prints the `git tag -a` command and the `git push origin refs/tags/...` command it would run. Neither runs.

The tag name is `{name}--v{version}`, read from `plugin.json` alone. Run `git -C notes-toolkit tag` and confirm it prints nothing: a dry run writes no tag.

---

## Step 3: Add the Install Line and Cut the Release

**Goal:** Answer the validator's advice, meet the refusal that protects a release from uncommitted edits, and create the real tag.

A tag marks a commit. If the files on disk differ from that commit, the release contains something other than what you tested, so the tool refuses.

**Prompt (in the Claude Code session):**

```text
Append a section to the end of notes-toolkit/README.md. Its heading is "## Install" and its body is one code block with the language text, containing the single line: /plugin install notes-toolkit@acme
```

Then try the dry run before committing:

```bash
claude plugin tag --dry-run notes-toolkit
```

**Expected result:** a refusal and a non-zero exit code:

```text
✘ Uncommitted changes affecting this release
```

The message continues with the advice to commit first, names `README.md` as the offending file, and mentions `--force`, an override this lab never uses.

Commit the change, create the tag, and read it back:

```bash
git -C notes-toolkit commit -am "Add install line"
claude plugin tag notes-toolkit
git -C notes-toolkit tag -n
```

**Expected result:** `✔ Created tag notes-toolkit--v0.1.0`, and `git tag -n` lists `notes-toolkit--v0.1.0` with the annotation `notes-toolkit 0.1.0`. The tag is annotated, which matters in Step 9. Run `claude plugin validate --strict notes-toolkit` once more: the advice block about the install line is gone.

---

## Step 4: Write the Catalog

**Goal:** Create the `acme` catalog with `notes-toolkit` listed as an entry, pinned to the `main` branch.

A catalog is one file, `.claude-plugin/marketplace.json`, in a folder of its own. Each entry says where a plugin lives and which revision of it to take. Production catalogs use a `github` source pointing at `acme-corp/notes-toolkit`; this lab uses a `url` source that points at the repository you just made, so everything runs offline with the same `ref` and `sha` rules.

First build the repository address. A `url` source needs an absolute `file://` address:

```bash
echo "file://$(pwd)/notes-toolkit"
```

```powershell
"file:///" + ((Get-Location).Path -replace '\\','/') + "/notes-toolkit"
```

**Expected result:** one line such as `file:///home/you/.../release-desk/notes-toolkit`. Copy it; it replaces `<REPO-URL>` below.

**Prompt (in the Claude Code session):**

```text
Create acme-catalog/.claude-plugin/marketplace.json with exactly this content, replacing <REPO-URL> with the address I give you after this prompt:

{
  "name": "acme",
  "owner": { "name": "Acme Corp" },
  "metadata": { "description": "Internal plugin catalog for Acme Corp engineering teams." },
  "plugins": [
    {
      "name": "notes-toolkit",
      "version": "0.1.0",
      "description": "Extract, prioritise, and report on TODO/FIXME/NOTE comments.",
      "source": { "source": "url", "url": "<REPO-URL>", "ref": "main" }
    }
  ]
}

The address is: <paste the line from the command above>
```

**Expected result:** `acme-catalog/.claude-plugin/marketplace.json` exists, the `url` value is your absolute address, and the file lives inside the catalog's `.claude-plugin/` folder.

---

## Step 5: Validate the Catalog

**Goal:** Check the catalog the way you checked the plugin, before a teammate meets it.

**Command:**

```bash
claude plugin validate acme-catalog
```

**Expected result:** `Validation passed` with no warnings. The `metadata.description` field is what keeps the "No marketplace description provided" warning away; remove it temporarily if you want to see that warning, then put it back.

---

## Step 6: Install as a Teammate

**Goal:** Run the two commands a teammate runs, and confirm the plugin arrives.

A teammate needs the catalog once and then installs by `plugin@catalog`. In production the first command takes `acme-corp/acme-catalog` or a git URL; here it takes the folder.

**Prompt (in the Claude Code session):**

```text
/plugin marketplace add ./acme-catalog
/plugin install notes-toolkit@acme
```

Then confirm from the second terminal:

```bash
claude plugin list
```

**Expected result:** both commands finish without an error. `claude plugin list` prints every plugin on your machine, so find the entry for this lab. It reads:

```text
  ❯ notes-toolkit@acme
    Version: 0.1.0
    Scope: user
    Status: ✔ enabled
```

The catalog works. What the teammate received is whatever `main` pointed at when they installed, which is the weakness the next steps remove.

---

## Step 7: Move the Branch Past the Release

**Goal:** See that a branch pin follows every commit you make, including the ones you did not mean to ship.

You are working on the next version while the team keeps installing. Simulate that by bumping the plugin without tagging it.

**Prompt (in the Claude Code session):**

```text
In notes-toolkit/.claude-plugin/plugin.json change the version from 0.1.0 to 0.1.1.
```

Commit it, then compare the branch with the release:

```bash
git -C notes-toolkit commit -am "0.1.1 work in progress"
git -C notes-toolkit rev-parse main "notes-toolkit--v0.1.0^{commit}"
```

**Expected result:** two different 40-character hashes: `main` has moved on, the release commit has not.

Now do what a teammate does on their next update. In the session:

```text
/plugin marketplace update acme
/plugin uninstall notes-toolkit@acme
/plugin install notes-toolkit@acme
```

```bash
claude plugin list
```

**Expected result:** `Version: 0.1.1`. The catalog still says `0.1.0` and the tag still marks `0.1.0`, yet the teammate runs 0.1.1: a branch `ref` ships whatever lands next.

---

## Step 8: Pin the Entry to the Release Tag

**Goal:** Repoint the catalog entry from `main` to `notes-toolkit--v0.1.0`, so installs get the release regardless of what happens on `main`.

A tag `ref` is a stable upgrade target: moving to the next release is an explicit catalog edit.

**Prompt (in the Claude Code session):**

```text
In acme-catalog/.claude-plugin/marketplace.json change the plugin's source "ref" from "main" to "notes-toolkit--v0.1.0". Change nothing else.
```

Validate, refresh and reinstall:

```bash
claude plugin validate acme-catalog
```

```text
/plugin marketplace update acme
/plugin uninstall notes-toolkit@acme
/plugin install notes-toolkit@acme
```

```bash
claude plugin list
```

**Expected result:** validation passes and `Version: 0.1.0` is back, although `main` is at 0.1.1. Same catalog, same repository, a different pin, a different result.

A tag name can be moved by someone with push access. The next step removes that last degree of freedom.

---

## Step 9: Pin the Entry to a Full Commit Sha

**Goal:** Replace the `ref` with the exact commit of the release, the pin that cannot move.

The catalog needs the hash of the commit. The tag from Step 3 is annotated, so plain `git rev-parse notes-toolkit--v0.1.0` returns the hash of the tag object, a different object, and the `^{commit}` suffix dereferences it to the commit.

**Command:**

```bash
git -C notes-toolkit rev-parse "notes-toolkit--v0.1.0^{commit}"
```

**Expected result:** one 40-character lowercase hash. Copy it.

**Prompt (in the Claude Code session):**

```text
In acme-catalog/.claude-plugin/marketplace.json remove the plugin's source "ref" and add "sha" with the first seven characters of this hash only: <first 7 characters>. Change nothing else.
```

```bash
claude plugin validate acme-catalog
```

**Expected result:** the validation fails, naming the field:

```text
  ❯ plugins.0.source.sha: Too small: expected string to have exactly 40 characters
  ❯ plugins.0.source.sha: Must be a full 40-character lowercase git commit SHA
```

An abbreviated sha is the common slip, and the validator catches it before a teammate does. Fix it:

```text
In acme-catalog/.claude-plugin/marketplace.json set the plugin's source "sha" to the full 40-character hash: <paste the full hash>. Change nothing else.
```

```bash
claude plugin validate acme-catalog
```

```text
/plugin marketplace update acme
/plugin uninstall notes-toolkit@acme
/plugin install notes-toolkit@acme
```

```bash
claude plugin list
```

**Expected result:** validation passes and `Version: 0.1.0` is installed from the pinned commit.

| Pin | Field | Follows | Choose it for |
|---|---|---|---|
| Branch | `ref: "main"` | Every commit | A plugin you develop together with its users |
| Tag | `ref: "notes-toolkit--v0.1.0"` | Nothing until you edit the catalog | A team release with a readable name |
| Commit | `sha: <40 characters>` | Nothing, and it cannot be re-pointed | Production, and any audit trail |

---

## Step 10: Clean Up and Compare

**Goal:** Remove the marketplace and the install from your machine, and compare your catalog with the reference.

```text
/plugin uninstall notes-toolkit@acme
/plugin marketplace remove acme
```

```bash
claude plugin list
```

**Expected result:** `claude plugin list` no longer shows `notes-toolkit@acme`, and `claude plugin marketplace list` no longer shows `acme`. Your user settings no longer mention `acme`. Other plugins on your machine stay in the list.

Compare your finished catalog with [`03-publish/release-desk-solution/acme-catalog/.claude-plugin/marketplace.json`](03-publish/release-desk-solution/acme-catalog/.claude-plugin/marketplace.json). The reference pins the tag with the production `github` source; your `url` source and your sha are the only expected differences.

---

## What You Just Practised

| Mechanic | Step | Why it matters |
|---|---|---|
| `claude plugin validate --strict` on a plugin and on a catalog | 1, 5, 8, 9 | Release gates that fail before a teammate does |
| A repository per plugin and `claude plugin tag --dry-run` | 2 | A release identity of `{name}--v{version}` that describes one plugin |
| Dirty-tree refusal | 3 | A tag always points at the commit you tested |
| `.claude-plugin/marketplace.json` entry | 4 | The catalog is one file that maps a name to a source and a revision |
| `/plugin marketplace add` and `/plugin install plugin@catalog` | 6 | The only two commands a teammate needs |
| Branch, tag and sha pins | 7, 8, 9 | Decide how much of your ongoing work reaches installers |
| Annotated tag versus commit hash | 9 | The sha field takes the commit hash, which `^{commit}` extracts from an annotated tag |

[Lab 01](lab-01-build-a-plugin.md) built the plugin and [Lab 02](lab-02-plugin-security.md) audited a plugin from someone else. This lab publishes yours, with the pin a security-minded team asks for.
