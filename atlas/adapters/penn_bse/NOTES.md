# Artificial Intelligence, BSE

Reviewed 2026-10-10 against official university sources. Raw source HTML was fetched to `/tmp/atlas-*.html` for development and is not committed. University robots policies were checked; no access restrictions were bypassed.

## Coverage and limits

The parser extracts computing, all six AI core areas and the AI elective option pool. Nested introductory-AI alternatives are flattened within a single choice while preserving course names. Other degree components are summarized in the curated record. Individual course credits are null because the page lists group totals. The overview implies concentrations are required; the explicit concentration section says optional. This conflict is retained in notes. Catalog endpoints returned empty responses; no catalog edition is assigned to the undated program page.

Seed record: `data/programs/penn-bse-ai.json`. 54 observed course records; option pools are not course requirements to sum. All curriculum records remain explicitly partial. Selected public course resources are verified below; others remain null.

## Parser behavior

`PROGRAM_ID`, `SOURCES` and `parse(html: str) -> dict` are exported. Parsing validates the official page heading and expected curriculum sections, then extracts actual course codes, titles when present, credits when explicit, and nested requirements. It never reads the curated JSON seed or returns a refreshed `last_verified`. Missing required headings/sections or changed selection rules raise `ValueError`. Returned observations remain partial and require coordinator review before replacing curated evidence.

## Source metadata

- [Artificial Intelligence, BSE](https://ai.engineering.upenn.edu/academics/undergraduate/) — locator: Curriculum requirements; catalog: not stated; source date: not stated; confidence: high. Metadata ID: `penn-bse-ai-curriculum`.
- [Academic calendar](https://almanac.upenn.edu/penn-academic-calendar) — locator: Fall and spring academic terms; catalog: not stated; source date: not stated; confidence: high. Metadata ID: `penn-bse-ai-calendar`.
- [Penn Engineering AI degree announcement](https://almanac.upenn.edu/volume-70-number-23) — locator: Penn Engineering Announces First Ivy League Undergraduate Degree in Artificial Intelligence; final paragraph; catalog: not stated; source date: 2024-02-20; confidence: high. Metadata ID: `penn-bse-ai-launch`.

## Validation

`tests/test_cmu_penn.py` uses synthetic HTML, not copied catalog fixtures, and checks section failure, actual changed-course extraction, nested options, unknown credits, credential distinctions, and record references. Live official HTML was also parsed locally for this review.

## Public course resource enrichment (2026-10-10)

- [CIS 3200: Intro to Algorithms — past offerings](https://www.engineering.upenn.edu/~cis3200/) — Archive identifies CIS 3200 and links Fall 2021. Source ID: `penn-cis3200-archive`.
- [Introduction to Algorithms — Fall 2021](https://www.engineering.upenn.edu/~cis3200/21fa/) — Heading, term, prerequisites, grading and Topics Covered; historical CIS 320 numbering. Source ID: `penn-cis3200-fall-2021-outline`.

Course `source_id` still cites the curriculum; resource metadata independently supports `public_site` and `syllabus`. CMU resources identify Fall 2026; the Penn outline is explicitly a historical Fall 2021 example linked by the official CIS 3200 archive (older CIS 320 numbering), not current curriculum evidence. No syllabus content was copied into the repository.

## Inferred comparison themes

Added explicitly `inferred_taxonomy` labels from the existing cited curriculum: AI methods, Mathematical foundations, Responsible AI and society, Software and systems, Applied AI. Locators name the supporting core, requirement, overview or elective-pool section. These are analyst classifications for comparison, not university-stated outcomes, and elective-pool themes do not imply every student takes every option. Existing source-stated outcomes are unchanged.
