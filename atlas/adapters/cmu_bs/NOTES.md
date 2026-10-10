# Artificial Intelligence, B.S.

Reviewed 2026-10-10 against official university sources. Raw source HTML was fetched to `/tmp/atlas-*.html` for development and is not committed. University robots policies were checked; no access restrictions were bypassed.

## Coverage and limits

The parser extracts CS core, AI core with the language/vision choice, four AI elective clusters, and ethics. The curated record adds the 360-unit degree minimum and incomplete math/general-education summaries. Math composite alternatives, science and humanities distributions, seminars, free electives, prerequisite and overlap policies remain incomplete.

Seed record: `data/programs/cmu-bs-ai.json`. 40 observed course records; option pools are not course requirements to sum. All curriculum records remain explicitly partial. Selected public course resources are verified below; others remain null.

## Parser behavior

`PROGRAM_ID`, `SOURCES` and `parse(html: str) -> dict` are exported. Parsing validates the official page heading and expected curriculum sections, then extracts actual course codes, titles when present, credits when explicit, and nested requirements. It never reads the curated JSON seed or returns a refreshed `last_verified`. Missing required headings/sections or changed selection rules raise `ValueError`. Returned observations remain partial and require coordinator review before replacing curated evidence.

## Source metadata

- [Artificial Intelligence, B.S.](https://coursecatalog.web.cmu.edu/schools-colleges/schoolofcomputerscience/artificialintelligence/artificial-intelligence-bs/) — locator: Curriculum tables; catalog: 2026-2027; source date: not stated; confidence: high. Metadata ID: `cmu-bs-ai-catalog`.
- [Academic calendar](https://www.cmu.edu/hub/calendar/) — locator: Fall and spring academic terms; catalog: not stated; source date: not stated; confidence: high. Metadata ID: `cmu-bs-ai-calendar`.
- [Carnegie Mellon Launches Undergraduate Degree in Artificial Intelligence](https://csd.cmu.edu/news/carnegie-mellon-launches-undergraduate-degree-in-artificial-intelligence) — locator: May 10, 2018 announcement; beginning this fall; catalog: not stated; source date: 2018-05-10; confidence: high. Metadata ID: `cmu-bs-ai-launch`.

## Validation

`tests/test_cmu_penn.py` uses synthetic HTML, not copied catalog fixtures, and checks section failure, actual changed-course extraction, nested options, unknown credits, credential distinctions, and record references. Live official HTML was also parsed locally for this review.

## Public course resource enrichment (2026-10-10)

- [15-150: Functional Programming, Fall 2026](https://www.cs.cmu.edu/~15150/) — Heading, overview and learning outcomes. Source ID: `cmu-15150-fall-2026-site`.
- [15-213/15-513/14-513 Introduction to Computer Systems (ICS), Fall 2026](https://www.cs.cmu.edu/~213/) — Course identity and Course Syllabus link. Source ID: `cmu-15213-fall-2026-site`.
- [15-213 / 15-513 / 14-513: Introduction to Computer Systems — Fall 2026 syllabus](https://www.cs.cmu.edu/~213/syllabus/syllabus.pdf) — PDF page 1: course codes, university and Fall 2026. Source ID: `cmu-15213-fall-2026-syllabus`.

Course `source_id` still cites the curriculum; resource metadata independently supports `public_site` and `syllabus`. CMU resources identify Fall 2026; the Penn outline is explicitly a historical Fall 2021 example linked by the official CIS 3200 archive (older CIS 320 numbering), not current curriculum evidence. No syllabus content was copied into the repository.

## Inferred comparison themes

Added explicitly `inferred_taxonomy` labels from the existing cited curriculum: AI methods, Mathematical foundations, Responsible AI and society, Software and systems, Applied AI. Locators name the supporting core, requirement, overview or elective-pool section. These are analyst classifications for comparison, not university-stated outcomes, and elective-pool themes do not imply every student takes every option. Existing source-stated outcomes are unchanged.
