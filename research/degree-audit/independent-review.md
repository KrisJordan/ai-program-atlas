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

## Lehigh bounded second pass (8b43440)

Independently read the official department degree page and current engineering catalog. The fixed identity arithmetic is11 expressly required technical courses+6 math/science rows+PHY011/012+ECO001=20. Linear algebra supplies3 alternatives, the depth table9, the named general-elective table12, and the engineering catalog’s WRT001/003 andWRT002/005 slots4; the full mapped option union is28. The ledger lists each manually checked identity. Open CSE/HSS/natural-science/free-elective predicates are requirements but cannot generate unobserved course identities.

Course-description spot checks independently support CSE027 foundations, CSE140 mathematics, CSE211 systems, CSE252 human context and ISE230 mathematics. CSE160 combines data preparation/statistics/software; CSE282 combines AI/ML/data-science projects and communication; ECE303 combines GPU/parallel architecture/programming and deep learning. Their mixed status avoids false precision. This is a cross-institution consistency check: an AI-oriented title does not turn foundational software into AI methods, just as Case data structures and CMU/Penn foundations are classified by subject.

The source still conflicts:130–131 versus130total, and11free credits versus4+6in the sample. Main-table economics/writing titles are also copied incorrectly; official course descriptions supply their actual identities. Reuse of prescribed/depth courses in the additional open elective allocation remains unclear. No degree completion claim follows from the20/28partition. The full degree correctness audit remains blocked by source questions; this independent second pass remains partial.

## Northwestern bounded second pass (1cf26ad)

Independently fetched and read the current degree, college and four subject directories. The college's **Select one** instruction applies to seven oral/innovation choices even though those rows lack indentation. The biomedical-engineering footnote does not make its listed course compulsory for AI students. Excluding this menu from the fixed set gives 14, not 21, fixed records. The independent ledger enumerates those 14 and the seven corrected options.

The fixed subjects total two foundations, six mathematics, two AI/ML, two human-context writing records and two mixed design records. COMP_SCI 211 concerns foundational software construction despite its systems title. Four design/writing records each carry 0.5 units: their two-unit load must not be confused with the four-record denominator. The major programming alternative and engineering introductory alternative remain distinct choice rules. The COMP_SCI 212 prerequisite naming 110/111 still differs from the major's 180/111 slot, and the broader elective/policy audit remains unfinished. This is a partial second pass, not whole-degree certification.

## Northeastern shared-course bounded second pass (1eaf8bc)

Fresh robots-aware requests returned both official CS and DS description directories. Independent reading supports CS 1800 and DS 3000 as mathematics; CS 2000/2001/2100 and DS 3500 as foundations; CS 3200 and DS 4300 as systems. DS 4200 combines programming, perception, visualization design and written communication, supporting its explicit mixed status. The AI wording in a mathematics title and the use of databases in programming do not replace the described primary subject. Regression checks follow these identities through Biology and Design family resolution without picking a pathway or adding fractional subjects.

CS 1800 explicitly lists CS 1802 as a corequisite. That omitted dependency has been sent to the primary owner for a source-specific repair; it is not permission to promote every prerequisite into fixed degree workload. These examples do not independently certify all 454 reviewed observations or the 24 degrees. The primary audits and this independent family check remain in progress/partial respectively.

## Rice bounded second pass (07e6ffc)

Independently fetched and read the 2026–2027 major and COMP, PHIL and PSYC directories. Eleven named COMP courses plus PHIL 108 and PSYC 203 form the 13 fixed identities. Their actual descriptions establish three foundations, one mathematics, two systems, five AI/ML, one human context and one domain application. COMP 329 remains systems despite its AI title; COMP 282 centers mathematical optimization. Cognitive psychology is domain knowledge, without an invented claim that the course applies AI. The AI senior-design pair centers intelligent systems, with communication in support of that work.

The calculus AP alternatives, linear-algebra menu and statistics bundles remain options. The elective obligation chooses three different areas out of five and one course within each selected area. These obligations do not make every listed alternative fixed. COMP 456/457's same-academic-year sequence is a timing rule, not extra workload.

Independent course descriptions confirm all three reported applicability conflicts: required COMP 345 and listed COMP 447 exclude registration based on credit in the other; COMP 345/346 name STAT 315 while the degree also offers STAT 310/311 plus 314; and listed COMP 585/631 limit enrollment to graduate students. No waiver or equivalence is inferred. Full elective and university-policy review remains unfinished, so this is a partial second pass despite the verified fixed aggregate.

## Penn State bounded second pass (c75af14)

Independently fetched the two University Park degree pages and official course directories. Engineering's five initial prescribed rows plus twelve C-minimum rows establish 17 fixed identities. Its five named choice blocks contain 13 code records: programming I has three identities across two routes, programming II two, machine learning two, speaking three and writing three. IST has nine prescribed identities. Exact descriptions support the fixed categories, including A-I 305 algorithm foundations, A-I 410 infrastructure, AIE 355 mathematical optimization and PHYS 211/212 domain physics. CMPSC 132 is an option in Engineering but fixed in IST; the subject does not change with that role.

The IST supporting lists were read in full, including unlinked codes and the University Park business branch. **160 names are code observations, not independently established distinct offerings.** Six source slash pairs require explicit cross-list identity handling: CMPSC 442/DS 442, DS 410/CMPSC 410, MATH 318/STAT 318, MATH 414/STAT 414, IST 301/ETI 301 and IST 302/ETI 302. These were routed to the owner and coordinator. Ordinary OR alternatives are not aliases. Neither open CYBER eligibility nor ROTC subject prefixes establish finite unseen courses.

The A-I 370 prerequisite/concurrency mismatch is confirmed in its actual description. The pending-implementation Senate policy and IST capstone/research route ambiguity remain unresolved. These checks do not certify a whole degree or treat every elective record as an additional obligation.

## RIT bounded second pass (e1ff15a)

Independently opened the public study page in ordinary Chrome, expanded all four years and read its 2026–2027 sequence and elective menu. The sequence confirms 23 unique fixed code identities, six two-course alternatives and five AI elective identities; the robotics elective entry itself has two alternatives. The advising PDF's retained public text separately lists CSCI 632, LING 582 and LING 584, preserving three unresolved observations rather than combining conflicting menus into a required pathway.

Eight live course cards were independently read: YOPS 10, IDAI 499/360/485/490, ISTE 476, EEEE 485 and CSCI 431. YOPS 10 and IDAI 499 explicitly carry **0 credits**; the preparation-seminar row also carries zero. Two co-op placements still represent one course identity. The current graph preserves these actual zeros after migration 11. The twelve uncoded context rows do not authorize memberships in the AI elective pool; their cleared memberships agree with the visible source.

IDAI 360's optimization mathematics, IDAI 485's distributed infrastructure and IDAI 490's software-development project provide useful counterexamples to classification by AI title. The live ISTE 476 card omits AI BS from its enrollment list; EEEE 485 requires EEEE 346 or equivalent; CSCI 431 contains the reported self-referential credit exclusion. No permission is invented. The other 32 descriptions and university policies were not independently reread in this bounded pass. Full-degree second-pass status remains partial.

## CMU independent counterexample and repair (2a80350)

The official **All of the following** math table exposed four singleton-choice mistakes: 21-120, 21-122, 21-241 and Modern Regression 36-401. These plain required rows were excluded from the fixed profile solely because their stored nodes said choose-one. The primary owner repaired those nodes after this independent finding. The fixed aggregate is **13**, superseding the earlier nine: four foundations, four mathematics, one systems, two AI/ML and two explicitly unclassified records.

Actual SCS descriptions support the distinction between systems in 15-213 and foundations in 15-122/150/210/251. The mathematics titles precisely identify calculus, linear algebra and regression, with their actual CMU unit amounts retained. Real conditional substitutions and probability/multivariable alternatives remain choices. In particular, 15-112 preparation is conditional on prior credit or waiver, so it is not silently added as a universal fixed requirement. The remaining elective taxonomy and university-policy review remains unfinished.

Penn State identity follow-up: reciprocal official descriptions verify four of the six observed slash pairs (DS/CMPSC 410 and 442; MATH/STAT 318 and 414). IST/ETI 301 and 302 are not established aliases by slash notation alone and must remain separate until source evidence supports merging. The initial 160-code observation count must not be presented as distinct underlying offerings.

## Preparation versus source contradiction

Follow-up interpretation distinguishes an enrollment prerequisite absent from one printed degree route from an actual contradictory rule. Rice's STAT 315 preparation, Northwestern's introductory preparation and Penn State's A-I 370 conditions may require additional or already-satisfied preparation; their absence from a core table alone does not prove the degree is impossible. These remain explicit enrollment metadata, without an invented equivalence or universally added fixed course. Reciprocal credit exclusions, graduate-only enrollment limits, explicit program restrictions and incompatible published totals remain separate source questions. This clarification supersedes earlier wording that grouped all prerequisite differences with source conflicts.

## Rice entire represented course inventory second pass (2508e11)

This supersedes the earlier fixed-core-only scope and its unresolved graduate-access statement. Fresh, independent robots-aware requests returned the 2026–2027 major, all nine relevant subject directories, and three university policy pages with HTTP 200. All **43 listed code records** were independently read, including exact titles, credit amounts, formal prerequisite fields and subject descriptions. The adjacent ledger now contains a per-record manual subject/role judgment and source-block fingerprint. Its observations agree with the curated seed; these judgments are not derived from the profile function.

The fixed set remains **13 identities**: COMP 140/182/215 explicitly teach computation, algorithms and program design, giving **3 computing foundations**. COMP 222's machine organization and COMP 329's data/computation infrastructure give **2 systems**. COMP 282 is mathematical optimization; COMP 345/346/348/456/457 are AI methods and intelligent-system projects; PHIL 108 is ethics; PSYC 203 is domain psychology. Formal preparation forms the documented chain COMP 140 → 182 → 215, while COMP 222 requires 140. The chart must display 3 foundations and 2 systems, not zero; their presence is independently asserted in the rendered-chart regression.

All **30 option code records** are also reviewed. Reciprocal department cross-list statements establish exactly three groups: STAT 315/DSCI 301, COMP 447/ELEC 447, and COMP 450/ELEC 450/MECH 450. Their four alias records reduce the option profile to **26 identities**, while retaining all source codes. The full represented inventory is **39 identities from 43 records**. No required course belongs to those alias groups. Options comprise 3 foundations, 14 mathematics, 5 AI/ML, 1 human context, 1 domain study and 2 mixed identities. COMP 409/480/585 focus on logic/algorithms; COMP 414 on mathematical optimization. COMP 462 combines robotics mechanics, controls and software, while COMP 631 combines retrieval systems and mining; both remain deliberately mixed. MATH 105/106 are examination-credit alternatives, not additional taught classes. The calculus and linear-algebra choices, statistics bundles, and choose-three-of-five elective areas remain separate obligations; no path is selected and nested quantities are not summed.

Selected policy clauses were independently checked. Rice expressly permits instructor-approved electronic overrides for out-of-level registration, so COMP 585/631 are conditional choices, not a remaining access blocker. The sources establish semester credit hours and STAT 314's one-credit amount. Three precise interpretation questions remain: reciprocal COMP 345/447 credit exclusions; STAT 315's prior STAT 310/311 exclusion and STAT 314's STAT 310 prerequisite versus the degree's alternative statistics routes; and the summer-semester difference between graduation and transfer residence policies. The entire listed-course inventory and displayed aggregate have now received this independent second pass. **Full-degree certification remains partial**: those source questions are unresolved, and the university-policy inventory has not received independent line-by-line certification. No permission, equivalence or impossible-degree claim is inferred.
