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
