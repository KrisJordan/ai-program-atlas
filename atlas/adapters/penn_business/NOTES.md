# Artificial Intelligence for Business

Reviewed 2026-10-10 against official university sources. Raw source HTML was fetched to `/tmp/atlas-*.html` for development and is not committed. University robots policies were checked; no access restrictions were bypassed.

## Coverage and limits

The parser extracts the two required pillar courses, 1 CU foundation electives and 1.5 CU impact electives. This is a concentration within BS Economics, not a standalone AI degree, despite the catalog URL ending in -bs. The official undergraduate department page establishes the credential. Crosslisted MGMT/OIDD 3130 is one course record. Elective credits are null; required course credits must be present or the parser fails. Advisor-approved substitutions and degree-wide requirements remain partial.

Seed record: `data/programs/penn-concentration-ai-business.json`. 28 observed course records; option pools are not course requirements to sum. All curriculum records remain explicitly partial. Public course sites and syllabi have not been verified and are null.

## Parser behavior

`PROGRAM_ID`, `SOURCES` and `parse(html: str) -> dict` are exported. Parsing validates the official page heading and expected curriculum sections, then extracts actual course codes, titles when present, credits when explicit, and nested requirements. It never reads the curated JSON seed or returns a refreshed `last_verified`. Missing required headings/sections or changed selection rules raise `ValueError`. Returned observations remain partial and require coordinator review before replacing curated evidence.

## Source metadata

- [Artificial Intelligence for Business](https://oid.wharton.upenn.edu/artificial-intelligence-joint-concentration/) — locator: Curriculum requirements; catalog: not stated; source date: not stated; confidence: high. Metadata ID: `penn-concentration-ai-business-curriculum`.
- [Academic calendar](https://almanac.upenn.edu/penn-academic-calendar) — locator: Fall and spring academic terms; catalog: not stated; source date: not stated; confidence: high. Metadata ID: `penn-concentration-ai-business-calendar`.
- [New MBA Major: Artificial Intelligence for Business](https://magazine.wharton.upenn.edu/digital/new-mba-major-artificial-intelligence-for-business/) — locator: Undergraduate concentration launch; eligible from Fall 2025; catalog: not stated; source date: 2025-04-02; confidence: high. Metadata ID: `penn-concentration-ai-business-launch`.
- [Wharton undergraduate concentrations](https://undergrad.wharton.upenn.edu/concentrations/) — locator: BS in Economics statement and AI concentration listing; catalog: not stated; source date: not stated; confidence: high. Metadata ID: `penn-concentration-ai-business-credential`.

## Validation

`tests/test_cmu_penn.py` uses synthetic HTML, not copied catalog fixtures, and checks section failure, actual changed-course extraction, nested options, unknown credits, credential distinctions, and record references. Live official HTML was also parsed locally for this review.

## Inferred comparison themes

Added explicitly `inferred_taxonomy` labels from the existing cited curriculum: AI methods, Responsible AI and society, Applied AI. Locators name the supporting core, requirement, overview or elective-pool section. These are analyst classifications for comparison, not university-stated outcomes, and elective-pool themes do not imply every student takes every option. Existing source-stated outcomes are unchanged.
