# UT Austin and Yeshiva concentration policy review

Reviewed 2026-10-11. This bounded pass addresses local concentration completion and exact UT course metadata. It does not inventory either complete host degree. Both programs remain **partial**, with the previously documented source conflicts intact.

## UT Austin

Reviewed the current [concentration directory](https://www.cs.utexas.edu/undergraduate/concentrations), its [dated course-list PDF](https://www.cs.utexas.edu/sites/default/files/2025-12/UTCS_Concentrations_Course_Listings_12172025.pdf), the [legacy concentration page](https://www.cs.utexas.edu/concentrations/mlai), and [current academic advising page](https://www.cs.utexas.edu/undergraduate/academic-advising). The published route is for current CS students, directed to their adviser. Advising covers transfer and substitution review. These sources did not supply a separate concentration GPA/residence threshold, declaration deadline, transcript-recognition process or explicit eligible host-degree list. This is a bounded observation, not a claim that such rules do not exist.

All nine PDF course routes were checked against the accessible [department undergraduate course directory](https://www.cs.utexas.edu/undergraduate/degrees-and-programs/courses) and [current general CS catalog](https://catalog.utexas.edu/general-information/coursesatoz/c-s/):

| PDF route | Result |
|---|---|
| CS 342 Neural Networks | Exact department entry: original description and prerequisite summary added. |
| CS 344M Autonomous Multiagent Systems | Exact department entry: original description and prerequisite summary added. |
| CS 344R Robotics | Exact department entry: original description and prerequisite summary added. |
| CS 371R Information Retrieval and Web Search | Exact department entry: original description and prerequisite summary added. |
| CS 376 Computer Vision | Exact department entry: original description and prerequisite summary added. |
| CS 343(H) | Directory has separate standard/honors entries; preserve the PDF's aggregate notation and leave metadata null pending the intended route interpretation. |
| CS 363M (378H) | Department uses older Data Mining terminology; current general catalog uses X-prefixed identifiers and Principles of Machine Learning I. No silent identity/equivalence join. |
| CS 371N | No exact numbered department entry; current general catalog's X-prefixed entry is not automatically a verified instance of the PDF route. |
| CS 378 Practical Applications of Natural Language Processing | Exact named topic was not established in these two directories; do not inherit an arbitrary CS 378 prerequisite. |

The separate [official credit-numbering policy](https://catalog.utexas.edu/general-information/academic-policies-and-procedures/credit-value-and-course-numbers/) explicitly defines first-digit semester credits and the 301–399 range as three credits. All nine printed PDF routes are 3xx, so they now have **3 semester credits**. This does not use lecture contact hours, resolve ambiguous honors instances or add courses to the requirement pool. Source IDs on five enriched course records identify their metadata source; the separately registered numbering-policy source and seed note document every numerical credit/unit value.

The current directory's five matched bodies are guarded by exact heading and normalized-content hash before approved original summaries are returned. Any changed prerequisite or new condition requires review. The credit rule is likewise guarded; the HTML identity parser still does not claim to refresh the PDF. Four course routes remain uncertain after the finite nine-route comparison, rather than unattempted. Section-specific teaching pages and syllabi were not searched in this bounded pass and remain possible public research, not declared blocked. The superseded `/undergraduate-program/courses` path redirected to a login page in the ordinary web reader; it was not accessed or retried as an authenticated route. The current public directory came from the institution's own navigation.

**Institutional confirmation needed:** UT CS undergraduate advising (`under-info@cs.utexas.edu`) should establish concentration declaration/recognition, eligible host awards, any distinct grade/residence restrictions, and the controlling interpretation of the PDF/legacy course conflict and aggregate honors notation. No message was sent.

## Yeshiva College

The [registrar catalog directory](https://www.yu.edu/registrar/ug-catalog) explicitly labels the rolling University Catalog link **2026–27**, providing edition provenance missing on the program page itself. The program and applicable current catalog sources now record 2026–2027 using that attribution.

Reviewed the catalog's undergraduate policy index and these eleven linked pages:

- [Grade Requirement](https://yu.smartcatalogiq.com/en/current/university-catalog/university-policies/undergraduate-policies/grade-requirement): major GPA and course/progression grades.
- [Residency](https://yu.smartcatalogiq.com/en/current/university-catalog/university-policies/undergraduate-policies/residency): 60% major residence and individualized transfer advice; full degree-wide entry-history tables are not collapsed into one concentration threshold.
- [Declaration of Major/Change of Major](https://yu.smartcatalogiq.com/en/current/university-catalog/university-policies/undergraduate-policies/declaration-of-major-change-of-major): deadline, form and change-year catalog rules.
- [Pass/No Credit](https://yu.smartcatalogiq.com/en/current/university-catalog/university-policies/undergraduate-policies/pass-no-credit): applicable Wilf/YC restriction on major and correlate courses.
- [Course Substitutions](https://yu.smartcatalogiq.com/en/current/university-catalog/university-policies/undergraduate-policies/course-substitutions): written authorization with chair/dean approval.
- [Courses at Outside Institutions](https://yu.smartcatalogiq.com/en/current/university-catalog/university-policies/undergraduate-policies/courses-at-outside-institutions): advance permission, minimum grade, summer limits and quarter-credit conversions.
- [Transfer Credit Policies](https://yu.smartcatalogiq.com/en/current/university-catalog/university-policies/undergraduate-policies/transfer-credit-policies): case-specific evaluation and separate high-school coursework conditions.
- [Prerequisite and Corequisite Policy](https://yu.smartcatalogiq.com/en/current/university-catalog/university-policies/undergraduate-policies/prerequiste-and-corequisite-policy): timing, C- and removal from subsequent courses.
- [Course Share](https://yu.smartcatalogiq.com/en/current/university-catalog/university-policies/undergraduate-policies/course-share): general rule, credit-intensive exceptions and department authority.
- [Graduation Information](https://yu.smartcatalogiq.com/en/current/university-catalog/university-policies/undergraduate-policies/graduation-information): reviewed for corroboration; degree conferral and administrative deadlines are not modeled as extra concentration course requirements.
- [Credit Hour Policy](https://yu.smartcatalogiq.com/en/current/university-catalog/university-policies/undergraduate-policies/credit-hour-policy): reviewed; it points to a general credit-hour definition without itself establishing a semester/quarter mapping, so normalized course units remain unknown.

Nine policy pages produce nine scoped note nodes. Three additional, individually scoped [department FAQ](https://www.yu.edu/yeshiva-college/ug/computer-science) sections supply CS summer approval, no AP-CS exemption for COM 1300, and the AI track's automatic mathematics-minor overlap. This yields **13 total nodes**: the unchanged 22-course required table plus twelve policy notes. The math-minor statement is not a second fully audited award or a reason to override the general department-controlled overlap rule.

Each policy/FAQ refresh compares its observed heading and normalized scoped content with the reviewed version before returning an original summary. Changed numbers, exceptions, approval rules or missing sections fail for review. Seeds are not read by parsers. The course-table parser retains its independent source scope.

**Institutional decisions:** actual transfer credit, substitutions, summer CS permission and any entry-history residence determination remain decisions of the named advisers/chair/dean. The 74-versus-75 guide/catalog conflict and separate AI-track declaration/recognition procedure still need clarification. The full host BS is outside this task. **Remaining unattempted accessible work:** 22 linked course pages for descriptions/prerequisites; term-specific public sites/syllabi; the linked provost credit-hour details if unit normalization is needed. No claim is made that these are unavailable. Launch date and assessed program outcomes remain unverified.

## Validation

149 focused tests passed at the policy checkpoint. An isolated database accepted both seeds; the normal scraper replayed the actual captured official HTML and produced three UT and eleven Yeshiva candidates. A second scrape produced zero new candidates for each. Repeat ingestion produced zero changes; SQLite integrity, foreign keys and a temporary static build passed. Raw official captures remain ignored. No maintained DB, core, PLAN or site files were edited.
