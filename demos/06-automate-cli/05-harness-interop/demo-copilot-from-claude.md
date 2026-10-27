# Run Copilot CLI on DeepSeek From Claude Code

Send one prompt, `create a poem about sighthounds`, to GitHub Copilot CLI running on DeepSeek V4.1 Flash, then hand the same prompt to Copilot from Claude Code: once from an interactive session and once from `claude -p`. You end with proof of which model wrote each poem.

Duration: about 10 minutes.

------

## Step 1: Point Copilot CLI at DeepSeek V4.1 Flash

Run every command from this topic folder (`cd demos/06-automate-cli/06-harness-interop`); the demo creates no files. Five variables route Copilot to DeepInfra for the rest of the shell session.

```bash
export COPILOT_PROVIDER_TYPE=openai
export COPILOT_PROVIDER_BASE_URL=https://api.deepinfra.com/v1/openai
export COPILOT_PROVIDER_API_KEY="paste-your-deepinfra-key"
export COPILOT_MODEL=deepseek-ai/DeepSeek-V4.1-Flash
export COPILOT_PROVIDER_WIRE_MODEL=deepseek-ai/DeepSeek-V4.1-Flash
```

```powershell
$env:COPILOT_PROVIDER_TYPE = "openai"
$env:COPILOT_PROVIDER_BASE_URL = "https://api.deepinfra.com/v1/openai"
$env:COPILOT_PROVIDER_API_KEY = "paste-your-deepinfra-key"
$env:COPILOT_MODEL = "deepseek-ai/DeepSeek-V4.1-Flash"
$env:COPILOT_PROVIDER_WIRE_MODEL = "deepseek-ai/DeepSeek-V4.1-Flash"
```

Now send the prompt. `-s` prints the answer and nothing else.

```bash
copilot -p "create a poem about sighthounds" -s
```

```text
Sighthounds lean into the wind's long line,
where hare and horizon both align.
Greyhound, saluki, whippet, deerhound too,
each built of arrow, silence, and sinew.

They do not run so much as pour
across the field, then ask for more.
A couch, a blanket, a bony knee,
and all that speed becomes a sigh of glee.

Give them a chase, then give them rest,
the fastest heart in a narrow chest.
```

Expected result: a poem on stdout and exit code 0. Your poem will differ; every run writes a new one. Without `-s` the same run ends with a stats footer (`Duration`, `Tokens`, and a `copilot --resume=<id>` line to continue the session).

## Step 2: Prove which model wrote it

The event stream names the model that wrote the poem. With `--output-format json` Copilot prints one JSON event per line; keep the two that settle the question.

```bash
copilot -p "create a poem about sighthounds" --output-format json | grep -E '"type":"(model.call_final_result|result)"'
```

```powershell
copilot -p "create a poem about sighthounds" --output-format json | ConvertFrom-Json | Where-Object type -in 'model.call_final_result','result' | ForEach-Object { $_ | ConvertTo-Json -Compress -Depth 5 }
```

```json
{"type":"model.call_final_result","data":{"model":"deepseek-ai/DeepSeek-V4.1-Flash","isByok":true,"result":"success"},...}
{"type":"result","sessionId":"67b58a70-2d8c-4d0a-b29d-4dabe1df69db","exitCode":0,"usage":{"premiumRequests":0,"totalApiDurationMs":7379,...}}
```

Expected result: `"model":"deepseek-ai/DeepSeek-V4.1-Flash"` with `"isByok":true`, and `"premiumRequests":0`. The poem came from your DeepInfra key and used none of your Copilot plan. If the model name is a GitHub-hosted one, a `model` key in `~/.copilot/settings.json` is overriding your variables.

## Step 3: Let Claude call Copilot from an interactive session

Start Claude Code in the same shell, so it inherits the five variables, and paste the prompt.

```bash
claude
```

```text
Run copilot -p 'create a poem about sighthounds' -s and show me the poem it returns.
```

Claude asks to run `copilot -p 'create a poem about sighthounds' -s` through its Bash tool; approve it. The command and its real stdout, trimmed:

```text
I'll write you a poem about sighthounds.

# The Sighthound

Built for the open, the long lean line,
a body that reads like a drawn-out breath,
deep in the chest where the heart beats fast,
narrow and light as a blade of grass.
...
So call them lazy, call them aloof,
they'll lift one eyebrow, and that's the proof:
they were never ours, not wholly, not quite,
they belong to the field, and the wind, and the light.
```

Expected result: Claude shows the Bash call, then the poem Copilot returned. If your settings already allow `Bash(copilot *)`, there is no prompt and the call runs straight away. Exit the session with `/exit`.

## Step 4: Chain `claude -p` into `copilot -p`

Now nobody is there to approve the call, so the rule goes on the command line. Claude runs headless, hands the prompt to Copilot, and returns Copilot's stdout inside its own envelope.

```bash
claude -p "Run this shell command and return its stdout verbatim, nothing else: copilot -p 'create a poem about sighthounds' -s" --allowed-tools "Bash(copilot *)" --output-format json
```

```json
{
  "type": "result",
  "subtype": "success",
  "is_error": false,
  "num_turns": 2,
  "session_id": "a6dd33a2-2010-4eee-9372-1d748b592ffd",
  "total_cost_usd": 0.5827186,
  "permission_denials": [],
  "result": "Sighthounds lean into the wind's long line,\nGreyhound, saluki, whippet, deerhound, fine\n..."
}
```

The `result` field, printed as text:

```text
Sighthounds lean into the wind's long line,
Greyhound, saluki, whippet, deerhound, fine
as drawn wire, built for the open run
where nothing outruns them beneath the sun.

They see the hare three fields away,
a flicker that turns the whole body to clay
fired into motion, coiled and released,
a bowstring loosed on the running beast.

Then home, they fold on the softest chair,
ribs like a harp, nose in the air,
and sleep the sleep of the truly fast,
dreaming of something that never outlasts
the first clean stride, the turning, the chase,
the wind's one law written over their face.
```

Expected result: `is_error` is `false`, `permission_denials` is empty, and `result` holds a poem. `num_turns` is 2: one turn to call Bash, one to return the output. `total_cost_usd` is Claude's share only; the DeepSeek tokens bill to DeepInfra.

To send Copilot back to GitHub's hosted models, close the shell or remove the five variables.
