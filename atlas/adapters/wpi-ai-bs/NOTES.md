# Official evidence — 2026-10-10

## Scope and current result

219 observed course records and 138 requirement nodes. The 2026–2027 official Clean Catalog program page, all **eleven** concentration pages, the MS-AI CS/DS core-bin graduate alternative, and fifteen university policy pages have been reviewed and mapped. Degree remains **partial** for a precise policy ambiguity: the HUA page states B- for transferred US courses, but its language subsection retains B for two-year/C for four-year institutions followed by a B- recommendation. The department’s current Degree Resources page directs evaluation to its coordinator and catalog without resolving that discrepancy. No inferred precedence or invented threshold is used.

## Program and concentration inventory

AI distribution includes ten program units; overall advanced-level minimum; two-of-three introductory CS groups with 1000-level ceiling; algorithms; math with separate calculus pairs; 8/3 core with four bins and its advanced minimum; ethics; natural/engineering science and overlap replenishment; exactly one six-course concentration; disciplinary electives and concentration-related MQP/advisers. The concentration root now selects one whole child inventory. The disciplinary pool includes every observed course option across those inventories, with local eligibility/level/relevance restrictions preserved.

All concentration pages explicitly identify their Associated Degree as Artificial Intelligence Major. They are parent-degree concentrations, not separately awarded/joint degrees. Source URLs in `concentrations.CONCENTRATIONS` correspond exactly to the eleven links on the official AI program page.

Special cases: Advanced AI and Optimization prohibit reuse of core courses. Built Environment excludes preparatory CE2000; molecular biochemistry excludes CH1010/1020; chemical production excludes CH1010/1020/1030. Optimization requires MA1024 plus one probability alternative, not both probability options. Experience Design includes two named graduate IMGD courses shown as 1/2 undergraduate unit and a two-course advanced floor. Social Policy requires a 4000-level course and allows special topics only when AI-relevant; six blank special-topic credit values remain null. Robotics allows an open RBE3000+ pool (including graduate) but excludes RBE3100. Open subject/level predicates are represented as rules rather than an invented exhaustive course list.

## Degree-wide inventory

Fifteen linked policies cover the 15-unit academic minimum, eight-unit residence, science baseline, HUA depth/breadth/language/AP/transfer/off-campus routes, social science eligibility and exclusions, wellness routes, IQP/MQP, grading, major certification, concentration declaration and one-unit additional-designation overlap ceiling/no triple counting, optional double majors and interdisciplinary MQP exceptions, graduate/BS-MS options, transfer approval, project registration/submission/completion/sponsor requirements and degree application deadlines. The standalone Double Major page describes the ordinary two-MQP case; the more detailed Degree Options page supplies the explicit joint-MQP/social-science exceptions, both represented. Administrative constraints are note nodes, not additive credits.

The general science baseline is not additional credit above overlapping major science. WPI has four seven-week terms within two semesters; `calendar: other` retains that distinction. Undergraduate course amounts remain fractional WPI units. Official Graduate Courses supplies the conversion 1 graduate credit = 1/6 undergraduate unit; graduate row values are still kept in their native published credit form. Conversion is a separately cited rule, not silently applied to course records.

## Extraction and metadata

Program, per-concentration, per-policy and selected course-page parsers inspect the supplied HTML. They return partial components, validate headings/clauses and observe changed course rows; they never emit the manual audit or verification date. Raw HTML is only in ignored cache. Three selected AI-degree course pages have short reviewed descriptions/advisory background; remaining metadata/public syllabi remain unverified. Focused synthetic tests cover nested probability choices, graduate wrappers, conditional topics, robotics exclusion, policy conversion and business prohibitions. Parent coordinator owns DB ingestion and family modeling.

## Bounded policy follow-up — 2026-10-11

The BS remains **partial, 219 course observations / 141 requirement nodes**. The public catalog's transfer-credit link redirects to a registrar URL explicitly disallowed by robots; the fetch stopped there. The denied URL was not retried with a removed query or another host, and no browser bypass was used. Existing published HUA thresholds remain contradictory; department resources still delegate evaluation rather than establish a controlling threshold.

The accessible [registrar graduation page](https://www.wpi.edu/offices/registrar/graduation) gives a current undergraduate table: October 4 applications for fall/spring completion, July 15 for summer, with December/May/August conferral. It explicitly accepts December 2026 and May 2027 applications. The catalog's existing prior-term deadlines and September reference differ. Both are retained as source-specific notes; no silent precedence is chosen. Project/HUA completion submission still requires final project work and the applicable eCDR, already represented. Ceremony participation is not degree conferral; optional honors criteria were not imposed on the ordinary degree.

The remaining blockers are the HUA language-transfer threshold and applicability of inconsistent graduation timing. No new finite major/concentration pool was missing. The new table parser reads actual undergraduate rows, excludes the graduate table, detects changed dates and emits partial candidates only. Separate advanced-methods concentration records are unchanged.

## Degree correctness audit correction — 2026-10-11

Reread the registered degree/concentration tables and five relevant official course descriptions. The source explicitly names DS1010, DS2010 and DS3010 as the closed three-course foundation set. These now have an all-only required path alongside CS2223 and MA2611/2612: **six fixed courses**. The 8/3-unit core selection descriptor includes those courses and its component bins; it is not an additional elective load. The exact DS clause and course identities are parser guards. Named courses inside the eleven optional concentrations remain options for the degree, not universal requirements.

The inherited course factory had labeled almost every course AI/ML by default. Removed this unsupported role-to-subject inference. Explicit manual subject mappings use exact official code/title pairs, with title-only limitations in `category_review`; five course-description decisions have descriptive rationales. Mixed/unclassified records use `other`. Changed source titles fall back to `other`, and observation parsers never emit or carry forward manual category reviews. This corrects obvious calculus/programming/accounting/domain-course misclassification without pretending every course description was reviewed. Individual prerequisite metadata, policy/source conflicts and unresolved concentration allocation remain blockers to a complete degree correctness audit.

## Degree correctness audit — 2026-10-11

See [eight-degree audit](../../../research/degree-audit/west-purdue-wpi.md) and its adjacent per-program JSON ledger. This program is blocked for whole-degree certification by the specific evidence gaps recorded there. Verified role/subject corrections are retained; parser success and prior local curriculum labels are not a completed degree audit. Remaining course-content review work is distinguished from actual source barriers. Independent second pass remains pending.

## Full course-content follow-up — 2026-10-11

Whole-degree correctness status is now **in_progress**, because accessible individual-course review remains unfinished even though the recorded policy blockers still apply. The new guarded `wpi_reviewed_course_content` helper reads current2026–27 course descriptions, Units and Recommended Background. FIN2070 is independently verified as Risk Analysis for Decision Making with substantive finance content; its differently named program slot does not leave the course identity unknown. DS2010 is now AI/ML from its actual predictive-methods description; DS1010 remains mixed. AI additionally verifies algorithms, the applied-statistics pair and DS3010’s mixed infrastructure/AI pipeline. All source values remain1/3 WPI units; recommended background is not added to the degree graph. No fixed/option identities change. Full-block source facts and exact remaining accessible work are recorded in the western degree audit; no whole-degree certification is claimed.

## Represented Business inventory closed — 2026-10-11

All 49 represented Business records now have actual current descriptions and exact 1/3-unit values: 47 options and two contextual HUA courses. Their complete page content, catalog edition and identity are guarded. Recommended and suggested preparation remains advisory; explicit HU entry requirements and instructor consent remain distinct. The HUA course entry minimum of two related prior courses is compatible with the degree's three-course graduation depth rule. Published credit exclusions do not establish cross-list identities. No role or course-count changes were made.

This AI degree inherits reviewed observations for 44 existing records (six fixed, 36 options, two contextual), but 175 option descriptions remain accessible and unreviewed. Its whole-degree correctness audit remains **in_progress**. The existing policy and concentration-allocation questions are genuine separate gaps.

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

## Life science and chemistry options reviewed

Twenty-eight complete 2026–27 course pages add 26 domain applications and two mathematical-methods decisions. AI coverage is now **144 of 219 represented records**: six fixed, 136 options, two contextual; **75 accessible option descriptions remain unreviewed**. All 28 explicitly publish 1/3 WPI unit. Role sets and choice quantities are unchanged.

Biological agents, neural physiology and software-assisted biological analysis are classified from their substantive domain descriptions, not terminology resembling AI. CH4210's brief description specifies AI applications in molecular life sciences but no learning algorithms; applications is the supported subject. CH3520 and CHE3501 explicitly organize mathematical tools, modeling and equation-solving and are mathematics. Physical chemistry, biology and chemical-process design remain substantive domain applications.

CHE2011/2012/2013 credit restrictions are expressly limited to CHE distribution requirements; the notes retain that scope rather than inventing a universal no-credit rule. Background preparation stays advisory, with CH2310's assumed general-chemistry familiarity noted separately. All full descriptions and associated fields are guarded. Genuine degree policy gaps remain separate from the remaining accessible work.

## Built-environment and engineering science options reviewed

Thirty further complete pages bring AI coverage to **174 of 219 records**: six fixed, 166 options, two contextual; **45 accessible option descriptions remain unread**. Twenty-six courses teach substantive architectural, civil or physical engineering practice; ENV2720's environmental/social AI critique and ENV2900's alternative-development policy analysis are human context. Generic ENV2800/4800 offerings remain unclassified after reading their entire descriptions because topics vary by offering. That is explicit source uncertainty, not an unread-page backlog.

Twenty-eight pages publish 1/3 WPI unit. ENV2800/4800 instead state an instructor-assigned **1/6–1/3 unit range**. Their fixed numeric credit stays null and the range is retained; it is neither zero nor an assumed endpoint. Both allow repetition for different topics. ENV4800's preparation is an inline recommendation, and any particular offering still needs the degree's AI-relevance approval. CE3051 says prior traffic-engineering knowledge is helpful but not required. Full-content guards cover these distinctions, including a newly appearing or changing credit amount. Fixed and option identities remain unchanged.
