# Produce Stakeholder-Readable Specs with the BMAD Agent Chain

Run the same tag-search feature through BMAD's role chain: a PM writes the requirements, an Architect makes the technical calls, a Developer breaks the work into stories. You finish with documents written for people to approve, which is where BMAD differs from Spec Kit.

------

## Setup

Run [setup-bmad.ps1](setup-bmad.ps1) on Windows, or [setup-bmad.sh](setup-bmad.sh) elsewhere, before the session starts. It leaves a prepared run folder at `~/spec-runs/notes-cli-bmad`, separate from the Spec Kit run so the two frameworks' artefacts stay isolated, and outside this checkout because BMAD writes its own `_bmad/` tree and 46 skills into the project. Pass a path as the first argument to put it somewhere else.

```powershell
.\setup-bmad.ps1
```

Then start the session and confirm the install:

```powershell
cd $HOME\spec-runs\notes-cli-bmad
claude
```

```text
/bmad-help What is the entry point for a new feature?
```

`bmad-help` is BMAD's orientation skill: it names which agent to invoke next and what each one produces. The roles this demo uses are skills too: `bmad-agent-pm`, `bmad-agent-architect` and `bmad-agent-dev`, with `bmad-party-mode` for Part B.

## Part A: Run the Role Chain

Stop before implementation. The artefacts are the point of this demo, not the code.

```text
Use the bmad-agent-pm skill to produce a PRD for this feature: tag-based search and pinning on
notes-cli, AND semantics across tags, pinned notes sort first. Save the PRD to docs/prd.md.

Then use bmad-agent-architect to produce an architecture document covering schema additions,
migration strategy and query approach. Save it to docs/architecture.md.

Then use bmad-agent-dev to produce story files (one per implementable unit) in docs/stories/.
Each story should be small enough that a single Claude session can complete it.

Stop before implementation. Do not write source code.
```

Expected result: `docs/prd.md`, `docs/architecture.md`, and a `docs/stories/` folder. The PRD reads like something a product manager would sign off; the architecture document explains rationale, not just decisions.

## Part B: Try Both Invocation Modes

```text
Run the same feature through bmad-party-mode instead. Where do the PM and the Architect disagree,
and which of those disagreements would I have missed reviewing their documents one at a time?
```

The useful output here is the disagreement, not the documents.

## Part C: Compare the Two Frameworks

With both runs on disk, put the artefacts side by side:

```text
Compare ~/spec-runs/notes-cli-bmad/docs/prd.md against ~/spec-runs/notes-cli-speckit/specs/<feature>/spec.md:
  1. Length, and who each document is written for
  2. Which one states rationale and which one states requirements
  3. Which would you hand to a designer, and which to an agent
```

BMAD's PRD runs several pages and is written for a PM; Spec Kit's spec is roughly half the length and written for an agent to consume. Neither is better, and the choice is an audience decision rather than a quality one.

Both frameworks install from the network and run interactively, so what they generate depends on the model and on your phrasing. The file names here are what each pipeline typically produces, not a guaranteed output set.

## Part D: Write the Verdict

With all three traditions now run at least once, commit to a default rather than leaving the comparison open:

```text
Write side-by-side-verdict.md with these sections:

  ## When to reach for each
  - Plan Mode by hand: [one sentence]
  - Spec Kit: [one sentence]
  - BMAD-METHOD: [one sentence]

  ## Where the overlap is real
  [What do all three force you to do that you would otherwise skip?]

  ## Where the overhead bites
  [Which of the three would feel like ceremony on a one-hour feature?]

  ## My default
  [Which one would you reach for first on the next non-trivial feature, and why?]
```

The "my default" answer typically lands on Plan Mode by hand for small features, Spec Kit for unfamiliar domains, and BMAD when the artefacts themselves need to be read by non-engineering stakeholders.

## Helpful Claude Slash Commands

| Command | Usage |
|---|---|
| `/bmad-help` | BMAD's orientation command: lists available agents and the recommended starting point |

## Key Topics Covered in This Demo

- [BMAD-METHOD on GitHub](https://github.com/bmad-code-org/BMAD-METHOD): agent roster, install instructions, and party-mode documentation
- [Extended thinking](https://platform.claude.com/docs/en/build-with-claude/extended-thinking): the reasoning budget an Architect agent spends on trade-offs
