# Independent profile correctness review

2026-10-11 · reviewer: frontend-independent. This is a bounded second pass, not a replacement for institution owners’ complete degree audits. The JSON preserves the initial published-data screen for all 63 degree records and the exact scope of each subsequent check.

## Case Western correction independently verified

The public data export showed BA fixed8/foundations0/other3 and BS fixed9/foundations0/other4. Its course inventory already included programming, data structures, discrete mathematics and algorithms. The immediate defect was category assignment and insufficiently explicit zero semantics, not missing course identities or numerical summation.

I independently fetched and read the current official BA and BS Program Requirements and CSDS descriptions through the robots-aware fetcher. The source bodies stay ignored under `var/degree-independent/`. Review of correction `41e36d5` confirms these manual fixed sets:

- BA: MATH121, MATH307, CSDS233, CSDS302, CSDS310, CSDS330, CSDS340, CSDS395A. Eight identities: two foundations, three mathematics, three AI/ML.
- BS: the same eight plus ENGR399. Its independently read description addresses ethical/professional responsibility and disparate impacts, supporting one human-context record.
- CSDS134 **or** the complete CSDS132+237 bundle is the introductory programming alternative. All three are foundation option records; none is an unconditional fixed course. The source excludes credit for both132/134 and134/237;237 requires132. CSDS310 has C-or-higher prerequisites in discrete mathematics and data structures. These source conditions are not extra fixed course nodes.

The degree tables and individual descriptions use differently presented credit labels. No alternative route is summed with the other, and no unit conversion is inferred. This second pass verifies the fixed aggregate and introductory alternatives, not the entire744/756-record elective/general-education inventories. Full-degree second-pass status remains **partial**; the primary audit’s earlier requirement-complete label cannot substitute for full correctness review.

## Cross-institution and graph checks

CMU15-210’s independently read description centers on designing, analyzing and programming data structures and algorithms. Penn’s official undergraduate Computing(5CUs) table explicitly lists CIS1210 Data Structures. These support a consistent foundations interpretation alongside CaseCSDS233. Their fixed graph membership is verified, while CMU15-112 prior programming preparation stays contextual rather than being added to the degree core.

MIT’s versioned6.1210 occurrence and the unresolved catalog occurrence have distinct provenance. Graph review confirms the versioned foundation is fixed while the conflicting note-rooted occurrence is unresolved. The duplicate code is not silently counted as another fixed obligation. This check does not resolve MIT’s source-version disagreement.

Resolved Northeastern Biology family records retain CS2000/2001 as inherited fixed occurrences counted once. Buffalo’s policy-analysis framework notes yield no fixed set; that zero means no fixed set established by the mapped graph, not no actual required curriculum. Existing family replacement/exclusion regressions remain applicable. The family checks here inspect graph semantics; they are not independent full source audits of these degrees.

The initial cross-program screen also flagged Northwestern’s large fixed `other` set, Rice’s unreviewed fixed categories, Penn technical-pool mathematics labeled `electives`, and WPI discrete mathematics labeled `ai_ml`. These were routed to the coordinator for exact-source review. The screen deliberately does not classify from keywords or department membership.

## Presentation and regression evidence

Detail and comparison profiles now show **0 mapped**, define it as no mapped classified records in the selected view, and state that it does not prove absence from the curriculum. Per-view reviewed/mixed/unclassified/unreviewed counts are separate from requirement completeness. Course rows disclose legacy/unreviewed classification or the source-backed rationale, locator and sources. Coverage/methodology and degree pages report the separate correctness audit.

`tests/test_independent_degree_profile.py` encodes the manually established Case fixed identities and introductory alternatives, CMU/Penn source-specific examples, MIT source-version isolation and resolved-family checks. Browser regressions verify corrected Case foundations2 with its official classification link and zero/missingness wording on mobile detail/comparison, preserving rank sorting and history.

## WPI bounded role correction (146700c)

Independently fetched both current official WPI degree pages. The AI page’s AI Core Courses explicitly lists “Three of” DS1010, DS2010 and DS3010 with exactly those three identities and3/3 units. This is source-established closure, not a generic inference that any observed menu matching its count is complete. Together with CS2223 and MA2611/2612, the fixed mapped set is six. The8/3-unit AI core total includes this sequence; it is not an additional8/3-unit selection. The revised graph has6 fixed,211 options and2 contextual records.

The Business Analytics and Applied AI source uses recommended/equivalent mathematics and course alternatives through the foundation blocks. Its six-elective load retains the Business Analytics Applications minimum3, Computing/Data/Math maximum3, and Business/Entrepreneurship maximum2. The revised graph’s0 fixed,47 options and2 contextual records is consistent with these choices; it does not imply no required curriculum.

WPI DS1010/2010/3010 mixed/other classifications explicitly disclose title-only uncertainty. This pass verifies the source-defined role correction, not all course categories or degree-wide policies. Full-degree second-pass status remains partial.
