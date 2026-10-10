# AI Program Atlas implementation and coverage plan

## Scope and truthfulness
Dedicated repository, provisionally KrisJordan/ai-program-atlas. Two independent U.S. News cohorts: National Universities and National Liberal Arts Colleges, rank <=100 inclusive of ties. Edition and complete membership require actual source verification. Pilot records do not establish full cohort coverage. Only programs with AI / Artificial Intelligence in official undergraduate title qualify; distinguish degrees, minors and concentrations.

## Milestones
- [x] Inspect empty workspace; preserve unrelated repositories.
- [ ] Verify account/repository collision, ranking edition and cohort source.
- [ ] Document architecture, schema, provenance and adapter contracts.
- [ ] Pilot CMU, Penn, Purdue and a minor/applied program from official sources.
- [ ] SQLite migrations, safe fetching, idempotent ingest, revisions and manual overrides.
- [ ] Full cohort inventory with explicit inspected/confirmed/no-find/inaccessible/pending states.
- [ ] Course and nested requirement extraction; outcomes and CSRankings evidence.
- [ ] Editorial static site with coverage, detail, comparison and methodology.
- [ ] Unit/integration/e2e checks, clean build, incremental commits.
- [ ] Create dedicated GitHub repository and verify Pages deployment.

## Current status
2026-10-10: Initial implementation. No full-coverage claim. GitHub connector confirms KrisJordan personal account; CLI authentication needs verification outside network sandbox. No raw copyrighted source documents will be committed.

## Coverage log
To be generated from the database. Pending is the default for uninspected cohort members; no qualifying program found requires a documented search of official catalogs and program directories.

2026-10-10 pilot research: Added separate Purdue AI BS and Liberal Arts BA, plus Penn State Artificial Intelligence Engineering minor. BS department curriculum has 42 courses / 17 requirement nodes; Purdue catalog 403 leaves college-level coverage partial and BA curriculum pending. Penn State current 2026–27 bulletin yields 5 courses / 6 nodes; approved department elective list remains unexpanded. All first-offering dates are null. Three real HTML parsers, synthetic regression tests and adapter NOTES document exact evidence/next checks.

2026-10-10 liberal arts survey: Added 66 currently verified cohort rows in data/surveys/liberal.json: 2 title-confirmed, 53 preliminary official-page inspections, 5 inaccessible and 6 pending directory resolution; no absence conclusions. Added Denison MLAI minor (eight required courses, partial credits/prerequisites) and Furman AI BS directory record (activity unknown, curriculum pending; detail page password protected). Both adapters validate observed HTML and do not replay seeds. Full catalog/concentration review and complete ranking membership remain outstanding. Verification at this checkpoint: 36 tests passed, 4 browser tests skipped; atlas build blocked because atlas.cli was still being implemented by coordinator.

## CMU and Penn pilot coverage (2026-10-10)

- Confirmed six distinct undergraduate credentials from official sources: CMU AI BS, minor and additional major; Penn AI BSE, CSCI AI concentration, and Wharton AI for Business concentration within BS Economics.
- Added program-specific parsers and researched seeds with 231 program-course records (option pools, with cross-program overlap), source metadata, nested choices and explicit partial coverage. CMU uses 2026–2027 catalog; Penn department pages have no assigned catalog year.
- Launch evidence: CMU BS Fall 2018; Penn BSE Fall 2024 (existing students, external applicants Fall 2025); Wharton concentration Fall 2025. Other launch dates remain null.
- Verified parser behavior with 19 synthetic tests and a live-HTML development pass for all six sources. Raw pages kept only in /tmp.
- Remaining: CMU full math/probability and general-education logic; all prerequisite/course description and syllabus validation; Penn catalog retrieval, curriculum policy exceptions and conflicting concentration language. No full graduation-audit or full-institution-discovery claim.

## Frontend delivery (2026-10-10)
Static editorial index, program details, coverage ledger and methodology implemented in atlas/site.py + atlas/web. Filters cover award, calendar, institution, U.S. News category and observed course category. Comparison supports four programs, deep URLs, reload/back/forward, preserved Pages base path, distinct credit units, nested requirement summaries, source outcomes and editorial taxonomy. Charts deduplicate stable course IDs; missingness stays explicit. Coverage links ranking evidence and inspection/discovery evidence with separate cohort caveats. CSRankings stays not_imported with external links only. Test-only synthetic records are confined to tests. Six site tests and four Chromium e2e tests passed; real-data desktop/mobile screenshots inspected (390px mobile, no document overflow), no-JS direct pages verified. Integration build passed; current database snapshot contained three programs and 174 institutions, pending coordinator reload of the latest program files. Remaining: integration with final research snapshot and deployed Pages check.

2026-10-10 liberal arts follow-up: Located all six pending paths through official homepages; loaded 66-member LAC subset now has 59 preliminary inspections, 2 title confirmations and 5 access failures. F&M and Saint Anselm AI certificates documented as exclusions. Denison official catalog now supplies all eight course credits and semester policy; full title is verified, curriculum remains partial. Isolated CLI init/ingest/build/integrity checks passed; latest build included 83 programs/174 institutions. Both LAC program pages passed local Chromium desktop/mobile checks and desktop screenshot inspection.

## National-university discovery contribution (2026-10-10)

Added national.json ledger for all 108 cohort members: 28 confirmed, 3 inspected, 5 inaccessible, 72 pending, no absence conclusions. Promoted 72 official-source identities (44 degrees, 25 minors, 3 concentrations) to separate curriculum-pending program records and identity-only adapters, manifest in research/national-discovery-manifest.json. Unknown calendars, first-offering dates and courses remain unknown. UMD BSAI is announced for fall 2027; GeoAI/GenAI held for title-scope review. National survey report documents directory-level evidence, catalog-access failures and follow-up leads. Full existing-venv suite: 129 passed, 4 skipped; atlas build: 83 programs/174 institutions. uv was unavailable on this shell PATH. Remaining: merge parallel surveys, complete institutional inventories, verify current activity and catalog years, extract curricula and test all adapters against permitted live sources.

2026-10-10 frontend integration: final 83-program snapshot rendered. Added program-type and curriculum-evidence facets, explicit additional-major badges, identity-only counts/labels, and corrected coverage terminology to documented records. Methodology renders CSRankings configured fields, 2016–2025 window, US filter, pinned snapshot, method, missingness and unresolved reuse status; additional majors are explicit in scope. ATLAS_REQUIRE_BROWSER=1 now makes missing Playwright/Chromium a test failure. Seven publishing tests and five required Chromium tests pass; complete current non-browser suite 136 passed. Final real-data screenshots /tmp/atlas-83-desktop.png, /tmp/atlas-83-mobile.png, /tmp/atlas-83-mobile-filters.png, /tmp/atlas-83-methodology.png. No JavaScript errors; 390px overflow false on index, coverage, methodology and CMU additional-major detail. Final deployment verification remains with coordinator.

2026-10-10 additional National University survey: Added data/surveys/national-additional.json with 25 previously pending rank≤60 institutions: 2 confirmed, 19 inspected and 4 inaccessible. Confirmed Columbia AI minor and Stanford AI concentration/formal CS BS track; both promoted to identity-only program records with pending curricula and conservative discovery adapters. Georgetown/UT AI certificates, UCI elective area, JHU graduate track and Brown discontinued pathway structure are not silently counted as qualifying undergraduate credentials. No absence conclusions. Research notes preserve official links and exact remaining coverage.
