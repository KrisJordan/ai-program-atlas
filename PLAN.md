# AI Program Atlas — research and publication plan

Updated 2026-10-11. A published research project; **the full target cohort and catalog inventory remain incomplete**.

## Immediate priority: degree correctness audit

The user reported Case Western showing zero computing foundations despite required data structures and algorithms. Inventory expansion is paused. All **63 standalone degree records across 25 institutions** are assigned to disjoint evidence reviews, including a separate cross-program second pass. The [audit contract](docs/DEGREE_AUDIT.md) defines independent source checks, per-course rationale, exact versions, required/option/prerequisite roles, manual expected sets and genuine blockers. Earlier completeness labels do not certify this new correctness audit.

Case Western's initial trace found correctly stored courses left `other` by a narrow classification helper. The verified core correction is committed: BA has eight fixed mapped courses (two foundations, three mathematics, three AI); BS adds one human-context course. Introductory programming remains a choice of one Python course or a Java-plus-Python bundle, represented by three option records. Case BA/BS primary elective and degree-wide classification reviews are now audited; full independent description coverage remains partial. Independent UI/source review and live publication of the bounded correction passed; the public site now shows the corrected values and explicit taxonomy review counts.

Shared taxonomy v1 now separates source-reviewed, mixed, unclassified and legacy/unreviewed course classifications, with relational evidence in migration 010. Empty or zero mapped categories never establish actual subject absence. Rank ordering and its eight additional browser tests are published in the same correction release. The audit continues beyond this checkpoint.

### Rice and discovery correction release

The user requested three further discovery refinements: a source-confirmed **Second majors** group; the actual parent program and award on every concentration/track card; and an accessible **Find a program** pane collapsed by default with visible active-filter context. Migration 013 separates those curricular relationships from awards and preserves source evidence, unknowns and revisions. All five additional-major catalog pages were reread successfully; all 50 concentration relationships have been inspected individually. Existing category ranks, family membership, IDs, comparison selections and shareable filter state remain part of the required browser gate.

The current published checkpoint carries these discovery refinements and subsequent degree corrections. It integrates all 63 primary audit entries: two primary reviews audited, 56 individually blocked, five in progress, and zero undocumented. No full independent second pass is certified. Migration through 015, repeat ingest (zero changes), database integrity and foreign keys passed; the maintained publication file is 80,265,216 bytes after compaction, retaining facts and history. Its 24,638 course observations and 19,743 requirement nodes contain 14,562 descriptions and 6,963 prerequisite statements. Course notes are now relationally stored and available through accessible HTML disclosures. The audit continues beyond publication.

Rice received a fresh independent 14-source review of all 43 represented course records. The maintained database now agrees with its manually checked 13 fixed identities: three computing foundations (COMP 140/182/215), two systems (COMP 222/329), one mathematics, five AI, one human-context and one domain course. Three reciprocal cross-lists reduce its 30 option source records to 26 identities. Desktop/mobile required/options/comparison regressions passed; public instructor-approved registration procedures resolve the statistics and vision restrictions as conditional paths, without implying permission was granted. Inconsistent summer versus fall/spring residency wording remains the sole documented Rice policy blocker, so its full-degree second-pass status remains partial. Concentration parent reviews are 47 verified, two partial on the award, and one university-wide immersion with no specific verified parent.

## Verified publication

- Repository: https://github.com/KrisJordan/ai-program-atlas
- Site: https://krisjordan.github.io/ai-program-atlas/
- Verified release: `6555510165abce8d4532e6ed06e9d38230c32a9c`, [successful CI and Pages deployment](https://github.com/KrisJordan/ai-program-atlas/actions/runs/38122729680).
- Fresh locked uv environment and clean committed source: **3,249 tests passed**, including all **58 required Chromium tests**. The 438 skipped cases require optional ignored source caches or historical snapshots; no browser tests were skipped.
- Fresh reconstruction and maintained publication copy passed integrity checks and agreed on current facts; additional historical coverage sources were preserved. Repeat ingest changed zero programs. Repeated static builds were byte-identical across 175 files.
- Live Rice has 13 fixed mapped identities including three computing foundations and two systems courses, with all 13 classifications reviewed; its 30 option source records resolve to 26 identities. All five second-major labels, all 50 concentration parent contexts, collapsed filters and active query persistence passed desktop/mobile checks. Live Case BA/BS fixed foundations both equal two; three introductory programming alternatives remain option records. All six ranking category/type panels passed ascending rank checks on desktop/mobile, including filtering, explicit name sort and history.
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
| Program-course records / resolved requirement nodes | 24,638 / 19,743 |
| Program families / concrete family variants | 2 / 31 |
| Descriptions / prerequisite statements | 14,562 / 6,963 |
| Credit amounts with verified units | 13,693 |
| Public course sites / example syllabi | 294 / 261 |

Caltech has one bounded no-qualifying-program finding after the current program directory and all 32 option/minor catalog pages were reviewed. It is a dated search result, not a claim about future offerings.

Course counts include elective pools and repeated observations across sibling programs. They are not unique institution-wide courses, required-course totals, completion percentages or quality scores. Complete refers to an explicitly reviewed scope: a complete minor/concentration/additional major does not certify the host degree. Metadata availability is separate. Zero pending in the loaded roster is not full target-cohort coverage; missing institutions remain outside that denominator.

## Cohort definition and boundaries

Qualifying official undergraduate titles contain AI or Artificial Intelligence, including source-defined GenAI and GeoAI compounds. Degrees, additional majors, minors and formal concentrations/tracks/emphases are distinct. Ordinary electives, research centers, informal interest areas, graduate credentials and surveyed certificates are excluded or retained as leads. A catalog-defined, formally declared specialization may qualify even when it is not a separate transcript credential; its exact institutional terminology, host degree and recognition limitations must remain explicit. See the [scope contract](docs/CONTRACT.md).

The target is **2027 U.S. News Best Colleges**, separately covering every institution ranked 100 or better in **National Universities** and **National Liberal Arts Colleges**, including all cutoff ties. The edition was released September 22, 2026. Category ranks are never combined.

National Universities has 108 cited secondary-table members, including nine tied at 100; authoritative primary enumeration remains unverified. Liberal arts has 86 documented members: 80 with edition-specific numeric evidence, three with explicitly qualified inferred editions, and three with verified top 100 membership but unknown exact ranks. Exact rank null never becomes 100. Both completeness flags remain false. Publisher restrictions were not bypassed. See [cohort research](research/cohort.md).

## Delivered architecture and product

- [x] Dedicated uv Python project, locked dependencies, architecture/contracts, agent ownership, research/refresh skills and incremental commits.
- [x] Maintained SQLite with migrations, integrity constraints, nested requirements, source provenance, catalog/fetch dates, revisions, scrape runs, changed-source detection and evidence-backed manual overrides.
- [x] Bounded robots-aware HTTP fetching, per-host pacing, cache, redirect validation, content limits and retries. Long crawl intervals are honored in bounded waits; Retry-After defers excessive waits. Raw sources stay ignored and unpublished.
- [x] Program-specific source adapters and adjacent Markdown notes. Partial/failed observations queue evidence without erasing reviewed facts; repeat observations do not duplicate candidates.
- [x] Reviewer-only completeness audits. Complete inherited inventories pin family content hashes; shared revisions and dependent variants transact atomically.
- [x] Carolina-blue/navy responsive sans-serif interface, keyboard navigation, filters, coverage ledger, detail pages and ranking methodology. No UNC marks or sponsorship claims.
- [x] Explicit families, expandable variants, discipline filtering, concrete comparison URLs, common/local requirements, provenance and missingness. Stable IDs and base-path reload/back/forward work on GitHub Pages.
- [x] Course-category and inferred-theme comparisons preserve credit units and separate source-stated learning outcomes, program aims and career pathways from editorial taxonomy. No opaque quality score.
- [x] Compact directory projection reduced root HTML about 69% raw and 64% gzipped in a controlled same-data comparison. Live root HTML is 4,274,438 bytes; full static detail pages and data.json remain intact. No runtime fetch/server added.
- [x] CI tests fresh reconstruction and publishes an updated copy of the maintained DB. Reviewed discovery classification corrections refresh correctly; manual program corrections and evidence history survive.

## Program families and current evidence

Northeastern's analyst-defined comparison family contains 23 independently verified combined degrees: 22 BS and one BSEnvE. Nine shared AI/core definitions plus 43 universal policy definitions are bound with program-specific provenance. All 14 Business concentration inventories are mapped with first/second concentration eligibility and conditional selection rules. Business, Biology and Design carry independently cited participating-college context. Participating colleges are not silently treated as permitted or mandatory home colleges. Exact allowed home-college options and applicable college rules remain a scope gap; all 23 degrees remain partial.

Buffalo's university-described AI+X family contains eight independently verified BS degrees sharing five framework notes. PPE's award is verified directly from its department. No identical course inventory is implied, and the two minors are outside this degree framework. The eight degrees now include independently accessible university policies and dated public Pathways candidates; detailed major catalog courses remain unverified. Dated general-education candidates are not represented as complete approved pools.

See [family contract](docs/PROGRAM_FAMILIES.md), [Northeastern evidence](research/program-families.md), [college applicability review](research/northeastern-policy-review.md) and [Buffalo evidence](research/families/buffalo-ai-plus-x.md).

## Meaning of a complete scoped inventory

A **complete requirement inventory** maps the cited program's applicable course choices, counts/credits, nested alternatives, admission or completion prerequisites, grades, overlap, residence/transfer and other completion policies. A degree includes its major and degree-wide college/university requirements. A minor, concentration or additional major covers that credential's own requirements and relationship to its host degree; it does not certify the whole host degree. Explicit open-ended approval rules can be represented; an unavailable finite approved list remains a gap. Completeness requires a reviewer audit and is never certified by the scraper.

This status does **not** mean complete program evidence. Course descriptions, individual course prerequisites and credits, public course sites, syllabi, source-stated learning outcomes and first-offered dates have separate evidence gaps. Unknown prerequisites never mean no prerequisites. Metadata availability is reported separately on the site; an empty outcome or launch date is unverified. If new course evidence exposes a substantive program-eligibility conflict, the requirement inventory returns to partial. See [review contract](docs/CURRICULUM_REVIEW.md).

## Current continuation

The verified public release remains **65555101** with the counts above. Its source, clean tests, CI/Pages and six live check scripts passed. Later source corrections are local until separately frozen and verified. Candidate 3d6587df was withheld after one outdated UCSB status assertion failed; the 3,550 other tests and deterministic reconstruction passed. The assertion is corrected with focused evidence checks. See [release history](research/release-history-2026-10-11.md).

The current primary ledger has **two audited, 58 individually blocked and three in progress** (MIT, UCSD and RIT); full independent certification remains zero. Inventory expansion remains paused for all 63 degree reviews. Workload and unread accessible sources are never access blockers.

- **MIT:** course descriptions are being checked against precise identities and historical/current versions. Historical renumbering now requires an explicit two-source observation. Registrar/department disagreements and remaining accessible content stay visible.
- **UCSD:** all eight college pools are mapped. Review of actual subject chapters continues, retaining paired components, joint undergraduate/graduate headings, cross-list evidence, current-code conflicts and exact unit amounts. A missing chapter heading is source-specific missingness, not nonexistence.
- **RIT:** all 77 local immersion routes have been read. The primary reviewer integrates finite menus only after the actual cards and route rules are reviewed. Nested groups, route overlap, excluded computing-college credits, variable credits and open approval routes remain distinct. The finite course queue is still active.
- **Purdue and UCSB:** identified accessible policy/course queues are exhausted; bounded primary reviews now document exact catalog access and source/version conflicts. This does not certify the entire degree. UCSB integrates all 856 reviewed general-education export rows, with current designation and exact prerequisite limits retained.
- **Other blocked degrees:** each has individual evidence, corrections and remaining questions in its primary ledger and adjacent notes. Miami's four reviews read all 7,727 course observations. USF's 152-course general-education pool is read; the exact catalog and brochure limits remain. Stevens retains unknown version/description facts and a human-verification boundary for further eligibility review.

## Remaining work and exact boundaries

1. **Finish the degree correctness audit.** Continue every identified accessible MIT, UCSD and RIT branch; either complete the audit or document its individual evidence blocker after the accessible queue is exhausted. Independent bounded checks do not certify whole degrees. Preserve required, option and contextual roles, individual course rationale and exact source versions.
2. **Complete the ranked cohort when permitted evidence is available.** Obtain an authoritative 2027 roster for both ranking categories and all cutoff ties. National Universities uses secondary enumeration; liberal arts still lacks at least 14 members before ties. Do not guess identities/ranks or certify full coverage. See [cohort research](research/cohort.md) and [liberal-arts follow-up](research/lac-cohort-evidence-2026-10-11.md).
3. **Resolve CSRankings reuse.** Numerical import is held for permission or qualified reuse review. The explicit proposed field membership, 2016–2025 U.S. window and computation are documented. Missing values remain null; publication rankings do not measure undergraduate teaching. See [reuse note](research/csrankings.md).
4. **Preserve source boundaries.** Seven loaded institutions remain inaccessible and seven published curricula pending. Use ordinary permitted public sources for transport/rendering gaps; do not bypass robots, authentication, paywalls or human-verification challenges. See [access review](research/access-review.md), [pending barriers](research/pending-curriculum-barriers.md) and individual notes.
5. **Keep scope and missingness explicit.** The 115 partial published requirement inventories, course metadata, verified teaching sites/syllabi, launch dates and source-stated outcomes are separate gaps. A confirmed title is not an exhaustive institution search. Caltech's single bounded absence finding does not establish absence elsewhere.
6. **Publish only tested snapshots.** Freeze committed evidence and primary ledgers, ingest into maintained SQLite, repeat to zero changes, verify foreign keys/integrity, compare fresh and maintained current facts, reproduce the build, run locked clean tests with required Chromium, push the exact tested SHA, then verify CI/Pages and the live site. Preserve newer agent work outside the snapshot.

See the [audit contract](docs/DEGREE_AUDIT.md), source-specific adapter notes, dated survey ledgers and [release history](research/release-history-2026-10-11.md). `uv run atlas status` and `uv run atlas candidates` expose maintenance work. Refreshes queue observations for review and preserve manual corrections; they do not silently replace reviewed database facts. The full cohort and audit remain incomplete beyond any publication checkpoint.
