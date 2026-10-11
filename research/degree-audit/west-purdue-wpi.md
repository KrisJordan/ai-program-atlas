# Eight-degree correctness review — 2026-10-11

Six records are **in progress** because accessible course-content review remains unfinished; UC Merced and Furman remain **blocked** at their unavailable detailed curricula. Genuine policy/access blockers coexist with the six ongoing audits, but do not conceal accessible work. This is not a claim that all accessible course descriptions were reviewed. The JSON ledger records specific source gaps and conflicts separately from the remaining accessible course-content review backlog. Earlier curriculum completeness labels and successful parsers do not establish a completed degree audit.

Official cached pages were reread without changing their fetch dates. Known catalog denials, protected pages and robots restrictions were not retried or bypassed. UCSD's Mathematics catalog was newly read through the ordinary public reader and the robots-aware fetcher (HTTP200); its 2026–27 heading and two fixed calculus entries were inspected. Raw sources remain ignored.

## Independent role sets

The JSON contains explicit, disjoint course-ID sets. Counts below describe mapped observations, not graduation workloads or completion percentages. They were constructed from these source-specific inventories, independently of `requirement_profile`:

| Program | Fixed | Options | Contextual/unresolved |
|---|---:|---:|---:|
| Purdue AI BS | 9 | 37 | 1,681 |
| Purdue AI BA | 5 | 0 | 0 |
| WPI AI BS | 6 | 211 | 2 |
| WPI Business Analytics and Applied AI BS | 0 | 47 | 2 |
| UCSD AI BS | 8 | 119 | 2,241 |
| UCSB AI BS | 19 | 65 | 2 |
| UC Merced AI BS | unknown | unknown | unknown |
| Furman AI BS | unknown | unknown | unknown |

- **Purdue BS:** manually named nine single-course core obligations. The remaining 33 department major records are alternative/selective/capstone candidates; four college calculus records are alternatives. All remaining observations are contextual college pools. NLP undergraduate/graduate alternatives count as one selection route, not two obligations. The new grade, transfer and graduate-enrollment notes do not add courses.
- **Purdue BA:** the department explicitly names five required CS courses. The unpublished eight-course philosophy inventory cannot be reconstructed from semester offerings. Its 15-hour CS total does not establish five equal three-hour values.
- **WPI AI:** CS2223, MA2611/2612 and the exact DS1010/2010/3010 triple are the six fixed records. The source says three of those three DS courses; the parser guards both the clause and set. The 8/3 core descriptor includes this triple, rather than adding 8/3 more units. The remaining named courses occur in concentration/core/disciplinary choices. HU3900/3910 are conditional HUA context, not universal fixed requirements.
- **WPI Business:** no single named course survives the catalog's equivalent/alternative routes as universally fixed. Named foundation and elective candidates form 47 options; HU3900/3910 remain contextual. Six electives is an inclusive total across bins, subject to minimum/maximum distributions and no double counting.
- **UCSD:** fixed CSE12/30/25/55/101/151A and MATH20A/20B. Options are the union of the explicitly inspected major groups `lower-core-0/2/3/4`, `lower-elective`, `math-1/3`, `science`, `probability`, `upper-core-0/2`, `ethics`, and `ai-electives`. This union has 119 distinct IDs. Other CSE tag/predicate notes and conditional college/approval observations remain unresolved. The 50 AHI course records now sit beneath the existing AHI policy note because high-school, exam and prior-college routes exist. Climate applicability is also structural: incoming transfers are exempt. No invented choose-one-college tree is introduced.
- **UCSB:** eleven preparation courses plus eight universally named upper courses are fixed; CMPSC181/ECE181 is an alternative. All other mapped degree/elective/writing candidates except contextual WRIT1/1E are options. The sample four-year plan is not a requirement source.
- **Merced/Furman:** identity-only evidence cannot establish a curricular partition; expected profiles are null, not a zero-degree claim.

Tests compare these independent partitions and category counts with the application profile. Source loads remain attached to their individual rules and are never summed across overlapping choices.

## Subject findings and limits

WPI's nearly universal AI defaults were corrected in commit146700c. The present pass corrects Purdue, UCSD and UCSB role-based defaults. In particular, algorithms/data structures are computing foundations, ECE139 probability/statistics is mathematics, CMPSC183 ethics/privacy/fairness is human context, and UCSD CSE30's processor/assembly/memory description is systems. UCSD's eight fixed courses now have actual description-supported categories: two foundations, two mathematics, three AI, one systems.

Purdue CS10100's broad digital survey and CS18200's mathematical/computational syllabus are deliberately mixed `other`. WPI DS courses remain mixed where the inspected title/content does not support one primary subject. Ambiguous seminar, data analytics and broad interdisciplinary titles remain `other` until a content review supports more.

Broad GE/culture eligibility does not establish subject matter. Unsupported categories were reset to `other`. A code-only record's `unclassified` rationale says precisely that the recorded observation lacks a title/description; it does **not** claim inspection of an unavailable course description. Named but unreviewed records carry no fabricated review. Exact-title mappings only apply to individually considered identities, and source parsers discard stale review metadata and return `other` when a title changes. Parser observations never manufacture independent review status.

The complete remaining course-content review backlog is substantial, especially the large Purdue/UCSD pools. This is accessible work not completed in this bounded pass, separate from actual access barriers. The ledger's blocked status also reflects concrete unresolved degree requirements, rather than treating workload as a blocker.

## Exact remaining degree gaps

**Purdue BS/BA:** current plans returned403. BS still lacks complete university GPA/residency/civics and competency mapping, language sequences and some UCORE pools; its chemistry grouping and AI-specific applicability remain unresolved. BA lacks the eight philosophy identities, current CLA core and university rules. June2025 canonical outlines and older department titles do not silently become Fall2026 catalog equivalences.

**WPI:** general HUA transfer B− language conflicts with language-specific B/C thresholds and a later B recommendation. Registrar graduation dates/deadlines differ from the catalog. AI Business Applications and Social Science/Policy concentration subsection allocations do not fully explain their six-course totals. Business AI references a graduate-course count limit that is not supplied; a graduate double-count percentage is not an equivalent rule. FIN2070's section label differs from its linked course-row title; the current individual course page now verifies the row identity and finance subject, so that naming context is no longer an unidentified-course blocker. The actual policy conflicts are not reconciled by assumption.

**UCSD:** tentative department versus catalog CSE191 eligibility, Roosevelt residence/MMW transfer differences, Revelle transfer humanities/science formulations, Marshall language eligibility, Seventh CalGETC applicability, and separately documented AP/IB/Chinese-course credit discrepancies remain. Legacy Warren discipline hosts stopped at robots redirects. The graph correctly retains conditional college/cohort scope despite these unresolved decisions.

**UCSB:** CMPSC41 five/four-unit disagreement, science ListsA/B membership, capstone identity, dynamic approved GE pools, ELWR wording and Engineering CalGETC applicability remain unresolved. Current GEAR supplies 72 upper units and 8/12 science allocations; it does not supply the missing memberships or resolve the CMPSC41 conflict.

**UC Merced:** the permitted official overview supplies a BS identity and aims, not named requirements. The officially linked current catalog returned403. **Furman:** the official directory verifies undergraduate BS identity, but its AI detail page is password protected; activity and curriculum remain unknown. No different program's curriculum is borrowed.

Independent second-pass review remains pending for all eight entries.

## Current WPI course follow-up

Seven actual current catalog pages were read through the robots-aware client on 2026-10-11 (HTTP200): CS2223, MA2611/2612, DS1010/2010/3010 and FIN2070. All explicitly publish 1/3 WPI units. CS2223 is foundations; MA2611/2612 mathematics. DS1010 remains mixed programming/mathematics/AI. DS2010 now has a defensible AI/ML focus from its learning-method and prediction workflow description. DS3010 remains mixed, with corrected systems/AI candidates rather than inferred mathematics. FIN2070’s current full heading is Risk Analysis for Decision Making; its description teaches finance, valuation and investment risk. The program slot label Fundamentals of Finance does not contradict that course identity. Its subject is applications.

The WPI AI fixed set is unchanged at six identities: one foundations, two mathematics, one AI/ML and two mixed other. FIN2070 remains an option in both degrees, and DS2010 remains an option in Business. Recommended Background text, including explicit None for DS1010, remains advisory rather than new degree prerequisites. FIN2070 has no displayed background field; that absence remains unknown. No course or requirement count changes. The complete source/credit/background guards emit observations only and stop on changed title, content, units or catalog edition. Accessible unreviewed WPI course pages remain queued; justified HUA, graduation-timing, graduate-count and concentration-allocation questions are retained.
