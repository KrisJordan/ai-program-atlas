# Artificial Intelligence

Reviewed 2026-10-10 against official university sources. Raw source HTML was fetched to `/tmp/atlas-*.html` for development and is not committed. University robots policies were checked; no access restrictions were bypassed.

## Coverage and limits

The parser scopes strictly to the Artificial Intelligence accordion, expands slash alternatives and extracts two required core choices plus 2 CU electives. It does not ingest courses from other concentrations. The source lists codes only: titles, individual credits, prerequisites and descriptions remain null. First offering unknown. Concentration optional for CSCI students, maximum one concentration per degree.

Seed record: `data/programs/penn-concentration-ai-cs.json`. 12 observed course records; option pools are not course requirements to sum. All curriculum records remain explicitly partial. Public course sites and syllabi have not been verified and are null.

## Parser behavior

`PROGRAM_ID`, `SOURCES` and `parse(html: str) -> dict` are exported. Parsing validates the official page heading and expected curriculum sections, then extracts actual course codes, titles when present, credits when explicit, and nested requirements. It never reads the curated JSON seed or returns a refreshed `last_verified`. Missing required headings/sections or changed selection rules raise `ValueError`. Returned observations remain partial and require coordinator review before replacing curated evidence.

## Source metadata

- [Artificial Intelligence](https://www.cis.upenn.edu/undergraduate-program-options/concentrations/) — locator: Curriculum requirements; catalog: not stated; source date: not stated; confidence: high. Metadata ID: `penn-concentration-ai-cs-curriculum`.
- [Academic calendar](https://almanac.upenn.edu/penn-academic-calendar) — locator: Fall and spring academic terms; catalog: not stated; source date: not stated; confidence: high. Metadata ID: `penn-concentration-ai-cs-calendar`.

## Validation

`tests/test_cmu_penn.py` uses synthetic HTML, not copied catalog fixtures, and checks section failure, actual changed-course extraction, nested options, unknown credits, credential distinctions, and record references. Live official HTML was also parsed locally for this review.

## Inferred comparison themes

Added explicitly `inferred_taxonomy` labels from the existing cited curriculum: AI methods, Applied AI. Locators name the supporting core, requirement, overview or elective-pool section. These are analyst classifications for comparison, not university-stated outcomes, and elective-pool themes do not imply every student takes every option. Existing source-stated outcomes are unchanged.
