# Constrain What the Model Returns

Everything so far let the model decide whether to call a tool and what shape its answer takes. Three API-level controls remove that discretion when a pipeline cannot tolerate it: `tool_choice` decides whether a tool runs at all, Structured Outputs guarantees the JSON shape, and the Message Batches API trades latency for cost on work nobody is waiting for.

## tool_choice: Forcing or Releasing the Tool Call

`tool_choice` is set per request and has four values. The distinction that matters in production is between "the model may call a tool" and "the model must".

| Value | Guarantee | Reach for it when |
|---|---|---|
| `{"type": "auto"}` | Model decides: it may call a tool or answer in prose. The default. | Conversational turns, and the final turn of any pipeline |
| `{"type": "any"}` | Model must call one of the supplied tools, but picks which | Every input must produce a structured record, even an empty one |
| `{"type": "tool", "name": "x"}` | Model must call exactly that tool | The classification is already known, so the router step is waste |
| `{"type": "none"}` | Model may not call any tool | A turn that must only summarize what already happened |

The failure mode worth memorizing belongs to `any`. It forces a tool call on **every** turn, including the turn after the pipeline finished its last step. The agent has nothing left to do, so it calls a tool anyway, usually the first one in the pipeline, and loops forever.

```text
fetch_record -> transform_record -> load_record -> fetch_record -> ...
```

The fix is not fewer tools or a sterner prompt. `tool_choice` is request-scoped, so switch it back to `auto` on the turn after the last required call and the model regains the option to stop and answer.

Two smaller consequences follow from the same mechanic. Setting `any` with exactly one tool in the array is the cheapest way to guarantee that tool runs, which is what you want when short or uninformative inputs otherwise make the model reply conversationally. And `{"type": "tool", "name": "x"}` overrides the system prompt: if the prompt says "classify first, then extract", forcing the extraction tool wins anyway.

## Structured Outputs: Guaranteeing the Shape

Prompting for JSON and validating afterwards, the Zod pattern from [02: Core API Surface](../02-api-surface/readme.md), catches a malformed response. Structured Outputs prevents one. Supply a JSON Schema through `output_config.format` and the API constrains decoding at the token level, so a response that violates the schema cannot be generated.

```python
response = client.messages.create(
    model="claude-sonnet-5",
    max_tokens=1024,
    output_config={"format": {
        "type": "json_schema",
        "schema": {
            "type": "object",
            "properties": {
                "patient_id": {"type": "string"},
                "diagnosis": {"type": "string"},
                "prescribed_medication": {"type": ["string", "null"]},
            },
            "required": ["patient_id", "diagnosis", "prescribed_medication"],
        },
    }},
    messages=[{"role": "user", "content": note}],
)
```

The `["string", "null"]` type array is the piece people miss. A field that is genuinely absent from the source needs an explicit null branch; without one the model inconsistently omits the key, emits the string `"N/A"`, or invents a plausible value. Type arrays cost more to compile but are fully supported.

Note the parameter name. `output_config.format` is the generally available form; the older `output_format` parameter is deprecated.

Three rules of thumb decide which control you want:

- Need a guaranteed **shape**, no tool involved: Structured Outputs.
- Need a guaranteed **tool call**: `tool_choice`.
- Need to reject bad output at your own boundary and throw: Zod, after the fact.

### Enum Design for Ambiguous Input

A schema that offers only `["positive", "negative", "neutral"]` gives the model nowhere to put a sarcastic review, so it guesses and your analytics inherit the noise. Adding an explicit `"unclear"` value gives ambiguity a home and makes it filterable. The general rule: every enum that classifies real-world text needs an escape value, or the model will silently smear ambiguous cases across the ones you did define.

### Validation Belongs in Code, Not in the Prompt

When a number has to be right, extract the inputs and compute in your own code rather than asking the model to check its own arithmetic. For a purchase order, extract the line items and the printed total as separate fields, sum the items in application code, and compare. That detects both a misprinted document and a bad extraction, and neither result depends on the model doing math correctly.

### Retry With the Error Attached

Schema validation failures are usually recoverable, because the source document still contains what the model needs and the validator already knows exactly what went wrong. Feed the specific violation back ("expected an array of objects, received a single object") and the retry generally succeeds. The exception is a field that is genuinely absent from the source: no amount of retrying invents it, so log the failure, halt the loop, and flag the document.

## The Message Batches API

The Batches API processes large request sets asynchronously at roughly half the cost of synchronous calls. The trade is a completion window of **up to 24 hours** with no latency SLA inside it, and no way to expedite a submitted batch.

That single property decides every design question around it.

| Workload | Batch? | Why |
|---|---|---|
| Reprocessing 5 million legacy records overnight | Yes | Nobody is waiting; the discount is the point |
| Inline code completion in an IDE | No | A blocking, keystroke-latency workflow |
| Nightly documentation regeneration | Yes | Deadline is the next morning, not the next second |
| A support bot answering a live user | No | The user is on the other end of the wait |

Because you cannot predict when a batch lands, do not promise stakeholders a completion time, and do not schedule a downstream job against an estimate. Poll the batch status and trigger the next stage from the completion event.

The cost profile also changes how you develop. A $10,000 batch run that fails on a prompt defect costs $10,000 to repeat, so refine the prompt against a stratified sample of a thousand records on the synchronous API first. Two days of iteration up front is cheap against one wasted full run, and the sample is where you discover the edge cases that would otherwise fail silently at scale.

## Exploration Prompt

```text
Write one script that extracts {name, title} pairs from a block of text three ways:
prompt-and-parse, tool_choice forcing a single extraction tool, and
output_config.format with a JSON schema. Feed all three a deliberately
ambiguous input and print which ones produced schema-valid output.
```

## Helpful Claude Slash Commands

| Command | Usage |
|---|---|
| `/claude-api` | Look up the current `tool_choice` and `output_config` shapes before hand-writing a request body |
| `/cost` | Compare a synchronous prototype run against the batch price before committing a large job |
| `/security-review` | Audit the retry loop before pointing it at a paid batch endpoint |

## Key Topics covered in this module

- [Tool use and `tool_choice`](https://platform.claude.com/docs/en/build-with-claude/tool-use): the four values, forced calls, and the loop that `any` causes
- [Structured Outputs](https://platform.claude.com/docs/en/build-with-claude/structured-outputs): `output_config.format`, constrained decoding, and schema support
- [Message Batches API](https://platform.claude.com/docs/en/build-with-claude/batch-processing): the 24-hour window, pricing, and status polling
