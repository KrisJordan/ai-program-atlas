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

## Third batch: seven science-focused combined majors

Seven additional 2026–2027 catalogs were obtained through the robots-aware Fetcher on 2026-10-10. Every record remains partial and carries a source-backed audit.

| Combined BS (Boston) | Courses | Requirement nodes |
| --- | ---: | ---: |
| [AI and Behavioral Neuroscience](https://catalog.northeastern.edu/undergraduate/computer-information-science/computer-information-science-combined-majors/artificial-intelligence-behavioral-neuroscience-bs-bos/) | 71 | 115 |
| [AI and Biochemistry](https://catalog.northeastern.edu/undergraduate/computer-information-science/computer-information-science-combined-majors/artificial-intelligence-biochemistry-bs-bos/) | 52 | 97 |
| [AI and Chemistry](https://catalog.northeastern.edu/undergraduate/computer-information-science/computer-information-science-combined-majors/artificial-intelligence-chemistry-bs-bos/) | 51 | 86 |
| [AI and Physics](https://catalog.northeastern.edu/undergraduate/computer-information-science/computer-information-science-combined-majors/artificial-intelligence-physics-bs-bos/) | 49 | 91 |
| [AI and Ecology and Evolutionary Biology](https://catalog.northeastern.edu/undergraduate/computer-information-science/computer-information-science-combined-majors/artificial-intelligence-ecology-evolutionary-biology-bs-bos/) | 71 | 113 |
| [AI and Environmental and Sustainability Sciences](https://catalog.northeastern.edu/undergraduate/computer-information-science/computer-information-science-combined-majors/artificial-intelligence-environmental-sustainability-sciences-bs-bos/) | 82 | 122 |
| [AI and Public Health](https://catalog.northeastern.edu/undergraduate/computer-information-science/computer-information-science-combined-majors/artificial-intelligence-public-health-bs-bos/) | 97 | 151 |

The batch contributes 473 program-course records, 775 requirement nodes, eleven source-stated educational aims and 38 DS course-metadata observations. All 38 DS records have short supported descriptions and formal prerequisite text. Counts include repeated courses across programs and elective pools.

New source-specific cases include Public Health's two multi-course biology options, a separate required psychology subsection, and independent introductory/upper-level social-science choices. Physics 2 is required independently of the Physics 1 alternative. Ecology's topical choice preserves 16 semester hours and a minimum of one course from each of three lists; summaries explicitly describe the minimum, while individual distribution/overlap checks remain unresolved. Environmental and Sustainability Sciences uses one four-course pool spanning multiple subject headings. Only its reviewed profile pools those unindented subheadings; unrelated subsection boundaries end a choice. Course-title parentheses are retained unless they introduce an explicit requirement annotation. The ecology overview's restrictions on combining majors/minors are preserved as source-guarded policy evidence.

Universitywide/NUpath requirements, eligible courses within open ranges, placement substitutions, corequisite/grade rules and individual course overlap remain documented review gaps. The university's published degree totals are preserved as source notes without summing course pools. Course metadata outside selected DS blocks and public course sites/syllabi remain unresearched. The updated focused suite has 35 passing tests, including the new distribution, sequence-boundary, option-path and overview-policy cases.

Third-batch integration: a temporary database ingested every currently enriched Northeastern record, then passed 34 cached production source parses across 18 programs (including concurrently enriched minors), repeat candidate deduplication, static export/build and SQLite integrity checks. Shared production data/schema were not modified.


## Fourth batch: remaining seven combined degrees

Seven official 2026–2027 program catalogs were reviewed on 2026-10-10 through the robots-aware Fetcher. Six award BS degrees; Environmental Engineering and AI awards **BSEnvE**, preserved in the full title and `award_level: other`. None has been relabeled as a BS or as two degrees.

| Program | Courses | Requirement nodes |
| --- | ---: | ---: |
| [Artificial Intelligence and Criminal Justice, BS (Boston)](https://catalog.northeastern.edu/undergraduate/computer-information-science/computer-information-science-combined-majors/artificial-intelligence-criminal-justice-bs-bos/) | 67 | 122 |
| [Artificial Intelligence and Communication Studies, BS (Boston)](https://catalog.northeastern.edu/undergraduate/computer-information-science/computer-information-science-combined-majors/artificial-intelligence-communication-studies-bs-bos/) | 77 | 133 |
| [Artificial Intelligence and Speech-Language Pathology and Audiology, BS (Boston)](https://catalog.northeastern.edu/undergraduate/computer-information-science/computer-information-science-combined-majors/artificial-intelligence-speech-language-pathology-audiology-bs-bos/) | 43 | 78 |
| [Artificial Intelligence and Sociology, BS (Boston)](https://catalog.northeastern.edu/undergraduate/computer-information-science/computer-information-science-combined-majors/artificial-intelligence-sociology-bs-bos/) | 36 | 80 |
| [Environmental Engineering and Artificial Intelligence, BSEnvE (Boston)](https://catalog.northeastern.edu/undergraduate/engineering/civil-environmental/environmental-engineering-artificial-intelligence-bsenve/) | 68 | 112 |
| [Artificial Intelligence and International Affairs, BS (Boston)](https://catalog.northeastern.edu/undergraduate/computer-information-science/computer-information-science-combined-majors/artificial-intelligence-international-affairs-bs-bos/) | 180 | 288 |
| [Artificial Intelligence and Journalism, BS (Boston)](https://catalog.northeastern.edu/undergraduate/computer-information-science/computer-information-science-combined-majors/artificial-intelligence-journalism-bs-bos/) | 45 | 92 |

This batch adds 516 program-course records and 905 nested requirement nodes. Official DS and partner-subject catalogs supply 193 metadata observations, including 57 supported description paraphrases and 87 prerequisite statements. Seven educational aims are paraphrased from the program overviews as source-stated outcomes. Counts include course options and repeated observations across programs, not required-course totals.

International Affairs has a two-course Global Dynamics choice spanning a second table; thematic headings explicitly do not impose additional selections. The model keeps its one-course-at-2000+ and no-reuse conditions visible as unresolved policy constraints. Regional Analysis is a choice of one region, with two courses within that region; advisor-approved study-abroad offerings remain unexpanded. A separate International Affairs elective also spans tables. The capstone must integrate international affairs and AI, and the international-experience requirement is a policy note rather than an invented course. Profiles guard the specific source statements; changed semantics fail for review.

Journalism's transfer residency table is conditional and becomes a source-guarded policy note, not a second unconditional course list. Its three named courses still occur in the ordinary curriculum. The parser accepts that catalog's SH/credits wording only after establishing explicit semester-hour context. Journalism's repeated writing course, and Engineering's repeated course allocations across categories, retain their identities without summing them into additional courses or credits. The engineering substitution footnote and grade/GPA conditions remain explicit review gaps.

Communication Studies retains its two integrative units and separate capstone choice. Sociology preserves lower- and upper-level open elective counts and non-reuse conditions. Speech-Language Pathology and Audiology retains C-or-higher conditions and unfulfilled NUpath responsibilities. SLPA 5107 is four hours in the program requirement but 3–4 in the general course catalog: the scalar course-credit field remains null, while the program-required four hours remains on its requirement node. GE 1501 and GE 1502 each have four hours established by the course catalog; partial allocations in program categories are never substituted as course credit values.

Every inventory remains **partial**. Universitywide/NUpath policy expansion, individual substitutions and approvals, elective eligibility, overlap constraints, and much course metadata remain unresolved in each audit. No language requirement is invented for International Affairs. Public course websites and syllabi remain unresearched.

Validation: synthetic tests cover two-table pools (including actual subheader DOM), same-region alternatives, changed choice counts and semantic guards, conditional transfer evidence, explicit BSEnvE identity, semester-unit guards and variable-credit metadata. A temporary database ingested all seven then repeated with zero changes; all 22 registered source parsers succeeded through the standard Fetcher, then repeated with zero new candidates or source changes. Export/static build and SQLite integrity passed. No maintained database or release-plan edits were made by this researcher.
