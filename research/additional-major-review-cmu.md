# CMU AI additional-major correctness review — 2026-10-11

Scope is the **Artificial Intelligence, Additional Major** and its own eligibility, requirements and course-entry conditions. This is not the BSAI or a certification of a student's primary degree. The SCS overview explicitly permits Carnegie Mellon students to pursue an SCS additional major subject to course availability and room in their schedules, advisor consultation and the particular program's declaration rules. No primary BA/BS award or home college restriction is inferred.

The seven official sources were read from the verified robots-aware Fetcher captures listed in the adjacent JSON. Raw bodies remain in ignored `.cache/additional-cmu/0.html` through `6.html`; the JSON records exact URLs, editions, fetch/review dates, SHA256 hashes and locators. The first capture is the complete program page; the next five contain all 61 current course descriptions; the last is the SCS eligibility paragraph. Search popup routes were not fetched because the catalog disallows them. No blocked source was retried or bypassed.

## Independent requirement interpretation

The explicit required-courses directive, the Prerequisites table and unqualified mathematics rows establish **15-112, 21-122, 21-241, 36-401** as fixed. These exact rows now use `all`; parser guards reject different identities or OR additions. This correction is independent of generic pool size. The five CS courses and two AI core courses are also fixed. Thus the exact eleven are:

`15-112, 15-122, 15-150, 15-210, 15-213, 15-251, 07-280, 07-380, 21-122, 21-241, 36-401`.

The five mathematical subject groups include two genuine OR groups (calculus and mathematical proof), three fixed single-course groups, plus a distinct choose-one probability branch with six children. Probability allows `36-218`, `15-259` taken Spring 2024 or later, or one complete pair: `21-325 + 36-226`, `21-425 + 36-226`, `36-225 + 36-226`, `36-235 + 36-236`. The four pairs each have source-stated **18 units** on the sequence node; each constituent's **9 units** was separately verified in the course directory. Repeated `36-226` is one course identity across three routes. “Six mathematics courses” is the source's subject label; a two-course probability route may make seven actual mathematics courses. No universal course or unit total is inferred.

AI clusters require four selections, one per pool: Cognition and Action has six options; Machine Learning twelve; Perception and Language six; Human-AI Interaction four. Ethics has four and Human Cognition five. Mathematics supplies thirteen distinct choices: two calculus + three proof + eight distinct probability identities. Together these are **50 distinct option records**. These counts describe available mapped identities and do not add to elective load.

Admission separately requires the exact listed prerequisites and a B average; 07-180 is recommended before 07-280 and explicitly not required. At most five CS-core/AI-core/AI-cluster courses may double count toward all other majors/minors combined. Mathematics, ethics and human cognition may double count without restriction; 36-402 stays under the five-course cap as a Machine Learning Cluster elective. Substantial overlap requires consultation. These are policy notes, not automatic waiver or graduation logic.

## Manual classification arithmetic

Course content was read individually rather than inherited from cluster labels. Exact IDs for all roles are recorded in JSON. The following manually enumerated subject sets give the independent expected profile:

- Fixed **11**: foundations **5** (`15-112, 15-122, 15-150, 15-210, 15-251`); systems **1** (`15-213`); AI **2** (`07-280, 07-380`); mathematics **3** (`21-122, 21-241, 36-401`).
- Options mathematics **15**: `21-112, 21-120, 21-127, 21-128, 15-151, 36-218, 15-259, 21-325, 36-226, 21-425, 36-225, 36-235, 36-236, 10-425, 36-402`.
- Options AI **14**: `15-482, 15-494, 16-350, 16-362, 10-403, 10-417, 10-418, 10-423, 10-424, 11-441, 11-485, 11-411, 11-492, 16-385`.
- Options human context **5**: `16-467, 16-161, 16-735, 17-200, 80-249`.
- Options applications **7**: `15-386, 16-384, 15-387, 85-110, 85-408, 85-413, 85-421`.
- Options mixed/other **9**: `10-405, 10-414, 10-422, 11-442, 15-463, 05-317, 05-318, 05-391, 85-213`.
- Unresolved membership **0**. Mixed content is distinct from unresolved role and from unreviewed classification.

Optimization and advanced statistical modeling remain mathematics; neuronal computation and natural perception are psychology/neuroscience domain applications; robotic kinematics is mechanics. Human-robot interaction centers interaction psychology and study design. The mixed courses preserve substantial systems/AI, mathematics/AI, vision/imaging, human/design or psychology/AI content without assigning fractional counts. Individual rationales and candidate categories are in `reviewed_courses.json` and the program's category reviews. No cross-list identity merge was inferred from ordinary alternatives or shared codes across program records.

## Eligibility, versions and limits

All formal prerequisite fields, individual units and conditional entry prose were inspected. Omitted fields remain unknown. Extra prerequisite chains do not become fixed additional-major requirements. Explicit no-prerequisite language is retained for 16-467. Conditional notes preserve CS-freshman restriction for 15-151, MCS intended audience for 21-128, synchronous/waitlist/priority rules for 05-391, undergraduate-only 16-385, recording authorization policy for 10-423, prose preparation for 16-350/362 and 10-424, ML co-requisite prose for 10-405, and concurrent programming enrollment for 85-213.

The listed 36-235/236 route does not override the course descriptions: 36-235 requires Statistics major/minor status, sophomore standing and no excluded previous probability credit; 36-236 permits Statistics majors/minors and qualifying CS majors. These restrictions affect individual feasibility and are recorded rather than silently assumed satisfied. 36-218 direct entry to 36-401 needs at least B for non-Statistics majors/minors; Statistics students must take 36-226. Other listed grade progression conditions remain explicit. 36-401's Fall offering header and prose reference to a spring SCS section are both retained. 21-325's recommendation sentence and formal proof-course OR prerequisite are preserved separately.

Current catalog facts remain authoritative for the requirement graph. Older public course sites/syllabi are historical examples, not replacement enrollment rules. The known 07-380 Fall-2026 offering/catalog prerequisite difference remains in course notes. No launch date is inferred. Local audit has no unresolved requirement or source-access block. Independent peer review by `university_plan_conflicts` checked the original bodies and manual sets, identified the missing 15-151 progression grade, and accepted the corrected final snapshot. `second_pass_status` is verified. Shared export integration is coordinator work. The digest pins actual content, title, award and second-major eligibility; it does not itself certify source interpretation.
