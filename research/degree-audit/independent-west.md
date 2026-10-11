# Independent RIT and Penn State review — 2026-10-11

This is a bounded second pass of primary audits by other researchers, not a replacement primary audit or whole-degree approval. The JSON ledger records manually established course-ID sets, evidence locators, precise scope and remaining work. No seeds or adapters were changed by this review. Frontend's earlier eight-card RIT review and fixed-core Penn State review are in `independent-review.*`; this pass extends to all 40 current RIT cards and the complete named Penn State IST option union.

## Evidence method and limits

RIT's public [AI BS curriculum](https://www.rit.edu/study/artificial-intelligence-bs#curriculum) displayed 2026–27. I independently inspected the ordinary browser curriculum, fourth-year/elective rows and IDAI-490 popup. I then independently reread the complete exact card fields captured by the primary researcher through the same ordinary UI: 41 observations, 40 distinct codes, with GCIS-123 duplicated. The raw capture stays outside the repository at `/tmp/rit-degree-audit-course-captures.json`; it contains title, credit amount, description and prerequisite fields, not a seed replay. The duplicate has identical fields. The known restricted/catalog-shell route was not retried or bypassed.

Penn State's 2026–27 Bulletin program and course-description pages were independently reread from the official HTML cached by a robots-aware HTTP 200 fetch on 2026-10-11. `var/degree-independent/next-index.json` records each original URL, capture time and ignored local path. Reading another researcher's raw official-source capture is independent interpretation, not an assertion of a new fetch. Source content, not prior category labels or parser output, determines the findings below.

## RIT AI BS

The 40 current chart/menu identities partition as **23 fixed / 17 options**. Six binary sequence menus contribute 12 options: introductory programming I and II, discrete mathematics, communication, database/web software, and language technology/NLP. The AI elective menu contributes five more identities: CSCI-431; the single robotics choice EEEE-485 or CSCI-634; SWEN-566; PUBL-550. Choosing two menu options does not mean completing all five courses. Three codes present only in the conflicting advising document—CSCI-632, LING-582 and LING-584—remain unresolved, producing **43 source identities: 23/17/3**. This is the role partition of the displayed typical sequence, not proof that every possible transfer/substitution route has those exact fixed courses.

IDAI-499 occurs twice in the chart, but contributes one course identity plus a separate two-placement requirement. Zero is evidence here: YOPS-10 and IDAI-499 each explicitly carry zero credits; the uncoded co-op preparation slot also has zero published hours. All 40 card credit amounts match the seed: two zero-credit, three one-credit, six four-credit and 29 three-credit records. These are inventory observations, not a degree-credit sum. The chart's total remains 122 semester hours. A policy note without a quantified amount stays null.

All 40 descriptions support the recorded subject decisions, with meaningful distinctions across AI-titled courses:

- GCIS-123/124 and CSCI-141/142 center on programming, data structures and software construction. SWEN-261/344/566 and IDAI-490 center on software development/design/integration; foundations is defensible even when AI services are involved.
- MATH-181/182/190/200/241/251 describe calculus, discrete reasoning, linear algebra or probability/statistics. IDAI-360 begins with combinatorial, continuous and hybrid optimization before its AI applications; mathematics is defensible.
- CSCI-331/335/431/634, IDAI-101/110/202/444 and LING-581 focus on AI methods, ML, perception, robot planning or computational NLP.
- ISTE-230 covers relational models, normalization, databases, integrity and security; IDAI-485 covers concurrent/distributed infrastructure; CSEC-521 covers attacks and defenses. These are systems content.
- COMM-142/201, UWRT-150, GCIS-350, ISTE-262 and PUBL-550 center on communication, law, human interaction or policy. PSYC-101/223 center on psychology domain knowledge and remain applications.
- ISTE-476 combines cognition, visual interaction, data transformation and analytical methods; LING-351 combines historical/social language technology and computational topics; EEEE-485 combines electrical/mechanical construction, control and AI. Each remains mixed `other`, not artificially forced into AI. YOPS-10's first-year development and IDAI-499's unspecified placement content are unclassified, not reviewed subject counts.

Manual subject totals:

| Role | Foundations | Mathematics | AI/ML | Systems | Human context | Applications | Other | Total |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| Fixed chart identities | 2 | 5 | 6 | 2 | 3 | 2 | 3 | 23 |
| Current option identities | 6 | 2 | 3 | 1 | 3 | 0 | 2 | 17 |
| Conflicting advising identities | 0 | 0 | 0 | 0 | 0 | 0 | 3 | 3 |

All 40 displayed prerequisite fields were reread. Equivalents, alternatives, minimum grades, standing and co-requisites stay enrollment conditions. EEEE-346 is preparation for the optional EEEE-485 route; its absence from fixed degree rows does **not** prove a degree contradiction or a waived prerequisite. LING-581 expects programming experience or instructor approval within its description, despite no separate prerequisite field. Null elsewhere means no prerequisite was displayed, not that registration is unrestricted.

Two genuine source uncertainties remain: ISTE-476's restriction omits the AI BS while the chart includes it; CSCI-431's exclusion refers anomalously to itself alongside CSCI-631. The [same-year advising flowchart](https://www.rit.edu/computing/sites/rit.edu.computing/files/docs/IST-Information/AI%202026_0.pdf) also disagrees with current robotics/linguistics elective choices and the immersion annotation. That document's content was not independently re-audited in this pass; no resolution is claimed. GE-approved lists, writing/immersion overlap and all degree-wide policy applications still prevent full-degree verification.

## Penn State Engineering AI BS

The [Engineering Bulletin](https://bulletins.psu.edu/undergraduate/colleges/engineering/artificial-intelligence-engineering-bs/) identifies AIE_BS, ending at University Park, with a 126-credit minimum. The major table prescribes **17 fixed identities**, and its programming, ML and communication choices contain **13 additional identities**. These sets are listed individually in the ledger.

The introductory programming expression is CMPSC-131 **or the entire CMPSC-121 + DS-120 route**. Its two courses cannot be reduced to independent substitutes. CMPSC-132/122 and CMPSC-448/445 remain separate alternatives. A-I-370's alternative/concurrent preparation does not turn DS-305, CMPSC-465 or other named preparation into additional universally fixed courses.

Independently reread descriptions support A-I-305 as algorithms/data structures foundations, A-I-410 as deployment/lifecycle infrastructure, AIE-355 as optimization mathematics, MATH-225 as calculus/linear algebra, A-I-370 as AI search methods, and AIE-489W as mixed project/engineering/communication. The entire 30-course taxonomy was not independently re-audited; the ledger therefore gives independently established role counts without pretending to establish all subject aggregates.

Major102–103 plus GE45 includes21 overlapping credits, rather than implying147–148 distinct credits. Technical27 (at least15 at400-level), nontechnical3 and seminar obligations retain their source approval/eligibility language. The reviewed major page does not enumerate complete technical/nontechnical approved lists. The 2026–27 rule set does not replace the entrance-year bulletin for earlier cohorts. All approved GE options and detailed Senate policy applications remain unfinished.

## Penn State IST AI Methods and Applications BS

The [IST Bulletin](https://bulletins.psu.edu/undergraduate/colleges/information-sciences-technology/artificial-intelligence-methods-applications-bs/) identifies the separate AIMA_BS at University Park with a 120-credit minimum. I independently transcribed the full major-choice and Supporting Courses tables, including every named technical course and all nine named application focus areas. The raw union is **9 fixed + 160 option code records**. Shared A-I-494 and IST-256 observations are each one record in this union. Open CYBER level predicates and the ROTC route do not invent a closed individual course list.

The University Park business list is ACCTG211, BA301–304, BLAW243, IB303 and ECON102. The separate Commonwealth list does not add BA241/242, FIN301, MGMT301, MKTG301 or SCM301 to this University Park inventory. The research option does not flatten the capstone sequence: AIMA430 and440 form a whole six-credit route, with 440 explicitly requiring430. This is distinct from a six-credit supervised research route.

I independently reread both descriptions for each of these reciprocal cross-list pairs:

| Same course, two source codes | Official course-description evidence | Subject / individual credit amount |
|---|---|---|
| DS410 and CMPSC410 | [DS](https://bulletins.psu.edu/university-course-descriptions/undergraduate/ds/) and [CMPSC](https://bulletins.psu.edu/university-course-descriptions/undergraduate/cmpsc/) each name the other as cross-listed | Scalable/distributed programming; systems; 3 |
| DS442 and CMPSC442 | Same two official lists contain reciprocal clauses | AI reasoning/search/learning; AI/ML; 3 |
| MATH318 and STAT318 | [MATH](https://bulletins.psu.edu/university-course-descriptions/undergraduate/math/) and [STAT](https://bulletins.psu.edu/university-course-descriptions/undergraduate/stat/) each name the other | Elementary probability; mathematics; 3 |
| MATH414 and STAT414 | Same two official lists contain reciprocal clauses | Probability theory; mathematics; 3 |

Thus 160 raw option records become **156 mapped option identities**, and 169 total records become165 identities. Source records, prerequisites, credits and choice quantities are all retained. IST/ETI301 and IST/ETI302 remain two unproven slash pairs; they are **not** additional merges. PLSC418/418W is an ordinary alternative, not a proven alias. None of these observations authorizes automatically making a one-identity observed menu mandatory.

Major67 + GE45 + electives14 − GE overlap6 =120. Technical9 with at least3 at400-level and application9 with at least3 at300/400-level and no more than6 ROTC remain load/level constraints, separate from profile counts. A-I-370 concurrency and AIMA440's prerequisite remain metadata, not additional universal fixed requirements. The many supporting-course records with `other` are not independently classified by their focus label. Whole-degree GE/policy review and remaining supporting-course metadata are still incomplete.

## Verification

`tests/test_independent_west_degree_audit.py` compares every mapped role against the manually transcribed sets; checks RIT's full subject partition and conditional preparation; exercises actual RIT zero-credit storage without changing null policy amounts; checks all four PSU identity groups, raw/canonical counts, unmerged pairs and University Park exclusions; and tests the two whole-route conjunctions. Isolated temporary databases verify idempotence and foreign keys. No parser fixture or seed-derived count is treated as independent source evidence.

The new seven tests and existing nine zero-credit tests pass. An isolated temporary database containing only these three programs ingests and builds successfully with `/ai-program-atlas/` as the base path. The three programs remain partial second passes; no whole degree is certified.


## Rice policy closure pass — 2026-10-11

This pass supplements the earlier 14-source/all-43-course review in `independent-review.json`; it does not relabel that work as a new full-course audit. I independently read the complete [AI BS requirement table](https://ga.rice.edu/programs-study/departments-programs/engineering/artificial-intelligence/artificial-intelligence-bs/), relevant [COMP](https://ga.rice.edu/programs-study/courses/comp/) and [STAT](https://ga.rice.edu/programs-study/courses/stat/) blocks, and the university policies below. No primary seeds or adapters were edited.

The [registrar error table](https://registrar.rice.edu/students/common-errors) explicitly offers instructor-approved exceptions for prerequisite and mutual-exclusion registration blocks. [Special Registration](https://registrar.rice.edu/students/special-registration) and the [registration FAQ](https://registrar.rice.edu/students/registration-FAQs) corroborate prerequisite exceptions. These are conditional permission mechanisms, not evidence that permission has been granted.

- **Statistics:** the degree's STAT310/314 and STAT311/314 alternatives do not automatically waive COMP345/346's STAT315 prerequisite. Approved prerequisite exceptions can support these routes without requiring new STAT315 credit after an excluded course. STAT314 after STAT311 also needs its own prerequisite exception. These courses remain options, not extra universal fixed requirements.
- **Vision:** COMP447 is a published elective despite reciprocal registration exclusions with required COMP345. An approved registration route now has evidence. No individual additional-credit outcome is certified: [repeat-credit rules](https://registrar.rice.edu/students/reg_repeated_courses) address cross-listed/equivalent courses, but mutual exclusion alone does not establish that identity relation. Do not infer either duplicate credit entitlement or impossibility. Once this option, restriction and approval route are mapped, the absence of a case-specific approval is not an inventory blocker.
- **Residence:** [graduation](https://ga.rice.edu/undergraduate-students/academic-policies-procedures/graduation-requirements/) permits one summer in the four-semester full-time requirement. [Transfer policy](https://ga.rice.edu/undergraduate-students/academic-policies-procedures/transfer-credit/) repeats a fall/spring-only version while explicitly presenting it as a reminder of general graduation requirements. It does not identify a separate stricter transfer cohort. [Registration](https://ga.rice.edu/undergraduate-students/academic-policies-procedures/registration/) defines full-time summer enrollment but does not settle this disagreement. Both competing statements are GA text; precedence over external publications cannot choose between them.

The public [graduation preparation](https://registrar.rice.edu/students/preparing-for-graduation), [undergraduate transfer](https://registrar.rice.edu/students/transfer-credit/undergraduate) and [Degree Works](https://registrar.rice.edu/students/degreeworks) pages were also read. They describe certification and individual exceptions, without resolving the residence wording or certifying both vision-course credits. No authentication, student records or personal contact was used. Four registrar pages were preserved locally by the robots-aware Fetcher; raw copyrighted pages remain uncommitted.

Result: statistics enrollment concerns are conditional approvals; vision enrollment has a conditional approval path without a promised credit outcome; residence is the sole remaining source conflict. The independent ledger remains partial and the whole degree is not certified. These findings informed primary correction `0ef4a05`.


## Northeastern AI and Mathematics BS — independent source pass

Reviewed 2026-10-11 against primary commit `da25629`. The complete [Boston degree panel](https://catalog.northeastern.edu/undergraduate/computer-information-science/computer-information-science-combined-majors/artificial-intelligence-mathematics-bs-bos/) and all 34 represented official course blocks were independently read from the preserved normal-fetch originals. The JSON ledger contains literal manually assembled code/role/category/credit decisions. Cached-source review dates are separate from original fetch timestamps.

The baseline fixed set is 20 identities: CS2000/2001, CS2100/2101, CS3200, DS3500/3000/4200/4300, nine named MATH courses, and integrative DS4400/4420. The named option set is 14: five college-dependent seminar/professional courses, EECE2160/2322/2323 and MKTG4606, plus five writing alternatives. Open subject-number electives are rules, not an invented finite pool. The placement exception remains separate from this default curriculum.

Content supports **5 foundations / 10 mathematics / 2 AI / 2 systems / 1 other** in the fixed set, and **2 systems / 5 human context / 1 domain application / 6 other** in options. [DS3000](https://catalog.northeastern.edu/course-descriptions/ds/) teaches mathematical foundations; DS4200 mixes visualization design, perception and programming. [CS3200](https://catalog.northeastern.edu/course-descriptions/cs/) concerns databases, while DS3500 emphasizes software construction. [EECE2160](https://catalog.northeastern.edu/course-descriptions/eece/) mixes embedded hardware and programming; EECE2322/2323 center on architecture and hardware. [MKTG4606](https://catalog.northeastern.edu/course-descriptions/mktg/) is a business application practicum. Orientation and career preparation do not become computing foundations.

[Mathematics descriptions](https://catalog.northeastern.edu/course-descriptions/math/) distinguish MATH1342's prior course or adviser permission from merely recommended Calculus2 preparation in2321/2341. [Writing descriptions](https://catalog.northeastern.edu/course-descriptions/engw/) establish the five communication courses and their eligibility. Alternative prerequisites do not become extra universal obligations. Exact one-hour labs/seminars remain separate from four-hour lectures.

The eight course-bearing family bindings match the individual catalog, including the local integrative placement of DS4400. CS1800/1802 are not added merely because they occur in other family variants or prerequisite alternatives. The resolved graph retains all 34 identities, with no unresolved mapped records.

The six shared university policies were read for Boston BS applicability: [university minima](https://catalog.northeastern.edu/undergraduate/university-academics/university-wide-requirements/), [NUpath](https://catalog.northeastern.edu/undergraduate/university-academics/general-education-requirements/), [experiential learning](https://catalog.northeastern.edu/undergraduate/academic-policies-procedures/experiential-learning-graduation-requirement/), [graduation](https://catalog.northeastern.edu/undergraduate/academic-policies-procedures/graduation-requirements/), [combined majors](https://catalog.northeastern.edu/undergraduate/academic-policies-procedures/degrees-majors-minors/) and [progression](https://catalog.northeastern.edu/undergraduate/academic-policies-procedures/progression-standards/). BA, NYC and nursing-specific provisions are not inherited. NUpath permits competency overlap and does not supply a fixed universal course list.

The [Science catalog](https://catalog.northeastern.edu/undergraduate/science/), [Science advising page](https://cos.northeastern.edu/college-of-science-life/advising-student-resources/) and [Khoury policies](https://www.khoury.northeastern.edu/current-undergraduate-students/undergraduate-advising-academic-support/academic-policies-and-procedures/) confirm college-specific rules and adviser-mediated designation. Exact permitted/designated home-college applicability remains unresolved; Science's detailed change-home route requires university sign-in. No restricted resource was accessed. This prevents a full-degree second-pass claim.

The source states 130 overall hours,24 general-elective hours,12 Khoury elective hours and four MATH electives/16 hours. Summing all blocks as disjoint would yield 136, but the source does not establish that disjointness or an exact overlap schedule. Neither136 nor a speculative subtraction replaces the published 130. These remain separately stated constraints, not a new contradiction or a computed student load. No seed or family changes were needed.
