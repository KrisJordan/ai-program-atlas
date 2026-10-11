# AI Program Atlas — research and publication plan

Updated 2026-10-11. A published research project; **the full target cohort and catalog inventory remain incomplete**.

## Verified publication

- Repository: https://github.com/KrisJordan/ai-program-atlas
- Site: https://krisjordan.github.io/ai-program-atlas/
- Verified release: `f18086ca2008fed7632690bb093e098c8d0f1227`, [successful CI and Pages deployment](https://github.com/KrisJordan/ai-program-atlas/actions/runs/38097182363).
- Fresh locked uv environment and clean committed source: **787 tests passed**, including all **17 required Chromium tests**. The 44 skipped cases require optional ignored source caches; no browser tests were skipped.
- Fresh reconstruction and maintained publication copy passed integrity checks and agreed on current facts; additional historical coverage sources were preserved. Repeat ingest changed zero programs. Repeated static builds were byte-identical across 132 files.
- Live public JSON matched these counts. Live checks passed keyboard family expansion, concrete comparison reload, discipline back/forward, direct program pages, learning/career statement distinctions and 390px mobile layout, with no JavaScript errors or horizontal overflow.
- Dedicated local repository: `ai-program-atlas/` in this Mac Studio task. No existing personal website or unrelated repository was changed. Coordinated Astra high research and implementation use explicit ownership and incremental commits.

## Published coverage

| Measure | Verified count |
| --- | ---: |
| Institutions in loaded roster | 194 |
| National Universities / National Liberal Arts Colleges | 108 / 86 |
| Confirmed qualifying title / partially inspected / inaccessible | 58 / 128 / 8 |
| Loaded institutions pending / absence conclusions | 0 / 0 |
| Concrete programs | 125 |
| Degrees / minors / concentrations / additional majors | 60 / 43 / 19 / 3 |
| Complete / partial / pending requirement inventories | 31 / 89 / 5 |
| Program-course records / resolved requirement nodes | 7,838 / 6,922 |
| Program families / concrete family variants | 2 / 31 |
| Descriptions / prerequisite statements | 825 / 831 |
| Credit amounts with verified units | 1,925 |
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
- [x] Compact directory projection reduced root HTML about 69% raw and 64% gzipped in a controlled same-data comparison. Live root HTML is 2,987,218 bytes; full static detail pages and data.json remain intact. No runtime fetch/server added.
- [x] CI tests fresh reconstruction and publishes an updated copy of the maintained DB. Reviewed discovery classification corrections refresh correctly; manual program corrections and evidence history survive.

## Program families and current evidence

Northeastern's analyst-defined comparison family contains 23 independently verified combined degrees: 22 BS and one BSEnvE. Nine shared AI/core definitions plus 43 universal policy definitions are bound with program-specific provenance. All 14 Business concentration inventories are mapped with first/second concentration eligibility and conditional selection rules. Business, Biology and Design carry independently cited participating-college context. Participating colleges are not silently treated as permitted or mandatory home colleges. Exact allowed home-college options and applicable college rules remain a scope gap; all 23 degrees remain partial.

Buffalo's university-described AI+X family contains eight independently verified BS degrees sharing five framework notes. PPE's award is verified directly from its department. No identical course inventory is implied, and the two minors are outside this degree framework. Detailed catalog courses remain unverified.

See [family contract](docs/PROGRAM_FAMILIES.md), [Northeastern evidence](research/program-families.md), [college applicability review](research/northeastern-policy-review.md) and [Buffalo evidence](research/families/buffalo-ai-plus-x.md).

## Meaning of a complete scoped inventory

A **complete requirement inventory** maps the cited program's applicable course choices, counts/credits, nested alternatives, admission or completion prerequisites, grades, overlap, residence/transfer and other completion policies. A degree includes its major and degree-wide college/university requirements. A minor, concentration or additional major covers that credential's own requirements and relationship to its host degree; it does not certify the whole host degree. Explicit open-ended approval rules can be represented; an unavailable finite approved list remains a gap. Completeness requires a reviewer audit and is never certified by the scraper.

This status does **not** mean complete program evidence. Course descriptions, individual course prerequisites and credits, public course sites, syllabi, source-stated learning outcomes and first-offered dates have separate evidence gaps. Unknown prerequisites never mean no prerequisites. Metadata availability is reported separately on the site; an empty outcome or launch date is unverified. If new course evidence exposes a substantive program-eligibility conflict, the requirement inventory returns to partial. See [review contract](docs/CURRICULUM_REVIEW.md).

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
3. **Access:** eight loaded institutions remain inaccessible. The five currently published pending curricula have documented barriers; additional program-specific links remain blocked or unread. See [access review](research/access-review.md), [pending curriculum barriers](research/pending-curriculum-barriers.md) and adapter notes. No bypass of robots/auth/403/password gates.
4. **Curricula:** Five published inventories remain pending and89 partial. Verify finite pools, nested alternatives, policy applicability and source conflicts before promoting completeness.
5. **Metadata:** many descriptions, prerequisites, public course sites and example syllabi remain unknown. Verify exact course identity and term; preserve historical labels and link rather than redistribute.
6. **Institution depth:** directory searches alone do not establish absence. Continue bounded catalog/minor/concentration searches and documented leads. No absence conclusion has been asserted.

Use `uv run atlas status`, `uv run atlas candidates`, adapter notes and task-specific skills. Refreshes queue observations for review; they never silently replace the research database.

## Research integration verified — 2026-10-11

Committed evidence through `351170d0` is ingested in the maintained database. Release f18086c passed clean locked-environment tests, fresh/maintained agreement, repeat ingest/build checks, successful GitHub CI/Pages deployment and live browser/JSON verification: 31 complete / 89 partial / 5 pending; 7838 course observations and 6922 requirement nodes. Michigan HCAI now has a public-handbook inventory; RIT’s two minors have complete scoped policy audits. Source-version conflicts at MIT/Penn/Purdue and home-college applicability at Northeastern remain explicit. Further committed research includes Case degree-scope audits, Miami policies, Drexel approved writing courses and Duke policies; those newer commits await the next frozen integration. Accessible research continues after this publication checkpoint.
