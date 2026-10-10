# Official evidence — 2026-10-10

## Scope and current result

219 observed course records and 138 requirement nodes. The 2026–2027 official Clean Catalog program page, all **eleven** concentration pages, the MS-AI CS/DS core-bin graduate alternative, and fifteen university policy pages have been reviewed and mapped. Degree remains **partial** for a precise policy ambiguity: the HUA page states B- for transferred US courses, but its language subsection retains B for two-year/C for four-year institutions followed by a B- recommendation. The department’s current Degree Resources page directs evaluation to its coordinator and catalog without resolving that discrepancy. No inferred precedence or invented threshold is used.

## Program and concentration inventory

AI distribution includes ten program units; overall advanced-level minimum; two-of-three introductory CS groups with 1000-level ceiling; algorithms; math with separate calculus pairs; 8/3 core with four bins and its advanced minimum; ethics; natural/engineering science and overlap replenishment; exactly one six-course concentration; disciplinary electives and concentration-related MQP/advisers. The concentration root now selects one whole child inventory. The disciplinary pool includes every observed course option across those inventories, with local eligibility/level/relevance restrictions preserved.

All concentration pages explicitly identify their Associated Degree as Artificial Intelligence Major. They are parent-degree concentrations, not separately awarded/joint degrees. Source URLs in `concentrations.CONCENTRATIONS` correspond exactly to the eleven links on the official AI program page.

Special cases: Advanced AI and Optimization prohibit reuse of core courses. Built Environment excludes preparatory CE2000; molecular biochemistry excludes CH1010/1020; chemical production excludes CH1010/1020/1030. Optimization requires MA1024 plus one probability alternative, not both probability options. Experience Design includes two named graduate IMGD courses shown as 1/2 undergraduate unit and a two-course advanced floor. Social Policy requires a 4000-level course and allows special topics only when AI-relevant; six blank special-topic credit values remain null. Robotics allows an open RBE3000+ pool (including graduate) but excludes RBE3100. Open subject/level predicates are represented as rules rather than an invented exhaustive course list.

## Degree-wide inventory

Fifteen linked policies cover the 15-unit academic minimum, eight-unit residence, science baseline, HUA depth/breadth/language/AP/transfer/off-campus routes, social science eligibility and exclusions, wellness routes, IQP/MQP, grading, major certification, concentration declaration and one-unit additional-designation overlap ceiling/no triple counting, optional double majors and interdisciplinary MQP exceptions, graduate/BS-MS options, transfer approval, project registration/submission/completion/sponsor requirements and degree application deadlines. The standalone Double Major page describes the ordinary two-MQP case; the more detailed Degree Options page supplies the explicit joint-MQP/social-science exceptions, both represented. Administrative constraints are note nodes, not additive credits.

The general science baseline is not additional credit above overlapping major science. WPI has four seven-week terms within two semesters; `calendar: other` retains that distinction. Undergraduate course amounts remain fractional WPI units. Official Graduate Courses supplies the conversion 1 graduate credit = 1/6 undergraduate unit; graduate row values are still kept in their native published credit form. Conversion is a separately cited rule, not silently applied to course records.

## Extraction and metadata

Program, per-concentration, per-policy and selected course-page parsers inspect the supplied HTML. They return partial components, validate headings/clauses and observe changed course rows; they never emit the manual audit or verification date. Raw HTML is only in ignored cache. Three selected AI-degree course pages have short reviewed descriptions/advisory background; remaining metadata/public syllabi remain unverified. Focused synthetic tests cover nested probability choices, graduate wrappers, conditional topics, robotics exclusion, policy conversion and business prohibitions. Parent coordinator owns DB ingestion and family modeling.
