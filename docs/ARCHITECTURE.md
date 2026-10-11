# Architecture and research protocol

## Pipeline

Official sources → respectful cached HTTP → institution/program adapter → candidate extraction + source change log → reviewed factual JSON → transactional SQLite ingest → deterministic JSON/HTML static build → tests → GitHub Pages.

A scraper run is an observation, not an authority to erase earlier research. Adapters return only fields they extracted. Failed fetches/parses create failed run records. A successful partial extraction is retained as a candidate. Source hashes detect changes. Curated records change only after evidence review; manual overrides remain a separate layer and survive reimport. Fetched source bodies are cache-only and excluded from Git and the website.

## Relational storage

Versioned migrations create institutions/aliases, hosting units, ranking observations, cohort memberships and coverage events; programs, sources/evidence, links, courses, prerequisite/credit metadata, nested requirement groups and membership, and outcomes; runs, fetch snapshots, program revisions, extraction candidates and manual overrides. Canonical UTF-8 JSON is also retained per revision in lossless zlib form to support audit and exact recovery. Migration 007 preserves every revision ID, content hash, timestamp and scrape-run association, checks the historical hash before conversion, and rolls back on corruption. Current program JSON and relational facts remain directly queryable. Decode a history row with `atlas.db.revision_record(row)`, which verifies the recovered payload against its SHA-256 content hash. The database is built from reviewed input in data/ and maintained between runs; transaction boundaries prevent partial program replacement.

Integrity rules: stable IDs; foreign keys on; unique program/institution associations; enumerated coverage and program kinds; nonnegative ranks/credits; tree cycle and dangling course checks before a transaction. Credits retain their original unit; totals are not compared across calendars. Unknown values remain null. Alternative and elective groups retain choose-N/credit semantics; group membership does not imply all courses are mandatory.

## Cohort and completeness

Two separate 2027 U.S. News categories, rank <=100 including all ties at the cutoff. Record category, edition, rank and citation for every admitted cohort member. Do not infer category from older editions: approximately 20% changed categories for 2027. Full category enumeration may be incomplete when lawful sources are unavailable. Site metrics expose both denominator completeness and inspection completeness.

Coverage states: pending (not inspected); inspected (some official sources reviewed, conclusion incomplete); confirmed (at least one qualifying official title verified, not a claim of exhaustive institution inventory); no_qualifying_program_found (documented program-directory and current-catalog review with limits); inaccessible (necessary official evidence blocked). Any review can remain partial. A confirmed program's curriculum may independently remain partial or pending.

## Source and copyright handling

Bounded retries on transient failure only, sequential per-host pacing, explicit timeout and size limits, robots checks with fail-closed behavior, cache TTL, and no attempts to bypass 401/403 or paywalls. Record source URL, fetch date, source date when given, catalog year, evidence locator, confidence and run. Curated factual metadata and original summaries are public. Long copyrighted passages, raw PDFs/HTML and private user context are excluded. Source-stated outcomes are concise paraphrases and separate from our inferred taxonomy.

## CSRankings

Public values are not imported pending reuse permission. Metadata records selected AI fields (ai, vision, mlmining, nlp, inforet), proposed 2016–2025 complete-year window and USA filter; each individual field and aggregate has explicit missing status. The source license and methodology are linked. The aggregate must never be invented from ordinal ranks or mistaken for undergraduate teaching quality. Computation and pinned source snapshot are recorded for a future authorized implementation.

## Static delivery

SQLite is the build input. Export sorted JSON and escaped HTML; copy local CSS/JS. No runtime server, remote fonts, tracking or secret configuration. Base paths are explicit. Root query parameters encode search/filter/compare state with the History API. Program/coverage/methodology pages are real directories and work on direct navigation; baseline content works without JavaScript. Compare observed course records, never spurious degree percentages. GitHub Actions tests and builds before Pages deployment.

## Work ownership and gates

Coordinator owns migrations and persistence. Independent researchers own program adapters and adjacent Markdown notes. Frontend owns rendering assets. Pilots test varied program/credit systems before inventory expansion. Integration tests cover idempotence, overrides, partial failure and requirement semantics; browser tests cover root/base-path routing, filters, detail, comparison history and mobile. A clean-checkout build and verified remote deployment are required before publication is reported complete.
