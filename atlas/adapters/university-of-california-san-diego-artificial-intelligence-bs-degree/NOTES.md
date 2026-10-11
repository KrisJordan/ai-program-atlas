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

## 2026-10-11 Muir current theme inventory

The current academic directory replaces the obsolete catalog link. Its complete approved theme page has **33 theme/language lists**, mapped into 674 nodes including writing variants; two current policy nodes cover overlap and transfer branches. Every printed comma-delimited option is preserved. Only unambiguous single-code options receive new course records. AND/OR pairs, MUS 18's four-unit condition, malformed `COGS-0-2`, unhyphenated TDGE codes, and unusual language entries remain literal qualified choices; none were silently repaired. Duplicate JAPN 150C is retained in its source option list but does not imply additional credit. Optional petition exceptions remain open approval routes, not absent finite inventories.

Current Muir policy permits at most three major courses in GE, requires the writing sequence in order at letter grade D or better, and distinguishes first-pass priorities. IGETC/CalGETC transfers take MCWP 125/125R; partial IGETC adds its outstanding one or two areas; reciprocal GE completion leaves the two-course writing route subject to petition. The catalog's MCWP 50 request option is not stated on the current page, so eligibility is not assumed. Language proficiency/placement alone cannot replace three credited courses.

Next: Warren's current Area Studies page explicitly lists Artificial Intelligence, resolving the earlier engineering applicability gap; map its approved subjects/specialized pools and public embedded formal-skills list. Revelle transfer exceptions and the other five college pools remain queued, followed by UCSB public progression/transfer policies. No new source denial was bypassed.

## 2026-10-11 Warren AI pathway and published tables

Current Area Studies explicitly names **Artificial Intelligence** within CSE's engineering list, closing the prior applicability gap. Its subject choices, three-course/two-upper/one-resident distribution, noncontiguous disciplines, P/NP, language restrictions, MGT exclusions, incompatible broad-area pair and optional minor approvals are mapped. Department predicates for Humanities, HDS and Perspectives of Social Science remain open eligible-subject rules, rather than an invented exhaustive catalog inventory. The certified-transfer route adds one four-unit upper-division noncontiguous course and its study-abroad/other-UC, minor, special-studies and overlap exceptions.

Five official embedded Google tables are readable publicly: **36 formal-skills rows, 28 anti-racism humanities, 79 anti-racism social science, 52 environmental studies, and 61 law-and-society rows**. Law preserves its one-introductory-plus-two-further split. Initial HTTP pages were render shells; ordinary Chrome rendering exposed the public table iframe URLs. Those exact URLs were independently fetched with robots checks and are registered sources with actual HTML parsers. No hidden API, sign-in or access restriction was bypassed. Empty course titles remain null; checkbox graphics are not interpreted as independent Senate DEI/climate approval.

Source issues remain visible: the formal table prints POLI 005 / ECON 005D (other GE sources reverse these suffixes); law labels PSYC 162 Environmental Policy and prints ETHN 153*** without a matching explanation. Annotated/cross-listed rows remain literal. Warren's linked interdisciplinary subject-program approved lists remain separate next checks, while European Studies explicitly uses counselor approval and optional minors need not all be inventoried. UCSD now has 1,094 course observations / 1,480 nodes and remains partial.

Next queue: Revelle transfer/AP-IB exceptions; Warren interdisciplinary linked pools; Marshall, Roosevelt, Sixth, Seventh and Eighth current finite pools and transfer details; then UCSB public progression/transfer and independent science/capstone/GE evidence. Existing catalog/department elective and Roosevelt residence conflicts are not silently reconciled.

## 2026-10-11 Marshall current pools and AI-specific breadth

Marshall's eight component pools are fully read, with 138 unambiguous course observations, DOC names/units, science distributions and the three math/statistics/logic combinations. Math subpools are conditional pools, not three additive one-course requirements. Literal PHYS lecture/lab combinations and MUS 4–19 range remain qualified options; MUS 80 requires four units. The current transfer page gives all certification/partial/reciprocity/no-agreement branches and a new **Fall 2026-onward DOC 170 writing-breadth requirement**, first available Winter 2027.

The July 28, 2026 one-page writing PDF is fully mapped into 21 department option expressions plus its policy. Explicit ranges and open upper-division predicates remain rules rather than invented course records. Paired EDS/service-learning entries and malformed HILA/HITO/SOCI separators or ETHN 119–121R notation remain visible. Summer 2026 uses a different advising-supplied list. The newer DOC 170 transfer requirement is not replaced by the broad list.

The public breadth selector was inspected with **CS29 – Artificial Intelligence** selected. It explicitly classifies AI as Engineering or Science and shows 42 subjects across Humanities/Fine Arts, Social Sciences, Interdepartmental/Interdisciplinary and Foreign Languages. Its normal browser UI worked after the raw fetcher's robots-file connection failed; there was no denial or authentication. The foreign-language tooltip points to the separate TritonLink language-course list. `parse_breadth_observation` requires the selected AI identity and observed groups; it cannot mistake the initial unselected shell for a fresh curriculum verification.

Next queue remains explicit: Marshall public-service and foreign-language eligibility; Revelle transfer/AP-IB exceptions; Warren interdisciplinary program pools; Roosevelt, Sixth, Seventh and Eighth component inventories. Sixth's full two-page 2026–27 PDF is downloaded and visually reviewed; Marshall's source-specific breadth selector is now resolved. Then continue UCSB public progression/transfer and independent science/capstone/GE evidence. UCSD remains partial, now 1,108 course observations / 1,668 requirement nodes.

## 2026-10-11 Sixth complete public GE and experiential pools

The August 12, 2026 two-page GE sheet supplies all seven breadth categories and department/course-number expressions, including approved AP routes, two-department social analysis, open language/literature predicates and eight-unit Art Making (not an inferred fixed two-course requirement). Numeric ranges and complex suffix/lecture-lab combinations stay literal; unambiguous individual codes are recorded without invented names/units. Both PDF pages were visually reviewed.

The full public experiential spreadsheet supplies **97 rows**, including all-department 195/197/198/199 and Global Seminar predicates, paired courses, all enrollment restrictions and offering terms. Ordinary browser rendering exposed its public iframe URL; robots-aware fetching then returned the full HTML table. The current policy approves four-unit 198/199 from Fall 2026; their Summer 2026 offering cells do not move that approval date backward. PH 196BH's self-prerequisite is retained as a source issue. Major/GPA restrictions are not waived for AI students; the table itself directs enrollment-rule confirmation in the catalog.

The five current track pages, course proposal, CAT 90 and CAT 125 pages resolve important exceptions. CAT 90 is explicitly **one unit, P/NP, fall only**, accepted after 80 hours across five weeks of approved summer experience ending July 1–October 1, with no other academic credit and supervisor confirmation by week one. It qualifies at either class standing. CAT 125GS may satisfy writing, but one class cannot count toward two Sixth GE areas. Nonautomatic study abroad needs four in-person weeks, faculty supervision, four transferable upper-division units and passing/transcript evidence; its proposal is due week eight after return, while off-list local courses require a syllabus and proposal by week eight before enrollment. Necessary experiential criteria do not guarantee approval. Full/partial/reciprocity/uncertified transfer routes remain conditional.

UCSD is still partial, now **1,201 course observations / 1,858 nodes**. Next: Roosevelt, Seventh and Eighth current pools; Marshall public-service/foreign-language follow-up (the latter redirects to 404), Revelle transfer/AP-IB exceptions, Warren linked interdisciplinary pools; then UCSB public progression/transfer and independent science/capstone/GE sources. The separately unresolved major-elective, residence and malformed-source conflicts remain visible.

## 2026-10-11 Roosevelt current component and regional pools

The current college page's component tables, overlap restrictions, language endpoints/alternative qualifications, writing petitions and all transfer-certification branches are mapped. All **six current regional pools** were read in full, dated August 2026, preserving course markers, enrollment/credit notes, same-region rules and lower/upper-division limits. The pre-Fall-2021 combined Americas page was inspected but not imported as a current choice; Fall-2021-onward students instead use distinct North America and Latin America pools. North America's explicit open DEI-approved predicate remains in addition to its listed courses. Blank leading cells in its Education Studies table are handled without dropping rows.

The full current-linked writing page has **215 option rows**, but explicitly says **December 3, 2020**; its age remains visible. Current off-list petition criteria provide a separate approval route (2,500-word paper, or 3,000-word portfolio including one 1,500-word paper; English/C−/original argument and exclusions). MMW 121/122 entries are transfer-only and letter graded. One course may satisfy writing and another requirement, but ordinary GE-to-GE, regional/fine-art, regional/language and upper-major overlap prohibitions remain.

Current public graduation and GE pages agree with Senate residence **35/45**, while the catalog says **36/44**. Public transfer branches now generally require **one MMW 122**, or MMW 12 when prior writing is incomplete; its own generic table says MMW 121 or 122, and the catalog sequence differs. These source inconsistencies remain explicit, not resolved by guesswork. CalGETC missing optional LOTE certification has an additional course/proficiency route. Minimum progress, DDA window and MMW 15 climate fulfillment are represented.

UCSD remains partial, now **1,972 course observations / 3,301 requirement nodes**. Next: Seventh/Eighth current pools, remaining college AP/IB and linked approval details, then UCSB public progression/transfer and independent science/capstone/GE sources. No source-denial retry or catalog-shell bypass was used.

### Eighth College published breadth and current transfer branches — 2026-10-11

Read the current first-year/transfer pages and the complete 646-row breadth sheet linked by the first-year page. The normal browser rendered the public wrapper; its observed iframe URL was fetched with robots checks and cached. All five area pools are mapped (660 requirement nodes including policy), preserving suffixes, open language ranges, paired conversation/analysis and physics lecture/lab expressions. University-overlap annotations remain annotations, subject to separate current approval/date rules. Credits and prerequisites are not inferred from list membership.

Current policies distinguish the CCE1/2/3/120 first-year sequence from CCE110/120 transfers (four units each, CCE110 starts Fall2026). IGETC/CalGETC/reciprocity waive lower-division breadth; other transfers need individual review, two additional writing courses and remaining breadth. Prior California community-college credit can use approved area articulation; post-enrollment credit requires approved UCSD equivalence or a petition. Open off-list petitions are represented as approval routes, not an infinite missing list. Current 35/45 residence agrees with Senate; Eighth's end-of-final-quarter international AHI waiver wording remains distinguished from university petition wording.

Next: Seventh's published alternatives/high-impact inventory and transfer branches; applicable AP/IB charts and remaining explicitly linked finite transfer pools; then UCSB progression/transfer and independently accessible science/capstone/GE sources. Degree remains partial with the existing major elective, residence-edition and other source conflicts.

### Seventh College alternatives and experiential routes — 2026-10-11

Mapped all 432 entries across five Alternatives pools and all 149 named High-Impact entries, plus current Synthesis/transfer policies (595 nodes). Inline HTML spans are joined without introducing fake code spaces; actual printed bundles, including unusual language notation, remain literal. EDS139 corequisite sequences and explicit no-prerequisite annotations remain qualified. The first-year and transfer pages each publish the High-Impact list; the seed's common pool is sourced to the first-year page, while separate transfer-policy evidence is registered.

SYN1/1R → SYN2/2R → SYN100, letter grading, college/ELWR/standing restrictions and normal/remote duplicate-credit rules are explicit. Transfer SYN100 is four units with winter preauthorization; SYN150/150R is optional preparation and cannot follow SYN100. Full/partial IGETC, reciprocity and individual review are separate branches. The current page does not independently establish CalGETC treatment. Open upper-division language, 195–199, AIP, abroad and experiential petition routes are rules, not missing finite inventories.

Next: the specific linked Warren interdisciplinary and Revelle transfer lists, Marshall public-service/language rules, AP/IB credit charts where applicable, and exact shared climate/DEI/AHI/writing exceptions. Then accessible UCSB progression/transfer and independent science/capstone/GE evidence. Existing source conflicts keep the degree partial.

### Linked Revelle transfer and Marshall service rules — 2026-10-11

Mapped all 24 external-institution humanities transfer rows (five introductory, nineteen history), including Foothill/De Anza paired-credit exceptions, CSU Dominguez Hills renumbering, repetition, entry-cohort/residence and petition rules. These remain institution-qualified requirement options, not mislabeled UCSD courses or guessed unit conversions. Current Revelle transfer GE separately establishes CalGETC language/LOTE, Fall2025 UC reciprocity, partial and individual-review branches. Its choice of two HUM3/4/5 courses conflicts with the humanities transfer page's three-quarter/two-semester formulation; retain both. Its three-science formulation also does not erase earlier cohort/catalog discrepancies.

Marshall public-service branches now preserve AIP197P and TMC120 as non-writing substitutions, the eight EDS choices with EDS139 except standalone six-unit EDS135, and the complete ENG100D+100L+project writing bundle. One breadth slot may be replaced, subject to major-overlap and double-major review. This closes the public-service cross-link; the broken foreign-language eligibility link, Warren's linked discipline lists, AP/IB charts and exact unresolved source conflicts remain explicit next checks before UCSB policy work.

### All-college 2026–27 AP/IB credit charts — 2026-10-11

Warren's current AP/IB page links official university-wide 2026 charts. Both six-page PDFs were fetched with robots checks, table cells extracted with page/column boundaries, and all twelve pages visually reviewed. Mapped26 AP subject rows and28 IB subject rows, each retaining its university credit/exemption and eight separate college treatments, plus duplicate-credit/general rules. All44 Warren HTML tables add score/subtest/language qualifications and footnotes (584 nodes total). These are conditional alternatives and exemptions, not new required courses or automatically summed college allowances. PDF observation functions take reviewed rows; no automatic PDF refresh/audit is claimed.

The AP African American Studies unit cell is blank in the university PDF, although Warren HTML states4units. Warren IBMath's main table says MATH20A plus4elective units while its subsequent note and university chart say MATH20A and10B. Preserve exact source disagreement. IB Applications and Interpretations is explicitly not credit-eligible; do not merge it with Analysis and Approaches. AP Precalculus has no units, and Seminar/Research can satisfy ELWR without units. Source-defined partial APUSHistory/IBHistory of Americas overlap is retained rather than replaced with a universal no-overlap assumption.

Warren discipline cross-link inspection: AAPI and Chicanx/Latinx pages mix quarter schedules with historical offerings; Chinese/Japanese pages are directories; Jewish Studies combines current projection with full course lists; LATI catalog has fuller approved pools. African American Studies and Middle East old hosts stopped at cross-origin robots redirects—no bypass. Next: extract the genuinely finite current lists behind those accessible directories while preserving schedules, petitions and discipline restrictions; resolve the broken Marshall language link through an official directory. UCSB policy batch is committed separately; its science/capstone/dynamic GE gaps remain specific blockers.

### Warren-linked finite discipline lists — 2026-10-11

Mapped553 qualified nodes from five explicit approved inventories: AAPI catalog, Chinese non-language catalog list, Japanese non-language department tables, Jewish full discipline list, and Latin American approved elective list. Added88 previously unobserved course records while retaining existing richer metadata. These are choices under Warren's own area/level/residence/overlap limits, not requirements to complete any optional non-AI degree. Each parser observes headings/rows and keeps compound, topic and petition conditions; Japanese descriptions are not copied, and its separate graduate-only table is excluded. Starred Japanese Literature/Music courses require more than33% Japan content and program confirmation. Jewish term projections/history are excluded; their inconsistent winter/spring2026 labels under2026–27 are not corrected.

AAPI lists compressed CHIN sequences at4units; the independently read current CHIN course catalog prints5units for first-year courses. That contextual source is registered, without replacing either source's fact or inferring Warren's treatment of a non-four-unit course. Semester-like course bundles and undergraduate/graduate cross-list strings remain literal rather than guessed expansions.

Next finite work: Chicanx/Latinx current approved offerings with petition markers, Chinese/Japanese language eligibility and metadata as needed, and Marshall's broken foreign-language link. African American/Middle East legacy hosts remain stopped at cross-origin robots redirects, and European Studies is an explicit advising route. Full optional minors/degrees and infinite advisor-approved choices are outside the necessary inventory. Main AI catalog/department elective and college source conflicts remain unresolved.

### Remaining accessible Warren language and current Chicanx lists — 2026-10-11

Current Chinese catalog now provides41 undergraduate course metadata observations, one literal CHIN160/260 cross-list and placement/track rules. Four graduate-only entries are excluded without an undergraduate approval exception. Known conflicting credits are not overwritten: first-year CHIN catalog values differ from the AAPI sequence table. Existing richer metadata is retained; course-specific prerequisites come from actual catalog text. Japanese language page supplies six A–B–C sequence headings and placement/interview rules; individual units remain unknown, and the whole sequence is not universally mandatory.

Chicanx/Latinx Fall2026/Winter2027/Spring2027 contains65 qualified term options. Historical blocks are excluded. Starred entries still require petitions; language paired enrollment and topic restrictions remain attached. The source calls its schedule tentative, so this closes inspection of the current linked schedule, not proof of a complete permanent approved pool. The optional other degree's core/capstone requirements are not added to AI.

Remaining UCSD blockers are now principally conflicting source rules and constrained sources: major elective edition/CSE191 eligibility; Revelle transfer humanities/science cohorts; ERC transfer/residence editions and old writing-list date; Warren ambiguous law/formal table codes plus IBMath interpretation; malformed climate/Marshall row notation; Sixth eligibility/term conflicts; African American/Middle East legacy robots redirects; broken Marshall foreign-language link. Open petitions/department predicates are explicitly represented rather than treated as endless missing inventories. Next bounded check is an official-directory replacement for Marshall's language link; no repeated access-denial or catalog-shell attempts.
# Finite policy closure — 2026-10-11

- Read [CLS petition policy](https://cls.ucsd.edu/courses/petition.html), HTTP200 via robots-aware fetch. The minor petition requires form, syllabus and evidence of at least 50% related content in one PDF. The page distinguishes minor, college GE and university DEI exception requests; incomplete requests are not processed. Added a guarded parser that reads the numeric threshold. This closes the previously unread petition branch, but does not turn seasonal starred courses into automatic Warren approvals or a permanent complete pool. No petition/contact was sent.
- Independently found and read the current [central language directory](https://advising.ucsd.edu/students/degree-requirements/language-requirement.html), HTTP200. It explicitly identifies Marshall language study as a disciplinary-breadth option. It supplies neither a finite eligible-course pool nor a blanket proficiency waiver. Added an observed-classification parser. Marshall's major discipline/unit/level/writing/overlap rules remain controlling.
- Bounded official discovery for a replacement course-level language policy found that the [LLP Spanish resources directory](https://llp.ucsd.edu/languages/spanish/resources.html) still links to the a legacy students.ucsd.edu language-course route. Did not follow this legacy directory link or retry the known broken route. Search results also surfaced an old 2013–14 Marshall sheet, not evidence of current eligibility. No replacement was verified; this is not evidence that a policy does not exist.
- Read current [UC Cal-GETC guidance](https://admission.universityofcalifornia.edu/admission-requirements/transfer-requirements/preparing-to-transfer/general-education-igetc/cal-getc/), HTTP200. It establishes fall2025+ CCC entry context, full completion before transfer and C-equivalent grading, not Seventh-specific substitutions. Official-source searches for Seventh with CalGETC/Cal-GETC reidentified its existing transfer page, which names IGETC. No independently published Seventh applicability decision was verified. The new context parser expressly leaves that college decision unresolved; no automatic IGETC equivalence is asserted.
- Three policy notes added; no course pools added. UCSD now 2,368 course observations / 5,846 requirement nodes, still partial. Other source conflicts/access barriers above remain. This finite pass is complete; any next work needs a specific new official policy lead or institution clarification, rather than repeated broken links or expanded optional-degree inventories.

### Conditional college graph correction — 2026-10-11

The fixed/choice curriculum profile exposed a structural error: college and admit-cohort qualifications were present in summaries, but 588 college-specific branch roots lacked the matching college pathway ancestry. Reparented these existing roots beneath the eight previously sourced `policy-college-*` note nodes. No course, amount, selection count, source, or cohort rule was removed; existing nested option structures remain unchanged. The source adapters now apply the same source-namespace-to-college binding when creating observations, including linked Warren pools, transfer policies and college-specific exam-credit rows. University-wide major, exam, DEI/AHI/climate and writing rules retain their existing separate scope.

In particular, [Revelle humanities](https://revelle.ucsd.edu/academics/general-education/humanities.html) HUM1–5 applies to its first-year route; [Marshall first-year GE](https://marshall.ucsd.edu/academics/first-year-ge.html) DOC1–3 applies to that route; [Marshall transfer GE](https://marshall.ucsd.edu/academics/transfer-ge.html) DOC170 applies to Fall2026-and-later transfers and first becomes available Winter2027; and [Eighth transfer requirements](https://eighth.ucsd.edu/academics/degree-requirements/transfer.html) CCE110/120 is the transfer sequence, with CCE110 beginning Fall2026. These are eleven conditional college/cohort courses, not eleven universally required AI-major courses. Existing source-specific summaries preserve transfer-certification, exemption, and source-conflict qualifications; no source was newly fetched or verification date advanced for this graph correction.

The profile now reports **8 fixed mapped major courses**, rather than 19; college-specific choices have unresolved applicability context under the conservative note-ancestry contract. There is no invented choose-one-college or elective obligation. This does not assert that the eight courses alone complete the major, or resolve a student's college/cohort/credit evaluation. The complete documented inventory remains **2,368 courses / 5,846 nodes**, and the curriculum remains partial with the previously documented evidence gaps and conflicts. Focused tests exercise the actual source parsers, all eight college bindings, nested-parent preservation, and the real seed's fixed-course/profile result.

## Degree correctness audit — 2026-10-11

See [eight-degree audit](../../../research/degree-audit/west-purdue-wpi.md) and its adjacent per-program JSON ledger. This program is blocked for whole-degree certification by the specific evidence gaps recorded there. Verified role/subject corrections are retained; parser success and prior local curriculum labels are not a completed degree audit. Remaining course-content review work is distinguished from actual source barriers. Independent second pass remains pending.

CSE12/30 now have actual course titles, four-unit values, concise descriptions and prerequisite metadata. CSE101 is computing foundations; CSE30 is systems. Newly inspected2026–27 Mathematics source confirms MATH20A/20B four-unit values and calculus content, with prior-credit reductions retained. No prerequisite course is added. AHI course choices now inherit the existing alternative-fulfillment policy note, and climate choices inherit the transfer-exemption scope note. The current partition is8fixed/119options/2,241contextual, from2,368course observations. Broad GE membership no longer implies human-context subject.

### Remaining CSE source-content integration (2026-10-11)

The coordinator's separately guarded82course review is composed after existing
CSEtag/core observation and subject wrapping, preserving all requirements and
original core records. Six exact identifiers are absent from that current chapter;
their dispositions are unclassified, without descriptions/renumbering assumptions.
Manual taxonomy review annotations are deliberately applied from the reviewed
manifest, never returned by a parser. See `CSE_REVIEW.md` and the source-review note.

The primary reviewer additionally reread all8existingcoreCSEdescription blocks.
The earlier metadata parser incorrectly truncated prerequisites at the first
semicolon/sentence, losing undergraduate/major-priority and space-permission rules.
It now retains full suffixes, CSE100optional preparation, and the preceding151A/
COGS188credit restriction. No logical parentheses are invented. CSE25/55priority
forCS29includes explicit space-based admission for others. Conditional restrictions
are retained rather than interpreted as extra required courses.

Role counts remain8fixed/119options/2241contextual. Source-reviewed new content
changes subject composition only; CSE5/5RAI/CS/DSexclusions do not disappear because
of a collegeGEreference. Other subjects and college/cohort applicability remain
accessible work; whole-degree status staysin_progress.


### UCSD PHIL/ECON contribution integration (2026-10-11)

The independent contributor read all66 available exact course blocks among68
represented PHIL/ECON records. Primary integration applies65 guarded observations
and manual subject dispositions; two absent exact codes and one substantive
identity conflict remain unclassified. This is a bounded contribution, not an
independent whole-degree audit. Existing8fixed/119option/2241contextual role sets
are unchanged. The65 contextual subjects add57human-context,7domain applications
and1mathematics disposition. Additional eligibility notes are preserved by code
in program notes, including the source’s PHIL110 sequence typo and PHIL185 repeat
wording; no prerequisite becomes a required degree course.

Primary reinspection of the saved June2026 DEI PDF text and rendered table confirms
that ECON185 actually bears the Educational Equity title and ECON120B AND MATH181B
there. The current Economics chapter instead names Detecting Discrimination in
Data and uses OR. This is not silently repaired as a parser-neighbor error; the
current candidate remains in the contribution manifest pending identity/source
clarification. ECON163 and PHIL28GS have no exact current headings, with no
substitution or discontinuation inferred. Other accessible UCSD subjects remain
active; SOCI87 is delegated separately for actual source-content review.

### Sociology and anthropology content integration — 2026-10-11

Delegated full-block reviews in `ucsd_soci_reviews` and `ucsd_anth_ansc_reviews` inspected 157 current descriptions among 162 represented identifiers. Primary integration replayed the whole-block/edition guards and independently checked consequential examples: SOCI 102/108 applied social-data methods, SOCI 105's six units and malformed conjoined prerequisite, SOCI 194's four units versus its separate six-unit internship, ANTH 43's mixed genetic/social content, ANTH 128A's six-unit climate fieldwork, ANTH 196B's B+ prerequisite, and ANSC 138/171's applied ethnographic methods. This is integration of delegated source review, not a claim that the primary independently reread every block.

155 approved observations were integrated. SOCI 171 remains the represented *Technology and Science* identity, with the current *Technology and Society* observation withheld. ANSC 190GS retains the represented Southeast Asia/Bali identity while the current South Asia observation is withheld. SOCI 123/144P/158J, ANSC 116 and ANTH 44 have no exact current chapter heading; no cancellation or replacement is inferred. Both title/version scopes and unknown classifications are preserved.

Source restrictions and repeat/cross-list details remain course-scoped notes and full eligibility suffixes. Approval, Global Seminar, Honors, UCDC and MMFRP rules are not waived by college-pool membership. No new identity group or requirement node was added. The manually established role sets remain **8 fixed / 119 options / 2,241 contextual records**. Accessible other-subject review remains in progress alongside the precise source conflicts; no whole-degree certification is implied.

### ETHN current descriptions — 2026-10-11

Delegated88full-block review for95represented ETHN identifiers integrated after source replay. Primary independently checked100H/114B/136/146A/162/179/189/110 examples and exact source-format guards; this is bounded integration, not all-block independent second review.81human-context,5mixed,2selected-topic unknown;7exact missing headings remainunclassified(107/124/154/190/1A/1B/1C). Unclassed110paragraph and both180/184/185A blocks are guarded. The189LatinAmerican pool restriction remains conditional, and179fourunits is not its eight-unit repeat ceiling. No role/identity changes:8fixed/119options/2241context. Further accessible chapters remain active.

### VIS current-description integration — 2026-10-11

Delegated review read 74 exact current descriptions for 87 represented identifiers; 67 observations were approved. Primary independently checked VIS 42/6/157/160A/160B/190/152/155 and replayed the full-source guards. VIS 42 teaches programming and computational thinking despite its creative setting; VIS 6 analyzes race/gender in AI fiction, not AI methods. VIS 160A/B project topics remain unknown with ICAM-major restrictions. VIS 190 is eight quarter units. The approved set contains 56 human-context, seven applications, one foundations, one mixed and two unknown observations.

Seven materially different title/version scopes (129A–E, 152, 155) remain held, and thirteen represented identifiers have no exact current heading. Missing 126D is not replaced by 126I merely because 126I excludes credit with it. Source prerequisites, consent and production-course limits remain course-specific; no degree obligations or identity groups were added. The manually reviewed profile remains 8 fixed / 119 options / 2,241 contextual records. Further public descriptions remain active work; no complete independent second pass is claimed.

### Current POLI content integration — 2026-10-11

All116 assigned identities have source dispositions:113 current observations integrated;132B/133DD/134A lack exact headings. The contributor read the chapter; primary checked full methods, units, graduate-scope and corequisite examples. Six grouped headings explicitly publish multiple codes, and132 uses an unusual unwrapped paragraph; guards preserve both structures. Category decisions are96human context,6applications,1mathematics,5mixed and5unknown. Intelligence fieldwork is not AI; cyberwar politics is not automatically computing.

191A's printed4–4 sequence notation is retained with scalar creditsnull.194SD's197SD corequisite remains conditional preparation, and120J/220J clauses retain their separate levels.124 has a one-sided explicitSOCI188I same-course statement, preserved without a new identity group. No roles or college/cohort contexts changed:8fixed/119options/2241context. Other accessible subject batches remain active.

### European history contribution — 2026-10-11

All74 assigned HIEU identities are dispositioned:56approved current observations,17missing exact headings and122held for a substantive temporal-title mismatch. Fifty approved descriptions support human context,145 combines historical inquiry/public-education project practice, and five unspecified topics/studies remain unclassified. Primary checked122/124/124GS/145/160/198 actual paragraphs and the chapter's before1800 plus marker.124omits units and198has variable1/2/3/4, so neither receives a guessed scalar amount. The124GS credit exclusion is preserved without importing its separate GlobalSeminar admission rule into124. Source-specific preparation and90UCSDunit/GPA2.95 conditions remain conditional. The shared History URL currently parses this bounded HIEU subset; later subject observers must explicitly compose rather than overwrite it.

### Urban Studies and Planning current content — 2026-10-11

All 53 exact current USP blocks among 57 represented codes were manually read. Four absent headings (129/130/154/165) remain unmatched, without suffix substitution. Source-specific judgments distinguish 33 human-context, 11 applied-domain, three mixed and six unspecified-topic records. Design/finance/public-health/data-method courses are not classified from their institutional prefix; critical policy and social interpretation remain human-context. Exact quantities are 47 four-unit, five six-unit and one eight-unit course. The USP194 internship is separately six units, not part of its four-unit seminar.

Full approval, application, senior/major, prior-course and offering conditions remain course-specific. USP188 Spanish fluency is recommended, MMFRP admission required; 185A/186 remain restricted to their named majors, and 190 retains its 3.5 major-GPA requirement. Source cross-list/renumbering statements are notes pending separate identity review. This changes no graph role: 8 fixed / 119 options / 2,241 context. Context subject totals are now 1,646 other, 512 human-context, 51 applications, seven foundations, 23 systems and two mathematics. Other accessible chapters remain active. See the [full contribution note](../../../research/degree-audit/ucsd-usp-course-content.md).

### Communication current-content integration — 2026-10-11

The contributor read all 41 exact current blocks among 45 targets; primary independently checked seven consequential taxonomy, title, eligibility and credit examples. Thirty-nine approved metadata observations are integrated: 31 human-context, four applications, one mixed and three unclassified. Four exact codes are absent; 102C and 120P retain older pool titles with current title/version holds rather than forced renames. Exact current descriptions for those held identities are documented in the contribution, not silently transferred.

COMM102D explicitly says no prerequisites, while absent labels elsewhere remain unknown. The three approved six-unit practicums retain those amounts; COMM194 remains a four-unit seminar with a separate six-unit internship. Critical-design124A is mixed; practical production/field methods support applications; thematic food justice and communication history remain human-context. Source prerequisite conjunctions, fieldwork, repeats and exclusions are retained without invented precedence or aliases. See [source review](../../../research/degree-audit/ucsd-comm-course-content.md). The unchanged8/119/2241 graph now has context categories1611other/543human/55applications/7foundations/23systems/2math; further accessible subject work remains active.
