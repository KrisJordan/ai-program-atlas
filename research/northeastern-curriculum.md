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
