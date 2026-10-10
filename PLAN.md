# AI Program Atlas — research and publication plan

Updated 2026-10-10. A published research project; **the full target cohort and catalog inventory remain incomplete**.

## Verified publication

- Repository: https://github.com/KrisJordan/ai-program-atlas
- Site: https://krisjordan.github.io/ai-program-atlas/
- Verified release: `44683b366db561fc05f5fbd5e9b55ae5b5102f96`, [successful CI and Pages deployment](https://github.com/KrisJordan/ai-program-atlas/actions/runs/38095099660).
- Fresh locked uv environment and clean committed source: **660 tests passed**, including all **17 required Chromium tests**. The 23 skipped cases require optional ignored source caches; no browser tests were skipped.
- Fresh reconstruction and maintained publication copy passed integrity checks and agreed on current facts; additional historical coverage sources were preserved. Repeat ingest changed zero programs. Repeated static builds were byte-identical.
- Live public JSON matched these counts. Live checks passed keyboard family expansion, concrete comparison reload, discipline back/forward, direct program pages, learning/career statement distinctions and 390px mobile layout, with no JavaScript errors or horizontal overflow.
- Dedicated local repository: `ai-program-atlas/` in this Mac Studio task. No existing personal website or unrelated repository was changed. Coordinated Astra high research and implementation use explicit ownership and incremental commits.

## Published coverage

| Measure | Verified count |
| --- | ---: |
| Institutions in loaded roster | 194 |
| National Universities / National Liberal Arts Colleges | 108 / 86 |
| Confirmed qualifying title / partially inspected / inaccessible | 58 / 128 / 8 |
| Loaded institutions pending / absence conclusions | 0 / 0 |
| Concrete programs | 124 |
| Degrees / minors / concentrations / additional majors | 60 / 42 / 19 / 3 |
| Complete / partial / pending requirement inventories | 27 / 85 / 12 |
| Program-course records / resolved requirement nodes | 4,985 / 5,927 |
| Program families / concrete family variants | 2 / 31 |
| Descriptions / prerequisite statements | 265 / 342 |
| Credit amounts with verified units | 1,483 |
| Public course sites / example syllabi | 22 / 18 |

Course counts include elective pools and repeated observations across sibling programs. They are not unique institution-wide courses, required-course totals, completion percentages or quality scores. Complete refers to an explicitly reviewed scope: a complete minor/concentration/additional major does not certify the host degree. Metadata availability is separate. Zero pending in the loaded roster is not full target-cohort coverage; missing institutions remain outside that denominator.

## Cohort definition and boundaries

Qualifying official undergraduate titles contain AI or Artificial Intelligence. Degrees, additional majors, minors and formal concentrations/tracks/emphases are distinct. Ordinary electives, research centers, informal interest areas, graduate credentials and surveyed certificates are excluded or retained as leads.

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
- [x] Compact directory projection reduced root HTML about 69% raw and 64% gzipped in a controlled same-data comparison. Live root HTML is 2,726,569 bytes; full static detail pages and data.json remain intact. No runtime fetch/server added.
- [x] CI tests fresh reconstruction and publishes an updated copy of the maintained DB. Reviewed discovery classification corrections refresh correctly; manual program corrections and evidence history survive.

## Program families and current evidence

Northeastern's analyst-defined comparison family contains 23 independently verified combined degrees: 22 BS and one BSEnvE. Nine shared AI/core definitions plus 43 universal policy definitions are bound with program-specific provenance. All 14 Business concentration inventories are mapped with first/second concentration eligibility and conditional selection rules. Exact allowed home-college options and applicable college rules remain a scope gap; all 23 degrees remain partial.

Buffalo's university-described AI+X family contains eight independently verified BS degrees sharing five framework notes. PPE's award is verified directly from its department. No identical course inventory is implied, and the two minors are outside this degree framework. Detailed catalog courses remain unverified.

See [family contract](docs/PROGRAM_FAMILIES.md), [Northeastern evidence](research/program-families.md), [college applicability review](research/northeastern-policy-review.md) and [Buffalo evidence](research/families/buffalo-ai-plus-x.md).

## Active continuation beyond the published release

- MIT and NC State curricula are now committed locally as partial (`6193ce3`), with exact CI-M/credit and grade-footnote conflicts retained. MIT degreewide rules are under further review.
- UVA's two concentrations and Tufts's two minors are committed locally as partial (`3a1d76d`). Visible pools and policies are mapped; linked registrar/checklist evidence remains under access review.
- Northeastern home-college applicability is being checked for representative Business, Biology and Design variants.
- Stanford's currently linked AI track sheet and Bulletin, Tulane's existing technical AI minor, and a newly verified distinct AI Literacy minor are being reviewed.
- Access failures are classified by actual evidence, distinguishing publisher denial/authentication from local transport/parser limitations. Any core correction receives regression tests before it is used for new source requests.

Research continues during fixed-snapshot tests. Working-tree changes are excluded from release until committed, ingested and verified. Each adapter's NOTES.md states evidence, interpretations, exact conflicts, metadata gaps and next checks.

## Remaining work and blockers

1. **Cohort:** obtain a permitted authoritative 2027 roster for both categories and all cutoff ties; complete missing liberal-arts enumeration. Preserve secondary/inferred/membership-only labels until resolved.
2. **CSRankings:** numerical import remains held pending permission or qualified reuse review. Methodology records ai,vision,mlmining,nlp,inforet, proposed 2016–2025 window, U.S. filter, pinned source snapshot and computation method. Values remain null, not zero quality. Publication research does not measure undergraduate teaching quality. See [research note](research/csrankings.md).
3. **Access:** eight loaded institutions remain inaccessible. Six older pending curricula have documented barriers; additional program-specific links remain blocked or unread. See [access review](research/access-review.md), [pending curriculum barriers](research/pending-curriculum-barriers.md) and adapter notes. No bypass of robots/auth/403/password gates.
4. **Curricula:** 12 published inventories remain pending and 85 partial; newer local batches reduce the queue but are not yet published. Verify finite pools, nested alternatives, policy applicability and source conflicts before promoting completeness.
5. **Metadata:** many descriptions, prerequisites, public course sites and example syllabi remain unknown. Verify exact course identity and term; preserve historical labels and link rather than redistribute.
6. **Institution depth:** directory searches alone do not establish absence. Continue bounded catalog/minor/concentration searches and documented leads. No absence conclusion has been asserted.

Use `uv run atlas status`, `uv run atlas candidates`, adapter notes and task-specific skills. Refreshes queue observations for review; they never silently replace the research database.
