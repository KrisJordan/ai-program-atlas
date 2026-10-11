# Stevens Artificial Intelligence BS

Reviewed 2026-10-10. Browser-rendered catalog plan: https://stevens.catalog.prod.coursedog.com/programs/qT6Ld1CzBAhQsVKYFNVv/academic-plan-JKlwr

Requirements: https://stevens.catalog.prod.coursedog.com/programs/qT6Ld1CzBAhQsVKYFNVv/requirements-and-concentrations-n90Np

Partial: 27 named plan courses, 125-credit rendered degree total, eight semesters, human-context alternatives and detailed elective/SUCCESS policy notes. The six science pathways include a conditional CH117/BIO182 lab choice. Six technical electives, two math/science electives and four general electives require prior advisor approval; explicit exclusion codes and nine overlap pairs are preserved. No option titles inferred from codes.

## Rendering boundary

The public catalog index initially returns “Loading results.” Normal browser rendering resolves the program and course entries. Direct plan HTML has unresolved course labels and an incomplete 58-credit total; this is not the source value adopted. The browser repeatedly shows 125. The parser explicitly rejects unresolved/changed totals and placeholder course references. Source-specific plan/rules parsers require rendered HTML; CLI HTTP refresh therefore fails safely for those sources rather than reporting a false verification. The overview parser can still observe the two-semester capstone.

## Next checks

Read linked university Humanities Requirements and other graduation/GPA/residency/transfer policies; expand open science/general pools, technical option metadata and graduate-course eligibility, SUCCESS course details, descriptions and prerequisites. Verify credit units and exact catalog edition. Launch date remains unknown. No public syllabi verified.

The browser catalog source is public, with no login or access bypass. Raw pages/screens are not committed; tests use synthetic hydrated and placeholder markup.


## Public policy review — 2026-10-10

The current catalog homepage explicitly identifies 2026–2027. Rendered Course Options and Transfer Credits tabs establish graduate-course access and external approval/grade restrictions. Graduation requires cumulative GPA 2.00, senior-year GPA 1.75 and 50-percent Stevens residency. The AI-specific humanities row clarifies three distribution choices plus HST 381/HSSC 371/HPL 455 after HASS 103/105. The finite language/music/theater/art list below is explicitly labeled SES/Business, leaving Computing applicability unresolved. The 600+ course-access clause likewise names SES/SSB, so it is not silently broadened to Computing. No degree-complete claim. Current policy URLs use fragment-selected tabs: ordinary HTTP yields the default tab and must not count as policy verification. Source-specific parsers require the rendered article identity/content, emit prose digests only, and never an audit.

## Full public elective and applicability follow-up — 2026-10-11

Normal public browser rendering re-established every program requirement panel. The revised `stevens_ai_requirements.py` observer now reads all six science-sequence rows with the nested CH 117/BIO 182 choice, the eleven-option technical pool (six selections; CS/CPE 558 is one cross-listed option), the two open math/science electives and their three additional named options, four open general electives, exclusions and nine overlap pairs, and PRV 101 plus three of five Frontiers courses. Named choices are now course rows even where their titles/credits are unknown. Excluded courses are not mislabeled eligible options.

**The prior “full open elective inventory” gap is closed.** The source expressly permits 3-credit PEP/CH/BIO/MA courses and 3+-credit Stevens general electives, subject to the stated exclusions, equivalence restrictions and prior adviser approval. This is a fully published open rule, not a missing finite list. No university-wide course enumeration is required. General-education example lists are separately labeled common examples, not exhaustive approved pools or blanket replacements for AI plan courses.

The public [School of Computing undergraduate tab](https://stevens.catalog.prod.coursedog.com/schools/computing#undergraduate-programs) explicitly lists this AI degree and incorporates General Education, Humanities and SUCCESS. Its links lead to the already reviewed university policy page. The [school FAQ](https://www.stevens.edu/page-right-nav/school-of-computing-frequently-asked-questions) describes a Fall-2026 school transition, not an AI degree launch or a general policy exception; no launch date is inferred.

New selected-tab policy observations are registered in `stevens_ai_general_education.py`:

- [General Education](https://stevens.catalog.prod.coursedog.com/academic-policies-procedures/undergraduate-education/requirements-procedures#general-education1): all eight published categories, named rows/amounts and example-versus-choice wording; Clark Scholars may substitute CLK 183 for PRV 101. Contextual totals are not added to the 125-credit AI plan.
- [International English](https://stevens.catalog.prod.coursedog.com/academic-policies-procedures/undergraduate-education/requirements-procedures#english-language-requirement-for-international-students): HASS 101 first, then 103/105; first-week diagnostic may allow direct HASS 103. HASS 101 can count as a general/free elective. No extra-credit amount is invented.
- [Course Options](https://stevens.catalog.prod.coursedog.com/academic-policies-procedures/undergraduate-education/requirements-procedures#course-options): exam-credit limits/grades/approval, unavailable-course application, optional overload, and graduate-course access. Existing audit/pass-fail restrictions are retained.
- [Advanced Placement](https://stevens.catalog.prod.coursedog.com/academic-policies-procedures/undergraduate-education/requirements-procedures#advanced-placement): the 30-credit combined pre-entry limit for entrants directly from high school, all 41 exam/score/equivalence rows, and QF economics footnote. Conditional school labels are preserved, not generalized to AI.
- [Grade Point Averages](https://stevens.catalog.prod.coursedog.com/academic-policies-procedures/undergraduate-education/requirements-procedures#grade-point-averages) and [Academic Standing](https://stevens.catalog.prod.coursedog.com/academic-policies-procedures/undergraduate-education/requirements-procedures#academic-standing): best-attempt GPA, three-attempt required-course limit counting W/F, retention of a prior passing attempt, external-grade exclusion, and published Notice/Warning progression.

The previous blanket School-of-Computing graduate-access gap was an overly broad reading. The text applies to an undergraduate taking a **600+ SES or SSB course**, not only to an undergraduate whose home school is SES/SSB. The current [MA 661 entry](https://stevens.catalog.prod.coursedog.com/courses/056460e313830166dcf5f1845234c2a3) identifies Engineering and Science and [BIA 665](https://stevens.catalog.prod.coursedog.com/courses/62f1e54e3e441000d12528653e9e0000) identifies School of Business. Their titles, three-credit amounts and original description summaries are mapped. Thus the published fifth-semester/3.25-GPA/approval/two-per-semester rule applies to these options; individual approval is still required, not granted by this record.

**Remaining inventory barriers are now two applicability questions:** (1) the arts/language humanities approval list expressly names SES and Business but not Computing; (2) AP Calculus AB/BC rows specify SES/QF/QSS or SB/HASS, omitting Computing. Neither a school-wide general-education link nor the FAQ explicitly extends these restricted rows. No automatic former-CS/SES inheritance or degree-complete claim is made. Other description/prerequisite/title/credit gaps and standalone credit-unit normalization are metadata, kept separately from these inventory questions.

All browser observations used ordinary public tabs without login or hidden endpoints. Default HTTP responses still contain unresolved course labels or the default policy tab and correctly fail these source observers. Development used the allowed HTML shell plus course labels visibly read in the browser and temporary transcriptions of rendered tables; neither is committed as a raw source fixture. Tests use reduced synthetic structures and verify changed choices, missing panels, unmatched columns, stale policy conditions, cross-list grouping and nested alternatives. Source observers never emit reviewer audits/freshness or promote completeness.

### Degree correctness review — 2026-10-11

The browser's fully hydrated academic plan repeats 125 credits; initial incomplete
HTML displays 58 with undefined course placeholders and remains invalid evidence.
Prescribed named rows independently total 24: 6/5/4/3/3/1/1/1 by semester. The
requirements tab was reread for all six science routes, nested laboratory
alternative, technical/general/math electives, advisor approval, exclusions and
SUCCESS. These are named-source inventory counts, not a student's full load.

Five course descriptions now have source-specific content guards and manual
subject reviews. CS368 is data-management infrastructure (systems). CS135
combines proof/discrete mathematics with programming, CS456 mathematics with
implemented AI methods, and CS508 governance/ethics with UX design: all three
retain mixed subjects. CS558/CPE558 resolves to one official Computer Vision
record under the combined heading; its single record is preserved.

CS368 eligibility is CS385. Computer Vision's description gives undergraduate
and graduate preparation separately; its Eligibility tab has a broader grouped
expression. Both source observations are preserved, without inventing an
undergraduate waiver from the graduate clause. Three other fetched eligibility
tabs show no rule; this is unknown, not proof of no prerequisites. Credits remain
in original unnormalized units until an explicit institutional definition is
reviewed. Whole-degree correctness remains in progress.

### Remaining fixed-course metadata — 2026-10-11

The independent ordinary-browser pass read 20 remaining fixed-course descriptions and all 20 settled Eligibility tabs. All 24 fixed identities now have actual-description reviews: six foundations, six mathematics, three AI, two human context, one systems, one entrepreneurship application, and five other (four mixed plus one unspecified computing seminar). The additional previously reviewed Computer Vision course remains an option. Public course pages display credits but do not define the institutional credit unit, which remains unknown.

CS 423 and CS 424 teach the general software development life cycle and application capstone practice; their AI-degree membership does not make those descriptions AI methods. CS 423 requires the displayed CS 182/385 alternative and senior standing; CS 424 requires CS 423. Five blank settled Eligibility tabs remain unknown, not unrestricted admission.

CS 583's prose requires Python and linear algebra, calls probability/statistics/numerical analysis recommended, and separately labels undergraduate linear algebra and probability as prerequisites. The Eligibility tab displays MA 232 or CS 556 and graduate/junior/senior conditions. Both statements remain visible with their original logical wording; no precedence correction or prerequisite waiver is invented. Existing policy applicability questions and remaining option descriptions keep the full audit in progress.

## Remaining description review — 2026-10-11

All 54 remaining current detail description fields have now been read via normally visible course links. All 79 represented records carry manual subject dispositions (68 reviewed, ten mixed, one unclassified), with 77 actual-content summaries. QF 102 current Basic Financial Tools metadata is withheld against its different GE title; HASS 101 contains restrictions only and keeps description null. Both use explicit limited title-only classification. Other mixed content, precise prerequisite alternatives, unknown credit units and dated BT renaming statements remain explicit. `stevens_option_course_reviews.py` guards identity/content/credits and composes existing MA 661/BIA 665 school observers. See `research/degree-audit/stevens-option-course-content.md` for source method and individual edge cases. Remaining selected Eligibility and school/cohort policy work stays in progress.

The independently transcribed role sets exposed a graph omission: EN 250, CE 240 and NANO 200 were only contextual despite the actual Math/Science Electives panel naming them as eligible choices. They now also attach to the existing choose-two rule. The pool remains explicitly open, with exclusions and advisor approval. Independent current totals are 24 fixed / 30 named options / 25 contextual records; no choice count or required load changed.
