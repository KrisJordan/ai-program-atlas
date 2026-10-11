# Independent core review: Northeastern and Penn State

Reviewed **2026-10-11** by `pilots_cmu_penn`. This is a bounded second pass of **26 degree records**, not a full-degree audit. The reviewer did not author Northeastern's primary degree graph. Two classification corrections were adjudicated with the coordinator and committed separately as `06e845e`; they are disclosed below rather than treated as an independent confirmation of unchanged data.

## Evidence and method

I read all 24 Northeastern `#programrequirementstextcontainer` panels in the existing official 2026–2027 captures, including preambles, course rows, selection instructions and footnotes. I manually wrote fixed code sets before comparing them with the family-resolved graph. Each variant was inspected individually, including Chemical Engineering outside the shared family; the common AI sequence was not assumed to transfer unchanged. The JSON pins the actual degree URL, capture time and source hash for every variant.

I then read the complete official course blocks for **178 distinct fixed Northeastern identities**, plus the DS 4440 option. Blocks include description and printed prerequisite/corequisite context. For Penn State, I read both complete major-requirement panels and **40 distinct prescribed/core-alternative course blocks**. The JSON's 219 `course_content_checks` preserve exact source URLs, locators, ignored cache paths, normalized whole-block hashes and original classification rationales. These are reviewed judgments, not parser-generated certifications. Raw copyrighted source text is not committed.

Manual course-ID sets and category calculations cover **581 fixed program-course identities across the 26 records**. That sum includes the same institution course in multiple degrees; it is not a unique-course count. Count/category expectations are computed from the independently written code/category lists, then tested against the resolved production profile. The content fingerprint protects the source and graph state reviewed; computing a hash does not establish that a review happened.

The remaining elective universe is deliberately **null**, not zero. This pass read local choice instructions but did not enumerate every department-range expansion, linked business concentration or general-education pool. Fixed categories can be verified while the overall chart-classification dimension stays partial. Penn State Engineering is the exception: all 30 currently represented course records (17 prescribed, 13 named alternatives) were independently reviewed, so its bounded mapped-chart classification is verified. Its uncaptured department-approved technical/nontechnical choices are still not certified.

## Role interpretation

- Northeastern's CS 2000/2001 are default listed requirements subject to a published proficiency self-assessment and replacement by otherwise unused upper-level CS/CY/DS coursework. Under the repository's default fixed-profile convention, they remain in the fixed set; this does not claim every student must enroll. Actual published OR choices remain optional.
- The degree preamble explicitly requires specified corequisite labs/recitations. Actual CS 1800 establishes CS 1802; CHEM 1161, 2161 and 2321 establish their named recitations. These are independently verified obligations, including zero-hour records, rather than prerequisites automatically promoted into the degree.
- Communication Studies says to complete eight integrative hours from the displayed list. Its COMM 2625/2941 alternative and CS 4120 retain the existing credit-choice ancestry. I initially questioned the NLP role, then confirmed the full header and conservative profile contract. No closed-credit-pool solver is used to promote CS 4120. It is directly fixed in Linguistics and Speech-Language Pathology, whose own tables differ.
- Design paths retain complete two-course branches, recommended substitutions and optional studios; Public Health biology retains its two distinct pathways and an inner alternative; International Affairs requires two regional courses in a single region; Ecology's 16-hour selection retains one course from each list. Repeated courses in GPA, integration or credit-allocation tables are counted once.
- Penn State Engineering retains CMPSC 131 **or** the complete CMPSC 121 + DS 120 route. Penn State IST retains AIMA 430 + 440 together within the six-credit capstone/research selection, rather than treating both capstones and research as universally required. Prerequisites were not added to the prescribed sets.

## Classification findings

Northeastern's five default fixed computing-foundation identities are CS 2000, CS 2001, CS 2100, CS 2101 and DS 3500. Their actual descriptions teach program construction, design, data structures, reusable software and pipelines. DS 3000 instead emphasizes linear algebra/probability and is mathematics; CS 3200 and DS 4300 teach database/storage infrastructure; DS 4400 and advanced learning/NLP courses teach explicit AI methods. DS 4200 remains mixed/other because visualization combines programming, perception and communication.

Chemistry, physics, clinical speech/hearing and engineering courses were judged from actual domain content. Formal statistics/logic stay mathematics even when hosted in economics, health or philosophy. Journalism and writing are communication/human-context subjects; editing software alone does not establish computing foundations. Scientific linguistic analysis is substantive domain knowledge, distinct from generic writing instruction. Unspecified research and orientation stay unknown rather than inheriting the department's category.

The complete descriptions of **CRIM 3600** and **INTL 2718** required a correction. They explicitly combine practical research design/implementation or quantitative/qualitative tool competency with critical social, normative and ethical inquiry. After comparing the actual descriptions with other institutions' applied social-research courses, the primary reviewer and coordinator agreed to **mixed applications/human_context**, stored as `other`. Each affected degree has one fewer fixed human-context course and one more other course; identities, credits, choices and total counts are unchanged. Their source blocks and rationales are included in this review. This does not convert social-science methods automatically into mathematics or classify all social inquiry as applied practice.

## Manual fixed-set totals

The table below summarizes the independently enumerated sets stored in JSON. Every listed fixed category was checked against actual course content. Option/context totals remain unreviewed except for the 13 explicit Engineering alternatives noted above.

| Program | Fixed identities | Foundations | AI/ML | Mathematics | Systems | Human context | Applications | Other |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Chemical Engineering and AI, BSChE (Boston) | 39 | 5 | 1 | 9 | 2 | 2 | 17 | 3 |
| AI + Behavioral Neuroscience, BS (Boston) | 23 | 5 | 2 | 2 | 2 | 0 | 11 | 1 |
| AI + Biochemistry, BS (Boston) | 27 | 5 | 1 | 3 | 2 | 0 | 15 | 1 |
| AI + Biology, BS (Boston) | 27 | 5 | 1 | 4 | 2 | 0 | 14 | 1 |
| AI + Business Administration, BS (Boston) | 21 | 5 | 2 | 4 | 2 | 2 | 5 | 1 |
| AI + Chemistry, BS (Boston) | 29 | 5 | 1 | 5 | 2 | 0 | 14 | 2 |
| AI + Communication Studies, BS (Boston) | 15 | 5 | 1 | 5 | 2 | 1 | 0 | 1 |
| AI + Criminal Justice, BS (Boston) | 19 | 5 | 1 | 5 | 2 | 4 | 0 | 2 |
| AI + Design, BS (Boston) | 23 | 5 | 1 | 5 | 2 | 3 | 5 | 2 |
| AI + Ecology and Evolutionary Biology, BS (Boston) | 27 | 5 | 2 | 4 | 2 | 0 | 12 | 2 |
| AI + Economics, BS (Boston) | 18 | 5 | 1 | 5 | 2 | 4 | 0 | 1 |
| AI + Environmental and Sustainability Sciences, BS (Boston) | 22 | 5 | 2 | 4 | 2 | 1 | 5 | 3 |
| AI + Health Science, BS (Boston) | 26 | 5 | 2 | 3 | 2 | 2 | 11 | 1 |
| AI + International Affairs, BS (Boston) | 20 | 5 | 1 | 5 | 2 | 5 | 0 | 2 |
| AI + Journalism, BS (Boston) | 25 | 5 | 2 | 5 | 2 | 10 | 0 | 1 |
| AI + Linguistics, BS (Boston) | 18 | 5 | 3 | 3 | 2 | 1 | 3 | 1 |
| AI + Mathematics, BS (Boston) | 20 | 5 | 2 | 10 | 2 | 0 | 0 | 1 |
| AI + Philosophy, BS (Boston) | 17 | 5 | 1 | 6 | 2 | 2 | 0 | 1 |
| AI + Physics, BS (Boston) | 25 | 5 | 1 | 6 | 2 | 0 | 10 | 1 |
| AI + Psychology, BS (Boston) | 14 | 5 | 2 | 3 | 2 | 0 | 1 | 1 |
| AI + Public Health, BS (Boston) | 18 | 5 | 2 | 3 | 2 | 2 | 3 | 1 |
| AI + Sociology, BS (Boston) | 16 | 5 | 1 | 4 | 2 | 2 | 0 | 2 |
| AI + Speech-Language Pathology and Audiology, BS (Boston) | 30 | 5 | 2 | 5 | 2 | 1 | 14 | 1 |
| Environmental Engineering and AI, BSEnvE (Boston) | 36 | 5 | 1 | 8 | 2 | 2 | 15 | 3 |
| Penn State — AI Engineering, B.S. | 17 | 1 | 4 | 6 | 1 | 2 | 2 | 1 |
| Penn State — AI Methods and Applications, B.S. (Information Sciences and Technology) | 9 | 2 | 3 | 3 | 0 | 1 | 0 | 0 |

## Boundaries and verification

All 26 fixed-requirement dimensions are verified within their stated default-core scope. Choice-rule review remains partial for all 26 because full expanded and linked elective inventories, student-specific permissions and degreewide policy applicability are not part of this pass. Classification is partial for the 24 Northeastern programs and Penn State IST; Penn State Engineering has verified classification only for its fully reviewed currently mapped 30 records. No whole-degree primary audit status or second-pass completion status is promoted.

Focused tests compare manual exact identities/categories, family-resolved fingerprints, bundles, mixed/unknown semantics, and all 219 actual cached source blocks. Optional raw-source tests skip when ignored captures are unavailable; ordinary identity/regression tests remain active. Root owns integration into the maintained database and published audit summary.
