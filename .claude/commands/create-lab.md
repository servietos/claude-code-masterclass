# Create Lab

$ARGUMENTS

Create a lab document in `labs/<module>/lab-<nn>-<slug>.md` following the conventions of this repository.

**Process:**

1. Parse `$ARGUMENTS` for: module number, lab number, lab title, and lab type (`guided`, `prompt-based`, or `discover-recipe`).
2. Write the new lab file to `labs/<module>/lab-<nn>-<slug>.md` using the structure for the chosen type below.
3. Do not create the file until you have confirmed module, number, title, and type with the user.

---

## Guided lab structure

````markdown
# <Verb-Action Title>

<One-sentence description of what the learner will accomplish.>

---

## Setup

<Universal setup steps. Add OS-specific sub-sections only when the commands actually differ between platforms, omit them when the steps are identical.>

```bash
command
```

---

## Step <n>: <Title>

1. Numbered instructions.
2. ...

```language
command or code
```

<Expected outcome sentence.>
````

Rules for guided labs:
- Use numbered lists for sequential steps; bullet lists for options.
- Every terminal block must declare a language (`bash`, `powershell`, etc.).
- Never include tool installation or SDK setup. This repository uses a devcontainer; all runtimes and global CLI tools are pre-installed.
- Never add OS-specific tracks. The devcontainer provides a single consistent environment for all platforms.
- Setup is limited to package restore commands (`npm install`, `dotnet restore`) and starting services.
- End with a verification step the learner can run to confirm success.

---

## Prompt-based lab structure

````markdown
# <Verb-Action Title>

<One-sentence description of what the learner will build.>

Each step follows the same pattern:

- **Overview** — what this step achieves
- **Research / Planning / Discussion** — an open prompt to reason through the problem before acting
- **Finding** — what to read and evaluate in Claude's response before moving on
- **Recipe** — a complete implementation prompt you can use as-is or adapt from your own findings
- **Expected Outcome** — observable artefacts that confirm success

---

## Setup

<Steps to get the project running before the lab begins.>

---

## Step <n>: <Title>

**Overview:** <What this step achieves and why it matters.>

**Research / Planning / Discussion:**

```text
<Open-ended prompt that asks Claude to read files, compare options, or reason through the problem. Must not contain the answer.>
```

**Finding:** <What a good response looks like. Name specific signals. Tell the learner when to push back.>

**Recipe:**

```text
<Exact, self-contained prompt the learner pastes into Claude Code.>
```

**Expected Outcome:** <Observable artefacts, files, server responses, or UI changes, that confirm the step succeeded.>

> The recipe above is one possible prompt based on typical findings from the research above. If your conversation led to different conclusions, use those instead.
````

Rules for prompt-based labs:
- Research prompts must be open-ended, they ask Claude to reason or read files, not execute a fix.
- Recipe prompts must be self-contained, no reference to earlier conversation context.
- Expected Outcome describes observable artefacts, not internal implementation.
- Steps build on each other; Recipe prompts may reference files created in prior steps.

---

## Discover-recipe lab structure

````markdown
# <Verb-Action Title>

<One-sentence description of what the learner will build.>

Each step follows the same pattern:

- **Overview** — what this step achieves
- **Research / Planning / Discussion** — an open prompt to reason through the problem before acting
- **Finding** — what to read and evaluate in Claude's response before moving on
- **Recipe** — a complete implementation prompt you can use as-is or adapt from your own findings
- **Expected Outcome** — observable artefacts that confirm success

---

## Running the Lab Starter

<Include this section whenever the lab has a pre-existing codebase to run. Provide exact, copy-paste commands, no explanation of what the stack is. End with one sentence describing what the learner should see when it starts successfully.>

```bash
<exact commands>
```

<What a successful start looks like.>

---

## Step <n>: <Title>

**Overview:** <What this step achieves and why it matters.>

**Research / Planning / Discussion:**

```text
<Open-ended prompt that asks Claude to reason, compare options, or read files. Must not contain the answer.>
```

**Finding:** <What a good response looks like. Name specific signals: a comparison table, a recommendation with reasoning, a file path. Tell the learner when to push back.>

**Recipe:**

```text
<Complete, self-contained implementation prompt. The learner must be able to skip the Research step and use this directly.>
```

**Expected Outcome:** <Observable artefacts, files, server responses, or UI changes, that confirm the step succeeded.>

> The recipe above is one possible prompt based on typical findings from the research above. If your conversation led to different conclusions, use those instead.
````

Rules for discover-recipe labs:
- The Research prompt must be open-ended, it asks Claude to reason or compare. It must not contain the answer.
- Finding must tell the learner what a good response looks like and when to push back. It is not a restatement of the goal.
- The Recipe prompt must be fully self-contained. The learner must be able to skip the Research step and use the Recipe directly.
- The blockquote note always uses the same phrasing shown above.
- Use this type when the lab involves design decisions, tradeoffs, or diagnostic work where learner agency matters.

---

## General rules

- File name: `lab-<nn>-<slug>.md`, two-digit zero-padded number, lowercase hyphen slug.
- The H1 is a bare verb-action phrase. Never prefix it with `Lab <nn>`, a number, or a type label; ordering comes from the file name and the module readme table.
- No bold or italic in body prose (headings and label words like **Goal** are fine).
- No inline comments in code blocks.
- Max 4 sentences per paragraph.
- No em dashes, use `,` `;` `:` or `()` instead.

---

**Expected usage:**

```text
/create-lab module=01 number=03 title="Permissions & CLAUDE.md" type=guided
/create-lab module=02 number=01 title="Context Engineering" type=prompt-based
/create-lab module=07 number=02 title="Orchestration Patterns" type=discover-recipe
```
