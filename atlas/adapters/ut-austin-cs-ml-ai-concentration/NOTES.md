# UT Austin CS Machine Learning & Artificial Intelligence Concentration

Reviewed 2026-10-11. This is an undergraduate Computer Science concentration, not a separately verified bachelor's degree or graduate credential. The current [CS concentration directory](https://www.cs.utexas.edu/undergraduate/concentrations) and [AI academics directory](https://ai.utexas.edu/academics) establish the identity. The particular eligible host degrees and launch date remain unverified.

## Curriculum evidence and conflict

The current directory links the [December 17, 2025 concentration course listing](https://www.cs.utexas.edu/sites/default/files/2025-12/UTCS_Concentrations_Course_Listings_12172025.pdf). Both PDF pages 2 and 3 were rendered and visually reviewed. The foundation instruction begins at the bottom of page 2 and continues with its two options on page 3; the section ends before Mobile Computing. The mapped local curriculum has nine published course routes and four requirement nodes: one foundation, three electives, and the explicit conditional permission to use the other foundation as an elective if both foundations are taken. The same foundation cannot fulfill both choices. Source notation `CS 343(H)` and `CS 363M (378H)` is preserved rather than expanded into unsupported independent course instances. The named CS 378 topic has a title-specific stable ID.

The older [dedicated concentration page](https://www.cs.utexas.edu/concentrations/mlai) instead names CS 363D Introduction to Data Mining, CS 378 Natural Language Processing, and an uncoded capstone. This disagreement remains explicit. The currently linked, dated PDF supplies the mapped course pool; the older page does not silently contribute additional options. Its advertised 12 credit hours does not establish the credits of individual courses. Its dated external ranking marketing is excluded.

Curriculum status is **partial**. Declaration and recognition rules, applicable host-degree requirements, grades, residence and other concentration policies have not been fully reviewed. Individual course credits, descriptions, prerequisites, public teaching sites and syllabi remain unknown pending direct course-source review. Two published statements are typed as a program aim and career pathway, not assessed learning outcomes. No complete curriculum audit is claimed.

## Rerunnable parser scope

The normal HTML adapter refreshes identity from the current directory only. It requires the main heading, the exact ML/AI section heading, current CS-student context and the official PDF course-list link. Navigation mentions cannot qualify. It does not claim that the PDF curriculum was refreshed by an HTML fetch.

`parse_pdf_text` / `PDF_TEXT_PARSER` separately accepts text extracted from an ordinarily accessible official PDF. It scopes the exact concentration section, verifies one-foundation/three-elective rules and the unused-foundation condition, then extracts the actual course bullets. Changed course options are observed. Unexpected requirement prose, incomplete or duplicate choices, wrapped bullets requiring interpretation, changed counts and missing section boundaries fail for review. The generic HTML fetcher does not process PDF bodies, so a subsequent PDF refresh still requires a permitted PDF retrieval, extraction and page review before applying a curriculum candidate. No seed replay supplies parser results.

The official HTML captures were obtained through the ordinary safe fetcher. PDF retrieval checked robots and returned HTTP 200 with PDF content. Raw HTML, PDF, extracted text and rendered pages are ignored local review artifacts and are not committed.

## Checks

`tests/test_ut_austin_ai_concentration.py` covers scoped identity, wrong contexts and navigation, changed PDF options, conditional eligibility, changed rules, unrelated adjacent concentration sections and source conflicts. Optional ignored-cache replay matches the actual reviewed PDF extraction to the seed. Together with Yeshiva, core review and discovery checks: **144 passed**.

An isolated database accepted the seed, exported nine courses and four rules, replayed the three captured HTML responses through the regular scrape orchestration, and deduplicated a second run. Repeated seed ingestion produced zero changes; SQLite integrity/foreign keys and a temporary static build passed. No maintained database or shared core files were edited.
