# Lehigh AI, ML and Data Science BS

Reviewed 2026-10-10: https://engineering.lehigh.edu/cse/academics/undergraduate/bs-ai-ml-ds

Partial curriculum: 43 named courses, 15 requirement nodes covering the required technical/math/science tables, nine depth choices, twelve general-elective choices, open CSE 100+ eligibility, and HSS/free-elective rules. Announced Fall 2026 start has direct department evidence. The table says 130–131 total credits; page highlight says 130.

## Source discrepancies

ECO 001, WRT 001 and WRT 002 incorrectly-looking displayed titles duplicate ENGR 005, ENGR 010 and CHM 030 titles. Do not silently repair from memory: current seeds retain their codes and 4/3/3 credits as notes, without course title records. The source free-elective requirement is eleven credits but the sample sequence lists four plus six. Clarification remains needed.

MATH 205/241/242 has an aggregate 3–4 range; PHY 011/012 has aggregate five credits. Do not attribute these to every alternative or each component. CSE 252 cannot count as HSS.

## Remaining work

Verify current catalog counterparts, correct titles/credit discrepancies, expand open CSE and HSS rules, and inspect university/college graduation, residency, GPA, substitution, transfer and overlap requirements. No prerequisites or public course sites/syllabi verified. Credit amounts remain unnormalized.

## Adapter

Actually parses the three labeled HTML tables, course codes/titles/credits, required versus alternative/pool membership, and guards published ambiguity. Changed ambiguous titles, totals or group ranges require review. No fabricated reviewer audit or completion promotion.

## 2026-10-11 college and university policy review

The current 2026–2027 college catalog resolves the three mislabelled HSS rows:
ECO 001 **Principles of Economics**, WRT 001 **Academic and Analytical Writing**,
and WRT 002 **Research and Argument**. It also explicitly permits WRT 003 and
WRT 005 as the respective multilingual alternatives. The four writing-course
entries verify their individual three-credit values and documented prerequisites
or placement conditions (missing prerequisite statements remain null).
The economics course listing offers a 0,4 credit pattern; the engineering
college’s degree requirement explicitly assigns **4**, which is the value used.
The original department page’s incorrect-looking titles remain recorded above;
the primary adapter still flags a changed source for renewed review.

`atlas.adapters.lehigh_degree_policies` parses the college HSS table and guards
the associated university rules. Advanced HSS means at least three courses/12
credits, all at least two credits, at least one 3+-credit course in each of two
categories, and at least one HE or AL course. Eligible categories are HE, SW, AL,
and College of Health CGH/POPH. No advanced HSS course may be P/F. These are open
designation predicates, not an unextracted finite option list. CSE 252 remains
excluded. The college’s basic ten HSS credits reuse the existing degree slots.

The Undergraduate Studies **Credit Hours** section explicitly defines semester
hours, supporting normalized units without inferring them from a calendar.
Mapped policies include the 2.00 graduation GPA; 90 Lehigh credits **or** 60 of
last 75 residency; eight-year degree limit; application/completion deadlines;
three-attempt repeats including withdrawals; optional P/F caps/prohibitions and
listed exclusions; transfer grades, equivalence, session caps and conversion;
course standing/prerequisite rules; free elective ROTC/work-experience limits;
and the department’s continuing-student CSE transfer caps, age, assessment,
institution and approval conditions. AP/exam credits count toward the CSE caps;
the scope is continuing students, not an invented incoming-transfer limit.

**Partial remains justified** by the unresolved 130 versus 130–131 total,
11 versus 10 sample-plan free-elective credits, and unconfirmed overlap between
required/depth courses and the additional CSE100+/approved elective allocation.
HSS identity and degree-wide policy gaps are substantially resolved. No protected
source or raw HTML was used in committed files. Most course metadata and public
sites/syllabi remain independently unverified.
