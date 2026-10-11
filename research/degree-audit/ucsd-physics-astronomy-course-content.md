# UC San Diego PHYS and ASTR course-content contribution

Reviewed 2026-10-11. Scope is exactly **26 represented targets: fifteen PHYS and eleven ASTR**, from `/tmp/ucsd-physics-astronomy-targets.json`. Only the owned helper, manifest, tests and note change; no seed, shared observer, requirement, identity or audit ledger is edited.

## Sources and coverage

The observed [official course index](https://catalog.ucsd.edu/front/courses.html) links the [Physics](https://catalog.ucsd.edu/courses/PHYS.html) and [Astronomy and Astrophysics](https://catalog.ucsd.edu/courses/ASTR.html) chapters. Their actual H1 headings establish chapter identity, not the Astronomy link’s stale tooltip. Normal robots-aware Fetcher requests returned HTTP 200 at `2026-10-11T08:56:36+00:00` and `2026-10-11T08:56:37+00:00`, respectively. Both identify **General Catalog 2026–27**. Raw pages are private in `/tmp/ucsd-physics-astronomy-PHYS.html` and `/tmp/ucsd-physics-astronomy-ASTR.html`, with provenance in `/tmp/ucsd-physics-astronomy-source-index.json` and the ignored HTTP cache. Exact source, edition, heading and full-body hashes are retained in the manifest; summaries are original.

All **25 exact matching blocks** were read in full. **24 observations are approved: 22 applications, one human-context and one mixed review**. Twenty-three have a reviewed single category. PHYS 13 has no current exact heading; ASTR 4’s similar name does not establish a replacement or alias. ASTR 150 is a conservative title/version hold: the pool lists **Observational Astrophysics Laboratory**, while the current five-unit course is **Observational Optical Research Lab**. Its current applied optical-astronomy content remains candidate evidence only, not certification of the older title. No cancellation or institutional absence is inferred.

All other title variations are punctuation, topic order, the explicit Physics for Physics Majors label or Lab/Laboratory wording. No target relies on a shared range heading.

## Content boundaries

- **ASTR 60, human context:** scientific racism, institutional barriers and antiracist interventions are the actual content. Its physics/astronomy setting does not make it physical-science methods.
- **ASTR 154, mixed mathematics/AI-ML:** the actual description introduces statistical methods and machine-learning algorithms together. It does not establish one as dominant. Python and existing public codes implement the methods; no beginning-programming objective is stated, and astronomy is the application context rather than a separately described astronomy-theory component.
- The other 22 approved courses teach physical, astronomical or instrumentation science/practice. Calculus prerequisites do not make physics a mathematics category. PHYS 4E’s quantum physics is not an inferred quantum-computing course, nor is ASTR 4’s extraterrestrial intelligence AI instruction.
- **ASTR 15:** the stated purpose is a survey of astrophysics using science-fiction novels/films and astronomy readings. The source does not separately specify cultural-history or literary-theory instruction; applications reflects its actual astronomy-learning aim.
- **PHYS 124/133:** experimental apparatus, electronic sensing/actuation, instrumentation and materials research are substantive applied practice. Arduino use does not establish general software foundations. PHYS 133 specifies concrete experimental methods despite student-designed projects.
- Held **ASTR 150** describes optical measurements and astronomical analysis with significant programming. That supports current domain-practice analysis but does not resolve the title/version issue.

## Units and course-specific conditions

The approved headings print **three three-unit courses** (PHYS 1A/B/C), **one five-unit course** (ASTR 154) and **twenty four-unit courses**. All use the verified quarter-hours contract. Held ASTR 150 also prints five units. No lab credits are added to lectures, and no sequence credits are totaled. Ten approved blocks lack a `Prerequisites:` clause and remain null; omission does not mean an absence of all preparation or policy.

- PHYS 1A/1B/1C and their respective labs are designed for concurrent enrollment **but may be taken in separate terms**, preferably lecture before lab. Concurrency is not rewritten as mandatory. PHYS 1A requires MATH 10A or 20A; MATH 10B or 20B is recommended at that stage and needed to continue to 1B/1BL.
- PHYS 11 explicitly distinguishes a MATH 10A/20A prerequisite from a **MATH 10B/20B corequisite**. PHYS 10 only recommends college algebra. PHYS 8 says no prior physics knowledge is required, although no formal prerequisite clause is printed.
- PHYS 2C’s opening calls it a continuation of 2B, but the body says prior 2B is **strongly recommended**, not part of its formal prerequisite list. Prior/concurrent MATH 20D is recommended and needed to proceed to 2D. PHYS 2D requires its printed physics alternatives plus 2B and MATH 20D, while prior/concurrent MATH 20E is recommended.
- PHYS 4C/4D/4E retain their exact alternate physics/mathematics sequences, commas and abbreviated numbers. Recommended concurrent preparation in 4C/4D is not promoted into mandatory courses. The helper does not invent Boolean precedence for compressed AND/OR notation.
- ASTR 20A retains the literal `MATH 20A-B-C or 31BH and PHYS 2A/2AR-B or 4A and 4C` prerequisite wording; ASTR 20B requires 20A. ASTR 154 and held 150 preserve the full alternate physics and programming-course lists.
- ASTR 154 may be coscheduled with ASTR 254. This does not certify identity or import graduate eligibility.
- PHYS 124 requires PHYS 120, may have program/materials fees and explicitly states it was formerly numbered PHYS 120B. Renumbering is noted without emitting an identity group or inventing a prior-credit exclusion not stated in this block.
- PHYS 133 requires PHYS 2CL and 2DL and is open only to **PY26, PY28, PY29, PY32, PY33, PY34 and PY35**. Program/materials fees may apply. The named major-code restriction is not broadened to all majors.
- The prior pool says None for ASTR 60 prerequisites; its current block has no prerequisite clause. Current-source null does not manufacture a new absence finding.

## Physics chapter-wide policies

The complete Physics preamble from Courses through the first individual course is independently hashed. It states that departmental prerequisites and enrollment policies/protocols are strictly enforced, offerings need not occur every term/year, and required courses may conflict in scheduling.

Its lower-division sequence guidance is scoped in notes:

- PHYS 1 is calculus-based and primarily intended for biology.
- PHYS 2 is advanced-calculus-based and intended for physical science, engineering and mathematically strong biological-science students.
- PHYS 4 is required for physics majors and others seeking enrollment in the specified core PHYS 100/105/110/120/130/140 series. This is not introduced as an AI-degree obligation.
- PHYS 8/10/11/12 are intended for nonscience majors. An intended audience is not treated as an exclusive enrollment prohibition.

The chapter’s external policy links were not used to infer additional rules. No separate Astronomy section-wide eligibility rule is stated in the inspected introductions. That bounded observation does not certify absence of policies elsewhere.

## Guarded output and validation

`ucsd_physics_astronomy_reviews.py` exports metadata-only `parse_observations(html, subject=None)` and URL-specific `SOURCE_PARSERS`. Without an explicit subject it requires exactly one recognized chapter heading; each chapter emits only its own assigned records. It guards edition, exact headings, complete bodies including nested/unwrapped text, and the separate Physics preamble. Changed source conditions, credits, policies, duplicate codes, missing-code appearance or title-hold content require renewed review. Password forms are rejected. Manual reviews remain in the manifest; no requirement, identity or audit certification is emitted.

**16 focused tests passed**, including both exact cached-source replays: fourteen PHYS and ten ASTR observations, with one disposition per chapter. Tests cover source routing, chapter-wide policy changes, full body guards, three/four/five-unit values, intended audiences versus restrictions, required corequisites versus optional preparation, literal prerequisites, missing identities and mixed taxonomy. No full suite, site build, seed or ledger update was performed; primary integration remains outstanding.
