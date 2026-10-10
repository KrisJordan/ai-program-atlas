# Purdue AI BS pilot

Verified 2026-10-10 from the official [department curriculum](https://www.cs.purdue.edu/undergraduate/curriculum/bachelor-ai.html), updated 2026-08-27, and [registrar calendar](https://www.purdue.edu/registrar/calendars/academic/). This is the BS in the Department of Computer Science / College of Science, separate from the Liberal Arts BA. University ID is `purdue-university`.

## Exact coverage

42 distinct course records and 17 requirement nodes cover the department's Fall 2026 onward core, three selective groups and capstone. Core alternatives retain their own nodes. MA 26100 / MA 27101 retain 4 / 5 credits respectively. The 50–51 core-credit range remains a summary with numeric credits null. CS 47700 / CS 57700 form one NLP option inside the choose-two selective. The capstone retains its course, unpaid research, honors and AI Forge routes separately. Source-stated objectives are short paraphrases; course/category taxonomy is editorial.

The full [catalog plan](https://catalog.purdue.edu/preview_program.php?catoid=19&poid=35981) was inaccessible (HTTP 403). No bypass attempted. The department page is current official evidence, but does not establish the exact catalog edition or full degree/college requirements. Catalog year and launch date remain null. Fall 2026 is a curriculum effective date, not a founding date. Verification and curriculum coverage are partial. Elective group totals do not prove individual course credits; these remain null. Descriptions and prerequisites mostly remain null; the capstone prerequisites are explicitly stated. Public course sites and syllabi were not verified.

## Adapter behavior

`parse(html)` extracts headings, core table cells, linked course identifiers/names, alternative credit values, selection counts, selective lists and capstone routes. It returns an observed subset for review, never a seed payload or a fabricated freshness timestamp. Unknown structure or capstone rules fail closed. Synthetic tests cover alternative credits, NLP nesting, changed counts/names, absent structure and unknown capstone routes. The initial seed was produced from actually fetched public HTML in `/tmp`, then enriched with concise reviewed source evidence. Raw HTML is excluded from the repository.

## Next checks

Obtain accessible catalog evidence through ordinary public access; reconcile university/college requirements and total credits. Inspect linked course records for exact credits, descriptions and prerequisites. Check current source approval rules before treating research/honors/AI Forge as automatic eligibility. Find dated launch evidence independently. Review the department's source typo `Introductions to Robotics` rather than silently correcting the course title. Do not count the two NLP alternatives twice. Current inventory is a pilot, not an exhaustive Purdue AI-program search or a ranking claim.

## College-core and course-detail follow-up — 2026-10-10

The permitted [College of Science core page](https://www.purdue.edu/science/Current_Students/curriculum_and_degree_requirements/college-of-science-core-requirements.html) adds eleven published required areas under one parent node. Inventory now has **29 requirement nodes / 42 courses**, still partial. Each area is a policy node with unknown credits and unresolved approved options; do not sum these as extra major credits. College substitutions, approved course lists/experiences, overlap and full university degree requirements remain audit gaps. A new `SOURCE_PARSERS` function extracts the actual linked area inventory and does not infer completion from headings alone.

Canonical outlines for [CS 18000](https://www.cs.purdue.edu/academic-programs/courses/canonical/cs180.html), [CS 18200](https://www.cs.purdue.edu/academic-programs/courses/canonical/cs182.html) and [CS 37300](https://www.cs.purdue.edu/academic-programs/courses/canonical/cs37300.html) support concise course-content paraphrases; CS 18200 explicitly names CS 18000 as prerequisite. Sources are registered and dated June 20, 2025, without asserting a current-term offering. CS 180 uses an older Programming I heading; the directory links its code as CS 18000. CS 471's canonical page contains a 1998.08 date and was excluded as current evidence. Selfservice course-detail endpoints are robots-disallowed. Full course metadata remains sparse; no source access restriction was bypassed. Synthetic tests check core-area extraction, parentage and missingness.
