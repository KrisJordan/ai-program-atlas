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

Exact remote SHA `dd797acc5dbf1523e2467df77f8a5b82ee02c83c`; GitHub Actions [38119241621](https://github.com/KrisJordan/ai-program-atlas/actions/runs/38119241621) completed build and Pages deployment at 06:52 UTC. Clean locked tests: 2,879 passed, 250 optional private-cache or historical cases skipped; all 56 Chromium cases passed. The maintained database uses schema 014 and occupies 72,622,080 bytes. Fresh and maintained current facts agree; repeat ingestion changes zero programs; integrity, foreign keys, and 175 byte-identical build files passed.

Live public JSON matched every projected curriculum profile and award bucket. Product, ranking, audit, Rice/discovery, current-degree correction, and Stevens checks passed at desktop and 390px mobile widths, including keyboard navigation and reload/back/forward. The Stevens mobile screenshot was visually inspected. Published coverage: 168 programs at 194 institutions; 24,251 course observations; 19,687 requirement nodes; 11,052 description summaries; 6,084 prerequisite statements; 191 teaching links; 173 syllabi. Primary degree reviews: two audited, 50 individually blocked, and 11 in progress. No full independent second-pass certification. The full target cohort remains incomplete.

## Unpublished candidate 93f1afce — 2026-10-11

The clean suite passed 3,065 cases and skipped 428 optional private-cache or historical cases, but one required mobile browser case failed: Stevens source locator fingerprints extended the 390px page to 501px. This candidate was not published. Fresh and maintained current facts agreed, repeat ingestion changed zero programs, integrity and foreign keys passed, and all 175 static files were deterministic.

Commit `3846967` fixes the cause with wrapping scoped to source citation paragraphs. It retains the full evidence text. Both real Stevens desktop/mobile cases and both no-JavaScript course-note cases pass, along with 15 site/note tests. The next complete release must still pass the full clean suite, CI/Pages, and live verification.

## Unpublished candidate 2d77063d — 2026-10-11

The complete clean suite passed 3,193 tests, including the repaired mobile browser checks, and skipped 434 optional private-cache or historical cases. Three old RIT tests expected the earlier 43-record inventory to still equal the entire expanded degree graph. This candidate was not published. Fresh and maintained facts agreed, repeat ingestion was unchanged, and 175 static files were deterministic.

Commit `acd03e6` declares the existing independent review's exact bounded inventory without altering its manually transcribed IDs, roles, or categories. New immersion records remain outside that independent certification. Tests still reject deletion of a reviewed course, changes to its role or subject, and promotion of later immersion additions into universal fixed requirements. All 44 affected tests pass. This is a scope correction, not an independent source review of new records.


## Verified release 65555101 — 2026-10-11

Exact remote SHA `6555510165abce8d4532e6ed06e9d38230c32a9c`; GitHub Actions [38122729680](https://github.com/KrisJordan/ai-program-atlas/actions/runs/38122729680) completed build and Pages deployment at 07:54 UTC. Clean locked tests: **3,249 passed**, 438 optional private-cache or historical cases skipped; all **58 required Chromium cases passed**. Schema 015 maintained database: 80,265,216 bytes. Fresh and maintained current facts agree; repeat ingestion changed zero programs; integrity, foreign keys and all 175 byte-identical static files passed.

All six live scripts passed: public facts and projected profiles, rankings/audit, Rice and discovery refinements, current degree corrections, Stevens detail/comparison, and native course-note disclosures. Desktop and 390px mobile checks include keyboard, direct navigation, comparison reload/back/forward and no-JavaScript notes. Source fingerprints wrap without document overflow.

Published coverage: 168 programs at 194 institutions; 24,638 course observations; 19,743 requirement nodes; 14,562 original description summaries; 6,963 prerequisite statements; 13,693 credit amounts with verified units; 294 actual teaching links; 261 syllabus links. Primary degree reviews: two audited, 56 individually blocked, five in progress. No full independent second-pass certification. The target cohort remains incomplete. Newer source commits are excluded from this exact verified checkpoint.


## Frozen continuation 3d6587df — not published

The source snapshot 1c2c4d8 produced 25,758 course observations, 19,854 requirement nodes, 16,288 descriptions, 7,383 prerequisite statements, 301 teaching links and 265 syllabus links. The 84,279,296-byte maintained schema-015 database passed repeat-zero ingestion and integrity checks. Fresh and maintained facts agreed, and 175 build files reproduced byte-for-byte. The full clean run passed 3,550 tests, including every required browser case, with 453 optional-cache/historical skips, but one UCSB status assertion still expected in-progress after the documented bounded closure. Candidate publication was withheld. Commit 16e1d84 corrects that evidence-specific assertion; its 20 focused tests passed. A new frozen release must pass all gates.

## Candidate 95b9648b — clean checks passed, publication withheld for clarification

The exact frozen candidate passed **3,701 tests**, including all **58 required Chromium cases**, with 454 optional private-cache/historical skips. Fresh and maintained current facts agreed, repeat ingestion changed zero programs, database integrity/foreign keys passed, and all 175 static files reproduced byte-for-byte. Its source checkpoint was 304ae0d; maintained database size was 86,056,960 bytes.

Candidate facts: 168 programs / 194 institutions, 25,988 course observations, 19,921 requirement nodes, 16,688 descriptions, 7,500 prerequisite statements, 15,718 credit amounts with known units, 304 actual teaching links and 268 syllabi. Audit status remained two audited, 58 blocked and three in progress.

During continuing independent review, a Theatre Ensemble requirement explanation was found to contain a copied sentence about variable-credit music ensembles. The actual PRFL-220 credit amount and three-enrollment graph were already correct. Commit 568dc66 clarifies the fixed one-credit theatre card and three-enrollment rule and adds focused assertions. Publication is withheld until the clarification is part of a new tested snapshot. GitHub/Pages and live checks were therefore not run for 95b9648b; the last verified public release remains 65555101. This is a prepublication wording correction, not a failed test run.

## Verified bounded primary release c90c128e

Exact remote source snapshot `c90c128e7e341d751dd51e7c17007ade052eb592`; GitHub Actions [38130959873](https://github.com/KrisJordan/ai-program-atlas/actions/runs/38130959873) completed build and Pages deployment successfully. Clean locked archive tests: **4,083 passed**, **454 optional source-cache/historical cases skipped**, including all **58 required Chromium cases passed**. Fresh and maintained current facts agree; repeat ingestion changed zero programs; integrity, foreign keys and all **175 byte-identical build files** passed. The maintained schema-015 database is **88,653,824 bytes**; root HTML is 4,428,008 bytes.

All six live check scripts passed against this publication: public data and every projected profile/award, rankings and audit, Rice/discovery refinements, current degree corrections, Stevens detail/comparison, and native course-note disclosures. Checks cover desktop and 390px mobile layout, direct paths, keyboard, comparison reload/back/forward and no-JavaScript disclosures. Representative screenshots were visually reviewed.

Verified inventory: **168 programs / 194 institutions; 26,119 course observations; 19,961 requirement nodes; 17,728 descriptions; 8,323 prerequisite statements; 16,717 credit amounts with known units; 305 course-site links; 269 syllabi**. Primary degree outcomes: **two audited, 61 individually blocked, zero in progress, zero pending**. Full independent certification remains zero. The 652 UCSD code-only records are now 605 actual descriptions and 47 exact-heading dispositions; earlier section preparation is corrected on 191 ETHN/POLI records. MIT and RIT finite queues are reconciled. No claim of complete target-cohort enumeration, exhaustive institutional search or resolution of the remaining degree policy/version/access questions is made.


## Verified bounded independent core release d4e1e2ab

Deployed source/data SHA `d4e1e2ab02ba3c5d3d39ec297c16cd5f3b2c63de`; GitHub Actions [38134035980](https://github.com/KrisJordan/ai-program-atlas/actions/runs/38134035980) completed build and Pages deployment successfully at 11:05 UTC. Clean locked archive tests: **4,199 passed**, including all **60 required Chromium cases**; **456 optional source-cache/historical cases skipped**. Fresh and maintained current facts agree, repeat ingestion changes zero programs, integrity and foreign keys pass, and all **175 static files reproduce byte-for-byte**. The maintained schema-015 SQLite file is **92,229,632 bytes**; root HTML is 4,428,402 bytes.

All 63 primary degrees now have independent bounded dimension ledgers. Fixed requirements: **47 verified within scope, three partial, 13 unverified**. Choice rules: one verified, 59 partial, three unverified. Chart classification: two verified, 59 partial, two unverified. Many partial classification reviews verify their fixed/core scope while leaving broader option/context records outside certification. The primary whole-degree result remains **two audited and 61 individually blocked**, with zero full independent whole-degree certifications; this does not label 61 core charts unusable.

Actual source rereads correct NJIT MGMT 422, USF PSY 2012, Northeastern CRIM 3600 and INTL 2718, and UCSB CMPSC 25 and CMPSC 183 without changing their fixed memberships. UCSD SIO 109/POLI 117 is a verified reciprocal cross-list with mixed technical/policy content: fixed eight and options 119 remain unchanged; contextual chart identities become 2,240 from 2,241 source records. The separate online pair is not merged. CHEM 174 explicitly names SIO 141, but the current SIO chapter lacks its exact body, so version/identity reconciliation stops at that documented boundary. Rice retains 13 fixed, 26 option identities and three computing-foundations courses; all three bounded dimensions are verified while the residence-policy conflict remains separate. WPI's exhaustive three-of-three foundation sequence remains fixed under a narrow source-reviewed judgment.

Live public data matched every projected profile and award bucket. Desktop and 390px mobile checks passed all 63 dimension records, correction assertions, direct detail pages, keyboard disclosures, grouped tabs/filters, comparison selection and reload/back/forward without JavaScript errors or document overflow. Rice audit screenshots were visually inspected. Nine representative live files (root, data, CSS, JavaScript, coverage, methodology and Rice/UCSB/UCSD pages) byte-match the frozen build. Subsequent closeout Markdown does not change the deployed checkpoint.

Inventory remains **168 programs at 194 loaded institutions**, with 26,119 program-course observations and 19,961 requirement nodes. Full ranked-cohort enumeration, exhaustive institutional searches, broad option/context certification and CSRankings numerical reuse remain explicit gaps. No MIT Stellar or other denied source was retried. No broad unrelated GE extraction was added.


## Verified Sol-medium sixteen-case closeout — 2026-10-11

Source **b5131baee11ffc4b371e9c1b9be9e5c3e5b08d4f** is verified live. All16 fixed-requirement cases were investigated and independently checked: Purdue BS reaches scoped department-major verification, Buffalo Economics gains19 fixed/16 option title identities, and14 retain exact available-source boundaries. Overall fixed dimensions are48 verified/3 partial/12 unverified; whole-degree status remains2 audited/61 blocked, with zero full independent certification. Stevens’ reconstructed named-choice claim was corrected to actual-source numeric/topology scope. No denied route or MIT Stellar was retried.

The schema016 maintained database preserves history/manual corrections and contains26,154 course observations and19,970 requirement nodes across168 programs/194 institutions. Clean locked tests passed4,251 including all62 required Chromium cases;457 optional ignored source-cache/historical cases skipped. Fresh/maintained facts, repeat-zero ingestion, integrity/FKs and175 deterministic files passed. [CI/Pages](https://github.com/KrisJordan/ai-program-atlas/actions/runs/38143199273) succeeded; ten live files byte-match the frozen build. All16 live review outcomes, unknown-code facts, projected profiles, grouped filters, keyboard disclosures, direct details and comparison reload/back/forward passed desktop/390px checks with inspected screenshots and no errors/overflow. Root HTML is4,434,808bytes.

Two earlier source candidates were rejected before publication: e67e8ef7 omitted explicit zero category keys in one primary expected map;78949e9 corrected that map but required regeneration of its compiled audit export. The published replacement includes both repairs and passed the full gate. Cohort enumeration, institution-wide inspection, CSRankings reuse, degree policy conflicts and exact source boundaries remain incomplete. Subsequent closeout Markdown does not change this tested deployed source/data SHA.

## University priority / five additional majors / CSRankings release

Source/data 2b9a170400628d34b65dd27eb14ed115388a413b, [CI/Pages 38146720730](https://github.com/KrisJordan/ai-program-atlas/actions/runs/38146720730). Fourteen university-only follow-ups accepted; Furman deferred. Stevens fixed scope advances to partial with 24 draft identities and an explicit three-course catalog conflict. Global fixed dimensions: 48 verified / 4 partial / 11 unverified. Five additional-major peer reviews accepted: fixed: 5 verified; choices/classification: 4 verified + 1 partial; eligibility: 3 verified + 2 partial. Whole host-degree certification is excluded.

CSRankings original upstream JavaScript independently matched 961 observed scores/ranks and 245 null no-output rows for 201 U.S. registry institutions; 91 of 194 Atlas institutions matched, 103 not listed. Snapshot 5e8a27d68310c728a182b8bb3b6437c39bce0cad, 2016–2025, five AI fields plus aggregate; educational owner-confirmed permission and attribution retained. Migration 017 stores immutable reviewed artifacts.

Clean locked release: 4,331 passed / 463 optional skips, all 66 browser cases; fresh/maintained facts agree; repeat: zero changes; integrity/FKs pass; 175 deterministic files. Twelve live files byte-match; direct additional-major details, research/methodology, mobile/desktop keyboard and comparison history passed; general discovery filters/profile navigation also passed. Screenshots inspected. Six program records changed; 168 programs / 194 institutions / 26,154 course observations / 20,000 requirements. Current completeness remains 46 complete / 115 partial / 7 pending scoped inventories.


## Compact table homepage and modal filters

Source **7ab48e1319c189ee0e3e1f8a8743cc3481ea7e39**, [CI/Pages 38150477614](https://github.com/KrisJordan/ai-program-atlas/actions/runs/38150477614). Coverage/stat boxes removed from the homepage; search and award filters moved into a keyboard-accessible native dialog. Concrete programs default to a semantic five-column table. Optional cards, numeric aggregate research sorting, verified ranking provenance, exact awards and Additional Major labeling, comparisons and nested-base-path History API state are preserved. Content-hashed asset queries align CSS/JS with publication.

Clean locked suite: **4,346 passed / 463 optional skips**, all **75 required browser cases**. Fresh/maintained facts agree; repeat ingestion changes zero programs; integrity/FKs and **175 deterministic build files** pass. Four live files byte-match the frozen build. Actual desktop/mobile checks pass with first National University rows above the fold (603px/900px and733px/844px), no document overflow or browser errors, sorting, modal state, comparison reload/back/forward, optional view switching and direct detail navigation. Inspected screenshots confirm the layout. Root HTML:4,865,659bytes. Inventory and research/audit facts unchanged.

Northeastern institution filtering shows **24 recorded majors**, including Chemical Engineering and AI, BSChE. Rechecked official2026–2027 catalog confirms the exact award and matching AI core. Existing local requirements remain independent of the combined-degree family's policy inheritance. Family membership needs a source-backed applicability/binding review; this release does not assert membership or promote completeness. Adapter notes and PLAN.md record that next check. Subsequent documentation-only closeout preserves this deployed source SHA.

## Curriculum matrix, requirement hierarchy and parent labels

Published source c77ba6b643de4f0ceaf2d52b94b06093ee407490, CI/Pages https://github.com/KrisJordan/ai-program-atlas/actions/runs/38176463397 . The table groups Northeastern joint degrees with individual comparison, puts checkboxes first, combines award/program labels and adds seven Required Curriculum counts. Shared graph logic counts fixed identities plus countable mandatory choose-N obligations; mixed, nested, credit-only and overlapping rules remain separately documented. UMD Computing becomes 3 while missing individual descriptions retain their unverified status. Detail pages lead with outcomes, then curriculum/rankings, native hierarchical disclosures and evidence/audit footer. Concentrations show recorded parent awards/names; minor/concentration rows omit award prefixes and their detail badges omit redundant award types.

Preceding source clean Mac suite: 4,357 passed/463 optional skips/all 79 browser cases. Final follow-up clean focused suite: 27 passed, including two additional browser cases. Final full Linux CI: 3,796 passed/1,027 optional source-cache/historical skips/all 81 required browser cases. Fresh/maintained facts agree, repeat ingest 0, integrity/FKs pass, 176 files reproduce. Five live files byte-match; desktop/mobile parent labels, UMD counts across three views, joint expansion, comparison/history and direct requirement fragments pass. Root 5,277,104 bytes; DB 92,225,536 bytes/schema017. Research coverage and audit limitations remain unchanged.


## Requirements reading / 033d999

Published source 033d999ad6f6fc288a740ff3bcb5b6644845019d; [CI and Pages](https://github.com/KrisJordan/ai-program-atlas/actions/runs/38179073987) succeeded. Clean Mac: 4,366 passed / 463 optional skips; Linux CI: 3,802 passed / 1,027 optional skips; all 83 required browser cases pass. Every one of 20,000 requirement IDs remains in 168 pages. Reruns, database integrity, current-fact agreement and 176-file deterministic export pass. Six live files match; desktop/mobile disclosures, all-of titles, deep-note reload, prerequisite links and rankings above Sources pass. Published data.json is unchanged. Research limits remain recorded in PLAN.md.


## Universal context hierarchy, density and AI literacy / b196cb9

Published b196cb9966e5289fc8d58f02cefc7a78fbed9862; [CI and Pages](https://github.com/KrisJordan/ai-program-atlas/actions/runs/38181189274) succeeded. Clean Mac: 4,376 passed / 463 optional skips; full Linux CI: 3,812 / 1,027 optional skips; all 87 mandatory browser cases pass. Restore course-bearing note headings, separate explicit general education after program courses at root and nested levels, respect major-scope exclusion wording, and compact requirement/outcome text. Every one of 20,000 requirement IDs remains present across 168 pages.

UNC DATA117 is reviewed Applications with official catalog evidence/rationale; its parser proposals are identity/description guarded and cannot overwrite curated reviews. Updated taxonomy guidance distinguishes technical AI methods, practical literacy/tool use, ethics-primary study and mixed/unknown content. Four legacy leads await actual source review. SQLite integrity/FKs, fresh/current-fact agreement, repeat ingest0 and 176 deterministic files pass; DB92,250,112 bytes/schema017. Nine deployed files match the build. Live desktop/mobile MIT/UNC/UCSD, keyboard/deep-fragment/reload, comparison, provenance and compact layout checks pass without errors/overflow. Research/audit coverage limits remain unchanged.
