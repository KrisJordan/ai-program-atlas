# Purdue AI BA pilot

Verified 2026-10-10 using [official admissions](https://admissions.purdue.edu/majors/artificial-intelligence/). Its h1 is **Artificial Intelligence (Liberal Arts)** and Quick Facts explicitly identifies **Bachelor of Arts**, West Lafayette, College of Liberal Arts. Retain that source title and separate BA award; do not merge this program with Purdue's technical AI BS. University ID is `purdue-university`.

## Exact coverage and blocker

Identity, degree type, hosting college, a brief overview and two short source-stated objective/career summaries are covered. The current [plan of study](https://catalog.purdue.edu/preview_program.php?catoid=19&poid=35726) returned HTTP 403. No bypass attempted. Curriculum status is **pending**; courses and requirements are empty. Catalog year, total credits, and launch date are null. Career examples are possibilities, not employment-outcome statistics. The admissions copy contains potentially inconsistent no-coding language alongside programming/data preparation; no technical waiver is inferred.

The registrar's [calendar](https://www.purdue.edu/registrar/calendars/academic/) and the BS page's semester-labelled curriculum support institution calendar classification. No BA-specific credit or course requirement is borrowed from the BS.

## Adapter behavior and next checks

The parser verifies h1, structured Quick Facts award and campus, and actually extracts the plan URL. It returns a limited observation for review with no freshness timestamp and no copied seed. A mere title does not pass. Tests use synthetic markup and detect changed award identity.

Next: inspect the linked current catalog when ordinary public access is available; extract core philosophy and computing alternatives, degree/college requirements, outcomes, credit units, course descriptions and prerequisites. Verify any historical first-offering claim using dated official evidence. Public course sites and syllabi remain unverified. Partial pilot coverage does not establish a comprehensive Purdue inventory or cohort rank.

## Department-plan follow-up — 2026-10-10

The permitted [Philosophy department BA page](https://www.cla.purdue.edu/academic/philosophy/students/undergraduate/majors/artificial-intelligence/index.html), Plan of Study, gives 24 philosophy credit hours and 15 CS credit hours plus five required CS courses. It links the same blocked current catalog plan. Curriculum is now **partial** (five courses, two requirement groups), superseding the earlier pending state. Individual credits are null: a group total does not establish equal course credits. Philosophy choices and degree-wide college/university/grade/residency/overlap rules remain unresolved; the review audit records them.

`SOURCE_PARSERS` adds a department parser that reads actual totals/course rows and fails closed on missing structure. The first admissions observation remains identity-only; neither observation overwrites reviewed seed metadata automatically. The department uses older CS 17600 and CS 24300 titles than the [Fall 2026 course directory](https://www.cs.purdue.edu/academic-programs/courses/index.html); preserve those source-specific titles pending catalog reconciliation. Canonical outlines for [CS 10100](https://www.cs.purdue.edu/academic-programs/courses/canonical/cs10100.html), [CS 18000](https://www.cs.purdue.edu/academic-programs/courses/canonical/cs180.html) and [CS 18200](https://www.cs.purdue.edu/academic-programs/courses/canonical/cs182.html) support short content summaries and the CS 18200 prerequisite. They are dated June 20, 2025 and are not current-term offering evidence; CS 180 uses its older Programming I heading, linked as CS 18000 in the canonical directory. The selfservice catalog endpoint is robots-disallowed. Synthetic tests cover changed group totals and avoid inferred individual credits.

## Degreewide-policy continuation (2026-10-10)

Still **partial: five course observations, three requirement nodes**. The department's introductory paragraph explicitly describes eight specialized philosophy courses, so the 24-hour philosophy group now records an eight-course count; it does **not** imply eight unrestricted electives. The precise required courses, internal categories and approved options remain inaccessible behind the previously blocked current catalog.

Inspected the college advising page and faculty Plan of Study page; neither supplies an alternate current AI curriculum. The currently linked `cla-core-21.pdf` identifies itself as a revised 2019 proposal, so it is not asserted as the current Fall-2026 CLA core. No attempt was made to switch catalog hosts or bypass the known 403.

The official university news article dated 2026-08-19 confirms required AI-focused coursework for the incoming Fall 2026 cohort, with approved courses spanning one to four hours. Added a university policy note; which BA course fulfills it remains unverified. This date is not a major launch date, and the range is not added to major credits. Raw HTTP disconnected; an official web read succeeded. The adapter independently observes the article's cohort and range.

Source statement types now identify the admissions program summary as a program aim and its career list as prospective career pathways. Full CLA core, university degree/GPA/residency/civics rules, major philosophy choices, overlap rules and AI competency mapping remain explicit audit gaps. Existing canonical descriptions are still dated outlines, not current course offerings.

## Bounded philosophy inventory follow-up — 2026-10-10

The independently linked [Fall 2026 philosophy directory](https://www.cla.purdue.edu/academic/philosophy/students/undergraduate/courses-new.html) and department undergraduate overview were accessible. They list actual offerings, including an AI-related philosophy seminar, but do not identify the eight courses / 24 philosophy credits required by this BA or any complete choice groups. No offering was inferred to be a degree requirement. The record remains **5 courses / 3 nodes, partial**. Current catalog denial was not retried or bypassed. The earlier CLA core PDF remains a 2019 proposal rather than current degree evidence. Full philosophy inventory, current CLA core and university GPA/residency/civics/AI-competency mapping remain blockers; the public registrar degree-planning page points to authenticated personal audits, not public rules.

## Degree correctness audit — 2026-10-11

See [eight-degree audit](../../../research/degree-audit/west-purdue-wpi.md) and its adjacent per-program JSON ledger. This program is blocked for whole-degree certification by the specific evidence gaps recorded there. Verified role/subject corrections are retained; parser success and prior local curriculum labels are not a completed degree audit. Remaining course-content review work is distinguished from actual source barriers. Independent second pass remains pending.

## Bounded Purdue canonical-content follow-up

Eleven distinct full departmental outlines were read: CS10100 for BA; CS18000/18200 for both; and CS34800/37300/38100/44800/47100/48300/52300/57700 for BS. This adds seven previously undescribed BS course records and rechecks the four previously described identities. The directory calls these faculty-approved canonical syllabi but explicitly marks CS48300 **proposed**. The pages report June 20, 2025 updates; some contain much older explicit outline dates (1998.08, 2004.08 or 2005.12). These are useful dated content evidence, not current Fall-2026 catalog equivalences. Full-page guards protect both topics and dated context; no credits, current titles or fresh manual review status are fabricated by the parser.

CS34800's database outline establishes systems. Algorithms and computation theory remain foundations; databases systems; explicit AI/NLP learning methods AI/ML; security law/economics human context. CS10100 and CS18200 remain mixed from their full scope. Only CS18200 publishes a prerequisite in these outlines, and its dated CS18000 condition is retained as such. Existing degree-source credit values are not inferred from these credit-free outlines.

The actual **Fall 2026 West Lafayette** directory lists CS17600 Data Engineering In Python and CS24300 Artificial Intelligence Basics. Both detail links lead to the previously robots-disallowed selfservice host, which was not retried. Neither has a canonical-directory entry. Search snippets from denied catalogs were not used as full-description evidence. BA keeps the older department-plan titles with this explicit current-directory distinction; current full descriptions and title-version reconciliation remain unverified.

For the five represented BA records, no known unread publicly linked description branch remains after this bounded check: three dated outlines are inspected and the other two detail sources are unavailable. BA returns to **blocked** for these precise gaps and its inaccessible philosophy/current college inventory, without claiming exhaustive web absence. BS remains **in_progress** for its much larger accessible named/contextual course backlog.

## Fixed-major resolution disposition — 2026-10-11

The department page was reread in full. Five named CS identities are verified, while the eight philosophy-course identities and their fixed/optional structure remain unspecified on this accessible source. A complete fixed major set cannot be established, so the proposed replacement review remains partial. Older BA titles and null individual credits remain source-specific; no BS facts or current offering membership are inherited. Exact manual identities/categories, permitted-alternative dispositions and limits are in [Purdue resolution](../../../research/degree-audit/independent-resolution-purdue.md). Known denied catalog/detail routes were not retried. Refresh now rejects truncated, duplicated or substituted computing lists against the exact five-source-identity inventory, without adding review status to observations.

## Public planning-source follow-up — 2026-10-11

See [planning-source conflict follow-up](../../../research/university-core-followup-plan-conflicts.md) and its complete proposed bounded review rows. Public advising/governance alternatives establish no governing current inventory sufficient to close this program's remaining core gap. Prior course facts, review statuses and source-specific version limits are retained. Known denied routes were not retried; no personal audit or contact with people. Full-degree status is not certified.
