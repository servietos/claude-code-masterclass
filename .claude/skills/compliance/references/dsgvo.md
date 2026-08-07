# DSGVO / GDPR (leaf of the `compliance` skill): Personal-Data Compliance Check

Leaf of the `compliance` master skill. Covers the EU General Data Protection Regulation
(Regulation 2016/679), known in German as the **Datenschutz-Grundverordnung (DSGVO)** and in
English as the **GDPR**, plus its Austrian companion law the **Datenschutzgesetz (DSG)**.

This is the personal-data half of compliance. For the AI-specific half, see the sibling leaf
[`eu-ai-act`](eu-ai-act.md) (`references/eu-ai-act.md`). Any feature that uses AI to read, extract, or generate
content about a person is in scope for **both** leaves at once: classify the AI use in the AI Act
leaf, and run this personal-data check here.

Source of truth (re-fetch before relying on specific articles or thresholds):
[eur-lex GDPR full text](https://eur-lex.europa.eu/eli/reg/2016/679/oj),
[GDPR-info.eu article index](https://gdpr-info.eu/),
Austria: [dsb.gv.at (Datenschutzbehörde)](https://www.dsb.gv.at/).

> **Not legal advice.** Everything this leaf produces is engineering-team orientation, not a
> legal opinion. Any document it helps author must say so, and must carry a "get counsel /
> the DPO to confirm before any external compliance claim" line.

## When to use

- Someone asks "are we DSGVO/GDPR compliant", "check for DSGVO compliance", "do we need a privacy
  notice / Datenschutzerklärung", "what's our lawful basis", or "can we store/keep this data".
- A feature is being added that collects, stores, transmits, or displays **personal data** (any
  information about an identifiable living person: name, email, phone, address, tenancy, employee
  record, photo, an IP address, a geolocated address, an AI extraction of any of these).
- Data is about to leave the EU/EEA (a third-country API call, a hosted model, a maps/geocoding
  service, cloud storage in a non-adequate region).
- A privacy notice, consent screen, cookie banner, or processor contract needs review.
- A data-subject request arrives (access, deletion, correction, export).
- Something went wrong: a suspected data breach, a leak, an over-collection.

## 1. Scope check first (does the DSGVO even apply?)

The DSGVO applies whenever you process **personal data** of people in the EU/EEA, regardless of
where your company or servers sit. Two questions settle scope:

1. **Is any field personal data?** If a record can be tied to an identifiable person, directly
   or indirectly (via an id, an email, an address, a device), it is personal data. Pseudonymized
   data is still personal data; only truly anonymous data (irreversibly non-attributable) is out.
2. **Are any of the people in the EU/EEA?** If yes, the DSGVO applies to that processing.

If both are yes, continue. If a field is a **special category** (Art. 9: health, biometric,
racial/ethnic origin, political/religious belief, trade-union membership, sex life/orientation),
flag it immediately: special categories need an Art. 9 exception on top of an Art. 6 lawful basis,
and are the highest-risk data to hold.

## 2. Your role: controller vs processor

- **Controller (Verantwortlicher):** decides *why* and *how* data is processed. The app operator
  is almost always the controller for its users' data.
- **Processor (Auftragsverarbeiter):** processes data on the controller's behalf and instructions
  (a hosting provider, a hosted-model API, a maps/geocoding service, an email/SMS sender, an
  analytics vendor). Every processor needs a **data-processing agreement (Auftragsverarbeitungs-
  vertrag, AVV / Art. 28 DPA)** in place before it touches personal data.

List every third party that receives personal data and confirm an Art. 28 agreement exists for
each. A missing AVV with a live processor is a common and material gap.

## 3. Lawful basis (Art. 6) — every processing needs exactly one

Pick the single most appropriate basis per processing purpose; do not stack "consent + contract"
as a hedge.

| Basis (Art. 6(1)) | Use when | Notes |
| --- | --- | --- |
| **(a) Consent** | No other basis fits (marketing, non-essential cookies, optional features) | Must be freely given, specific, informed, unambiguous, opt-in, and **as easy to withdraw as to give** (Art. 7). No pre-ticked boxes. |
| **(b) Contract** | Processing is necessary to deliver the service the person signed up for | The default basis for core app data (an account, a booking, a tenancy record). |
| **(c) Legal obligation** | A law requires you to keep it (tax, accounting retention) | Cite the actual law. |
| **(d) Vital interests** | Life-or-death only | Rare. |
| **(e) Public task** | Official authority / public-interest task | Mostly public bodies. |
| **(f) Legitimate interests** | A genuine business need not overridden by the person's rights | Requires a documented **balancing test (LIA)**. Cannot be used by public authorities for their tasks. |

Document the basis per purpose. This mapping is the backbone of the privacy notice and the
records of processing.

## 4. The seven principles (Art. 5) — the check to run against every feature

| Principle | Concrete question to ask of the feature |
| --- | --- |
| **Lawfulness, fairness, transparency** | Is there a lawful basis (Section 3), and does the person know about it? |
| **Purpose limitation** | Is the data used only for the purpose it was collected for? No silent repurposing. |
| **Data minimization** | Is every field actually needed? Drop what you don't use. The single most common finding. |
| **Accuracy** | Can wrong data be corrected? Is stale data refreshed or removed? |
| **Storage limitation** | Is there a **retention period** and an actual deletion mechanism, not "keep forever"? |
| **Integrity & confidentiality** | Encryption in transit and at rest, access control, least privilege (see Art. 32, Section 7). |
| **Accountability** | Can you *demonstrate* all of the above with records, not just assert it? |

## 5. Data-subject rights (Arts. 15–22) — can the app actually honour them?

The controller must be able to fulfil these, generally within **one month**:

- **Access (Art. 15):** provide a copy of the person's data and the processing details.
- **Rectification (Art. 16):** correct inaccurate data.
- **Erasure / "right to be forgotten" (Art. 17):** delete on request when no basis to keep it.
- **Restriction (Art. 18):** freeze processing while a dispute is resolved.
- **Portability (Art. 20):** export the person's data in a structured, machine-readable format.
- **Objection (Art. 21):** stop processing based on legitimate interests / direct marketing.
- **Automated decisions & profiling (Art. 22):** a person may refuse a solely-automated decision
  with legal or similarly significant effect. This is the direct bridge to the [`eu-ai-act`](eu-ai-act.md)
  leaf: if AI decides something about a person autonomously, Art. 22 DSGVO **and** the AI Act
  high-risk analysis both fire. The usual safe design (a human reviews and confirms every AI
  output before it is acted on or stored) satisfies both at once; name that invariant explicitly.

For each right, verify there is a real mechanism (a support process is acceptable; a hard-coded
"we can't delete that" is a finding).

## 6. Transparency: the privacy notice (Arts. 13/14)

If you collect data you must inform the person, at collection time, in plain language:

- Who the controller is (and the DPO, if any, and contact details).
- What data, for what purpose, on what lawful basis (and the legitimate interest, if (f)).
- Who receives it (processors, third countries) and the safeguards for transfers.
- How long it is kept (retention).
- Their rights (Section 5) and how to exercise them, including the right to complain to the
  supervisory authority (in Austria: the **Datenschutzbehörde**).
- Whether any decision is automated, and meaningful information about the logic (ties to Art. 22
  and the [`eu-ai-act`](eu-ai-act.md) Art. 50 disclosure: keep them consistent, do not contradict each other).

For a consent/ToS screen that also involves AI, reuse the two-tier essential-visible +
"Weitere Informationen" expansion pattern from the [`eu-ai-act`](eu-ai-act.md) leaf so the DSGVO processing
text and the AI disclosure sit in one coherent, non-overwhelming block.

## 6a. Cookie consent in practice (opt-in gating)

For a website that loads a non-essential tracker (Google Analytics, gtag, a marketing pixel),
a notice-only banner ("we use cookies" + an Accept button that gates nothing) is not compliant.
Non-essential cookies need opt-in consent (Art. 6(1)(a)): the script must not run until the
visitor actively consents, and declining must be as easy as accepting.

Concrete pattern that satisfies this on a static or server-rendered site:

- **Do not auto-load the tracker.** Replace the auto-firing analytics `<script>` with a
  consent-gated loader: define a function that injects the tracker, and call it on page load
  ONLY if the stored choice is "accepted". On the accept click, call it directly (no reload
  needed); on decline, do nothing.
- **Two buttons, not one.** Accept and Reject (Ablehnen), styled equally. The banner stays until
  the visitor makes a choice; store "accepted" or "declined" in a first-party cookie (a year is
  typical) so it is not re-asked every page.
- **Enable IP anonymization** on the analytics config, and disclose the tool in the privacy
  notice (Section 6): name the provider, the lawful basis (consent), the US transfer and its
  mechanism (SCC / EU-US Data Privacy Framework), and that consent is withdrawable (delete the
  cookie / choose Reject next visit).
- **A 1:1 site mirror inherits the original's non-compliant banner.** When mirroring a live site
  (see the `static-site-mirror` skill), the copied cookie banner and un-gated analytics come
  along verbatim; converting to opt-in gating is a deliberate, disclosed deviation from 1:1.

## 6b. Impressum and Datenschutzerklärung must name the SAME controller

On Austrian/German sites the imprint (Impressum, per ECG / MedienG) and the privacy notice
(Datenschutzerklärung) both identify the responsible entity. They must name the SAME legal
entity and contact. A mismatch (the Impressum naming one GmbH, the privacy notice another) is a
real and common finding: it makes the controller ambiguous, which undermines every data-subject
right that depends on knowing whom to contact. Cross-check the two pages whenever either is
touched; if they disagree, do not guess which is correct: confirm the actual controller with the
owner, then make both consistent.

## 6c. The zero-tracking static site (coming-soon pages, brochureware)

A single static page with no cookies, no analytics, no forms and self-hosted fonts looks like it
has no personal-data surface at all. It usually has two, and both are easy to miss because
nothing in the page source reveals them.

- **The web server's access log is the personal data.** The default config of every mainstream
  image (including `nginx` and `nginx-unprivileged`) logs each request with the client IP to
  stdout. In a container that lands in the Docker json-file log, whose **default driver has no
  size or age cap at all**, so IP-bearing records accumulate forever: an Art. 5(1)(e)
  storage-limitation finding on a page that "collects nothing". Two clean fixes: `access_log off;`
  in the server block (correct for a page with nothing to analyse, and it lets the notice make an
  absolute claim instead of a retention promise), or masked IPs plus a `logging:` block with
  `max-size` / `max-file`. Do both when in doubt: turn the access log off *and* cap the driver, so
  residual error output stays bounded too.
- **An imprint is owed even by a placeholder page.** In Austria § 5 ECG (and § 25 MedienG for the
  media-owner disclosure) binds any commercially operated site, a coming-soon teaser included. A
  footer line with company name, address and VAT ID is **not** an imprint: it is missing the
  register number and court, the trade authority, chamber membership with a pointer to the
  applicable trade rules, the managing director, and an email inside the imprint block itself.
  Verify the required set against the current statute; do not ship the list from memory.

**Put both texts on the page, not on invented subpages.** A one-page static site fronted by a
server that deliberately 404s unknown paths has nowhere for `/impressum` to live, and a subpage
would be a second document containing nothing else. In-page sections plus a permanent footer nav
satisfy the "easily, directly and permanently accessible" requirement. Match the page's own
language (a German page gets German texts, an English page English ones, with the German legal
terms in parentheses when the operator is Austrian or German), and keep § 6b's same-controller
rule: one entity, named identically in both.

### Never assert a compliance fact you have not verified

A privacy notice necessarily makes factual claims: "our server keeps no access log", "a
processor agreement under Art. 28 is in place", "no data is transferred to a third country".
Two rules follow, and the second is the one that gets violated:

- **Prove the claims you can prove, mechanically.** For the log claim: build the image, run it,
  issue a few requests including a 404, then count access lines in the container log
  (`docker logs <c> | grep -c "GET /"` must be `0`). That is a real test of the sentence the
  notice contains, and it takes one command.
- **Mark the claims you cannot prove, at the exact spot.** An AVV with the hosting provider is
  usually concluded in a customer portal you cannot see from the codebase. Leave the required
  sentence in place (it is what the notice must say) and put a `TODO` comment immediately next to
  it naming what must be confirmed before launch. Same for register numbers and authority names:
  **never invent a registry value**, and prefer an inline `TODO` comment over a visible
  `[FILL ME]` placeholder, which reads as broken if the page goes live early.

### Infrastructure facts come from the deploy manifest, never from the IaC defaults

A privacy notice states where data is processed and stored. That sentence is a factual claim, and
the infrastructure-as-code file is the wrong place to source it: a Bicep or Terraform parameter
default is an *intention*, and the deployed resource may sit somewhere else entirely. In one audit
`infra/azd-main.bicep` declared `apiLocation = 'swedencentral'` while the deploy manifest recorded
the live API as `...westeurope-01.azurewebsites.net`; the notice was "corrected" to the wrong region
on the strength of the Bicep default alone.

Order of authority for "where does this run":

1. The live resource, queried (`az`, `gcloud`, the provider console).
2. The repo's deploy manifest (`deploy.json` or equivalent), which records what was actually shipped.
3. The IaC defaults, which are only a statement of intent.

Two further traps in the same family:

- **A resource named in config may not exist.** Confirm it before writing a claim about it. A
  project endpoint appearing in `appsettings.json` and a deploy config proved unreachable: no
  matching account existed in any subscription the CLI could see.
- **The data store is often absent from the IaC.** A database provisioned by hand, inherited, or
  running on a rented box will have no module in `infra/` and an empty connection string in the
  committed config. Art. 13(1)(e) still requires it named and Art. 13(1)(f) still requires its
  transfer position, so the gap must be closed by asking the owner, never by inference.

### A consent control the backend ignores is a false statement, not a missing feature

When adding an opt-in, opt-out, or withdrawal control, grep the backend for the field in the same
change. A widget that transmits `AiResearchOptOut` to an endpoint where the identifier appears
nowhere is worse than having shipped no control at all: an absent control is an omission, while a
control that visibly does nothing is an affirmative misrepresentation to the data subject, and the
privacy notice built on it becomes untrue. The same applies to a cookie banner whose "Reject" path
still loads the tracker, and to a deletion request form with no deletion mechanism behind it.

Corollary for retention: a stated retention period is a claim about a mechanism. If nothing in the
codebase deletes the rows (no scheduled job, no `ExecuteDelete`, no retention policy), either build
it or state the period the system actually enforces. "We keep this for 24 months" with no deleting
code is an Art. 5(1)(e) finding wearing a compliance costume.

### Self-certification is itself a defect

Strike any sentence in which the site certifies its own compliance: "This website complies with the
ECG, the DSG, the GDPR and the UGB", "This Impressum is effective and legally binding", "we conduct
regular security audits", "incident response procedures are in place". These are unverifiable
assertions that an audit will usually contradict, and they add nothing a regulator credits. Keep
only the claims that name a mechanism you can evidence, and attach a `TODO` to the ones the notice
must contain but you cannot yet prove.

### One home per fact across the imprint, notice and terms

Legal pages accrete duplicates: the same contact block on three pages, liability limits stated in
three different sections with three different carve-outs, a certification list copied from the
About page. Duplication is not merely untidy, it is a correctness risk, because the copies drift and
a reader cannot tell which one governs.

Assign each disclosure exactly one home and cross-reference from the others:

| Belongs in | Content |
| --- | --- |
| **Imprint** | Identity, registration, trade authority, media-owner disclosure, infrastructure and data locations |
| **Privacy notice** | Every processing purpose, basis, recipient, retention, transfer, and the data-subject rights with their exercise route and the supervisory authority |
| **Terms** | Warranty and liability limits, intellectual property and trademarks, professional-advice disclaimer, governing law, jurisdiction, consumer conciliation |

The controller identity is the one legitimate duplicate: § 5 ECG needs it in the imprint and
Art. 13(1)(a) needs it in the notice. Keep those two byte-identical (see § 6b).

### The reverse-proxy trap: a later edge re-introduces the log you just removed

Turning off the origin server's access log makes the notice true **only for the topology you
tested**. The moment a reverse proxy or edge (Caddy, Traefik, nginx, a CDN) is put in front to
terminate TLS, it starts writing its own access log with the same client IPs, and the sentence
silently becomes false. Whenever the deployment topology changes, re-check every factual claim in
the notice: either disable the access log at the new edge for those hosts, or update the wording.
Record this as an explicit item in the deployment runbook, because the change that adds TLS is
never the change that is reviewing the privacy notice.

## 7. Security: technical & organizational measures (Art. 32)

Appropriate to the risk. Baseline the app should be able to evidence:

- TLS in transit; encryption / access-controlled storage at rest for sensitive fields.
- Authentication and least-privilege authorization (no shared admin accounts, no broad reads).
- Secrets kept out of source control and logs (no personal data or tokens in log lines).
- Pseudonymization where feasible; backups and a tested restore path.
- Logging/audit of access to personal data, and a way to detect anomalies.

In German these are the **technische und organisatorische Maßnahmen (TOMs)**; a documented TOM
list is often expected by processors and auditors.

## 8. Records, DPIA, breaches, transfers, DPO (the accountability artifacts)

- **Records of processing (Art. 30) — Verzeichnis von Verarbeitungstätigkeiten:** a register of
  each processing activity (purpose, categories of data and people, recipients, transfers,
  retention, security). Required for most organizations; the reference document an auditor asks
  for first.
- **DPIA (Art. 35) — Datenschutz-Folgenabschätzung:** required when processing is likely high-risk
  to individuals (large-scale special-category data, systematic monitoring, new tech with
  significant effects). An AI feature deciding about people is a classic DPIA trigger; coordinate
  with the [`eu-ai-act`](eu-ai-act.md) high-risk analysis.
- **Breach notification (Arts. 33/34):** notify the supervisory authority **within 72 hours** of
  becoming aware of a breach that risks people's rights, and notify affected individuals if the
  risk is high. Have the contact path and template ready *before* an incident.
- **International transfers (Chapter V):** data leaving the EU/EEA needs a legal transfer
  mechanism: an adequacy decision, Standard Contractual Clauses (SCCs), or another Art. 46
  safeguard. Every third-country API call (a hosted model, a maps/geocoding service, US-hosted
  storage) is a transfer. Check the vendor's mechanism; a US vendor typically relies on the
  EU-US Data Privacy Framework or SCCs. For the DeepInfra model host specifically (US-only, AVV
  status, sub-processor chain), see the sibling leaf [`deepinfra-dsgvo`](deepinfra-dsgvo.md)
  (`references/deepinfra-dsgvo.md`).
- **DPO (Art. 37) — Datenschutzbeauftragter:** required for public authorities, large-scale
  systematic monitoring, or large-scale special-category processing. If required and absent,
  that is a finding.

## 9. The compliance-check checklist

Run this against the feature or the whole app. Each item is verifiable; document evidence, not
just a tick.

- [ ] Every personal-data field is inventoried, and each has a documented **purpose** and
      **lawful basis** (Art. 6; Art. 9 exception too, if special-category).
- [ ] **Data minimization** applied: no field collected that isn't used.
- [ ] A **retention period** and a real **deletion mechanism** exist for each data category.
- [ ] A **privacy notice** (Datenschutzerklärung) exists and is accurate, reachable, and plain.
- [ ] **Consent** (where used) is opt-in, granular, logged, and withdrawable as easily as given.
- [ ] All **data-subject rights** (access, rectification, erasure, restriction, portability,
      objection, no-unreviewed-automated-decision) have a working mechanism.
- [ ] Every **processor** (hosting, model API, maps/geocoding, email/SMS, analytics) has a signed
      **Art. 28 data-processing agreement**.
- [ ] Every **third-country transfer** has a valid mechanism (adequacy / SCC / DPF).
- [ ] **Art. 32 security / TOMs** are in place and documented (encryption, access control, no
      personal data in logs/source).
- [ ] **Records of processing (Art. 30)** exist and are current.
- [ ] A **DPIA (Art. 35)** has been done or explicitly ruled out with reasoning (esp. for any AI
      feature; cross-check the [`eu-ai-act`](eu-ai-act.md) leaf).
- [ ] A **72-hour breach-notification** process and contact path are ready.
- [ ] A **DPO** is appointed if required, or its non-requirement is documented.
- [ ] For a static / brochure / coming-soon site (Section 6c): the **access-log posture** is a
      decision, not a default, the container log driver is size-capped, and an **imprint** exists
      rather than a footer line.
- [ ] Every **processing location** in the notice was taken from the live resource or the deploy
      manifest, not from an IaC default, and every named resource was confirmed to exist.
- [ ] Every **consent / opt-out / withdrawal control** has been traced into the backend and actually
      changes behaviour; every **stated retention period** has deleting code behind it.
- [ ] No **self-certification** sentences remain, and no fact is stated on more than one legal page
      except the controller identity, which is byte-identical in the imprint and the notice.
- [ ] Every **factual claim** in the notice is either mechanically verified (the log claim) or
      carries a `TODO` naming who must confirm it before launch (the AVV, register numbers).
- [ ] The claims still hold **after the last topology change** (a new TLS edge or CDN writes its
      own access log; see Section 6c).
- [ ] Where AI processes personal data, this check and the [`eu-ai-act`](eu-ai-act.md) Art. 50 disclosure are
      **consistent** and the human-review invariant is named.

## 10. Two checklists, two audiences (same split as the AI Act leaf)

Produce the same two write-ups the [`eu-ai-act`](eu-ai-act.md) leaf describes, so a combined compliance pack
reads consistently:

- **Stakeholder checklist** (business/product, non-legal): plain language, what the DSGVO is,
  why it applies to *this* product (name the actual data-touching features), the `- [ ]` items
  from Section 9, and open items.
- **Owner / sign-off checklist** (the decision-maker): shorter, decision-and-risk-framed. What
  needs an owner signature (approve the privacy notice wording, confirm processors are under AVV,
  confirm no un-mitigated third-country transfer, confirm counsel/DPO reviewed) and the actual
  exposure of doing nothing (regulatory fines up to the higher of EUR 20M or 4% of global annual
  turnover, plus reputational). Keep it to roughly a third the length of the stakeholder version.

Both carry the "not legal advice / confirm with counsel or the DPO before any external claim" line.

## 11. Writing style for anything this leaf produces

Same rule as the rest of the `compliance` skill: no em dashes. Use a colon before a list or
elaboration, parentheses or commas for an aside, a semicolon or two sentences for related clauses,
and a comma or its own sentence for a hard qualifier ("only", "unless", "not"). This applies to
every deliverable (checklists, privacy-notice copy, skill prose, artifacts), including this file.
