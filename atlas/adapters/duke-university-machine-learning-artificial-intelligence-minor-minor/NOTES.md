# Reviewed local minor inventory

Reviewed 2026-10-10. Status: **partial**. This scope is the minor, not the parent degree.

## Evidence and coverage

- ECE minors: Machine Learning & Artificial Intelligence: https://ece.duke.edu/academics/undergrad/minors/ — #ml section: Fundamental Courses; Upper-Level Focus Courses; Note on Prerequisites; Notes on Course Counting
- 2026–27 ML/AI minor bulletin: https://undergraduate.bulletins.duke.edu/programs/U-ECE-MLAI/requirements-IkDU1 — Requirements: fundamental/focus courses; Important Notes; Prerequisites
- Trinity majors, minors and certificates: https://trinity.duke.edu/undergraduate/academic-policies/change-major-minor-certificate — Minor; Restrictions on Majors, Minors, Certificates; Changing/Adding/Deleting

25 course records and 28 requirement nodes. Courses include alternatives/elective pools; not all are required. Course metadata is separate from inventory completeness.

## Unresolved requirements

- Reconcile narrower 2026–27 bulletin focus pool with expanded undated department list.
- Reconcile bulletin primary-major overlap restriction with department major(s) restriction.
- Verify minor-specific grading and applicable Pratt residency/transfer policies before certifying complete local requirements.

## Interpretation and refresh

- The displayed pool follows the current undated ECE department page; catalog_year is null because its relationship to the 2026–27 bulletin is unresolved.
- Special-topic examples retain their offering context in requirement notes. ECE 495 F24/F25 and ECE 590 S25/S26 are historical examples, not confirmed future availability. ME 555 has two named topic examples and is not counted as two compulsory courses.
- Preparatory programming, linear algebra and statistics courses are examples of expected knowledge, not a mandatory list of every example course.
- This partial inventory represents the minor only, not the host degree or an individual graduation audit.
- Course inventory contains alternatives and elective examples; not every listed course is compulsory.
- Adapters extract actual local headings, course choices and numeric rules; secondary pages validate relevant policies and emit content digests. Changed sources create candidates and never recertify completeness. Scrapers emit no review audit or verification date.
- The Duke adapter scopes to the ML section or AI applications accordion, excluding adjacent minors. Cross-listed identifiers remain one record; different named ME 555 topics remain separate examples with approval context.
- Focused synthetic fixtures cover changed counts/units/declaration dates, omitted subject prefixes, cross-listing identity and unknown metadata. No fetched source bodies are committed.


## Accessible policy follow-up — 2026-10-11

The official 2026–27 undergraduate bulletin returned HTTP 200 at [Grading](https://undergraduate.bulletins.duke.edu/policies-procedures/grades), [Transfer/Entrance Credit](https://undergraduate.bulletins.duke.edu/policies-procedures/transfer-entrance-credit) and [Pratt Degree Requirements](https://undergraduate.bulletins.duke.edu/undergraduate-instruction/pratt-degree). The initial HTML renders the first tab, but the ordinary response's public `__NUXT_DATA__` payload contains the published tab bodies. `duke_public_policies.py` follows only the matching published page's `widgets` → `tabs` → named content, verifies the visible section heading and material policy clauses, and excludes `temporaryContent`/unrelated cached objects. No hidden endpoint, authentication, or access restriction was bypassed.

The records now contain the general D-grade rule and the DUS approval required to count voluntary S/U work toward a major/minor/certificate or prerequisite. Transfer approval, at-least-half-at-Duke requirement for incoming transfer students, department acceptance of entrance credit, post-matriculation C- threshold and no P/F transfer rule, school-specific individually arranged transfer limits, and study-away limits are explicit. These are credential policies and host-school context, not a full reconstruction of a host degree. No individual course is presumed transferable.

The public [Trinity S/U policy](https://trinity.duke.edu/undergraduate/academic-policies/unsatisfactory-satisfactory-grading-option) additionally requires instructor permission for S/U courses numbered 500 or above. The public [Trinity Transfer Credit policy](https://trinity.duke.edu/undergraduate/academic-policies/transfer-credit) supplies simultaneous-enrollment, institution, summer-duration, replacement-D and third-party-transcript restrictions. Those notes expressly apply to Trinity students. Administrative request forms and academic records were not accessed. All parsers emit observations only, never completion/audits/fresh verification.

The **ML/AI minor is now 25 courses / 40 requirement nodes**. Published Pratt B.4.e establishes at least five technical courses, at least three upper-level, limits introductory work and independent study, opens ML/AI to engineering/non-engineering students, and supplies a one-cross-listed-upper-level-elective exception. The latter differs from the department's major(s) no-overlap wording. The prior unreviewed grading/residency/transfer gap is closed; **partial remains** for the focus-pool and overlap-source conflicts. Pratt B.4.b residency is labeled host-degree context, not a minor credit total. IDEAS students cannot add another major/minor.
