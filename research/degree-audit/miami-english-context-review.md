# Miami English contextual course review — 2026-10-11

This bounded contribution independently reads the actual 143 English course blocks assigned from `research/miami-description-review-remaining.json`. It supplies guarded observations and manual subject reviews to the Miami owner; it does not edit program seeds, requirements, shared ledgers or degree audit status.

Source: [English and Creative Writing (ENG)](https://bulletin.miami.edu/courses-az/eng/), ordinary public chapter captured at 2026-10-11T04:14:32+00:00. The capture's SHA-256 is `57bfc45b8d34f6ef5bb349656235ba10cac80c155937108fc72b5eb29aa483ca`. The source includes current and stale download-navigation labels; the chapter's catalog edition remains null. No copyright year or download label is used as course-version or first-offered evidence. Raw HTML remains ignored at `.cache/research/miami-degree-audit/eng.html`.

## Manual decisions

All 143 selected source blocks were read. There are 120 `human_context` reviews and 23 `other`/`unclassified` reviews. Literary interpretation, cultural history, linguistic analysis and writing practice support the humanities classifications in each individual summary. In particular, ENG 344 examines data's meanings and politics through humanities and social-science readings, rather than teaching a technical data method. Literary treatment of medicine, scientific inquiry, environmental crisis or detective work does not turn those courses into medical practice, science, AI or computer-science courses.

The 23 unclassified records are ENG 250, 251, 253, 254, 255, 257, 258, 259, 350–359, 395–397, 495 and 595. The first 18 describe external study without a direct equivalent; the final five specify changing topics without an actual topic. These are source-inspected content gaps, not unread descriptions. ENG 493 is explicitly a limited exact-title review: *History of Literary Criticism* establishes humanities scope, while its description states only that semester content changes. No particular critical theory is inferred.

Seventeen records publish 1–5 credit hours and retain null scalar credits with an explicit observed range. ENG 350 publishes a scalar 3 despite sharing the transfer-placeholder description. All other selected entries publish 3. The independently read [Course Information policy](https://bulletin.miami.edu/general-university-information/university-policies/course-information/) explicitly equates credit hours with semester hours and semester credits under Miami’s semester system. Its capture at 2026-10-11T05:57:04+00:00 and digest are registered in the manifest’s separate credit-unit evidence. The English chapter itself labels amounts only as credit hours. No degree totals are calculated from this context inventory.

Explicit prerequisite expressions retain their source alternatives, including WRS/ENG route differences and the additional ENG 107 alternative in ENG 379/380. ENG 209's credit-only exclusion is preserved. ENG 319 excludes students who have already taken ENG 430/431 and bars concurrent enrollment; the reciprocal 430/431 blocks state concurrent/same-term restrictions. These restrictions do not establish cross-listed identity, so all codes remain distinct. Missing prerequisite text remains null and does not mean unrestricted enrollment.

The same 143 codes are represented in all four assigned Miami records. That existing contextual membership is neither a new degree option nor an assurance of enrollment, cognate approval or degree-credit applicability. No source-stated identity groups or program outcomes are asserted.

## Deliverables and validation

- `atlas/adapters/miami_eng_context_reviews.json`: concise course summaries, exact-source block hashes, source provenance, amounts/ranges, prerequisites and separate manual review rationale.
- `atlas/adapters/miami_eng_context_reviews.py`: exact-heading and full selected-block guards, exact program scope, missing/duplicate rejection, observed credit ranges, and optional idempotent composition with prior observations. No runtime `category_review`, curriculum audit, requirements or freshness is generated.
- `tests/test_miami_eng_context_reviews.py`: 11 checks, including content/eligibility/credit changes, missing or duplicate courses, wrong/login pages, range preservation, composition and all four actual source replays.

The public chapter was accessible and no additional access attempt was required. The only source-content limits within this subset are the stated unspecified transfer/topic content and uncertain chapter edition. Integration into the four program seeds and broader policy/audit closure remains with the Miami owner.

Validation also completed `atlas build --output /tmp/atlas-miami-eng-build`: 168 programs and 194 institutions rendered successfully from the maintained database. This verifies the existing build path, not integration of this new evidence; seed integration remains a separate owner action.
