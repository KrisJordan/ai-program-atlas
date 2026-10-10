# Artificial Intelligence, Additional Major

Reviewed 2026-10-10 against official university sources. Raw source HTML was fetched to `/tmp/atlas-*.html` for development and is not committed. University robots policies were checked; no access restrictions were bypassed.

## Coverage and limits

The parser extracts five CS core courses, two AI core courses, four one-course AI cluster choices, ethics and cognition. Six mathematics requirements and admission prerequisite alternatives are not fully extracted. The additional major is not an independently awarded degree: program_kind=additional_major, award_level=other. No launch date verified. Overlap restrictions are summarized in record notes.

Seed record: `data/programs/cmu-additional-ai.json`. 44 observed course records; option pools are not course requirements to sum. All curriculum records remain explicitly partial. Selected public course resources are verified below; others remain null.

## Parser behavior

`PROGRAM_ID`, `SOURCES` and `parse(html: str) -> dict` are exported. Parsing validates the official page heading and expected curriculum sections, then extracts actual course codes, titles when present, credits when explicit, and nested requirements. It never reads the curated JSON seed or returns a refreshed `last_verified`. Missing required headings/sections or changed selection rules raise `ValueError`. Returned observations remain partial and require coordinator review before replacing curated evidence.

## Source metadata

- [Artificial Intelligence, Additional Major](https://coursecatalog.web.cmu.edu/schools-colleges/schoolofcomputerscience/artificialintelligence/artificial-intelligence-additional-major/) — locator: Curriculum tables; catalog: 2026-2027; source date: not stated; confidence: high. Metadata ID: `cmu-additional-ai-catalog`.
- [Academic calendar](https://www.cmu.edu/hub/calendar/) — locator: Fall and spring academic terms; catalog: not stated; source date: not stated; confidence: high. Metadata ID: `cmu-additional-ai-calendar`.

## Validation

`tests/test_cmu_penn.py` uses synthetic HTML, not copied catalog fixtures, and checks section failure, actual changed-course extraction, nested options, unknown credits, credential distinctions, and record references. Live official HTML was also parsed locally for this review.

## Public course resource enrichment (2026-10-10)

- [15-150: Functional Programming, Fall 2026](https://www.cs.cmu.edu/~15150/) — Heading, overview and learning outcomes. Source ID: `cmu-15150-fall-2026-site`.
- [15-213/15-513/14-513 Introduction to Computer Systems (ICS), Fall 2026](https://www.cs.cmu.edu/~213/) — Course identity and Course Syllabus link. Source ID: `cmu-15213-fall-2026-site`.
- [15-213 / 15-513 / 14-513: Introduction to Computer Systems — Fall 2026 syllabus](https://www.cs.cmu.edu/~213/syllabus/syllabus.pdf) — PDF page 1: course codes, university and Fall 2026. Source ID: `cmu-15213-fall-2026-syllabus`.

Course `source_id` still cites the curriculum; resource metadata independently supports `public_site` and `syllabus`. CMU resources identify Fall 2026; the Penn outline is explicitly a historical Fall 2021 example linked by the official CIS 3200 archive (older CIS 320 numbering), not current curriculum evidence. No syllabus content was copied into the repository.

## Inferred comparison themes

Added explicitly `inferred_taxonomy` labels from the existing cited curriculum: AI methods, Mathematical foundations, Responsible AI and society, Software and systems, Applied AI. Locators name the supporting core, requirement, overview or elective-pool section. These are analyst classifications for comparison, not university-stated outcomes, and elective-pool themes do not imply every student takes every option. Existing source-stated outcomes are unchanged.

## Local inventory review — 2026-10-10

The complete local additional-major curriculum is now mapped: 61 observed course records and 30 nested requirement/policy nodes. Mathematics preserves six alternative probability paths, including four two-course AND sequences. Published combined 18-unit values remain on sequence requirements, not copied to each course. Admission includes the B average and course prerequisites; the 07-180 exception and aggregate five-course overlap cap (including the 36-402 exception) are explicit. This complete local inventory does not certify the host degree. Individual descriptions, prerequisites and blank course-unit cells remain separate metadata gaps.

`requirements.py` extends the source table parser, validates the complete heading inventory and admission/policy markers, and extracts actual row values. It fails on changed policies for review. Parsing remains `partial`, emits no audit, and cannot renew the reviewed complete seed automatically. Synthetic tests cover sequence units, alternatives, admission and policy drift.

## Course metadata — 2026-10-10

Verified 40 matching course blocks in the official [SCS course directory](https://coursecatalog.web.cmu.edu/schools-colleges/schoolofcomputerscience/courses/). Separate `SOURCE_PARSERS` extraction observes title, explicit individual units and prerequisite Boolean expressions; it never imports seed values or marks curriculum complete. Range-valued credits and absent prerequisites remain null. Seven AI/CS core descriptions are selectively paraphrased across applicable programs; other descriptions remain unknown. Course source IDs now point to this directory, while requirement membership keeps program-catalog citations. Existing independently verified public sites/syllabi are preserved; links merely listed in the catalog were not promoted without a visit. Robots disallow the search popup route, so it was not fetched; the permitted canonical directory is used. Penn course catalog pages encountered a challenge and were not bypassed.


## Core metadata and offering resources — 2026-10-10

Rechecked 07-280, 07-380, 11-411 and 16-385 against the 2026–2027 SCS directory; explicit 12-unit values and catalog prerequisite Boolean expressions remain unchanged. Added paraphrases for NLP and vision, so all four selected AI core/choice courses now have descriptions, prerequisites and credit values. The directory observer now hashes description text to flag future changes without copying catalog paragraphs into candidate descriptions.

Visited every promoted course resource: 07-280 and 07-380 identify Fall2026; official 11-411 gateway links a Spring2026 course site and public HTML syllabus; 16-385 catalog URL resolves to a Spring2020 site with a Syllabus and Schedule section. These older examples are explicitly dated, not presented as current enrollment rules. Reviewed the CMU HTTP-to-HTTPS upgrade against the same host’s available HTTPS robots policy. No private LMS or publisher materials were accessed.

07-380’s Fall2026 site and catalog differ: the site omits catalog 21-122 and lists additional probability choices. Catalog prerequisites remain stored; source-specific notes document the discrepancy. The 11-411 gateway itself mixes a Fall2026 heading, S’26 site link and older syllabus/grading references, so the unambiguous linked Spring2026 offering is used as the example resource.

For the BS and minor only, the existing source-stated outcomes were checked in actual source context: BS says skills expected upon graduation; minor has What You’ll Learn / Students who minor in AI will. They are explicitly tagged learning_outcome. Inferred themes remain unchanged; additional-major outcomes were not reclassified.
