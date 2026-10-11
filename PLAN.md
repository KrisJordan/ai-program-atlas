# AI Program Atlas — research and publication plan

Updated 2026-10-11. A published research project; **the full target cohort and catalog inventory remain incomplete**.

## Verified publication

- Repository: https://github.com/KrisJordan/ai-program-atlas
- Site: https://krisjordan.github.io/ai-program-atlas/
- Verified release: `7ae8cf4dfbb4f7b45c6baf8621347c2495acb375`, [successful CI and Pages deployment](https://github.com/KrisJordan/ai-program-atlas/actions/runs/38101661236).
- Fresh locked uv environment and clean committed source: **1,322 tests passed**, including all **17 required Chromium tests**. The 111 skipped cases require optional ignored source caches or historical snapshots; no browser tests were skipped.
- Fresh reconstruction and maintained publication copy passed integrity checks and agreed on current facts; additional historical coverage sources were preserved. Repeat ingest changed zero programs. Repeated static builds were byte-identical across 143 files.
- Live public JSON matched these counts. Live checks passed keyboard family expansion, concrete comparison reload, discipline back/forward, direct program pages, learning/career statement distinctions and 390px mobile layout, with no JavaScript errors or horizontal overflow.
- Dedicated local repository: `ai-program-atlas/` in this Mac Studio task. No existing personal website or unrelated repository was changed. Coordinated Astra high research and implementation use explicit ownership and incremental commits.

## Published coverage

| Measure | Verified count |
| --- | ---: |
| Institutions in loaded roster | 194 |
| National Universities / National Liberal Arts Colleges | 108 / 86 |
| Confirmed qualifying title / partially inspected / inaccessible | 67 / 118 / 8 |
| Loaded institutions pending / absence conclusions | 0 / 1 |
| Concrete programs | 136 |
| Degrees / minors / concentrations / additional majors | 60 / 48 / 25 / 3 |
| Complete / partial / pending requirement inventories | 36 / 93 / 7 |
| Program-course records / resolved requirement nodes | 22,480 / 16,033 |
| Program families / concrete family variants | 2 / 31 |
| Descriptions / prerequisite statements | 1,839 / 2,651 |
| Credit amounts with verified units | 8,591 |
| Public course sites / example syllabi | 78 / 72 |

Caltech has one bounded no-qualifying-program finding after the current program directory and all 32 option/minor catalog pages were reviewed. It is a dated search result, not a claim about future offerings.

Course counts include elective pools and repeated observations across sibling programs. They are not unique institution-wide courses, required-course totals, completion percentages or quality scores. Complete refers to an explicitly reviewed scope: a complete minor/concentration/additional major does not certify the host degree. Metadata availability is separate. Zero pending in the loaded roster is not full target-cohort coverage; missing institutions remain outside that denominator.

## Cohort definition and boundaries

Qualifying official undergraduate titles contain AI or Artificial Intelligence, including source-defined GenAI and GeoAI compounds. Degrees, additional majors, minors and formal concentrations/tracks/emphases are distinct. Ordinary electives, research centers, informal interest areas, graduate credentials and surveyed certificates are excluded or retained as leads.

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
- [x] Compact directory projection reduced root HTML about 69% raw and 64% gzipped in a controlled same-data comparison. Live root HTML is 2,785,533 bytes; full static detail pages and data.json remain intact. No runtime fetch/server added.
- [x] CI tests fresh reconstruction and publishes an updated copy of the maintained DB. Reviewed discovery classification corrections refresh correctly; manual program corrections and evidence history survive.

## Program families and current evidence

Northeastern's analyst-defined comparison family contains 23 independently verified combined degrees: 22 BS and one BSEnvE. Nine shared AI/core definitions plus 43 universal policy definitions are bound with program-specific provenance. All 14 Business concentration inventories are mapped with first/second concentration eligibility and conditional selection rules. Business, Biology and Design carry independently cited participating-college context. Participating colleges are not silently treated as permitted or mandatory home colleges. Exact allowed home-college options and applicable college rules remain a scope gap; all 23 degrees remain partial.

Buffalo's university-described AI+X family contains eight independently verified BS degrees sharing five framework notes. PPE's award is verified directly from its department. No identical course inventory is implied, and the two minors are outside this degree framework. The eight degrees now include independently accessible university policies and dated public Pathways candidates; detailed major catalog courses remain unverified. Dated general-education candidates are not represented as complete approved pools.

See [family contract](docs/PROGRAM_FAMILIES.md), [Northeastern evidence](research/program-families.md), [college applicability review](research/northeastern-policy-review.md) and [Buffalo evidence](research/families/buffalo-ai-plus-x.md).

## Meaning of a complete scoped inventory

A **complete requirement inventory** maps the cited program's applicable course choices, counts/credits, nested alternatives, admission or completion prerequisites, grades, overlap, residence/transfer and other completion policies. A degree includes its major and degree-wide college/university requirements. A minor, concentration or additional major covers that credential's own requirements and relationship to its host degree; it does not certify the whole host degree. Explicit open-ended approval rules can be represented; an unavailable finite approved list remains a gap. Completeness requires a reviewer audit and is never certified by the scraper.

This status does **not** mean complete program evidence. Course descriptions, individual course prerequisites and credits, public course sites, syllabi, source-stated learning outcomes and first-offered dates have separate evidence gaps. Unknown prerequisites never mean no prerequisites. Metadata availability is reported separately on the site; an empty outcome or launch date is unverified. If new course evidence exposes a substantive program-eligibility conflict, the requirement inventory returns to partial. See [review contract](docs/CURRICULUM_REVIEW.md).

## Current work after the verified release

The 136-program release is a checkpoint. Subsequent committed evidence and active adapters remain unreleased until another fixed-commit verification.

- **Institution discovery:** ordinary liberal-arts depth reviews cover the loaded roster's assigned queue, with readable and unresolved branches documented separately. An 18-candidate official-news follow-up verified no additional 2027 cohort member; wrong editions and component ranks were rejected. The roster remains incomplete. See [membership follow-up](research/lac-cohort-evidence-2026-10-11.md).
- **National Universities:** deeper directory and concentration reviews continue across the remaining inspected pool. New official evidence includes Yeshiva, UNC–Chapel Hill, American, San Diego and UT Austin; their publication depends on completed adapters, tests and integration. Certificates remain excluded rather than relabeled. See dated `data/surveys/national-*` and adjacent research notes.
- **MIT:** all 43 registrar HASS fields have a dated review ledger. The current committed inventory maps 34, records three precise source questions and six department-detail barriers. Ordinary browser review is testing whether client TLS failures can be resolved without relaxing validation. The degree remains partial because of source/cohort conflicts and remaining policies. See [field ledger](research/mit-hass-field-review-2026-10-11.json).
- **UCSD/UCSB:** all eight principal UCSD college pools are mapped; linked discipline, transfer and examination-policy checks continue. UCSB's current guide, progression and transfer policies are mapped; science-list/course-credit/capstone ambiguity and dynamic GE pools remain explicit.
- **Miami/Northeastern:** all 215 active Miami cognate pages have been captured and reviewed; blank/conflicting plans and applicability gaps keep the degrees partial. Northeastern's 1,593 course observations now have names/descriptions, while exact home-college applicability remains unresolved. Large option pools are not portrayed as mandatory-course counts.
- **Product review:** an independent live review is fixing two query/keyboard edge cases and stale Case degree overview text. Existing live checks passed mobile overflow, navigation and comparison workflows.
- **Parser compatibility:** Soup Sieve 3.0.1 failed valid tag/attribute selectors in both local and fresh Python 3.11.4 environments. The dependency is now constrained to verified 2.x, with six regression probes. See [compatibility evidence](research/parser-compatibility.md).

## Remaining work and exact boundaries

1. **Ranked cohort:** obtain a permitted authoritative 2027 roster for both categories and every cutoff tie. National Universities has a secondary-table enumeration; liberal arts still lacks at least 14 members before accounting for ties. Do not certify full coverage or guess missing identities/ranks. Publisher access restrictions and the failed official-news branches remain documented.
2. **CSRankings:** numerical import is held for permission or qualified reuse review. Methodology records `ai`, `vision`, `mlmining`, `nlp`, `inforet`, the proposed 2016–2025 U.S. window, source snapshot and computation method. Missing values remain null; publication research does not measure undergraduate teaching. See [reuse note](research/csrankings.md).
3. **Access:** eight loaded institutions remain inaccessible in the verified release. Seven published curricula remain pending: the original six separately documented restricted/detail-unavailable programs and the announced UIC concentration. A normal public browser may resolve transport or dynamic-rendering gaps; robots, authentication and explicit restrictions are never bypassed. See [pending barriers](research/pending-curriculum-barriers.md), [access review](research/access-review.md), and each adapter's notes.
4. **Requirement inventories:** 93 published records remain partial. Finish finite eligible lists, nested alternatives, home-college applicability and completion policies where accessible. Source disagreements need documentary reconciliation; elapsed time or program marketing cannot resolve them. Every proposed promotion requires an explicit scoped audit.
5. **Institution search depth:** a confirmed program proves that title exists, not that every program at the institution was found. Inspected records retain the areas searched and unreviewed. Caltech alone has the documented bounded no-qualifying-program finding; no global absence is implied.
6. **Course metadata:** descriptions, prerequisites, exact credits, public sites, syllabi, launch dates and outcomes remain separately incomplete. Match exact course identity/term; source-stated aims and careers stay distinct from learning outcomes and analyst taxonomy. Do not redistribute raw copyrighted catalogs.
7. **Next publication:** freeze committed evidence, ingest into the maintained database, repeat to zero changes, check foreign keys/integrity, compare fresh and maintained current facts, reproduce the static build, run locked clean tests with required Chromium, push that tested commit, and verify both CI/Pages and the public site. Preserve WIP and newer commits outside the tested release.

The [initial gap triage](research/curriculum-gap-triage.md) is a dated starting snapshot; subsequent adapter notes and dated survey ledgers are the current evidence. [Historical release notes](research/release-history-2026-10-11.md) retain the earlier checkpoints without presenting obsolete counts as current. Use `uv run atlas status` and `uv run atlas candidates` to inspect maintenance work. Refreshes queue observations for review and preserve manual corrections; they do not silently replace the research database.
