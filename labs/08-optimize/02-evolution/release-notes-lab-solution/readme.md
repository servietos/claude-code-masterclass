# Release Notes Experiment Solution

Completed reference for [`lab-02-evolve-via-metrics.md`](../../lab-02-evolve-via-metrics.md). The starter you scaffold yourself lives beside this folder as `release-notes-lab/`.

## What is here

| Path | Role |
|---|---|
| `hello.py`, `math_utils.py`, `cli.py` | The Typer CLI the release notes describe |
| `requirements.txt` | `typer==0.27.0` |
| `.claude/skills/release-notes/SKILL.md` | The deliberately under-specified starting skill |
| `experiments/runner.sh` | The deterministic harness: three runs, then `metrics.json` |

This folder ships without a `.git` directory on purpose: a nested repository inside the class repo shows up as an embedded repo. Run `git init` here (and the five commits the lab asks for) before you use `experiments/runner.sh`, because the harness reads git history.

## Run it

```bash
python -m venv .venv
./.venv/Scripts/python.exe -m pip install -r requirements.txt
./.venv/Scripts/python.exe cli.py hello Ada

git init
git add . && git commit -m "chore: initial import"

bash experiments/runner.sh
```

On Linux or macOS use `.venv/bin/python`. `experiments/runner.sh` needs `jq` on `PATH`, which the lab lists as a prerequisite (`winget install jqlang.jq` on Windows, `brew install jq`, `apt install jq`).

## Harness contract

The runner invokes `claude -p "$PROMPT" --output-format json` and reads two keys from the envelope: `is_error` and `result`. Both are documented fields of the result message, together with `type`, `subtype`, `duration_ms`, `session_id`, `total_cost_usd`, `num_turns` and `usage`.

`metrics.json` looks like this:

```json
{
  "measured_rev": "80cfd3d57c5af4cb2133804f1a7d85e9113c1b79",
  "run_count": 3,
  "identical_outputs": 1,
  "sections_present": 0,
  "merge_commits_included": 3,
  "aborted_runs": 0
}
```

`identical_outputs` counts *pairs* of byte-identical runs, which is the definition both the lab and [`demos/08-optimize/03-autoresearch-loop/readme.md`](../../../../demos/08-optimize/03-autoresearch-loop/readme.md) use: over three runs the only values are 0 (all differ), 1 (exactly two match) and 3 (all match). A count of matching *runs* could never reach the 0 that the baseline reports.

## Why BASE_REV is opt-in

An earlier version of the lab told the runner to reset the working tree to a known commit before every measurement. Two problems, both reproduced here:

1. Checking out an older commit deletes the files that were added later, including `.claude/skills/release-notes/SKILL.md` and `experiments/runner.sh` itself. The runs then measure a repo with no skill in it.
2. The propose-and-evaluate loop edits `SKILL.md` without committing it, and `git checkout <sha>` refuses to run with those edits present (`error: Your local changes to the following files would be overwritten by checkout`).

So `BASE_REV` is opt-in here. With no `BASE_REV` the harness measures the working tree, which is the thing you are actually experimenting on. With `BASE_REV` set the harness first refuses a dirty tree, then checks out detached, runs, and returns to the original branch.

## Verified without paid model calls

The plumbing was proven with a stub `claude` placed earlier on `PATH` that prints a canned result envelope. Stub outcomes and the metrics they produced:

| Stub behaviour | Resulting metrics |
|---|---|
| Same structured markdown every run | `identical_outputs: 3`, `sections_present: 3`, `aborted_runs: 0` |
| Different text every run, mentions a merge | `identical_outputs: 0`, `merge_commits_included: 3`, `aborted_runs: 0` |
| Two runs identical, third different | `identical_outputs: 1`, `aborted_runs: 0` |
| `is_error: true` | `aborted_runs: 3`, `identical_outputs: 0` |
| Exit code 1 | `aborted_runs: 3`, `identical_outputs: 0` |

Steps 2 to 5 of the lab (proposals, promote or revert, second loop) need real model runs, so the numbers in `metrics.json` from a stub are plumbing evidence only.
