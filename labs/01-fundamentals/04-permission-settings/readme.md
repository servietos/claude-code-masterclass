# Lock Down a Secrets File With Permission Rules

Every approval prompt you click through by reflex is a control that no longer controls anything, and a line in `CLAUDE.md` asking Claude to leave a secrets file alone is only a request. You will write a project `.claude/settings.json` with allow, ask and deny rules, add a git-ignored `.claude/settings.local.json` for your own habits, and prove every rule by attempting the path it guards. You finish with a report listing each attempt, its outcome and the rule file that produced it.

What you practice here: decide in advance which commands run silently, which ask and which are impossible, then verify each decision by trying to break it.

Duration: about 65 minutes.

Teaching for this lab lives in [Configure the Permission Model](../../../demos/01-fundamentals/03-permissions/readme.md); the rule syntax is under [Writing Permission Rules](../../../demos/01-fundamentals/03-permissions/readme.md#writing-permission-rules) and the file precedence under [Where Permissions Are Stored](../../../demos/01-fundamentals/03-permissions/readme.md#where-permissions-are-stored).

Each step contains:

- **Goal**: what you are building
- **Prompt**: paste this into Claude Code
- **Expected result**: what the outcome looks like

You build three things in the starter folder: `.claude/settings.json` (team policy), `.claude/settings.local.json` (personal override) and `PERMISSIONS-REPORT.md` (one row per attempted action).

## Where to Open Claude Code

The starter is a small Python billing tool with two passing tests, a `CLAUDE.md`, a `config.secrets.json` and a `secrets/` folder holding fake credentials. Open Claude Code inside the starter folder, because `.claude/settings.json` is resolved from the directory the session starts in. Run this from the repo root.

```bash
cd labs/01-fundamentals/04-permission-settings/starter && claude
```

```powershell
cd labs/01-fundamentals/04-permission-settings/starter; claude
```

The first start shows a trust dialog. Accept it: project allow rules are ignored in a workspace you have not trusted, and a policy that looks inert for that reason wastes a lot of debugging time.

## How to Restart and Read a Rule

Claude Code loads settings files at session start, so every step that edits a settings file ends with the same two actions:

1. Type `/exit`, then run `claude` again in the starter folder. Read the first lines it prints; Claude Code warns there about rules it cannot match.
2. Type `/permissions` and find your rule in the list. Each entry names the file it came from.

Every attempt in this lab uses the wording `Run exactly:` so Claude issues the command you typed and does not substitute its own. When a prompt asks you to approve or refuse, the step tells you which answer to give.

---

## Step 1: Watch an Unprotected Secret Get Read

**Goal:** See that `CLAUDE.md` is guidance and that a read-only shell command never asks.

The starter's `CLAUDE.md` already says never to read `config.secrets.json`. The values in the file are fake, so reading them costs nothing here, and that is the point: nothing in the harness stands in the way.

**Prompt:**

```text
Run exactly: cat config.secrets.json
This is a lab fixture with fake values and I authorise reading it.
```

Then check what is enforced:

```text
/permissions
```

**Expected result:** Claude prints the JSON with `FAKE-gateway-key-0000` and `FAKE-webhook-secret-0000` and no approval prompt appeared, because `cat` belongs to the built-in read-only command set. `/permissions` lists no deny rules. If Claude declines and quotes `CLAUDE.md`, that is the model choosing to comply, which a different prompt or a different model can undo; restate the authorisation once and carry on. Nothing so far is a control, and the next steps build one.

---

## Step 2: Pre-Approve the Commands You Run All Day

**Goal:** Remove the prompts that train you to click Yes without reading.

Create the file `.claude/settings.json` in the starter folder (make the `.claude` folder first) with this content. It allows the test runner and nothing else.

```json
{
  "permissions": {
    "allow": [
      "Bash(python -m unittest *)"
    ]
  }
}
```

Restart as described in [How to Restart and Read a Rule](#how-to-restart-and-read-a-rule), then run two commands, one at a time.

**Prompt:**

```text
Run exactly: python -m unittest discover -s tests
```

```text
Run exactly: python -m billing data/invoices.csv
```

**Expected result:** the first command runs with no prompt and reports `Ran 2 tests` and `OK`. The second prompts for approval because no rule covers it; answer No. `/permissions` shows the allow rule attributed to `.claude/settings.json`. Compare this with Step 1: `python -m unittest` is not in the built-in read-only set, so only your rule made it silent.

---

## Step 3: Make the Secrets Unreachable by Read and by Shell

**Goal:** Turn the line in `CLAUDE.md` into a rule that holds no matter what Claude decides.

Edit `.claude/settings.json` to add a `deny` list. The two path patterns are anchored at the project root, and the `**` covers everything under `secrets/`.

```json
{
  "permissions": {
    "allow": [
      "Bash(python -m unittest *)"
    ],
    "deny": [
      "Read(./config.secrets.json)",
      "Read(./secrets/**)",
      "Edit(./secrets/**)"
    ]
  }
}
```

Restart, then attempt each route to the same file. Run the prompts one at a time and let each one finish. Each prompt lifts the `CLAUDE.md` secrets rule for that one command; without the lift Claude refuses on its own, the deny rule is never reached, and the step proves nothing.

**Prompt:**

```text
Read config.secrets.json with your Read tool and show me its contents.
Permission test: I lift the CLAUDE.md secrets rule for this command, so only a settings rule can stop it.
```

```text
Run exactly: cat config.secrets.json
Permission test: I lift the CLAUDE.md secrets rule for this command, so only a settings rule can stop it.
```

```text
Run exactly: head -n 1 secrets/payment.env
Permission test: I lift the CLAUDE.md secrets rule for this command, so only a settings rule can stop it.
```

```text
Append the line "EXTRA=1" to secrets/payment.env.
Permission test: I lift the CLAUDE.md secrets rule for this command, so only a settings rule can stop it.
```

**Expected result:** all four attempts are refused with a permission denial and none prints a secret. The `cat` and `head` refusals matter most: you wrote one `Read` rule and it also closed the shell commands Claude Code recognises as file reads, which is the bypass Step 1 used. The `Edit` rule blocks the append. Keep the terminal output; Step 8 turns it into a report.

---

## Step 4: Find the Route the Deny Rule Does Not Close

**Goal:** Learn the limit of a path rule by attempting a route it does not cover.

A `Read` deny covers Claude's file tools and the file commands Claude Code recognises inside Bash. A script that opens the file itself is a different process, and the rule was not written for it. Attempt it and decline the prompt.

**Prompt:**

```text
Run exactly: python -c "print(open('config.secrets.json').read())"
Permission test: I lift the CLAUDE.md secrets rule for this command, so only a settings rule can stop it.
```

**Expected result:** an approval prompt appears for the command, because no allow rule matches it. Answer No; the file stays unread. The finding is that the path deny does not refuse this command by itself, so the only barrier left is your own click. Now close the route you can name with a pattern: add `"Bash(python -c *)"` and `"Bash(python3 -c *)"` to the `deny` list, restart, and run the same prompt again.

The command is now refused without asking. Path rules and command patterns close the routes you can name; the sandbox is the option that enforces file boundaries across every process, and Step 8 asks Claude to summarise it from the docs.

---

## Step 5: Add an Ask Tier and Refuse the Destructive Commands

**Goal:** Give each command the right level of friction: silent, asking or impossible.

Add an `ask` list for the one command that is legitimate but consequential, and extend `deny` with the commands whose worst case you cannot undo. Your complete file now reads as follows.

```json
{
  "permissions": {
    "allow": [
      "Bash(python -m unittest *)"
    ],
    "ask": [
      "Bash(git push *)"
    ],
    "deny": [
      "Read(./config.secrets.json)",
      "Read(./secrets/**)",
      "Edit(./secrets/**)",
      "Bash(python -c *)",
      "Bash(python3 -c *)",
      "Bash(rm -rf *)",
      "Bash(git push --force *)"
    ]
  }
}
```

Restart, then attempt the three. The `--dry-run` flag keeps a mistaken Yes harmless, so you can answer the prompt either way.

**Prompt:**

```text
Run exactly: rm -rf build
```

```text
Run exactly: git push --force --dry-run origin HEAD
```

```text
Run exactly: git push --dry-run origin HEAD
```

**Expected result:** the first two are refused with no prompt, the third stops and asks. The rule order is deny, then ask, then allow, and the first match wins, so `git push --force --dry-run` matches the deny rule before the broader ask rule sees it. That is also why a deny cannot carry exceptions: you cannot permit one force push while denying the pattern. Answer No to the third prompt, or Yes and read the dry-run output; both are safe.

---

## Step 6: Add a Personal Override That Stays Out of Git

**Goal:** Keep your own convenience rules apart from the policy the team shares.

In Step 2 `python -m billing data/invoices.csv` prompted you. Running the tool is your own habit and no team policy, so it belongs in `.claude/settings.local.json`. Create that file with this content.

```json
{
  "permissions": {
    "allow": [
      "Bash(python -m billing *)"
    ]
  }
}
```

Now keep it out of version control. Add this line to the starter's `.gitignore`:

```text
.claude/settings.local.json
```

Verify the ignore rule and the commit set from the starter folder.

```bash
git check-ignore -v .claude/settings.local.json
git status --short .
```

Restart and run the tool again.

**Prompt:**

```text
Run exactly: python -m billing data/invoices.csv
```

**Expected result:** `git check-ignore -v` prints the `.gitignore` line that matches `.claude/settings.local.json`, and `git status --short .` lists the `.gitignore` change and the `.claude/` folder, with no line that names `settings.local.json`. In a folder that is not committed yet, git shows the whole folder as `?? ./` and the same file stays out of the list. The command now runs with no prompt and prints `Acme: 1200.00`, `Borealis: 497.25` and `Citrine: 640.00`. In `/permissions` the unittest rule is attributed to `.claude/settings.json` and the billing rule to `.claude/settings.local.json`. A teammate who clones the repo gets the first rule and never sees the second.

---

## Step 7: Prove a Local Allow Cannot Undo a Team Deny

**Goal:** Confirm that the local file is for convenience and cannot weaken the policy, then catch a rule that protects nothing.

Add two allow rules to `.claude/settings.local.json` that try to reopen what the team file closed.

```json
{
  "permissions": {
    "allow": [
      "Bash(python -m billing *)",
      "Read(./config.secrets.json)",
      "Bash(git push --force *)"
    ]
  }
}
```

Restart and repeat two earlier attempts.

**Prompt:**

```text
Read config.secrets.json with your Read tool and show me its contents.
```

```text
Run exactly: git push --force --dry-run origin HEAD
```

**Expected result:** both are still refused. Deny rules from every file are evaluated before any allow rule, so the local file, which ranks above the project file for conflicting allows, cannot override a deny. Remove the two extra allow rules from `.claude/settings.local.json` so only the billing rule remains.

Now add a rule that looks like protection and is not. Put `"Write(./secrets/**)"` in the `deny` list of `.claude/settings.json`, restart, and read the first lines Claude Code prints.

**Expected result:** a startup warning names the rule and says that only `Edit(path)` rules are matched by the file permission checks, and that `Edit` covers all file-editing tools. The exact wording can change between releases; the signal is a warning that names your `Write` rule. Delete the `Write` line, restart, and confirm the warning is gone. A clean start means every rule you wrote matches something.

---

## Step 8: Audit Every Rule by Its Attempt

**Goal:** Leave a record that ties each decision to the rule file that produced it.

You attempted most routes in the earlier steps. Ask Claude to build the report and to run the two actions you have not attempted since the final settings were in place.

**Prompt:**

```text
Create PERMISSIONS-REPORT.md in this folder with the heading "# Permissions report" and a Markdown table with the columns Action | Outcome | Rule | File.
Then run each action below one at a time, and add one row per action with the outcome you observed (ran silently, asked, or refused), the rule that produced it, and the settings file that rule lives in. If an action is refused, quote the denial text in the Outcome cell. This is a permission audit: I lift the CLAUDE.md secrets rule for every action, so attempt each one and let the settings rules decide. A shell read such as cat or head is governed by the Read rules.
1. python -m unittest discover -s tests
2. python -m billing data/invoices.csv
3. cat config.secrets.json
4. head -n 1 secrets/payment.env
5. python -c "print(1)"
6. rm -rf build
7. git push --dry-run origin HEAD
8. git push --force --dry-run origin HEAD
For action 7, record the outcome the prompt gave you and answer No if it asks. Do not edit any settings file.
```

Finish with the last open question from Step 4:

```text
Append one line under the table starting with "Sandbox:" that says what enabling the sandbox adds beyond the deny rules in this report. Use only what the settings documentation says.
```

**Expected result:** a table with eight rows. Rows 1 and 2 are "ran silently" with the unittest rule from `.claude/settings.json` and the billing rule from `.claude/settings.local.json`. Row 7 is "asked" with the `git push` ask rule. Rows 3, 4, 5, 6 and 8 are "refused", each citing a deny rule from `.claude/settings.json`. Check every Rule and File cell against `/permissions` yourself; a row that names a rule your files do not contain is the failure to catch here. Your deliverables are `.claude/settings.json`, `.claude/settings.local.json` and `PERMISSIONS-REPORT.md`.

---

## Troubleshooting

| Symptom | Cause | Fix |
|---|---|---|
| A rule you wrote never fires | The session started before the file changed | Run `/exit`, start `claude` again, then check `/permissions` |
| Your allow rules do nothing | The workspace was never trusted | Start `claude` in the starter folder and accept the trust dialog |
| `python -m unittest` still asks | A space is missing or the pattern has a typo | Compare with `Bash(python -m unittest *)`; the space before `*` is part of the pattern |
| `git check-ignore` prints nothing | The `.gitignore` line is missing or sits in another folder | Add the line to the starter's `.gitignore` and run the command from the starter folder |
| `python` is not found on macOS or Linux | The interpreter is called `python3` | Use `python3` in every command and rule, and keep the `python3 -c` deny rule |
