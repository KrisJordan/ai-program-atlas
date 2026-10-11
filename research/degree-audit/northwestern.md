# Northwestern BSE correctness audit — policy-blocked

Reviewed the current **2026–2027** AI major and McCormick catalog, all represented course-directory blocks, and the public degree-policy sources on 2026-10-11. This covers the standalone McCormick BSE pathway; the two additional-major variants are separate records. The primary review has finished its accessible represented-course, role, identity and policy work. It remains **blocked** by two specific authoritative policy discrepancies below. The full independent second pass is pending.

## Verified requirements and corrections

The degree has 48 units: 26 core and 22 major. The major requires five core course slots, four advanced electives, one course in five distinct breadth domains out of six, one societal-impact course and seven technical electives. Engineering programming, introductory CS and physics retain their alternatives. The basic-science total includes the major's physics choice; laboratory/lecture bundles and the four half-unit writing/design records remain intact.

The prior agent corrected seven unindented innovation/oral-communication rows that had been wrongly promoted to fixed courses. The continuation found two further role errors. Four advanced-elective introductory exceptions were still represented as a note; their existing 14-item pool now has four-course choice ancestry alongside the open rule for any course at level 300 or above. Separately, the honors-calculus substitution was present only in prose while MATH 228-1 remained fixed. The college explicitly permits ES_APPM 252-1/252-2 for the corresponding MATH 228-1/228-2 sequence; the actual honors descriptions corroborate that correspondence. MATH 228-1 now has its ES_APPM 252-1 choice. ES_APPM 252-2 stays contextual to the general sequence and does **not** replace AI's fixed COMP_SCI 212.

Thirteen finite theme exceptions were previously embedded only in prose. They now appear under the seven-unit theme requirement, supplementing its open department predicates. GEOG 1xx and the credit-bearing 300-level PRDV rule remain open predicates. Nine exceptions have exact current descriptions; four GEOG codes retain unknown names/content/amounts after the public subject path returned 404. The source's unsuffixed single-term codes were matched explicitly to the corresponding current `-0` identities for BUS_INST, NAV_SCI, TEACH_ED and TRANS, rather than applying a general guessed normalization.

## Independent expected sets

The fixed list is MATH 220-1/220-2; COMP_SCI 212/208/211/348/349; GEN_ENG 231/241; DSGN 106-1/106-2; ENGLISH 106-1/106-2. Thus there are **13** fixed records: **2 foundations, 5 mathematics, 2 AI/ML, 2 human context and 2 mixed design**. Four fixed writing/design records total two units, not four.

`northwestern-profile-expectations.py` independently reads the actual first-column major/college code sets and introductory exceptions, adds the manually reviewed 13 theme exceptions and honors correspondence, and checks the complete source-code inventory. Specific topic versions are preserved as distinct records matching the actual major table. Without traversing requirements or calling the profile function, it applies the manual fixed set, assigns the remaining actual option pools, retains ES_APPM 252-2 as context, and applies the separately reviewed robotics cross-list. The explicit canonical-ID sets and independently tallied categories are in the JSON ledger.

| View | Identities | Foundations | Math | AI/ML | Systems | Human context | Applications | Other |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| Fixed | 13 | 2 | 5 | 2 | 0 | 2 | 0 | 2 |
| Options | 175 | 8 | 8 | 24 | 29 | 16 | 61 | 29 |
| Honors context | 1 | 0 | 1 | 0 | 0 | 0 | 0 | 0 |

These are **190 source records / 189 reconciled identities**, not the number of courses a student takes or a workload/credit distribution. The contextual honors record is not an unresolved missing requirement.

## Content, eligibility and identity evidence

All 190 records have explicit reviews. There are 169 substantive descriptions/core summaries; 16 named special topics have only their exact approved title and a generic course block, so topic-specific descriptions remain null. The COMP_SCI 1CA examination-credit designation and four GEOG code-only entries remain unclassified. Five credit amounts are unknown. Missing prerequisite statements remain null; no independent syllabus or first-offered date is inferred.

The 34-subject editorial manifest uses original summaries and exact source-body digests. It separates systems work from general software foundations, science-domain content from AI methods, and ethical/social AI inquiry from algorithm instruction. Mixed robot hardware/AI, biological/computational vision, online-market methods, responsible software engineering, and formal social modeling remain explicitly mixed. Generic special-topics bodies do not certify topic-specific classifications; those seed reviews cite the major table and state their limited basis.

Course conditions remain independent of degree roles. COMP_SCI 212 names 110/111 preparation while the major introductory choice is 180/111; choosing 180 does not establish a waiver. COMP_SCI 469 permits undergraduate enrollment only with instructor permission. MATH 230-2 excludes McCormick students despite its inclusion in the major introductory exceptions; it is not presented as unconditionally available to every student. Graduate/undergraduate level variants, prior preparation and permissions are not new fixed obligations.

MECH_ENG 301 explicitly identifies COMP_SCI 301 as its cross-list; both actual descriptions were read and describe the same introductory robotics laboratory. That pair is reconciled while preserving both source records. Other slash-separated alternatives, identical 300/400-level descriptions and credit exclusions do not establish identity and remain separate. In particular, COMP_ENG 368/468 explicitly exclude dual credit but the graduate course has its own project condition.

## Policy limits and access observations

The 2026–2027 catalog and undated public school page disagree on the theme declaration deadline: junior winter versus the end of sophomore year. They also specify the P/N cap as **eight units** versus **eight courses**. Fractional-unit courses make those statements non-equivalent. The linked January 22, 2018 departmental P/N table has no AI row; its CS prohibition is not transferred to AI. The current catalog delegates major P/N applicability to the department, and permission is not assumed. These are the two primary audit blockers.

Public transfer guidance calls the generic major 21 units, whereas both the exact AI degree and current college catalog say 22. The represented degree remains 22, and the older/general discrepancy remains visible. Other home-school degrees are outside this standalone pathway, not an unfinished McCormick requirement.

Reread public sources also confirm GPA 2.0 overall and in the major, at most three D major units, C or better external credit, four major transfer units with approvals, 11 unique major units, university quarter/unit residency, theme categories/overlap/level limits, complete duplicate sets, registration/transfer procedures and waiver rules. No private advising system was entered.

Actual course captures and original fetch timestamps are in ignored `/tmp/nw-full-audit/`, with `fetch-index.json`, `tgs-index.json`, `tgs-comp_eng-retry.json` and `theme-fetch-index.json`. The initial sandbox DNS failure was resolved through an approved ordinary network call. One public TGS computer-engineering disconnect succeeded on one retry. `/search/?P=COMP_SCI%20449-0` is robots-disallowed and was not retried; Graduate School directories were independently linked by catalog navigation. The GEOG course-directory path returned 404; no bypass or absence inference followed. The major and college source captures are `/tmp/nw-audit-major.html` and `/tmp/nw-audit-college.html`; public policy captures are cached by URL and `/tmp/atlas-policy-nw-*`.
