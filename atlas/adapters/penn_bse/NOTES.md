# Artificial Intelligence, BSE

Reviewed 2026-10-10 against official university sources. Raw source HTML was fetched to `/tmp/atlas-*.html` for development and is not committed. University robots policies were checked; no access restrictions were bypassed.

## Coverage and limits

The parser extracts computing, all six AI core areas and the AI elective option pool. Nested introductory-AI alternatives are flattened within a single choice while preserving course names. Other degree components are summarized in the curated record. Individual course credits are null because the page lists group totals. The overview implies concentrations are required; the explicit concentration section says optional. This conflict is retained in notes. Catalog endpoints returned empty responses; no catalog edition is assigned to the undated program page.

Seed record: `data/programs/penn-bse-ai.json`. 54 observed course records; option pools are not course requirements to sum. All curriculum records remain explicitly partial. Selected public course resources are verified below; others remain null.

## Parser behavior

`PROGRAM_ID`, `SOURCES` and `parse(html: str) -> dict` are exported. Parsing validates the official page heading and expected curriculum sections, then extracts actual course codes, titles when present, credits when explicit, and nested requirements. It never reads the curated JSON seed or returns a refreshed `last_verified`. Missing required headings/sections or changed selection rules raise `ValueError`. Returned observations remain partial and require coordinator review before replacing curated evidence.

## Source metadata

- [Artificial Intelligence, BSE](https://ai.engineering.upenn.edu/academics/undergraduate/) — locator: Curriculum requirements; catalog: not stated; source date: not stated; confidence: high. Metadata ID: `penn-bse-ai-curriculum`.
- [Academic calendar](https://almanac.upenn.edu/penn-academic-calendar) — locator: Fall and spring academic terms; catalog: not stated; source date: not stated; confidence: high. Metadata ID: `penn-bse-ai-calendar`.
- [Penn Engineering AI degree announcement](https://almanac.upenn.edu/volume-70-number-23) — locator: Penn Engineering Announces First Ivy League Undergraduate Degree in Artificial Intelligence; final paragraph; catalog: not stated; source date: 2024-02-20; confidence: high. Metadata ID: `penn-bse-ai-launch`.

## Validation

`tests/test_cmu_penn.py` uses synthetic HTML, not copied catalog fixtures, and checks section failure, actual changed-course extraction, nested options, unknown credits, credential distinctions, and record references. Live official HTML was also parsed locally for this review.

## Public course resource enrichment (2026-10-10)

- [CIS 3200: Intro to Algorithms — past offerings](https://www.engineering.upenn.edu/~cis3200/) — Archive identifies CIS 3200 and links Fall 2021. Source ID: `penn-cis3200-archive`.
- [Introduction to Algorithms — Fall 2021](https://www.engineering.upenn.edu/~cis3200/21fa/) — Heading, term, prerequisites, grading and Topics Covered; historical CIS 320 numbering. Source ID: `penn-cis3200-fall-2021-outline`.

Course `source_id` still cites the curriculum; resource metadata independently supports `public_site` and `syllabus`. CMU resources identify Fall 2026; the Penn outline is explicitly a historical Fall 2021 example linked by the official CIS 3200 archive (older CIS 320 numbering), not current curriculum evidence. No syllabus content was copied into the repository.

## Inferred comparison themes

Added explicitly `inferred_taxonomy` labels from the existing cited curriculum: AI methods, Mathematical foundations, Responsible AI and society, Software and systems, Applied AI. Locators name the supporting core, requirement, overview or elective-pool section. These are analyst classifications for comparison, not university-stated outcomes, and elective-pool themes do not imply every student takes every option. Existing source-stated outcomes are unchanged.

## Expanded degree inventory — 2026-10-10

All eight primary curriculum accordions are now parsed, yielding 83 observed course records and 26 nested requirements. New mapping includes six mathematics subjects with the ESE 3010 / STAT 4300 alternative, a natural-science slot without lab, three optional four-course concentration pools, senior design, technical electives, ethics and cognition choices, five-unit SS/H distribution with included writing, and the free elective. STAT 4300's title remains null because the source gives only its code. Optional concentrations remain under a note parent, not mandatory extra credits; cross-listed pool membership cannot imply double-counting permission. Where optional concentration titles differ for an existing code, the main curriculum-pool title is retained.

Still **partial**: the linked technical-elective list and engineering-wide approved general education, grading, residency and degree rules require inspection; the overview/detailed optional-concentration inconsistency remains; FAQ transfer limits and dual-major exclusions need complete modeling. The audit records each gap. Course descriptions, units and prerequisites remain a separate mostly incomplete metadata layer; no challenged course-catalog access was bypassed. The rerunnable parser emits partial observations only, never the reviewer audit. Synthetic tests cover probability alternatives, conditional concentration structure, writing inclusion and changed policy detection.

## Linked electives and FAQ review — 2026-10-10

Read the [CIS technical-elective policy](https://advising.cis.upenn.edu/tech-electives/) and its directly linked [official JSON inventory](https://advising.cis.upenn.edu/assets/json/37cu_csci_tech_elective_list.json). The introductory policy explicitly extends approved list entries to ARIN, while restricting the subsequent quota rules to the 37-CU CSCI degree. **Do not import the CSCI restricted-course quota into AI.** The current status column supplies 351 approved options; 13 `ask` entries are separated as conditional notes, and 142 `no` entries are excluded. AI's independent Engineering/Math/Natural Science eligibility remains an open category. No individual course units are inferred from the three-unit group total. The inventory also verifies the previously missing STAT 4300 title.

Mapped the source program FAQ's transfer/declaration steps, eight-semester completion limit (ten for M&T), CSCI/NETS/SSE dual-major exclusions, advising-dependent dual degrees, and first-fall declaration timing for incoming M&T students.

The official Engineering handbook host returned a cross-origin robots redirect for `https://ugrad.seas.upenn.edu/robots.txt`. Collection stopped; no alternate route was used. Degree-wide grading, residency, approved general education/writing and transfer-in policies remain unresolved. The concentration optionality inconsistency remains. The record stays **partial**. Earlier inventory counts above describe earlier review stages, not the final expanded technical-elective pool.

## Canonical handbook migration resolved — 2026-10-10

A bounded robots review established the actual old-site migration: `ugrad.seas.upenn.edu/robots.txt` redirects to the academic-services landing page through `academics.seas.upenn.edu`, finally reaching `academics.engineering.upenn.edu/ugrad/`. The endpoint is HTML, not a robots policy. The canonical host's own robots policy is valid and permits the relevant public pages. The previous stop was our conservative redirect-review condition, **not a demonstrated publisher access denial**. No old HTML-as-robots allowlist or fetcher change was introduced.

Following the canonical site's official navigation, read the [current Undergraduate Student Handbook](https://academics.engineering.upenn.edu/ugrad/student-handbook/). Mapped 13 policy notes and 49 WRIT course classifications across five worksheet groups. This covers curriculum cohort, credit away and external-transfer residence, dual-major rules, uncleared grades and the Summer 2026 incomplete-work rule, cumulative/major GPA and progress, pass/fail, repetition, elapsed degree time, internal transfer eligibility and writing policy. Writing courses marked free elective or unclassified are explicitly separate; they do not silently satisfy AI's SS/H distribution.

The generic SSH depth rule applies only to 40-unit curricula and is **not imposed on the 37-unit AI degree**. Breadth applicability still needs clarification. The handbook's CIS 4230/5230 Engineering-ethics eligibility list omits ARIN while the AI program lists CIS 4230 in its ethics pool; preserve both source statements. The full natural-science, SS/H, TBS and no-credit exception inventories remain to be structured, and other degree-completion policies remain under review. Penn remains partial.
