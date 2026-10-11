# UC San Diego remaining computing and design course-content contribution

Reviewed 2026-10-11. Scope is exactly **22 identifiers** in `/tmp/ucsd-codeonly-computing_design22-targets.json`: DSC 11, ENG 4, DSGN 3, FILM 3 and CSS 1. Earlier entries had null titles/descriptions and evidence-insufficiency labels rather than content reviews. This contribution reads their exact source blocks; only its helper, manual manifest, tests and this note change. No seed, shared observer, identity or audit ledger is edited.

## Official sources and bounded coverage

The observed [official course index](https://catalog.ucsd.edu/front/courses.html) supplied the actual ENG, DSGN and Cinematic Arts links. Ordinary robots-aware Fetcher requests returned HTTP 200. Existing DSC/CSS caches were SHA-verified against the prior final-science manifest before reuse.

| Chapter | Official source | Original fetch time, UTC | Edition | Approved observations |
| --- | --- | --- | --- | ---: |
| ENG | [Engineering, Jacobs School of](https://catalog.ucsd.edu/courses/ENG.html) | 2026-10-11 09:48:41 | 2026–27 | 4 |
| DSGN | [Design](https://catalog.ucsd.edu/courses/DSGN.html) | 2026-10-11 09:48:42 | 2026–27 | 3 |
| CIN | [Cinematic Arts and Film Studies](https://catalog.ucsd.edu/courses/CIN.html) | 2026-10-11 09:48:44 | 2026–27 | 3 |
| DSC | [Data Science](https://catalog.ucsd.edu/courses/DSC.html) | 2026-10-11 09:31:40 | 2026–27 | 9 |
| CSS | [Computational Social Science](https://catalog.ucsd.edu/courses/css.html) | 2026-10-11 09:31:43 | **2023–24** | 1 |

The Cinematic Arts page actually prints **FILM 71, 72 and 73**. They are not guessed CIN-code substitutions. The CSS page's own disclaimer remains **2023–24**, despite the current index link. CSS 2 is therefore version-qualified authentic evidence, with an explicit gap in current-edition and current-degree-membership confirmation. The helper does not promote its edition to 2026–27.

All **20 matching full target descriptions** and relevant chapter/section introductions were read. **20 observations are approved**: twelve applications, three mathematics, three AI/ML, one systems and one mixed. Nineteen have a single reviewed category. **DSC 131 and DSC 185 lack exact current headings**; no replacement, renumbering, cancellation or institution-wide absence is inferred. There are no title holds because the observed targets had no earlier titles to match.

Raw ENG/DSGN/CIN sources are private in `/tmp/ucsd-computing-design-{ENG,DSGN,CIN}.html`; DSC/CSS reuse `/tmp/ucsd-final-science-{DSC,CSS}.html`. Provenance is `/tmp/ucsd-computing-design-source-index.json` plus ignored HTTP cache. Exact raw-source and normalized body hashes are retained. Summaries and rationales are original.

## Exact headings and credits

DSC 10 uses the complete shared heading **DSC 10/R. Principles of Data Science (4)**. The helper validates that heading and full body, then emits only assigned DSC 10. It creates no R record, alias group or online modality. Other targets have individual exact headings. Section membership is independently guarded, including FILM in the actual CIN chapter.

**ENG 10 and ENG 15 print two quarter units; the other eighteen approved observations print four.** No sequence or version amounts are summed. ENG 10/15/30 and DSGN 1/2 omit formal prerequisite clauses and retain null, without implying unrestricted institutional eligibility. DSC 10 and FILM 71/72/73 explicitly print **none**, which remains distinct from omission.

## Manual content judgments

- **Systems — DSC 102:** actual memory hierarchies, distributed computing, scalable deployment and MapReduce/Spark design/implementation establish computing infrastructure. Model selection and data preparation occur within that systems objective.
- **Mathematics — DSC 10/120/155:** statistical exploration/inference/prediction, mathematical signal representations, and rigorous random-matrix/principal-component theory respectively. DSC 10 explicitly introduces Python **as a tool** for data analysis; this does not require a coequal foundations classification. DSC 120 covers sampling, Fourier/basis representations, transformations and filters without a specific application domain taking precedence. DSC 155's statistical/matrix theory agrees with the independently reviewed MATH 182 content boundary.
- **AI/ML — DSC 140A/140B/148:** probabilistic/graphical learning, representation learning/deep networks, and mining/classification/clustering methods are explicit. Mathematical foundations support those named AI methods.
- **Mixed applications/human context — CSS 2:** computational social-science research design and legal/ethical dimensions are both explicit. Python is used to demonstrate research methods; no new general programming concepts are independently described. The candidate judgment is limited to the stated 2023–24 edition.
- **Applications — ENG 10/15/30/100D; DSGN 1/2/100; FILM 71/72/73; DSC 161/170.** Each has a separate content rationale. ENG 10 applies mathematics and tools to engineering problems; ENG 15 teaches academic/personal management skills, not technical engineering from its audience alone. ENG 30 specifies structured problem-solving techniques. ENG 100D's nonprofit engineering project is primary, with ethics/culture/stakeholders guiding the applied design process. DSGN covers observation, life design or user-experience prototyping. FILM explicitly trains cinematography, directing and editing. DSC 161 applies statistical/computational methods to text-based social research without naming an AI algorithm; DSC 170 specifies spatial/GIS analysis and geostatistics as a concrete applied domain.

No course is labeled systems simply because its title includes design or because it belongs to engineering. Camera/editing technology is not software foundations, and UI experimentation is not a security curriculum. Human-centered design and social beneficiaries do not alone make applied practice primarily cultural/social analysis.

## Preparation, access and credit restrictions

- **DSC 102/120/140A** require upper-division standing and their exact formal course lists. Their DS25 restriction has an explicit **space-available exception for all other students**. **DSC 140B/148/170** also allow that exception, but their individual blocks do not separately print the same standing clause; it is not copied across from nearby courses.
- **DSC 140A:** prior MATH 181A is **strongly recommended**, not mandatory. **DSC 148:** students should be comfortable with programming, optimization and linear algebra; the actual parenthesized course alternatives remain unchanged. Its credit exclusion with CSE 158 or CSE 158R does not establish three-code identity.
- **DSC 155:** MATH 180A and the printed linear-algebra alternative are required. MATH 102 is encouraged and explicitly **not required**. No credit for both MATH 182 and DSC 155. Neither a DS25 restriction nor Mathematics-chapter equivalent-course/consent policies are imported into this DSC block.
- **DSC 161:** one of the printed ECON/POLI preparation alternatives; junior/senior level and upper-division standing are both stated. No DS25 restriction is printed. Credit cannot be received for both POLI 176 and DSC 161; this is not a cross-list certification.
- **DSC 170:** DSC 80 is required. **DSC 120/140A/140B** retain DSC 80/R exactly, without synthesizing an online record or alias.
- **CSS 2:** CSS 1 **and choose one** of COGS 14B, MATH 11, MGT 3, POLI 30, POLI 30D or PSYC 60. The explicit selection wording is not treated as requiring every statistics course.
- **ENG 100D:** gateway to Global TIES but expressly open to all undergraduates, subject to its printed writing-course prerequisite alternatives. It is not major-only or program-member-only. One university-level mathematics course is recommended, not required. A nonprofit design project is not described as a guaranteed internship.
- **DSGN 100:** DSGN 1 is required. No extra technical prerequisite is invented from tools such as UI hacking.
- **FILM 71/72/73:** each explicitly has no prerequisites and separately excludes credit with its same-numbered VIS course. The exclusions do not alone establish course identity. Historical directing methods in FILM 72 serve professional directing practice rather than a separate film-history survey.

The inspected chapter/section introductions add no further undergraduate eligibility rule. That bounded observation does not certify absence of university-wide policies. No unsupported repeat allowance, minimum grade, major restriction or project placement is introduced.

## Guarded output and focused checks

`ucsd_computing_design_remaining_reviews.py` exports metadata-only `parse_observations(html, subject=None)` and five URL-keyed `SOURCE_PARSERS`. It uses actual source headings and declared editions, exact full course/shared headings, entire bodies including nested/unwrapped text, independent section membership and complete normalized introductory context. Missing DSC codes appearing, altered shared headings, duplicates, password forms or changed conditions fail closed. Manual reviews stay in the manifest; no requirements, identity group or audit certification is emitted.

**20 focused tests passed**, including all five exact cached replays: ENG 4, DSGN 3, FILM 3, DSC 9 plus two missing dispositions, CSS 1. Tests cover two-unit courses, explicit none versus omission, 10/R heading boundaries, old CSS edition, exact FILM codes under CIN, recommendation/major-access scope, no inherited insufficiency labels and manual categories. No full suite, build, seed or ledger update was performed; primary integration remains separate.
