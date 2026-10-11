# Stevens fixed-course description contribution — 2026-10-11

Scope: twenty previously unreviewed fixed identities in the existing Artificial Intelligence BS. This is a primary metadata contribution for integration by the program owner, not a whole-degree or independent second-pass certification. The five earlier reviewed identities include optional CS 558 / CPE 558, so there were twenty remaining fixed identities, not nineteen. No seed, requirement role, inherited prerequisite, degree total or option membership is changed here.

## Evidence actually read

The [public academic plan](https://stevens.catalog.prod.coursedog.com/programs/qT6Ld1CzBAhQsVKYFNVv/academic-plan-JKlwr) was read after its normal browser hydration displayed the named courses and source-stated 125 total degree credits. Its public course links were followed in ordinary Chrome. All twenty Course Information descriptions, titles and credit fields and all twenty selected Eligibility tabs were read. The initial HTTP/transition placeholder is not evidence. No internal service request, account, access denial workaround or guessed course URL was used.

`atlas/adapters/stevens_fixed_course_reviews.json` records each exact observed course URL, eligibility URL, identity/title, credit amount, content digest, original summary and manual taxonomy rationale. Raw public DOM observations are intentionally untracked at `/tmp/stevens-fixed-course-captures.json` (forty settled tabs). Individual course pages do not identify a catalog year, so the manifest records current public catalog access without inventing a course version year. This review does not independently establish a credit-unit definition, contact hours, delivery modality, or term-specific section eligibility. Numeric Credits remain `credit_unit: unknown`.

## Per-course dispositions

| Identities | Subject disposition | Evidence basis |
|---|---|---|
| HASS 103, HASS 105 | human_context | Writing/oral communication; social-cultural inquiry and research writing |
| CS 115, CS 284, CS 385, CS 334 | foundations | Programming, data structures, algorithms and computation theory |
| CS 423, CS 424 | foundations | General software construction for clients, followed by continuation of that project; no guarantee of an AI project |
| MA 121, MA 122, MA 125, MA 126, MA 223, MA 331 | mathematics | Differential/integral/multivariable calculus, linear algebra, probability and statistics |
| CS 367, CS 559, CS 583 | ai_ml | Explicit AI, machine-learning and deep-learning methods |
| MGT 103 | applications | Entrepreneurial problem discovery, business assessment and customer research |
| CS 101 | other / unclassified | Seminar spans unspecified computing research areas; no defensible dominant subject from the actual description |
| PRV 101 | other / mixed | College transition, wellness, career skills, cultural awareness and ethical judgment; human-context and applied practice candidates retained |

This contribution contains six foundations, six mathematics, three AI/ML, two human-context, one applications and two other identities. These are twenty fixed-course metadata dispositions, not the complete degree profile. Credits are two one-credit, five two-credit, ten three-credit and three four-credit observations. No total or cross-institution conversion is inferred from unknown normalized units.

## Prerequisites and ambiguities

The five blank Eligibility tabs (CS 101, CS 115, MA 121, PRV 101, MGT 103) yield unknown prerequisites, not unrestricted registration. HASS 103 and 105 explicitly restrict eligibility to freshmen, sophomores and transfers. MA 122 requires MA 121; MA 125 requires MA 122; MA 126 requires MA 125. CS 284 requires CS 115; CS 367 requires CS 284; CS 385 requires both CS 135 and 284; CS 334 requires both CS 135 and 385. MA 223 gives MA 124 **or** 126; MA 331 gives MA 223. CS 559 gives `(MA 223 and MA 331) or CS 556`. These are contextual eligibility observations; they are not newly added degree obligations.

[CS 583 Course Information](https://stevens.catalog.prod.coursedog.com/courses/056460e3138301600bb9352b5234424f) makes Python and linear algebra compulsory, calls probability/statistics/numerical analysis recommended, then identifies undergraduate linear algebra and probability as prerequisite preparation. Its [Eligibility tab](https://stevens.catalog.prod.coursedog.com/courses/056460e3138301600bb9352b5234424f/eligibility-6OfL6) supplies a separate Boolean expression involving MA 232, CS 556 and graduate/junior/senior standing. Both are preserved; the observer neither resolves the prose tension nor inserts parentheses into the source expression. An actual registration decision is outside this contribution.

CS 423 permits CS 182 or CS 385 and restricts enrollment to seniors. CS 424 requires CS 423. Its terse continuation description is classified using both inspected source descriptions, with both source IDs attached to the manual rationale. MGT 103 uses projects and simulations, but that does not imply AI subject matter. No prerequisite aliases, substitutions or course-credit double counts have been inferred.

## Observer and verification

`stevens_fixed_course_reviews.py` accepts only the expected code/title and a settled selected tab. It validates the reviewed description or eligibility digest and the credit amount. Empty eligibility requires the selected Eligibility tab, no stale Course Description and the reviewed absence of a rule. Changed descriptions, names, credits or eligibility raise a review error. Registration is idempotent and refuses to overwrite an unrelated observer. Runtime candidates contain metadata, never manual `category_review` or whole-degree audit certification. CS 583's description context survives the separate eligibility observation.

Four focused tests pass: synthetic content/identity/credit/tab guards, empty-rule semantics, exact identity/classification scope and registration collision handling, plus all forty actual ignored UI captures. Primary integration still needs to register these forty source observations and copy the manual per-course reviews into the existing seed. Existing degree-wide policy and optional-course inventory audit gaps are not closed by this contribution.
