# Run a Headless Agent and Prove Its Tool Scope

Run `claude -p` for the first time, read the JSON envelope it returns, then prove on your own machine which scoping flag actually makes a run read-only. You end holding evidence that `--allowed-tools` grants permission while `--tools` withdraws capability, plus the envelope fields a script branches on.

------

## Step 1: Read the JSON envelope

Run every command from this topic folder (`cd demos/05-cli/01-intro`); the only file the demo can create is `scoped.txt`. With `--output-format json` the answer arrives inside an envelope a script can branch on.

```bash
claude -p "List the H2 headings in readme.md, one per line, with no commentary." --tools "Read,Glob,Grep" --max-turns 5 --output-format json
```

```json
{
  "type": "result",
  "is_error": false,
  "num_turns": 2,
  "session_id": "1ef515cf-ab16-45b7-b7af-748b6a60454c",
  "total_cost_usd": 1.584339,
  "result": "The Terminal and the CLI\nWhere Headless Mode Fits\n..."
}
```

Expected result: a single JSON object on stdout. Your `session_id` and `total_cost_usd` will differ; the field names will not.

The process has already exited with code 0 (`echo $?` in bash, `$LASTEXITCODE` in PowerShell), so `claude -p` composes with pipes and exit codes.

## Step 2: Watch `--allowed-tools` fail to lock the run down

Ask a supposedly read-only agent to create a file, then check whether it did.

```bash
claude -p "Create a file named scoped.txt in this folder containing the word hello." --allowed-tools "Read,Glob,Grep" --max-turns 3
```

```bash
ls scoped.txt
```

Expected result: on a typical developer setup the file exists, and Claude reports having created it. If your `settings.json` does not already permit writing you may see a refusal instead, which is the same lesson: your settings decided the outcome.

The flag named "allowed tools" restricted nothing, because it grants permissions and withdraws none.

## Step 3: Lock it down for real with `--tools`

Delete the `scoped.txt` from Step 2, then send the same prompt with `--tools`.

```bash
claude -p "Create a file named scoped.txt in this folder containing the word hello." --tools "Read,Glob,Grep" --max-turns 3
```

```text
I can't create that file: this session has no file-writing tool enabled. The only
local tools available to me here are read-only: Read, Glob, and Grep.
```

Expected result: no file is created. Run `ls scoped.txt` and the shell reports that it does not exist, which is the only proof that matters.

The exact wording of the refusal varies between runs; the absence of the file does not, and only `--tools` produces a read-only run.
