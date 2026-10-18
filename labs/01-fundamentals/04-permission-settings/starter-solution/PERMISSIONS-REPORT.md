# Permissions report

| Action | Outcome | Rule | File |
| --- | --- | --- | --- |
| `python -m unittest discover -s tests` | Ran silently (2 tests, OK) | `allow`: `Bash(python -m unittest *)` | `.claude/settings.json` |
| `python -m billing data/invoices.csv` | Ran silently (Acme: 1200.00, Borealis: 497.25, Citrine: 640.00) | `allow`: `Bash(python -m billing *)` | `.claude/settings.local.json` |
| `cat config.secrets.json` | Refused: "Permission to use Bash with command cat config.secrets.json has been denied." | `deny`: `Read(./config.secrets.json)` (shell read governed by Read rules) | `.claude/settings.json` |
| `head -n 1 secrets/payment.env` | Refused: "Permission to use Bash with command head -n 1 secrets/payment.env has been denied." | `deny`: `Read(./secrets/**)` (shell read governed by Read rules) | `.claude/settings.json` |
| `python -c "print(1)"` | Refused: "Permission to use Bash with command python -c "print(1)" has been denied." | `deny`: `Bash(python -c *)` | `.claude/settings.json` |
| `rm -rf build` | Refused: "Permission to use Bash with command rm -rf build has been denied." | `deny`: `Bash(rm -rf *)` | `.claude/settings.json` |
| `git push --dry-run origin HEAD` | Asked: "Claude requested permissions to use Bash, but you haven't granted it yet." Answered No, command not run. | `ask`: `Bash(git push *)` | `.claude/settings.json` |
| `git push --force --dry-run origin HEAD` | Refused: "Permission to use Bash with command git push --force --dry-run origin HEAD has been denied." | `deny`: `Bash(git push --force *)` | `.claude/settings.json` |

Sandbox: Enabling the sandbox puts an OS-enforced boundary around shell commands (Bash, PowerShell and Monitor) and the processes they start. It limits writes to the working directory and a per-user temp directory, restricts reads through `filesystem.denyRead`, and routes network access through a proxy that checks each host against `network.allowedDomains`. The built-in Read, Edit, Write, WebFetch and WebSearch tools stay under permission rules, and the sandbox runs on macOS, Linux and WSL2 only, with native Windows running commands unsandboxed.
