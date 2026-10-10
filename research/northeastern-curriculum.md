# Northeastern combined-major curriculum batch

Reviewed 2026-10-10 from the 2026–2027 official academic catalog. The production Fetcher obtained each direct page with HTTP 200 after robots checks; no access restriction was bypassed. Cached response timestamps are registered on each program source. Raw HTML remains in the ignored HTTP cache.

| Combined BS (Boston) | Courses | Requirement nodes | Curriculum status |
| --- | ---: | ---: | --- |
| [AI and Philosophy](https://catalog.northeastern.edu/undergraduate/computer-information-science/computer-information-science-combined-majors/artificial-intelligence-philosophy-bs-bos/) | 50 | 97 | Partial |
| [AI and Business Administration](https://catalog.northeastern.edu/undergraduate/computer-information-science/computer-information-science-combined-majors/artificial-intelligence-business-admnistration-bs-bos/) | 52 | 101 | Partial |
| [AI and Biology](https://catalog.northeastern.edu/undergraduate/computer-information-science/computer-information-science-combined-majors/artificial-intelligence-biology-bs-bos/) | 72 | 126 | Partial |

These are program-course records, including alternatives and elective pools, not distinct university-wide courses or required-course totals. Every course and requirement links to its direct catalog source. Two source-stated overview outcomes per program are paraphrased; they are educational aims, not measured graduate outcomes. Course categories are editorial taxonomy.

The separate `northeastern_courseleaf.py` helper validates the exact scoped program heading, expected requirement sections and explicit semester-hour units. It parses all major-page requirement tables, area/subarea nesting, course bundles, `or` alternatives, course and credit choices, open-range notes, general electives and policy references. The biology capstone's concurrent research alternatives are nested under that capstone, reusing course IDs already evidenced elsewhere. Excluded courses mentioned in elective range rules are not imported as eligible courses. Source-stated numeric changes produce changed observations; wrong pages, missing expected sections, orphan alternatives and conflicting choice amounts fail conservatively.

Bundle totals are assigned only to requirement nodes. Individual course credits remain null when the catalog provides only a bundle total or an empty alternative/elective credit cell. Numeric credit ranges are preserved in rule summaries without inventing a scalar value. Course descriptions, prerequisites, public course sites and syllabi remain unresearched.

All three records remain partial. External universitywide and NUpath rules are referenced but not fully expanded. Open course ranges, advisor-approved electives and placement substitutions need further modeling/review. Business requires a concentration whose individual curriculum is not expanded; Marketing Analytics has an additional general-elective condition. Biology has open elective ranges and conditional overlap rules. Each record contains a reviewer-authored curriculum audit with these unresolved requirements. The parser never emits an audit or a fresh verification timestamp.

Verification: `python -m pytest tests/test_northeastern_curriculum.py` passes 13 synthetic tests covering changed credits, bundles, alternatives, course/lab choices, open ranges, source scoping, missing sections, source-stated outcomes, unit changes and nested concurrency. All three curated JSON records pass `validate_program`, including provenance and requirement-tree validation. Production refresh can now request the direct program URLs in the adapters' `SOURCES`; it does not replay seed data.

Integration check: the current full Python test run passed 249 tests with nine browser tests skipped in this shell. A separate temporary SQLite database ingested the three records, exported them and built their static detail pages successfully; SQLite integrity check returned `ok`. Shared production database, schema and PLAN were not modified by this batch.

## Second batch: six additional combined majors

The same production Fetcher obtained these six direct 2026–2027 catalogs on 2026-10-10. All remain **partial**, with reviewer-authored unresolved-requirement audits. The first batch's reviewed seed records were not altered.

| Combined BS (Boston) | Courses | Requirement nodes | Course descriptions / prerequisite fields |
| --- | ---: | ---: | ---: |
| [AI and Mathematics](https://catalog.northeastern.edu/undergraduate/computer-information-science/computer-information-science-combined-majors/artificial-intelligence-mathematics-bs-bos/) | 34 | 74 | 6 / 6 |
| [AI and Economics](https://catalog.northeastern.edu/undergraduate/computer-information-science/computer-information-science-combined-majors/artificial-intelligence-economics-bs-bos/) | 49 | 101 | 5 / 5 |
| [AI and Design](https://catalog.northeastern.edu/undergraduate/computer-information-science/computer-information-science-combined-majors/artificial-intelligence-design-bs-bos/) | 62 | 117 | 5 / 5 |
| [AI and Linguistics](https://catalog.northeastern.edu/undergraduate/computer-information-science/computer-information-science-combined-majors/artificial-intelligence-linguistics-bs-bos/) | 45 | 93 | 17 / 14 |
| [AI and Psychology](https://catalog.northeastern.edu/undergraduate/computer-information-science/computer-information-science-combined-majors/artificial-intelligence-psychology-bs-bos/) | 62 | 115 | 6 / 6 |
| [AI and Health Science](https://catalog.northeastern.edu/undergraduate/computer-information-science/computer-information-science-combined-majors/artificial-intelligence-health-science-bs-bos/) | 51 | 93 | 6 / 6 |

This batch adds 303 program-course records, 593 requirement nodes and eight paraphrased source-stated educational aims. Official [Data Science](https://catalog.northeastern.edu/course-descriptions/ds/) and [Linguistics](https://catalog.northeastern.edu/course-descriptions/ling/) subject catalogs supply metadata for 47 program-course records: 45 have supported short description summaries and 42 have prerequisite text. The other selected course blocks omit those fields or lack a reviewed summary, so null remains explicit. These are repeated program-course records, not university-wide unique courses. Credits are source-stated hours within the program's semester catalog.

The helper now distinguishes Design's five alternative two-course paths from five mandatory paths. It supports written selection counts (including four linguistics courses and five economics electives), preserves footnotes without contaminating course names with superscript markers, and treats single-choice lecture/lab/recitation bundles as alternatives. Unsupported written counts fail conservatively rather than flattening the option pool into requirements.

A separate `northeastern_course_metadata.py` parses scoped official course blocks. Metadata summaries require current source phrases, prerequisites are observed from the current page, and the Linguistics seminar's extra prerequisite in descriptive prose is preserved. Every subject source has a registered source ID and `SOURCE_PARSERS` entry. These parsers emit metadata-only review candidates for the explicitly selected codes; they do not automatically replace a program curriculum or infer that omitted prerequisites mean none.

Remaining boundaries include universitywide/NUpath requirements, open elective course ranges, adviser-approved substitutions, major-specific GPA/grade policies and conditional course reuse. Design recommendations and optional seminars remain notes, not mandatory courses. Economics' lower-level elective limit, Linguistics' non-reuse rule, Psychology's transfer restriction and separately stated major-credit requirement, and Health Science's grade conditions are preserved for review. Most courses still lack descriptions/prerequisites; public course websites and syllabi remain unresearched. None of these records claims a complete degree curriculum.

Second-batch verification: 27 focused parser tests passed. All 13 registered source parsers succeeded with the production fetcher’s current cache, and a repeated run added zero duplicate candidates. A separate temporary database passed ingest, export, static build and SQLite integrity checks. A contemporaneous shared discovery-test failure concerned the RIT adapter/source registration being updated by another agent; no Northeastern test failed.
