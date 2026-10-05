# Build an Ask-Check Mod Test-First

Claude often ends a turn by asking something you already told it, and answering costs you a round trip. In this lab you build `ask-check`, a mod that spots those questions, shows your own earlier sentence in a band above the prompt, and sends it back on one key. The six tests in the starter are the specification: you start with one passing and grow the hooks module one behaviour at a time until all six pass.

| Step | What you build | Tests passing after |
|------|----------------|---------------------|
| 1 | Read the specification | 1 of 6 |
| 2 | Remember the user's prompts in mod state | 1 |
| 3 | Find the questions in an answer | 1 |
| 4 | Match a question against earlier sentences | 1 |
| 5 | Draw the band above the prompt | 2 |
| 6 | Send the answers back on one key | 3 |
| 7 | Ignore sentences pasted back from Claude | 4 |
| 8 | Honour a standing "no questions" instruction | 5 |
| 9 | Recognise a question asked before | 6 |
| 10 | Try it live | 6 |

---

## Where to Open Claude Code

Open Claude Code inside the starter and load it as a mod for the session. `--plugin-dir` is what makes Claude Code hot-reload the mod at the end of every turn that changes it, so each step's change is live in the same session without a restart.

```bash
cd labs/02-harness/lab-04-ask-check
claude --plugin-dir .
```

Both commands work unchanged in PowerShell. You need Claude Code 2.1.287 or later; mods are on by default from that version. The finished reference is beside the starter in `lab-04-ask-check-solution/`.

The starter holds the plugin manifest, `hooks/hooks.json` pointing at `hooks/ask-check.mjs`, the state contract in `types/index.d.ts`, the six tests in `tests/ask-check.test.ts`, and a hooks module that registers nothing:

```javascript
export function register(on) {}
```

Run the two checks from a second terminal in the same folder whenever a step asks for them, or let Claude run them. Neither needs a session or a sign-in.

---

## Step 1: Read the Specification

**Overview:** The tests drive real events through the mods runtime (a prompt, a finished turn, a band being drawn, a key press) and assert on what the band shows and what gets sent. Reading them first tells you what the mod must do before you write a line.

**Research / Planning / Discussion:**

```text
Read tests/ask-check.test.ts and types/index.d.ts in this folder. Do not write any code.

For each of the six tests, tell me in one sentence which events it fires, what it expects the band above the prompt to show, and what it expects to be sent. Then list the state keys in types/index.d.ts and say which test needs each one.
```

**Finding:** A good answer names `prompt.submit` and `turn.complete` as the events every test fires, and `ui.render` on `AbovePrompt` as what `$.ui.mount` draws. It should notice that only the first test presses the `send` button, that the standing-instruction test answers two questions with one sentence, and that the code-block test expects `already answered 0` even though the earlier prompt repeats Claude's own report. If it maps `asked` or `answers` to no test, push back: `asked` serves the repeat-question test and `answers` the pasted-back one.

Now run the baseline:

```bash
claude plugin validate .
claude plugin test
```

**Expected Outcome:** The validator finds the state contract but no hooks, and one test already passes, because an empty mod draws no band:

```text
  ❯ types ./types/index.d.ts declares state: ask-check.prompts, ask-check.questions, ask-check.asked, ask-check.answers, ask-check.count
  ❯ ./ask-check.mjs hooks: nothing
  ❯ ./ask-check.mjs calls: nothing on $
✔ Validation passed

 1 pass
 5 fail
```

---

## Step 2: Remember the User's Prompts

**Overview:** A mod's hooks share state, so what `prompt.submit` records, `turn.complete` and the band can read. Only prompts the user typed count: a prompt another session or a plugin submits arrives with a different origin.

**Recipe:**

```text
In hooks/ask-check.mjs in this folder, implement register(on) so the mod remembers what the user asked.

Add a prompt.submit hook that first awaits next(e) and keeps its result to return. Ignore any prompt whose e.origin?.kind is not composer, bridge or sdk, and any prompt whose trimmed text is empty. For a user prompt, increment a count in mod state and append { n: count, text } to a prompts list in state, with the text clipped to 4000 characters and only the last 40 prompts kept. Then reset the questions list in state to [].

Use $.state.get and $.state.set. Write each state reference literally as a const at the top of the file, for example const promptsRef = { plugin: "ask-check", key: "prompts" }. The keys are prompts, questions and count, matching types/index.d.ts.

Then run claude plugin validate . and show me the hooks: and calls: lines.
```

**Expected Outcome:** The first hook shows up in the validator, with state as its only reach:

```text
  ❯ ./ask-check.mjs hooks: prompt.submit
  ❯ ./ask-check.mjs calls: $.state.get, $.state.set
```

The references must be literal objects: a reference built from a variable fails validation, because the validator can only list state it can read from the source.

---

## Step 3: Find the Questions in an Answer

**Overview:** A question is a sentence that ends in `?`, but not every `?` is one: SQL placeholders in a code block and a `?` inside inline code are not questions to the user.

**Recipe:**

```text
In hooks/ask-check.mjs in this folder, find the questions at the end of each of Claude's answers.

Add and export a function questionsIn(answer) that returns the questions in an answer. Remove fenced code blocks and unwrap inline code first. Split the rest into sentences on newlines and on a sentence end followed by whitespace and then a capital letter, a digit, a quote, an asterisk or an opening parenthesis. Strip leading list, heading and quote markers and any ** bold markers, and keep only sentences that end with "?" and are 12 to 500 characters long.

Then add a turn.complete hook that awaits next(e) and keeps its result to return. Ignore subagent turns (e.agentId set), turns whose e.reason is not "answer", and turns whose e.answer is not a string. Otherwise store questionsIn(e.answer).map((question) => ({ question, answer: null })) in the questions state.

Then run claude plugin validate . and show me the hooks: line.
```

Check the function on its own:

```text
Call questionsIn from hooks/ask-check.mjs with node on this answer and show me the result:
"Done.\n\n```sql\nSELECT * FROM t WHERE x = ?\n```\nShould I also update the README with the hotkey?"
```

**Expected Outcome:** `turn.complete` joins the hooks line, and only the real question survives:

```text
  ❯ ./ask-check.mjs hooks: turn.complete, prompt.submit
```

```text
[ 'Should I also update the README with the hotkey?' ]
```

---

## Step 4: Match a Question Against Earlier Sentences

**Overview:** An earlier sentence answers a question when it shares enough of the question's meaningful words. Stop words and simple stemming keep "the", "should" and the difference between "mention" and "mentions" from deciding the match.

**Recipe:**

```text
In hooks/ask-check.mjs in this folder, match each question against what the user already said.

Add and export findAnswer(question, prompts). Tokenize text by lowercasing it and taking words of at least 3 characters made of letters (including äöüß) and digits, allowing . _ - inside a word. Drop pure numbers and a stop-word set of common English and German filler words (articles, pronouns, auxiliaries, and words like yes, okay, proceed, option, maybe, bitte, und, oder). Stem every word that contains no . _ - by removing a trailing ing, ed, es or s and then collapsing a doubled final letter.

Split each prompt into clauses on newlines, on "...", "…" and "->", on . ! ? ; followed by whitespace, and on numbered list markers such as "1." or "2)", and keep clauses of 3 to 300 characters. A clause is a candidate when it shares at least 2 tokens with the question and those cover at least 45% of the question's distinct tokens. Score a candidate as the shared count plus that ratio, let a later prompt win a tie, and return the best as { text: clause, n: prompt.n, via: "said" }, or null.

In the turn.complete hook, read the prompts from state and use findAnswer(question, prompts) as each question's answer instead of null.
```

Check it on its own:

```text
Call findAnswer from hooks/ask-check.mjs with node: the question "Should the README mention the send hotkey?" and one prompt { n: 1, text: "Keep the README short and mention the send hotkey. Do not write it yet." }. Show me the result.
```

**Expected Outcome:** The first clause of the prompt answers the question; the second clause shares too few words to compete:

```text
{
  text: 'Keep the README short and mention the send hotkey.',
  n: 1,
  via: 'said'
}
```

The tests still read 1 pass: nothing draws the result yet.

---

## Step 5: Draw the Band Above the Prompt

**Overview:** `ui.render` on `AbovePrompt` runs every time Claude Code draws the area above the prompt. Calling `next(e)` first and stacking your box on its result is what keeps another mod's band visible beside yours.

**Recipe:**

```text
In hooks/ask-check.mjs in this folder, draw the result as a band above the prompt.

Add a ui.render hook with the matcher { component: "AbovePrompt" }. Await next(e) first and keep the result as below. Return below unchanged when e.props.hasSurvey or e.props.isWorking is true, or when the questions state is empty.

Otherwise get Box and Text from $.ui.resolve(e) and build a column Box with paddingX 1 that holds:
- a summary Text reading "asked N · already answered M", yellow when M > 0 and dimColor otherwise
- for every answered question, a Text with wrap "truncate-end" reading   ↳ you said "<answer text>" (prompt <n>)   where the answer text is clipped to (e.props.bodyColumns or 80) minus 38 characters, ending in "…" when clipped

Return a column Box with your box first and below second when below exists, so a band another mod draws stays visible; return your box alone otherwise.

Then run claude plugin test and tell me which tests pass and which fail.
```

**Expected Outcome:** The unanswered-question test joins the one that already passed:

```text
(fail) ask-check > a question the user already answered shows their sentence and one key sends it
(fail) ask-check > a standing no-questions instruction answers every question
(fail) ask-check > a question asked again shows the reply to the first ask
(pass) ask-check > an unanswered question is counted without a send key
(pass) ask-check > the band clears on the next prompt and stays away while working
(fail) ask-check > question marks in code and pasted-back answer text are ignored
 2 pass
 4 fail
```

---

## Step 6: Send the Answers Back on One Key

**Overview:** A band button can act without a Claude turn. Submitting a prompt as the user from a mod is the one call that closes the loop: Claude receives your own earlier sentence as the reply.

**Recipe:**

```text
In hooks/ask-check.mjs in this folder, let the user send the already-given answers back with one key.

When at least one question is answered, put the summary Text and a Button side by side in a row Box, with a Text of three spaces between them. The Button has key "send", label "send already answered", hotkey "1" and plain true. Get Button from $.ui.resolve(e) as well.

Its onPress calls a top-level async function sendAnswered($). That function reads the questions state, keeps the answered ones, removes duplicate answer texts, clears the questions state, and submits as the user one prompt of this exact form:
Already answered: "<text>" (my prompt <n>); "<text>" (my prompt <n>). Proceed.
Use $.prompt.submit({ text, asUser: true }).

Then run claude plugin test and tell me which tests pass and which fail.
```

**Expected Outcome:** The first test passes, and the validator lists the new reach through the helper:

```text
  ❯ ./ask-check.mjs calls: $.prompt.submit (via sendAnswered), $.state.get, $.state.set, $.ui.resolve
```

```text
 3 pass
 3 fail
```

`sendAnswered` must be a function declared at the top level of the file: that is the only shape through which the validator can follow `$` into a helper.

---

## Step 7: Ignore Sentences Pasted Back from Claude

**Overview:** Users paste parts of Claude's own report into their next prompt. Those sentences share every word with Claude's follow-up question, so without a filter they look like answers to everything.

**Recipe:**

```text
In hooks/ask-check.mjs in this folder, stop matching a sentence the user only pasted back from Claude.

Users often paste part of Claude's own report into their next prompt, and that sentence then looks like an answer to everything. In the turn.complete hook, keep the last 10 answers in an answers state list. Normalize each one to lowercase, remove backticks, asterisks and underscores, collapse whitespace, and clip it to 8000 characters. Check the current answer before you add it to the list.

Pass the answers list to findAnswer as a third argument, and skip any clause of 25 characters or more whose normalized text appears inside one of those answers. Add an answers state reference next to the others; types/index.d.ts already declares it.

Then run claude plugin test and tell me which tests pass and which fail.
```

**Expected Outcome:**

```text
(pass) ask-check > question marks in code and pasted-back answer text are ignored
 4 pass
 2 fail
```

---

## Step 8: Honour a Standing "No Questions" Instruction

**Overview:** "No other questions, just do it" answers every question Claude asks afterwards, whatever its words. A rule like this is checked before any word matching.

**Recipe:**

```text
In hooks/ask-check.mjs in this folder, honour a standing instruction not to ask questions.

Before any matching, scan the prompts newest first, clause by clause, for this pattern:
/\b(no (other |more |further )?(questions?|q)\b|(do ?n.?t|stop|never) (ask|bother|bloat)\w*( me)?( with)? (any |more )?(questions?|findings)|without questions|bloat\w* me with questions|(invent|make up) (findings and )?questions)/i

When a clause matches, it answers every question in the turn as { text: clause, n: prompt.n, via: "rule" }, and the band shows it with the same "you said" lead as a matched sentence. Move the per-question decision into an exported function checkAnswer(answer, prompts, answers) that the turn.complete hook calls.

Then run claude plugin test and tell me which tests pass and which fail.
```

**Expected Outcome:**

```text
(pass) ask-check > a standing no-questions instruction answers every question
 5 pass
 1 fail
```

---

## Step 9: Recognise a Question Asked Before

**Overview:** When Claude asks the same thing twice, the best answer is whatever the user said right after the first ask, even if it shares no words with the question.

**Recipe:**

```text
In hooks/ask-check.mjs in this folder, recognise a question Claude already asked earlier in the session.

Keep an asked state list of the last 40 questions, each stored with the prompt count at the time it was asked as { question, n: count }, appended in the turn.complete hook whenever the turn has questions. A new question repeats an earlier one when the two share at least 2 tokens and those cover at least 50% of the smaller token set. Its answer is then the user's next prompt after the earlier ask (prompt n + 1), with whitespace collapsed and clipped to 300 characters, as { text, n, via: "replied" }.

In checkAnswer, try the standing rule first, then this repeat check, then findAnswer. In the band, list repeats after the answered ones with the lead: asked before, you replied. Leave them out of the "already answered" count and add " · asked before K" to the summary when K > 0. In sendAnswered, phrase them as a second sentence: You asked this before and I replied: "<text>" (my prompt <n>).

Then run claude plugin test and tell me which tests pass and which fail.
```

**Expected Outcome:** The specification is met, and the validator shows every hook the mod needs:

```text
  ❯ ./ask-check.mjs hooks: turn.complete, prompt.submit, ui.render{component=AbovePrompt}
✔ Validation passed

 6 pass
 0 fail
```

---

## Step 10: Try It Live

**Overview:** The tests prove the logic; a live session proves the wiring. The standing rule gives a result you can count on, because it answers any question whatever Claude's wording.

Send these two prompts in the session you started with `--plugin-dir .`:

```text
We will write a README for this mod later. Make your own choices, no questions. For now just say ok.
```

```text
Now ask me one thing about the README in plain text, then stop.
```

**Expected Outcome:** Claude asks something about the README, and the band appears above the prompt with the send key:

```text
 asked 1 · already answered 1   1: send already answered
   ↳ you said "Make your own choices, no questions." (prompt 1)
```

Press `1` on the empty prompt. The mod submits the reply for you, marked as coming from the plugin:

```text
› Prompt from the ask-check plugin
❯ Already answered: "Make your own choices, no questions." (my prompt 1). Proceed.
```

Claude then goes ahead and writes the README. Two cases where the band stays away, and why:

- A question asked through Claude's question dialog is not prose in the answer, so `questionsIn` never sees it.
- A long question shares too few of its words with a short earlier sentence to pass the 45% overlap, and the band shows `already answered 0`. That is the heuristic working as specified, not a fault.

Also watch the standing-rule pattern: "ask me a yes/no question" contains "no question", so it reads as an instruction not to ask.

---

## Cleanup

Generated type declarations land in `.claude-plugin/types/`, which the starter's `.gitignore` excludes. To return the starter to its shipped state, discard your changes and the README Claude wrote:

```bash
git restore hooks/ask-check.mjs
rm README.md
```

```powershell
git restore hooks/ask-check.mjs
Remove-Item README.md
```

---

## What You Just Practised

| Technique | Step | When to reach for it |
|-----------|------|----------------------|
| Tests as the specification | 1, 5 to 9 | Any mod: `claude plugin test` runs without a session, so every behaviour can be pinned before it ships |
| Mod state shared between hooks | 2, 7, 9 | Whenever one event has to remember what another one saw |
| Observe with `await next(e)` | 2, 3 | Recording what happened without changing it |
| Chaining a band with `next(e)` | 5 | Every `AbovePrompt` hook, so other mods' bands survive |
| Submitting as the user from a button | 6 | Closing a loop without a Claude turn |
| `claude plugin validate` as the reach inventory | 1 to 9 | Before trusting any mod, yours included |
