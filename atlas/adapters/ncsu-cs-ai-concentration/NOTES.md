# Computer Science (BS): Artificial Intelligence Concentration

Reviewed 2026-10-10 against the [2026–2027 official catalog](https://catalog.ncsu.edu/undergraduate/engineering/computer-science/artificial-intelligence-concentration/). This is a formal concentration in the Computer Science BS, not a standalone AI degree. First offering remains unknown.

## Mapped local scope

Partial inventory: **40 course records, 8 requirement nodes**, and one explicitly classified program-aim paraphrase. The parser scopes to the concentration rows of Plan Requirements plus the two named AI elective tables, excluding the host degree’s separate general CSC and Group B lists.

- Two required courses: CSC 411 and CSC 422.
- Six credit hours from the four-course CSC AI restricted list.
- Nine credit hours from 34 named interdisciplinary options plus the CSC AI subset; at most three hours may come from that subset.
- Total concentration size: 21 published credit hours. One-credit DSA/ST choices are preserved; the nine-hour selection is not simplified to three courses.
- Main-plan grade footnotes, CS major GPA alternative, and the host degree’s CODA entry relationship.

The credit choices are policy nodes with observed numeric amounts, exact finite pool membership and clear selection summaries while the credit unit remains unnormalized. The schema requires a known unit for `choose_credits`; no unit or course count was invented to satisfy that constraint.

## Source conflicts and remaining requirements

The main plan marks the required AI courses and CSC AI elective block with footnote 1 (C minimum), while the CSC AI pool heading carries footnote 2 (C-minus). Both observations remain visible; the parser detects changed footnote mapping and does not resolve the discrepancy automatically.

The AI pool uses DSA 405/406/412/435, while a different host-degree table uses DSC codes. The concentration-local DSA labels are retained without inventing equivalence. Course entries need confirmation. Concentration declaration/eligibility, elective-credit reuse, substitutions, residency and any additional local completion policies remain unreviewed. These gaps make the concentration partial. The 121-hour host BS is outside this local concentration inventory.

The [official academic calendar](https://catalog.ncsu.edu/about/academic-calendar/) separately verifies Fall 2026 and Spring 2027 semesters. Calendar verification does not establish a semester-credit conversion, so course credit units remain unknown. Descriptions, prerequisites, public course resources and syllabi remain unknown. The overview describes intended preparation; it is labeled a program aim rather than a measured learning or employment outcome.

## Refresh and validation

The source-specific parser extracts current course rows and credit amounts and checks headings, cap, grade references and key policy conditions. It emits no audit, verification timestamp or completeness. Synthetic fixtures contain invented course titles and exercise source scoping, credit choices, one-credit options, missing identity, access gates and changed policy references. Raw official HTML remains in `/tmp` or ignored fetch cache, not committed.

## Public policy follow-up — 2026-10-11

40 courses, 20 nodes. Added twelve guarded policy observations from the AI department page, Curriculum Restrictions, and public Advising FAQ: admission course/GPA thresholds and review timing; department-approved AI CSC 495 option (catalog omission explicit); prior substitution/study-abroad approval; distinct credit-bearing slots; Group A exclusion; six-hour non-NC-State-GPA caps per host elective category; letter grading; application timing; Robotics-track exclusion; topic reuse; external transfer review. Do not use general host elective lists to expand the narrower concentration pools.

DSA 405/406/412/435 are independently verified in the official Data Science subject page linked by the course directory: https://catalog.ncsu.edu/course-descriptions/dsc/ . The URL slug says dsc, but all four displayed codes are DSA and each is one credit. Descriptions/prerequisite skills now sourced. This resolves whether DSA identities exist, not whether older DSC plan labels are aliases. `/search/?P=DSA+...` is robots-disallowed to our fetcher; we did not bypass that route. The independently linked public subject document passed robots and HTTP200.

Remaining source conflicts: C vs C-minus pool heading; department approved CSC495 absent from catalog list; department says apply after CSC230/316 while advising permits application while enrolled, with C-or-higher completion before review. No automated reconciliation. Additional local residency/exception rules and normalized units unverified; status remains partial. Host full degree is outside scope. Source-specific parsers emit observations only, never audit certification. Raw HTML stays ignored.
