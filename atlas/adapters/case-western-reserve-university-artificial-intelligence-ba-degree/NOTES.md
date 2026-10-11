# Case AI BA curriculum

The official Program Requirements tab supplies the mapped major tables. Sample plans are excluded. Course alternatives retain whole bundles, and finite choice pools are distinct from required courses.

The application rule retains one 3–4 credit course or two 1.5 credit courses; missing individual credits are not inferred.

Partial degree coverage: university general degree rules and the Unified General Education Requirements approved course lists remain to be fully mapped. Course metadata remains incomplete. Six published learning outcomes are recorded as short source-backed paraphrases. The page identifies the 2026–2027 Bulletin.

Sources inspected on 2026-10-10:
- https://bulletin.case.edu/engineering/computer-data-sciences/artificial-intelligence-ba/
- https://bulletin.case.edu/undergraduate-academics/bachelors-degree-requirements/
- https://bulletin.case.edu/undergraduate-academics/unified-general-education-requirements/

## Degreewide closure — reviewed 2026-10-11

**Complete degree-scope inventory: 744 course observations / 84 requirement nodes.** This supersedes the earlier partial note above. The 2026–2027 Bulletin's major tables, [bachelor's requirements](https://bulletin.case.edu/undergraduate-academics/bachelors-degree-requirements/) and [UGER](https://bulletin.case.edu/undergraduate-academics/unified-general-education-requirements/) were read from permitted cached official pages fetched 2026-10-10. The reviewer audit is explicit and separate from scraper output.

The BA requires 120 credits, 90 arts/sciences (six-credit reduction for concurrent BA+BS), 30 at the 300/400 level, 2.000 graded-major average and 2.000 CWRU average. Half the major, including related required fields, must be at CWRU; university residency requires 60 CWRU credits including 15 after reaching 105 total. Catalog choice and possible updates after ten years are represented. The secondary-major school exemption is recorded without changing this full-degree record.

AI's STEM+N classification fixes breadth outside the major: 18 credits across A+H and SS+M, at least six each, with the transfer/test ceiling, three-in-each CWRU minimum and incoming-transfer exception. Full subject eligibility and finite exceptions are explicit open rules, including MUED 320's exclusion from A+H. All thirteen published UGER course tables are mapped, preserving eight entire course bundles, SAGES-designated capstone eligibility and eight approved engagement activities. The shared extraction observes 692 course identities before merging exact major code/title matches. Pools overlap and are not extra required courses.

Communication/portfolio, inquiry placement and first-year timing, passing letter grades, transfer appeal restrictions, quantitative reasoning, four perspectives, and wellness are represented. Wellness counts semester-equivalent enrollment independent of credits, with physical-movement minimum, repeat limits, ROTC/varsity/marching-band exceptions, military waiver and transfer policy. Explicit zero-credit rows stay zero. AIAE 100 preparation and portfolio reflections are policy requirements; ordinary example word counts are not mandatory universal minima. CSDS 310 is an approved disciplinary communication course; CSDS 395A is an approved capstone; CSDS 132/134 satisfy quantitative reasoning. Approved UGER/major overlap is allowed.

No unavailable finite requirement pool remains in these cited pages. Department-wide breadth eligibility and advisor-approved routes are deliberately open rules. The Bulletin warns approvals may expand during the academic year; completeness covers this published snapshot, not future approvals. Individual descriptions, prerequisites, syllabi and some credits/units remain unknown. Source-listed multi-course totals are never divided into inferred individual amounts. Some major course credit metadata is corroborated by matching UGER rows, with that provenance recorded in program notes.

`case_degree_policies.py` reads real headings, AI breadth classification, actual tables/bundles/activities, degree values and material policy markers. It returns partial observations without audit or timestamps. Synthetic tests exercise whole bundles, changed degree values, award-specific school rules, zero-credit wellness, changed pool order and observed titles; optional ignored-cache checks exercise real source structure.

## Independent correctness hotfix — 2026-10-11

Official 2026–2027 CSDS descriptions now support exact core classifications: CSDS 132/134/237 programming and CSDS 233/310 data structures/algorithms are computing foundations; CSDS 302 is mathematics. The BS ENGR 399 description supports human context. MATH 121/307 have explicitly limited exact-title classification reviews. The fixed graph is unchanged: BA has eight fixed records (2 foundations, 3 mathematics, 3 AI/ML); BS adds ENGR 399 (1 human context). Programming remains a required alternative between CSDS 134 and the full CSDS 132+237 bundle. Three programming option records do not mean three required courses.

The shared narrow title heuristic caused the error. A Case-specific exact-identity layer now corrects major observations, and separate description parsers check subject markers, actual titles/credits/prerequisites and changed-prose digests. They emit no independent category review or completeness audit. Seed manual category reviews cite https://bulletin.case.edu/course-descriptions/csds/ and (BS) https://bulletin.case.edu/course-descriptions/engr/. Description paraphrases and prerequisite observations are independent of original catalog-row provenance.

The earlier complete requirement inventory is not a complete correctness audit. Remaining course classifications and general-education second-pass review are still unreviewed, so research/degree-audit/case-western.json reports in progress. See its adjacent Markdown for manual fixed-set arithmetic and exact remaining work.

## Named major/elective description audit — 2026-10-11

All 78 distinct named major identities across the two degrees were independently read in the current 2026–2027 Bulletin's 14 subject pages: 59 BA and 72 BS program records. Each now has an original concise description and source-backed subject review. Exact prerequisites, permission routes, invitation/placement restrictions and credit exclusions remain course metadata. Advanced prerequisites are not silently made fixed degree requirements. CSDS 102 requires no prior/current 300-level CSDS enrollment; CSDS 499 explicitly allows Requisites Not Met permission instead of graduate standing. CSDS 463's heading/degree row are preserved despite a conflicting CSDS 466 cross-list footer. No identity merge is inferred.

Individual course amounts are observed, including the 1.5-unit application options. Course headers use Units; existing corroborated credit units remain, and other units stay unknown. The application rule remains its accurate prose alternative rather than selecting an invented route.

`case_degree_metadata.py` registers source-specific parsers for every relevant subject; exact headings/titles/blocks and raw-body digests guard the original summaries and taxonomy. Changed descriptions yield unclassified observations, never stale reviews. Seed-only `category_review` rationales distinguish mixed subjects, e.g. CSDS 102/225/443, from explicit AI methods. Generic prefix/title classifications are disabled for other Case major identities.

**This supersedes the earlier complete-inventory claim:** SCMG 462 and SCMG 463 are BA application options, but their current descriptions require enrollment in the Master of Supply Chain Management program. Neither reviewed source states an undergraduate exception. The inventory is now **partial**, with this substantive eligibility conflict in the audit. The correctness ledger is blocked on that conflict while separately retaining accessible general-education work in progress.

### UGER role correction — 2026-10-11

Reread all governing bachelor/UGER policy prose and all thirteen approval tables. The required communication sequence now has an `all` parent; its inquiry, two CI, disciplinary communication and capstone choices no longer incorrectly inherit a note role. Counts and entire course bundles are unchanged. Wellness remains prose duration logic. Corrected the inquiry summary: direct AIQS 120 applies to some ESL students, not all students who omit AIAE 100. General-education descriptions still need independent review.

## General-education description batch 1 — 2026-10-11

Independently read 59 additional course blocks across AIQS, CSDS, ECON, ECSE, ENGR, HUMN, MATH, PHIL, PHYS and STAT. They enrich 59 BA and 58 BS records (ENGR399 was already reviewed for BS). Both programs now have 626 unreviewed general-education records; accessible work remains in progress. The 118 BA/130 BS reviewed records are not a complete correctness audit. Original summaries and per-course rationales are guarded by actual source-body hashes; no copied full descriptions are published. Mixed computing/philosophy/engineering subjects remain other with explicit candidate categories. AI ethics/politics/community research is human context rather than title-based AI methods. Formal logic is mathematical. The policy adapter no longer infers subject categories from UGER approval or generic prefixes.

AIQS course registration placeholders, advisor consent, course enrollment restrictions and credit exclusions are metadata; no additional fixed requirement is inferred. Missing prerequisite fields remain unknown except where the source explicitly states no prerequisites. CSDS132 and ECSE132 have reciprocal official cross-list statements, so one reviewed identity group now counts Java once while preserving both records. The CSDS134 exclusion is not a cross-list equivalence. No other cross-list group is claimed by this batch.
