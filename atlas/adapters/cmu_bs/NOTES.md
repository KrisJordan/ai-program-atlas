# Artificial Intelligence, B.S.

Reviewed 2026-10-10 against official university sources. Raw source HTML was fetched to `/tmp/atlas-*.html` for development and is not committed. University robots policies were checked; no access restrictions were bypassed.

## Coverage and limits

The parser extracts CS core, AI core with the language/vision choice, four AI elective clusters, and ethics. The curated record adds the 360-unit degree minimum and incomplete math/general-education summaries. Math composite alternatives, science and humanities distributions, seminars, free electives, prerequisite and overlap policies remain incomplete.

Seed record: `data/programs/cmu-bs-ai.json`. 40 observed course records; option pools are not course requirements to sum. All curriculum records remain explicitly partial. Public course sites and syllabi have not been verified and are null.

## Parser behavior

`PROGRAM_ID`, `SOURCES` and `parse(html: str) -> dict` are exported. Parsing validates the official page heading and expected curriculum sections, then extracts actual course codes, titles when present, credits when explicit, and nested requirements. It never reads the curated JSON seed or returns a refreshed `last_verified`. Missing required headings/sections or changed selection rules raise `ValueError`. Returned observations remain partial and require coordinator review before replacing curated evidence.

## Source metadata

- [Artificial Intelligence, B.S.](https://coursecatalog.web.cmu.edu/schools-colleges/schoolofcomputerscience/artificialintelligence/artificial-intelligence-bs/) — locator: Curriculum tables; catalog: 2026-2027; source date: not stated; confidence: high. Metadata ID: `cmu-bs-ai-catalog`.
- [Academic calendar](https://www.cmu.edu/hub/calendar/) — locator: Fall and spring academic terms; catalog: not stated; source date: not stated; confidence: high. Metadata ID: `cmu-bs-ai-calendar`.
- [Carnegie Mellon Launches Undergraduate Degree in Artificial Intelligence](https://csd.cmu.edu/news/carnegie-mellon-launches-undergraduate-degree-in-artificial-intelligence) — locator: May 10, 2018 announcement; beginning this fall; catalog: not stated; source date: 2018-05-10; confidence: high. Metadata ID: `cmu-bs-ai-launch`.

## Validation

`tests/test_cmu_penn.py` uses synthetic HTML, not copied catalog fixtures, and checks section failure, actual changed-course extraction, nested options, unknown credits, credential distinctions, and record references. Live official HTML was also parsed locally for this review.
