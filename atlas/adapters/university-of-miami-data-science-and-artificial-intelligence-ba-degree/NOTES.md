# B.A. Data Science and Artificial Intelligence

Reviewed 2026-10-10. Full program curriculum table mapped with course alternatives, choice pools, uncoded degree requirements and all local table footnotes. The program remains partial because linked university and college degree-wide policies have not been exhaustively audited. Course amounts remain in original published units (normalization unknown); ranges are retained in notes. A sample plan is not an authoritative substitute for requirements, and additional-major rules stay separate.

Degree curriculum is taken from the Curriculum tab, not the sample semester plan or the Additional Major tab. Sample-plan totals and courses may differ from the requirements table.

Published ranges remain in notes; they are not converted into invented scalar course credits. Credit unit normalization is unresolved.

The elective pools are represented as choices by published credit amount, not as all required courses. EPS 351 / PSY 292 is retained as an alternative where the BA table presents it.

A non-STEM minor/second major applies to the BA only; BS quantitative coursework and degree total are separately sourced.

The source-specific adapter observes the Curriculum table and validates the full award/title heading. It never emits a review date or audit. Observed alternative rows become one-course choices; unrecognized or missing headings fail. Curated policy notes and editorial course themes remain independent of scraping.

## 2026-10-11 university and college policy review

Reviewed public CourseLeaf policy pages with the robots-aware fetcher (all HTTP 200): Course Information, undergraduate Transfer Credit, Grades, Graduation, General Education, Advanced Writing, the undergraduate policy landing page and the applicable college. Degree records include the corresponding degree-wide rules; the minor includes only its credential relationship and applicable coursework policies. The source explicitly defines semester credit units, so existing numeric amounts are normalized without conversion. No missing credit amount is filled from a group total.

The transfer page is internally inconsistent: its eligibility paragraph excepts summer from the concurrent-enrollment prohibition, but its excluded-course paragraph explicitly prohibits separate UM/outside summer sessions. The record stays partial, with both statements preserved and no permission inferred. Business residency remains stricter; its optional general overlap exception does not replace the AI program’s local restriction. Applicable source dates/editions remain unknown. Degree option inventories (cognate attributes and any selected additional credential) remain incomplete. Arts and Sciences also has a non-exhaustive excluded-elective list and unreviewed heritage-language placements; the BS’s 9-versus-3 language-credit and proposed-status issues remain visible.

Policy reruns validate source identity and required headings, then hash actual content sections for a reviewer. They emit no audit, review timestamp or complete claim, and never replay these manually interpreted policies. Course metadata and student-specific DPR/term availability are separate gaps.

## 2026-10-11 cognate and language supplement

Added source-specific guarded observations for student-selected cognates and their declaration, plus the individualized-cognate prohibition on reuse toward other degree requirements. The public Tableau course list is accessible and visibly dated October 2, 2026; its export menu offered image/vector/PDF/PowerPoint, not a data export. The complete approved pool is not captured, and this is not an authentication barrier. Thematic choices also load publicly; their individual plans remain inventory work. A chosen extra major/minor is an open route, not a demand to enumerate every optional credential. See research/miami-supplemental-review.md.

Spanish heritage placement now identifies SPA 107/207/208/307, first-day diagnostic placement, native-speaker exclusions and outside-language equivalency. These four courses are conditional placement/preparation, not all required. Other languages’ heritage-specific placement is still unverified. The BS language-credit discrepancy remains.

No complete promotion or inferred source date. Existing summer-transfer conflict and other audit gaps remain. New HTML parsers validate source identity and pin observed text; changed policies require renewed review.

## 2026-10-11 bounded cognate pool capture

The public Tableau PDF export works through ordinary Download/PDF/Specific sheets/Select All controls. This pass maps Master List pages1–2 only:77 identities/101 area memberships in a structured research sample;75 AH/PS candidate courses apply to these degrees. The remaining48 Master List pages and the other sheets are accessible unreviewed work. No full-pool claim or credit default is made. Three truncated titles remain null.

Two optional thematic routes are fully observed for Fall2026: PS_0031 (17 active options, two inactive flags preserved separately; at least1+at least2) and AT_0027 (27 options; exactly1+exactly2). Each requires at least3courses/9credits only if selected. Their source rules and the individualized no-other-degree-requirement rule stay separate. All four AI degrees already supply STEM through the major. Existing summer-transfer and degree-specific language/status conflicts survive; status remains partial. See [the capture review](../../../research/miami-cognate-pool-review.md) and [fact sample](../../../research/miami-individualized-cognate-pool.json) for provenance, counts, next work and rerun instructions.

New helper: `miami_cognate_pools.py`; the thematic URLs are registered for ordinary refresh, while the PDF parser requires a new public UI export. No source parser emits an audit, verification date or completeness. 58 focused Miami tests passed; isolated four-program ingest/check/build passed.

## Full Master List continuation — 2026-10-11

All50 rendered Master pages are captured:2,075 course identities/2,463 area memberships. The degree now includes1,680 unique AH/PS candidate identities (deduplicated against existing courses), with current CaneLink attribute and strict individualized non-overlap conditions retained. The full research manifest preserves every page/row locator;121 truncated titles globally remain unknown (104 AH/PS). Previously verified metadata survives. The former bounded sample is superseded; plain PDF text included clipped boundary context, so APY435’s correct visible locator is page3,row1. All prior identities remain valid.

New parser `miami_cognate_export.py` handles rendered columns, wrapped titles, alphabetic numbers, transfer-equivalency codes, identity/area deduplication and complete page/row accounting. No credit amounts or prerequisites are invented. Thematic inventory still has210 unreviewed plans after the initial2; the215-entry active directory also includes3 individualized routes. The program remains partial with existing conflicts unchanged. Full source replay and focused tests are documented in the research review.

## Complete dated thematic inventory — 2026-10-11

Supersedes the two-plan limit above: all 215 active public directory links are fetched and reviewed for the selected Fall 2026 semester, comprising212 thematic plans and3 individualized routes. Exact accounting:440 groups/2,699 displayed rows, including98 inactive rows. Zero entries remain unreviewed in this dated active listing. Other semesters/deactivated plans are outside scope. All 173 AH/PS thematic plans are represented for Arts and Sciences; the two business degrees receive 172 and an explicit PS_0051 BUS-credit exclusion. STEM's 39 plans are captured in the shared research inventory without creating an additional requirement.

New `miami_thematic_directory.py` extracts actual rows, groups, exact/minimum/cap/credit-based rules, registration conditions, conditional placement/major branches and inactive flags. Reviewed description and conditional-rule digests prevent silent replay of stale manual interpretations. No audit or verification timestamp is emitted. Existing independently verified course metadata is unchanged; directory-only facts receive attributable thematic metadata, with 43truncated/unknown names still null.

Four plans leave overall logic blank (AT_0077, AT_0094, PS_0079, PS_0082); PS_0017 has conflicting group/description wording; AT_0102 uses a separate ensemble alternative. All are explicit, and all four degrees remain partial. Beyond-USA approved coursework is an open route, not an uncaptured finite pool. Individualized no-other-degree-requirement restrictions and current attribute conditions remain separate from thematic rules. Existing summer-transfer, college exclusions/other-language placement and BS language/status issues are preserved.

See [full review](../../../research/miami-cognate-pool-review.md) and [plan/group/row facts](../../../research/miami-thematic-cognate-pools.json). Raw HTML remains ignored. Isolated four-program ingest/check/build passed; focused source-change, completeness-accounting and preservation tests are documented in the review. No maintained DB edit.

Validation: 83 focused Miami tests passed, including every actual HTML plan replay and full public PDF replay; isolated four-program ingest/check/build passed. Five optional PyMuPDF deprecation warnings only.

### Degree correctness review — 2026-10-11

Numeric elective pools are published credit choices, not contextual notes. The named one-of component inside the four-W writing overlay is required, while overlap with major courses remains permitted. Main-table mapped roles are 7 fixed / 39 named options. The much larger university cognate inventory remains contextual, not a degree workload. No subject labels were inferred from elective or cognate membership.

This is a bounded requirement-role correction. Whole-degree correctness remains
in progress; existing partial curriculum status and substantive source questions
are preserved. Synthetic tests distinguish explicit choices from context, and
current cached catalog replay agrees with the reviewed seed roles.

## Fixed-course description audit — 2026-10-11

Read 7 additional fixed-course descriptions and their published eligibility clauses; manual content classifications and exact credit amounts are preserved. The exact reviewed codes are CSC 113, CSC 120, CSC 220, DSC 344, DSC 345, MTH 161, WRS 105. Course eligibility remains distinct from degree obligation; extra prerequisite identities are not inserted as fixed requirements. Each complete source block is guarded on replay, and observations contain no independent audit or classification-review certificate. Remaining options, cognate metadata and previously documented policy questions remain in progress.

CSC 113 is mixed introductory data analysis and R programming; the current course block is titled Data Science for the World, while the degree table uses an older/qualified title. CSC 345 and CSC 545 remain different codes despite identical current course titles. CSC 345 and DSC 344/345 publish unlabeled eligibility expressions; those expressions are preserved as unlabeled, without inventing catalog labels or waiver rules.

WRS 105 excludes credit-only grading and says “Not for major or minor” without naming a credential. That limitation is recorded literally, not interpreted as removing the course from these explicit degree tables. No first-offered date is inferred from routine offering-season text.

## Named primary-table options — 2026-10-11

Read all 39 remaining named option blocks applicable to this degree. Source rows are now retained on requirement evidence, so course-catalog title normalization cannot erase project approval, course-order, overlap or exclusion conditions. Observed credit ranges remain null scalar amounts, with the range recorded. Credit exclusions do not establish cross-listed identities. All named primary-table fixed and option course descriptions are now reviewed; this does not cover the much larger contextual cognate inventory or settle the open degree-wide policy questions.

Course 405 is explicitly one credit; CSC 410–412 are variable 1–3 credits and keep degree-specific DS/AI project approval. CSC 506 combines logic and automated reasoning, CSC 548/549 combine computational methods and life-science applications, and CSC 550 teaches neuroscience through modeling. Current CSC 545 course-title wording differs from the BA degree table; the code and both source contexts are preserved without assuming a rename date. APY 313 has insufficiently specified methods for a single primary subject; the broad PSY 110 survey is mixed, not automatically AI.

## 2026-10-11 contextual content review continuation

Actual complete source blocks now supply further cognate-course metadata and manual content reviews. The four-degree batch adds 131 observations from 42 reread blocks, preserving original contextual roles, explicit nonbusiness/credit exclusions and source-version boundaries. A reviewed CSC 506 in the BA contextual inventory does not become a BA primary-table option. See research/miami-context-course-review.md and the exact running queue research/miami-description-review-remaining.json. Accessible remaining descriptions and whole-degree policies stay in progress.
