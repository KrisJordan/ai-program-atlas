# Eight-degree correctness review — 2026-10-11

Five records are **in progress** because accessible course-content review remains unfinished; UC Merced and Furman remain **blocked** at their unavailable detailed curricula. WPI Business is now **blocked** only by three specific policy questions after its represented course-content review finished. Genuine policy/access blockers coexist with the five ongoing audits, but do not conceal accessible work. This is not a claim that all accessible course descriptions were reviewed. The JSON ledger records specific source gaps and conflicts separately from the remaining accessible course-content review backlog. Earlier curriculum completeness labels and successful parsers do not establish a completed degree audit.

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

**WPI:** general HUA transfer B− language conflicts with language-specific B/C thresholds and a later B− recommendation. Registrar graduation dates/deadlines differ from the catalog. AI Business Applications and Social Science/Policy concentration subsection allocations do not fully explain their six-course totals. Business AI references a graduate-course count limit that is not supplied; a graduate double-count percentage is not an equivalent rule. FIN2070's section label differs from its linked course-row title; the current individual course page now verifies the row identity and finance subject, so that naming context is no longer an unidentified-course blocker. The actual policy conflicts are not reconciled by assumption.

**UCSD:** tentative department versus catalog CSE191 eligibility, Roosevelt residence/MMW transfer differences, Revelle transfer humanities/science formulations, Marshall language eligibility, Seventh CalGETC applicability, and separately documented AP/IB/Chinese-course credit discrepancies remain. Legacy Warren discipline hosts stopped at robots redirects. The graph correctly retains conditional college/cohort scope despite these unresolved decisions.

**UCSB:** CMPSC41 five/four-unit disagreement, science ListsA/B membership, capstone identity, dynamic approved GE pools, ELWR wording and Engineering CalGETC applicability remain unresolved. Current GEAR supplies 72 upper units and 8/12 science allocations; it does not supply the missing memberships or resolve the CMPSC41 conflict.

**UC Merced:** the permitted official overview supplies a BS identity and aims, not named requirements. The officially linked current catalog returned403. **Furman:** the official directory verifies undergraduate BS identity, but its AI detail page is password protected; activity and curriculum remain unknown. No different program's curriculum is borrowed.

Independent second-pass review remains pending for all eight entries.

## Current WPI course follow-up

Seven actual current catalog pages were read through the robots-aware client on 2026-10-11 (HTTP200): CS2223, MA2611/2612, DS1010/2010/3010 and FIN2070. All explicitly publish 1/3 WPI units. CS2223 is foundations; MA2611/2612 mathematics. DS1010 remains mixed programming/mathematics/AI. DS2010 now has a defensible AI/ML focus from its learning-method and prediction workflow description. DS3010 remains mixed, with corrected systems/AI candidates rather than inferred mathematics. FIN2070’s current full heading is Risk Analysis for Decision Making; its description teaches finance, valuation and investment risk. The program slot label Fundamentals of Finance does not contradict that course identity. Its subject is applications.

The WPI AI fixed set is unchanged at six identities: one foundations, two mathematics, one AI/ML and two mixed other. FIN2070 remains an option in both degrees, and DS2010 remains an option in Business. Recommended Background text, including explicit None for DS1010, remains advisory rather than new degree prerequisites. FIN2070 has no displayed background field; that absence remains unknown. No course or requirement count changes. The complete source/credit/background guards emit observations only and stop on changed title, content, units or catalog edition. Accessible unreviewed WPI course pages remain queued; justified HUA, graduation-timing, graduate-count and concentration-allocation questions are retained.

## Completed WPI Business content inventory

The current program distribution and all **49 represented course descriptions** were read: 47 options and two contextual HUA records. The observed partition remains zero fixed / 47 options / two contextual. The options independently comprise four foundations, eleven mathematics, six AI/ML, three systems, three human-context, seventeen applications and three mixed records. HU3900/3910 are human context. Every reviewed course explicitly publishes 1/3 WPI units. Full course-page guards include descriptions, credits, recommended and suggested background, eligibility and credit restrictions. Runtime parsers emit observations, never manual category reviews.

The two HUA pages establish five prior HUA courses, including two thematically related and one at 2000 level or above; HU3910 additionally requires instructor consent. The degree's three-course depth rule applies at graduation and is compatible with the smaller entry minimum. They remain contextual courses. Credit exclusions are retained as restrictions, not cross-list identity evidence. OIE4430's suggested mathematics preparation is advisory. FIN3330 centers on learning algorithms and is AI/ML; optimization and simulation courses with substantive mathematical methods are mathematics. Business subject membership alone determines neither classification.

No known unread represented Business course block remains. Open prefix, level, approved-equivalent and relevance criteria remain source-defined rules, without fabricating finite exhaustive lists. The three genuine whole-degree blockers are HUA transfer-grade applicability, catalog versus registrar graduation timing, and the unspecified referenced graduate-course count limit. The graduate enrollment exception and 1-to-1/6 unit conversion do not supply that count.

Shared source observations also complete **44 WPI AI records**: six fixed, 36 options and two contextual. **175 AI option descriptions remain accessible and unreviewed**, so that audit stays in progress. Its concentration-allocation and university-policy questions remain separate. No additional course obligations or changes to role counts were introduced.

## WPI AI computing and mathematics option follow-up

A further 33 current undergraduate descriptions were read in full. Coverage is now **77 of 219 represented records**: six fixed, 69 options and two contextual; **142 option descriptions remain accessible and unreviewed**. Each new page explicitly publishes 1/3 WPI units, including fourteen-week MA1020/1120; course duration does not imply a different credit value. Role sets remain six fixed / 211 options / two contextual.

Classification follows actual content: numerical methods and discrete proofs are mathematics; database internals and machine-facing systems programming are systems; general software design and algorithms are foundations; neural learning, language models and multi-agent methods are AI/ML. CS4445 combines data integration infrastructure and learning-based discovery, CS3041 combines human evaluation and interactive construction, and CS4804 combines graphical communication and implementation; each remains mixed other with explicit candidates. These are whole-course categories, not fractional counts.

Explicit restrictions are retained separately from advisory preparation. CS2301 prohibits subsequent credit after CS2303, a directional rule rather than an invented symmetric equivalence. CS3043/SS3043 cannot satisfy the Social Science Requirement even though it is an eligible major ethics course. Duplicate-credit exclusions and slash-code headings do not establish new cross-list identity groups. MA2210's suggested preparation and credit restriction remain separately identified. No new prerequisites are counted as degree obligations. Full content/version/identity guards cover all 33 observations; the audit remains in progress.

## Graduate computing alternatives reviewed

Fifteen official graduate computing/data-science pages were read in full, bringing AI coverage to **92 represented records** (six fixed, 84 options, two contextual), with **127 accessible options still unreviewed**. Each page publishes **3 credits**, without a displayed edition or a normalized credit type. Records therefore retain 3 with `credit_unit: unknown`, and source `catalog_year: null`; no 2026–27 edition is fabricated from the undergraduate parent page. The separately published conversion to undergraduate units remains a policy, not a rewritten course value.

Actual preparation fields preserve alternatives and permission clauses. CS542's field labeled Prerequisites says CS5084 would be helpful; this is not treated as mandatory merely because of its heading. CS509 distinguishes needed programming/data-structure knowledge from a desirable software-engineering course. Full-page guards include these qualifications. Runtime parsers return facts, not manual category reviews.

Responsible AI combines substantial social/ethical analysis and technical learning methods; learning development/operations combines programming and infrastructure rather than establishing an AI-methods focus. These and the substantive mining/infrastructure and retrieval mixtures remain `other` with explicit candidates. Neural, generative, reinforcement and language learning courses have AI methods rationales; databases are systems and general software engineering is foundations. No graph memberships, choice quantities or fixed-course counts change. The primary audit remains in progress.

## Electrical engineering and robotics option follow-up

A further 24 complete course descriptions are reviewed: nineteen undergraduate pages publish 1/3 WPI unit, and five graduate pages publish three credits without an edition or normalized unit label. AI coverage is now **116 of 219 represented records** (six fixed, 108 options, two contextual), with **103 accessible options still unreviewed**. Fixed/option/contextual roles remain unchanged.

Robotics mechanical construction and sensor integration are applications; neither robotics nor perception in a title establishes AI. The explicit neural-learning and AI algorithms do establish AI/ML. Digital hardware and embedded architecture are systems. Continuous/discrete signal courses focus on mathematical transform analysis, while real-time DSP focuses on hardware execution. Human-factors studies are human context. Substantial software/hardware, learning/infrastructure and human/robot-learning mixtures retain explicit candidate categories.

Credit exclusions remain conditions, including the reciprocal ECE2049/RBE2020 restriction. The RBE526 page explicitly equates RBE595, but no separate RBE595 record exists in this inventory, so no identity group or new course is invented. ECE545/CS545 publishes only a referral to CS545. The linked official Computer Science directory identifies CS545/ECE545's full image-processing and machine-vision description; both pages are registered and independently guarded, preserving the existing single combined-code identity. Qualified probability preparation remains helpful rather than mandatory. No description-referral text is passed off as a full subject review.
