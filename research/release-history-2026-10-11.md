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
