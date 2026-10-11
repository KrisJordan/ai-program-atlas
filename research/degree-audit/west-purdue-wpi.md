# Eight-degree correctness review — 2026-10-11

Three records are **in progress** because accessible course-content review remains unfinished; UC Merced and Furman remain **blocked** at their unavailable detailed curricula. Both WPI degrees are now **blocked** only by specific policy questions after their represented course-content reviews finished. Genuine policy/access blockers coexist with the three ongoing audits, but do not conceal accessible work. This is not a claim that all accessible course descriptions were reviewed. The JSON ledger records specific source gaps and conflicts separately from the remaining accessible course-content review backlog. Earlier curriculum completeness labels and successful parsers do not establish a completed degree audit.

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

**WPI:** general HUA transfer B− language conflicts with language-specific B/C thresholds and a later B− recommendation. Registrar graduation dates/deadlines differ from the catalog. The AI Business Applications and Social Science/Policy minimum-allocation rules have been rechecked and are compatible with their six-course totals. Business AI references a graduate-course count limit that is not supplied; a graduate double-count percentage is not an equivalent rule. FIN2070's section label differs from its linked course-row title; the current individual course page now verifies the row identity and finance subject, so that naming context is no longer an unidentified-course blocker. The actual policy conflicts are not reconciled by assumption.

**UCSD:** tentative department versus catalog CSE191 eligibility, Roosevelt residence/MMW transfer differences, Revelle transfer humanities/science formulations, Marshall language eligibility, Seventh CalGETC applicability, and separately documented AP/IB/Chinese-course credit discrepancies remain. Legacy Warren discipline hosts stopped at robots redirects. The graph correctly retains conditional college/cohort scope despite these unresolved decisions.

**UCSB:** CMPSC41 five/four-unit disagreement, science ListsA/B membership, capstone identity, dynamic approved GE pools, ELWR wording and Engineering CalGETC applicability remain unresolved. Current GEAR supplies 72 upper units and 8/12 science allocations; it does not supply the missing memberships or resolve the CMPSC41 conflict.

**UC Merced:** the permitted official overview supplies a BS identity and aims, not named requirements. The officially linked current catalog returned403. **Furman:** the official directory verifies undergraduate BS identity, but its AI detail page is password protected; activity and curriculum remain unknown. No different program's curriculum is borrowed.

Independent second-pass review remains pending for all eight entries.

## Current WPI course follow-up

Seven actual current catalog pages were read through the robots-aware client on 2026-10-11 (HTTP200): CS2223, MA2611/2612, DS1010/2010/3010 and FIN2070. All explicitly publish 1/3 WPI units. CS2223 is foundations; MA2611/2612 mathematics. DS1010 remains mixed programming/mathematics/AI. DS2010 now has a defensible AI/ML focus from its learning-method and prediction workflow description. DS3010 remains mixed, with corrected systems/AI candidates rather than inferred mathematics. FIN2070’s current full heading is Risk Analysis for Decision Making; its description teaches finance, valuation and investment risk. The program slot label Fundamentals of Finance does not contradict that course identity. Its subject is applications.

The WPI AI fixed set is unchanged at six identities: one foundations, two mathematics, one AI/ML and two mixed other. FIN2070 remains an option in both degrees, and DS2010 remains an option in Business. Recommended Background text, including explicit None for DS1010, remains advisory rather than new degree prerequisites. FIN2070 has no displayed background field; that absence remains unknown. No course or requirement count changes. The complete source/credit/background guards emit observations only and stop on changed title, content, units or catalog edition. Accessible unreviewed WPI course pages remain queued; justified HUA, graduation-timing, graduate-count and concentration-allocation questions are retained.

## Completed WPI Business content inventory

The current program distribution and all **49 represented course descriptions** were read: 47 options and two contextual HUA records. The observed partition remains zero fixed / 47 options / two contextual. The options independently comprise four foundations, eleven mathematics, six AI/ML, three systems, three human-context, seventeen applications and three mixed records. HU3900/3910 are human context. Every reviewed course explicitly publishes 1/3 WPI units. Full course-page guards include descriptions, credits, recommended and suggested background, eligibility and credit restrictions. Runtime parsers emit observations, never manual category reviews.

The two HUA pages establish five prior HUA courses, including two thematically related and one at 2000 level or above; HU3910 additionally requires instructor consent. The degree's three-course depth rule applies before the seminar/practicum; its stronger condition is compatible with the generic course-entry minimum of two. They remain contextual courses. Credit exclusions are retained as restrictions, not cross-list identity evidence. OIE4430's suggested mathematics preparation is advisory. FIN3330 centers on learning algorithms and is AI/ML; optimization and simulation courses with substantive mathematical methods are mathematics. Business subject membership alone determines neither classification.

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

## Life science and chemistry options reviewed

Twenty-eight complete 2026–27 course pages add 26 domain applications and two mathematical-methods decisions. AI coverage is now **144 of 219 represented records**: six fixed, 136 options, two contextual; **75 accessible option descriptions remain unreviewed**. All 28 explicitly publish 1/3 WPI unit. Role sets and choice quantities are unchanged.

Biological agents, neural physiology and software-assisted biological analysis are classified from their substantive domain descriptions, not terminology resembling AI. CH4210's brief description specifies AI applications in molecular life sciences but no learning algorithms; applications is the supported subject. CH3520 and CHE3501 explicitly organize mathematical tools, modeling and equation-solving and are mathematics. Physical chemistry, biology and chemical-process design remain substantive domain applications.

CHE2011/2012/2013 credit restrictions are expressly limited to CHE distribution requirements; the notes retain that scope rather than inventing a universal no-credit rule. Background preparation stays advisory, with CH2310's assumed general-chemistry familiarity noted separately. All full descriptions and associated fields are guarded. Genuine degree policy gaps remain separate from the remaining accessible work.

## Built-environment and engineering science options reviewed

Thirty further complete pages bring AI coverage to **174 of 219 records**: six fixed, 166 options, two contextual; **45 accessible option descriptions remain unread**. Twenty-six courses teach substantive architectural, civil or physical engineering practice; ENV2720's environmental/social AI critique and ENV2900's alternative-development policy analysis are human context. Generic ENV2800/4800 offerings remain unclassified after reading their entire descriptions because topics vary by offering. That is explicit source uncertainty, not an unread-page backlog.

Twenty-eight pages publish 1/3 WPI unit. ENV2800/4800 instead state an instructor-assigned **1/6–1/3 unit range**. Their fixed numeric credit stays null and the range is retained; it is neither zero nor an assumed endpoint. Both allow repetition for different topics. ENV4800's preparation is an inline recommendation, and any particular offering still needs the degree's AI-relevance approval. CE3051 says prior traffic-engineering knowledge is helpful but not required. Full-content guards cover these distinctions, including a newly appearing or changing credit amount. Fixed and option identities remain unchanged.

## Represented WPI AI course inventory closed

All **219 represented course descriptions** have now been read. The final partition remains **six fixed / 211 options / two contextual**. The options independently comprise eleven foundations, twenty-eight mathematics, twenty-two AI/ML, fifteen systems, eighteen human context, eighty-seven applications and thirty other. Across all records there are 187 single-category reviews, 22 mixed reviews and ten explicitly unclassified generic topics. No known unread represented course block remains. The AI degree audit is now **blocked** by two specific policy applicability questions, not by reading workload.

The final forty-five records distinguish AI methods for game agents from critical literacy, ethics and technology policy; substantive game design, finance and empirical psychology remain applications. Generic economics and psychology topics remain unclassified until their actual offering is known. All four economics topics publish 1/3 unit; the four psychology topics publish no amount. The PSY2411 credit exclusion is specifically for the PSY2800 Social Neuroscience offering, not all PSY2800 topics.

The ordinary graduate catalog search resolved IMGD5100/5300 to their full descriptions. Their native three graduate credits are consistent with the undergraduate Experience Design table's half-unit values under the separately documented conversion. Course records now cite the native source and retain unknown normalized type/edition, not invented semester credits. In total, 191 records publish fixed 1/3 WPI unit, twenty-two publish native three graduate credits, two publish variable 1/6–1/3 unit ranges, and four psychology topics publish no value.

Two earlier supposed concentration blockers were overstated. Business explicitly requires six total with **at least** 2/1/1 from three listed pools; Social Policy requires six total, both named psychology courses, **at least** three from its listed pool, and a 4000-level floor. These are compatible minima and inclusive totals, already preserved by the graph. They do not create unidentified free electives. Those audit blockers are removed. No named-course role or choice quantity changes.

A related prose correction: the HUA degree policy requires three related courses **before** the seminar/practicum, while the generic HU course pages state a minimum of two. The course minimum does not waive the stronger degree-path pre-seminar condition. Earlier shorthand describing the three-course condition only as a graduation rule was imprecise; the graph's actual HUA policy remains correct.

The two genuine remaining AI questions are the HUA page's general B− versus language-specific B/C transfer thresholds and the catalog/registrar graduation timing discrepancy. Business separately retains its referenced but unstated graduate-course count limit. Offering-specific topic eligibility and missing course fields remain explicit limits, with no arbitrary invented approvals or prerequisites. Whole-degree verification and independent second pass are not claimed.

## Bounded Purdue canonical-content follow-up

Eleven distinct full departmental outlines were read: CS10100 for BA; CS18000/18200 for both; and CS34800/37300/38100/44800/47100/48300/52300/57700 for BS. This adds seven previously undescribed BS course records and rechecks the four previously described identities. The directory calls these faculty-approved canonical syllabi but explicitly marks CS48300 **proposed**. The pages report June 20, 2025 updates; some contain much older explicit outline dates (1998.08, 2004.08 or 2005.12). These are useful dated content evidence, not current Fall-2026 catalog equivalences. Full-page guards protect both topics and dated context; no credits, current titles or fresh manual review status are fabricated by the parser.

CS34800's database outline establishes systems. Algorithms and computation theory remain foundations; databases systems; explicit AI/NLP learning methods AI/ML; security law/economics human context. CS10100 and CS18200 remain mixed from their full scope. Only CS18200 publishes a prerequisite in these outlines, and its dated CS18000 condition is retained as such. Existing degree-source credit values are not inferred from these credit-free outlines.

The actual **Fall 2026 West Lafayette** directory lists CS17600 Data Engineering In Python and CS24300 Artificial Intelligence Basics. Both detail links lead to the previously robots-disallowed selfservice host, which was not retried. Neither has a canonical-directory entry. Search snippets from denied catalogs were not used as full-description evidence. BA keeps the older department-plan titles with this explicit current-directory distinction; current full descriptions and title-version reconciliation remain unverified.

For the five represented BA records, no known unread publicly linked description branch remains after this bounded check: three dated outlines are inspected and the other two detail sources are unavailable. BA returns to **blocked** for these precise gaps and its inaccessible philosophy/current college inventory, without claiming exhaustive web absence. BS remains **in_progress** for its much larger accessible named/contextual course backlog.

### UCSB independent department-content closure — 2026-10-11

Ordinary public navigation from the AI site's department link led through the CS course overview to its [course-description directory](https://cs.ucsb.edu/education/courses/course-descriptions). Thirty-five exact existing codes have actual detail pages; all full course/eligibility blocks were read. The ignored cache index preserves original fetch timestamps and hashes. No known denied catalog route or loading shell was worked around.

Manual subject dispositions:11 foundations,12 systems,4 AI/ML,2 mathematics,1 human context,1 graphics application,1 mixed HCI and3 unclassified (historical184; variable research/project192/196). Numeric cryptography and computational-science methods are mathematics; advanced general programming is foundations; IoT infrastructure is systems. None follows an elective role or AI degree membership. All19 fixed identities remain unchanged; the65 options now divide into8 foundations,12systems,2mathematics,1AI,1human context,1application and40other. Two writing contexts remain separate. Thirty-three observed courses are four quarter units; project/research ranges remain null. Prerequisites, consent alternatives, concurrent enrollment, credit exclusions and recommendations do not add fixed obligations.

The CMPSC184 page explicitly says Fall2017 and publishes no substantive description. Other34 detail pages are undated, not certified as2026–27. Current AI eligibility for undated CS/CE-only rules remains unverified. Explicit CMPSC153A/ECE153A andCMPSC181/ECE181 same-course statements warrant a paired-source identity check next; no slash-based grouping was added. Nine new AI codes absent from this directory and remaining mathematics/ECE/writing/humanities descriptions require bounded follow-up. The degree stays `in_progress`; actual unit/science/capstone/GE/access conflicts are unchanged.

The [Mathematics department](https://www.math.ucsb.edu/undergraduate/undergraduate-course-descriptions) independently supplies the full five fixed mathematical descriptions and their prerequisite chains. All five are mathematics; no role/category counts change. It states no units, so the parser does not overwrite degree-source amounts. Login-only linked study resources were not accessed. The [ECE2026–27 schedule](https://www.ece.ucsb.edu/undergrad/courses), updated September18,2026, was read but publishes no full descriptions/reciprocal cross-list statements and directs prerequisites to the catalog. Availability markings are not absence or degree-eligibility findings. Current paired-source identity review remains open.

The [upper Writing Program page](https://writing.ucsb.edu/courses/upper-division-and-specialized-courses) and [lower page](https://writing.ucsb.edu/courses/lower-division-courses) were read in full, including shared prerequisites and unit declarations. They provide25existing code blocks:19upper and6lower, with2ELWRcontexts already reviewed earlier. All65options remain options; manual subject counts are now8foundations,12systems,2mathematics,1AI,23human context,1application,18other. Writing105AI is communication rather than technicalAI methods;105CDgenuinely combines writing and code. WRIT2is5units,2E4. WRIT107EP's explicit former109ESdesignation is preserved without creating an unsupported current cross-list group. This leaves21represented codes needing exact current descriptions/version follow-up:9newCMPSC,5ECE,1ME,2comparative-literature/German,3English andlegacyWRIT109ES. Whole-degree progress remains `in_progress`.

WRIT1 follow-up: the previously cached, actually reread [individual guide](https://writing.ucsb.edu/writing-requirements/required-writing-courses-guide/writing-1) states4quarter units; the independent lower-division overview states5. Both are undated. The curated record and contextual rule now preserve this as an unresolved source conflict with null credits; source observations retain their individual values. No precedence is inferred from which page was inspected later.

The alternate official [images-path2026–27GEAR](https://engineering.ucsb.edu/sites/default/files/images/26-27_GEAR.pdf) was normally fetched and its AIrequirement/sample-plan pages visually read. Its whole-file hash differs, but all four previously reviewed applicable PDFpages13/14/16/17have identical whitespace-normalized text. The CMPSC41five/four-unit discrepancy and unspecified scienceListsA/Bremain; no capstone identity appears. ExistingCMPSC190AA–ZZopen criterion is already represented. This accessible comparison is completed rather than retained as a backlog item.

English exact-code closure adds three represented dispositions from five full offering pages. The main department publishes historical146AIWinter2021and146DSWinter2023(the146AIURLmislabels spring) and threeFall2026ENGL197literary/cultural seminars. Their observed subjects arehuman context; actualprerequisites areunpublished here(CheckGOLD), unitsunstated. The current65options now have26human-context and15other; allrolecounts unchanged. Current applicability of the historical versions remainsunverified. DistinctFall2025ENGL155AIwasread butnot substituted. This work used the permitted main department host; robots-disallowedTranscriptions wasnotretried. MEcourse-content route pointsCanvas, andtheindependentlylinked publiccourse-searchrobots redirects toregistrarhelp, so no protecteddatawere accessed. Eighteen representedcode descriptions andexactversion/identityquestions remainactive/blocked as individually recorded; whole-degreein_progress remainshonest.

### UCSB current catalog: reciprocal Critical AI identity (2026-10-11)

Ordinary rendered 2026–27 catalog pages for GER155 and C LIT155 were individually
read, including the full description, fixed four-unit amount, Area E and advisory
same-course statements. Both expressly name the other code and ENGL155AI. The
existing two represented codes therefore form one verified identity; historical
ENGL146AI is not included. The humanities-centered critical analysis supports
human_context. No published prerequisite field means unknown, not no restriction.

Manual option accounting: prior65 code observations, minus one reciprocal alias,
yields64 identities. Two formerly unclassified code observations become one
human-context identity: human_context26→27 and other15→13. Fixed19 and contextual2
stay unchanged; all86raw code records remain. The reviewed course-ID lists now
use the canonical C-LIT155 identity. Seventy represented codes have bounded
content dispositions; the16 remaining code descriptions and newly accessible
catalog policies/pools remain active work. No whole-degree completion claimed.

### UCSB current CS/ECE/ME records and role correction (2026-10-11)

Sixteen complete current course pages add13new code dispositions and refresh3.
Manual taxonomy follows the actual descriptions: introductory1AsurveysAItechniques;
25teaches programming/data workflows;42formal computation;135mathematical foundations;
183ethics with practical tools;184softwaredevelopment;139probability;153Aembedded
systems;180/181/186/187andME107learning/visionmethods. No inherited prerequisites
become extra degree requirements. Recommendations and consent alternatives remain
explicit, and missing prerequisites remain unknown.

Reciprocal153Aand181identities are now verified. For181the current degree expressly
requires the course under either alias, so the graph's local rule isalland one
canonical identity isfixed. Starting19fixed/64options/2context: remove both181options,
add one fixedidentity, and deduplicate153Aoptions→20/61/2. Rawcounts21/63/2still sum86.
No automatic one-member-pool promotion is used. Current181AI-major admission is
explicitly allowed; other narrowed major restrictions remain exact policy questions.
Science approval lists remain department-referred; currentprogrambody has two opaque
references. Three exactcode descriptions plus broader accessiblecatalogreview remain,
so whole-degree status isin_progress.

CurrentWRIT109ESfull description closes its accessible content gap: professional
writing establisheshuman_context,4units, explicit prerequisite andEnglish109Icredit
restriction. No automatic renumbering merge with107EP. The currentcatalogsearch
`CMPSC189`returnsA/Bonly and no exactC/Drecords; these two represented worksheet
codes remain unknown rather than replaced. Eighty-four of86coursecodes now have
bounded content dispositions. Optionhuman_context27→28andother7→6; all role and
identity counts remain20/61/2. GE/current-version/approval-policywork remainsactive.

### UCSD CSE contribution integration and core eligibility repair (2026-10-11)

Coordinator-read82full descriptions and6missing exact-heading dispositions were
integrated from the guarded manifest, with author/scope distinguished from the
primary review. The original8CSEcoredescription blocks were independently reread
for eligibility and credit clauses; all suffixes now remain intact rather than
being truncated at a semicolon or sentence. CSE100preparation remainsrecommended,
151A/COGS188credit exclusion remains explicit, and25/55majorpriority includes its
space-permission exception. No prerequisite becomes a new degree obligation.

Manual existing role sets remain8fixed/119options/2241context. Their subject
composition now reflects82actual descriptions; six exact missing codes remain
unknown. No crosslist identities or contextualcollegeeligibility were inferred.
The code-set partition is unchanged and the composedsource retains existingtags.
Non-CSEchapters and policy applicability remain active accessiblework.

UCSB fixed-course version follow-up:11full current records (sixCS/fivemath) close
current-source review for all20fixedidentities. No role or category counts change.
CMPSC188has explicit current prerequisites unlike the oldundateddepartmentpage.
CMPSC130Aprobabilityis listed in both preparation and prerequisitefields, retained
literally. Calculus conditionalcredit/AP/repeatrules and alternate mathpreparation
remain distinct from ordinaryfour-unit values and from degreecourseobligations.
Currentoptionalversions, approvalmechanisms andGEpoolsremainactivework.

UCSB publicapprovalpolicy closure: actualcatalogRegulation10 andRegistrar quarterly/
course-registration bodies were fullyread. They establish preparednessdiscretion,
late-addcodeapproval, repeatedprerequisitechecks and optionalgraduateenrollment
conditions, but not a blanketAImajor waiver. Exact college applicability is retained
for graduatecoursecredit/deanapprovalrules. Fourguardednote nodes contain no course
references or additionaldegree-load assumptions. Major-restrictionapplicability is
still an evidence question, not inferred impossibility or automatic permission.


### Current English version closure (2026-10-11)

The ordinary current catalog records for ENGL 146AI, 146DS and 197 were read
in full. Each gives four units and explicit writing/standing prerequisites.
146AI studies literary and philosophical questions about artificial entities;
146DS studies narrative/media theory and data storytelling. Their classifications
remain human context, independently of their AI or data titles. Current evidence
replaces the earlier dated offering metadata without treating those older pages
as a fresh catalog version or merging 146AI with the separate 155AI identity.

The current generic 197 description establishes a variable seminar and library
research project, not a universal seminar subject. Its metadata parser therefore
omits category; the retained manual human-context classification is explicitly
limited to the three separately read Fall 2026 offerings and does not certify
future topics. Exact repeat limits and writing alternatives remain in the
observed eligibility field. Roles, aliases and 20 fixed/61 option/2 contextual
identity counts are unchanged. Remaining optional-course versions, approved GE
pools and specific AI enrollment exceptions remain accessible audit work.


### Current GE policy and published-pool discovery closure (2026-10-11)

Full visible sections of the current [GE program](https://catalog.ucsb.edu/pages/rPLy4cgKMOtJPnaDpVTT#satisfying-general-education1)
and [Engineering GE policy](https://catalog.ucsb.edu/pages/XKpjtzsyizq40mvKrD0E)
were read through ordinary public navigation. The all-college policy expressly
recognizes certified full Cal-GETC and links Engineering. This supersedes the
earlier unresolved local-applicability finding; no inference from GEAR’s older
IGETC wording was necessary. Partial certification requires no more than two
missing courses and college consultation. The source still says IGETC areas1–6
in that combined paragraph; its separate three-course STEM exception names
IGETC only and is not extended to Cal-GETC. No major or other university waiver
is inferred from GE certification.

Engineering uses two D, two E, one F and one G courses, with four writing, one
ethnicity and one European Traditions-or-World Cultures designation as overlays.
Major and American History overlap are permitted; a course may serve only one
A–G general area even when multiple area tags are published. The permission to
petition two other UCSB writing courses on the special-subject page belongs to
Letters and Science, not Engineering’s separately documented UCEAP exception.

The linked course-search filters and ordinary Export all results CSV establish
856 distinct published D/E/F/G code rows: D175, E299, F168, G273, with overlapping
tags retained. The ignored CSV and visible filter capture are preserved. The
new `ucsb_ge_catalog_pools` manifest/helper records only exact code/title/area
membership with a full source-row hash; it does not certify hundreds of unread
descriptions, assign subjects from GE tags, or emit degree requirements. Its
pool integration and content review remain an explicit accessible queue. The
HTML loading shell alone cannot refresh this CSV-backed observation.

One current source-list inconsistency remains: the Engineering-specific Area A
list includes105AI and W105M/W107B/W107L/W107WC/W109ST, while the general-area
page’s Engineering-only list omits them. Preserve both source observations; do
not silently drop existing105AI or merge online codes by label. Whole-degree
status remains in progress, with science/capstone, credit/version and remaining
GE course-content issues separately listed.


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


### Current entry-writing field review (2026-10-11)

Full current WRIT1/1E catalog records were read. They publish5/4units respectively;
WRIT1’s curated units remain unknown because the separate undated individual
Writing Program guide still publishes4, with no explained version relationship.
The new5-unit observation is guarded independently instead of erasing the conflict.
Both descriptions concern academic rhetoric and writing. Current1E eligibility
is freshmen in ECE, Chemical Engineering, Mechanical Engineering or Computer
Engineering only; the AI major is not named. A broad course title or college GE
listing does not independently establish an override. Both records’ AWPE<=6
wording is preserved alongside the separately reviewed current university CWP
and transfer-only AWPE policy, rather than imposed as a universal exam rule.
No required/option/context role changes or course-identity merges were made.


### All represented writing choices: current-version closure (2026-10-11)

All23 remaining represented writing course pages were read in full through
actual directory links, bringing all26 represented WRIT records to current
catalog evidence. Current WRIT50 publishes5units versus4in the earlier undated
department page; both observations remain guarded and curated units are null.
Current2E/50E specify freshmen and ECE/ChemE/ME/CE only, rather than a generic
Engineering restriction.105CW/105SW/107WC explicitly allow encoded AP, IB and
waiver alternatives; the exact source codes remain unexpanded.107G and107M
have term-bounded prior-course credit exclusions.107WC’s legal-repeat statement
is not treated as a cross-list identity. The older107EP “formerly109ES” statement
is retained as a version note without merging two currently published records.

Current descriptions confirm22 human-context dispositions and the mixed writing/
coding105CD record in this batch; no category or role totals change. The five
online codes named by the college-specific Area A page still need exact local
list/identity review, and hundreds of GE pool descriptions are still unread.
Current-version review of these26 records does not certify those other branches.


### Computing option versions and explicit verification barrier (2026-10-11)

Nineteen additional current CS records were read in full through observed
directory links. Their content confirms existing manual categories.132publishes
recommended preparation but no required-prerequisite field; do not restate the
older “none” observation as a current fact.134requires130B atB or better, and172
explicitly permits departmental consent beyond its named-major restriction.
Term-bounded190A/189A credit exclusions, legal-repeat clauses, concurrent routes
and recommended preparation remain distinct. No required/option roles changed.

Normal navigation to the observed current CMPSC177 link then presented a human-
verification challenge. Work stopped without clicking Begin, solving a challenge
or using another transport. Current177/178/180/185/186/192/196versions now have
that concrete access barrier; their earlier public departmental descriptions
remain version-limited evidence. Current189C/Dexact identities were absent from
the prior bounded directory/search inspection, a separate source-identity gap.
The already downloaded856-row GE export remains available for actual content
review, so the overall degree audit remains in progress rather than hiding that
accessible queue behind the new browser barrier.

### UCSD delegated SOCI / ANTH / ANSC integration — 2026-10-11

The contributor read all 157 available blocks for 162 represented identifiers in the 2026–27 Sociology and Anthropology chapters. Primary integration checked exact block guards and significant credit, eligibility and taxonomy cases, retaining 155 approved current observations and seven held/missing dispositions. The source-specific contribution notes document the original summaries and manual taxonomy rationale. This bounded integration is not a full independent second pass.

The two source contributions preserve 139 human-context, six applications, four mixed and six topic-dependent unknown observations. SOCI 171 and ANSC 190GS have unresolved substantive title/region differences; five other identifiers have no exact current heading. SOCI 194's separate internship is not added to its four units, ANTH 196B's B+ condition remains exact, and conditional admission rules remain attached to their own courses. Expected category counts were recalculated only within the previously independently enumerated role-ID sets: **8 fixed / 119 options / 2,241 context**, with no graph change. Further accessible chapters remain active work.

### UCSB cached GE linguistics closure — 2026-10-11

All15LING/LING W complete exported rows were manually read and integrated into exact D/E/G memberships. Thirteenhuman-context/twomixed classifications have individual rationales; allunitamounts are source-read. The expected options set is the prior61 reviewed identities plus15 new exact source identities, now76; fixed20/context2unchanged. Overlapping area memberships and online variants were not collapsed or summed into degree load. The source exports only prerequisiteYes/No flags, so exact rules remainunknown; fourYes flags are explicitly retained. Individual-page follow-up is blocked by the observed verification challenge, while remaining841cachedrows are accessible ongoing work. No whole-degree audit promotion.

### UCSD ETHN integration — 2026-10-11

Delegated source review read88current ETHN descriptions; seven represented identifiers lack exact headings. The primary checked consequential mixed/unknown and eligibility examples, then replayed guards that include the actual unclassed110description and paired duplicate180/184/185A source blocks.81human-context/5mixed/2unknown observations were integrated, with all seven missing-code dispositions retained. Expected categories were recomputed within the unchanged manual8fixed/119options/2241context sets. Selected topics and combined repeat-credit ceilings do not become automatic pool eligibility or course-unit amounts. No full-degree or independent-second-pass completion claim.

### UCSB delegated Art History integration — 2026-10-11

All57ARTHI/ARTHIW rows were read by the delegated reviewer; primary independently checked eight consequential content/eligibility examples and replayed exact guards. Their manual dispositions are55human-context/1applications/1mixed, with exact17five-unit/40four-unit amounts. Exact prerequisite rules remainnull because40Yes/17Noflags carry no rule text. Advisor restrictions remaincourse-scoped. The previous76option-ID set plus57new identities gives133options, fixed20/context2unchanged. Overlapping areas do not multiply identities. Online same-course6F evidence is retained explicitly while identity normalization remains unresolved; no invented crosslist declaration.72GEexportrows now reviewed/integrated,784remainingaccessible contentrows still active.
