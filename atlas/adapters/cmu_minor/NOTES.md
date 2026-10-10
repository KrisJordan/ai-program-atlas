# Artificial Intelligence, Minor

Reviewed 2026-10-10 against official university sources. Raw source HTML was fetched to `/tmp/atlas-*.html` for development and is not committed. University robots policies were checked; no access restrictions were bypassed.

## Coverage and limits

The parser extracts AI core, probability alternatives, three technical pools and two societal pools. The six-course minor and four prerequisite areas are source-stated. Technical choices must come from two distinct clusters; the societal choice comes from either cluster. Those cross-cluster rules are represented as notes, not falsely as required courses from every cluster. No launch date verified. Admission and prerequisite alternatives remain partial.

Seed record: `data/programs/cmu-minor-ai.json`. 53 observed course records; option pools are not course requirements to sum. All curriculum records remain explicitly partial. Public course sites and syllabi have not been verified and are null.

## Parser behavior

`PROGRAM_ID`, `SOURCES` and `parse(html: str) -> dict` are exported. Parsing validates the official page heading and expected curriculum sections, then extracts actual course codes, titles when present, credits when explicit, and nested requirements. It never reads the curated JSON seed or returns a refreshed `last_verified`. Missing required headings/sections or changed selection rules raise `ValueError`. Returned observations remain partial and require coordinator review before replacing curated evidence.

## Source metadata

- [Artificial Intelligence, Minor](https://coursecatalog.web.cmu.edu/schools-colleges/schoolofcomputerscience/minors/artificial-intelligence-minor/) — locator: Curriculum tables; catalog: 2026-2027; source date: not stated; confidence: high. Metadata ID: `cmu-minor-ai-catalog`.
- [Academic calendar](https://www.cmu.edu/hub/calendar/) — locator: Fall and spring academic terms; catalog: not stated; source date: not stated; confidence: high. Metadata ID: `cmu-minor-ai-calendar`.

## Validation

`tests/test_cmu_penn.py` uses synthetic HTML, not copied catalog fixtures, and checks section failure, actual changed-course extraction, nested options, unknown credits, credential distinctions, and record references. Live official HTML was also parsed locally for this review.

## Inferred comparison themes

Added explicitly `inferred_taxonomy` labels from the existing cited curriculum: AI methods, Mathematical foundations, Responsible AI and society, Applied AI. Locators name the supporting core, requirement, overview or elective-pool section. These are analyst classifications for comparison, not university-stated outcomes, and elective-pool themes do not imply every student takes every option. Existing source-stated outcomes are unchanged.
