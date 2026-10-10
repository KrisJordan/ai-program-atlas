# Artificial Intelligence, Minor

Reviewed 2026-10-10 against official university sources. Raw source HTML was fetched to `/tmp/atlas-*.html` for development and is not committed. University robots policies were checked; no access restrictions were bypassed.

## Coverage and limits

The parser extracts AI core, probability alternatives, three technical pools and two societal pools. The six-course minor and four prerequisite areas are source-stated. Technical choices must come from two distinct clusters; the societal choice comes from either cluster. Cross-cluster rules are nested choices with explicit summaries, rather than requiring every cluster. Admission, prerequisite alternatives, overlap and mini-course rules are now mapped. No launch date verified.

Seed record: `data/programs/cmu-minor-ai.json`. 63 observed course records; option pools are not course requirements to sum. The local requirement inventory is now complete after the review below; course metadata remain partial. Public course sites and syllabi have not been verified and are null.

## Parser behavior

`PROGRAM_ID`, `SOURCES` and `parse(html: str) -> dict` are exported. Parsing validates the official page heading and expected curriculum sections, then extracts actual course codes, titles when present, credits when explicit, and nested requirements. It never reads the curated JSON seed or returns a refreshed `last_verified`. Missing required headings/sections or changed selection rules raise `ValueError`. Returned observations remain partial and require coordinator review before replacing curated evidence.

## Source metadata

- [Artificial Intelligence, Minor](https://coursecatalog.web.cmu.edu/schools-colleges/schoolofcomputerscience/minors/artificial-intelligence-minor/) — locator: Curriculum tables; catalog: 2026-2027; source date: not stated; confidence: high. Metadata ID: `cmu-minor-ai-catalog`.
- [Academic calendar](https://www.cmu.edu/hub/calendar/) — locator: Fall and spring academic terms; catalog: not stated; source date: not stated; confidence: high. Metadata ID: `cmu-minor-ai-calendar`.

## Validation

`tests/test_cmu_penn.py` uses synthetic HTML, not copied catalog fixtures, and checks section failure, actual changed-course extraction, nested options, unknown credits, credential distinctions, and record references. Live official HTML was also parsed locally for this review.

## Inferred comparison themes

Added explicitly `inferred_taxonomy` labels from the existing cited curriculum: AI methods, Mathematical foundations, Responsible AI and society, Applied AI. Locators name the supporting core, requirement, overview or elective-pool section. These are analyst classifications for comparison, not university-stated outcomes, and elective-pool themes do not imply every student takes every option. Existing source-stated outcomes are unchanged.

## Full local requirement review (2026-10-10)

All current local requirements were compared against the official page and safe-fetch cache. The seed now carries `curriculum_status: complete` plus an explicit `curriculum_audit`; parsers continue returning partial observations without an audit or verification timestamp. Completeness concerns this minor/concentration, not the host degree.

Reviewed sections: Six-course AI minor, Prerequisites, Required Core Courses, Technical Electives, Societal Aspects of AI, Eligibility and admission, Mini-course combination, Double-counting limit.

Added all four prerequisite groups, six-course structure, distinct technical-cluster choices, societal cluster selection, mini-course exception, non-SCS eligibility, admission C-average/deadline and two-course aggregate overlap cap. All 63 named course records are inventoried, including prerequisites and alternative/elective pools; this is not a 63-course workload.

Remaining course metadata gaps: Course descriptions and individual course prerequisites remain unextracted. Some individual course credits are unknown; requirement totals are represented. Public course resources are not comprehensively inventoried.

## Course metadata — 2026-10-10

Verified 37 matching course blocks in the official [SCS course directory](https://coursecatalog.web.cmu.edu/schools-colleges/schoolofcomputerscience/courses/). Separate `SOURCE_PARSERS` extraction observes title, explicit individual units and prerequisite Boolean expressions; it never imports seed values or marks curriculum complete. Range-valued credits and absent prerequisites remain null. Seven AI/CS core descriptions are selectively paraphrased across applicable programs; other descriptions remain unknown. Course source IDs now point to this directory, while requirement membership keeps program-catalog citations. Existing independently verified public sites/syllabi are preserved; links merely listed in the catalog were not promoted without a visit. Robots disallow the search popup route, so it was not fetched; the permitted canonical directory is used. Penn course catalog pages encountered a challenge and were not bypassed.


## Core metadata and offering resources — 2026-10-10

Rechecked 07-280, 07-380, 11-411 and 16-385 against the 2026–2027 SCS directory; explicit 12-unit values and catalog prerequisite Boolean expressions remain unchanged. Added paraphrases for NLP and vision, so all four selected AI core/choice courses now have descriptions, prerequisites and credit values. The directory observer now hashes description text to flag future changes without copying catalog paragraphs into candidate descriptions.

Visited every promoted course resource: 07-280 and 07-380 identify Fall2026; official 11-411 gateway links a Spring2026 course site and public HTML syllabus; 16-385 catalog URL resolves to a Spring2020 site with a Syllabus and Schedule section. These older examples are explicitly dated, not presented as current enrollment rules. Reviewed the CMU HTTP-to-HTTPS upgrade against the same host’s available HTTPS robots policy. No private LMS or publisher materials were accessed.

07-380’s Fall2026 site and catalog differ: the site omits catalog 21-122 and lists additional probability choices. Catalog prerequisites remain stored; source-specific notes document the discrepancy. The 11-411 gateway itself mixes a Fall2026 heading, S’26 site link and older syllabus/grading references, so the unambiguous linked Spring2026 offering is used as the example resource.

For the BS and minor only, the existing source-stated outcomes were checked in actual source context: BS says skills expected upon graduation; minor has What You’ll Learn / Students who minor in AI will. They are explicitly tagged learning_outcome. Inferred themes remain unchanged; additional-major outcomes were not reclassified.
