# UC San Diego engineering course-content contribution

Reviewed 2026-10-11. Scope is exactly **29 represented targets**: ECE 9, MAE 9, SE 5, BENG 3, NANO 2 and CENG 1 from `/tmp/ucsd-engineering-targets.json`. This is a bounded metadata contribution, not an engineering curriculum or whole-degree audit. Only the helper, manual manifest, focused tests and this note are changed.

## Official evidence and coverage

The already observed [official course index](https://catalog.ucsd.edu/front/courses.html) links the five actual chapters used here:

| Chapter | Official source | Fetch time, UTC | Approved observations |
| --- | --- | --- | ---: |
| ECE | [Electrical and Computer Engineering](https://catalog.ucsd.edu/courses/ECE.html) | 2026-10-11 09:09:25 | 9 |
| MAE | [Mechanical and Aerospace Engineering](https://catalog.ucsd.edu/courses/MAE.html) | 2026-10-11 09:09:27 | 6 |
| SE | [Structural Engineering](https://catalog.ucsd.edu/courses/SE.html) | 2026-10-11 09:09:28 | 5 |
| BENG | [Bioengineering](https://catalog.ucsd.edu/courses/BENG.html) | 2026-10-11 09:09:30 | 2 |
| NANO/CENG | [Chemical and Nano Engineering](https://catalog.ucsd.edu/courses/NANO.html) | 2026-10-11 09:09:31 | 3 |

All returned HTTP 200 through the ordinary robots-aware repository Fetcher and identify **General Catalog 2026–27**. CENG is a separate section within the observed NANO URL; no guessed CENG endpoint was used. That page prints the edition in an ordinary paragraph rather than the other chapters' disclaimer class; the helper guards the actual edition paragraph and full context. Private raw files are `/tmp/ucsd-engineering-{ECE,MAE,SE,BENG,NANO}.html`, with `/tmp/ucsd-engineering-source-index.json` provenance and ignored HTTP cache. Full-source and complete normalized block hashes are retained in the manifest. Committed summaries are original.

All **27 exact matching blocks** and chapter/section introductions were read in full. **25 observations are approved**: 16 applications, one systems, four mixed and four unclassified. Seventeen have a single reviewed subject category. Missing exact headings are **MAE 124 and BENG 191**. No substitute, cancellation or institution-wide absence is inferred.

Two current blocks remain **title/version holds**:

- MAE 118: the pool lists *Sustainable Energy Systems*, while the current chapter lists *Introduction to Energy and Environment*. Similar energy content is not sufficient to certify the older version. Current domain-science analysis remains candidate evidence only.
- MAE 190: the pool specifies *Digital Storytelling: Dynamic STEM Communication*, while the chapter gives generic *Topics in Mechanical and Aerospace Engineering*. The current generic block cannot certify the older topic. Its current candidate review is unclassified.

ECE 85's expanded subtitle and NanoEngineering capitalization align with the listed identities. SE 140B drops “Professional Issues and” from its title but explicitly retains professionalism, communication and ethics in the body, alongside the same Civil Structures II subject. This is documented as aligned content, not silently renamed unrelated work.

## Manual content boundaries

- **ECE 25, systems:** Boolean logic, sequential/combinational circuits and gate implementations establish computing hardware design. The classification comes from those methods, not the ECE prefix.
- **ECE 5, mixed foundations/applications:** embedded programming/debugging and physical circuits/transducers are both explicit taught components. No primary one is established.
- **ECE 85, mixed systems/human context:** information generation/transmission/processing and relationships to privacy/net neutrality are both stated topics.
- **ECE 148 and MAE 148, mixed applications/AI-ML:** physical autonomous-car development and AI vision/learning are explicit. Both descriptions support the same bounded mixed judgment despite different detail. Programming and ROS support the combined activity; no separate primary software-foundations course is inferred.
- **ECE 190/191/193H/196, unclassified:** engineering project/research processes are described, but their substantive technical subjects remain unspecified. Design percentage, documentation, honors status and preparation alternatives cannot determine whether a project teaches computing, applied electronics or another domain.
- The other **sixteen approved observations are applications**. Concrete aerospace, mechanical, civil, geotechnical, chemical, nanoscale and biomedical practice establishes the domain. ECE 115's physical mechatronic prototype is not automatically AI. SE 165 teaches monitoring of structural/mechanical systems using statistical tools; MATLAB and statistical modeling alone do not establish general mathematics, programming or AI content.
- Professional ethics, economics, safety, reporting and regulatory constraints support the explicit applied design work in NANO 120B, SE 140A/B, CENG 124A and MAE 155/156. The descriptions do not separately establish a coequal social-analysis objective. MAE 154's product development/business planning is applied professional practice.

## Credits, preparation and eligibility

Twenty-three approved observations print **four quarter units**. **BENG 196 prints 1–4** and **ECE 193H prints 4–8**; their scalar credits remain null, with exact ranges in notes. The ECE honors program's four-unit design requirement is not substituted for the course's 4–8 range. No range is averaged or totaled.

ECE 5 omits a formal prerequisite clause, so its current prerequisite value remains null. ECE 25 and 85 explicitly print **none**, which is retained distinctly. Every other approved prerequisite clause is preserved literally, including spaced `Prerequisites :`, numbered alternatives and compressed AND/OR wording.

- **BENG 193:** preserves two physiology-course alternative pairs, instructor consent and the exact GPA statement. The source describes **3.5 as requested as a requirement** under the School of Medicine agreement; neither optional-advice wording nor an independently verified hard-cutoff interpretation is invented. Coscheduling with BENG 294C does not import graduate eligibility.
- **BENG 196:** faculty/industry supervision, technical report, P/NP only and credit up to three times are retained. Department approval can allow four units to substitute for a technical elective; that is not automatic AI-degree applicability. Prerequisites include department consent, all lower-division requirements including general science, and laboratory experience.
- **ECE 190/191:** require completion of all breadth courses and one depth course, but the blocks do not enumerate those sets. ECE 190 additionally requires the department stamp and at least 50 percent design. **ECE 193H** requires departmental honors admission and a letter grade, with a possible two-quarter span and grade assigned on completion for both quarters. **ECE 196** permits credit two times and retains eight alternative introductory courses.
- **ECE 148/MAE 148:** explicit reciprocal cross-listing is recorded, with ECE's duplicate-credit exclusion. ECE requires instructor consent, MAE department approval; the helper preserves each source rather than inventing identical permission rules. No identity group is emitted.
- **MAE 155A/B:** exact prerequisites and instructor-consent alternatives are retained. The older pool says MAE majors only for 155B; the current block does not repeat that absolute restriction. This discrepancy remains in notes with the chapter's conditional enrollment-policy language, rather than being interpreted as a waiver.
- **MAE 156A/B:** open only to **MC 27 and MC 30–34**. MAE 156B requires 156A in the **immediately preceding quarter**, in addition to its other printed prerequisites. The exact list is narrower than a generic all-MAE-major restriction. MAE 156A's instructor-consent alternative is not silently extended to waive the separately printed major restriction.
- **MAE 154:** upper-division standing and instructor consent are both required. NANO 120A requires NANO 110 and initiates the sequence; NANO 120B requires 120A and completes it.
- **CENG 124A:** chemical engineering major admission and C– or better in CENG 113/122, **or instructor consent**, are retained. The consent alternative is not removed to manufacture an unconditional major prohibition.
- **SE courses:** exact prerequisite sets are retained. SE 165 coscheduling with SE 265 does not imply equivalence or graduate eligibility. Program/materials fee statements remain conditional, including fees in lab-heavy SE courses.

## Chapter-wide rules and exact scope

Each chapter's complete normalized introductory text is independently guarded, including introductions for Lower Division, Upper Division, Graduate and both CENG/NANO sections.

- **ECE:** planned offerings may change; actual schedules must be checked. The helper does not certify recurring availability.
- **MAE:** prerequisite/performance standards apply to students enrolled in MAE courses; prerequisite courses must be passed with **D or better**, and unmet prerequisites can lead to removal from rosters. The separate MAE own-major letter-grade requirement, minimum D in required courses and at-most-one-D graduation rule remain described as **MAE major rules**, not AI-degree graduation requirements. Where MAE priority/exclusive enrollment restrictions apply, other students need departmental approval; the chapter does not make every course absolutely major-only. Many upper-division offerings occur once annually.
- **SE:** undergraduate enrollees must meet prerequisite/performance standards and may be dropped if they do not. Most courses occur once annually, with possible fees for large laboratory components. No unstated minimum letter grade is invented.
- **BENG:** registration enforces prerequisites; transfer/AP satisfaction may need departmental preauthorization, rather than an automatic waiver. Scheduled quarters may change, and some materials fees apply.
- **CENG:** its own introductory section requires **C– or better** for prerequisite preparation and rejects D/F as adequate. This applies to CENG, **not automatically to NANO**, whose separate section introduction does not state that rule. Course-specific instructor consent remains visible without resolving an unstated policy-precedence question.

Printed term codes in BENG blocks are source schedule indications, qualified by the chapter's change warnings. No graduate section's course-specific conditions are imported into undergraduate observations.

## Output and checks

The helper exports metadata-only `parse_observations(html, subject=None)` and five URL-keyed `SOURCE_PARSERS`. It infers exactly one known chapter when no subject is given. The NANO parser handles both owned CENG and NANO prefixes; other parsers emit only entries belonging to their chapter. Changed edition, heading, complete body including nested/unwrapped text, chapter/section context, duplicate identifiers, missing-code appearance and password forms fail closed. Manual taxonomy reviews remain in the manifest; no requirements, identity mapping or audit certification is emitted.

**20 focused tests passed**, including all five exact cached chapter replays: 9 ECE, 6 MAE, 5 SE, 2 BENG and 3 NANO/CENG observations, plus four holds/missing dispositions. Tests cover full-body and context changes, combined-chapter routing, ranges, explicit none versus omission, title/missing holds, required versus conditional eligibility and manual classification boundaries. Primary integration and whole-release validation remain outside this contribution.
