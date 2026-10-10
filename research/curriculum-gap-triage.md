# Curriculum gap triage

Snapshot `1eb6d3aaf8360a63e24bd58480eb94399ef37f0c` · reviewed 2026-10-10 · **96 incomplete programs: 90 partial + 6 pending; 29 complete excluded**. No new source fetches, messages or program edits occurred. Categories and next actions are editorial judgments grounded in the committed audits and adapter notes. The [JSON companion](curriculum-gap-triage.json) retains exact audit pointers, note line excerpts, all recorded evidence URLs/locators, hashes, metadata missingness and classification provenance.

## Read the queue correctly

- Newest committed audit and explicit follow-up supersession control current gaps; historical access stops are retained only with their later resolution.
- Requirement scope is the represented award. Degrees include applicable university/college rules; minors/concentrations/additional majors do not claim the full host degree.
- Open subject ranges and advisor-approved alternatives can be complete when the rule is represented; a missing finite approved list is different.
- Course metadata, optional outcome taxonomy, first-offered dates and standalone credit-unit normalization are separate work. Standalone normalization entries misfiled in unresolved_requirements are retained as provenance under metadata, not silently deleted.
- General course prerequisites remain metadata unless the source imposes them as program admission/completion conditions. Next actions flag this distinction where existing audits combine them.
- Sources and adapter note excerpts are project evidence summaries, not newly fetched source copies. Exact failed URLs are null where the earlier review did not retain one. No guessed endpoint or inferred denial is added.
- This is an immutable snapshot work queue, not a live dashboard; later research requires a new snapshot or explicit revision.

| Requirement category | Programs |
| --- | ---: |
| `access_barrier` | 28 |
| `accessible_unreviewed` | 12 |
| `institutional_clarification` | 29 |
| `mixed` | 22 |
| `source_conflict` | 5 |

Categories describe requirement work, not quality or completion likelihood. `accessible_unreviewed` does not assert that an unattempted URL works. `access_barrier` includes precisely labeled transport failures and is never a blanket publisher-denial claim. Missing course metadata/outcomes/launch dates are shown separately in JSON and do not by themselves require a partial curriculum status.

## Priorities

- **Accessible policy extraction:** Requirement inventories already exist and the next work can proceed on public policy evidence without waiting for an institutional answer.
- **Narrow academic source conflicts:** Finish clarification of specific eligibility/count/threshold disagreements while retaining current partial status. These are bounded questions, not automatic completion promises.
- **Northeastern shared applicability research:** A sourced home-college policy matrix could benefit 23 variants, but every program’s applicability must be verified independently.
- **Access-dependent inventory:** Prioritize authoritative readable sources or explicit clarification; repeat network retries alone cannot substitute for policy evidence.
- **Versioned or broad mixed reconciliation:** MIT, Penn, Purdue and other mixed records combine source conflicts with substantial policy/pool extraction; split these tasks by source and cohort, not generic metadata enrichment.

Resolve narrow conflicts with public corrected policy or attributable institutional clarification; this deliverable does not authorize sending messages. No program becomes complete merely by removing a blocker label.

## Shared workstreams

### Northeastern: program-specific home-college applicability

23 concrete variants; 22 BS and 1 BSEnvE. Universal policies are mapped. Participating colleges verified only for Biology, Business and Design in the bounded applicability review. Never infer the remaining variants’ choices from those examples.

Next: Obtain program-and-cohort-specific home-college choices, change-of-home-college criteria, applicable progression/graduation/transfer rules and seminar/co-op mapping. Start with the Biology/Business/Design evidence matrix, then verify each concrete variant rather than generalizing their participating-college pairs.

Evidence: [northeastern-home-college-review.md](../research/northeastern-home-college-review.md), [northeastern-business-concentrations.md](../research/northeastern-business-concentrations.md), [northeastern-university-policies.json](../research/families/northeastern-university-policies.json)

- `northeastern-university-artificial-intelligence-and-behavioral-neuroscience-bs-boston-bs-degree`
- `northeastern-university-artificial-intelligence-and-biochemistry-bs-boston-bs-degree`
- `northeastern-university-artificial-intelligence-and-biology-bs-boston-bs-degree`
- `northeastern-university-artificial-intelligence-and-business-administration-bs-boston-bs-degree`
- `northeastern-university-artificial-intelligence-and-chemistry-bs-boston-bs-degree`
- `northeastern-university-artificial-intelligence-and-communication-studies-bs-boston-bs-degree`
- `northeastern-university-artificial-intelligence-and-criminal-justice-bs-boston-bs-degree`
- `northeastern-university-artificial-intelligence-and-design-bs-boston-bs-degree`
- `northeastern-university-artificial-intelligence-and-ecology-and-evolutionary-biology-bs-boston-bs-degree`
- `northeastern-university-artificial-intelligence-and-economics-bs-boston-bs-degree`
- `northeastern-university-artificial-intelligence-and-environmental-and-sustainability-sciences-bs-boston-bs-degree`
- `northeastern-university-artificial-intelligence-and-health-science-bs-boston-bs-degree`
- `northeastern-university-artificial-intelligence-and-international-affairs-bs-boston-bs-degree`
- `northeastern-university-artificial-intelligence-and-journalism-bs-boston-bs-degree`
- `northeastern-university-artificial-intelligence-and-linguistics-bs-boston-bs-degree`
- `northeastern-university-artificial-intelligence-and-mathematics-bs-boston-bs-degree`
- `northeastern-university-artificial-intelligence-and-philosophy-bs-boston-bs-degree`
- `northeastern-university-artificial-intelligence-and-physics-bs-boston-bs-degree`
- `northeastern-university-artificial-intelligence-and-psychology-bs-boston-bs-degree`
- `northeastern-university-artificial-intelligence-and-public-health-bs-boston-bs-degree`
- `northeastern-university-artificial-intelligence-and-sociology-bs-boston-bs-degree`
- `northeastern-university-artificial-intelligence-and-speech-language-pathology-and-audiology-bs-boston-bs-degree`
- `northeastern-university-environmental-engineering-and-artificial-intelligence-bsenve-boston-other-degree`

### Buffalo: unreadable catalog requirements across 8 degrees and 2 minors

Eight degree records belong to AI+X; AI Ethics and AI, Crime and Society minors do not. The five broad degree framework notes do not identify course pools or prove identical curricula. Shared host transport failure is not a per-URL 403; PPE has its own later HTTP 202 observation.

Next: Resolve permitted catalog evidence once, then separately map each degree’s local/domain and degree-wide rules and each minor’s local rules. Do not propagate one degree curriculum into the other nine records.

Evidence: [buffalo-ai-plus-x.md](../research/families/buffalo-ai-plus-x.md)

- `university-at-buffalo-suny-ai-and-geospatial-analytics-bs-degree`
- `university-at-buffalo-suny-ai-and-language-and-intercultural-competence-bs-degree`
- `university-at-buffalo-suny-ai-and-language-technology-bs-degree`
- `university-at-buffalo-suny-ai-and-logic-and-ontology-bs-degree`
- `university-at-buffalo-suny-ai-and-philosophy-politics-economics-bs-degree`
- `university-at-buffalo-suny-ai-and-policy-analysis-bs-degree`
- `university-at-buffalo-suny-ai-and-quantitative-economics-bs-degree`
- `university-at-buffalo-suny-ai-and-responsible-communication-bs-degree`
- `university-at-buffalo-suny-ai-ethics-minor-minor`
- `university-at-buffalo-suny-artificial-intelligence-crime-and-society-minor-minor`

## Concrete program queue

Every incomplete concrete ID appears below, including all grouped variants. Sources listed under each entry are the audit’s evidence set; JSON contains additional course/context sources. Old note paragraphs are not reintroduced as current blockers where the audit or a later follow-up supersedes them.

### Boston College — Artificial Intelligence Concentration

`boston-college-artificial-intelligence-concentration-concentration-concentration` · partial · `institutional_clarification` · scope: concentration

Published local structure is available; exact approved pools and local policy are not established by the reviewed pages.

Requirement gaps:

- Finite approved application and ethics course pools are not enumerated.
- Deep Learning and capstone course-code matches are unverified.
- Any additional concentration-specific completion/declaration policies require department clarification.

**Next action:** Obtain the department-approved application/ethics pools, exact Deep Learning and capstone codes, and local declaration/completion rules; do not infer eligibility from AI titles.

Separate metadata: 1 course records; missing descriptions/prerequisite statements/public sites/syllabi = 0/0/1/1. Missing fields do not establish no prerequisites, no outcomes or no launch. Full metadata annotations and first-offered evidence are in JSON.

Provenance: [program audit](../data/programs/boston-college-artificial-intelligence-concentration-concentration-concentration.json) · [adapter notes](../atlas/adapters/boston-college-artificial-intelligence-concentration-concentration-concentration/NOTES.md).

Official evidence (audit-wide):

- [Artificial Intelligence Concentration](https://www.bc.edu/bc-web/schools/morrissey/departments/computer-science/academics/programs.html) — Artificial Intelligence Concentration accordion; six-course structure, overlap and preparation paragraphs
- [Official Boston College Fall 2026 course feed](https://bcweb.bc.edu/aem/coursesfall.json) — CSCI3345, title Machine Learning, 2026FALL; course feed published in official departmental Courses page script

### Case Western Reserve University — Applied Artificial Intelligence

`case-applied-ai-minor` · partial · `source_conflict` · scope: minor

The minor option list conflicts with explicit course-enrollment restrictions; missing syllabi are not the requirement blocker.

Requirement gaps:

- The undergraduate minor lists BUAI 446 and SCMG 462/463, but their course catalogs restrict enrollment to named master’s programs. An applicable undergraduate exception or correction to the published option list has not been verified.

**Next action:** Resolve undergraduate eligibility for BUAI 446 and SCMG 462/463 against the master’s-only course restrictions using a published correction or attributable departmental exception. Keep the activity-status disagreement separate.

Separate metadata: 25 course records; missing descriptions/prerequisite statements/public sites/syllabi = 0/7/25/25. Missing fields do not establish no prerequisites, no outcomes or no launch. Full metadata annotations and first-offered evidence are in JSON.

Provenance: [program audit](../data/programs/case-applied-ai-minor.json) · [adapter notes](../atlas/adapters/case-applied-ai-minor/NOTES.md).

Official evidence (audit-wide):

- [Applied Artificial Intelligence, Minor](https://bulletin.case.edu/engineering/computer-data-sciences/applied-artificial-intelligence-minor/) — Overview, learning outcomes and complete program requirements table
- [University minor policies — case-policy](https://bulletin.case.edu/undergraduate-academics/academic-policies-procedures/) — Declaring a Major or Minor; Progress Toward Graduation; Study at Other Colleges and Transfer Credit
- [University minor policies — case-grades](https://bulletin.case.edu/undergraduate-academics/grades/) — Pass/No Pass section
- 16 additional audit sources, with exact URLs and locators, in this program’s JSON entry.

### Case Western Reserve University — Artificial Intelligence

`case-western-reserve-university-artificial-intelligence-ba-degree` · partial · `accessible_unreviewed` · scope: degree

Program and linked general-degree pages were inspected; remaining work is structured policy extraction, without a documented requirement-source denial.

Requirement gaps:

- Full general degree and Unified General Education Requirements inventory and policies remain to be mapped.
- Open department-wide electives and approved substitutions cannot be treated as a finite course list.

**Next action:** Map the linked bachelor-degree and Unified General Education policies and approved categories; preserve CSDS open-range and adviser-approved options as predicates rather than inventing a finite list. Audit BA and BS separately.

Separate metadata: 59 course records; missing descriptions/prerequisite statements/public sites/syllabi = 59/59/59/59. Missing fields do not establish no prerequisites, no outcomes or no launch. Full metadata annotations and first-offered evidence are in JSON.

Provenance: [program audit](../data/programs/case-western-reserve-university-artificial-intelligence-ba-degree.json) · [adapter notes](../atlas/adapters/case-western-reserve-university-artificial-intelligence-ba-degree/NOTES.md).

Official evidence (audit-wide):

- [Artificial Intelligence, BA — Case Western Reserve University Bulletin](https://bulletin.case.edu/engineering/computer-data-sciences/artificial-intelligence-ba/) — Program Requirements tab; sample plan excluded

### Case Western Reserve University — Artificial Intelligence

`case-western-reserve-university-artificial-intelligence-bs-degree` · partial · `accessible_unreviewed` · scope: degree

Program and linked general-degree pages were inspected; remaining work is structured policy extraction, without a documented requirement-source denial.

Requirement gaps:

- Full general degree and Unified General Education Requirements inventory and policies remain to be mapped.
- Open department-wide electives and approved substitutions cannot be treated as a finite course list.

**Next action:** Map the linked bachelor-degree and Unified General Education policies and approved categories; preserve CSDS open-range and adviser-approved options as predicates rather than inventing a finite list. Audit BA and BS separately.

Separate metadata: 72 course records; missing descriptions/prerequisite statements/public sites/syllabi = 72/72/72/72. Missing fields do not establish no prerequisites, no outcomes or no launch. Full metadata annotations and first-offered evidence are in JSON.

Provenance: [program audit](../data/programs/case-western-reserve-university-artificial-intelligence-bs-degree.json) · [adapter notes](../atlas/adapters/case-western-reserve-university-artificial-intelligence-bs-degree/NOTES.md).

Official evidence (audit-wide):

- [Artificial Intelligence, BS — Case Western Reserve University Bulletin](https://bulletin.case.edu/engineering/computer-data-sciences/artificial-intelligence-bs/) — Program Requirements tab; sample plan excluded

### Clemson University — Artificial Intelligence

`clemson-university-artificial-intelligence-minor-minor` · partial · `access_barrier` · scope: minor

The current requirement-source gap has a documented retrieval or access condition; this is not an assertion of program absence or a university-wide denial.

Requirement gaps:

- Catalog returned HTTP 403: required courses, choice rules, eligibility and completion policies remain unresolved.

Access evidence (`http_denial`): Linked catalog returned HTTP403; no bypass. Department description remains readable. Exact failed endpoint is not retained here; do not substitute the identity URL or guess one.

**Next action:** Use the recorded official requirement link only when normally readable, or obtain independently authoritative public requirements/institutional clarification. Preserve the recorded access condition; do not bypass it. Then map this represented award’s exact pools, choices and completion rules.

Separate metadata: 0 course records; missing descriptions/prerequisite statements/public sites/syllabi = 0/0/0/0. Missing fields do not establish no prerequisites, no outcomes or no launch. Full metadata annotations and first-offered evidence are in JSON.

Credit normalization is a separate metadata task, even where the original audit listed it under unresolved requirements.

Provenance: [program audit](../data/programs/clemson-university-artificial-intelligence-minor-minor.json) · [adapter notes](../atlas/adapters/clemson-university-artificial-intelligence-minor-minor/NOTES.md).

Official evidence (audit-wide):

- [Artificial Intelligence](https://www.clemson.edu/cecas/departments/computing/academics/undergrad/degrees/) — Named undergraduate program entry: Artificial Intelligence; award/type: minor / minor
- [School of Computing: Undergraduate Degrees](https://www.clemson.edu/cecas/departments/computing/academics/undergrad/degrees/) — Academic minors: Artificial Intelligence

### Columbia University — Artificial Intelligence

`columbia-ai-minor` · partial · `mixed` · scope: minor

The accessible minor section contains a count/row conflict, alongside unreviewed local policy links.

Requirement gaps:

- Duplicated IEOR E2000 foundation row and six-course count ambiguity
- Detailed CS Core mathematics substitution combinations
- General minor grade/overlap policies and broad elective overlap

**Next action:** Resolve duplicated IEOR E2000 and the six-course count; inspect linked CS Core math substitution combinations and college minor grade/overlap rules, including W4701 reuse. Do not infer Engineering/Barnard applicability.

Separate metadata: 34 course records; missing descriptions/prerequisite statements/public sites/syllabi = 34/34/34/34. Missing fields do not establish no prerequisites, no outcomes or no launch. Full metadata annotations and first-offered evidence are in JSON.

Provenance: [program audit](../data/programs/columbia-ai-minor.json) · [adapter notes](../atlas/adapters/columbia-ai-minor/NOTES.md).

Official evidence (audit-wide):

- [Computer Science — Columbia College bulletin](https://bulletin.columbia.edu/columbia-college/departments-instruction/computer-science/) — Minor in Artificial Intelligence: foundation table, AI/Ethics/Elective tables, math substitution and CS-program exclusion

### Cornell University — Artificial Intelligence

`cornell-university-artificial-intelligence-minor-minor` · partial · `access_barrier` · scope: minor

The current requirement-source gap has a documented retrieval or access condition; this is not an assertion of program absence or a university-wide denial.

Requirement gaps:

- Detailed catalog foundation distribution, approved course pools, forbidden overlaps and any further policies remain inaccessible behind a JavaScript robot challenge.

Access evidence (`challenge`): Detailed linked catalog returned a JavaScript robot challenge; department overview remains readable. Exact failed endpoint is not retained here; do not substitute the identity URL or guess one.

**Next action:** Use the recorded official requirement link only when normally readable, or obtain independently authoritative public requirements/institutional clarification. Preserve the recorded access condition; do not bypass it. Then map this represented award’s exact pools, choices and completion rules.

Separate metadata: 0 course records; missing descriptions/prerequisite statements/public sites/syllabi = 0/0/0/0. Missing fields do not establish no prerequisites, no outcomes or no launch. Full metadata annotations and first-offered evidence are in JSON.

Provenance: [program audit](../data/programs/cornell-university-artificial-intelligence-minor-minor.json) · [adapter notes](../atlas/adapters/cornell-university-artificial-intelligence-minor-minor/NOTES.md).

Official evidence (audit-wide):

- [Artificial Intelligence](https://bowers.cornell.edu/programs/artificial-intelligence-minor) — Program requirements, course tables, eligibility and policy text

### University of Delaware — Artificial Intelligence Engineering

`delaware-ai-engineering-major` · partial · `access_barrier` · scope: degree

The current requirement-source gap has a documented retrieval or access condition; this is not an assertion of program absence or a university-wide denial.

Requirement gaps:

- Current mandatory catalog curriculum and degree total (catalog HTTP403)
- Open AI/STEM/breadth/writing/multicultural pools
- Graduate-level alternative eligibility; physics laboratory metadata
- University/college GPA, residency, transfer, overlap and other graduation rules

Access evidence (`http_denial`): 2026–27 catalog plan returned HTTP403; department sample plan is not the mandatory degree inventory. Exact failed endpoint: <https://catalog.udel.edu/preview_program.php?catoid=97&poid=98013&returnto=35894>.

**Next action:** Use the recorded official requirement link only when normally readable, or obtain independently authoritative public requirements/institutional clarification. Preserve the recorded access condition; do not bypass it. Then map this represented award’s exact pools, choices and completion rules.

Separate metadata: 28 course records; missing descriptions/prerequisite statements/public sites/syllabi = 28/28/28/28. Missing fields do not establish no prerequisites, no outcomes or no launch. Full metadata annotations and first-offered evidence are in JSON.

Provenance: [program audit](../data/programs/delaware-ai-engineering-major.json) · [adapter notes](../atlas/adapters/delaware-ai-engineering-major/NOTES.md).

Official evidence (audit-wide):

- [Artificial Intelligence Engineering BS](https://www.ece.udel.edu/academics/undergraduate/artificial-intelligence-engineering-bs/) — BS heading; Sample Plan of Study; Career options

### Drexel University — Artificial Intelligence & Machine Learning

`drexel-ai-ml-bs` · partial · `mixed` · scope: degree

The plan has an unresolved coded sequence and policy applicability questions, while degree-wide rules remain unreviewed; no requirement-source barrier is established.

Requirement gaps:

- ECEC 455 missing title and incomplete elective-sequence row
- Open science, free-elective and MATH substitution inventories
- Current writing-intensive eligibility and transfer applicability
- University/school graduation, GPA, residency, transfer, co-op and overlap policies

**Next action:** Verify ECEC 455 and the incomplete sequence row in the current course catalog, then map school/university graduation, co-op, WI, transfer, residence and substitution rules. Preserve open science/MATH predicates where the policy is genuinely open-ended.

Separate metadata: 83 course records; missing descriptions/prerequisite statements/public sites/syllabi = 83/83/83/83. Missing fields do not establish no prerequisites, no outcomes or no launch. Full metadata annotations and first-offered evidence are in JSON.

Provenance: [program audit](../data/programs/drexel-ai-ml-bs.json) · [adapter notes](../atlas/adapters/drexel-ai-ml-bs/NOTES.md).

Official evidence (audit-wide):

- [Artificial Intelligence & Machine Learning](https://catalog.drexel.edu/undergraduate/computer-information-sciences/artificialintellicenceandmachinelearningbs/) — Degree Requirements table; footnotes; Writing-Intensive Course Requirements; co-op options; Program Level Outcomes

### Duke University — AI and Machine Learning

`duke-university-ai-and-machine-learning-concentration-concentration` · partial · `mixed` · scope: concentration

Conflicting public elective rules coexist with an explicitly student-only comprehensive list and remaining local policy review.

Requirement gaps:

- Two-of-three versus all-three COMPSCI elective wording conflicts within the current program page.
- Comprehensive elective list is in student-only Stellic and cannot be verified publicly.
- Conditional two-course, statistics and advanced substitutions are not exhaustively mapped; guide differs from current concentration on 270/270L, MATH222 and elective structure.

Access evidence (`student_only_system`): Source explicitly directs the comprehensive elective list to student-only Stellic; no login or attempted protected access is claimed. Exact failed endpoint is not retained here; do not substitute the identity URL or guess one.

**Next action:** Reconcile the COMPSCI elective wording and Fall-2026 cohort/substitution rules; obtain a public or attributable approved-elective list instead of accessing student-only Stellic. Finish only the represented concentration/minor’s completion policies.

Separate metadata: 87 course records; missing descriptions/prerequisite statements/public sites/syllabi = 87/87/87/87. Missing fields do not establish no prerequisites, no outcomes or no launch. Full metadata annotations and first-offered evidence are in JSON.

Provenance: [program audit](../data/programs/duke-university-ai-and-machine-learning-concentration-concentration.json) · [adapter notes](../atlas/adapters/duke-university-ai-and-machine-learning-concentration-concentration/NOTES.md).

Official evidence (audit-wide):

- [AI and Machine Learning](https://cs.duke.edu/undergraduate/degrees/BS/concentrations/ai-ml) — Current Academic Requirements introduction and accordions 1–8; Fall 2026 applicability and 15/34-unit context
- [CS Course Substitutions Guide](https://cs.duke.edu/undergraduate/courses/substitutions) — Opening substitution policies; CS Majors table COMPSCI201,210D,230,270L,330 and statistics; elective guide

### Duke University — Artificial Intelligence: Applications and Implications

`duke-university-artificial-intelligence-applications-and-implications-minor-minor` · partial · `mixed` · scope: minor

Conflicting public elective rules coexist with an explicitly student-only comprehensive list and remaining local policy review.

Requirement gaps:

- Resolve contradictory COMPSCI versus outside-COMPSCI wording in both elective requirements.
- The additional concentration approved-elective pool is not enumerated in this record; its comprehensive list is in student-only Stellic, and applicability of Fall 2026 versus earlier options requires clarification.
- Verify any minor-specific grade and transfer approval requirements before certifying complete local inventory.

Access evidence (`student_only_system`): Source explicitly directs the comprehensive elective list to student-only Stellic; no login or attempted protected access is claimed. Exact failed endpoint is not retained here; do not substitute the identity URL or guess one.

**Next action:** Reconcile the COMPSCI elective wording and Fall-2026 cohort/substitution rules; obtain a public or attributable approved-elective list instead of accessing student-only Stellic. Finish only the represented concentration/minor’s completion policies.

Separate metadata: 47 course records; missing descriptions/prerequisite statements/public sites/syllabi = 47/47/47/47. Missing fields do not establish no prerequisites, no outcomes or no launch. Full metadata annotations and first-offered evidence are in JSON.

Provenance: [program audit](../data/programs/duke-university-artificial-intelligence-applications-and-implications-minor-minor.json) · [adapter notes](../atlas/adapters/duke-university-artificial-intelligence-applications-and-implications-minor-minor/NOTES.md).

Official evidence (audit-wide):

- [CS minor: Artificial Intelligence — Applications and Implications](https://cs.duke.edu/undergraduate/degrees/minors) — AI minor accordion: prerequisite/core/minor elective/free elective sections; page-wide minor eligibility
- [CS BS concentration in AI and Machine Learning](https://cs.duke.edu/undergraduate/degrees/BS/concentrations/ai-ml) — Concentration Electives; Fall 2026 curriculum change; comprehensive electives in Stellic
- [Trinity majors, minors and certificates](https://trinity.duke.edu/undergraduate/academic-policies/change-major-minor-certificate) — Minor; Restrictions on Majors, Minors, Certificates; Changing/Adding/Deleting

### Duke University — Machine Learning & Artificial Intelligence

`duke-university-machine-learning-artificial-intelligence-minor-minor` · partial · `mixed` · scope: minor

Both sources are public and disagree; local completion-policy review also remains unfinished.

Requirement gaps:

- Reconcile narrower 2026–27 bulletin focus pool with expanded undated department list.
- Reconcile bulletin primary-major overlap restriction with department major(s) restriction.
- Verify minor-specific grading and applicable Pratt residency/transfer policies before certifying complete local requirements.

**Next action:** Reconcile the 2026–27 bulletin focus pool and primary-major overlap restriction with the undated ECE page; verify applicable minor grading and Pratt transfer/residence rules. Retain historical special-topic examples as historical.

Separate metadata: 25 course records; missing descriptions/prerequisite statements/public sites/syllabi = 25/25/25/25. Missing fields do not establish no prerequisites, no outcomes or no launch. Full metadata annotations and first-offered evidence are in JSON.

Provenance: [program audit](../data/programs/duke-university-machine-learning-artificial-intelligence-minor-minor.json) · [adapter notes](../atlas/adapters/duke-university-machine-learning-artificial-intelligence-minor-minor/NOTES.md).

Official evidence (audit-wide):

- [ECE minors: Machine Learning & Artificial Intelligence](https://ece.duke.edu/academics/undergrad/minors/) — #ml section: Fundamental Courses; Upper-Level Focus Courses; Note on Prerequisites; Notes on Course Counting
- [2026–27 ML/AI minor bulletin](https://undergraduate.bulletins.duke.edu/programs/U-ECE-MLAI/requirements-IkDU1) — Requirements: fundamental/focus courses; Important Notes; Prerequisites
- [Trinity majors, minors and certificates](https://trinity.duke.edu/undergraduate/academic-policies/change-major-minor-certificate) — Minor; Restrictions on Majors, Minors, Certificates; Changing/Adding/Deleting

### Florida International University — Artificial Intelligence

`florida-international-university-artificial-intelligence-minor-minor` · partial · `mixed` · scope: minor

Catalog and department choices/admission wording differ; general minor policies remain unreviewed.

Requirement gaps:

- Resolve CAI 4105 versus CAP 4612 disagreement between catalog and department.
- Institution-wide minor grade, overlap and residency rules remain unreviewed.

**Next action:** Resolve CAI 4105 versus CAP 4612 and the omitted IDC 2002 admission condition; map university minor grade, overlap and residence rules. Normalize credits separately only with evidence.

Separate metadata: 8 course records; missing descriptions/prerequisite statements/public sites/syllabi = 7/7/8/8. Missing fields do not establish no prerequisites, no outcomes or no launch. Full metadata annotations and first-offered evidence are in JSON.

Credit normalization is a separate metadata task, even where the original audit listed it under unresolved requirements.

Provenance: [program audit](../data/programs/florida-international-university-artificial-intelligence-minor-minor.json) · [adapter notes](../atlas/adapters/florida-international-university-artificial-intelligence-minor-minor/NOTES.md).

Official evidence (audit-wide):

- [Artificial Intelligence](https://cec.fiu.edu/news-events/news/2026/new-artificial-intelligence-ai-minor-prepares-fiu-engineering-computing-students-for-an-ai-driven-future.html) — Named undergraduate program entry: Artificial Intelligence; award/type: minor / minor
- [Minor in Artificial Intelligence](https://cec.fiu.edu/degrees-programs/undergraduate/minor-in-artificial-intelligence/) — Program at a Glance; four course areas; Prerequisites; admission request
- [XAI:MN Artificial Intelligence Minor — Requirements](https://catalog.fiu.edu/programs/XAI%3AMN/requirements-uz47h) — 2026–2027 catalog, rendered admission and core requirements; CNT 4153 course popup
- 1 additional audit sources, with exact URLs and locators, in this program’s JSON entry.

### Furman University — Artificial Intelligence

`furman-ai-bs` · pending · `access_barrier` · scope: degree

The current requirement-source gap has a documented retrieval or access condition; this is not an assertion of program absence or a university-wide denial.

Requirement gaps:

- No reviewed current course/choice inventory or completion-policy map for the whole represented degree and university/college rules.

Access evidence (`password_gate`): Linked AI major page was password protected; public directory proves identity only. Exact failed endpoint: <https://www.furman.edu/academics/majors-minors-programs/artificial-intelligence-major/>.

**Next action:** Use the recorded official requirement link only when normally readable, or obtain independently authoritative public requirements/institutional clarification. Preserve the recorded access condition; do not bypass it. Then map this represented award’s exact pools, choices and completion rules.

Separate metadata: 0 course records; missing descriptions/prerequisite statements/public sites/syllabi = 0/0/0/0. Missing fields do not establish no prerequisites, no outcomes or no launch. Full metadata annotations and first-offered evidence are in JSON.

Provenance: [program audit](../data/programs/furman-ai-bs.json) · [adapter notes](../atlas/adapters/furman-ai-bs/NOTES.md).

Official evidence (audit-wide):

- [Majors, Minors & Programs | Furman University](https://www.furman.edu/academics/majors-minors-programs/) — Artificial Intelligence Major card: Bachelor of Science; Undergraduate Majors

### Georgia Institute of Technology — Applications of Artificial Intelligence and Machine Learning

`georgia-institute-of-technology-applications-of-artificial-intelligence-and-machine-learning-minor-minor` · partial · `source_conflict` · scope: minor

Public catalog, program website and advising roster differ on named neuroscience options and participating schools.

Requirement gaps:

- Catalog science-track neuroscience entries disagree with the program website: the site lists NEUR/PSYC3803 for the cognitive-neuroscience topic and NEUR/PSYC4740 for Neuroethics. The catalog attaches the cognitive topic to a differently cross-listed Neuroethics row. Preserve catalog entries pending adviser clarification.
- The 2026–2027 overview lists four eligible colleges, but declaration is limited to participating schools. The linked advising roster omits Sciences and some engineering schools; exact current major eligibility requires confirmation with the home-major adviser.

**Next action:** Obtain the correct neuroscience course/topic cross-list mapping and current participating-major eligibility from an authoritative catalog correction or minor/home-major adviser clarification; retain both catalog and website observations.

Separate metadata: 87 course records; missing descriptions/prerequisite statements/public sites/syllabi = 87/87/87/87. Missing fields do not establish no prerequisites, no outcomes or no launch. Full metadata annotations and first-offered evidence are in JSON.

Provenance: [program audit](../data/programs/georgia-institute-of-technology-applications-of-artificial-intelligence-and-machine-learning-minor-minor.json) · [adapter notes](../atlas/adapters/georgia-institute-of-technology-applications-of-artificial-intelligence-and-machine-learning-minor-minor/NOTES.md).

Official evidence (audit-wide):

- [Applications of Artificial Intelligence and Machine Learning](https://catalog.gatech.edu/programs/minor-artificial-intelligence-machine-learning/) — Minor-specific requirement groups, course choices, eligibility and policy text
- [Undergraduate Minor Guidelines](https://catalog.gatech.edu/academics/minors/) — Program of Study; Other Guidelines
- [Minor overview](https://sites.gatech.edu/apps-ai-ml-minor/) — Academic year2026–2027 participating colleges
- 3 additional audit sources, with exact URLs and locators, in this program’s JSON entry.

### Georgia Institute of Technology — Computing and Artificial Intelligence

`georgia-institute-of-technology-computing-and-artificial-intelligence-minor-minor` · partial · `institutional_clarification` · scope: minor

The published exception is incomplete, rather than a missing unreviewed course pool or access failure.

Requirement gaps:

- Catalog ECE substitution eligibility contains incomplete wording (ECE2035 and either ECE2020 with no completed alternative). Confirm with advisor before applying the 15-hour exception.

**Next action:** Clarify the missing alternative after “ECE2035 and either ECE2020” before applying the ECE substitution or 15-hour exception.

Separate metadata: 15 course records; missing descriptions/prerequisite statements/public sites/syllabi = 11/15/15/15. Missing fields do not establish no prerequisites, no outcomes or no launch. Full metadata annotations and first-offered evidence are in JSON.

Provenance: [program audit](../data/programs/georgia-institute-of-technology-computing-and-artificial-intelligence-minor-minor.json) · [adapter notes](../atlas/adapters/georgia-institute-of-technology-computing-and-artificial-intelligence-minor-minor/NOTES.md).

Official evidence (audit-wide):

- [Computing and Artificial Intelligence](https://catalog.gatech.edu/programs/minor-computing-artificial-intelligence/) — Program requirements, course tables, eligibility and policy text
- [Artificial Intelligence thread](https://www.cc.gatech.edu/academics/threads/intelligence) — Named elective categories
- [Undergraduate Minor Guidelines](https://catalog.gatech.edu/academics/minors/) — Requirements for the Program of Study; Other Guidelines
- 1 additional audit sources, with exact URLs and locators, in this program’s JSON entry.

### Gonzaga University — AI in Engineering and Applied Science

`gonzaga-university-ai-in-engineering-and-applied-science-minor-minor` · pending · `access_barrier` · scope: minor

The current requirement-source gap has a documented retrieval or access condition; this is not an assertion of program absence or a university-wide denial.

Requirement gaps:

- No reviewed current course/choice inventory or completion-policy map for the local minor requirements and eligibility, not the whole parent degree.

Access evidence (`robots_preflight_http_denial`): Robots request returned HTTP403, before the minor page was requested; this is not a claim that the minor body returned403. Exact failed endpoint: <https://www.gonzaga.edu/robots.txt>.

**Next action:** Use the recorded official requirement link only when normally readable, or obtain independently authoritative public requirements/institutional clarification. Preserve the recorded access condition; do not bypass it. Then map this represented award’s exact pools, choices and completion rules.

Separate metadata: 0 course records; missing descriptions/prerequisite statements/public sites/syllabi = 0/0/0/0. Missing fields do not establish no prerequisites, no outcomes or no launch. Full metadata annotations and first-offered evidence are in JSON.

Provenance: [program audit](../data/programs/gonzaga-university-ai-in-engineering-and-applied-science-minor-minor.json) · [adapter notes](../atlas/adapters/gonzaga-university-ai-in-engineering-and-applied-science-minor-minor/NOTES.md).

Official evidence (audit-wide):

- [AI in Engineering and Applied Science](https://www.gonzaga.edu/school-of-engineering-applied-science/degrees-and-programs/electrical-computer-engineering/ece-tech-minors/ai-minor) — Named undergraduate program entry: AI in Engineering and Applied Science; award/type: minor / minor

### Lehigh University — Artificial Intelligence, Machine Learning and Data Science

`lehigh-university-artificial-intelligence-machine-learning-and-data-science-bs-degree` · partial · `mixed` · scope: degree

Source rows and sample plan disagree, and degree-wide policy extraction is incomplete.

Requirement gaps:

- Correct HSS course titles and sample-plan/free-elective discrepancy
- Open CSE 100+ inventory and advanced HSS distribution policies
- University and college graduation, GPA, residency, transfer and overlap rules

**Next action:** Reconcile HSS titles, 130 versus 130–131 total wording and eleven versus ten sample-plan free-elective credits; map university/college completion rules and advanced HSS distribution while preserving open CSE eligibility.

Separate metadata: 43 course records; missing descriptions/prerequisite statements/public sites/syllabi = 43/43/43/43. Missing fields do not establish no prerequisites, no outcomes or no launch. Full metadata annotations and first-offered evidence are in JSON.

Provenance: [program audit](../data/programs/lehigh-university-artificial-intelligence-machine-learning-and-data-science-bs-degree.json) · [adapter notes](../atlas/adapters/lehigh-university-artificial-intelligence-machine-learning-and-data-science-bs-degree/NOTES.md).

Official evidence (audit-wide):

- [Artificial Intelligence, Machine Learning and Data Science](https://engineering.lehigh.edu/cse/academics/undergraduate/bs-ai-ml-ds) — Named undergraduate program entry: Artificial Intelligence, Machine Learning and Data Science; award/type: BS / degree

### University of Miami — Artificial Intelligence Technologies for Business

`miami-ai-technologies-business-bsba` · partial · `accessible_unreviewed` · scope: degree

The actual curriculum table is mapped; degree-wide policy review remains unfinished with no documented requirement-source access barrier.

Requirement gaps:

- Full university and college general education, completion/residency, transfer and admission/progression policy audit remains unfinished.

**Next action:** Follow the linked university/college general education, admission/progression, transfer, residence and completion policies for this exact BA/BBA/BSBA pathway. Do not substitute Additional Major or sample-plan rules. Treat unit normalization separately.

Separate metadata: 54 course records; missing descriptions/prerequisite statements/public sites/syllabi = 54/54/54/54. Missing fields do not establish no prerequisites, no outcomes or no launch. Full metadata annotations and first-offered evidence are in JSON.

Credit normalization is a separate metadata task, even where the original audit listed it under unresolved requirements.

Provenance: [program audit](../data/programs/miami-ai-technologies-business-bsba.json) · [adapter notes](../atlas/adapters/miami-ai-technologies-business-bsba/NOTES.md).

Official evidence (audit-wide):

- [B.S.B.A. in Artificial Intelligence Technologies for Business](https://bulletin.miami.edu/undergraduate-academic-programs/business/business-technology/ai-tech-for-business-bsba/) — Curriculum table and footnotes; Learning Outcomes; Additional Major section read separately from degree requirements

### University of Miami — Data Science and Artificial Intelligence

`miami-data-science-ai-bs` · partial · `mixed` · scope: degree

Public rows disagree and policy review is incomplete; proposed-program activity wording is a separate identity field.

Requirement gaps:

- Full university and college general education, completion/residency, transfer and admission/progression policy audit remains unfinished.
- Resolve BS language row nine-credit amount against college three-credit minimum.

**Next action:** Resolve the BS language row’s nine credits against the college three-credit minimum and 121 versus 120 requirement/sample-plan context; complete the linked university/college policies without importing the BA’s non-STEM minor condition.

Separate metadata: 57 course records; missing descriptions/prerequisite statements/public sites/syllabi = 57/57/57/57. Missing fields do not establish no prerequisites, no outcomes or no launch. Full metadata annotations and first-offered evidence are in JSON.

Credit normalization is a separate metadata task, even where the original audit listed it under unresolved requirements.

Provenance: [program audit](../data/programs/miami-data-science-ai-bs.json) · [adapter notes](../atlas/adapters/miami-data-science-ai-bs/NOTES.md).

Official evidence (audit-wide):

- [B.S. in Data Science and Artificial Intelligence](https://bulletin.miami.edu/undergraduate-academic-programs/arts-sciences/computer-science/data-science-and-ai-bs/) — Curriculum table and footnotes; Learning Outcomes; Additional Major section read separately from degree requirements
- [College of Arts and Sciences requirements](https://bulletin.miami.edu/undergraduate-academic-programs/arts-sciences/) — Requirements for Graduation; BA/BS additional requirements; majors/minors; electives; Credit Only and Transfer Credit Hours

### Massachusetts Institute of Technology — Artificial Intelligence and Decision Making

`mit-ai-decision-making-bs` · partial · `mixed` · scope: degree

The public version and chart conflict; additional institute policy branches remain unreviewed. Restricted individual degree audits are not needed to label the public sources blocked.

Requirement gaps:

- Reconcile the unversioned catalog chart with mandatory 6-4_2025 departmental rules for Fall 2025+ entrants, explicitly current to Fall 2026. The public version adds center, application, advanced and graduate choices not yet fully represented in its own coherent inventory.
- Reconcile 6.4300 credit discrepancy: chart 15 versus unversioned general CI-M list 12; versioned annotation uses a 4-0-11 breakdown. No publication-date/source-precedence assumption resolves the conflict.
- Review chosen HASS-field concentration details and linked CI-H/HW designation/placement exceptions; generic institute criteria and deadlines are mapped, not every field-specific plan.
- Review first-year/flexible P/NR, transfer/AP/advanced-standing credit and repeat rules, degree-specific exceptions and applicable cohort-transition policy. Current public institute attendance, standing, completion and petition rules are mapped.

**Next action:** Build a coherent Fall-2025+ entrant inventory from the public 6-4_2025/Fall-2026 version, reconcile its center/application/advanced choices and 6.4300 amounts with the unversioned chart, then finish HASS-field/CI-H-HW, P/NR, prior-credit/repeat and cohort-transition policies.

Separate metadata: 84 course records; missing descriptions/prerequisite statements/public sites/syllabi = 84/83/84/84. Missing fields do not establish no prerequisites, no outcomes or no launch. Full metadata annotations and first-offered evidence are in JSON.

Provenance: [program audit](../data/programs/mit-ai-decision-making-bs.json) · [adapter notes](../atlas/adapters/mit-ai-decision-making-bs/NOTES.md).

Official evidence (audit-wide):

- [Artificial Intelligence and Decision Making (Course 6-4)](https://catalog.mit.edu/degree-charts/artifical-intelligence-decision-making-course-6-4/) — Degree chart requirements, options, unit accounting and footnotes
- [EECS Subject Groupings — Communication-Intensive in the Major Subjects](https://catalog.mit.edu/degree-charts/eecs-subject-groupings/) — cimtextcontainer; linked general CI-M subject table
- [General Institute Requirements](https://catalog.mit.edu/mit/undergraduate-education/general-institute-requirements/) — GIR overview and science/communication/HASS/REST/laboratory/physical education tabs
- 5 additional audit sources, with exact URLs and locators, in this program’s JSON entry.

### North Carolina State University — Artificial Intelligence

`ncsu-cs-ai-concentration` · partial · `mixed` · scope: concentration

Accessible table footnotes conflict and concentration completion policies remain unreviewed.

Requirement gaps:

- Resolve C versus C-minus footnote discrepancy for the CSC AI elective block.
- Review concentration declaration/eligibility, elective-credit reuse, substitutions, residency and any additional local completion policies.
- Verify concentration DSA course-code spellings against official course entries before treating them as DSC aliases.

**Next action:** Resolve the C versus C-minus footnote for CSC AI electives and verify DSA codes against actual course entries; audit concentration-local declaration, reuse, substitutions and residence without claiming the whole BS.

Separate metadata: 40 course records; missing descriptions/prerequisite statements/public sites/syllabi = 40/40/40/40. Missing fields do not establish no prerequisites, no outcomes or no launch. Full metadata annotations and first-offered evidence are in JSON.

Provenance: [program audit](../data/programs/ncsu-cs-ai-concentration.json) · [adapter notes](../atlas/adapters/ncsu-cs-ai-concentration/NOTES.md).

Official evidence (audit-wide):

- [Computer Science (BS): Artificial Intelligence Concentration](https://catalog.ncsu.edu/undergraduate/engineering/computer-science/artificial-intelligence-concentration/) — Concentration rows under Plan Requirements; AI and CSC AI restricted tables; numbered grade footnotes; semester sequence GPA note

### New Jersey Institute of Technology — Business with AI

`new-jersey-institute-of-technology-business-with-ai-bs-degree` · partial · `accessible_unreviewed` · scope: degree

Requirement directories are accessible but incompletely structured. Robots-disallowed course-search endpoints affect metadata, not this requirement classification.

Requirement gaps:

- Complete linked GER approved pools and course/lab combinations
- General-education overlap and substitution rules
- School and university graduation, grade, residency and transfer rules

Robots-disallowed course-search endpoints concern course metadata; linked GER directories are accessible.

**Next action:** Extract the already accessible GER 200/300, natural-science/lab and capstone directories with wildcard/Rutgers eligibility and overlap rules; finish school/university grade, transfer and residence policies.

Separate metadata: 32 course records; missing descriptions/prerequisite statements/public sites/syllabi = 32/32/32/32. Missing fields do not establish no prerequisites, no outcomes or no launch. Full metadata annotations and first-offered evidence are in JSON.

Provenance: [program audit](../data/programs/new-jersey-institute-of-technology-business-with-ai-bs-degree.json) · [adapter notes](../atlas/adapters/new-jersey-institute-of-technology-business-with-ai-bs-degree/NOTES.md).

Official evidence (audit-wide):

- [Bachelors of Science in Business with AI](https://management.njit.edu/bachelors-science-business-ai) — Opening paragraph explicitly identifies Bachelor of Science in Business with AI; What is Business with AI section.
- [Business with AI](https://catalog.njit.edu/undergraduate/management/management/business-with-ai-bs/) — Business with AI heading and undergraduate plan of study; explicit BS award is established by the separate school overview source.
- [History and Humanities GER 200 level](https://catalog.njit.edu/undergraduate/academic-policies-procedures/general-education-requirements/ger-200-level/) — Approved GER course list
- 3 additional audit sources, with exact URLs and locators, in this program’s JSON entry.

### Northeastern University — Artificial Intelligence and Behavioral Neuroscience, BS (Boston)

`northeastern-university-artificial-intelligence-and-behavioral-neuroscience-bs-boston-bs-degree` · partial · `institutional_clarification` · scope: degree

Current audits narrow the remaining gap to home-college applicability. Published hosting/participating-college context does not establish allowed or mandatory home-college designations.

Requirement gaps:

- Permitted home-college options and their additional progression/graduation rules have not been exhaustively verified for this combined degree. Catalog hosting context is not assumed to fix the student’s designated home college.

Latest audit and university-policy follow-up supersede earlier unexpanded-university/open-range notes. Open predicates and individual student clearance are not finite missing course pools. Business’s 14 concentrations are now mapped; no stale concentration gap is carried forward.

**Next action:** Obtain program-and-cohort-specific home-college choices, change-of-home-college criteria, applicable progression/graduation/transfer rules and seminar/co-op mapping. Start with the Biology/Business/Design evidence matrix, then verify each concrete variant rather than generalizing their participating-college pairs.

Separate metadata: 71 course records; missing descriptions/prerequisite statements/public sites/syllabi = 66/66/71/71. Missing fields do not establish no prerequisites, no outcomes or no launch. Full metadata annotations and first-offered evidence are in JSON.

Provenance: [program audit](../data/programs/northeastern-university-artificial-intelligence-and-behavioral-neuroscience-bs-boston-bs-degree.json) · [adapter notes](../atlas/adapters/northeastern-university-artificial-intelligence-and-behavioral-neuroscience-bs-boston-bs-degree/NOTES.md).

Official evidence (audit-wide):

- [Artificial Intelligence and Behavioral Neuroscience, BS (Boston)](https://catalog.northeastern.edu/undergraduate/computer-information-science/computer-information-science-combined-majors/artificial-intelligence-behavioral-neuroscience-bs-bos/) — Program Requirements tab, including footnotes; Program overview
- [Data Science (DS)](https://catalog.northeastern.edu/course-descriptions/ds/) — Named course blocks: DS 3500, DS 3000, DS 4200, DS 4300, DS 4400
- [Universitywide Requirements](https://catalog.northeastern.edu/undergraduate/university-academics/university-wide-requirements/) — textcontainer; named completion/eligibility sections only
- 5 additional audit sources, with exact URLs and locators, in this program’s JSON entry.

### Northeastern University — Artificial Intelligence and Biochemistry, BS (Boston)

`northeastern-university-artificial-intelligence-and-biochemistry-bs-boston-bs-degree` · partial · `institutional_clarification` · scope: degree

Current audits narrow the remaining gap to home-college applicability. Published hosting/participating-college context does not establish allowed or mandatory home-college designations.

Requirement gaps:

- Permitted home-college options and their additional progression/graduation rules have not been exhaustively verified for this combined degree. Catalog hosting context is not assumed to fix the student’s designated home college.

Latest audit and university-policy follow-up supersede earlier unexpanded-university/open-range notes. Open predicates and individual student clearance are not finite missing course pools. Business’s 14 concentrations are now mapped; no stale concentration gap is carried forward.

**Next action:** Obtain program-and-cohort-specific home-college choices, change-of-home-college criteria, applicable progression/graduation/transfer rules and seminar/co-op mapping. Start with the Biology/Business/Design evidence matrix, then verify each concrete variant rather than generalizing their participating-college pairs.

Separate metadata: 52 course records; missing descriptions/prerequisite statements/public sites/syllabi = 47/47/52/52. Missing fields do not establish no prerequisites, no outcomes or no launch. Full metadata annotations and first-offered evidence are in JSON.

Provenance: [program audit](../data/programs/northeastern-university-artificial-intelligence-and-biochemistry-bs-boston-bs-degree.json) · [adapter notes](../atlas/adapters/northeastern-university-artificial-intelligence-and-biochemistry-bs-boston-bs-degree/NOTES.md).

Official evidence (audit-wide):

- [Artificial Intelligence and Biochemistry, BS (Boston)](https://catalog.northeastern.edu/undergraduate/computer-information-science/computer-information-science-combined-majors/artificial-intelligence-biochemistry-bs-bos/) — Program Requirements tab, including footnotes; Program overview
- [Data Science (DS)](https://catalog.northeastern.edu/course-descriptions/ds/) — Named course blocks: DS 3500, DS 3000, DS 4200, DS 4300, DS 4400
- [Universitywide Requirements](https://catalog.northeastern.edu/undergraduate/university-academics/university-wide-requirements/) — textcontainer; named completion/eligibility sections only
- 5 additional audit sources, with exact URLs and locators, in this program’s JSON entry.

### Northeastern University — Artificial Intelligence and Biology, BS (Boston)

`northeastern-university-artificial-intelligence-and-biology-bs-boston-bs-degree` · partial · `institutional_clarification` · scope: degree

Current audits narrow the remaining gap to home-college applicability. Published hosting/participating-college context does not establish allowed or mandatory home-college designations.

Requirement gaps:

- Permitted home-college options and their additional progression/graduation rules have not been exhaustively verified for this combined degree. Catalog hosting context is not assumed to fix the student’s designated home college.

Latest audit and university-policy follow-up supersede earlier unexpanded-university/open-range notes. Open predicates and individual student clearance are not finite missing course pools. Business’s 14 concentrations are now mapped; no stale concentration gap is carried forward.

**Next action:** Obtain program-and-cohort-specific home-college choices, change-of-home-college criteria, applicable progression/graduation/transfer rules and seminar/co-op mapping. Start with the Biology/Business/Design evidence matrix, then verify each concrete variant rather than generalizing their participating-college pairs.

Separate metadata: 72 course records; missing descriptions/prerequisite statements/public sites/syllabi = 72/72/72/72. Missing fields do not establish no prerequisites, no outcomes or no launch. Full metadata annotations and first-offered evidence are in JSON.

Provenance: [program audit](../data/programs/northeastern-university-artificial-intelligence-and-biology-bs-boston-bs-degree.json) · [adapter notes](../atlas/adapters/northeastern-university-artificial-intelligence-and-biology-bs-boston-bs-degree/NOTES.md).

Official evidence (audit-wide):

- [Artificial Intelligence and Biology, BS (Boston)](https://catalog.northeastern.edu/undergraduate/computer-information-science/computer-information-science-combined-majors/artificial-intelligence-biology-bs-bos/) — Program Requirements tab; Program overview
- [Universitywide Requirements](https://catalog.northeastern.edu/undergraduate/university-academics/university-wide-requirements/) — textcontainer; named completion/eligibility sections only
- [General Education Requirements](https://catalog.northeastern.edu/undergraduate/university-academics/general-education-requirements/) — nupathtextcontainer; named completion/eligibility sections only
- 4 additional audit sources, with exact URLs and locators, in this program’s JSON entry.

### Northeastern University — Artificial Intelligence and Business Administration, BS (Boston)

`northeastern-university-artificial-intelligence-and-business-administration-bs-boston-bs-degree` · partial · `institutional_clarification` · scope: degree

Current audits narrow the remaining gap to home-college applicability. Published hosting/participating-college context does not establish allowed or mandatory home-college designations.

Requirement gaps:

- Permitted home-college options and their additional progression/graduation rules have not been exhaustively verified for this combined degree. Catalog hosting context is not assumed to fix the student’s designated home college.

Latest audit and university-policy follow-up supersede earlier unexpanded-university/open-range notes. Open predicates and individual student clearance are not finite missing course pools. Business’s 14 concentrations are now mapped; no stale concentration gap is carried forward.

**Next action:** Obtain program-and-cohort-specific home-college choices, change-of-home-college criteria, applicable progression/graduation/transfer rules and seminar/co-op mapping. Start with the Biology/Business/Design evidence matrix, then verify each concrete variant rather than generalizing their participating-college pairs.

Separate metadata: 179 course records; missing descriptions/prerequisite statements/public sites/syllabi = 179/179/179/179. Missing fields do not establish no prerequisites, no outcomes or no launch. Full metadata annotations and first-offered evidence are in JSON.

Provenance: [program audit](../data/programs/northeastern-university-artificial-intelligence-and-business-administration-bs-boston-bs-degree.json) · [adapter notes](../atlas/adapters/northeastern-university-artificial-intelligence-and-business-administration-bs-boston-bs-degree/NOTES.md).

Official evidence (audit-wide):

- [Artificial Intelligence and Business Administration, BS (Boston)](https://catalog.northeastern.edu/undergraduate/computer-information-science/computer-information-science-combined-majors/artificial-intelligence-business-admnistration-bs-bos/) — Program Requirements tab; Program overview
- [Universitywide Requirements](https://catalog.northeastern.edu/undergraduate/university-academics/university-wide-requirements/) — textcontainer; named completion/eligibility sections only
- [General Education Requirements](https://catalog.northeastern.edu/undergraduate/university-academics/general-education-requirements/) — nupathtextcontainer; named completion/eligibility sections only
- 18 additional audit sources, with exact URLs and locators, in this program’s JSON entry.

### Northeastern University — Artificial Intelligence and Chemistry, BS (Boston)

`northeastern-university-artificial-intelligence-and-chemistry-bs-boston-bs-degree` · partial · `institutional_clarification` · scope: degree

Current audits narrow the remaining gap to home-college applicability. Published hosting/participating-college context does not establish allowed or mandatory home-college designations.

Requirement gaps:

- Permitted home-college options and their additional progression/graduation rules have not been exhaustively verified for this combined degree. Catalog hosting context is not assumed to fix the student’s designated home college.

Latest audit and university-policy follow-up supersede earlier unexpanded-university/open-range notes. Open predicates and individual student clearance are not finite missing course pools. Business’s 14 concentrations are now mapped; no stale concentration gap is carried forward.

**Next action:** Obtain program-and-cohort-specific home-college choices, change-of-home-college criteria, applicable progression/graduation/transfer rules and seminar/co-op mapping. Start with the Biology/Business/Design evidence matrix, then verify each concrete variant rather than generalizing their participating-college pairs.

Separate metadata: 51 course records; missing descriptions/prerequisite statements/public sites/syllabi = 46/46/51/51. Missing fields do not establish no prerequisites, no outcomes or no launch. Full metadata annotations and first-offered evidence are in JSON.

Provenance: [program audit](../data/programs/northeastern-university-artificial-intelligence-and-chemistry-bs-boston-bs-degree.json) · [adapter notes](../atlas/adapters/northeastern-university-artificial-intelligence-and-chemistry-bs-boston-bs-degree/NOTES.md).

Official evidence (audit-wide):

- [Artificial Intelligence and Chemistry, BS (Boston)](https://catalog.northeastern.edu/undergraduate/computer-information-science/computer-information-science-combined-majors/artificial-intelligence-chemistry-bs-bos/) — Program Requirements tab, including footnotes; Program overview
- [Data Science (DS)](https://catalog.northeastern.edu/course-descriptions/ds/) — Named course blocks: DS 3500, DS 3000, DS 4200, DS 4300, DS 4400
- [Universitywide Requirements](https://catalog.northeastern.edu/undergraduate/university-academics/university-wide-requirements/) — textcontainer; named completion/eligibility sections only
- 5 additional audit sources, with exact URLs and locators, in this program’s JSON entry.

### Northeastern University — Artificial Intelligence and Communication Studies, BS (Boston)

`northeastern-university-artificial-intelligence-and-communication-studies-bs-boston-bs-degree` · partial · `institutional_clarification` · scope: degree

Current audits narrow the remaining gap to home-college applicability. Published hosting/participating-college context does not establish allowed or mandatory home-college designations.

Requirement gaps:

- Permitted home-college options and their additional progression/graduation rules have not been exhaustively verified for this combined degree. Catalog hosting context is not assumed to fix the student’s designated home college.

Latest audit and university-policy follow-up supersede earlier unexpanded-university/open-range notes. Open predicates and individual student clearance are not finite missing course pools. Business’s 14 concentrations are now mapped; no stale concentration gap is carried forward.

**Next action:** Obtain program-and-cohort-specific home-college choices, change-of-home-college criteria, applicable progression/graduation/transfer rules and seminar/co-op mapping. Start with the Biology/Business/Design evidence matrix, then verify each concrete variant rather than generalizing their participating-college pairs.

Separate metadata: 77 course records; missing descriptions/prerequisite statements/public sites/syllabi = 67/56/77/77. Missing fields do not establish no prerequisites, no outcomes or no launch. Full metadata annotations and first-offered evidence are in JSON.

Provenance: [program audit](../data/programs/northeastern-university-artificial-intelligence-and-communication-studies-bs-boston-bs-degree.json) · [adapter notes](../atlas/adapters/northeastern-university-artificial-intelligence-and-communication-studies-bs-boston-bs-degree/NOTES.md).

Official evidence (audit-wide):

- [Artificial Intelligence and Communication Studies, BS (Boston)](https://catalog.northeastern.edu/undergraduate/computer-information-science/computer-information-science-combined-majors/artificial-intelligence-communication-studies-bs-bos/) — Program Requirements tab, all local tables and footnotes; Program overview
- [Data Science (DS)](https://catalog.northeastern.edu/course-descriptions/ds/) — Named course blocks: DS 3500, DS 3000, DS 4200, DS 4300, DS 4400, DS 4420, DS 4440, DS 1300
- [Communication Studies (COMM)](https://catalog.northeastern.edu/course-descriptions/comm/) — Named course blocks: COMM 1101, COMM 1112, COMM 2301, COMM 1210, COMM 1225, COMM 1231, COMM 1255, COMM 1131, COMM 2303, COMM 2304, COMM 2501, COMM 2551, COMM 3200, COMM 3201, COMM 3230, COMM 3304, COMM 3320, COMM 3415, COMM 3500, COMM 3501, COMM 3530, COMM 3532, COMM 4535, COMM 4605, COMM 4631, COMM 2625, COMM 2941, COMM 4608, COMM 4625, COMM 4901, COMM 1000, COMM 3409
- 6 additional audit sources, with exact URLs and locators, in this program’s JSON entry.

### Northeastern University — Artificial Intelligence and Criminal Justice, BS (Boston)

`northeastern-university-artificial-intelligence-and-criminal-justice-bs-boston-bs-degree` · partial · `institutional_clarification` · scope: degree

Current audits narrow the remaining gap to home-college applicability. Published hosting/participating-college context does not establish allowed or mandatory home-college designations.

Requirement gaps:

- Permitted home-college options and their additional progression/graduation rules have not been exhaustively verified for this combined degree. Catalog hosting context is not assumed to fix the student’s designated home college.

Latest audit and university-policy follow-up supersede earlier unexpanded-university/open-range notes. Open predicates and individual student clearance are not finite missing course pools. Business’s 14 concentrations are now mapped; no stale concentration gap is carried forward.

**Next action:** Obtain program-and-cohort-specific home-college choices, change-of-home-college criteria, applicable progression/graduation/transfer rules and seminar/co-op mapping. Start with the Biology/Business/Design evidence matrix, then verify each concrete variant rather than generalizing their participating-college pairs.

Separate metadata: 67 course records; missing descriptions/prerequisite statements/public sites/syllabi = 59/61/67/67. Missing fields do not establish no prerequisites, no outcomes or no launch. Full metadata annotations and first-offered evidence are in JSON.

Provenance: [program audit](../data/programs/northeastern-university-artificial-intelligence-and-criminal-justice-bs-boston-bs-degree.json) · [adapter notes](../atlas/adapters/northeastern-university-artificial-intelligence-and-criminal-justice-bs-boston-bs-degree/NOTES.md).

Official evidence (audit-wide):

- [Artificial Intelligence and Criminal Justice, BS (Boston)](https://catalog.northeastern.edu/undergraduate/computer-information-science/computer-information-science-combined-majors/artificial-intelligence-criminal-justice-bs-bos/) — Program Requirements tab, all local tables and footnotes; Program overview
- [Data Science (DS)](https://catalog.northeastern.edu/course-descriptions/ds/) — Named course blocks: DS 3500, DS 3000, DS 4200, DS 4300, DS 4400, DS 1300
- [Criminal Justice (CRIM)](https://catalog.northeastern.edu/course-descriptions/crim/) — Named course blocks: CRIM 1000, CRIM 1100, CRIM 1110, CRIM 1120, CRIM 1300, CRIM 1400, CRIM 1500, CRIM 1700, CRIM 2310, CRIM 2320, CRIM 2330, CRIM 2350, CRIM 2370, CRIM 2380, CRIM 3010, CRIM 3030, CRIM 3040, CRIM 3050, CRIM 3060, CRIM 3070, CRIM 3100, CRIM 3540, CRIM 3110, CRIM 3120, CRIM 3600, CRIM 4949, CRIM 3700, CRIM 4040
- 6 additional audit sources, with exact URLs and locators, in this program’s JSON entry.

### Northeastern University — Artificial Intelligence and Design, BS (Boston)

`northeastern-university-artificial-intelligence-and-design-bs-boston-bs-degree` · partial · `institutional_clarification` · scope: degree

Current audits narrow the remaining gap to home-college applicability. Published hosting/participating-college context does not establish allowed or mandatory home-college designations.

Requirement gaps:

- Permitted home-college options and their additional progression/graduation rules have not been exhaustively verified for this combined degree. Catalog hosting context is not assumed to fix the student’s designated home college.

Latest audit and university-policy follow-up supersede earlier unexpanded-university/open-range notes. Open predicates and individual student clearance are not finite missing course pools. Business’s 14 concentrations are now mapped; no stale concentration gap is carried forward.

**Next action:** Obtain program-and-cohort-specific home-college choices, change-of-home-college criteria, applicable progression/graduation/transfer rules and seminar/co-op mapping. Start with the Biology/Business/Design evidence matrix, then verify each concrete variant rather than generalizing their participating-college pairs.

Separate metadata: 62 course records; missing descriptions/prerequisite statements/public sites/syllabi = 57/57/62/62. Missing fields do not establish no prerequisites, no outcomes or no launch. Full metadata annotations and first-offered evidence are in JSON.

Provenance: [program audit](../data/programs/northeastern-university-artificial-intelligence-and-design-bs-boston-bs-degree.json) · [adapter notes](../atlas/adapters/northeastern-university-artificial-intelligence-and-design-bs-boston-bs-degree/NOTES.md).

Official evidence (audit-wide):

- [Artificial Intelligence and Design, BS (Boston)](https://catalog.northeastern.edu/undergraduate/computer-information-science/computer-information-science-combined-majors/artificial-intelligence-design-bs-bos/) — Program Requirements tab, including footnotes; Program overview
- [Data Science (DS)](https://catalog.northeastern.edu/course-descriptions/ds/) — Named course blocks: DS 3500, DS 3000, DS 4300, DS 4400, DS 4200, DS 1300
- [Universitywide Requirements](https://catalog.northeastern.edu/undergraduate/university-academics/university-wide-requirements/) — textcontainer; named completion/eligibility sections only
- 5 additional audit sources, with exact URLs and locators, in this program’s JSON entry.

### Northeastern University — Artificial Intelligence and Ecology and Evolutionary Biology, BS (Boston)

`northeastern-university-artificial-intelligence-and-ecology-and-evolutionary-biology-bs-boston-bs-degree` · partial · `institutional_clarification` · scope: degree

Current audits narrow the remaining gap to home-college applicability. Published hosting/participating-college context does not establish allowed or mandatory home-college designations.

Requirement gaps:

- Permitted home-college options and their additional progression/graduation rules have not been exhaustively verified for this combined degree. Catalog hosting context is not assumed to fix the student’s designated home college.

Latest audit and university-policy follow-up supersede earlier unexpanded-university/open-range notes. Open predicates and individual student clearance are not finite missing course pools. Business’s 14 concentrations are now mapped; no stale concentration gap is carried forward.

**Next action:** Obtain program-and-cohort-specific home-college choices, change-of-home-college criteria, applicable progression/graduation/transfer rules and seminar/co-op mapping. Start with the Biology/Business/Design evidence matrix, then verify each concrete variant rather than generalizing their participating-college pairs.

Separate metadata: 71 course records; missing descriptions/prerequisite statements/public sites/syllabi = 65/65/71/71. Missing fields do not establish no prerequisites, no outcomes or no launch. Full metadata annotations and first-offered evidence are in JSON.

Provenance: [program audit](../data/programs/northeastern-university-artificial-intelligence-and-ecology-and-evolutionary-biology-bs-boston-bs-degree.json) · [adapter notes](../atlas/adapters/northeastern-university-artificial-intelligence-and-ecology-and-evolutionary-biology-bs-boston-bs-degree/NOTES.md).

Official evidence (audit-wide):

- [Artificial Intelligence and Ecology and Evolutionary Biology, BS (Boston)](https://catalog.northeastern.edu/undergraduate/computer-information-science/computer-information-science-combined-majors/artificial-intelligence-ecology-evolutionary-biology-bs-bos/) — Program Requirements tab, including footnotes; Program overview
- [Data Science (DS)](https://catalog.northeastern.edu/course-descriptions/ds/) — Named course blocks: DS 3500, DS 3000, DS 4200, DS 4300, DS 4400, DS 4420
- [Universitywide Requirements](https://catalog.northeastern.edu/undergraduate/university-academics/university-wide-requirements/) — textcontainer; named completion/eligibility sections only
- 5 additional audit sources, with exact URLs and locators, in this program’s JSON entry.

### Northeastern University — Artificial Intelligence and Economics, BS (Boston)

`northeastern-university-artificial-intelligence-and-economics-bs-boston-bs-degree` · partial · `institutional_clarification` · scope: degree

Current audits narrow the remaining gap to home-college applicability. Published hosting/participating-college context does not establish allowed or mandatory home-college designations.

Requirement gaps:

- Permitted home-college options and their additional progression/graduation rules have not been exhaustively verified for this combined degree. Catalog hosting context is not assumed to fix the student’s designated home college.

Latest audit and university-policy follow-up supersede earlier unexpanded-university/open-range notes. Open predicates and individual student clearance are not finite missing course pools. Business’s 14 concentrations are now mapped; no stale concentration gap is carried forward.

**Next action:** Obtain program-and-cohort-specific home-college choices, change-of-home-college criteria, applicable progression/graduation/transfer rules and seminar/co-op mapping. Start with the Biology/Business/Design evidence matrix, then verify each concrete variant rather than generalizing their participating-college pairs.

Separate metadata: 49 course records; missing descriptions/prerequisite statements/public sites/syllabi = 44/44/49/49. Missing fields do not establish no prerequisites, no outcomes or no launch. Full metadata annotations and first-offered evidence are in JSON.

Provenance: [program audit](../data/programs/northeastern-university-artificial-intelligence-and-economics-bs-boston-bs-degree.json) · [adapter notes](../atlas/adapters/northeastern-university-artificial-intelligence-and-economics-bs-boston-bs-degree/NOTES.md).

Official evidence (audit-wide):

- [Artificial Intelligence and Economics, BS (Boston)](https://catalog.northeastern.edu/undergraduate/computer-information-science/computer-information-science-combined-majors/artificial-intelligence-economics-bs-bos/) — Program Requirements tab, including footnotes; Program overview
- [Data Science (DS)](https://catalog.northeastern.edu/course-descriptions/ds/) — Named course blocks: DS 3500, DS 3000, DS 4200, DS 4300, DS 4400, DS 1300
- [Universitywide Requirements](https://catalog.northeastern.edu/undergraduate/university-academics/university-wide-requirements/) — textcontainer; named completion/eligibility sections only
- 5 additional audit sources, with exact URLs and locators, in this program’s JSON entry.

### Northeastern University — Artificial Intelligence and Environmental and Sustainability Sciences, BS (Boston)

`northeastern-university-artificial-intelligence-and-environmental-and-sustainability-sciences-bs-boston-bs-degree` · partial · `institutional_clarification` · scope: degree

Current audits narrow the remaining gap to home-college applicability. Published hosting/participating-college context does not establish allowed or mandatory home-college designations.

Requirement gaps:

- Permitted home-college options and their additional progression/graduation rules have not been exhaustively verified for this combined degree. Catalog hosting context is not assumed to fix the student’s designated home college.

Latest audit and university-policy follow-up supersede earlier unexpanded-university/open-range notes. Open predicates and individual student clearance are not finite missing course pools. Business’s 14 concentrations are now mapped; no stale concentration gap is carried forward.

**Next action:** Obtain program-and-cohort-specific home-college choices, change-of-home-college criteria, applicable progression/graduation/transfer rules and seminar/co-op mapping. Start with the Biology/Business/Design evidence matrix, then verify each concrete variant rather than generalizing their participating-college pairs.

Separate metadata: 82 course records; missing descriptions/prerequisite statements/public sites/syllabi = 76/76/82/82. Missing fields do not establish no prerequisites, no outcomes or no launch. Full metadata annotations and first-offered evidence are in JSON.

Provenance: [program audit](../data/programs/northeastern-university-artificial-intelligence-and-environmental-and-sustainability-sciences-bs-boston-bs-degree.json) · [adapter notes](../atlas/adapters/northeastern-university-artificial-intelligence-and-environmental-and-sustainability-sciences-bs-boston-bs-degree/NOTES.md).

Official evidence (audit-wide):

- [Artificial Intelligence and Environmental and Sustainability Sciences, BS (Boston)](https://catalog.northeastern.edu/undergraduate/computer-information-science/computer-information-science-combined-majors/artificial-intelligence-environmental-sustainability-sciences-bs-bos/) — Program Requirements tab, including footnotes; Program overview
- [Data Science (DS)](https://catalog.northeastern.edu/course-descriptions/ds/) — Named course blocks: DS 3500, DS 3000, DS 4200, DS 4300, DS 4400, DS 4420
- [Universitywide Requirements](https://catalog.northeastern.edu/undergraduate/university-academics/university-wide-requirements/) — textcontainer; named completion/eligibility sections only
- 5 additional audit sources, with exact URLs and locators, in this program’s JSON entry.

### Northeastern University — Artificial Intelligence and Health Science, BS (Boston)

`northeastern-university-artificial-intelligence-and-health-science-bs-boston-bs-degree` · partial · `institutional_clarification` · scope: degree

Current audits narrow the remaining gap to home-college applicability. Published hosting/participating-college context does not establish allowed or mandatory home-college designations.

Requirement gaps:

- Permitted home-college options and their additional progression/graduation rules have not been exhaustively verified for this combined degree. Catalog hosting context is not assumed to fix the student’s designated home college.

Latest audit and university-policy follow-up supersede earlier unexpanded-university/open-range notes. Open predicates and individual student clearance are not finite missing course pools. Business’s 14 concentrations are now mapped; no stale concentration gap is carried forward.

**Next action:** Obtain program-and-cohort-specific home-college choices, change-of-home-college criteria, applicable progression/graduation/transfer rules and seminar/co-op mapping. Start with the Biology/Business/Design evidence matrix, then verify each concrete variant rather than generalizing their participating-college pairs.

Separate metadata: 51 course records; missing descriptions/prerequisite statements/public sites/syllabi = 45/45/51/51. Missing fields do not establish no prerequisites, no outcomes or no launch. Full metadata annotations and first-offered evidence are in JSON.

Provenance: [program audit](../data/programs/northeastern-university-artificial-intelligence-and-health-science-bs-boston-bs-degree.json) · [adapter notes](../atlas/adapters/northeastern-university-artificial-intelligence-and-health-science-bs-boston-bs-degree/NOTES.md).

Official evidence (audit-wide):

- [Artificial Intelligence and Health Science, BS (Boston)](https://catalog.northeastern.edu/undergraduate/computer-information-science/computer-information-science-combined-majors/artificial-intelligence-health-science-bs-bos/) — Program Requirements tab, including footnotes; Program overview
- [Data Science (DS)](https://catalog.northeastern.edu/course-descriptions/ds/) — Named course blocks: DS 3500, DS 3000, DS 4200, DS 4300, DS 4400, DS 4420
- [Universitywide Requirements](https://catalog.northeastern.edu/undergraduate/university-academics/university-wide-requirements/) — textcontainer; named completion/eligibility sections only
- 5 additional audit sources, with exact URLs and locators, in this program’s JSON entry.

### Northeastern University — Artificial Intelligence and International Affairs, BS (Boston)

`northeastern-university-artificial-intelligence-and-international-affairs-bs-boston-bs-degree` · partial · `institutional_clarification` · scope: degree

Current audits narrow the remaining gap to home-college applicability. Published hosting/participating-college context does not establish allowed or mandatory home-college designations.

Requirement gaps:

- Permitted home-college options and their additional progression/graduation rules have not been exhaustively verified for this combined degree. Catalog hosting context is not assumed to fix the student’s designated home college.

Latest audit and university-policy follow-up supersede earlier unexpanded-university/open-range notes. Open predicates and individual student clearance are not finite missing course pools. Business’s 14 concentrations are now mapped; no stale concentration gap is carried forward.

**Next action:** Obtain program-and-cohort-specific home-college choices, change-of-home-college criteria, applicable progression/graduation/transfer rules and seminar/co-op mapping. Start with the Biology/Business/Design evidence matrix, then verify each concrete variant rather than generalizing their participating-college pairs.

Separate metadata: 180 course records; missing descriptions/prerequisite statements/public sites/syllabi = 173/167/180/180. Missing fields do not establish no prerequisites, no outcomes or no launch. Full metadata annotations and first-offered evidence are in JSON.

Provenance: [program audit](../data/programs/northeastern-university-artificial-intelligence-and-international-affairs-bs-boston-bs-degree.json) · [adapter notes](../atlas/adapters/northeastern-university-artificial-intelligence-and-international-affairs-bs-boston-bs-degree/NOTES.md).

Official evidence (audit-wide):

- [Artificial Intelligence and International Affairs, BS (Boston)](https://catalog.northeastern.edu/undergraduate/computer-information-science/computer-information-science-combined-majors/artificial-intelligence-international-affairs-bs-bos/) — Program Requirements tab, all local tables and footnotes; Program overview
- [Data Science (DS)](https://catalog.northeastern.edu/course-descriptions/ds/) — Named course blocks: DS 3500, DS 3000, DS 4200, DS 4300, DS 4400
- [International Affairs (INTL)](https://catalog.northeastern.edu/course-descriptions/intl/) — Named course blocks: INTL 1000, INTL 1101, INTL 2718, INTL 3400, INTL 5100, INTL 5268, INTL 2480, INTL 2600, INTL 3520, INTL 5010, INTL 3430, INTL 3450, INTL 3300, INTL 3200, INTL 2500, INTL 4100, INTL 3150, INTL 3255, INTL 3455, INTL 4500, INTL 1160, INTL 2100, INTL 2200, INTL 3470, INTL 3350, INTL 3406, INTL 4700
- 6 additional audit sources, with exact URLs and locators, in this program’s JSON entry.

### Northeastern University — Artificial Intelligence and Journalism, BS (Boston)

`northeastern-university-artificial-intelligence-and-journalism-bs-boston-bs-degree` · partial · `institutional_clarification` · scope: degree

Current audits narrow the remaining gap to home-college applicability. Published hosting/participating-college context does not establish allowed or mandatory home-college designations.

Requirement gaps:

- Permitted home-college options and their additional progression/graduation rules have not been exhaustively verified for this combined degree. Catalog hosting context is not assumed to fix the student’s designated home college.

Latest audit and university-policy follow-up supersede earlier unexpanded-university/open-range notes. Open predicates and individual student clearance are not finite missing course pools. Business’s 14 concentrations are now mapped; no stale concentration gap is carried forward.

**Next action:** Obtain program-and-cohort-specific home-college choices, change-of-home-college criteria, applicable progression/graduation/transfer rules and seminar/co-op mapping. Start with the Biology/Business/Design evidence matrix, then verify each concrete variant rather than generalizing their participating-college pairs.

Separate metadata: 45 course records; missing descriptions/prerequisite statements/public sites/syllabi = 36/37/45/45. Missing fields do not establish no prerequisites, no outcomes or no launch. Full metadata annotations and first-offered evidence are in JSON.

Provenance: [program audit](../data/programs/northeastern-university-artificial-intelligence-and-journalism-bs-boston-bs-degree.json) · [adapter notes](../atlas/adapters/northeastern-university-artificial-intelligence-and-journalism-bs-boston-bs-degree/NOTES.md).

Official evidence (audit-wide):

- [Artificial Intelligence and Journalism, BS (Boston)](https://catalog.northeastern.edu/undergraduate/computer-information-science/computer-information-science-combined-majors/artificial-intelligence-journalism-bs-bos/) — Program Requirements tab, all local tables and footnotes; Program overview
- [Data Science (DS)](https://catalog.northeastern.edu/course-descriptions/ds/) — Named course blocks: DS 3500, DS 3000, DS 4200, DS 4300, DS 4400, DS 4420, DS 1300
- [Journalism (JRNL)](https://catalog.northeastern.edu/course-descriptions/jrnl/) — Named course blocks: JRNL 1000, JRNL 1101, JRNL 1102, JRNL 2201, JRNL 2301, JRNL 3610, JRNL 1150, JRNL 3550, JRNL 4650, JRNL 3700, JRNL 5500
- 6 additional audit sources, with exact URLs and locators, in this program’s JSON entry.

### Northeastern University — Artificial Intelligence and Linguistics, BS (Boston)

`northeastern-university-artificial-intelligence-and-linguistics-bs-boston-bs-degree` · partial · `institutional_clarification` · scope: degree

Current audits narrow the remaining gap to home-college applicability. Published hosting/participating-college context does not establish allowed or mandatory home-college designations.

Requirement gaps:

- Permitted home-college options and their additional progression/graduation rules have not been exhaustively verified for this combined degree. Catalog hosting context is not assumed to fix the student’s designated home college.

Latest audit and university-policy follow-up supersede earlier unexpanded-university/open-range notes. Open predicates and individual student clearance are not finite missing course pools. Business’s 14 concentrations are now mapped; no stale concentration gap is carried forward.

**Next action:** Obtain program-and-cohort-specific home-college choices, change-of-home-college criteria, applicable progression/graduation/transfer rules and seminar/co-op mapping. Start with the Biology/Business/Design evidence matrix, then verify each concrete variant rather than generalizing their participating-college pairs.

Separate metadata: 45 course records; missing descriptions/prerequisite statements/public sites/syllabi = 28/31/45/45. Missing fields do not establish no prerequisites, no outcomes or no launch. Full metadata annotations and first-offered evidence are in JSON.

Provenance: [program audit](../data/programs/northeastern-university-artificial-intelligence-and-linguistics-bs-boston-bs-degree.json) · [adapter notes](../atlas/adapters/northeastern-university-artificial-intelligence-and-linguistics-bs-boston-bs-degree/NOTES.md).

Official evidence (audit-wide):

- [Artificial Intelligence and Linguistics, BS (Boston)](https://catalog.northeastern.edu/undergraduate/computer-information-science/computer-information-science-combined-majors/artificial-intelligence-linguistics-bs-bos/) — Program Requirements tab, including footnotes; Program overview
- [Data Science (DS)](https://catalog.northeastern.edu/course-descriptions/ds/) — Named course blocks: DS 3500, DS 3000, DS 4200, DS 4300, DS 4400, DS 4420
- [Linguistics (LING)](https://catalog.northeastern.edu/course-descriptions/ling/) — Named course blocks: LING 1150, LING 2350, LING 3412, LING 3420, LING 3422, LING 3424, LING 3450, LING 3452, LING 4891, LING 4991, LING 4654
- 6 additional audit sources, with exact URLs and locators, in this program’s JSON entry.

### Northeastern University — Artificial Intelligence and Mathematics, BS (Boston)

`northeastern-university-artificial-intelligence-and-mathematics-bs-boston-bs-degree` · partial · `institutional_clarification` · scope: degree

Current audits narrow the remaining gap to home-college applicability. Published hosting/participating-college context does not establish allowed or mandatory home-college designations.

Requirement gaps:

- Permitted home-college options and their additional progression/graduation rules have not been exhaustively verified for this combined degree. Catalog hosting context is not assumed to fix the student’s designated home college.

Latest audit and university-policy follow-up supersede earlier unexpanded-university/open-range notes. Open predicates and individual student clearance are not finite missing course pools. Business’s 14 concentrations are now mapped; no stale concentration gap is carried forward.

**Next action:** Obtain program-and-cohort-specific home-college choices, change-of-home-college criteria, applicable progression/graduation/transfer rules and seminar/co-op mapping. Start with the Biology/Business/Design evidence matrix, then verify each concrete variant rather than generalizing their participating-college pairs.

Separate metadata: 34 course records; missing descriptions/prerequisite statements/public sites/syllabi = 28/28/34/34. Missing fields do not establish no prerequisites, no outcomes or no launch. Full metadata annotations and first-offered evidence are in JSON.

Provenance: [program audit](../data/programs/northeastern-university-artificial-intelligence-and-mathematics-bs-boston-bs-degree.json) · [adapter notes](../atlas/adapters/northeastern-university-artificial-intelligence-and-mathematics-bs-boston-bs-degree/NOTES.md).

Official evidence (audit-wide):

- [Artificial Intelligence and Mathematics, BS (Boston)](https://catalog.northeastern.edu/undergraduate/computer-information-science/computer-information-science-combined-majors/artificial-intelligence-mathematics-bs-bos/) — Program Requirements tab, including footnotes; Program overview
- [Data Science (DS)](https://catalog.northeastern.edu/course-descriptions/ds/) — Named course blocks: DS 3500, DS 3000, DS 4200, DS 4300, DS 4400, DS 4420
- [Universitywide Requirements](https://catalog.northeastern.edu/undergraduate/university-academics/university-wide-requirements/) — textcontainer; named completion/eligibility sections only
- 5 additional audit sources, with exact URLs and locators, in this program’s JSON entry.

### Northeastern University — Artificial Intelligence and Philosophy, BS (Boston)

`northeastern-university-artificial-intelligence-and-philosophy-bs-boston-bs-degree` · partial · `institutional_clarification` · scope: degree

Current audits narrow the remaining gap to home-college applicability. Published hosting/participating-college context does not establish allowed or mandatory home-college designations.

Requirement gaps:

- Permitted home-college options and their additional progression/graduation rules have not been exhaustively verified for this combined degree. Catalog hosting context is not assumed to fix the student’s designated home college.

Latest audit and university-policy follow-up supersede earlier unexpanded-university/open-range notes. Open predicates and individual student clearance are not finite missing course pools. Business’s 14 concentrations are now mapped; no stale concentration gap is carried forward.

**Next action:** Obtain program-and-cohort-specific home-college choices, change-of-home-college criteria, applicable progression/graduation/transfer rules and seminar/co-op mapping. Start with the Biology/Business/Design evidence matrix, then verify each concrete variant rather than generalizing their participating-college pairs.

Separate metadata: 50 course records; missing descriptions/prerequisite statements/public sites/syllabi = 50/50/50/50. Missing fields do not establish no prerequisites, no outcomes or no launch. Full metadata annotations and first-offered evidence are in JSON.

Provenance: [program audit](../data/programs/northeastern-university-artificial-intelligence-and-philosophy-bs-boston-bs-degree.json) · [adapter notes](../atlas/adapters/northeastern-university-artificial-intelligence-and-philosophy-bs-boston-bs-degree/NOTES.md).

Official evidence (audit-wide):

- [Artificial Intelligence and Philosophy, BS (Boston)](https://catalog.northeastern.edu/undergraduate/computer-information-science/computer-information-science-combined-majors/artificial-intelligence-philosophy-bs-bos/) — Program Requirements tab; Program overview
- [Universitywide Requirements](https://catalog.northeastern.edu/undergraduate/university-academics/university-wide-requirements/) — textcontainer; named completion/eligibility sections only
- [General Education Requirements](https://catalog.northeastern.edu/undergraduate/university-academics/general-education-requirements/) — nupathtextcontainer; named completion/eligibility sections only
- 4 additional audit sources, with exact URLs and locators, in this program’s JSON entry.

### Northeastern University — Artificial Intelligence and Physics, BS (Boston)

`northeastern-university-artificial-intelligence-and-physics-bs-boston-bs-degree` · partial · `institutional_clarification` · scope: degree

Current audits narrow the remaining gap to home-college applicability. Published hosting/participating-college context does not establish allowed or mandatory home-college designations.

Requirement gaps:

- Permitted home-college options and their additional progression/graduation rules have not been exhaustively verified for this combined degree. Catalog hosting context is not assumed to fix the student’s designated home college.

Latest audit and university-policy follow-up supersede earlier unexpanded-university/open-range notes. Open predicates and individual student clearance are not finite missing course pools. Business’s 14 concentrations are now mapped; no stale concentration gap is carried forward.

**Next action:** Obtain program-and-cohort-specific home-college choices, change-of-home-college criteria, applicable progression/graduation/transfer rules and seminar/co-op mapping. Start with the Biology/Business/Design evidence matrix, then verify each concrete variant rather than generalizing their participating-college pairs.

Separate metadata: 49 course records; missing descriptions/prerequisite statements/public sites/syllabi = 44/44/49/49. Missing fields do not establish no prerequisites, no outcomes or no launch. Full metadata annotations and first-offered evidence are in JSON.

Provenance: [program audit](../data/programs/northeastern-university-artificial-intelligence-and-physics-bs-boston-bs-degree.json) · [adapter notes](../atlas/adapters/northeastern-university-artificial-intelligence-and-physics-bs-boston-bs-degree/NOTES.md).

Official evidence (audit-wide):

- [Artificial Intelligence and Physics, BS (Boston)](https://catalog.northeastern.edu/undergraduate/computer-information-science/computer-information-science-combined-majors/artificial-intelligence-physics-bs-bos/) — Program Requirements tab, including footnotes; Program overview
- [Data Science (DS)](https://catalog.northeastern.edu/course-descriptions/ds/) — Named course blocks: DS 3500, DS 3000, DS 4200, DS 4300, DS 4400
- [Universitywide Requirements](https://catalog.northeastern.edu/undergraduate/university-academics/university-wide-requirements/) — textcontainer; named completion/eligibility sections only
- 5 additional audit sources, with exact URLs and locators, in this program’s JSON entry.

### Northeastern University — Artificial Intelligence and Psychology, BS (Boston)

`northeastern-university-artificial-intelligence-and-psychology-bs-boston-bs-degree` · partial · `institutional_clarification` · scope: degree

Current audits narrow the remaining gap to home-college applicability. Published hosting/participating-college context does not establish allowed or mandatory home-college designations.

Requirement gaps:

- Permitted home-college options and their additional progression/graduation rules have not been exhaustively verified for this combined degree. Catalog hosting context is not assumed to fix the student’s designated home college.

Latest audit and university-policy follow-up supersede earlier unexpanded-university/open-range notes. Open predicates and individual student clearance are not finite missing course pools. Business’s 14 concentrations are now mapped; no stale concentration gap is carried forward.

**Next action:** Obtain program-and-cohort-specific home-college choices, change-of-home-college criteria, applicable progression/graduation/transfer rules and seminar/co-op mapping. Start with the Biology/Business/Design evidence matrix, then verify each concrete variant rather than generalizing their participating-college pairs.

Separate metadata: 62 course records; missing descriptions/prerequisite statements/public sites/syllabi = 56/56/62/62. Missing fields do not establish no prerequisites, no outcomes or no launch. Full metadata annotations and first-offered evidence are in JSON.

Provenance: [program audit](../data/programs/northeastern-university-artificial-intelligence-and-psychology-bs-boston-bs-degree.json) · [adapter notes](../atlas/adapters/northeastern-university-artificial-intelligence-and-psychology-bs-boston-bs-degree/NOTES.md).

Official evidence (audit-wide):

- [Artificial Intelligence and Psychology, BS (Boston)](https://catalog.northeastern.edu/undergraduate/computer-information-science/computer-information-science-combined-majors/artificial-intelligence-psychology-bs-bos/) — Program Requirements tab, including footnotes; Program overview
- [Data Science (DS)](https://catalog.northeastern.edu/course-descriptions/ds/) — Named course blocks: DS 3500, DS 3000, DS 4200, DS 4300, DS 4400, DS 4420
- [Universitywide Requirements](https://catalog.northeastern.edu/undergraduate/university-academics/university-wide-requirements/) — textcontainer; named completion/eligibility sections only
- 5 additional audit sources, with exact URLs and locators, in this program’s JSON entry.

### Northeastern University — Artificial Intelligence and Public Health, BS (Boston)

`northeastern-university-artificial-intelligence-and-public-health-bs-boston-bs-degree` · partial · `institutional_clarification` · scope: degree

Current audits narrow the remaining gap to home-college applicability. Published hosting/participating-college context does not establish allowed or mandatory home-college designations.

Requirement gaps:

- Permitted home-college options and their additional progression/graduation rules have not been exhaustively verified for this combined degree. Catalog hosting context is not assumed to fix the student’s designated home college.

Latest audit and university-policy follow-up supersede earlier unexpanded-university/open-range notes. Open predicates and individual student clearance are not finite missing course pools. Business’s 14 concentrations are now mapped; no stale concentration gap is carried forward.

**Next action:** Obtain program-and-cohort-specific home-college choices, change-of-home-college criteria, applicable progression/graduation/transfer rules and seminar/co-op mapping. Start with the Biology/Business/Design evidence matrix, then verify each concrete variant rather than generalizing their participating-college pairs.

Separate metadata: 97 course records; missing descriptions/prerequisite statements/public sites/syllabi = 91/91/97/97. Missing fields do not establish no prerequisites, no outcomes or no launch. Full metadata annotations and first-offered evidence are in JSON.

Provenance: [program audit](../data/programs/northeastern-university-artificial-intelligence-and-public-health-bs-boston-bs-degree.json) · [adapter notes](../atlas/adapters/northeastern-university-artificial-intelligence-and-public-health-bs-boston-bs-degree/NOTES.md).

Official evidence (audit-wide):

- [Artificial Intelligence and Public Health, BS (Boston)](https://catalog.northeastern.edu/undergraduate/computer-information-science/computer-information-science-combined-majors/artificial-intelligence-public-health-bs-bos/) — Program Requirements tab, including footnotes; Program overview
- [Data Science (DS)](https://catalog.northeastern.edu/course-descriptions/ds/) — Named course blocks: DS 3500, DS 3000, DS 4200, DS 4300, DS 4400, DS 4420
- [Universitywide Requirements](https://catalog.northeastern.edu/undergraduate/university-academics/university-wide-requirements/) — textcontainer; named completion/eligibility sections only
- 5 additional audit sources, with exact URLs and locators, in this program’s JSON entry.

### Northeastern University — Artificial Intelligence and Sociology, BS (Boston)

`northeastern-university-artificial-intelligence-and-sociology-bs-boston-bs-degree` · partial · `institutional_clarification` · scope: degree

Current audits narrow the remaining gap to home-college applicability. Published hosting/participating-college context does not establish allowed or mandatory home-college designations.

Requirement gaps:

- Permitted home-college options and their additional progression/graduation rules have not been exhaustively verified for this combined degree. Catalog hosting context is not assumed to fix the student’s designated home college.

Latest audit and university-policy follow-up supersede earlier unexpanded-university/open-range notes. Open predicates and individual student clearance are not finite missing course pools. Business’s 14 concentrations are now mapped; no stale concentration gap is carried forward.

**Next action:** Obtain program-and-cohort-specific home-college choices, change-of-home-college criteria, applicable progression/graduation/transfer rules and seminar/co-op mapping. Start with the Biology/Business/Design evidence matrix, then verify each concrete variant rather than generalizing their participating-college pairs.

Separate metadata: 36 course records; missing descriptions/prerequisite statements/public sites/syllabi = 29/27/36/36. Missing fields do not establish no prerequisites, no outcomes or no launch. Full metadata annotations and first-offered evidence are in JSON.

Provenance: [program audit](../data/programs/northeastern-university-artificial-intelligence-and-sociology-bs-boston-bs-degree.json) · [adapter notes](../atlas/adapters/northeastern-university-artificial-intelligence-and-sociology-bs-boston-bs-degree/NOTES.md).

Official evidence (audit-wide):

- [Artificial Intelligence and Sociology, BS (Boston)](https://catalog.northeastern.edu/undergraduate/computer-information-science/computer-information-science-combined-majors/artificial-intelligence-sociology-bs-bos/) — Program Requirements tab, all local tables and footnotes; Program overview
- [Data Science (DS)](https://catalog.northeastern.edu/course-descriptions/ds/) — Named course blocks: DS 3500, DS 3000, DS 4200, DS 4300, DS 4400
- [Sociology (SOCL)](https://catalog.northeastern.edu/course-descriptions/socl/) — Named course blocks: SOCL 1101, SOCL 3300, SOCL 2321, SOCL 4600, SOCL 1000, SOCL 2320, SOCL 2485, SOCL 4528
- 6 additional audit sources, with exact URLs and locators, in this program’s JSON entry.

### Northeastern University — Artificial Intelligence and Speech-Language Pathology and Audiology, BS (Boston)

`northeastern-university-artificial-intelligence-and-speech-language-pathology-and-audiology-bs-boston-bs-degree` · partial · `institutional_clarification` · scope: degree

Current audits narrow the remaining gap to home-college applicability. Published hosting/participating-college context does not establish allowed or mandatory home-college designations.

Requirement gaps:

- Permitted home-college options and their additional progression/graduation rules have not been exhaustively verified for this combined degree. Catalog hosting context is not assumed to fix the student’s designated home college.

Latest audit and university-policy follow-up supersede earlier unexpanded-university/open-range notes. Open predicates and individual student clearance are not finite missing course pools. Business’s 14 concentrations are now mapped; no stale concentration gap is carried forward.

**Next action:** Obtain program-and-cohort-specific home-college choices, change-of-home-college criteria, applicable progression/graduation/transfer rules and seminar/co-op mapping. Start with the Biology/Business/Design evidence matrix, then verify each concrete variant rather than generalizing their participating-college pairs.

Separate metadata: 43 course records; missing descriptions/prerequisite statements/public sites/syllabi = 35/35/43/43. Missing fields do not establish no prerequisites, no outcomes or no launch. Full metadata annotations and first-offered evidence are in JSON.

Provenance: [program audit](../data/programs/northeastern-university-artificial-intelligence-and-speech-language-pathology-and-audiology-bs-boston-bs-degree.json) · [adapter notes](../atlas/adapters/northeastern-university-artificial-intelligence-and-speech-language-pathology-and-audiology-bs-boston-bs-degree/NOTES.md).

Official evidence (audit-wide):

- [Artificial Intelligence and Speech-Language Pathology and Audiology, BS (Boston)](https://catalog.northeastern.edu/undergraduate/computer-information-science/computer-information-science-combined-majors/artificial-intelligence-speech-language-pathology-audiology-bs-bos/) — Program Requirements tab, all local tables and footnotes; Program overview
- [Data Science (DS)](https://catalog.northeastern.edu/course-descriptions/ds/) — Named course blocks: DS 3500, DS 3000, DS 4200, DS 4300, DS 4400
- [Speech-Language Pathology and Audiology (SLPA)](https://catalog.northeastern.edu/course-descriptions/slpa/) — Named course blocks: SLPA 2000, SLPA 1101, SLPA 1102, SLPA 1103, SLPA 1200, SLPA 1203, SLPA 1205, SLPA 4219, SLPA 4500, SLPA 4651, SLPA 5107
- 6 additional audit sources, with exact URLs and locators, in this program’s JSON entry.

### Northeastern University — Environmental Engineering and Artificial Intelligence, BSEnvE (Boston)

`northeastern-university-environmental-engineering-and-artificial-intelligence-bsenve-boston-other-degree` · partial · `institutional_clarification` · scope: degree

Current audits narrow the remaining gap to home-college applicability. Published hosting/participating-college context does not establish allowed or mandatory home-college designations.

Requirement gaps:

- Permitted home-college options and their additional progression/graduation rules have not been exhaustively verified for this combined degree. Catalog hosting context is not assumed to fix the student’s designated home college.

Latest audit and university-policy follow-up supersede earlier unexpanded-university/open-range notes. Open predicates and individual student clearance are not finite missing course pools. Business’s 14 concentrations are now mapped; no stale concentration gap is carried forward.

**Next action:** Obtain program-and-cohort-specific home-college choices, change-of-home-college criteria, applicable progression/graduation/transfer rules and seminar/co-op mapping. Start with the Biology/Business/Design evidence matrix, then verify each concrete variant rather than generalizing their participating-college pairs.

Separate metadata: 68 course records; missing descriptions/prerequisite statements/public sites/syllabi = 60/46/68/68. Missing fields do not establish no prerequisites, no outcomes or no launch. Full metadata annotations and first-offered evidence are in JSON.

Provenance: [program audit](../data/programs/northeastern-university-environmental-engineering-and-artificial-intelligence-bsenve-boston-other-degree.json) · [adapter notes](../atlas/adapters/northeastern-university-environmental-engineering-and-artificial-intelligence-bsenve-boston-other-degree/NOTES.md).

Official evidence (audit-wide):

- [Environmental Engineering and Artificial Intelligence, BSEnvE (Boston)](https://catalog.northeastern.edu/undergraduate/engineering/civil-environmental/environmental-engineering-artificial-intelligence-bsenve/) — Program Requirements tab, all local tables and footnotes; Program overview
- [Data Science (DS)](https://catalog.northeastern.edu/course-descriptions/ds/) — Named course blocks: DS 3500, DS 3000, DS 4200, DS 4300, DS 4400
- [Civil and Environmental Engineering (CIVE)](https://catalog.northeastern.edu/course-descriptions/cive/) — Named course blocks: CIVE 2221, CIVE 2222, CIVE 2300, CIVE 2301, CIVE 2331, CIVE 2334, CIVE 3435, CIVE 4534, CIVE 4535, CIVE 4765, CIVE 4540, CIVE 4777, CIVE 5100, CIVE 5150, CIVE 5250, CIVE 5255, CIVE 5260, CIVE 5261, CIVE 5271, CIVE 5275, CIVE 5280, CIVE 5281, CIVE 5363, CIVE 5365, CIVE 5366, CIVE 5368, CIVE 5369, CIVE 5536, CIVE 5670, CIVE 5699, CIVE 3430
- 7 additional audit sources, with exact URLs and locators, in this program’s JSON entry.

### Northwestern University — Artificial Intelligence Major, BS in Engineering

`northwestern-university-artificial-intelligence-major-bs-in-engineering-bse-degree` · partial · `mixed` · scope: degree

Public degree-wide material remains unstructured and the complete humanities criteria are deferred to advising; no authentication or publisher denial has been established for that system.

Requirement gaps:

- School-wide engineering, science, design and humanities approved pools and policies remain incomplete.
- The college page explicitly defers complete humanities criteria to its advising system; public rules alone are not a full degree audit.
- Four advanced-elective introductory exceptions and physics-substitute metadata remain to be expanded.
- The Undergraduate Registration Requirement and full college degree policies remain to be mapped.

**Next action:** Map engineering/science/design/HSS requirements and the Undergraduate Registration Requirement; expand four introductory advanced-elective exceptions. Obtain the complete humanities criteria referenced to advising and confirm applicable rules before declaring full BSE coverage.

Separate metadata: 98 course records; missing descriptions/prerequisite statements/public sites/syllabi = 98/98/98/98. Missing fields do not establish no prerequisites, no outcomes or no launch. Full metadata annotations and first-offered evidence are in JSON.

Provenance: [program audit](../data/programs/northwestern-university-artificial-intelligence-major-bs-in-engineering-bse-degree.json) · [adapter notes](../atlas/adapters/northwestern-university-artificial-intelligence-major-bs-in-engineering-bse-degree/NOTES.md).

Official evidence (audit-wide):

- [Artificial Intelligence Major, BS in Engineering — official degree catalog](https://catalogs.northwestern.edu/undergraduate/engineering-applied-science/artificial-intelligence/artificial-intelligence-major/) — Degree requirements tables and associated major policies

### University of Notre Dame — AI Essentials for Business

`notre-dame-ai-essentials-business-minor` · partial · `mixed` · scope: minor

The expanded public section was empty, not access-denied; a separate university/college policy disagreement and applicability review remain.

Requirement gaps:

- Additional approved electives section remained empty after public-browser expansion; the full finite approved list is unresolved.
- College-specific minor completion/transfer and first-course pass/fail applicability for students from different home colleges require further review.

**Next action:** Obtain the missing finite Additional Approved Electives list; reconcile the university pass/fail prohibition with Mendoza’s first-minor-course wording and establish home-college applicability for all-majors students.

Separate metadata: 12 course records; missing descriptions/prerequisite statements/public sites/syllabi = 0/11/12/12. Missing fields do not establish no prerequisites, no outcomes or no launch. Full metadata annotations and first-offered evidence are in JSON.

Provenance: [program audit](../data/programs/notre-dame-ai-essentials-business-minor.json) · [adapter notes](../atlas/adapters/notre-dame-ai-essentials-business-minor/NOTES.md).

Official evidence (audit-wide):

- [AI Essentials for Business — curriculum](https://mendoza.nd.edu/undergraduate/ai-essentials-for-business-minor/) — Course Requirements; Course List; Electives; How to Apply; eligibility and overlap notes
- [Undergraduate Academic Code — July 1, 2026](https://provost.nd.edu/assets/674712/undergraduate_academic_code_2026_final_1_.pdf) — §§1.2.2, 2.3, 3.3.11, 3.3.14, 5.4.2–5.4.5; semester hours, transfer, overlap, pass/fail and repeat rules
- [Mendoza College of Business — 2026–2027 Bulletin](https://catalog.nd.edu/undergraduate/business/) — Curriculum for BBA; four-year completion of added credentials; Pass-Fail paragraph

### University of Pennsylvania — Artificial Intelligence, BSE

`penn-bse-ai` · partial · `mixed` · scope: degree

Current audit retains source/applicability conflicts and unfinished handbook extraction. The old-host robots redirect was resolved, so it is not a current requirement access barrier.

Requirement gaps:

- Overview/detailed optional-concentration language still differs.
- The AI ethics pool and generic Engineering ethics course-eligibility list are not reconciled; the latter omits ARIN from CIS 4230/5230 eligibility.
- Breadth applicability for the 37-unit AI curriculum requires department clarification; the handbook explicitly scopes its depth rule to 40-unit curricula.
- Natural-science, SS/H and Technology in Business and Society classifications, exceptions and finite approved lists are inspected but not fully structured; free-elective no-credit exclusions remain to be mapped.
- Remaining degree-completion and residence details beyond the mapped external-transfer rule, and approved study-abroad/consortium exceptions, require further review.

Canonical Engineering handbook migration resolved the earlier conservative robots redirect stop; no current handbook access barrier is asserted.

**Next action:** Reconcile concentration optionality, AI ethics eligibility and 37-CU breadth applicability; structure natural-science/SS-H/TBS/no-credit exceptions and remaining residence/away-credit completion rules from the now-accessible canonical handbook.

Separate metadata: 450 course records; missing descriptions/prerequisite statements/public sites/syllabi = 450/450/449/449. Missing fields do not establish no prerequisites, no outcomes or no launch. Full metadata annotations and first-offered evidence are in JSON.

Provenance: [program audit](../data/programs/penn-bse-ai.json) · [adapter notes](../atlas/adapters/penn_bse/NOTES.md).

Official evidence (audit-wide):

- [Artificial Intelligence, BSE](https://ai.engineering.upenn.edu/academics/undergraduate/) — Curriculum requirements
- [Technical Electives — CIS Advising Handbook](https://advising.cis.upenn.edu/tech-electives/) — Introductory ARIN applicability statement; subsequent CSCI-only scope boundary
- [Official technical-elective JSON inventory](https://advising.cis.upenn.edu/assets/json/37cu_csci_tech_elective_list.json) — Current status column: approved entries and ask entries separated
- 1 additional audit sources, with exact URLs and locators, in this program’s JSON entry.

### Pennsylvania State University — Artificial Intelligence Engineering, Minor

`penn-state-ai-engineering-minor` · partial · `institutional_clarification` · scope: minor

Reviewed bulletin and EECS directory do not supply the finite list; no access-denial mechanism was documented for that missing list.

Requirement gaps:

- Department List approved elective inventory unavailable

**Next action:** Obtain the finite Department List of approved six-credit electives and restrictions from EECS or a public policy; verify the CMPSC 445 alternative’s relationship to A-I 410 prerequisites without assuming a waiver.

Separate metadata: 5 course records; missing descriptions/prerequisite statements/public sites/syllabi = 0/0/5/5. Missing fields do not establish no prerequisites, no outcomes or no launch. Full metadata annotations and first-offered evidence are in JSON.

Provenance: [program audit](../data/programs/penn-state-ai-engineering-minor.json) · [adapter notes](../atlas/adapters/penn-state-ai-engineering-minor/NOTES.md).

Official evidence (audit-wide):

- [Artificial Intelligence Engineering, Minor](https://bulletins.psu.edu/undergraduate/colleges/engineering/artificial-intelligence-engineering-minor/) — Program Description; Entrance to Minor; Program Requirements
- [2026-27 Academic Calendar](https://www.registrar.psu.edu/academic-calendars/2026-27.cfm) — Fall and Spring regular sessions; full semester footnote
- [Penn State ai course descriptions](https://bulletins.psu.edu/university-course-descriptions/undergraduate/a-i/) — Course blocks: A-I 305, A-I 410; credits and enforced prerequisites
- 3 additional audit sources, with exact URLs and locators, in this program’s JSON entry.

### Purdue University — Artificial Intelligence (Liberal Arts)

`purdue-ai-ba` · partial · `mixed` · scope: degree

The current catalog plan returned403 and the university announcement does not identify this BA’s competency fulfillment.

Requirement gaps:

- Philosophy required and elective inventory
- Degree-wide college and university requirements
- Grade, residency and overlap policies
- AI major fulfillment of the new university AI competency is not identified

Access evidence (`http_denial`): Current catalog plan returned HTTP 403; department plan and selected college sources remain accessible. Exact failed endpoint: <https://catalog.purdue.edu/preview_program.php?catoid=19&poid=35726>.

**Next action:** Obtain a readable authoritative BA plan, then map the eight philosophy courses and college/university completion rules; ask which BA requirement satisfies the Fall-2026 university AI competency. Do not adopt the old CLA-core proposal as current.

Separate metadata: 5 course records; missing descriptions/prerequisite statements/public sites/syllabi = 2/4/5/2. Missing fields do not establish no prerequisites, no outcomes or no launch. Full metadata annotations and first-offered evidence are in JSON.

Provenance: [program audit](../data/programs/purdue-ai-ba.json) · [adapter notes](../atlas/adapters/purdue-ai-ba/NOTES.md).

Official evidence (audit-wide):

- [BA in Artificial Intelligence](https://www.cla.purdue.edu/academic/philosophy/students/undergraduate/majors/artificial-intelligence/index.html) — Plan of Study; five listed required CS courses and subject credit totals
- [AI competency graduation requirement begins in every undergraduate degree program](https://www.purdue.edu/newsroom/2026/Q3/purdues-ai-competency-graduation-requirement-begins-in-every-undergraduate-degree-program/) — Incoming Fall 2026 class; university core requirement; approved course credit range

### Purdue University — Artificial Intelligence, BS

`purdue-ai-bs` · partial · `mixed` · scope: degree

A documented catalog403 coexists with accessible unextracted pools and specific approval/wording ambiguities; the entire university source set is not blocked.

Requirement gaps:

- Full current AI catalog plan and university degree/GPA/residency/civics rules remain inaccessible or unreviewed
- Full general education/culture approved title pools not materialized; language sequence approvals and detailed study-abroad conditions remain unresolved
- University Written/Oral Communication and STS approved lists are linked to a Tableau dashboard, not yet extracted
- Malformed chemistry sequence text and AI-specific laboratory approval need clarification
- AI major fulfillment of the new university AI competency is not identified
- College not-recommended free-elective list not yet reviewed

Access evidence (`http_denial`): Current catalog plan returned HTTP 403; GE/culture and other linked College of Science pages are accessible/unextracted. Exact failed endpoint: <https://catalog.purdue.edu/preview_program.php?catoid=19&poid=35981>.

**Next action:** Prioritize accessible GE/culture tables, approved communication/STS dashboard lists and free-elective rules; resolve chemistry grouping, AI lab applicability and Fall-2026 competency fulfillment; obtain the blocked current catalog plan and remaining university degree policies through permitted evidence.

Separate metadata: 100 course records; missing descriptions/prerequisite statements/public sites/syllabi = 97/98/100/97. Missing fields do not establish no prerequisites, no outcomes or no launch. Full metadata annotations and first-offered evidence are in JSON.

Provenance: [program audit](../data/programs/purdue-ai-bs.json) · [adapter notes](../atlas/adapters/purdue-ai-bs/NOTES.md).

Official evidence (audit-wide):

- [Artificial Intelligence Degree Requirements - Fall 2026 to Present](https://www.cs.purdue.edu/undergraduate/curriculum/bachelor-ai.html) — h1; core table; Course Selectives; capstone
- [College of Science Core Curriculum Requirements](https://www.purdue.edu/science/Current_Students/curriculum_and_degree_requirements/college-of-science-core-requirements.html) — Fall 2007 onward applicability; 11 required scientific/professional development areas; approved experiential learning
- [Writing requirements](https://www.purdue.edu/science/Current_Students/curriculum_and_degree_requirements/approved-courses-in-technical-writing.html) — Current course pools / selection conditions
- 13 additional audit sources, with exact URLs and locators, in this program’s JSON entry.

### Rice University — Artificial Intelligence

`rice-university-artificial-intelligence-bs-degree` · partial · `accessible_unreviewed` · scope: degree

The degree’s linked general policies remain structurally unreviewed; no requirement-source access failure is documented.

Requirement gaps:

- University graduation, residence, distribution, communication, diversity and physical activity policies require full structured mapping.
- Program substitutions and transfer rules link to university policies that remain incompletely mapped.

**Next action:** Map linked university distribution, communication, diversity, physical activity, residence, graduation and transfer/substitution policies; retain existing major counts and cross-listed bundles.

Separate metadata: 43 course records; missing descriptions/prerequisite statements/public sites/syllabi = 43/43/43/43. Missing fields do not establish no prerequisites, no outcomes or no launch. Full metadata annotations and first-offered evidence are in JSON.

Provenance: [program audit](../data/programs/rice-university-artificial-intelligence-bs-degree.json) · [adapter notes](../atlas/adapters/rice-university-artificial-intelligence-bs-degree/NOTES.md).

Official evidence (audit-wide):

- [Artificial Intelligence — official degree catalog](https://ga.rice.edu/programs-study/departments-programs/engineering/artificial-intelligence/artificial-intelligence-bs/) — Degree requirements tables and associated major policies

### Rochester Institute of Technology — AI in Society

`rit-ai-society-minor` · partial · `accessible_unreviewed` · scope: minor

The curriculum is readable in the normal browser. The missing requirement work is university policy review; robots 202 limits automatic refresh, not proof those policies are inaccessible.

Requirement gaps:

- General university minor residence, transfer and grading policies have not been fully reviewed.

Automated robots 202 stop remains a refresh limitation; normal public browser curriculum review succeeded.

**Next action:** Use the ordinary public catalog interface to review applicable university minor residence, transfer and grading rules; maintain browser-reviewed evidence separately from the automated refresh limitation.

Separate metadata: 16 course records; missing descriptions/prerequisite statements/public sites/syllabi = 16/16/16/16. Missing fields do not establish no prerequisites, no outcomes or no launch. Full metadata annotations and first-offered evidence are in JSON.

Provenance: [program audit](../data/programs/rit-ai-society-minor.json) · [adapter notes](../atlas/adapters/rit-ai-society-minor/NOTES.md).

Official evidence (audit-wide):

- [AI in Society — curriculum](https://academiccatalog.rit.edu/programs/ai-society-minor/) — Program overview, course requirement table, elective lists and program policy notes; reviewed in ordinary browser UI

### Rochester Institute of Technology — Artificial Intelligence

`rochester-institute-of-technology-artificial-intelligence-bs-degree` · partial · `mixed` · scope: degree

The browser-readable source is a typical sequence with ambiguous immersion placement; mandatory degree-wide policies remain unreviewed. Automated shells are a refresh limitation.

Requirement gaps:

- Full university/college degree-wide graduation, residence, transfer, GPA and general-education policies remain unreviewed.
- Approved general-education and immersion inventories and the duplicate Immersion 3 annotation need review.
- Normalized credit unit is unverified; sequence alone does not certify the full mandatory degree inventory.

Automated retrieval yielded a JavaScript/bot shell, while the normal browser displayed the curriculum. Do not label the reviewed catalog universally inaccessible.

**Next action:** Verify mandatory requirements beyond the typical sequence, resolve duplicated Immersion3 allocation, and map full GE/immersion and degree completion policies in the ordinary public catalog. Keep grouped credits and current enrollment separate.

Separate metadata: 40 course records; missing descriptions/prerequisite statements/public sites/syllabi = 40/40/40/40. Missing fields do not establish no prerequisites, no outcomes or no launch. Full metadata annotations and first-offered evidence are in JSON.

Provenance: [program audit](../data/programs/rochester-institute-of-technology-artificial-intelligence-bs-degree.json) · [adapter notes](../atlas/adapters/rochester-institute-of-technology-artificial-intelligence-bs-degree/NOTES.md).

Official evidence (audit-wide):

- [Artificial Intelligence Bachelor of Science Degree](https://www.rit.edu/study/artificial-intelligence-bs) — Degree overview, required co-op blocks, first-year and transfer admissions
- [Artificial Intelligence BS](https://academiccatalog.rit.edu/programs/artificial-intelligence-bs/) — Curriculum tab: typical sequence, total hours, wellness note and AI electives; read in ordinary browser

### Rochester Institute of Technology — Artificial Intelligence

`rochester-institute-of-technology-artificial-intelligence-minor-minor` · partial · `accessible_unreviewed` · scope: minor

The curriculum is readable in the normal browser. The missing requirement work is university policy review; robots 202 limits automatic refresh, not proof those policies are inaccessible.

Requirement gaps:

- General university minor residence, transfer and grading policies have not been fully reviewed.

Automated robots 202 stop remains a refresh limitation; normal public browser curriculum review succeeded.

**Next action:** Use the ordinary public catalog interface to review applicable university minor residence, transfer and grading rules; maintain browser-reviewed evidence separately from the automated refresh limitation.

Separate metadata: 17 course records; missing descriptions/prerequisite statements/public sites/syllabi = 16/16/17/17. Missing fields do not establish no prerequisites, no outcomes or no launch. Full metadata annotations and first-offered evidence are in JSON.

Provenance: [program audit](../data/programs/rochester-institute-of-technology-artificial-intelligence-minor-minor.json) · [adapter notes](../atlas/adapters/rochester-institute-of-technology-artificial-intelligence-minor-minor/NOTES.md).

Official evidence (audit-wide):

- [Artificial Intelligence](https://www.rit.edu/study/artificial-intelligence-minor) — Named undergraduate program entry: Artificial Intelligence; award/type: minor / minor
- [Artificial Intelligence — curriculum](https://academiccatalog.rit.edu/programs/artificial-intelligence-minor/) — Program overview, course requirement table, elective lists and program policy notes; reviewed in ordinary browser UI
- [GCIS-505 AI for Programmers](https://academiccatalog.rit.edu/search/?P=GCIS-505) — GCIS-505 course popup opened from minor curriculum: description, 1 credit and prerequisites

### Stevens Institute of Technology — Artificial Intelligence

`stevens-institute-of-technology-artificial-intelligence-bs-degree` · partial · `accessible_unreviewed` · scope: degree

Rendered public catalog content works; raw-HTML placeholders are a parser-input limitation, not a current access barrier.

Requirement gaps:

- Linked university humanities distribution requirements
- Full open math/science/general elective inventory and detailed option eligibility
- Individual technical/science/SUCCESS option metadata and graduate-course access
- University graduation, GPA, residency, transfer and other overlap rules

RawHTML unresolved labels require ordinary rendering; a functioning public catalog is not an access barrier.

**Next action:** Read the linked humanities and university graduation/GPA/residence/transfer rules, then verify elective/SUCCESS eligibility and graduate options; use ordinary rendered content and retain open advisor-approved ranges as policies.

Separate metadata: 27 course records; missing descriptions/prerequisite statements/public sites/syllabi = 27/27/27/27. Missing fields do not establish no prerequisites, no outcomes or no launch. Full metadata annotations and first-offered evidence are in JSON.

Provenance: [program audit](../data/programs/stevens-institute-of-technology-artificial-intelligence-bs-degree.json) · [adapter notes](../atlas/adapters/stevens-institute-of-technology-artificial-intelligence-bs-degree/NOTES.md).

Official evidence (audit-wide):

- [Bachelor of Science in Artificial Intelligence — Academic Plan](https://stevens.catalog.prod.coursedog.com/programs/qT6Ld1CzBAhQsVKYFNVv/academic-plan-JKlwr) — Browser-rendered academic plan, eight semesters; 125-credit total
- [Bachelor of Science in Artificial Intelligence — Requirements and Concentrations](https://stevens.catalog.prod.coursedog.com/programs/qT6Ld1CzBAhQsVKYFNVv/requirements-and-concentrations-n90Np) — Browser-rendered math/science, technical/general electives, exclusion pairs, humanities and SUCCESS sections
- [Bachelor of Science in Artificial Intelligence — General](https://stevens.catalog.prod.coursedog.com/programs/qT6Ld1CzBAhQsVKYFNVv) — Program description and objectives

### Stevens Institute of Technology — Artificial Intelligence

`stevens-institute-of-technology-artificial-intelligence-minor-minor` · partial · `institutional_clarification` · scope: minor

Three related public policy sections were inspected without resolving the incorporated rule; no denial was documented.

Requirement gaps:

- The catalog explicitly incorporates institute-wide minor requirements; their full applicable policy has not been verified.

**Next action:** Locate or obtain the institute-wide minor policy explicitly incorporated by this program, with grade, overlap, transfer and residence applicability; retain the two mapped student-major pathways.

Separate metadata: 19 course records; missing descriptions/prerequisite statements/public sites/syllabi = 19/19/19/19. Missing fields do not establish no prerequisites, no outcomes or no launch. Full metadata annotations and first-offered evidence are in JSON.

Provenance: [program audit](../data/programs/stevens-institute-of-technology-artificial-intelligence-minor-minor.json) · [adapter notes](../atlas/adapters/stevens-institute-of-technology-artificial-intelligence-minor-minor/NOTES.md).

Official evidence (audit-wide):

- [Artificial Intelligence](https://stevens.catalog.prod.coursedog.com/programs/9a968dad026510010633ba4bf9db0000) — Named undergraduate program entry: Artificial Intelligence; award/type: minor / minor
- [Minor in Artificial Intelligence — Requirements and Concentrations](https://stevens.catalog.prod.coursedog.com/programs/9a968dad026510010633ba4bf9db0000/requirements-and-concentrations-n90Np) — Rendered catalog: both major-dependent pathways; required courses, electives and overlap/grade rules

### Stony Brook University–SUNY — AI for Business Innovation

`stony-brook-ai-business-innovation-specialization` · partial · `access_barrier` · scope: concentration

The current requirement-source gap has a documented retrieval or access condition; this is not an assertion of program absence or a university-wide denial.

Requirement gaps:

- Named course inventory, credit total and selection rules are unavailable from the inspected department page; linked catalog access remains blocked by TLS verification failure.

Access evidence (`tls_transport_failure`): Main-host robots policy is valid; redirect to catalog.stonybrook.edu fails TLS issuer verification during robots retrieval. No publisher denial is established; TLS checks were not disabled. Exact failed endpoint: <https://catalog.stonybrook.edu/robots.txt>.

**Next action:** Use the recorded official requirement link only when normally readable, or obtain independently authoritative public requirements/institutional clarification. Preserve the recorded access condition; do not bypass it. Then map this represented award’s exact pools, choices and completion rules.

Separate metadata: 0 course records; missing descriptions/prerequisite statements/public sites/syllabi = 0/0/0/0. Missing fields do not establish no prerequisites, no outcomes or no launch. Full metadata annotations and first-offered evidence are in JSON.

Provenance: [program audit](../data/programs/stony-brook-ai-business-innovation-specialization.json) · [adapter notes](../atlas/adapters/stony-brook-ai-business-innovation-specialization/NOTES.md).

Official evidence (audit-wide):

- [Business Management Specializations](https://www.stonybrook.edu/business/undergraduate/specializations.html) — AI for Business Innovation entry, cohort note and specialization FAQs

### Stony Brook University–SUNY — Artificial Intelligence and Data Science

`stony-brook-ai-data-science-specialization` · pending · `access_barrier` · scope: concentration

The current requirement-source gap has a documented retrieval or access condition; this is not an assertion of program absence or a university-wide denial.

Requirement gaps:

- No reviewed current course/choice inventory or completion-policy map for the local concentration requirements and eligibility, not the whole parent degree.

Access evidence (`tls_transport_failure`): Main-host robots policy is valid; redirect to catalog.stonybrook.edu fails TLS issuer verification during robots retrieval. No publisher denial is established; TLS checks were not disabled. Exact failed endpoint: <https://catalog.stonybrook.edu/robots.txt>.

**Next action:** Resolve the catalog-host TLS/trust failure without disabling verification, then inspect the current CS specialization. Keep the readable Fall 2024 rules historical; map current choices/policies only from current authoritative evidence.

Separate metadata: 0 course records; missing descriptions/prerequisite statements/public sites/syllabi = 0/0/0/0. Missing fields do not establish no prerequisites, no outcomes or no launch. Full metadata annotations and first-offered evidence are in JSON.

Provenance: [program audit](../data/programs/stony-brook-ai-data-science-specialization.json) · [adapter notes](../atlas/adapters/stony-brook-ai-data-science-specialization/NOTES.md).

Official evidence (audit-wide):

- [Requirements for the Major and Minor in Computer Science](https://www.stonybrook.edu/sb/bulletin/current-fall24/academicprograms/cse/degreesandrequirements.php) — Requirements for the Major and Minor in Computer Science; Artificial Intelligence and Data Science program entry
- [Majors, Minors & Degrees](https://www.stonybrook.edu/undergraduate-admissions/programs/index.php) — Computer Science BS: Artificial Intelligence and Data Science

### Tufts University — AI Development

`tufts-ai-development-minor` · partial · `source_conflict` · scope: minor

The checklist is public and reviewed; only the substantive core-alternative discrepancy keeps this minor partial.

Requirement gaps:

- Checklist requires CS 135 without the EE 140/CS 128 alternative permitted by the current program page; source precedence/acceptance remains unresolved.

Box viewer is public, ordinary fetch now returns 200, and the prior robot-parser issue was fixed; neither authentication nor blank/TBD annotation is a current academic inventory blocker.

**Next action:** Obtain explicit source precedence or accepted eligibility for EE140/CS128 versus required CS135 between the undated checklist and program page. Preserve the academic conflict; blank-versus-TBD form annotation and past Box transport issues are not inventory blockers.

Separate metadata: 32 course records; missing descriptions/prerequisite statements/public sites/syllabi = 32/27/32/32. Missing fields do not establish no prerequisites, no outcomes or no launch. Full metadata annotations and first-offered evidence are in JSON.

Provenance: [program audit](../data/programs/tufts-ai-development-minor.json) · [adapter notes](../atlas/adapters/tufts-ai-development-minor/NOTES.md).

Official evidence (audit-wide):

- [Minor in AI Development](https://engineering.tufts.edu/cs/current-students/undergraduate/minor-ai-development) — Full local program section: required courses, electives, topic restrictions, eligibility and published policy statements
- [Programs and Courses — Undergraduate Programs](https://ai.tufts.edu/ai-tufts/programs-and-courses) — Official undergraduate directory or catalog context
- [Student Forms — undergraduate minor checklists](https://engineering.tufts.edu/cs/current-students/undergraduate/student-forms) — Minor in the Application of AI and Minor in AI Development checklist links
- 2 additional audit sources, with exact URLs and locators, in this program’s JSON entry.

### Tulane University of Louisiana — Artificial Intelligence (AI) Literacy

`tulane-ai-literacy-minor` · partial · `mixed` · scope: minor

The source amounts need institutional interpretation; remaining local and host-school applicability rules are unreviewed, not blocked.

Requirement gaps:

- Clarify four-credit CMPS 1500 allocation within the six-credit problem-solving group and published 15-credit total
- Minor declaration procedure and any additional non-SSE host-school restrictions not yet verified

**Next action:** Clarify how four-credit CMPS1500 and zero-credit CMPS1501 fit the six-credit problem-solving group/15-credit total; verify Literacy declaration and any non-SSE student restrictions without importing SSE-only rules universally.

Separate metadata: 14 course records; missing descriptions/prerequisite statements/public sites/syllabi = 14/13/14/14. Missing fields do not establish no prerequisites, no outcomes or no launch. Full metadata annotations and first-offered evidence are in JSON.

Provenance: [program audit](../data/programs/tulane-ai-literacy-minor.json) · [adapter notes](../atlas/adapters/tulane-ai-literacy-minor/NOTES.md).

Official evidence (audit-wide):

- [Artificial Intelligence (AI) Literacy Minor](https://catalog.tulane.edu/newcomb-tulane/ai-literacy-minor/) — Overview; Requirements table, equivalent-course options and overlap footnote
- [Newcomb-Tulane College catalog policies](https://catalog.tulane.edu/newcomb-tulane/) — Minor Component; Undergraduate Certificates; S/U Grading Option; Credit Expiration; Transfer Credit
- [School of Science and Engineering catalog policies](https://catalog.tulane.edu/science-engineering/) — Undergraduate Programs; Second Majors, Minors, and Certificates
- 1 additional audit sources, with exact URLs and locators, in this program’s JSON entry.

### University of California, Merced — Artificial Intelligence

`uc-merced-ai-bs` · pending · `access_barrier` · scope: degree

The current requirement-source gap has a documented retrieval or access condition; this is not an assertion of program absence or a university-wide denial.

Requirement gaps:

- No reviewed current course/choice inventory or completion-policy map for the whole represented degree and university/college rules.

Access evidence (`http_denial_url_unrecorded`): Prior notes report catalog HTTP 403, but the exact failed catalog URL was not retained. Identity URLs are not substitutes for the unknown failed endpoint. Exact failed endpoint is not retained here; do not substitute the identity URL or guess one.

**Next action:** Recover the actual failed catalog link from current official navigation/provenance before any retry; do not guess an endpoint. Obtain permitted current requirements for this exact degree/emphasis and preserve the current identity-only state until reviewed.

Separate metadata: 0 course records; missing descriptions/prerequisite statements/public sites/syllabi = 0/0/0/0. Missing fields do not establish no prerequisites, no outcomes or no launch. Full metadata annotations and first-offered evidence are in JSON.

Provenance: [program audit](../data/programs/uc-merced-ai-bs.json) · [adapter notes](../atlas/adapters/uc-merced-ai-bs/NOTES.md).

Official evidence (audit-wide):

- [Artificial Intelligence, B.S. | University of California, Merced](https://www.ucmerced.edu/majors-and-minors/artificial-intelligence-bs) — Program heading and local award or specialization section

### University of California, Merced — Computer Science and Engineering — Artificial Intelligence Emphasis

`uc-merced-cse-ai-emphasis` · pending · `access_barrier` · scope: concentration

The current requirement-source gap has a documented retrieval or access condition; this is not an assertion of program absence or a university-wide denial.

Requirement gaps:

- No reviewed current course/choice inventory or completion-policy map for the local concentration requirements and eligibility, not the whole parent degree.

Access evidence (`http_denial_url_unrecorded`): Prior notes report catalog HTTP 403, but the exact failed catalog URL was not retained. Identity URLs are not substitutes for the unknown failed endpoint. Exact failed endpoint is not retained here; do not substitute the identity URL or guess one.

**Next action:** Recover the actual failed catalog link from current official navigation/provenance before any retry; do not guess an endpoint. Obtain permitted current requirements for this exact degree/emphasis and preserve the current identity-only state until reviewed.

Separate metadata: 0 course records; missing descriptions/prerequisite statements/public sites/syllabi = 0/0/0/0. Missing fields do not establish no prerequisites, no outcomes or no launch. Full metadata annotations and first-offered evidence are in JSON.

Provenance: [program audit](../data/programs/uc-merced-cse-ai-emphasis.json) · [adapter notes](../atlas/adapters/uc-merced-cse-ai-emphasis/NOTES.md).

Official evidence (audit-wide):

- [Majors, Minors & Programs](https://admissions.ucmerced.edu/academics/majors-minors) — Program heading and local award or specialization section

### University of California, Santa Barbara — Artificial Intelligence

`ucsb-ai-bs` · partial · `mixed` · scope: degree

Readable webpage and worksheet disagree, and approved lists/degree policies are missing; no access-denial claim is supported.

Requirement gaps:

- CMPSC 41: webpage four units versus worksheet five; worksheet sample plan returns to four.
- Upper-division subtotal 81 on worksheet does not reconcile with listed rows or webpage 36 core + 36 electives.
- Science List A/B approved lists unavailable on inspected pages; worksheet List B allocation blank.
- Capstone course, full college policies and ambiguous worksheet department wording need clarification.

**Next action:** Reconcile CMPSC41 credits and upper-division subtotal between webpage/worksheet; obtain Science ListA/B, capstone definition and full college policies. Retain announcement versus verified enrollment distinction separately.

Separate metadata: 60 course records; missing descriptions/prerequisite statements/public sites/syllabi = 60/60/60/60. Missing fields do not establish no prerequisites, no outcomes or no launch. Full metadata annotations and first-offered evidence are in JSON.

Provenance: [program audit](../data/programs/ucsb-ai-bs.json) · [adapter notes](../atlas/adapters/ucsb-ai-bs/NOTES.md).

Official evidence (audit-wide):

- [Curriculum — Bachelor of Science in Artificial Intelligence](https://ai.cs.ucsb.edu/curriculum) — Preparation table, Core Areas and unit breakdown
- [Artificial Intelligence 2026–27](https://ai.cs.ucsb.edu/sites/default/files/2026-04/AI%20major%20rqmnts_4.10%20(1).pdf) — Page 1: major worksheet; page 2: illustrative plan

### University at Buffalo–SUNY — AI and Geospatial Analytics

`university-at-buffalo-suny-ai-and-geospatial-analytics-bs-degree` · partial · `access_barrier` · scope: degree

The current requirement-source gap has a documented retrieval or access condition; this is not an assertion of program absence or a university-wide denial.

Requirement gaps:

- Exact course inventory and approved choice pools
- Credit total and degree-specific selection rules
- Prerequisites, admission, grade, residency and overlap policies
- University and college degreewide requirements

Access evidence (`robots_transport_failure`): Shared Buffalo catalog-host robots retrieval failed with ConnectError; the indexed Language Technology catalog page also could not be opened. This is inherited host-level evidence, not a fresh denial at every concrete program URL. Exact failed endpoint is not retained here; do not substitute the identity URL or guess one.

**Next action:** Use the recorded official requirement link only when normally readable, or obtain independently authoritative public requirements/institutional clarification. Preserve the recorded access condition; do not bypass it. Then map this represented award’s exact pools, choices and completion rules.

Separate metadata: 0 course records; missing descriptions/prerequisite statements/public sites/syllabi = 0/0/0/0. Missing fields do not establish no prerequisites, no outcomes or no launch. Full metadata annotations and first-offered evidence are in JSON.

Provenance: [program audit](../data/programs/university-at-buffalo-suny-ai-and-geospatial-analytics-bs-degree.json) · [adapter notes](../atlas/adapters/university-at-buffalo-suny-ai-and-geospatial-analytics-bs-degree/NOTES.md).

Official evidence (audit-wide):

- [AI and Society — College of Arts and Sciences](https://arts-sciences.buffalo.edu/college/departments-and-programs/social-sciences/ai-society.html) — Named undergraduate program entry: AI and Geospatial Analytics; award/type: BS / degree
- [AI and Geospatial Analytics](https://www.buffalo.edu/undergrad-programs/ai-and-geospatial-analytics.html) — Program overview; curriculum summary; learning and career sections
- [AI and Society — Academics](https://engineering.buffalo.edu/ai-society/academics.html) — Based in AI and its Societal Impacts; Current AI+X Programs / Majors

### University at Buffalo–SUNY — AI and Language and Intercultural Competence

`university-at-buffalo-suny-ai-and-language-and-intercultural-competence-bs-degree` · partial · `access_barrier` · scope: degree

The current requirement-source gap has a documented retrieval or access condition; this is not an assertion of program absence or a university-wide denial.

Requirement gaps:

- Exact course inventory and approved choice pools
- Credit total and degree-specific selection rules
- Prerequisites, admission, grade, residency and overlap policies
- University and college degreewide requirements

Access evidence (`robots_transport_failure`): Shared Buffalo catalog-host robots retrieval failed with ConnectError; the indexed Language Technology catalog page also could not be opened. This is inherited host-level evidence, not a fresh denial at every concrete program URL. Exact failed endpoint is not retained here; do not substitute the identity URL or guess one.

**Next action:** Use the recorded official requirement link only when normally readable, or obtain independently authoritative public requirements/institutional clarification. Preserve the recorded access condition; do not bypass it. Then map this represented award’s exact pools, choices and completion rules.

Separate metadata: 0 course records; missing descriptions/prerequisite statements/public sites/syllabi = 0/0/0/0. Missing fields do not establish no prerequisites, no outcomes or no launch. Full metadata annotations and first-offered evidence are in JSON.

Provenance: [program audit](../data/programs/university-at-buffalo-suny-ai-and-language-and-intercultural-competence-bs-degree.json) · [adapter notes](../atlas/adapters/university-at-buffalo-suny-ai-and-language-and-intercultural-competence-bs-degree/NOTES.md).

Official evidence (audit-wide):

- [AI and Society — College of Arts and Sciences](https://arts-sciences.buffalo.edu/college/departments-and-programs/social-sciences/ai-society.html) — Named undergraduate program entry: AI and Language and Intercultural Competence; award/type: BS / degree
- [AI and Language and Intercultural Competence](https://www.buffalo.edu/undergrad-programs/ai-and-language-and-intercultural-competence.html) — Program overview; curriculum summary; learning and career sections
- [AI and Society — Academics](https://engineering.buffalo.edu/ai-society/academics.html) — Based in AI and its Societal Impacts; Current AI+X Programs / Majors

### University at Buffalo–SUNY — AI and Language Technology

`university-at-buffalo-suny-ai-and-language-technology-bs-degree` · partial · `access_barrier` · scope: degree

The current requirement-source gap has a documented retrieval or access condition; this is not an assertion of program absence or a university-wide denial.

Requirement gaps:

- Exact course inventory and approved choice pools
- Credit total and degree-specific selection rules
- Prerequisites, admission, grade, residency and overlap policies
- University and college degreewide requirements

Access evidence (`robots_transport_failure`): Shared Buffalo catalog-host robots retrieval failed with ConnectError; the indexed Language Technology catalog page also could not be opened. This is inherited host-level evidence, not a fresh denial at every concrete program URL. Exact failed endpoint is not retained here; do not substitute the identity URL or guess one.

**Next action:** Use the recorded official requirement link only when normally readable, or obtain independently authoritative public requirements/institutional clarification. Preserve the recorded access condition; do not bypass it. Then map this represented award’s exact pools, choices and completion rules.

Separate metadata: 0 course records; missing descriptions/prerequisite statements/public sites/syllabi = 0/0/0/0. Missing fields do not establish no prerequisites, no outcomes or no launch. Full metadata annotations and first-offered evidence are in JSON.

Provenance: [program audit](../data/programs/university-at-buffalo-suny-ai-and-language-technology-bs-degree.json) · [adapter notes](../atlas/adapters/university-at-buffalo-suny-ai-and-language-technology-bs-degree/NOTES.md).

Official evidence (audit-wide):

- [AI and Society — College of Arts and Sciences](https://arts-sciences.buffalo.edu/college/departments-and-programs/social-sciences/ai-society.html) — Named undergraduate program entry: AI and Language Technology; award/type: BS / degree
- [AI and Language Technology](https://www.buffalo.edu/undergrad-programs/ai-and-language-technology.html) — Program overview; curriculum summary; learning and career sections
- [AI and Society — Academics](https://engineering.buffalo.edu/ai-society/academics.html) — Based in AI and its Societal Impacts; Current AI+X Programs / Majors

### University at Buffalo–SUNY — AI and Logic and Ontology

`university-at-buffalo-suny-ai-and-logic-and-ontology-bs-degree` · partial · `access_barrier` · scope: degree

The current requirement-source gap has a documented retrieval or access condition; this is not an assertion of program absence or a university-wide denial.

Requirement gaps:

- Exact course inventory and approved choice pools
- Credit total and degree-specific selection rules
- Prerequisites, admission, grade, residency and overlap policies
- University and college degreewide requirements

Access evidence (`robots_transport_failure`): Shared Buffalo catalog-host robots retrieval failed with ConnectError; the indexed Language Technology catalog page also could not be opened. This is inherited host-level evidence, not a fresh denial at every concrete program URL. Exact failed endpoint is not retained here; do not substitute the identity URL or guess one.

**Next action:** Use the recorded official requirement link only when normally readable, or obtain independently authoritative public requirements/institutional clarification. Preserve the recorded access condition; do not bypass it. Then map this represented award’s exact pools, choices and completion rules.

Separate metadata: 0 course records; missing descriptions/prerequisite statements/public sites/syllabi = 0/0/0/0. Missing fields do not establish no prerequisites, no outcomes or no launch. Full metadata annotations and first-offered evidence are in JSON.

Provenance: [program audit](../data/programs/university-at-buffalo-suny-ai-and-logic-and-ontology-bs-degree.json) · [adapter notes](../atlas/adapters/university-at-buffalo-suny-ai-and-logic-and-ontology-bs-degree/NOTES.md).

Official evidence (audit-wide):

- [AI and Society — College of Arts and Sciences](https://arts-sciences.buffalo.edu/college/departments-and-programs/social-sciences/ai-society.html) — Named undergraduate program entry: AI and Logic and Ontology; award/type: BS / degree
- [AI and Logic and Ontology](https://www.buffalo.edu/undergrad-programs/ai-and-logic-and-ontology.html) — Program overview; curriculum summary; learning and career sections
- [AI and Society — Academics](https://engineering.buffalo.edu/ai-society/academics.html) — Based in AI and its Societal Impacts; Current AI+X Programs / Majors

### University at Buffalo–SUNY — AI and Philosophy, Politics and Economics

`university-at-buffalo-suny-ai-and-philosophy-politics-economics-bs-degree` · partial · `access_barrier` · scope: degree

The current requirement-source gap has a documented retrieval or access condition; this is not an assertion of program absence or a university-wide denial.

Requirement gaps:

- Exact course inventory and approved choice pools
- Credit total and degree-specific selection rules
- Prerequisites, admission, grade, residency and overlap policies
- University and college degreewide requirements

Access evidence (`unreadable_http_response`): This exact PPE catalog URL passed robots/pacing but returned HTTP 202 without readable content; this later observation is more precise than earlier family transport failure. Exact failed endpoint: <https://catalogs.buffalo.edu/preview_program.php?catoid=21&poid=9576&returnto=1177>.

**Next action:** Use the recorded official requirement link only when normally readable, or obtain independently authoritative public requirements/institutional clarification. Preserve the recorded access condition; do not bypass it. Then map this represented award’s exact pools, choices and completion rules.

Separate metadata: 0 course records; missing descriptions/prerequisite statements/public sites/syllabi = 0/0/0/0. Missing fields do not establish no prerequisites, no outcomes or no launch. Full metadata annotations and first-offered evidence are in JSON.

Provenance: [program audit](../data/programs/university-at-buffalo-suny-ai-and-philosophy-politics-economics-bs-degree.json) · [adapter notes](../atlas/adapters/university-at-buffalo-suny-ai-and-philosophy-politics-economics-bs-degree/NOTES.md).

Official evidence (audit-wide):

- [BS in AI and PPE](https://arts-sciences.buffalo.edu/philosophy-politics-economics/undergraduate/bs.html) — BS in AI and PPE heading; full degree title in opening paragraph; What you will learn
- [AI and Philosophy, Politics and Economics](https://www.buffalo.edu/undergrad-programs/ai-and-politics-philosophy-economics.html) — Program heading, College/Department labels, What will I learn?, career section
- [AI and Society — Academics](https://engineering.buffalo.edu/ai-society/academics.html) — Based in AI and its Societal Impacts; Current AI+X Programs / Majors

### University at Buffalo–SUNY — AI and Policy Analysis

`university-at-buffalo-suny-ai-and-policy-analysis-bs-degree` · partial · `access_barrier` · scope: degree

The current requirement-source gap has a documented retrieval or access condition; this is not an assertion of program absence or a university-wide denial.

Requirement gaps:

- Exact course inventory and approved choice pools
- Credit total and degree-specific selection rules
- Prerequisites, admission, grade, residency and overlap policies
- University and college degreewide requirements

Access evidence (`robots_transport_failure`): Shared Buffalo catalog-host robots retrieval failed with ConnectError; the indexed Language Technology catalog page also could not be opened. This is inherited host-level evidence, not a fresh denial at every concrete program URL. Exact failed endpoint is not retained here; do not substitute the identity URL or guess one.

**Next action:** Use the recorded official requirement link only when normally readable, or obtain independently authoritative public requirements/institutional clarification. Preserve the recorded access condition; do not bypass it. Then map this represented award’s exact pools, choices and completion rules.

Separate metadata: 0 course records; missing descriptions/prerequisite statements/public sites/syllabi = 0/0/0/0. Missing fields do not establish no prerequisites, no outcomes or no launch. Full metadata annotations and first-offered evidence are in JSON.

Provenance: [program audit](../data/programs/university-at-buffalo-suny-ai-and-policy-analysis-bs-degree.json) · [adapter notes](../atlas/adapters/university-at-buffalo-suny-ai-and-policy-analysis-bs-degree/NOTES.md).

Official evidence (audit-wide):

- [AI and Society — College of Arts and Sciences](https://arts-sciences.buffalo.edu/college/departments-and-programs/social-sciences/ai-society.html) — Named undergraduate program entry: AI and Policy Analysis; award/type: BS / degree
- [AI and Policy Analysis](https://www.buffalo.edu/undergrad-programs/ai-and-policy-analysis.html) — Program overview; curriculum summary; learning and career sections
- [AI and Society — Academics](https://engineering.buffalo.edu/ai-society/academics.html) — Based in AI and its Societal Impacts; Current AI+X Programs / Majors

### University at Buffalo–SUNY — AI and Quantitative Economics

`university-at-buffalo-suny-ai-and-quantitative-economics-bs-degree` · partial · `access_barrier` · scope: degree

The current requirement-source gap has a documented retrieval or access condition; this is not an assertion of program absence or a university-wide denial.

Requirement gaps:

- Exact course inventory and approved choice pools
- Credit total and degree-specific selection rules
- Prerequisites, admission, grade, residency and overlap policies
- University and college degreewide requirements

Access evidence (`robots_transport_failure`): Shared Buffalo catalog-host robots retrieval failed with ConnectError; the indexed Language Technology catalog page also could not be opened. This is inherited host-level evidence, not a fresh denial at every concrete program URL. Exact failed endpoint is not retained here; do not substitute the identity URL or guess one.

**Next action:** Use the recorded official requirement link only when normally readable, or obtain independently authoritative public requirements/institutional clarification. Preserve the recorded access condition; do not bypass it. Then map this represented award’s exact pools, choices and completion rules.

Separate metadata: 0 course records; missing descriptions/prerequisite statements/public sites/syllabi = 0/0/0/0. Missing fields do not establish no prerequisites, no outcomes or no launch. Full metadata annotations and first-offered evidence are in JSON.

Provenance: [program audit](../data/programs/university-at-buffalo-suny-ai-and-quantitative-economics-bs-degree.json) · [adapter notes](../atlas/adapters/university-at-buffalo-suny-ai-and-quantitative-economics-bs-degree/NOTES.md).

Official evidence (audit-wide):

- [AI and Society — College of Arts and Sciences](https://arts-sciences.buffalo.edu/college/departments-and-programs/social-sciences/ai-society.html) — Named undergraduate program entry: AI and Quantitative Economics; award/type: BS / degree
- [AI and Quantitative Economics](https://www.buffalo.edu/undergrad-programs/ai-and-quantitative-economics.html) — Program overview; curriculum summary; learning and career sections
- [AI and Society — Academics](https://engineering.buffalo.edu/ai-society/academics.html) — Based in AI and its Societal Impacts; Current AI+X Programs / Majors

### University at Buffalo–SUNY — AI and Responsible Communication

`university-at-buffalo-suny-ai-and-responsible-communication-bs-degree` · partial · `access_barrier` · scope: degree

The current requirement-source gap has a documented retrieval or access condition; this is not an assertion of program absence or a university-wide denial.

Requirement gaps:

- Exact course inventory and approved choice pools
- Credit total and degree-specific selection rules
- Prerequisites, admission, grade, residency and overlap policies
- University and college degreewide requirements

Access evidence (`robots_transport_failure`): Shared Buffalo catalog-host robots retrieval failed with ConnectError; the indexed Language Technology catalog page also could not be opened. This is inherited host-level evidence, not a fresh denial at every concrete program URL. Exact failed endpoint is not retained here; do not substitute the identity URL or guess one.

**Next action:** Use the recorded official requirement link only when normally readable, or obtain independently authoritative public requirements/institutional clarification. Preserve the recorded access condition; do not bypass it. Then map this represented award’s exact pools, choices and completion rules.

Separate metadata: 0 course records; missing descriptions/prerequisite statements/public sites/syllabi = 0/0/0/0. Missing fields do not establish no prerequisites, no outcomes or no launch. Full metadata annotations and first-offered evidence are in JSON.

Provenance: [program audit](../data/programs/university-at-buffalo-suny-ai-and-responsible-communication-bs-degree.json) · [adapter notes](../atlas/adapters/university-at-buffalo-suny-ai-and-responsible-communication-bs-degree/NOTES.md).

Official evidence (audit-wide):

- [AI and Society — College of Arts and Sciences](https://arts-sciences.buffalo.edu/college/departments-and-programs/social-sciences/ai-society.html) — Named undergraduate program entry: AI and Responsible Communication; award/type: BS / degree
- [AI and Responsible Communication](https://www.buffalo.edu/undergrad-programs/ai-and-responsible-communication.html) — Program overview; curriculum summary; learning and career sections
- [AI and Society — Academics](https://engineering.buffalo.edu/ai-society/academics.html) — Based in AI and its Societal Impacts; Current AI+X Programs / Majors

### University at Buffalo–SUNY — AI Ethics

`university-at-buffalo-suny-ai-ethics-minor-minor` · partial · `access_barrier` · scope: minor

The current requirement-source gap has a documented retrieval or access condition; this is not an assertion of program absence or a university-wide denial.

Requirement gaps:

- Exact course inventory and approved choice pools
- Credit total and degree-specific selection rules
- Prerequisites, admission, grade, residency and overlap policies

Access evidence (`robots_transport_failure`): Shared Buffalo catalog-host robots retrieval failed with ConnectError; the indexed Language Technology catalog page also could not be opened. This is inherited host-level evidence, not a fresh denial at every concrete program URL. Exact failed endpoint is not retained here; do not substitute the identity URL or guess one.

**Next action:** Use the recorded official requirement link only when normally readable, or obtain independently authoritative public requirements/institutional clarification. Preserve the recorded access condition; do not bypass it. Then map this represented award’s exact pools, choices and completion rules.

Separate metadata: 0 course records; missing descriptions/prerequisite statements/public sites/syllabi = 0/0/0/0. Missing fields do not establish no prerequisites, no outcomes or no launch. Full metadata annotations and first-offered evidence are in JSON.

Provenance: [program audit](../data/programs/university-at-buffalo-suny-ai-ethics-minor-minor.json) · [adapter notes](../atlas/adapters/university-at-buffalo-suny-ai-ethics-minor-minor/NOTES.md).

Official evidence (audit-wide):

- [AI and Society — College of Arts and Sciences](https://arts-sciences.buffalo.edu/college/departments-and-programs/social-sciences/ai-society.html) — Named undergraduate program entry: AI Ethics; award/type: minor / minor
- [Minor in AI Ethics](https://www.buffalo.edu/cas/philosophy/undergraduate/minor-ai-ethics.html) — Program overview; curriculum summary; learning and career sections

### University at Buffalo–SUNY — Artificial Intelligence, Crime and Society

`university-at-buffalo-suny-artificial-intelligence-crime-and-society-minor-minor` · partial · `access_barrier` · scope: minor

The current requirement-source gap has a documented retrieval or access condition; this is not an assertion of program absence or a university-wide denial.

Requirement gaps:

- Exact course inventory and approved choice pools
- Credit total and degree-specific selection rules
- Prerequisites, admission, grade, residency and overlap policies

Access evidence (`robots_transport_failure`): Shared Buffalo catalog-host robots retrieval failed with ConnectError; the indexed Language Technology catalog page also could not be opened. This is inherited host-level evidence, not a fresh denial at every concrete program URL. Exact failed endpoint is not retained here; do not substitute the identity URL or guess one.

**Next action:** Use the recorded official requirement link only when normally readable, or obtain independently authoritative public requirements/institutional clarification. Preserve the recorded access condition; do not bypass it. Then map this represented award’s exact pools, choices and completion rules.

Separate metadata: 0 course records; missing descriptions/prerequisite statements/public sites/syllabi = 0/0/0/0. Missing fields do not establish no prerequisites, no outcomes or no launch. Full metadata annotations and first-offered evidence are in JSON.

Provenance: [program audit](../data/programs/university-at-buffalo-suny-artificial-intelligence-crime-and-society-minor-minor.json) · [adapter notes](../atlas/adapters/university-at-buffalo-suny-artificial-intelligence-crime-and-society-minor-minor/NOTES.md).

Official evidence (audit-wide):

- [AI and Society — College of Arts and Sciences](https://arts-sciences.buffalo.edu/college/departments-and-programs/social-sciences/ai-society.html) — Named undergraduate program entry: Artificial Intelligence, Crime and Society; award/type: minor / minor
- [Minor in Artificial Intelligence, Crime and Society](https://arts-sciences.buffalo.edu/sociology-criminology/undergraduate/ai-crime-society.html) — Program overview; curriculum summary; learning and career sections

### University of California San Diego — Artificial Intelligence

`university-of-california-san-diego-artificial-intelligence-bs-degree` · partial · `mixed` · scope: degree

Both public sources were read; their elective pools differ and degree-wide policies remain unreviewed.

Requirement gaps:

- Full CSE breadth-tag mapping and university/college graduation requirements unreviewed.
- Catalog and tentative 2026 department elective lists differ; applicability needs confirmation.

**Next action:** Resolve catalog versus tentative August 2026 elective applicability, then map CSE breadth tags and university/college completion rules for the represented BS. Do not union editions or treat direct-admit scope as a launch date.

Separate metadata: 153 course records; missing descriptions/prerequisite statements/public sites/syllabi = 147/147/153/153. Missing fields do not establish no prerequisites, no outcomes or no launch. Full metadata annotations and first-offered evidence are in JSON.

Provenance: [program audit](../data/programs/university-of-california-san-diego-artificial-intelligence-bs-degree.json) · [adapter notes](../atlas/adapters/university-of-california-san-diego-artificial-intelligence-bs-degree/NOTES.md).

Official evidence (audit-wide):

- [Computer Science and Engineering undergraduate curriculum](https://catalog.ucsd.edu/curric/CSE-ug.html) — BS Artificial Intelligence Program through its scheduling notes
- [B.S. Artificial Intelligence (CSE-BS-004)](https://cse.ucsd.edu/undergraduate/bs-artificial-intelligence-cse-bs-004) — Updated August 3, 2026; tentative Fall 2026 curriculum and elective list

### University of Maryland, College Park — Artificial Intelligence: Computational Structures for AI Systems

`university-of-maryland-college-park-artificial-intelligence-computational-structures-for-ai-systems-bsai-degree` · partial · `mixed` · scope: degree

Accessible catalog contains a specialization-total discrepancy plus unreviewed degree-wide rules.

Requirement gaps:

- University-wide graduation/general education and linked college requirements remain unreviewed.
- Catalog AI Algorithms total conflicts with the 18-credit specialization rule.

**Next action:** Resolve AI Algorithms’ printed 12-credit subtotal against the 18-credit specialization requirement, then map all linked college/university graduation and GE rules.

Separate metadata: 85 course records; missing descriptions/prerequisite statements/public sites/syllabi = 85/85/85/85. Missing fields do not establish no prerequisites, no outcomes or no launch. Full metadata annotations and first-offered evidence are in JSON.

Provenance: [program audit](../data/programs/university-of-maryland-college-park-artificial-intelligence-computational-structures-for-ai-systems-bsai-degree.json) · [adapter notes](../atlas/adapters/university-of-maryland-college-park-artificial-intelligence-computational-structures-for-ai-systems-bsai-degree/NOTES.md).

Official evidence (audit-wide):

- [Artificial Intelligence: Computational Structures for AI Systems Major](https://academiccatalog.umd.edu/undergraduate/colleges-schools/computer-mathematical-natural-sciences/computer-science/artificial-intelligence-computational-structures-ai-systems-major/) — Requirements tab: all course tables and footnotes

### University of Maryland, College Park — Human-Centered Artificial Intelligence

`university-of-maryland-college-park-human-centered-ai-ba-degree` · partial · `accessible_unreviewed` · scope: degree

Current catalog major structure is mapped; university/college requirements remain unreviewed without a recorded access barrier.

Requirement gaps:

- University-wide graduation/general education and linked college requirements remain unreviewed.

**Next action:** Map linked Arts and Humanities/university GE and graduation rules while retaining each six-course specialization’s prerequisites and content approvals; do not convert open approvals into compulsory courses.

Separate metadata: 68 course records; missing descriptions/prerequisite statements/public sites/syllabi = 68/68/68/68. Missing fields do not establish no prerequisites, no outcomes or no launch. Full metadata annotations and first-offered evidence are in JSON.

Provenance: [program audit](../data/programs/university-of-maryland-college-park-human-centered-ai-ba-degree.json) · [adapter notes](../atlas/adapters/university-of-maryland-college-park-human-centered-ai-ba-degree/NOTES.md).

Official evidence (audit-wide):

- [Human-Centered Artificial Intelligence Major](https://academiccatalog.umd.edu/undergraduate/colleges-schools/arts-humanities/philosophy/human-centered-artificial-intelligence-major/) — Requirements tab: all course tables and footnotes

### University of Miami — Artificial Intelligence for Business Technology

`university-of-miami-artificial-intelligence-for-business-technology-minor-minor` · partial · `accessible_unreviewed` · scope: minor

The linked business policies and minor source are available; applicable policy and program prerequisite review is incomplete.

Requirement gaps:

- Full linked university residency/transfer and repeat/GPA policies remain unreviewed.
- Current course prerequisite structure has not been fully extracted.

**Next action:** Finish university/minor-applicable transfer, residence, repeat/GPA and Python/other program prerequisite eligibility review. Separate general course preparation metadata from any actual minor admission/completion condition.

Separate metadata: 15 course records; missing descriptions/prerequisite statements/public sites/syllabi = 15/15/15/15. Missing fields do not establish no prerequisites, no outcomes or no launch. Full metadata annotations and first-offered evidence are in JSON.

Provenance: [program audit](../data/programs/university-of-miami-artificial-intelligence-for-business-technology-minor-minor.json) · [adapter notes](../atlas/adapters/university-of-miami-artificial-intelligence-for-business-technology-minor-minor/NOTES.md).

Official evidence (audit-wide):

- [Artificial Intelligence for Business Technology](https://bulletin.miami.edu/undergraduate-academic-programs/business/business-technology/ai-for-business-technology-minor/) — Named undergraduate program entry: Artificial Intelligence for Business Technology; award/type: minor / minor
- [Artificial Intelligence for Business Technology — curriculum](https://bulletin.miami.edu/undergraduate-academic-programs/business/business-technology/ai-for-business-technology-minor/) — Course Requirements; Course List; Electives; How to Apply; eligibility and overlap notes
- [Miami Business academic policies](https://bulletin.miami.edu/undergraduate-academic-programs/business/) — External Transfer Admission; Repeat Rules; Residency and Graduation Requirements; Major and Minor Areas of Specialization

### University of Miami — Artificial Intelligence Technologies for Business

`university-of-miami-artificial-intelligence-technologies-for-business-other-degree` · partial · `accessible_unreviewed` · scope: degree

The actual curriculum table is mapped; degree-wide policy review remains unfinished with no documented requirement-source access barrier.

Requirement gaps:

- Full university and college general education, completion/residency, transfer and admission/progression policy audit remains unfinished.

**Next action:** Follow the linked university/college general education, admission/progression, transfer, residence and completion policies for this exact BA/BBA/BSBA pathway. Do not substitute Additional Major or sample-plan rules. Treat unit normalization separately.

Separate metadata: 43 course records; missing descriptions/prerequisite statements/public sites/syllabi = 43/43/43/43. Missing fields do not establish no prerequisites, no outcomes or no launch. Full metadata annotations and first-offered evidence are in JSON.

Credit normalization is a separate metadata task, even where the original audit listed it under unresolved requirements.

Provenance: [program audit](../data/programs/university-of-miami-artificial-intelligence-technologies-for-business-other-degree.json) · [adapter notes](../atlas/adapters/university-of-miami-artificial-intelligence-technologies-for-business-other-degree/NOTES.md).

Official evidence (audit-wide):

- [B.B.A. in Artificial Intelligence Technologies for Business](https://bulletin.miami.edu/undergraduate-academic-programs/business/business-technology/ai-tech-for-business-bba/) — Curriculum table and footnotes; Learning Outcomes; Additional Major section read separately from degree requirements

### University of Miami — Data Science and Artificial Intelligence

`university-of-miami-data-science-and-artificial-intelligence-ba-degree` · partial · `accessible_unreviewed` · scope: degree

The actual curriculum table is mapped; degree-wide policy review remains unfinished with no documented requirement-source access barrier.

Requirement gaps:

- Full university and college general education, completion/residency, transfer and admission/progression policy audit remains unfinished.

**Next action:** Follow the linked university/college general education, admission/progression, transfer, residence and completion policies for this exact BA/BBA/BSBA pathway. Do not substitute Additional Major or sample-plan rules. Treat unit normalization separately.

Separate metadata: 46 course records; missing descriptions/prerequisite statements/public sites/syllabi = 46/46/46/46. Missing fields do not establish no prerequisites, no outcomes or no launch. Full metadata annotations and first-offered evidence are in JSON.

Credit normalization is a separate metadata task, even where the original audit listed it under unresolved requirements.

Provenance: [program audit](../data/programs/university-of-miami-data-science-and-artificial-intelligence-ba-degree.json) · [adapter notes](../atlas/adapters/university-of-miami-data-science-and-artificial-intelligence-ba-degree/NOTES.md).

Official evidence (audit-wide):

- [B.A. in Data Science and Artificial Intelligence](https://bulletin.miami.edu/undergraduate-academic-programs/arts-sciences/computer-science/data-science-and-ai-ba/) — Curriculum table and footnotes; Learning Outcomes; Additional Major section read separately from degree requirements
- [College of Arts and Sciences requirements](https://bulletin.miami.edu/undergraduate-academic-programs/arts-sciences/) — Requirements for Graduation; BA/BS additional requirements; majors/minors; electives; Credit Only and Transfer Credit Hours

### University of Michigan–Ann Arbor — Human-Centered Artificial Intelligence

`university-of-michigan-ann-arbor-human-centered-artificial-intelligence-minor-minor` · pending · `access_barrier` · scope: minor

The current requirement-source gap has a documented retrieval or access condition; this is not an assertion of program absence or a university-wide denial.

Requirement gaps:

- No reviewed current course/choice inventory or completion-policy map for the local minor requirements and eligibility, not the whole parent degree.

Access evidence (`http_denial`): Named minor page returned HTTP 403 after robots check; collection stopped. Exact failed endpoint: <https://www.si.umich.edu/programs/undergraduate-minors/human-centered-artificial-intelligence>.

**Next action:** Use the recorded official requirement link only when normally readable, or obtain independently authoritative public requirements/institutional clarification. Preserve the recorded access condition; do not bypass it. Then map this represented award’s exact pools, choices and completion rules.

Separate metadata: 0 course records; missing descriptions/prerequisite statements/public sites/syllabi = 0/0/0/0. Missing fields do not establish no prerequisites, no outcomes or no launch. Full metadata annotations and first-offered evidence are in JSON.

Provenance: [program audit](../data/programs/university-of-michigan-ann-arbor-human-centered-artificial-intelligence-minor-minor.json) · [adapter notes](../atlas/adapters/university-of-michigan-ann-arbor-human-centered-artificial-intelligence-minor-minor/NOTES.md).

Official evidence (audit-wide):

- [Human-Centered Artificial Intelligence](https://www.si.umich.edu/programs/undergraduate-minors/human-centered-artificial-intelligence) — Named undergraduate program entry: Human-Centered Artificial Intelligence; award/type: minor / minor

### University of Notre Dame — AI Analytics in Business

`university-of-notre-dame-ai-analytics-in-business-minor-minor` · partial · `source_conflict` · scope: minor

Two readable curriculum sources differ and college/university pass/fail wording conflicts; unit normalization is already resolved.

Requirement gaps:

- Reconcile current Mendoza and 2026–2027 catalog elective pools, including whether six of nine elective hours must be ITAO.
- Resolve college first-minor-course pass/fail exception wording against the university code prohibiting pass/fail for program requirements; no exception is assumed.

**Next action:** Reconcile the current Class-of-2028+ Mendoza pool with the 2026–27 catalog, including six-of-nine ITAO hours, and resolve pass/fail exception applicability. Preserve source-specific pools and enrollment restrictions rather than merging freely.

Separate metadata: 38 course records; missing descriptions/prerequisite statements/public sites/syllabi = 34/32/38/38. Missing fields do not establish no prerequisites, no outcomes or no launch. Full metadata annotations and first-offered evidence are in JSON.

Provenance: [program audit](../data/programs/university-of-notre-dame-ai-analytics-in-business-minor-minor.json) · [adapter notes](../atlas/adapters/university-of-notre-dame-ai-analytics-in-business-minor-minor/NOTES.md).

Official evidence (audit-wide):

- [AI Analytics in Business](https://mendoza.nd.edu/undergraduate/ai-analytics-in-business/) — Named undergraduate program entry: AI Analytics in Business; award/type: minor / minor
- [AI Analytics in Business — curriculum](https://mendoza.nd.edu/undergraduate/ai-analytics-in-business/) — Course Requirements; Course List; Electives; How to Apply; eligibility and overlap notes
- [Mendoza undergraduate minors](https://mendoza.nd.edu/undergraduate/) — AI Analytics in Business card: Open To Mendoza College of Business Majors; 15 credit hours
- 6 additional audit sources, with exact URLs and locators, in this program’s JSON entry.

### University of South Florida — Artificial Intelligence

`university-of-south-florida-artificial-intelligence-bs-degree` · partial · `access_barrier` · scope: degree

The current requirement-source gap has a documented retrieval or access condition; this is not an assertion of program absence or a university-wide denial.

Requirement gaps:

- Definitive catalog retried with compliant 120-second pacing but returned HTTP 202; full curriculum remains unavailable through the fetcher.
- Major elective pool, credit requirements, GE/college/university policies and course prerequisites unreviewed.

Access evidence (`unreadable_http_response`): Compliant 120-second paced retry resolved the official shortlink to catalog HTTP 202. Former local pacing limit is resolved; unreadable server response remains. Exact failed endpoint: <https://catalog.usf.edu/preview_program.php?catoid=25&poid=13990>.

**Next action:** Use the recorded official requirement link only when normally readable, or obtain independently authoritative public requirements/institutional clarification. Preserve the recorded access condition; do not bypass it. Then map this represented award’s exact pools, choices and completion rules.

Separate metadata: 29 course records; missing descriptions/prerequisite statements/public sites/syllabi = 29/29/29/29. Missing fields do not establish no prerequisites, no outcomes or no launch. Full metadata annotations and first-offered evidence are in JSON.

Provenance: [program audit](../data/programs/university-of-south-florida-artificial-intelligence-bs-degree.json) · [adapter notes](../atlas/adapters/university-of-south-florida-artificial-intelligence-bs-degree/NOTES.md).

Official evidence (audit-wide):

- [Bellini Bachelor of Science Programs — Artificial Intelligence](https://www.usf.edu/ai-cybersecurity-computing/documents/brochures/bellini-ug-bsai.pdf) — Page 2: BSAI Four Year Plan; updated September 2026; enrolled-student account

### University of Southern California — Applied AI in Business

`university-of-southern-california-applied-ai-in-business-minor-minor` · partial · `access_barrier` · scope: minor

The current requirement-source gap has a documented retrieval or access condition; this is not an assertion of program absence or a university-wide denial.

Requirement gaps:

- Program-specific course inventory, total units and completion policies remain unverified: the linked catalog returned HTTP 202 after compliant 120-second pacing.
- Detailed major/emphasis overlap limits and eligibility exceptions need catalog or advisor-policy confirmation.

Access evidence (`unreadable_http_response`): Catalog returned HTTP 202 after compliant 120-second pacing; public web reader also failed. Search snippets are not promoted to requirements. Exact failed endpoint: <https://catalogue.usc.edu/preview_program.php?catoid=22&poid=32945&returnto=9453>.

**Next action:** Obtain normally readable catalog evidence for the exact minor inventory/total and detailed major-emphasis overlap exceptions; preserve the Marshall matrix’s restrictions and do not promote indexed16-unit/GPA snippets or common unique-unit minima.

Separate metadata: 0 course records; missing descriptions/prerequisite statements/public sites/syllabi = 0/0/0/0. Missing fields do not establish no prerequisites, no outcomes or no launch. Full metadata annotations and first-offered evidence are in JSON.

Provenance: [program audit](../data/programs/university-of-southern-california-applied-ai-in-business-minor-minor.json) · [adapter notes](../atlas/adapters/university-of-southern-california-applied-ai-in-business-minor-minor/NOTES.md).

Official evidence (audit-wide):

- [Applied AI in Business](https://www.marshall.usc.edu/news/usc-marshall-launches-applied-ai-and-business-minor) — Announcement dated August 5, 2026; Fall 2026 launch and curriculum aims
- [Marshall Minors — admission and eligibility](https://students.marshall.usc.edu/current-students/applying-marshall-current-usc-students/marshall-minors) — Admission paragraphs and 2026–2027 minor list
- [Which Marshall Minors Can I Add?](https://students.marshall.usc.edu/sites/default/files/2026-07/Marshall%20Minors%20List.pdf) — Three-page major/emphasis eligibility matrix; visually inspected

### Ursinus College — Artificial Intelligence

`ursinus-ai-minor` · partial · `institutional_clarification` · scope: minor

The catalog refers to normal overlap rules without establishing AI applicability, and a listed elective lacks a current description. Neither proves an access barrier or course absence.

Requirement gaps:

- Applicability and exact amount of the catalog’s referenced normal major/minor overlap limits to the AI minor remain unverified.
- CS-372 remains an explicitly listed elective without a located current course description; current availability/equivalence is unresolved.

**Next action:** Obtain the AI minor’s applicable normal overlap allowance and confirm current CS372 eligibility/equivalence from a department/registrar policy. Do not import numeric limits from unrelated majors/minors.

Separate metadata: 22 course records; missing descriptions/prerequisite statements/public sites/syllabi = 1/7/22/22. Missing fields do not establish no prerequisites, no outcomes or no launch. Full metadata annotations and first-offered evidence are in JSON.

Provenance: [program audit](../data/programs/ursinus-ai-minor.json) · [adapter notes](../atlas/adapters/ursinus-ai-minor/NOTES.md).

Official evidence (audit-wide):

- [Artificial Intelligence](https://www.ursinus.edu/academics/artificial-intelligence/) — Interdisciplinary minor; human impact
- [AI Courses and Requirements](https://www.ursinus.edu/academics/artificial-intelligence/courses-requirements/) — Requirements for Artificial Intelligence Minor; CS-357 course description
- [Ursinus College Catalog 2026–2027](https://www.ursinus.edu/live/files/5614-catalog-2026) — Printed pp. 7–14, 21–29, 57, 67–68, 124–128, 261–277, 343–345; AI requirements and relevant course descriptions/policies
- 4 additional audit sources, with exact URLs and locators, in this program’s JSON entry.

### University of Virginia — Artificial Intelligence

`uva-bacs-ai-concentration` · partial · `access_barrier` · scope: concentration

The current requirement-source gap has a documented retrieval or access condition; this is not an assertion of program absence or a university-wide denial.

Requirement gaps:

- Linked registrar program page could not be inspected; additional catalog constraints or discrepancies remain unverified.

Access evidence (`http_denial_or_unavailable`): Linked registrar program page returned403/unavailable; official advising page is normally readable. Department context was readable via web reader despite local robots preflight 403. Exact failed endpoint: <https://records.ureg.virginia.edu/preview_program.php?catoid=72&poid=11700>.

**Next action:** Obtain readable current registrar constraints and reconcile them with the mapped BACS-specific advising inventory; retain its manual-override and topic rules without borrowing BSCS restrictions.

Separate metadata: 15 course records; missing descriptions/prerequisite statements/public sites/syllabi = 15/15/15/15. Missing fields do not establish no prerequisites, no outcomes or no launch. Full metadata annotations and first-offered evidence are in JSON.

Provenance: [program audit](../data/programs/uva-bacs-ai-concentration.json) · [adapter notes](../atlas/adapters/uva-bacs-ai-concentration/NOTES.md).

Official evidence (audit-wide):

- [Artificial Intelligence Concentration — BACS AI Concentration](https://uvacsadvising.org/ai-concentration.html) — Full local program section: required courses, electives, topic restrictions, eligibility and published policy statements
- [BS in Computer Science — official advising-site link](https://engineering.virginia.edu/department/computer-science/academics/undergraduate-programs/bs-computer-science) — Official undergraduate directory or catalog context
- [CS Undergraduate Artificial Intelligence Concentrations](https://engineering.virginia.edu/department/computer-science/cs-undergraduate-artificial-intelligence-concentrations) — About the AI Concentration; BS/BA concentration sections

### University of Virginia — Artificial Intelligence

`uva-bscs-ai-concentration` · partial · `access_barrier` · scope: concentration

The current requirement-source gap has a documented retrieval or access condition; this is not an assertion of program absence or a university-wide denial.

Requirement gaps:

- Linked registrar program page could not be inspected; additional catalog constraints or discrepancies remain unverified.

Access evidence (`http_denial_or_unavailable`): Linked registrar program page returned403/unavailable; official advising page is normally readable. Department context was readable via web reader despite local robots preflight 403. Exact failed endpoint: <https://records.ureg.virginia.edu/preview_program.php?catoid=72&poid=11700>.

**Next action:** Obtain readable current registrar constraints and reconcile them with the mapped BSCS-specific advising inventory; retain BS topic limits without assuming the BACS choices apply.

Separate metadata: 16 course records; missing descriptions/prerequisite statements/public sites/syllabi = 16/16/16/16. Missing fields do not establish no prerequisites, no outcomes or no launch. Full metadata annotations and first-offered evidence are in JSON.

Provenance: [program audit](../data/programs/uva-bscs-ai-concentration.json) · [adapter notes](../atlas/adapters/uva-bscs-ai-concentration/NOTES.md).

Official evidence (audit-wide):

- [Artificial Intelligence Concentration — BSCS AI Concentration](https://uvacsadvising.org/ai-concentration.html) — Full local program section: required courses, electives, topic restrictions, eligibility and published policy statements
- [BS in Computer Science — official advising-site link](https://engineering.virginia.edu/department/computer-science/academics/undergraduate-programs/bs-computer-science) — Official undergraduate directory or catalog context
- [CS Undergraduate Artificial Intelligence Concentrations](https://engineering.virginia.edu/department/computer-science/cs-undergraduate-artificial-intelligence-concentrations) — About the AI Concentration; BS/BA concentration sections

### Villanova University — Analytics & Artificial Intelligence

`villanova-analytics-ai-co-major` · partial · `institutional_clarification` · scope: additional_major

The public modal is empty; it does not establish an access denial or justify borrowing the distinct minor’s pool.

Requirement gaps:

- Empty Other Approved Electives entry has no verified inventory or approval rule.

**Next action:** Obtain the co-major’s Other Approved Electives inventory or explicit approval rule; preserve Class-of-2029+ scope and graduate substitution conditions.

Separate metadata: 14 course records; missing descriptions/prerequisite statements/public sites/syllabi = 12/12/14/14. Missing fields do not establish no prerequisites, no outcomes or no launch. Full metadata annotations and first-offered evidence are in JSON.

Provenance: [program audit](../data/programs/villanova-analytics-ai-co-major.json) · [adapter notes](../atlas/adapters/villanova-analytics-ai-co-major/NOTES.md).

Official evidence (audit-wide):

- [Analytics & Artificial Intelligence Co-Major](https://live-villanova-catalog.cleancatalog.io/analytics-artificial-intelligence/analytics-artificial-intelligence-comajor) — Course Requirements; all course groups and subsequent Note/graduate-substitution paragraphs
- [MGT 3170: Data Mining and AI](https://live-villanova-catalog.cleancatalog.io/management/mgt-3170) — Course description, credits and Prerequisites
- [MGT 4170: Decision Analytics & AI](https://live-villanova-catalog.cleancatalog.io/management/mgt-4170) — Course description, credits and Prerequisites

### Virginia Tech — Artificial Intelligence (AI)

`virginia-tech-artificial-intelligence-ai-minor-minor` · partial · `access_barrier` · scope: minor

The current requirement-source gap has a documented retrieval or access condition; this is not an assertion of program absence or a university-wide denial.

Requirement gaps:

- Catalog course and study-track inventory, credits, alternatives and completion constraints remain unreviewed because catalog access was unavailable.
- Minor grade, overlap, residency and transfer policies are not verified.

Access evidence (`robots_preflight_unreadable`): Catalog robots policy could not be obtained (HTTP202), so no catalog body was accessed. Department/minor declaration sources remain readable. Exact failed endpoint is not retained here; do not substitute the identity URL or guess one.

**Next action:** Use the recorded official requirement link only when normally readable, or obtain independently authoritative public requirements/institutional clarification. Preserve the recorded access condition; do not bypass it. Then map this represented award’s exact pools, choices and completion rules.

Separate metadata: 0 course records; missing descriptions/prerequisite statements/public sites/syllabi = 0/0/0/0. Missing fields do not establish no prerequisites, no outcomes or no launch. Full metadata annotations and first-offered evidence are in JSON.

Provenance: [program audit](../data/programs/virginia-tech-artificial-intelligence-ai-minor-minor.json) · [adapter notes](../atlas/adapters/virginia-tech-artificial-intelligence-ai-minor-minor/NOTES.md).

Official evidence (audit-wide):

- [Artificial Intelligence (AI) minor](https://website.cs.vt.edu/academic/undergraduate/ai-minor.html) — Who should pursue this minor; How to pursue the minor; introductory program aims
- [Engineering minors](https://eng.vt.edu/undergraduate/minors.html) — Non-Restricted Engineering Minors: Artificial Intelligence; application procedure

### William & Mary — Artificial Intelligence

`william-mary-ai-minor` · partial · `access_barrier` · scope: minor

The current requirement-source gap has a documented retrieval or access condition; this is not an assertion of program absence or a university-wide denial.

Requirement gaps:

- Detailed required and elective course inventory, choice rules and minor completion policies remain inaccessible.

Access evidence (`challenge`): Official catalog returned a JavaScript/robot challenge; accessible department sources do not establish the full catalog inventory. Exact failed endpoint is not retained here; do not substitute the identity URL or guess one.

**Next action:** Use the recorded official requirement link only when normally readable, or obtain independently authoritative public requirements/institutional clarification. Preserve the recorded access condition; do not bypass it. Then map this represented award’s exact pools, choices and completion rules.

Separate metadata: 0 course records; missing descriptions/prerequisite statements/public sites/syllabi = 0/0/0/0. Missing fields do not establish no prerequisites, no outcomes or no launch. Full metadata annotations and first-offered evidence are in JSON.

Provenance: [program audit](../data/programs/william-mary-ai-minor.json) · [adapter notes](../atlas/adapters/william-mary-ai-minor/NOTES.md).

Official evidence (audit-wide):

- [Minoring in Artificial Intelligence](https://cdsp.wm.edu/academics/undergraduate/ai-minor/) — Minoring in Artificial Intelligence; Artificial Intelligence program entry

### William & Mary — Applied Artificial Intelligence

`william-mary-applied-ai-ba` · partial · `mixed` · scope: degree

The catalog challenge is documented and public department/example-pathway codes disagree.

Requirement gaps:

- Resolve DATA 305 (FAQ) versus AAI 301 (example pathway) for Designing AI Agents.
- Map the full major including the two elective slots, methods and ethics alternatives; the example pathway names illustrative options rather than an exhaustive approved pool.
- Map all university and school BA degree requirements and confirm the complete capstone requirement.

Access evidence (`challenge`): Official catalog returned a JavaScript/robot challenge; accessible department sources do not establish the full catalog inventory. Exact failed endpoint is not retained here; do not substitute the identity URL or guess one.

**Next action:** Resolve DATA305 versus AAI301 for Designing AI Agents and obtain a readable authoritative major/BA inventory, including methods/ethics/electives/capstone and university rules; do not turn example-pathway options into a full pool.

Separate metadata: 3 course records; missing descriptions/prerequisite statements/public sites/syllabi = 3/3/3/3. Missing fields do not establish no prerequisites, no outcomes or no launch. Full metadata annotations and first-offered evidence are in JSON.

Provenance: [program audit](../data/programs/william-mary-applied-ai-ba.json) · [adapter notes](../atlas/adapters/william-mary-applied-ai-ba/NOTES.md).

Official evidence (audit-wide):

- [Major in Applied AI](https://cdsp.wm.edu/data-science/degrees/ba_appliedai/) — Major in Applied AI; Applied Artificial Intelligence program entry
- [Declaring a Major in Applied AI](https://cdsp.wm.edu/data-science/degrees/ba_appliedai/declare-ba-aai/) — Declaration steps
- [Coursework Sequence — Major in Applied AI](https://cdsp.wm.edu/data-science/degrees/ba_appliedai/ba_ai_coursework.png) — Department-linked example pathway image, visually inspected

### William & Mary — Artificial Intelligence/Machine Learning

`william-mary-cs-ai-ml-concentration` · partial · `access_barrier` · scope: concentration

The current requirement-source gap has a documented retrieval or access condition; this is not an assertion of program absence or a university-wide denial.

Requirement gaps:

- AI/ML-specific required and elective courses, choice rules and concentration completion policies remain inaccessible.

Access evidence (`challenge`): Official catalog returned a JavaScript/robot challenge; accessible department sources do not establish the full catalog inventory. Exact failed endpoint is not retained here; do not substitute the identity URL or guess one.

**Next action:** Use the recorded official requirement link only when normally readable, or obtain independently authoritative public requirements/institutional clarification. Preserve the recorded access condition; do not bypass it. Then map this represented award’s exact pools, choices and completion rules.

Separate metadata: 0 course records; missing descriptions/prerequisite statements/public sites/syllabi = 0/0/0/0. Missing fields do not establish no prerequisites, no outcomes or no launch. Full metadata annotations and first-offered evidence are in JSON.

Provenance: [program audit](../data/programs/william-mary-cs-ai-ml-concentration.json) · [adapter notes](../atlas/adapters/william-mary-cs-ai-ml-concentration/NOTES.md).

Official evidence (audit-wide):

- [Bachelor of Science](https://cdsp.wm.edu/computerscience/undergraduate/bachelor-of-science-b.s-in-computer-science.php?mapstat=1) — Bachelor of Science; Artificial Intelligence/Machine Learning program entry

### William & Mary — Artificial Intelligence

`william-mary-data-science-ai-specialization` · partial · `access_barrier` · scope: concentration

The current requirement-source gap has a documented retrieval or access condition; this is not an assertion of program absence or a university-wide denial.

Requirement gaps:

- Confirm catalog-specific specialization restrictions, including eligible DATA 440 topics; the department declaration table does not specify them.

Access evidence (`challenge`): Official catalog returned a JavaScript/robot challenge; accessible department sources do not establish the full catalog inventory. Exact failed endpoint is not retained here; do not substitute the identity URL or guess one.

**Next action:** Use the recorded official requirement link only when normally readable, or obtain independently authoritative public requirements/institutional clarification. Preserve the recorded access condition; do not bypass it. Then map this represented award’s exact pools, choices and completion rules.

Separate metadata: 6 course records; missing descriptions/prerequisite statements/public sites/syllabi = 6/6/6/6. Missing fields do not establish no prerequisites, no outcomes or no launch. Full metadata annotations and first-offered evidence are in JSON.

Provenance: [program audit](../data/programs/william-mary-data-science-ai-specialization.json) · [adapter notes](../atlas/adapters/william-mary-data-science-ai-specialization/NOTES.md).

Official evidence (audit-wide):

- [Bachelors of Science & Minor in Data Science](https://cdsp.wm.edu/data-science/degrees/bs_minor/) — Bachelors of Science & Minor in Data Science; Artificial Intelligence program entry
- [Declaring a Major in Data Science](https://cdsp.wm.edu/data-science/degrees/bs_minor/declare-bsdsci/) — Declaration steps; Artificial Intelligence specialization row

### Worcester Polytechnic Institute — Artificial Intelligence

`wpi-ai-bs` · partial · `source_conflict` · scope: degree

One conditional policy conflict remains after degree-wide review; ordinary metadata omissions are separate.

Requirement gaps:

- HUA source retains conflicting transfer-grade thresholds in its language subsection; coordinator determination is needed for that conditional pathway.

**Next action:** Obtain an authoritative HUA transfer-language threshold or coordinator determination resolving general B-minus versus legacy two-year B/four-year C wording; preserve the already mapped full degree/concentration structure.

Separate metadata: 219 course records; missing descriptions/prerequisite statements/public sites/syllabi = 216/216/219/219. Missing fields do not establish no prerequisites, no outcomes or no launch. Full metadata annotations and first-offered evidence are in JSON.

Provenance: [program audit](../data/programs/wpi-ai-bs.json) · [adapter notes](../atlas/adapters/wpi-ai-bs/NOTES.md).

Official evidence (audit-wide):

- [Artificial Intelligence Major](https://wpi.cleancatalog.net/artificial-intelligence/artificial-intelligence-major) — Program distribution and course-option tables
- [Artificial Intelligence Major with Concentration in Advanced AI Methods and Technologies](https://wpi.cleancatalog.net/artificial-intelligence/artificial-intelligence-major-with-concentration-in-advanced-ai-methods-and) — All local choice sections, exclusions and level requirements
- [Artificial Intelligence Major with Concentration in Built and Natural Environment](https://wpi.cleancatalog.net/artificial-intelligence/artificial-intelligence-major-with-concentration-in-built-and-natural) — All local choice sections, exclusions and level requirements
- 25 additional audit sources, with exact URLs and locators, in this program’s JSON entry.

### Worcester Polytechnic Institute — Business Analytics & Applied AI

`wpi-business-analytics-applied-ai-bs` · partial · `mixed` · scope: degree

A transfer-grade conflict and an independently unspecified optional graduate-credit limit require clarification.

Requirement gaps:

- HUA source retains conflicting transfer-grade thresholds in its language subsection; coordinator determination is needed for that conditional pathway.
- Program refers to a limit on graduate courses; university optional BS/MS rules give percentage-based shared-credit caps instead. An approved individual agreement is required.

**Next action:** Resolve the HUA language-transfer threshold and the program’s graduate-course count reference against percentage-based BS/MS rules/approved agreement. Do not invent a universal graduate-course count.

Separate metadata: 49 course records; missing descriptions/prerequisite statements/public sites/syllabi = 44/46/49/49. Missing fields do not establish no prerequisites, no outcomes or no launch. Full metadata annotations and first-offered evidence are in JSON.

Provenance: [program audit](../data/programs/wpi-business-analytics-applied-ai-bs.json) · [adapter notes](../atlas/adapters/wpi-business-analytics-applied-ai-bs/NOTES.md).

Official evidence (audit-wide):

- [Business Analytics and Applied AI Major](https://wpi.cleancatalog.net/business/business-analytics-and-applied-ai-major) — Program distribution and course-option tables
- [WPI Degree Requirements](https://wpi.cleancatalog.net/wpi-degree-requirements) — Applicable bachelor requirements and conditional options; full policy section reviewed
- [Humanities and Arts Requirement](https://wpi.cleancatalog.net/humanities-and-arts-requirement) — Applicable bachelor requirements and conditional options; full policy section reviewed
- 13 additional audit sources, with exact URLs and locators, in this program’s JSON entry.

