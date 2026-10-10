# AI Program Atlas — research and publication plan

Updated 2026-10-10. A working, published research project; **the full target cohort and catalog inventory remain incomplete**.

## Verified publication

- Repository: https://github.com/KrisJordan/ai-program-atlas
- Site: https://krisjordan.github.io/ai-program-atlas/
- Latest verified release: `1bf0963abcb4270e8f4cab9e516b64bc45a05872`, [successful build and Pages deployment](https://github.com/KrisJordan/ai-program-atlas/actions/runs/38093333711).
- Clean committed checkout: **514 tests passed**, including all **15 required Chromium tests**. Four optional local source-cache replay cases were skipped; no browser tests were skipped. Clean reconstruction and the maintained publication copy passed integrity/build checks; repeat ingest changed zero records.
- Live public JSON verified all counts below. Live keyboard family expansion, concrete comparison permalink/reload, discipline filter back/forward, direct program details and 390px mobile layout passed with no JavaScript errors or document overflow.
- Local project: dedicated `ai-program-atlas/` repository in this task. Existing personal website and unrelated repositories remain untouched. Astra high research/implementation agents coordinate explicit ownership and incremental commits.

## Published coverage checkpoint

| Measure | Published count |
| --- | ---: |
| Institutions in loaded roster | 193 |
| National Universities / National Liberal Arts Colleges | 108 / 85 |
| Confirmed qualifying title / partially inspected / inaccessible | 53 / 123 / 17 |
| Loaded institutions pending / absence conclusions | 0 / 0 |
| Concrete program records | 110 |
| Degrees / minors / concentrations / additional majors | 56 / 37 / 15 / 2 |
| Complete / partial / pending requirement inventories | 22 / 62 / 26 |
| Program-course records / resolved requirement nodes | 3,025 / 3,034 |
| Program families / concrete family variants | 2 / 23 |
| Descriptions / prerequisite statements | 155 / 205 |
| Credit amounts with known units | 1,094 |
| Public course-site links / syllabus links | 5 / 9 |

Counts include repeated course observations across sibling programs and elective pools. They are not unique institution-wide courses, required-course totals, completion percentages or quality scores. Complete refers to the explicitly reviewed program scope: a complete minor/concentration/additional major does not certify the host degree. Course metadata availability is separate. Zero pending in the loaded roster is not full target-cohort coverage; unlisted institutions remain outside that denominator.

## Cohort definition and unresolved boundaries

Qualifying official undergraduate titles contain AI or Artificial Intelligence. Degrees, additional majors, minors and formal concentrations/tracks/emphases are distinguished. Ordinary electives, research centers, informal interest areas, graduate credentials and surveyed certificates are excluded or retained as leads.

The target is **2027 U.S. News Best Colleges**, separately covering every institution ranked 100 or better in **National Universities** and **National Liberal Arts Colleges**, including all cutoff ties. The edition was released September 22, 2026. Category ranks are never combined.

National Universities enumeration has 108 members from a cited secondary table, including nine tied at 100; authoritative primary enumeration remains unverified. Liberal arts coverage contains 85 cited members but is incomplete: 80 have edition-specific numeric evidence, two have explicitly qualified inferred editions and three have verified top-100 membership with unknown exact ranks. Exact rank null never becomes rank100. Both category completeness flags remain false. Publisher restrictions were not bypassed. See [cohort research](research/cohort.md).

## Delivered engineering and product

- [x] Dedicated uv Python project, locked dependencies, architecture/data contracts, agent ownership, research/refresh skills, incremental commits.
- [x] Maintained SQLite database with migrations, integrity constraints, requirement trees, source provenance, revisions, fetched dates/catalog years, scrape runs, changed-source detection and evidence-backed manual overrides.
- [x] Robots-aware bounded fetching, per-host pacing, cache, redirect validation, content limits, bounded retries and Retry-After deferral. Raw catalogs remain ignored and unpublished.
- [x] Program-specific rerunnable source adapters and adjacent Markdown notes. Failed or partial source observations cannot erase curated research; repeated observations do not duplicate candidates.
- [x] Reviewer-only curriculum completeness audits. Complete inherited inventories pin a reviewed family hash; shared revisions and dependent variants commit atomically or roll back together.
- [x] Carolina-blue/navy, modern sans-serif responsive interface, clear hierarchy, keyboard navigation, filters, coverage ledger, detail pages and ranking methodology. No UNC marks or sponsorship claims.
- [x] Explicit families, expandable variants, discipline filtering, concrete comparison URLs, common/local requirement views, provenance and missingness. Existing IDs and URLs preserved; base-path reload/back/forward work on GitHub Pages.
- [x] Course-category and inferred-theme comparisons retain exact units and separate source statements from analyst taxonomy. No opaque quality score.
- [x] CI validates a fresh reconstruction, then publishes from an updated copy of the maintained database so manual corrections survive. Public HTML/JSON contain curated factual metadata, original summaries and links, not raw copyrighted documents or private context.

## Program-family evidence

The published Northeastern comparison family has 16 independently verified combined BS variants sharing nine definitions, with 144 provenance bindings. Program-specific integration roles and parents remain intact. This grouping is explicitly analyst-classified; combined-major relationships are source-stated. Buffalo's seven BS variants share five university-described AI+X framework notes, not an asserted identical course inventory. Detailed Buffalo catalog requirements remain unverified. Together these families organize 23 concrete degrees while retaining individual titles, awards, hosts, local additions and comparisons.

Newer committed local research expands Northeastern to 23 variants, preserving 22 BS plus one BSEnvE and the distinct Communication Studies/Engineering hosting units. This brings the local two-family model to 30 variants, pending the next verified release. See [family contract](docs/PROGRAM_FAMILIES.md), [Northeastern evidence](research/program-families.md) and [Buffalo evidence](research/families/buffalo-ai-plus-x.md).

## Active continuation — beyond the published checkpoint

Newer work is committed or being reviewed locally and is not represented by the published counts above:

- All 23 documented Northeastern combined-degree curricula are mapped as partial; common university/college degree policies and competency-based NUpath requirements are being checked.
- BC/Duke/Emory and Indiana concentration requirements, Case Applied AI minor, Maryland/California/USF degrees, Delaware/Drexel/Stevens, Miami degree variants and RIT are being researched or integrated. New identities preserve source/status conflicts rather than implying launch dates.
- Source statement types now distinguish learning outcomes, program aims, career pathways and unclassified statements independently of source/inferred provenance. Buffalo career lists are explicitly tagged; associated UI verification is underway.
- Penn BSE remaining FAQ/elective/policy gaps are under review. Already-partial degree records remain partial until published requirements and interpretations are accounted for.

Each adapter's NOTES.md records the exact evidence, interpretations, unresolved lists, source discrepancies and next checks. Working-tree data may include uncommitted research. Release snapshots are made from a fixed committed tree before updating the maintained database, testing and pushing; unrelated agent edits are preserved.

## Remaining work and access blockers

1. **Cohort:** obtain a permitted authoritative 2027 roster for both categories and full cutoff ties. Complete missing liberal-arts enumeration and catalog searches; preserve secondary/inferred/membership-only labels until resolved.
2. **CSRankings numeric data:** import remains held pending permission or qualified reuse review. Published methodology records ai, vision, mlmining, nlp and inforet, proposed 2016–2025 window, U.S. filter, pinned snapshot and computation method. Values remain null with explicit missingness. Publication output is not a measure of undergraduate teaching quality. See [research note](research/csrankings.md).
3. **Institution/program access:** robots restrictions, 403s, password gates and unavailable catalog transport remain explicit, including Furman curriculum, Buffalo catalog and documented Michigan/UC Merced/Gonzaga refresh limits. No alternate-path circumvention. Public official summaries may support partial records but do not substitute invented course lists.
4. **Curricula:** 26 published identities still await extraction and 62 published inventories remain partial. Local batches reduce this queue; the target is not complete. Verify university/college policies, finite approved pools, alternatives, nesting and all source conflicts before upgrading audit status.
5. **Metadata:** many prerequisites, descriptions, course sites and example syllabi remain unknown. Verify course identity and term; retain historical labels and link rather than redistribute.
6. **Institution depth:** initial directory searches do not establish absence. Continue bounded catalog/minor/concentration searches and documented leads; do not change partial inspection to no qualifying program without evidence.

Use `uv run atlas status`, `uv run atlas candidates`, the adapter notes and task-specific skills. Refreshes queue observations for review; they never silently replace the research database.
