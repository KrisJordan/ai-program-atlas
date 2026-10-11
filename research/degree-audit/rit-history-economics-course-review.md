# RIT economics and history course cards

Reviewed 2026-10-11. This contribution reads exactly **64 assigned identifiers: 23 ECON and 41 HIST** from the 2026–2027 [Economics Immersion](https://www.rit.edu/study/economics-immersion) and [History Immersion](https://www.rit.edu/study/history-immersion) pages. All complete public popups were opened using visible exact-code links. The previously reviewed language-route history courses were excluded from this allocation. No access barrier remained in this batch, no prerequisite chain was expanded, and no course identity was inferred from matching text.

Each card independently printed **three credits**. The economics prerequisite ECON-101 remains separate from its choose-three option pool. Source-defined roles come from the earlier local-rule review, not the category judgment or credit amount. Semester-hour normalization cites the separately reviewed [D01.4](https://www.rit.edu/policies/d014) policy; the runtime observer leaves the unit unknown when only Credits is printed.

All 22 economics courses after ECON-101 publish prerequisite statements. ECON-101 and all 41 history cards have no separate prerequisite field; their null values do not establish unrestricted enrollment. The numerous economics alternatives involving a completed 400- or 500-level ECON course are retained literally. ECON-401/402/404/405 have incomplete Boolean punctuation in the source; the observer does not impose precedence or infer a student’s eligibility. ECON-403 retains the printed historical `1016-171T` code without merging it with a contemporary identity. Ordinary placement, permission or completion conditions are not access blockers.

## Manual content review

Every record has an original summary and individual rationale. Counts are **43 human-context, 17 applications, three mathematics and one mixed**. These describe course content, not required status, degree proportions or quality.

- ECON-403 explicitly teaches regression estimation and interpretation, ECON-404 matrix algebra/calculus/optimization, and ECON-410 mathematical game models and equilibrium reasoning. They are mathematics based on their descriptions, not their department or prerequisites.
- Micro/macro theory, resource allocation, managerial and financial economics, labor markets, health care, development and experimental economic behavior are substantive economic domain knowledge or practice. Their quantitative tools do not automatically make them mathematics.
- ECON-411 creates computational models in Julia, Python or R to investigate economic phenomena. The primary domain purpose is economic modeling; the card does not establish a general programming/software-construction curriculum or AI methods. It is applications.
- ECON-406 centers global social problems and development; ECON-445 studies intellectual history. Both are human-context.
- ECON-408 combines economic modeling and practice with legal institutions, intellectual-property policy and rights interpretation. Both strands are substantive; it remains mixed with applications/human-context candidates.
- All 41 HIST cards have an explicit historical-analysis or historical-communication purpose. HIST-180/282/330/480 analyze technology’s social, ethical and historical implications. They are not classified as technical computing courses from their titles.
- HIST-324 conducts oral-history interviews and produces a podcast. HIST-421 conducts original historical research. These are historical research and communication under the established human-context taxonomy, not automatically generic applications because they involve projects.
- HIST-326 names digitization, preservation, text mining, mapping, programming and digital storytelling within the stated purpose of producing and communicating history. The card does not establish a general CS curriculum; its historical methods purpose supports human-context. No AI coverage is inferred from text mining.
- HIST-102/103/104/302 have instructor-selected themes or cities within an explicit historical scope. HIST-302 prohibits repeating the same topic. HIST-421 announces a shared theme and welcomes all majors. These limits remain notes rather than invented fixed topics.
- HIST-345’s prose dates one earthquake example to 2008. The original summary describes the course’s historical disaster analysis and does not adopt that example as a verified event date.

## Deliverables and checks

`atlas/adapters/rit_history_economics_course_reviews.py/.json` separates the manual manifest from a rerunnable observer. The observer requires a registered route, exact current heading/year, table membership and settled full card. Changed title, description, prerequisite and amount are actual observations; it never emits manual review metadata. Credit ranges stay null scalars with printed evidence; zero remains zero. Missing fields, loading placeholders, wrong sources and duplicate cards reject incomplete observations.

**12 focused tests passed**, including exact allocation and source evidence, quantitative/domain/history distinctions, mixed semantics, prerequisite alternatives, changed fields, missing conditions, zero/range credits and source/version guards. Synthetic fixtures verify behavior; the actual full descriptions were read through ordinary Chrome and are not bulk-reproduced in the public repository. Primary route integration, queue updates, full-seed integrity and static build belong to the RIT owner. No whole-degree or independent second-pass certification is claimed.
