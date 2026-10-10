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
