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

## Disciplinary batch — 2026-10-10

The next batch reviews 22 distinct, already listed courses in [Biology](https://catalog.northeastern.edu/course-descriptions/biol/), [Chemistry and Chemical Biology](https://catalog.northeastern.edu/course-descriptions/chem/), [Economics](https://catalog.northeastern.edu/course-descriptions/econ/) and [Psychology](https://catalog.northeastern.edu/course-descriptions/psyc/). All four pages returned HTTP 200 through the safe Fetcher at 23:53:57–23:54:02 UTC; edition 2026–2027.

Selections prioritize shared foundation courses and methods connecting the disciplines with AI: BIOL 1107/1108, 2301/2302, 2407 and 4701; CHEM 1161/1162/1163 and 2311/2312; ECON 1115/1116, 2315/2316, 2350 and 2560; PSYC 1101, 2320, 3450, 3466 and 4540. Each parser observes only codes actually listed in its concrete program; a prerequisite mentioned by the catalog is not automatically inserted into the prescribed major inventory.

Across 18 affected variants, this yields **79 additional descriptions and 39 explicit prerequisite statements**. Fixed-credit availability among these 79 observations increases from **21 to 79**. Twenty-six additional program-local sources and parser registrations preserve exact code locators. Together with the first batch, the additions are 342 descriptions, 110 prerequisite statements and 187 fixed-credit values across 51 distinct course codes; program-course counts repeat shared courses by variant.

CHEM 1163 explicitly carries zero hours; this known value is preserved, while absent values elsewhere remain null. BIOL 2302 and ECON 2350 permit concurrent enrollment in courses labelled as prerequisites; their permissions, alternatives and grade thresholds remain intact. PSYC 2320 advises completion before the end of sophomore year; that planning advice is recorded separately from registration prerequisites. All lab corequisites remain concurrent conditions in notes. No presumed course-offering term, institutional launch date or learning-outcome claim is created from a course description.

The four catalogs still have unreviewed disciplinary courses; this selected batch does not claim exhaustive subject coverage. The next accessible queue includes biology/neuroscience electives, upper-level chemistry, economics methods/policy electives, and psychology laboratories/seminars. Home-college applicability remains the distinct institutional-confirmation boundary documented in the companion review.

Validation at the disciplinary checkpoint: **210 focused tests passed**. All 23 reviewed variants ingested and repeated idempotently in a temporary database; the 26 new source registrations succeeded twice, with zero second-run candidates or source changes. Export/build and integrity checks passed.

## Data Science consistency follow-up — 2026-10-10

The [official DS catalog](https://catalog.northeastern.edu/course-descriptions/ds/), safely fetched at 22:22:37 UTC for the 2026–2027 edition, already supported most later variants but not all initial variants or DS 1300 descriptions. Eight variants were reconciled against the same accessible current source. Three gain a program-local DS source; five extend an existing source locator/observation. Explicit selectors replace narrower DS observations with one fetch per URL, without adding any course to a degree.

This adds **23 descriptions, 18 prerequisite statements and one fixed-credit value**. All **133 existing DS observations across 23 variants** now have independently stated four-semester-hour values and guarded concise descriptions. The 128 observations outside DS 1300 preserve explicit prerequisites; the five DS 1300 observations remain null for prerequisites because its block does not publish one. Its description concerns the ethical and epistemological effects of digital technology, not a claimed learning-outcome assessment. No program learning outcome or launch date is inferred.

Combined additions through this follow-up: **365 descriptions, 128 prerequisite statements and 188 fixed-credit values**. These are added program-course fields, not distinct course counts or curriculum-completeness claims. All 23 programs remain partial at the established home-college applicability boundary.

DS follow-up validation: **212 focused tests passed**; all-variant temporary ingest/repeat/export/build/integrity passed. All eight revised DS source registrations succeeded twice via the safe Fetcher/cache, with zero repeat candidates or source changes.

## Writing, physics and philosophy — 2026-10-10

The official [English Writing](https://catalog.northeastern.edu/course-descriptions/engw/), [Physics](https://catalog.northeastern.edu/course-descriptions/phys/) and [Philosophy](https://catalog.northeastern.edu/course-descriptions/phil/) catalogs returned HTTP 200 through the safe Fetcher at 23:58:19–22 UTC. The 2026–2027 source blocks support 29 distinct selected codes: all 12 ENGW codes already in the inventories, eight introductory PHYS lecture/lab/seminar/recitation codes, and nine PHIL logic/technology/AI-ethics codes. Remaining upper-level physics and philosophy options are outside this selected batch.

This supplies **152 descriptions and 78 explicit prerequisite statements**, with fixed credits increasing **41→152**, across all 23 variants. The program-course observations comprise 110 writing, 22 physics and 20 philosophy records. Thirty-seven new source registrations observe the selections. Published C-grade alternatives for advanced writing remain intact; cross-college combined-major audiences in those course descriptions do not establish mandatory or allowed home-college assignments.

PHYS 1152 and 1153 embed mandatory concurrent registration in prose rather than a corequisite label. The parser now observes that wording into a separate concurrent-registration note. It does not turn concurrent registration into prior completion. PHYS 1163’s explicitly published zero-hour value is preserved; PHYS 1151 has three lecture hours, distinct from its lab and seminar. PHIL and DS offerings with similar names remain separate catalog observations; no cross-list equivalence is inferred.

Cumulative additions across these four checkpoints are **517 descriptions, 206 prerequisite statements and 299 fixed-credit values**. Course graphs and all 23 partial audit statuses remain intact. Learning-outcome assessment, program inception dates and home-college rules are not inferred from course descriptions.

Writing/physics/philosophy validation completed 2026-10-11 UTC: **119 Northeastern-focused tests passed**. The broader discovery run passed 213 tests and encountered one unrelated concurrent Michigan adapter/source-registration mismatch; no Michigan files were edited. All 23 temporary records ingested/repeated/exported/built with integrity intact. All 37 new source registrations succeeded twice, with zero repeat candidates or source changes.

## Remaining facts in accessible disciplines — 2026-10-11

The six already accessible BIOL/CHEM/ECON/PSYC/PHYS/PHIL catalogs also support factual extraction for every remaining course of those subjects already listed in a variant. Sixteen variants gain **173 additional course observations** with independently sourced identity, credits and explicit registration conditions. No unreviewed description is invented. The updated observations include 49 BIOL, 45 PSYC, 24 CHEM, 15 ECON, 25 PHIL and 15 PHYS program-course records.

Twenty-four subject registrations are added or expanded, six with new program-local sources; each URL is still fetched only once per program. Across their full selections, prerequisite availability grows **36→163** and fixed-credit availability **87→243**: **127 additional prerequisite statements and 156 fixed-credit fields**. Existing 70 descriptions in those selections remain unchanged; unreviewed descriptions remain null.

PSYC 4600’s research-area preparation and PHIL 2330/3492’s prior-course requirements are observed from required prose. PHIL 3822 explicitly permits departmental permission as an alternative to prior philosophy courses; ECON 5650 requires previous macroeconomic theory coursework. The parser preserves those conditions without converting them into a fabricated list of eligible courses. Required writing within a course is not mislabelled as admission eligibility. Variable-credit and concurrent-enrollment handling remain unchanged.

Cumulative additions through this fifth checkpoint: **517 descriptions, 333 prerequisite statements and 455 fixed-credit values**. This closes factual extraction for the six subjects’ existing listed courses, not their unreviewed descriptions or the programs’ home-college scope gap. Other subject catalogs and public course resources remain in the accessible research queue.

Fifth-checkpoint validation: **122 Northeastern-focused tests passed**. All 23 variants ingested and repeated idempotently in a temporary database. All 24 expanded subject registrations succeeded twice through the safe Fetcher/cache, with zero repeat candidates or source changes. Export/build and SQLite integrity passed.

## Engineering, environment, health and social sciences — 2026-10-11

The next pass safely fetched the official 2026–2027 [Electrical and Computer Engineering](https://catalog.northeastern.edu/course-descriptions/eece/), [Earth and Environmental Sciences](https://catalog.northeastern.edu/course-descriptions/envr/), [Public Health](https://catalog.northeastern.edu/course-descriptions/phth/), [Ecology, Evolution, and Marine Biology](https://catalog.northeastern.edu/course-descriptions/eemb/), [Provost interdisciplinary seminar](https://catalog.northeastern.edu/course-descriptions/inpr/) and [Science interdisciplinary seminar](https://catalog.northeastern.edu/course-descriptions/insc/) catalogs. All six returned HTTP 200 at 00:07:02–10 UTC. It also completed the existing listed-code observations in the already accessed [Sociology](https://catalog.northeastern.edu/course-descriptions/socl/), [Journalism](https://catalog.northeastern.edu/course-descriptions/jrnl/), [Communication](https://catalog.northeastern.edu/course-descriptions/comm/), [Criminal Justice](https://catalog.northeastern.edu/course-descriptions/crim/) and [International Affairs](https://catalog.northeastern.edu/course-descriptions/intl/) catalogs.

Across all 23 variants, 377 selected program-course observations include **271 newly observed records**, with **101 new descriptions, 117 new prerequisite statements and 253 new fixed-credit values**. Ninety-six subject registrations replace or extend narrower observations, adding 91 program-local evidence records while retaining one fetch per subject URL per program. Descriptions are short guarded summaries only for the 12 separately read foundation courses; other newly observed descriptions stay unknown. Cumulative additions through this checkpoint: **618 descriptions, 450 prerequisite statements and 708 fixed-credit fields**.

ENVR 3300 permits students who lack the published prerequisites to seek instructor permission; the observation does not guarantee that permission. PHTH 5222 requires permission outside designated programs, but the course description does not enumerate those programs; the condition remains explicit and unresolved. JRNL 5360 requires international students to consult the International Student and Scholar Institute before registration. These are scoped notes, separate from labelled prerequisites. Required course assignments, presentations, readings and research are not turned into admission conditions. PHTH 2350/4540’s expressly recommended preparation remains advice.

INSC 1000 describes its College of Science audience, and INPR 1000 describes an interdisciplinary first-year seminar. Neither description assigns a combined major’s home college or changes the conditional choices already represented in its requirements. All 23 historical requirement graphs and partial audits remain unchanged. A course’s stated learning opportunities are not promoted into program-level assessed outcomes.

Validation: **126 Northeastern-focused tests passed**. All 23 variants passed temporary ingest/repeat/export/build/integrity checks. All 96 registered observations succeeded twice through the safe Fetcher/cache; the repeats created zero candidates and reported zero source changes. The next accessible queue includes business, design and remaining humanities/social-science catalogs plus independently public course resources.
