# Feature Specification: Meeting Cost Calculator

**Feature Branch**: `v2` (not created by this command)

**Created**: 2026-10-17

**Status**: Draft

**Input**: User description: "Teams keep scheduling recurring meetings without knowing what they cost. Build a small library with a command line wrapper that calculates what a meeting costs in salary time, so an organizer can see the number before they hit send."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - See the total salary cost of a meeting (Priority: P1)

A meeting organizer enters the meeting length in minutes and the list of attendee hourly rates. The tool returns the total salary cost of one occurrence of the meeting, before the invitation is sent.

**Why this priority**: The total is the number the organizer needs to decide whether the meeting is worth scheduling. Nothing else in this feature is useful without it.

**Independent Test**: Run the tool with a 60 minute meeting and three attendees at 100, 80 and 60 per hour. The reported total is 240. Run it again with a 30 minute meeting and one attendee at 90 per hour. The reported total is 45.

**Acceptance Scenarios**:

1. **Given** a meeting of 60 minutes with attendees at 100, 80 and 60 per hour, **When** the organizer runs the calculator, **Then** the total cost is 240 and the command exits with code 0.
2. **Given** a meeting of 30 minutes with one attendee at 90 per hour, **When** the organizer runs the calculator, **Then** the total cost is 45 and the command exits with code 0.
3. **Given** a valid meeting, **When** the organizer runs the calculator, **Then** the output shows the total cost.

---

### User Story 2 - See what each attendee contributes (Priority: P2)

After the total, the organizer sees the cost each attendee adds to the meeting, so they can judge whether the most expensive attendees need to be in the room.

**Why this priority**: The breakdown turns the total into a decision about who to invite. It depends on the total calculation in User Story 1.

**Independent Test**: Run the tool with the three attendees from User Story 1. The output lists each attendee by position (first, second, third) with their cost (100 for the first, 80 for the second, 60 for the third) and the listed costs add up to the total of 240.

**Acceptance Scenarios**:

1. **Given** a meeting with several attendees, **When** the organizer runs the calculator, **Then** the output lists each attendee by position in the list with the cost that attendee adds.
2. **Given** any valid meeting, **When** the organizer runs the calculator, **Then** the per attendee amounts add up exactly to the total before rounding.

---

### User Story 3 - Judge a recurring meeting (Priority: P3)

A team lead runs the calculator for a recurring meeting and takes the per occurrence total. They multiply it by the number of occurrences per year themselves to decide whether the series should be cancelled.

**Why this priority**: The annual figure is a multiplication of the per occurrence total. The tool supplies the input for that decision but does not perform the multiplication.

**Independent Test**: Run the tool once for the recurring meeting. The reported total is the cost of one occurrence, labelled as one occurrence so the reader can tell it apart from the annual cost.

**Acceptance Scenarios**:

1. **Given** a recurring meeting, **When** the team lead runs the calculator once, **Then** the output states the cost of one occurrence and does not report an annual figure.

---

### Edge Cases

- Zero attendees: the command exits with a non-zero code and names the field `attendees`.
- A duration of zero minutes: the command exits with a non-zero code and names the field `duration`.
- A negative duration: the command exits with a non-zero code and names the field `duration`.
- A negative hourly rate: the command exits with a non-zero code and names the attendee's position and the field `hourly rate`.
- A non-numeric hourly rate: the command exits with a non-zero code and names the attendee's position and the field `hourly rate`.
- An hourly rate of zero: valid. The attendee adds 0 to the total and still appears in the breakdown.
- A duration that is not a whole number of minutes: the command exits with a non-zero code and names the field `duration`.
- Invalid input produces no partial total and no partial breakdown.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST calculate the cost of a meeting as the meeting duration in hours multiplied by each attendee's hourly rate, summed over all attendees.
- **FR-002**: System MUST accept the meeting duration as a whole number of minutes greater than zero.
- **FR-003**: System MUST accept a list of one or more attendees, where each attendee is an hourly rate and nothing else.
- **FR-004**: System MUST report the total cost of the meeting, rounded half up to two decimal places (see Resolved Gaps).
- **FR-005**: System MUST report a per attendee breakdown that shows each attendee's position in the list and the exact, unrounded cost that attendee adds.
- **FR-006**: The per attendee amounts in the breakdown MUST add up exactly to the total before rounding.
- **FR-007**: The reported total MUST be the sum of the unrounded per attendee amounts, rounded half up to two decimal places. The breakdown amounts MUST NOT be rounded.
- **FR-008**: All amounts MUST be plain decimal numbers with no currency symbol, and System MUST NOT convert, detect or label a currency.
- **FR-009**: System MUST reject a meeting with zero attendees and name the field `attendees`.
- **FR-010**: System MUST reject a duration of zero or less minutes and name the field `duration`.
- **FR-011**: System MUST reject a duration that is not a whole number of minutes and name the field `duration`.
- **FR-012**: System MUST reject an hourly rate that is negative or not numeric, and name both the attendee's position and the field `hourly rate`.
- **FR-013**: System MUST accept an hourly rate of zero as valid.
- **FR-014**: System MUST NOT produce a total or breakdown for input it has rejected.
- **FR-015**: The command line wrapper MUST print the total and the per attendee breakdown for valid input and exit with code 0.
- **FR-016**: The command line wrapper MUST exit with a non-zero code for invalid input and print a message that names the offending field.
- **FR-017**: The calculation MUST be usable on its own, without starting the command line wrapper.
- **FR-018**: System MUST NOT make network calls, use a database, or depend on any external service.
- **FR-019**: System MUST report the cost of one occurrence only. The user multiplies that figure by occurrences per year.
- **FR-020**: System MUST depend only on the standard library of its implementation language, plus the test framework.

### Key Entities

- **Meeting**: A single occurrence with a duration in whole minutes and a list of attendees.
- **Attendee**: A participant represented only by an hourly rate, identified by its position in the list.
- **Cost Result**: The total cost of one meeting occurrence, plus one line per attendee giving that attendee's position and the exact amount that attendee adds.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Both worked examples report the expected totals (240 and 45) in every run.
- **SC-002**: For every valid meeting, the per attendee amounts add up to the total before rounding.
- **SC-003**: Every invalid input case in the edge case list ends with a non-zero exit code and a message that names the offending field.
- **SC-004**: Every valid input ends with exit code 0 and shows both the total and the breakdown.
- **SC-005**: An organizer gets the cost of a meeting from a single command, with no network access and no setup beyond the tool itself.

## Resolved Gaps

- **Annual cost (Q1)**: Out of scope. The team lead multiplies the printed total by occurrences per year (FR-019).
- **Rounding (Q2)**: The total is rounded half up to two decimal places. The breakdown amounts stay unrounded. "The breakdown sums to the total" means the breakdown sums to the total before rounding (FR-006, FR-007).
- **Currency (Q3)**: Amounts are currency-agnostic decimals with no symbol (FR-008).
- **Attendee identity**: Attendees are a list of hourly rates and nothing more. No name or label is captured. An attendee is identified by its position in the list, such as first or second.

## Assumptions

- Duration is entered in whole minutes. Hours are derived from minutes for the calculation.
- Rates are plain decimal numbers.
- The cost counts only the salary time of the listed attendees. Room, equipment and preparation time are out of scope.
- The tool is used from a terminal by one person at a time. No sharing, storage or history of past calculations is part of this feature.
- Annual cost, occurrence counts and cancellation decisions are out of scope (see FR-019).
