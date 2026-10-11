# Historical integration and release notes

Archived 2026-10-11. This is a chronological record of earlier checkpoints and then-current work queues; counts and assignments below are historical. Consult PLAN.md for the verified live release and current work.

## Continued sourcing after this release

The initial90 partial and six pending inventories now have a pinned, itemized [gap ledger](research/curriculum-gap-triage.md), with accessible work distinguished from access and policy conflicts. Accessible work is proceeding independently of the cohort and CSRankings issues. Current parallel batches cover Northeastern shared course evidence; MIT/Rice/Maryland major policies; Penn/Columbia/Duke requirements; Purdue/Case degrees; RIT/Stevens/Ursinus/Miami policies; and NJIT/Drexel/Lehigh degree policies. The coordinator is reviewing pending-program transport boundaries and Buffalo's shared-family source gaps. Publications are checkpoints, not a stopping condition for accessible research.

## Latest research and verification

- Stanford's AI track has a complete concentration scope: 217 fixed course observations, 29 requirement nodes, the seven-course/25-unit depth, elective areas, humanities options and applicable policies. This does not certify the entire CS BS; missing individual credits remain visible.
- Tulane's technical AI minor and Tufts' Application of AI minor now have complete local scopes. The distinct Tulane AI Literacy minor is separately listed and partial. Tufts' AI Development minor stays partial because its checklist and department disagree on a required-course alternative.
- MIT now has390 course observations and633 requirement nodes including institute policies and explicitly versioned department evidence. Its Fall-2025-entry requirements differ from the unversioned catalog chart; reconciliation and the 6.4300 credit conflict remain unresolved. NC State and both UVA concentrations retain their mapped partial inventories and exact policy/source gaps.
- Case minor metadata adds 30 descriptions, 20 prerequisite statements and 28 verified credit amounts. Applied AI was downgraded to partial because three listed electives restrict enrollment to graduate programs; no undergraduate exception is invented. The catalog's approval-status ambiguity is also retained.
- Robots precedence now follows RFC 9309 through Protego: more-specific allow rules work while more-specific denials still stop retrieval. Pacing, request-rate limits, visit windows, redirect checks and access failures have regressions. This corrected a local interpretation error for Tufts' ordinary public Box checklist viewers; no authentication or publisher restriction was bypassed.
- A final product audit found and fixed long source-URL overflow on mobile. Isolated browser checks verified Stanford's large course table, Tufts' differing statuses and source conflict, Tulane's separate listing and Northeastern's carefully qualified hosting context. The clean release suite includes this regression.

Each adapter's NOTES.md states evidence, interpretations, exact conflicts, metadata gaps and next checks. Research edits were committed before the database freeze; the release was tested from a separate committed archive and fresh locked uv environment.

## Remaining work and blockers

1. **Cohort:** obtain a permitted authoritative 2027 roster for both categories and all cutoff ties; complete missing liberal-arts enumeration. Preserve secondary/inferred/membership-only labels until resolved.
2. **CSRankings:** numerical import remains held pending permission or qualified reuse review. Methodology records ai,vision,mlmining,nlp,inforet, proposed 2016–2025 window, U.S. filter, pinned source snapshot and computation method. Values remain null, not zero quality. Publication research does not measure undergraduate teaching quality. See [research note](research/csrankings.md).
3. **Access:** eight loaded institutions remain inaccessible. Six published pending curricula have documented barriers; six newly verified program identities have curriculum extraction underway. Additional program-specific links remain blocked or unread. See [access review](research/access-review.md), [pending curriculum barriers](research/pending-curriculum-barriers.md) and adapter notes. No bypass of robots/auth/403/password gates.
4. **Curricula:** Twelve published inventories remain pending and 87 partial. Verify finite pools, nested alternatives, policy applicability and source conflicts before promoting completeness.
5. **Metadata:** many descriptions, prerequisites, public course sites and example syllabi remain unknown. Verify exact course identity and term; preserve historical labels and link rather than redistribute.
6. **Institution depth:** directory searches alone do not establish absence. Continue bounded catalog/minor/concentration searches and documented leads. No absence conclusion has been asserted.

Use `uv run atlas status`, `uv run atlas candidates`, adapter notes and task-specific skills. Refreshes queue observations for review; they never silently replace the research database.

## Research integration verified — 2026-10-11

Committed evidence through `bc71b611` is integrated in release `551a81e9`:33 complete/87 partial/5 pending inventories;11963 observed course records;8488 resolved requirement nodes. Case BA/BS now have complete degree-scope audits; Buffalo adds independently accessible general-education policies and dated Pathways candidates while major catalogs remain unavailable. Michigan HCAI has a public-handbook inventory, and Northeastern course catalogs plus several university policy sources expand independently measured metadata.

A clean locked uv environment passed904 tests, including all17 required Chromium cases. Fresh reconstruction and the maintained publication copy agreed on current facts; repeat ingest changed zero programs, database integrity passed, and132 build files reproduced byte-for-byte. GitHub CI and Pages deployment succeeded. Live JSON matched the frozen counts; browser checks passed direct details, comparison reload, filter back/forward, keyboard expansion and390px mobile layout without JavaScript errors or overflow.

Subsequent commits continue Northeastern descriptions/resources, UCSB's current college guide, William & Mary policies and additional minor-policy reviews. They await the next frozen integration. The initial gap ledger is being reconciled against these follow-ups to identify remaining accessible work independently of the unresolved cohort and CSRankings questions. Publications remain checkpoints, not a stopping condition.

## Latest published checkpoint — 2026-10-11

Release`98a9cc4` is verified live:126programs,33complete/87partial/6pending,12036course observations and8613requirement nodes. The separate Michigan Engineering technical AI minor adds one confirmed title with pending detailed requirements; it is not merged with UMSI HCAI. Northeastern public examples add46site and46syllabus observations across23variants. Clean tests passed974 with all17required browser cases, fresh/maintained current facts agreed, and133files reproduced identically. CI/Pages succeeded and live JSON/browser checks matched. RootHTML is2,304,964bytes after another measured projection reduction; detail evidence remains intact.

Later research continues Michigan home-college rules and a verified SI326 Winter2026 syllabus; Northwestern engineering policies; NJIT lab pairings; USF independent course-inventory metadata; Maryland's dated public language viewer; and Northeastern descriptions. Those newer commits await the next frozen release. Exact accessible work remains assigned at Stevens/MIT, Miami/RIT, UCSD/UCSB and CMU/Penn. Publication does not end this source work.

## Next release candidate — 2026-10-11

Evidence through `b504ea14` is frozen in the maintained database: 126 programs, 33 complete / 87 partial / 6 pending inventories, 13,452 program-course observations and 10,018 resolved requirement nodes. This candidate includes all 1,593 Northeastern course descriptions; UCSD shared graduation, Revelle and Muir pools; Miami's initial public cognate capture; Maryland language routes; Stevens policy choices; Michigan syllabus evidence; and CMU/Penn core metadata. It is not yet a verified publication.

Newer survey observations now survive older files loaded later, while earlier evidence stays in history. Migration 007 compresses canonical revision JSON losslessly: a copy of the 582-revision database recovered every original payload byte and metadata field, preserved the complete current export, and shrank from 77,545,472 to 39,616,512 bytes after compaction. Subsequent committed research makes the current frozen database 40,398,848 bytes. Ninety-eight focused persistence/family/pipeline tests passed before the clean full release check.

Remaining accessible work is assigned at UCSD's other college pools, UCSB and MIT, Miami's remaining finite cognate lists, and deeper catalog discovery at 30 institutions. Official identity leads at Florida State, UMass Amherst and RPI are being researched separately and are not included in this frozen count. Both ranking-cohort completeness flags and the CSRankings permission boundary remain unchanged.

The `5b464d4` candidate passed 1,115 tests (including required browser tests) but was **not published**: fresh/maintained export comparison exposed order-dependent institution inspection dates. Commit `6ab229a` derives that date from all current program verifications and survey observations, repairing old imports without changing their evidence. The replacement freeze through `e16c6de0` includes later Warren/MIT evidence and 20 deeper liberal-arts inspections: 13,920 program-course observations, 10,403 requirement nodes, and the same 126-program/status counts. It awaits a new clean verification. The official-title rule now explicitly includes source-defined GenAI and GeoAI compounds; their new records are still in research and outside this freeze.


## Verified checkpoint and continuing work — 2026-10-11

Release `8043d5c` is verified live with 132 programs: 33 complete / 87 partial / 12 pending curricula, 13,920 program-course observations and 10,403 resolved requirement nodes. The final committed source includes six new official identities at FSU, UMass Amherst, RPI, SMU and UIC, added after the 126-program database freeze. CI reconstructs the publication copy from every committed record; that copy and a fresh database agreed on current facts. UIC remains announced on its April 2026 evidence, not presumed active from elapsed time.

A clean locked environment passed 1,193 tests with all 17 required browser cases. The 96 skips concern optional ignored source caches or historical snapshots. Repeat ingest changed zero programs, foreign keys/integrity passed, and 139 build files reproduced byte-for-byte. GitHub CI and Pages succeeded; live data matched, comparison reload/back/forward and keyboard expansion passed, every new identity page loaded directly, and the 390px checks found no overflow or JavaScript errors. The rejected `5b464d4` candidate was never published; its inspection-date inconsistency is repaired and covered by regression tests.

Newer research commits are not included in these published metrics. They continue full Miami cognate pools, UCSD Marshall/Sixth and remaining colleges, MIT HASS fields, six new program curricula, Vanderbilt/Florida minors and deeper liberal-arts catalog review. Northeastern's 1,593 descriptions are now verified across 787 distinct codes; that finite metadata queue is complete, while home-college applicability remains partial. Publications remain checkpoints. Cohort enumeration, CSRankings permission, inaccessible sources and unresolved program-specific policy conflicts remain explicitly open.

### Verified 136-program checkpoint (2026-10-11)

Release `7ae8cf4d` passed 1,322 tests (all 17 Chromium cases), fresh/maintained current-fact comparison, repeat ingest, integrity and 143-file deterministic builds. CI/Pages run `38101661236` succeeded. Public JSON and browser verified the new Binghamton, Lewis & Clark, Vanderbilt and Florida details, complete SMU local audits, Caltech bounded coverage state, existing direct links, comparison reload/history, keyboard expansion and 390px layout. Root HTML is 2,785,533 bytes. New research commits after this release remain unreleased until a subsequent checkpoint.


## Verified 136-program checkpoint (superseded)

Release `7ae8cf4dfbb4f7b45c6baf8621347c2495acb375`, [CI/Pages run](https://github.com/KrisJordan/ai-program-atlas/actions/runs/38101661236): 1,322 passing tests with 17 required Chromium cases, 111 optional-cache/historical skips, fresh/maintained equality, repeat ingest zero, 143 deterministic files and live browser checks. It contained 136 programs across 194 institutions (67 confirmed, 118 inspected, eight inaccessible, one bounded absence result), with 36 complete scoped inventories, 93 partial and seven pending. This is historical; PLAN.md records the newer verified release.


## Verified 142-program checkpoint (superseded)

Release `fd44e55b7437452986ba145d5473978c4e9f521f`, [CI/Pages run](https://github.com/KrisJordan/ai-program-atlas/actions/runs/38102605687), passed 1,405 tests with all 23 required browser cases, 118 optional-cache/historical skips, fresh/maintained equality, repeat ingest zero and 149-file deterministic builds. It contained 142 programs across 194 institutions: 72 confirmed, 113 inspected, eight inaccessible, one bounded absence finding; curricula were 37 complete, 98 partial and seven pending. Program-course observations were 22,609 and requirement nodes 16,717. Live checks verified family expansion/collapse history, comparison focus, direct links and mobile layout. Root HTML was 2,831,909 bytes. These are historical counts; PLAN.md records the later 164-program release and requested profile/navigation changes.


## Archived 164-program checkpoint: 91974dc

## Verified publication

- Repository: https://github.com/KrisJordan/ai-program-atlas
- Site: https://krisjordan.github.io/ai-program-atlas/
- Verified release: `91974dc63c95a863960f8685e20eb6f80e74315b`, [successful CI and Pages deployment](https://github.com/KrisJordan/ai-program-atlas/actions/runs/38104814294).
- Fresh locked uv environment and clean committed source: **1,617 tests passed**, including all **32 required Chromium tests**. The 132 skipped cases require optional ignored source caches or historical snapshots; no browser tests were skipped.
- Fresh reconstruction and maintained publication copy passed integrity checks and agreed on current facts; additional historical coverage sources were preserved. Repeat ingest changed zero programs. Repeated static builds were byte-identical across 171 files.
- Live public JSON matched these counts, and every projected curriculum profile and award bucket matched the source data. Live checks passed cohort tabs, BS/BSE/BA/Other filters, keyboard navigation, hidden comparison selection, profile toggling, reload/back/forward, comparison-clear focus, direct new and existing pages and 390px mobile layout. Screenshots were visually checked; no JavaScript errors or document overflow occurred. Family, empty-state, no-JS and multi-award cases also passed the required browser suite.
- Dedicated local repository: `ai-program-atlas/` in this Mac Studio task. No existing personal website or unrelated repository was changed. Coordinated Astra high research and implementation use explicit ownership and incremental commits.

## Published coverage

| Measure | Verified count |
| --- | ---: |
| Institutions in loaded roster | 194 |
| National Universities / National Liberal Arts Colleges | 108 / 86 |
| Confirmed qualifying title / partially inspected / inaccessible | 72 / 114 / 7 |
| Loaded institutions pending / absence conclusions | 0 / 1 |
| Concrete programs | 164 |
| Degrees / minors / concentrations / additional majors | 63 / 49 / 47 / 5 |
| Complete / partial / pending requirement inventories | 36 / 119 / 9 |
| Program-course records / resolved requirement nodes | 23,722 / 18,476 |
| Program families / concrete family variants | 2 / 31 |
| Descriptions / prerequisite statements | 1,941 / 2,768 |
| Credit amounts with verified units | 8,949 |
| Public course sites / example syllabi | 78 / 72 |

Caltech has one bounded no-qualifying-program finding after the current program directory and all 32 option/minor catalog pages were reviewed. It is a dated search result, not a claim about future offerings.

Course counts include elective pools and repeated observations across sibling programs. They are not unique institution-wide courses, required-course totals, completion percentages or quality scores. Complete refers to an explicitly reviewed scope: a complete minor/concentration/additional major does not certify the host degree. Metadata availability is separate. Zero pending in the loaded roster is not full target-cohort coverage; missing institutions remain outside that denominator.



## Superseded cf263e40 checkpoint

## Verified publication

- Repository: https://github.com/KrisJordan/ai-program-atlas
- Site: https://krisjordan.github.io/ai-program-atlas/
- Verified release: `cf263e40e395ac88d453972bd3378d7b55e07fa5`, [successful CI and Pages deployment](https://github.com/KrisJordan/ai-program-atlas/actions/runs/38106627097).
- Fresh locked uv environment and clean committed source: **1,787 tests passed**, including all **42 required Chromium tests**. The 143 skipped cases require optional ignored source caches or historical snapshots; no browser tests were skipped.
- Fresh reconstruction and maintained publication copy passed integrity checks and agreed on current facts; additional historical coverage sources were preserved. Repeat ingest changed zero programs. Repeated static builds were byte-identical across 175 files.
- Live Case BA/BS fixed foundations both equal two; three introductory programming alternatives remain option records. All six ranking category/type panels passed ascending rank checks on desktop/mobile, including filtering, explicit name sort and history.
- Live public JSON matched these counts, and every projected curriculum profile and award bucket matched the source data. Live checks passed cohort tabs, BS/BSE/BA/Other filters, keyboard navigation, hidden comparison selection, profile toggling, reload/back/forward, comparison-clear focus, direct new and existing pages and 390px mobile layout. Screenshots were visually checked; no JavaScript errors or document overflow occurred. Family, empty-state, no-JS and multi-award cases also passed the required browser suite.
- Dedicated local repository: `ai-program-atlas/` in this Mac Studio task. No existing personal website or unrelated repository was changed. Coordinated Astra high research and implementation use explicit ownership and incremental commits.

## Published coverage

| Measure | Verified count |
| --- | ---: |
| Institutions in loaded roster | 194 |
| National Universities / National Liberal Arts Colleges | 108 / 86 |
| Confirmed qualifying title / partially inspected / inaccessible | 72 / 114 / 7 |
| Loaded institutions pending / absence conclusions | 0 / 1 |
| Concrete programs | 168 |
| Degrees / minors / concentrations / additional majors | 63 / 50 / 50 / 5 |
| Complete / partial / pending requirement inventories | 46 / 115 / 7 |
| Program-course records / resolved requirement nodes | 23,999 / 18,671 |
| Program families / concrete family variants | 2 / 31 |
| Descriptions / prerequisite statements | 2,042 / 2,831 |
| Credit amounts with verified units | 8,993 |
| Public course sites / example syllabi | 78 / 72 |

Caltech has one bounded no-qualifying-program finding after the current program directory and all 32 option/minor catalog pages were reviewed. It is a dated search result, not a claim about future offerings.

Course counts include elective pools and repeated observations across sibling programs. They are not unique institution-wide courses, required-course totals, completion percentages or quality scores. Complete refers to an explicitly reviewed scope: a complete minor/concentration/additional major does not certify the host degree. Metadata availability is separate. Zero pending in the loaded roster is not full target-cohort coverage; missing institutions remain outside that denominator.



## Verified source-correction checkpoint — 531073fe

Published 2026-10-11 from exact clean commit `531073fe5a33dca48080163c874f0fa19be3020a`. [CI and Pages run](https://github.com/KrisJordan/ai-program-atlas/actions/runs/38114281903) succeeded. Clean locked suite: 2,376 passed, 183 optional-cache/historical skips, all 54 mandatory Chromium tests passed. Maintained/fresh current facts agree; repeat ingest zero; FK and integrity pass; 175 deterministic files. SQLite 89,964,544 bytes.

Live 168 programs/194 institutions, 24,248 course observations/19,560 nodes, 5,464 descriptions/4,606 prerequisites. Audit statuses: two primary audited, 23 individually blocked, 38 active; no full second pass certified. All projected profiles matched; desktop/390px filters, ranking panels, second majors, concentration parents, detail links, comparison reload/back/forward and keyboard checks passed without document overflow or JavaScript errors. Source-specific corrected fixed counts: MIT3, MarylandBA10, Northwestern13, Northeastern Environmental36. PublicHealth18 fixed/79 options. The target cohort remains incomplete; no expansion or audit-completion claim.

Prior ddd112ac and640b89fb candidates were not published because clean tests identified stale expected roles or optional partial-observer assumptions; evidence-aligned regression fixes preceded this exact tested release. New research continues after this checkpoint.


## Historical unpublished candidates preceding dd797acc

### Unpublished continuation after 531073fe

Stevens now has all 79 represented subject dispositions (68 reviewed, ten mixed, one unclassified) after reading the remaining 54 public course description fields. QF 102 retains a version/title metadata hold; HASS 101 has no substantive description. All 54 real-source replays and 106 focused tests passed; isolated ingest/repeat (1/0), integrity, foreign keys and static build passed. Remaining selected Eligibility and school/cohort applicability review continues. These source changes do not update the verified publication totals above until the next clean release gate.

Migration 014 is ready for frozen integration: current canonical program snapshots now use lossless, hash-verified compression while relational facts and history remain intact. A copy of the published database shrank from 89,964,544 to 61,747,200 bytes after compaction; the complete export and all 45 other table hashes remained identical. Storage/family/identity/pipeline regression subset: 120 passed. The full-inventory test awaits the coordinated ledger freeze because ongoing research has intentionally moved source profiles beyond the last compiled audit snapshot.

Stevens independent role enumeration corrected three named math/science options previously stranded as context. Its verified graph now has 24 fixed, 30 mapped option and 25 contextual records. The choose-two rule remains open and conditional; source eligibility, not the displayed pool size, determines permitted selections. Focused source/profile suite: 107 passed.

Stevens transition-policy follow-up read the current school FAQ, dated communication and full Humanities/AP tabs; no explicit resolution of the two school-scoped AI applicability questions was found. Two desktop/mobile Chromium regressions passed the corrected 24/30/25 role counts and comparison reload/back/forward. The primary review remains in progress while remaining selected course Eligibility tabs are inspected.

### Frozen candidate after a64c2b6 (verification pending)

Committed source and primary ledgers were archived before ingestion. The maintained database is migrated through 014 and compacted to 64,876,544 bytes, retaining historical rows and corrections. It contains 168 programs at 194 loaded institutions, 24,251 course observations, 19,623 requirement nodes, 6,302 description summaries and 5,082 prerequisite statements. Repeat ingest changed zero programs; integrity and foreign keys passed. This candidate is not yet the verified public release; the publication section above remains the live checkpoint until clean tests, CI and live checks succeed.

Candidate `87c56012` was not published: its clean suite found ten legacy-schema upgrade regression failures (2,641 other tests passed, 225 optional cache/historical tests skipped). The new snapshot storage code had assumed schema 014 even during pre-migration verification. The repair preserves verified reads/writes on the older text schema while preferring compressed storage after migration and never falling back from a corrupt compressed payload. All 130 focused storage/family/identity/pipeline tests passed after repair; a new frozen candidate must pass the full release gate.

Repaired frozen integration: 2 primary degree reviews audited, 51 individually blocked and 10 in progress; no full independent second pass certified. Maintained database 65,875,968 bytes; 24,251 course observations, 19,623 requirement nodes, 6,570 descriptions and 5,316 prerequisite statements. Repeat ingest, integrity and foreign keys passed. Publication remains pending the clean suite.

Candidate `d4aea55d` was not published: eight tests still required an unresolved Miami summer-policy conflict that the source review had resolved. The corrected tests now verify the actual conditional credit restriction and financial-aid scope; both affected suites pass (31 tests). A new frozen checkpoint from `3d03065c` has 2 audited, 51 blocked and 10 in-progress primary degree reviews, 24,251 course observations, 19,664 requirement nodes, 8,985 descriptions and 5,612 prerequisite statements. The maintained database is 68,702,208 bytes; repeat ingestion, integrity and foreign keys passed. Public-course-site metadata in MIT needs a separate correction because generic catalog/concentration evidence links were counted as course teaching sites. The latest live verified release remains `531073fe`.

Checkpoint `aae187ba` clean testing was interrupted by exhausted host disk space and is not a passed release. Root reclaimed reproducible Git archives and generated builds while retaining sources, commits and logs. MIT generic evidence links are now removed from public-course-site counts; actual teaching/OCW pages remain. The frozen source checkpoint `0ed8f3c` contains 10,408 original description summaries, 5,884 prerequisite statements, 171 verified teaching links and 153 syllabus links across 24,251 program-course records. The maintained database is 71,041,024 bytes; repeat ingestion, integrity and foreign keys passed. RIT is corrected to in progress because accessible GE/WI pool review remains. The 63-degree primary audit now stands at **2 audited, 50 blocked and 11 in progress**, with no full independent second-pass certification. Clean tests, CI and live checks are still pending; publication remains `531073fe` until all gates pass.

Candidate `ececd587` reproduced all 175 static files deterministically and passed fresh/maintained fact equivalence, but one stale RIT-status assertion failed among 2,859 passing tests (248 optional private-cache/historical skips). The assertion repair passed its 14-test suite. The next frozen source `d9c167b` preserves the 2/50/11 audit status, removes ordinary approval conditions from Lehigh/NJIT blocker descriptions, and includes 11,052 description summaries, 6,084 prerequisite statements, 191 verified teaching links and 173 syllabus links. Database size is 72,622,080 bytes; idempotence and integrity checks passed. Full verification and publication are pending. A fresh desktop/mobile live check still confirms Rice 13 fixed/26 options, three foundations/two systems, five Second majors, concentration parent labels and the collapsed filter pane at the previously verified release.


## Verified release dd797acc — 2026-10-11

Exact remote SHA `dd797acc5dbf1523e2467df77f8a5b82ee02c83c`; GitHub Actions [38119241621](https://github.com/KrisJordan/ai-program-atlas/actions/runs/38119241621) build and Pages deployment succeeded at 06:52 UTC. Clean locked tests: 2,879 passed, 250 optional private-cache/historical skipped; all56Chromium tests passed. Schema14,72,622,080-byte maintained database; fresh/maintained fact equivalence, repeat0, integrity/FK and175byte-identical files passed. Live public JSON matched every projected profile/award; product, ranking/audit, Rice/discovery, current-degree-fix and Stevens detail/comparison scripts passed at1440/390px with History API reload/back/forward, keyboard and no document overflow. Root inspected Stevens mobile screenshot. Published counts:168programs/194institutions;24,251course observations;19,687requirement nodes;11,052descriptions;6,084prerequisites;191actual teaching links;173syllabi. Primarydegree status2audited/50blocked/11progress;0fullindependent certifications. Full targetcohort incomplete.
