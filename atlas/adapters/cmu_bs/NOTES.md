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

## Course metadata — 2026-10-10

Verified 38 matching course blocks in the official [SCS course directory](https://coursecatalog.web.cmu.edu/schools-colleges/schoolofcomputerscience/courses/). Separate `SOURCE_PARSERS` extraction observes title, explicit individual units and prerequisite Boolean expressions; it never imports seed values or marks curriculum complete. Range-valued credits and absent prerequisites remain null. Seven AI/CS core descriptions are selectively paraphrased across applicable programs; other descriptions remain unknown. Course source IDs now point to this directory, while requirement membership keeps program-catalog citations. Existing independently verified public sites/syllabi are preserved; links merely listed in the catalog were not promoted without a visit. Robots disallow the search popup route, so it was not fetched; the permitted canonical directory is used. Penn course catalog pages encountered a challenge and were not bypassed.

## Explicit remaining degree audit — 2026-10-10

The standalone BS remains **partial**. `curriculum_audit` now names the unresolved math/statistics alternatives, SCS elective/science distributions, humanities and linked general education, first-year seminar, CoRE@CMU, free electives, optional research-thesis conditions, and linked degree/grading policies. Course metadata enrichment does not alter this requirement-inventory judgment. The 38 matched SCS records include 29 stated prerequisite expressions and seven reviewed core-course summaries; missing fields remain unknown.

## Full degree and linked-policy review — 2026-10-10

The 2026–2027 BS requirement inventory is reviewed complete: 273 positive course-option records and 65 requirement/policy nodes. This supersedes the earlier partial-audit entries above. It maps the primary curriculum, mathematics conditional substitutions and probability AND/OR paths, programming prerequisite, cluster minima/designated options, SCS elective exclusions/mini exception, degree-wide science/humanities distributions, seminar/Core, published 22 free-elective units, 360 total units and PE/ROTC/StuCo cap. Linked school policies cover graduation/residence, academic standing and AI progress, and conditional transfer rules. University policies cover credit/grading, repeats, transfer/examination approvals, the first-year QPA exception, applicable catalog, certification and eight-year unit limit. Optional thesis application and deliverables remain conditional note branches. Adviser/dean approval pathways are represented as published rules; this is not an individual graduation audit.

### Catalog/current source reconciliation

The catalog explicitly dates its general-education tables to July 2026 and directs readers to separate **up-to-date** science and humanities lists. We inspected those public pages and the exact JSON feed URLs embedded in their JavaScript, through the robots-aware fetcher. All feeds returned complete responses (`success=true`, `more=0`) on 2026-10-10; no private sheet, login or restricted syllabus was accessed. The current feeds govern the reconciled finite pools; catalog prose still supplies complementary distribution rules. Each feed, current page, catalog and policy page has a distinct registered source ID. Current pages also supply approval rules for combined minis and ECE graduate exclusions. Source parsers collect separate partial candidates; only this explicit review assigned completeness.

Observed code differences from the July catalog:

- Science additions omit 85-314. Lab membership is unchanged.
- Science exclusions add 18-090, 18-411 and 49-101.
- Category 2 adds 79-177, 79-244 and 82-208; removes 79-246.
- Category 3 adds 48-321, 79-145, 79-156 and 79-286.
- Humanities elective additions omit 73-369; it remains independently listed in Category 2.
- Humanities exclusions add department-wide 36-xxx, 67-xxx and 73-xxx rules with explicit exceptions, plus 80-405 and 85-370; remove 85-314 and 85-414.

No general Category 1 pool is imported for AI, which uses Category 1A. Excluded codes appear in policy notes, not as approved course options. Current-source titles/units are used for current positive pools; school course-directory facts enrich 51 matching records. Null descriptions, prerequisite omissions, unnamed inline math substitutes, variable units and sparse public syllabi remain metadata gaps separate from requirement completeness. The large course count includes alternatives and general-education options, not 273 required courses. Source pages remain only in ignored cache or `/tmp`.


## Core metadata and offering resources — 2026-10-10

Rechecked 07-280, 07-380, 11-411 and 16-385 against the 2026–2027 SCS directory; explicit 12-unit values and catalog prerequisite Boolean expressions remain unchanged. Added paraphrases for NLP and vision, so all four selected AI core/choice courses now have descriptions, prerequisites and credit values. The directory observer now hashes description text to flag future changes without copying catalog paragraphs into candidate descriptions.

Visited every promoted course resource: 07-280 and 07-380 identify Fall2026; official 11-411 gateway links a Spring2026 course site and public HTML syllabus; 16-385 catalog URL resolves to a Spring2020 site with a Syllabus and Schedule section. These older examples are explicitly dated, not presented as current enrollment rules. Reviewed the CMU HTTP-to-HTTPS upgrade against the same host’s available HTTPS robots policy. No private LMS or publisher materials were accessed.

07-380’s Fall2026 site and catalog differ: the site omits catalog 21-122 and lists additional probability choices. Catalog prerequisites remain stored; source-specific notes document the discrepancy. The 11-411 gateway itself mixes a Fall2026 heading, S’26 site link and older syllabus/grading references, so the unambiguous linked Spring2026 offering is used as the example resource.

For the BS and minor only, the existing source-stated outcomes were checked in actual source context: BS says skills expected upon graduation; minor has What You’ll Learn / Students who minor in AI will. They are explicitly tagged learning_outcome. Inferred themes remain unchanged; additional-major outcomes were not reclassified.
