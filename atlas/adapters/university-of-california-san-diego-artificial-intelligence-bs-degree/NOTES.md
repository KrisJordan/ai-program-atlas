# UCSD AI curriculum

Reviewed 2026-10-10 with robots-aware fetcher. Extractor isolates the actual BS AI catalog section, excluding adjacent computer science and bioinformatics degrees, and re-extracts nested alternatives and course-code ranges. Returns partial observations without audit/timestamps.

Catalog major inventory only; college/university requirements and full approved CSE tag mapping remain unreviewed. Department page is explicitly tentative and its 2026 elective list differs from this catalog; no silent union of editions. Course titles/credits not supplied in this catalog section remain unknown.

The department page is dated August 3, 2026 and explicitly tentative; it also limits 2026–27 admission to direct admits. Its elective pool differs from the catalog, so it was not silently merged. Official September 25, 2025 news establishes Fall 2025 launch.

https://catalog.ucsd.edu/curric/CSE-ug.html
https://cse.ucsd.edu/undergraduate/bs-artificial-intelligence-cse-bs-004
https://today.ucsd.edu/story/uc-san-diegos-new-ai-major-is-here

Six bounded core-course metadata entries were fetched from https://catalog.ucsd.edu/courses/CSE.html. A separate source parser extracts current titles, credits and prerequisites; curated short descriptions are paraphrases. Prerequisite logic is not re-parenthesized.

## 2026-10-11 breadth and degree-policy follow-up

Current official CSE course headings supply 61 tagged courses; their actual names/units and each Systems/Theory/Applications tag are mapped without converting multi-tag membership into permission to double-count. Dynamic CSE 190 topics still need offering-level review. Core metadata remains separate. Parser rejects unknown tag labels or an absent category.

The general degree-requirements page supplies 180 total/60 upper-division minimums, senior residence, DEI/AHI routes, writing placement/deadlines, completion-time limits, applications and double-major rules. Eight official college catalog pages were fetched and their GE/transfer structures summarized as **conditional pathways**, not eight additive requirements. Finite approved college lists and full transfer exceptions remain gaps. Warren states an engineering area-study exception; AI-specific applicability still needs confirmation. No sample plan is promoted to requirements.

New discrepancies are retained: Roosevelt prints residence **36 of final 44**, versus university **35 of final 45**. Revelle and Eighth explicitly name climate-change education (Eighth: Fall 2024 admits onward), which the inspected university degree page does not cover. The institution-wide climate rule and approved pool need separate review. The university AHI/DEI pools and UC-wide pre-entry writing alternatives remain incomplete.

The August 3, 2026 department page remains explicitly tentative and supplies direct-admit-only 2026–27 admission, C− grading, one-requirement-per-course and graduate instructor/department TEA approval rules. Its AI list omits catalog entries **CSE 151B, 154, 157, 176B, 186, DSC 131, DSC 185**; none were removed without an applicability decision. CSE 151B is also shown in the new sample as core, but that sample is not used to silently recast the catalog tree. Department exclusions name 180/180R, whereas catalog additionally excludes 191. No union of differing editions was formed.

`ucsd_degree_policies.py` produces bounded observations, not reviewer audits. Each college parser checks its own title and operative clauses. On later source changes these guards force review rather than falsely refreshing a complete inventory. Degree remains partial.
