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

## 2026-10-11 shared requirement pools and eligibility

[Senate Regulation 600](https://senate.ucsd.edu/Operating-Procedures/Senate-Manual/Regulations/600) resolves climate applicability: first-year/lower-division entrants from Fall 2024, transfers exempt, one approved quarter course at C−/P. No DEI four-unit minimum is transferred to climate. The Undergraduate Education climate page prohibits AP/IB credit (including AP-derived ESYS 10) and allows overlap with GE/DEI/major/minor requirements. Senate 600B4, enacted June 2025, caps designated distance-education work below 50% of UCSD-earned units unless the major has an approved distance exception; none is assumed for AI. Additional residence exceptions are represented without erasing Roosevelt's discrepancy.

The complete current-linked approved PDFs were inspected, not just term offering tables: **229 DEI rows across 16 pages** and **58 climate rows across four pages**. All table rows preserve effective terms, prerequisites/enrollment restrictions, historical expirations and future approvals. AAS 190 approval ends Spring 2023; CGS 138/LTCS 138 begins Fall 2027. These are not unconditional current choices. DEI mainly says Updated June 2026 but page 14 retains a December 2024 footer; climate says November 2025. MGT 18GS's prerequisite continuation at the top of page 12 was joined to its page-11 row. Blank prerequisites stay null and no course units are inferred from the requirement minimum.

Composite slash/cross-list/service-learning/legacy rows are retained literally as option notes rather than expanded into guessed independent courses. The climate PDF prints USP/ANTH 128A with 128 and repeats 128B; this source ambiguity remains explicit. Simple single-code rows receive course records. `parse_approval_rows` reads reviewed PDF table cells; PDF URLs have no automatic HTML parser or fabricated refresh date. Raw PDFs, tables and contact sheets remain temporary/ignored, not committed. Each source lists its actual review locator/date.

AHI now includes its 50 explicitly enumerated course codes plus the source-stated open predicate “HIUS except colloquia”; no exhaustive changing HIUS inventory is required. Current UC ELWR alternatives include ACT English+Reading 63 from the same sitting and explicitly exclude digital SAT. Pre-enrollment composition requires C or better and three semester/four quarter units. Campus AWP placement rules remain separate.

Next research queue: the eight colleges' approved GE pools and transfer/overlap rules (current public hubs and Revelle component pages already fetched); then UCSB progression/transfer and independently linked science/capstone/GE sources. The obsolete catalog-linked Muir `degree_reqs.html` returned 404; its current academic directory is accessible. No private account, denied source bypass, or student action was used.

## 2026-10-11 Revelle component pools

Six current public component pages add 133 conditional requirement nodes and 103 new course observations (551 total observations / 485 nodes). Humanities includes actual names/units and D-or-better grading, ELWR/sequence prerequisites, HUM 100 for all Fall-2024-onward transfers, and IGETC/non-IGETC distinctions. Mathematics retains row alternatives, the one-statistics limit and former MATH 20F alias without turning the alias into an extra option. The six science tables preserve preparation subheadings and literal cross-list, extension and concurrent lecture/lab rows; no inferred credit split. The social-science page supplies 58 finite course codes and separate open department/range predicates. Fine arts uses the published open department predicates. The 15 language endpoint rows distinguish first-year and transfer endpoints from beginner placement; slash combinations remain literal.

A current source change is explicit: the science page gives **three courses for transfers from Fall 2026**, whereas the catalog gives **four from Fall 2024**. The component page does not specify Fall 2024/2025 transfers. The existing catalog rule is preserved with cohort qualification; no unsupported reconciliation. Revelle's upper-division-major/GE overlap restriction applies to social science and fine arts. General science lab waiver does not override a course's concurrency rule or an AI departmental rule.

Next: linked Revelle humanities transfer policy/AP-IB qualifications; Muir theme pools; Warren area-study/formal-skills scope; Roosevelt approved regional/writing lists; Sixth breadth PDF/ELR; Seventh alternatives and transfer routes; Eighth first-year/transfer lists. Then UCSB public progression/transfer rules and independent science/capstone/GE sources. All eight college pathways remain alternatives based on actual college affiliation, not additive requirements. Parsers read observed table/list cells and never emit a completeness audit.
