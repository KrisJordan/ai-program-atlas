# AI Program Atlas — research and publication plan

Updated 2026-10-11. A published research project; **the full target cohort and catalog inventory remain incomplete**.

## Immediate priority: degree correctness audit

The user reported Case Western showing zero computing foundations despite required data structures and algorithms. Inventory expansion is paused. All **63 standalone degree records across 25 institutions** are assigned to disjoint evidence reviews, including a separate cross-program second pass. The [audit contract](docs/DEGREE_AUDIT.md) defines independent source checks, per-course rationale, exact versions, required/option/prerequisite roles, manual expected sets and genuine blockers. Earlier completeness labels do not certify this new correctness audit.

Case Western's initial trace found correctly stored courses left `other` by a narrow classification helper. The verified core correction is committed: BA has eight fixed mapped courses (two foundations, three mathematics, three AI); BS adds one human-context course. Introductory programming remains a choice of one Python course or a Java-plus-Python bundle, represented by three option records. Full elective and degree-wide classification review remains in progress. Independent UI/source review and live publication of the bounded correction passed; the public site now shows the corrected values and explicit taxonomy review counts.

Shared taxonomy v1 now separates source-reviewed, mixed, unclassified and legacy/unreviewed course classifications, with relational evidence in migration 010. Empty or zero mapped categories never establish actual subject absence. Rank ordering and its eight additional browser tests are published in the same correction release. The audit continues beyond this checkpoint.

### Next release in preparation

The user requested three further discovery refinements: a source-confirmed **Second majors** group; the actual parent program and award on every concentration/track card; and an accessible **Find a program** pane collapsed by default with visible active-filter context. Migration 013 separates those curricular relationships from awards and preserves source evidence, unknowns and revisions. All five additional-major catalog pages were reread successfully; all 50 concentration relationships are being inspected individually. Existing category ranks, family membership, IDs, comparison selections and shareable filter state remain part of the required browser gate.

This release will also carry the intervening degree corrections, including verified cross-list identities and known zero-credit requirements. A committed-source integration at `a43d56b` passed repeat ingest, migration, integrity and foreign-key checks: 58 of 63 primary audit entries were documented (22 with specific source blockers and 36 in progress; five entries pending documentation). None was yet certified as a completed full-degree audit or complete second pass. This is a checkpoint, not current publication or the end of the audit.

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
- [x] Compact directory projection reduced root HTML about 69% raw and 64% gzipped in a controlled same-data comparison. Live root HTML is 3,885,551 bytes; full static detail pages and data.json remain intact. No runtime fetch/server added.
- [x] CI tests fresh reconstruction and publishes an updated copy of the maintained DB. Reviewed discovery classification corrections refresh correctly; manual program corrections and evidence history survive.

## Program families and current evidence

Northeastern's analyst-defined comparison family contains 23 independently verified combined degrees: 22 BS and one BSEnvE. Nine shared AI/core definitions plus 43 universal policy definitions are bound with program-specific provenance. All 14 Business concentration inventories are mapped with first/second concentration eligibility and conditional selection rules. Business, Biology and Design carry independently cited participating-college context. Participating colleges are not silently treated as permitted or mandatory home colleges. Exact allowed home-college options and applicable college rules remain a scope gap; all 23 degrees remain partial.

Buffalo's university-described AI+X family contains eight independently verified BS degrees sharing five framework notes. PPE's award is verified directly from its department. No identical course inventory is implied, and the two minors are outside this degree framework. The eight degrees now include independently accessible university policies and dated public Pathways candidates; detailed major catalog courses remain unverified. Dated general-education candidates are not represented as complete approved pools.

See [family contract](docs/PROGRAM_FAMILIES.md), [Northeastern evidence](research/program-families.md), [college applicability review](research/northeastern-policy-review.md) and [Buffalo evidence](research/families/buffalo-ai-plus-x.md).

## Meaning of a complete scoped inventory

A **complete requirement inventory** maps the cited program's applicable course choices, counts/credits, nested alternatives, admission or completion prerequisites, grades, overlap, residence/transfer and other completion policies. A degree includes its major and degree-wide college/university requirements. A minor, concentration or additional major covers that credential's own requirements and relationship to its host degree; it does not certify the whole host degree. Explicit open-ended approval rules can be represented; an unavailable finite approved list remains a gap. Completeness requires a reviewer audit and is never certified by the scraper.

This status does **not** mean complete program evidence. Course descriptions, individual course prerequisites and credits, public course sites, syllabi, source-stated learning outcomes and first-offered dates have separate evidence gaps. Unknown prerequisites never mean no prerequisites. Metadata availability is reported separately on the site; an empty outcome or launch date is unverified. If new course evidence exposes a substantive program-eligibility conflict, the requirement inventory returns to partial. See [review contract](docs/CURRICULUM_REVIEW.md).

## Current work after the verified release

The 168-program correction release is a checkpoint. It includes the four paths committed before the audit priority change, completed RIT immersion/CMU concentration/WPI local inventory work, and verified degree-data corrections. **Inventory expansion is paused for the full 63-degree correctness audit.**

The published audit ledger has **zero fully audited, one blocked, 27 in progress and 35 awaiting documented results**; all are assigned. Bounded independent checks verify Case's fixed core/programming routes and WPI's fixed/choice roles without certifying their entire degrees. Subsequent committed reviews cover Lehigh, Northwestern and Rice, while additional Northeastern, RIT, Buffalo, Delaware and Penn State corrections are being prepared for the next checkpoint. Accessible unfinished work remains in progress, never an invented access blocker.

All requested navigation changes, required/options views and the initial correctness correction are published and verified at `cf263e40`. The maintained publication SQLite snapshot is 71,532,544 bytes with migration 010, retaining revisions and manual corrections. Migration 011 subsequently preserves source-known zero-credit requirements (not missing values), with positive credit-choice constraints; 91 focused tests and a maintained-copy migration preserved all facts/history/family bindings.

- **Required versus options:** profiles use resolved family graphs and separate fixed mapped courses, elective/required-choice option pools and unresolved roles. Counts are distinct IDs, never degree proportions or summed credits. Choice loads remain individual source rules. Large pools, overlapping groups, nested alternatives, unknown credits and family replacements have regression coverage. Real-data review found UCSD college/cohort branches falsely attached as universal roots; the adapter and seed now preserve their conditional ancestry, reducing fixed courses from 19 to eight without removing any evidence. Cohort, placement, waiver and substitution caveats remain visible.
- **Homepage organization:** National Universities and National Liberal Arts Colleges use actual ranking evidence. Each group has Majors, Concentrations and Minors tabs; Majors includes separately labeled additional majors and BS/BSE/BA/Other filters. Verified multi-award options retain exact labels and evidence; unusual labels are not guessed from abbreviations or hosting units. Independent URL state, back/forward, active counts, family variants, comparison selections, keyboard operation and mobile layout passed clean and live publication checks.

- **Institution discovery:** ordinary liberal-arts depth reviews cover the loaded roster's assigned queue, with readable and unresolved branches documented separately. An 18-candidate official-news follow-up verified no additional 2027 cohort member; wrong editions and component ranks were rejected. A further Knox official-news follow-up also found no edition-specific addition; its rank is undated and returned archive incomplete. The roster remains incomplete. See [membership follow-up](research/lac-cohort-evidence-2026-10-11.md).
- **National Universities:** deeper directory and concentration reviews continue across the remaining inspected pool. Yeshiva, UNC–Chapel Hill, American, San Diego and UT Austin are now published. A further bounded review of six already-confirmed universities found additional formal Stanford, Northwestern and Rice paths; their adapters are in progress. Certificates remain excluded rather than relabeled. See dated `data/surveys/national-*` and adjacent research notes.
- **MIT:** all 43 registrar HASS fields have a dated review ledger: 39 mapped and four source questions. Public CMS/W pages were verified through ordinary Chrome interaction. Music/Theater current department pages succeeded with ordinary network-enabled robots-aware fetches; source-specific concentration rules are mapped. Prior restricted-shell transport failures were not publisher denials. The degree remains partial because of source/cohort conflicts and remaining policies. See [field ledger](research/mit-hass-field-review-2026-10-11.json).
- **UCSD/UCSB:** all eight principal UCSD college pools are mapped; linked discipline, transfer and examination-policy checks continue. UCSB's current guide, progression and transfer policies are mapped; science-list/course-credit/capstone ambiguity and dynamic GE pools remain explicit.
- **Miami/Northeastern:** all 215 active Miami cognate pages have been captured and reviewed; blank/conflicting plans and applicability gaps keep the degrees partial. Northeastern's 1,593 course observations now have names/descriptions, while exact home-college applicability remains unresolved. Large option pools are not portrayed as mandatory-course counts.
- **Product review:** family collapse persistence, comparison focus and stale Case overview fixes are live. Two six-program metadata passes now add descriptions, enrollment restrictions, credit evidence and explicitly typed program aims. Ohio State and MSU inventories returned to partial because new course evidence exposed unresolved eligibility conflicts; missing launch dates remain null. The new profile and grouped navigation changes passed combined clean and live browser validation.
- **New concentration policies:** UT and Yeshiva gained exact-match course metadata and scoped declaration, grade, transfer, residence and approval rules after the verified release. American and San Diego policy reviews are in progress; remaining conflicts are retained. See [policy review](research/concentration-policy-review-2026-10-11.md).
- **SQLite storage:** migration 008 stores composite requirement keys without redundant rowid indexes. A maintained-copy check preserved the full export, all revisions and source snapshots; 106 focused tests passed. After release ingestion and compaction, the maintained file is 69,058,560 bytes. See [storage validation](research/sqlite-storage-layout.md).
- **Parser compatibility:** Soup Sieve 3.0.1 failed valid tag/attribute selectors in both local and fresh Python 3.11.4 environments. The dependency is now constrained to verified 2.x, with six regression probes. See [compatibility evidence](research/parser-compatibility.md).

## Remaining work and exact boundaries

1. **Ranked cohort:** obtain a permitted authoritative 2027 roster for both categories and every cutoff tie. National Universities has a secondary-table enumeration; liberal arts still lacks at least 14 members before accounting for ties. Do not certify full coverage or guess missing identities/ranks. Publisher access restrictions and the failed official-news branches remain documented.
2. **CSRankings:** numerical import is held for permission or qualified reuse review. Methodology records `ai`, `vision`, `mlmining`, `nlp`, `inforet`, the proposed 2016–2025 U.S. window, source snapshot and computation method. Missing values remain null; publication research does not measure undergraduate teaching. See [reuse note](research/csrankings.md).
3. **Access:** seven loaded institutions remain inaccessible in the verified release. Seven published curricula remain pending. RIT’s immersion now has a complete local inventory; Delaware’s concentration has public policy evidence and remains partial. Delaware’s exact current catalog pool remains restricted. A normal public browser may resolve transport or dynamic-rendering gaps; robots, authentication and explicit restrictions are never bypassed. See [pending barriers](research/pending-curriculum-barriers.md), [access review](research/access-review.md), and each adapter's notes.
4. **Requirement inventories:** 115 published records remain partial. Eight WPI local concentration reviews were completed; business/social allocation ambiguities remain explicit. These local inventory labels are separate from the ongoing whole-degree correctness audit. Finish finite eligible lists, nested alternatives, home-college applicability and completion policies where accessible. Source disagreements need documentary reconciliation; elapsed time or program marketing cannot resolve them. Every proposed promotion requires an explicit scoped audit.
5. **Institution search depth:** a confirmed program proves that title exists, not that every program at the institution was found. Inspected records retain the areas searched and unreviewed. Caltech alone has the documented bounded no-qualifying-program finding; no global absence is implied.
6. **Course metadata:** descriptions, prerequisites, exact credits, public sites, syllabi, launch dates and outcomes remain separately incomplete. Match exact course identity/term; source-stated aims and careers stay distinct from learning outcomes and analyst taxonomy. Do not redistribute raw copyrighted catalogs.
7. **Next publication:** freeze committed evidence, ingest into the maintained database, repeat to zero changes, check foreign keys/integrity, compare fresh and maintained current facts, reproduce the static build, run locked clean tests with required Chromium, push that tested commit, and verify both CI/Pages and the public site. Preserve WIP and newer commits outside the tested release.

The [initial gap triage](research/curriculum-gap-triage.md) is a dated starting snapshot; subsequent adapter notes and dated survey ledgers are the current evidence. [Historical release notes](research/release-history-2026-10-11.md) retain the earlier checkpoints without presenting obsolete counts as current. Use `uv run atlas status` and `uv run atlas candidates` to inspect maintenance work. Refreshes queue observations for review and preserve manual corrections; they do not silently replace the research database.
