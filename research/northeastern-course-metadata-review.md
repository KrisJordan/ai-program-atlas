# Northeastern course metadata continuation

## Foundation and systems batch — 2026-10-10

Scope: the existing 23 combined-degree variants, preserving 22 BS awards and one BSEnvE, all partial. The public [Computer Science](https://catalog.northeastern.edu/course-descriptions/cs/), [Mathematics](https://catalog.northeastern.edu/course-descriptions/math/) and [Cybersecurity](https://catalog.northeastern.edu/course-descriptions/cy/) subject catalogs were fetched through the robots-aware production Fetcher, each HTTP 200, on 2026-10-10 at 23:49:50–53 UTC. The reviewed catalog edition is 2026–2027; no semester-specific offering or launch date is inferred.

All 29 distinct CS/MATH/CY codes already present in the 23 inventories were reviewed: 13 CS, 14 MATH and two CY. They produce 263 program-course observations (180 CS, 72 MATH and 11 CY), not 263 distinct institutional courses or required courses. The same official description may be relevant to multiple independently addressable variants.

| Metadata among the 263 selected observations | Before | After |
| --- | ---: | ---: |
| Short descriptions | 0 | 263 |
| Explicit prerequisite conditions | 0 | 71 |
| Fixed semester-hour values | 133 | 262 |

The remaining 192 prerequisite fields stay null because no explicit prerequisite was found in the reviewed course block; null is not a claim of unrestricted enrollment. Course titles, numeric values and prerequisite logic come from the course blocks. Concise descriptions are reviewer paraphrases with source-phrase guards: if the supporting text changes, the adapter does not replay the old summary. No raw HTML or full descriptions are committed.

### Conditions and source scope

- MATH 1342 embeds its prerequisite/permission alternative in the prose rather than a labelled prerequisite field. The parser observes that required condition. MATH 1245, 2321 and 2341 describe recommended preparation; these remain separately labelled notes and do not become prerequisites.
- Course corequisites, including CS 1800’s CS 1802 and the CS 2000/2001 and 2100/2101 lab pairings, are recorded as concurrent course conditions in notes. They are not mislabelled as prerequisites or silently added as universal requirements for students who do not select that course. Existing prescribed program requirement trees remain unchanged.
- CS 4991 publishes discrete credit options of 4 or 8 hours. Its scalar course-credit value remains null and its options appear in a note; the values are not added together, averaged or collapsed to four. Any credit allocation in a degree’s requirement table remains that separately sourced requirement.
- Alternative prerequisite courses, parenthetical groups, conjunctions and minimum grades remain intact. A permitted graduate-admission route in CY 5240 is retained as published; undergraduate applicability is not expanded beyond the program’s own listed option.
- Independently stated course credits fill previously unknown lab or alternative rows without assigning a bundle’s total to each course. No requirement-level credit, parent, choice count or course membership changes.

### Refresh and verification

Each variant registers explicit reviewed subject/course selectors; 52 new source-parser registrations cover the three subject pages across the variants. Parsers operate on current HTML, validate exact subject headings and scoped course blocks, reject missing/duplicate selected codes and never read seed files or emit review timestamps/completeness audits. Source records retain the actual fetch timestamp, edition and exact course-code locator. Recommendations, corequisites and variable-credit conditions travel as labelled metadata notes.

Synthetic tests cover changed prerequisites/credits/corequisites, discrete credit options, required prose versus recommendations, changed description guards, separate registered selectors and wrong/ambiguous source content. The existing historical requirement-graph checks continue to ensure all 23 original major/core graphs survive unchanged. Shared family definitions, home-college context, curriculum partial status, degree identities, public course-site links and syllabi are preserved.

### Continuing queue

Next inspect accessible BIOL/CHEM and economics/psychology course catalogs for already listed high-value disciplinary requirements. Do not revisit the documented home-college-choice boundary without new institutional evidence. Review any explicit learning-outcome statement by its source context, separately from marketing aims and career lists. A course catalog’s first observed date does not establish a program launch date.

Validation at the foundation/systems checkpoint: **208 focused tests passed**. A temporary database ingested all 23 variants and repeated with zero changed records. All 52 new source registrations succeeded twice using the safe Fetcher/cache; the second observations created zero candidates and reported zero source changes. Export/static build and SQLite integrity passed. The maintained database and publication plan were not edited.
