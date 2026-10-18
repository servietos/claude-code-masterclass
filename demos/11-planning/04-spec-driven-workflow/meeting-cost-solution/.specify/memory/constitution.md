<!--
SYNC IMPACT REPORT (temporary scratch for review, remove before commit)
Version change: template (unversioned) → 1.0.0
Modified principles (template slot → new title):
  [PRINCIPLE_1_NAME] → Separation of Concerns
  [PRINCIPLE_2_NAME] → No Hidden Dependencies
  [PRINCIPLE_3_NAME] → Explicit Failure
  [PRINCIPLE_4_NAME] → Money Is Never a Float
  [PRINCIPLE_5_NAME] → Every Acceptance Criterion Has a Test
Added principles: Offline by Default (sixth principle, beyond the five template slots)
Added sections: none
Removed sections: [SECTION_2_NAME] and [SECTION_3_NAME] placeholders, no content supplied in the input
Deferred TODOs: none
Not written: the input's "How the agent uses this" note describes /speckit-plan behavior, not governance
-->

# Meeting Cost Calculator Constitution

## Core Principles

### Separation of Concerns

Calculation logic MUST NOT import the command line layer. The logic module MUST be importable and testable without invoking the CLI.

Rationale: tests exercise the calculation directly, without starting a process or parsing arguments.

### No Hidden Dependencies

The project MUST use only the standard library, plus the test framework. Adding any other package requires a written rationale in `plan.md`.

### Explicit Failure

Invalid input MUST produce a named error that identifies the offending field. Input MUST NOT be silently coerced, defaulted, or clamped.

Rationale: a silent default hides a wrong input, and the organizer then trusts a wrong cost.

### Money Is Never a Float

Currency amounts MUST use a decimal or integer minor-unit type. Binary floating point MUST NOT be used for any monetary result.

Rationale: binary floating point cannot represent most decimal amounts exactly, so totals drift by fractions of a cent.

### Every Acceptance Criterion Has a Test

Each acceptance criterion in `spec.md` MUST have a corresponding test. A criterion without a test makes its task incomplete.

### Offline by Default

The program MUST NOT make network calls. It MUST NOT write to the filesystem outside the project directory.

## Governance

This constitution supersedes all other practices in this project. Plans, specs, tasks, and code MUST comply with every principle above.

**Compliance review**: `/speckit-plan` MUST verify its proposal against each principle and state the result for each one. A violation, such as a float used for a monetary total or a package outside the standard library without a rationale in `plan.md`, stops the plan at the checkpoint before any code is written.

**Amendment procedure**: An amendment is a change to this file. Each amendment MUST update the version line, the Last Amended date, and the Sync Impact Report.

**Versioning policy**: Semantic versioning applies.

- MAJOR: a principle is removed or redefined in a way that invalidates existing plans or code.
- MINOR: a principle or section is added, or guidance is materially expanded.
- PATCH: wording, clarification, or typo fixes that change no obligation.

**Version**: 1.0.0 | **Ratified**: 2026-10-17 | **Last Amended**: 2026-10-17
