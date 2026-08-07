---
presents: demo-bmad-agent-chain.md
budget: 4 min
beats: 4
---

# Present: Produce Stakeholder-Readable Specs with the BMAD Agent Chain

BMAD's role chain buys artefacts a non-engineer can approve. Choosing between the three traditions is an audience decision, not a quality one. Four beats: the roles and their hard stop, party mode, the length comparison, the verdict.

------

**Shell:** setup ships twice, [`setup-bmad.ps1`](setup-bmad.ps1) on Windows and [`setup-bmad.sh`](setup-bmad.sh) elsewhere; both prepare `~/spec-runs/notes-cli-bmad`, kept separate from the Spec Kit run and outside this checkout because BMAD writes its own `_bmad/` tree and 46 skills. The beats quote no shell, only skills invoked inside the session.

## Beats

### Beat 1: three roles, three artefacts, and a hard stop before code (1.5 min)

**Open:** [Part A: Run the Role Chain](demo-bmad-agent-chain.md#part-a-run-the-role-chain) · [`setup-bmad.ps1`](setup-bmad.ps1)
**Say:** Different stages need different questions asked, and one general session answers all of them at once. Separate invocations keep product intent and schema detail reviewable on their own terms.

```text
Use the bmad-agent-pm skill to produce a PRD for this feature: tag-based search and pinning on
notes-cli, AND semantics across tags, pinned notes sort first. Save the PRD to docs/prd.md.

Then use bmad-agent-architect to produce an architecture document covering schema additions,
migration strategy and query approach. Save it to docs/architecture.md.

Then use bmad-agent-dev to produce story files (one per implementable unit) in docs/stories/.
Each story should be small enough that a single Claude session can complete it.

Stop before implementation. Do not write source code.
```

**Result:** three documents and no source, none of them linkable: `docs/prd.md`, `docs/architecture.md` and `docs/stories/` all land in the `~/spec-runs/notes-cli-bmad` run folder outside this checkout.

**Gotcha:** the last line is the one to read aloud; letting the chain slide into implementation destroys the comparison the demo is set up to make.

### Beat 2: party mode makes the disagreement the output (1 min)

**Open:** [Part B: Try Both Invocation Modes](demo-bmad-agent-chain.md#part-b-try-both-invocation-modes) · [BMAD-METHOD](readme.md#bmad-method)
**Say:** Each role document is internally coherent, so reviewing them one at a time hides where the roles conflict. Party mode trades the approval gate for that friction happening where you can watch it.

```text
Run the same feature through bmad-party-mode instead. Where do the PM and the Architect disagree,
and which of those disagreements would I have missed reviewing their documents one at a time?
```

**Result:** no new document, and nothing to link. What comes back is the list of places the PM and the Architect conflict, which reviewing their documents separately never surfaces.

**Gotcha:** if the room sees no disagreement at all, the feature was too small to need the chain.

### Beat 3: length and audience, not better and worse (1 min)

**Open:** [Part C: Compare the Two Frameworks](demo-bmad-agent-chain.md#part-c-compare-the-two-frameworks) · [demo-spec-kit-pipeline.md](demo-spec-kit-pipeline.md)
**Say:** The variable that differs is the reader: one artefact is written for a person to approve, the other for an agent to consume. Each is verbose exactly where its reader needs it.

```text
Compare ~/spec-runs/notes-cli-bmad/docs/prd.md against ~/spec-runs/notes-cli-speckit/specs/<feature>/spec.md:
  1. Length, and who each document is written for
  2. Which one states rationale and which one states requirements
  3. Which would you hand to a designer, and which to an agent
```

**Result:** both documents sit in run folders outside this checkout, so the evidence is in words: BMAD's PRD runs several pages and is written for a PM, Spec Kit's spec is roughly half the length and written for an agent to consume.

**Gotcha:** both frameworks install from the network and generate interactively, so a file name missing from your run is drift in the tool, not a broken demo.

### Beat 4: end with a default, not an open comparison (0.5 min)

**Open:** [When to Reach for Each](readme.md#when-to-reach-for-each) · [Part D: Write the Verdict](demo-bmad-agent-chain.md#part-d-write-the-verdict)
**Say:** Nobody weighs three columns of a table at the moment they need to start planning. Naming a first choice per situation is what turns an hour of frameworks into something used next week.

```text
Write side-by-side-verdict.md with these sections:

  ## When to reach for each
  - Plan Mode by hand: [one sentence]
  - Spec Kit: [one sentence]
  - BMAD-METHOD: [one sentence]
...
  ## My default
  [Which one would you reach for first on the next non-trivial feature, and why?]
```

**Result:** `side-by-side-verdict.md` in the run folder, not linkable from here. It typically lands on Plan Mode by hand for small features, Spec Kit for unfamiliar domains, and BMAD when non-engineering stakeholders approve.

**Gotcha:** the overhead question is the tiebreaker, since all three would feel like ceremony on a one-hour change.

## If the room asks

| Question | Answer |
|---|---|
| Are the BMAD roles agents or skills? | Skills: `bmad-agent-pm`, `bmad-agent-architect`, `bmad-agent-dev`, `bmad-party-mode`, and `bmad-help` for orientation. |
| Why a separate run folder from Spec Kit? | BMAD writes its own `_bmad/` tree and 46 skills; separate folders keep both frameworks out of this checkout and out of each other. |
| When does the extra length pay off? | When someone outside engineering approves before implementation; on a one-hour feature it is ceremony. |
| Sequential or party mode? | Sequential when you want a human checkpoint between stages, party mode when the trade-off review fits in one sitting. |
| Where is the feature both pipelines describe? | Checked in once at [notes-cli-solution/](notes-cli-solution/), with `--tag` on `add` and `pinned DESC, id DESC` on `list`; the code does not care which tradition produced the paperwork. |
