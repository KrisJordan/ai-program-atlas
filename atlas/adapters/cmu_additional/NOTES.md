# Artificial Intelligence, Additional Major

Reviewed 2026-10-10 against official university sources. Raw source HTML was fetched to `/tmp/atlas-*.html` for development and is not committed. University robots policies were checked; no access restrictions were bypassed.

## Coverage and limits

The parser extracts five CS core courses, two AI core courses, four one-course AI cluster choices, ethics and cognition. Six mathematics requirements and admission prerequisite alternatives are not fully extracted. The additional major is not an independently awarded degree: program_kind=additional_major, award_level=other. No launch date verified. Overlap restrictions are summarized in record notes.

Seed record: `data/programs/cmu-additional-ai.json`. 44 observed course records; option pools are not course requirements to sum. All curriculum records remain explicitly partial. Public course sites and syllabi have not been verified and are null.

## Parser behavior

`PROGRAM_ID`, `SOURCES` and `parse(html: str) -> dict` are exported. Parsing validates the official page heading and expected curriculum sections, then extracts actual course codes, titles when present, credits when explicit, and nested requirements. It never reads the curated JSON seed or returns a refreshed `last_verified`. Missing required headings/sections or changed selection rules raise `ValueError`. Returned observations remain partial and require coordinator review before replacing curated evidence.

## Source metadata

- [Artificial Intelligence, Additional Major](https://coursecatalog.web.cmu.edu/schools-colleges/schoolofcomputerscience/artificialintelligence/artificial-intelligence-additional-major/) — locator: Curriculum tables; catalog: 2026-2027; source date: not stated; confidence: high. Metadata ID: `cmu-additional-ai-catalog`.
- [Academic calendar](https://www.cmu.edu/hub/calendar/) — locator: Fall and spring academic terms; catalog: not stated; source date: not stated; confidence: high. Metadata ID: `cmu-additional-ai-calendar`.

## Validation

`tests/test_cmu_penn.py` uses synthetic HTML, not copied catalog fixtures, and checks section failure, actual changed-course extraction, nested options, unknown credits, credential distinctions, and record references. Live official HTML was also parsed locally for this review.
