# Liberal arts discovery depth pass, batch 2 — 2026-10-11

This pass deepens ten previously shallow `inspected` records, with 43 cited source observations. **All ten remain inspected; zero qualifying awards were verified and zero institution-wide absence conclusions were made.** Cohort/ranking evidence and existing programs are unchanged. Exact URLs, observation dates, locators, decisions and remaining scope are in the [batch2 survey](../data/surveys/liberal-depth-batch2-2026-10-11.json).

| Institution | Evidence added | Decision and remaining scope |
| --- | --- | --- |
| Macalester | Academic concentration list, Cognitive Science structure/course options, MSCS offerings and CS major advice | The named concentration is Cognitive Science. AI/robotics options do not establish a separate AI concentration. The catalog homepage timed out; internal catalog tracks and wider announcements remain unreviewed. |
| Lafayette | 2026-27 program index, CS BS requirements for Class of 2030 onward, Data Science minor | The inspected credentials are CS and Data Science. Class-year distinctions are preserved. Other class-year rules, internal tracks and approved elective pools remain outside this bounded review. |
| Bryn Mawr | Department index, CS major/minor overview and Data Science minor description | The interactive finder rendered placeholders. Linked catalog CS requirements presented robot verification. No AI title verified from readable institutional pages; cross-campus and concentration rules remain unreviewed. |
| Trinity College, Connecticut | Official named program list, 2026-27 bulletin, CS BS requirements and Cognitive Science minor | AI is an option in the CS software breadth requirement. Cognitive Science is the separately named minor. Bulletin enumeration showed generic program labels, so the index was not accepted as a complete readable roster. |
| Colorado College | Major/minor index, 2026-27 catalog CS title/requirements and department emphasis announcement | The formal optional emphasis is Data Science, introduced Fall 2025; the catalog says completion can be noted on the transcript. Its ML relevance does not turn it into an AI emphasis. Some catalog course rows and the department overview were unreadable. |
| Mount Holyoke | Program-type directory and readable CS/Data Science requirement sections | AI appears as a field/course option. DATA-121 is a course, not a named AI award. Other departmental tracks, NEXUS and consortium details remain unreviewed. |
| Spelman | Major/minor directory; CS BS, CS minor and Information Sciences minor requirements | AI/ML engineering is a career possibility. Information Sciences is business-oriented but not AI-titled. College-wide catalog, partner-program and announcement review remain incomplete. |
| Occidental | Areas of Study, AI and business exploration guides, CS pathways/course list, Cognitive Science overview | AI at Oxy is an interdisciplinary guide; CS lists standard, computational mathematics and CS+X pathways. None is verified as an AI-titled award. Full formal track rules and other announcements remain unreviewed. |
| Scripps | Program directory, local CS minor requirements and Data Science description | Local minors are CS/Data Science; cross-campus CS majors are separately listed. Linked catalog requirements returned 403. Cross-campus applicability and internal tracks remain unreviewed. |
| Trinity University, Texas | Schools/departments, CS BA/BS/minor and Finance/Business Analytics offerings | AI is a computing/research topic; reviewed business degrees retain their actual names. The linked CS BS catalog returned 403. Formal concentration details remain unreviewed. |

## Useful exclusions with primary evidence

- [Occidental's directory](https://www.oxy.edu/academics/areas-study) explicitly separates exploration guides from majors/minors. [AI at Oxy](https://www.oxy.edu/academics/student-success/ai-oxy) offers interdisciplinary coursework, not a stated award. Neither the guide title nor the CS+X label is enough to create an AI degree or family.
- [Colorado's catalog](https://coursecatalog.coloradocollege.edu/programs/COSC-BA-Major/requirements-SQ02k) identifies an optional Data Science emphasis and transcript notation. The [department announcement](https://www.coloradocollege.edu/academics/dept/mathcs/major-minor-reqs/computer-science/csmajorchanges.html) explicitly dates this emphasis to Fall 2025. This is evidence for the differently named emphasis, not an AI launch date.
- [Trinity College's CS requirements](https://bulletin.trincoll.edu/programs/BS-CPSC/requirements-krhha) place CPSC 352 Artificial Intelligence among software breadth choices. [Spelman's program page](https://www.spelman.edu/academics/computer-and-information-sciences/index.html) places AI/Machine Learning Engineer in career possibilities. Neither placement denotes a formal AI credential.

## Access and scope boundaries

No robot challenge or HTTP restriction was bypassed. Scripps and Trinity University catalog attempts returned HTTP 403; Bryn Mawr requested robot verification. Those paths were left at the access boundary. Macalester timed out; that is a fetch failure, not a known denial. Colorado's department catalog overview returned a footer without substantive text, while its linked concrete CS program was readable; the requirement view omitted some course rows. Trinity College's catalog index exposed generic link labels, while its named CS and Cognitive Science records were readable. Dynamic response limitations are not evidence of absence.

Lafayette, Colorado and Trinity College catalog entry pages explicitly identify 2026-27. Undated departmental pages are observations as of 2026-10-11, not assigned an invented catalog year. Individual requirement versions and links can be older than the institutional directory; they are not silently promoted to current degree audits.

Keyword/domain search attempts yielded irrelevant results and did not establish credible announcement coverage. This batch therefore relies on directly followed official navigation and readable program/requirement pages; broader announcement archives remain an explicit gap. No institution is upgraded to an absence conclusion because a directory lacks the phrase AI.

## Validation

Targeted core/discovery tests and a fresh temporary full-data ingest, repeat ingest, integrity check and static build validate integration. No schema, adapter, program, maintained database, shared PLAN or frontend file changed. The coordinator runs the full suite against a frozen release; this batch does not repeat it.

Results: **116 targeted tests passed**. All ten newer notes survived sorted full-data ingestion. Repeat ingest changed zero programs and did not add coverage events; SQLite integrity and foreign-key checks passed, and the temporary static build succeeded. No maintained database was modified.
