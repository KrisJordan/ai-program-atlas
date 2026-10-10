# Artificial Intelligence for Business

Reviewed 2026-10-10 against official university sources. Raw source HTML was fetched to `/tmp/atlas-*.html` for development and is not committed. University robots policies were checked; no access restrictions were bypassed.

## Coverage and limits

The parser extracts the two required pillar courses, 1 CU foundation electives and 1.5 CU impact electives. This is a concentration within BS Economics, not a standalone AI degree, despite the catalog URL ending in -bs. The official undergraduate department page establishes the credential. Crosslisted MGMT/OIDD 3130 is one course record. Elective credits are null; required course credits must be present or the parser fails. The three published pass/fail and advisor-approved allowance policies are mapped. Host-degree requirements are outside this concentration audit.

Seed record: `data/programs/penn-concentration-ai-business.json`. 28 observed course records; option pools are not course requirements to sum. The local requirement inventory is now complete after the review below; course metadata remain partial. Public course sites and syllabi have not been verified and are null.

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

## Full local requirement review (2026-10-10)

All current local requirements were compared against the official page and safe-fetch cache. The seed now carries `curriculum_status: complete` plus an explicit `curriculum_audit`; parsers continue returning partial observations without an audit or verification timestamp. Completeness concerns this minor/concentration, not the host degree.

Reviewed sections: Concentration requirements, Pillar F, Pillar I, Letter-grade policy, Independent-study allowance, Outside-Wharton allowance.

Added every local policy and eligibility constraint to the requirement inventory. Advisor exceptions are maxima/conditions represented as notes rather than minimum required credits.

Remaining course metadata gaps: Course descriptions and individual course prerequisites remain unextracted. Some individual course credits are unknown; requirement totals are represented. Public course resources are not comprehensively inventoried.


## Required-core metadata — 2026-10-10

Visited the official Statistics and Legal Studies undergraduate Course Descriptions pages. Exact STAT4230 and LGST2420 blocks support new paraphrased descriptions. STAT4230 explicitly requires STAT1020 OR STAT1120 OR STAT4310 and allows concurrent enrollment with instructor permission; both the alternatives and qualification are preserved. LGST2420 has no published prerequisite field, so null remains unknown, not none required. Existing formal titles and 1/0.5-CU values remain supported by the concentration curriculum source; department metadata sources have separate IDs.

The LGST faculty page corroborates Fall2026 teaching and links a term-specific syllabus, but apps.wharton.upenn.edu/robots.txt redirects to https://www.wharton.upenn.edu:443/404. The safe-fetch guard stopped there. The linked syllabus contents were not verified, and public_site/syllabus stay null. We did not bypass the course-catalog challenge or access authenticated systems.

Course-block parsers select only the requested identity, detect changed prerequisites/description digests, keep absent credits and prerequisites null, and do not promote unvisited syllabus links. Completeness of the reviewed local requirement inventory is unchanged.
