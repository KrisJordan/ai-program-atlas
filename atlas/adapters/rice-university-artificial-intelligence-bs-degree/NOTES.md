# AI degree curriculum observations

Reviewed the official catalog on 2026-10-10: https://ga.rice.edu/programs-study/departments-programs/engineering/artificial-intelligence/artificial-intelligence-bs/

Mapped sections:
- Mathematics and computing core with whole statistics bundles
- AI core and cross-listed alternatives
- Three of five elective areas
- Major credit totals, level minimum, GPA and transfer limits

Remaining degree-audit gaps:
- University graduation, residence, distribution, communication, diversity and physical activity policies require full structured mapping.
- Program substitutions and transfer rules link to university policies that remain incompletely mapped.

Course descriptions, prerequisites, missing individual credits remain separate metadata gaps. Parser output never asserts review status or completeness.

The catalog banner identifies the 2026–2027 edition. Four published learning outcomes are recorded as short source-backed paraphrases.

## University scope review — 2026-10-11

The record now has **43 courses and 70 requirement nodes**. The 2026–2027 GA graduation, transfer and registration pages add 18 source-guarded policies. They cover minimum total/resident/upper-level hours, GPA and letter grades, applicable catalog year, degree application, FWIS placement and transfer restrictions, all three distribution categories, AD overlap, LPAP, transfer approval/limits, course loads, graduate-course enrollment, repeats and cross-list credit. Distribution and AD remain term-designation criteria; no fixed course universe is invented.

A concrete inconsistency prevents completion: the [graduation page](https://ga.rice.edu/undergraduate-students/academic-policies-procedures/graduation-requirements/) allows up to one summer within the four full-time residency semesters, while the [transfer page](https://ga.rice.edu/undergraduate-students/academic-policies-procedures/transfer-credit/) states four full fall/spring semesters. Both are General Announcements pages; the GA-authority rule cannot itself resolve their disagreement. The [registration page](https://ga.rice.edu/undergraduate-students/academic-policies-procedures/registration/) defines full-time summer status but does not explicitly reconcile the two residency rules.

Rice remains **partial**, with this source conflict identified. Individual advisor-approved substitutions are not inferred. Missing course descriptions and prerequisites remain metadata gaps, separate from the newly reviewed degree policies. All requests used the public robots-aware fetcher and preserved TLS checks.

## Independent correctness pass — 2026-10-11

Official fixed-course descriptions now support all 13 fixed classifications: 3 foundations, 1 mathematics, 2 systems, 5 AI/ML, 1 human context and 1 applications (cognitive psychology as substantive domain knowledge, not an invented AI application). Source titles' ARTIFICAL spelling is preserved; exact-identity subject review replaces generic keyword misses. COMP 329 is computing infrastructure and COMP 282 mathematical optimization, despite AI in their titles. Parsers check identities/descriptions and emit no category_review certification.

COMP 456/457 must be sequential within one academic year. Current descriptions also expose reciprocal credit exclusions between required COMP 345 and listed elective COMP 447; STAT 315-specific prerequisites despite degree statistics alternatives; and Graduate-only restrictions on listed COMP 585/631. The STAT315 requirement is conditional preparation: selecting a different degree statistics route does not waive it and may require extra preparation. It is not by itself a curriculum contradiction or another universal fixed course. Reciprocal exclusions and graduate-only eligibility remain explicit restrictions, with no inferred waiver. Source-specific parser notes guard each published restriction. Full correctness audit remains in progress; see research/degree-audit/rice.json and its Markdown for manual fixed-set arithmetic and remaining work. Sources: https://ga.rice.edu/programs-study/courses/comp/, /phil/, /psyc/.
