# Artificial Intelligence

Reviewed 2026-10-10 against official university sources. Raw source HTML was fetched to `/tmp/atlas-*.html` for development and is not committed. University robots policies were checked; no access restrictions were bypassed.

## Coverage and limits

The parser scopes strictly to the Artificial Intelligence accordion, expands slash alternatives and extracts two required core choices plus 2 CU electives. It does not ingest courses from other concentrations. The source lists codes only: titles, individual credits, prerequisites and descriptions remain null. First offering unknown. Concentration optional for CSCI students, maximum one concentration per degree.

Seed record: `data/programs/penn-concentration-ai-cs.json`. 12 observed course records; option pools are not course requirements to sum. The local requirement inventory is now complete after the review below; course metadata remain partial. Public course sites and syllabi have not been verified and are null.

## Parser behavior

`PROGRAM_ID`, `SOURCES` and `parse(html: str) -> dict` are exported. Parsing validates the official page heading and expected curriculum sections, then extracts actual course codes, titles when present, credits when explicit, and nested requirements. It never reads the curated JSON seed or returns a refreshed `last_verified`. Missing required headings/sections or changed selection rules raise `ValueError`. Returned observations remain partial and require coordinator review before replacing curated evidence.

## Source metadata

- [Artificial Intelligence](https://www.cis.upenn.edu/undergraduate-program-options/concentrations/) — locator: Curriculum requirements; catalog: not stated; source date: not stated; confidence: high. Metadata ID: `penn-concentration-ai-cs-curriculum`.
- [Academic calendar](https://almanac.upenn.edu/penn-academic-calendar) — locator: Fall and spring academic terms; catalog: not stated; source date: not stated; confidence: high. Metadata ID: `penn-concentration-ai-cs-calendar`.

## Validation

`tests/test_cmu_penn.py` uses synthetic HTML, not copied catalog fixtures, and checks section failure, actual changed-course extraction, nested options, unknown credits, credential distinctions, and record references. Live official HTML was also parsed locally for this review.

## Inferred comparison themes

Added explicitly `inferred_taxonomy` labels from the existing cited curriculum: AI methods, Applied AI. Locators name the supporting core, requirement, overview or elective-pool section. These are analyst classifications for comparison, not university-stated outcomes, and elective-pool themes do not imply every student takes every option. Existing source-stated outcomes are unchanged.

## Full local requirement review (2026-10-10)

All current local requirements were compared against the official page and safe-fetch cache. The seed now carries `curriculum_status: complete` plus an explicit `curriculum_audit`; parsers continue returning partial observations without an audit or verification timestamp. Completeness concerns this minor/concentration, not the host degree.

Reviewed sections: AI concentration, Required core option 1, Required core option 2, Remaining AI electives, Parent-degree eligibility and concentration limit.

Added every local policy and eligibility constraint to the requirement inventory. Advisor exceptions are maxima/conditions represented as notes rather than minimum required credits.

Remaining course metadata gaps: Course descriptions and individual course prerequisites remain unextracted. Some individual course credits are unknown; requirement totals are represented. Public course resources are not comprehensively inventoried. Concentration source provides codes only; course titles remain unverified. Penn course catalog returned a robot-verification challenge on 2026-10-10.


## Required-core metadata — 2026-10-10

The two required option groups now have names and paraphrased descriptions for CIS4210,5210,4190,5190,5200. Fall2026 CIS4190/5190 public syllabus identifies both numbers and distinguishes their assessments; its prerequisites are recorded with the term. Summer2026 CIS5210 home and linked HTML syllabus verify identity, prerequisites and assignment-topic context. Individual credits remain null: selection slots and four-CU concentration totals do not prove each course’s credit amount.

The official CIS Course Site Directory links machine-learning-upenn.github.io, whose actual page is Spring2023; that is an explicitly historical CIS5200 example. The public artificial-intelligence-class.org archive identifies Penn and Chris Callison-Burch, and his official faculty Teaching page independently confirms CIS4210/5210 identity. Its class dates are Fall2022 despite a January2026 update stamp. Only historical description/resource evidence is used for CIS4210; its current prerequisites remain null. No claim that these older resources are the current syllabus.

All resources were visited through the robots-aware fetcher. The protected catalog was not bypassed, and no LMS login was used. Resource parsers validate exact course identities and offering markers, extract source prerequisite fields where contemporary, and hash source contents for review. They never assign completeness or verification timestamps. Descriptions are manually reviewed paraphrases; unknown course credits stay null. BSE seed and requirements remain owned by the national researcher.
